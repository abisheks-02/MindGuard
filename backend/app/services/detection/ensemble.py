"""
Ensemble Detection Service v2
==============================
Complete rebuild with all 8 layers:
  1. Input Gate (sanitize, language, gibberish, injection)
  2. Chunking for long text
  3. Context Analyzer (negation, subject, sarcasm, tone)
  4. Detectors (lexicon, hybrid sentiment, embedding kNN)
  5. Aggregator with proper severity rules
  6. Response contract
  7. Explainability
"""

import os
import re
import time
import logging
import yaml
from typing import Dict, List, Optional

from app.services.detection.input_gate import InputGate
from app.services.detection.context_analyzer import ContextAnalyzer
from app.services.detection.tanglish_translator import TanglishTranslator
from app.services.detection.lexicon import LexiconDetector
from app.services.detection.hybrid_sentiment import HybridSentimentDetector
from app.services.detection.embedding_knn import EmbeddingKNNDetector
from app.services.detection.xai import XAIService
from app.services.detection.base import DetectionResult

logger = logging.getLogger(__name__)

# ── Severity level utilities ────────────────────────────────────────────
LEVEL_MAP = {"Normal": 0, "Mild": 1, "Moderate": 2, "Severe": 3}
INV_LEVEL = {0: "Normal", 1: "Mild", 2: "Moderate", 3: "Severe"}
EXPLICIT_SELF_HARM = re.compile(
    r"\b(?:i|i'm|im|naan|na|enaku|ennaku|yennaku)\b.{0,40}"
    r"\b(?:want|will|going|plan|planning|need|poven|pannuven|virupam)\b.{0,40}"
    r"\b(?:die|dying|suicide|kill myself|end (?:my )?life|sagalam|saagalam|sethuduven)\b",
    re.IGNORECASE,
)


class EnsembleDetectionService:
    """
    The main detection service wired into /api/v1/analyze.
    Accepts ANY text and always returns a safe, explainable result.
    """

    def __init__(self, llama_model=None, llama_tokenizer=None, **kwargs):
        # ── Layer 1: Input Gate ──
        self.gate = InputGate()

        # ── Layer 2: Translator ──
        self.translator = TanglishTranslator()

        # ── Layer 3: Context Analyzer ──
        self.context_analyzer = ContextAnalyzer()

        # ── Layer 4: Detectors ──
        self.lexicon = LexiconDetector()
        self.sentiment = HybridSentimentDetector()
        self.knn = EmbeddingKNNDetector()

        # ── Layer 5: Config ──
        config_path = kwargs.get("config_path", "config/ensemble.yaml")
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", config_path)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except Exception:
            self.config = {
                "thresholds": {
                    "confidence_min_threshold": 0.60,
                    "severe_min_sources": 2,
                }
            }

    # ── Public API ──────────────────────────────────────────────────────

    def analyze(self, text: str) -> dict:
        """Main entry point. Always returns a valid response dict."""
        start_time = time.time()

        # ═══ LAYER 1: INPUT GATE ═══
        gate_result = self.gate.process(text)

        if gate_result["status"] in ("empty", "gibberish", "emoji_only", "unsupported_language"):
            return self._out_of_scope_response(gate_result)

        cleaned = gate_result["cleaned_text"]
        language = gate_result["language"]

        # ═══ LAYER 2: TRANSLATION ═══
        translated, tanglish_ratio = self.translator.translate(cleaned)

        # ═══ LAYER 3: CONTEXT ANALYSIS ═══
        ctx = self.context_analyzer.analyze(cleaned, translated)

        # ═══ LAYER 4: CHUNKING (for long text) ═══
        chunks = self._split_chunks(cleaned)
        chunk_results = []
        for chunk in chunks:
            chunk_translated, _ = self.translator.translate(chunk)
            cr = self._run_detectors(chunk, chunk_translated)
            chunk_results.append(cr)

        # ═══ LAYER 5: AGGREGATION ═══
        result = self._aggregate(chunk_results, ctx, gate_result)

        # ═══ LAYER 6: EXPLAINABILITY ═══
        lex_res = self.lexicon.detect(cleaned)
        lex_matches = lex_res.evidence if lex_res.label != "Normal" else []
        token_scores = XAIService.merge_explanations(None, lex_matches, cleaned)

        latency = time.time() - start_time
        logger.info(
            "Analyze: text=%r -> label=%s conf=%.2f lang=%s latency=%.2fs",
            cleaned[:60], result["label"], result["confidence"], language, latency
        )

        # ═══ LAYER 7: RESPONSE CONTRACT ═══
        return {
            "status": "ok",
            "predicted_class": result["label"],
            "confidence": int(result["confidence"] * 100),
            "uncertain": result["label"] == "Uncertain",
            "tone_context": {
                "subject": ctx.subject,
                "tense": ctx.tense,
                "negated": ctx.is_negated,
                "sarcasm": ctx.is_sarcastic,
                "hyperbole": ctx.is_hyperbolic,
                "tone": ctx.tone,
                "intensity": round(ctx.intensity, 2),
            },
            "translation": translated if tanglish_ratio > 0.2 else "",
            "chunk_results": [
                {"text": c["chunk_text"][:80], "label": c["label"], "confidence": c["confidence"]}
                for c in chunk_results
            ] if len(chunks) > 1 else [],
            "per_detector_results": result.get("per_detector", {}),
            "evidence": result.get("evidence", []),
            "shap_tokens": token_scores,
            "needs_review": result.get("needs_review", False),
            "suggested_reply_type": self._suggest_reply_type(result["label"]),
            "code_switching": {"ratio": round(tanglish_ratio * 100), "status": "Tanglish" if tanglish_ratio > 0.3 else "English"},
            "disclaimer": "Possible indicator, not a diagnosis.",
        }

    # ── Internal methods ────────────────────────────────────────────────

    def _split_chunks(self, text: str) -> List[str]:
        """Split text into sentence-level chunks."""
        # Split on sentence boundaries
        sentences = re.split(r'[.!?\n]+', text)
        chunks = [s.strip() for s in sentences if s.strip()]
        return chunks if chunks else [text]

    def _run_detectors(self, text: str, translated: str) -> dict:
        """Run all detectors on a single chunk and return raw results."""
        results = {}
        evidence = []

        # Lexicon detector (on original text — handles Tanglish spelling variants)
        try:
            lex = self.lexicon.detect(text)
            results["lexicon"] = {"label": lex.label, "score": lex.score}
            if lex.evidence:
                evidence.extend([f"[Lexicon]: {e}" for e in lex.evidence])
        except Exception as e:
            results["lexicon"] = {"label": "Normal", "score": 0.0, "error": str(e)}

        # Hybrid sentiment (translates internally + VADER)
        try:
            sent = self.sentiment.detect(text)
            results["sentiment"] = {"label": sent.label, "score": sent.score}
            if sent.evidence:
                evidence.extend([f"[Sentiment]: {e}" for e in sent.evidence])
        except Exception as e:
            results["sentiment"] = {"label": "Normal", "score": 0.0, "error": str(e)}

        # Embedding kNN (on translated text)
        try:
            knn = self.knn.detect(translated)
            results["knn"] = {"label": knn.label, "score": knn.score}
            if knn.evidence:
                evidence.extend([f"[kNN]: {e}" for e in knn.evidence])
        except Exception as e:
            results["knn"] = {"label": "Normal", "score": 0.0, "error": str(e)}

        return {
            "chunk_text": text,
            "per_detector": results,
            "evidence": evidence,
            "label": "Normal",
            "confidence": 0.0,
        }

    def _aggregate(self, chunk_results: List[dict], ctx, gate_result: dict) -> dict:
        """
        Aggregate detector results into a final label.
        
        Uses MAJORITY VOTE across detectors, with safety rules:
        - Severe requires 2+ sources AND no negation
        - Negated text with severe keywords -> Normal
        - Sentiment detector is the tiebreaker (it understands negation best)
        - Sarcasm/hyperbole → cap at Moderate
        - Question/command with no self-reference → Normal
        """
        all_evidence = []
        per_detector = {}
        detector_labels = []
        detector_scores = []

        for cr in chunk_results:
            all_evidence.extend(cr["evidence"])
            for det_name, det_result in cr["per_detector"].items():
                per_detector[det_name] = det_result
                label = det_result.get("label", "Normal")
                score = det_result.get("score", 0.0)
                detector_labels.append((det_name, label))
                detector_scores.append(score)

        # Abstaining detectors do not get converted into an arbitrary class.
        label_counts = {}
        for _, label in detector_labels:
            if label in LEVEL_MAP:
                label_counts[label] = label_counts.get(label, 0) + 1

        valid_labels = [label for _, label in detector_labels if label in LEVEL_MAP]
        if not valid_labels:
            return {
                "label": "Uncertain",
                "confidence": 0.0,
                "evidence": all_evidence + ["[Aggregator]: No detector had sufficient evidence"],
                "per_detector": per_detector,
                "needs_review": True,
            }

        severe_count = label_counts.get("Severe", 0)
        normal_count = label_counts.get("Normal", 0)
        mild_count = label_counts.get("Mild", 0)
        moderate_count = label_counts.get("Moderate", 0)

        # ── RULE: Sentiment detector is the authority on negation ──
        sentiment_label = per_detector.get("sentiment", {}).get("label", "Normal")

        # ── RULE: Negation override (strongest rule) ──
        if ctx.is_negated:
            if sentiment_label == "Normal":
                # Sentiment engine (VADER) understood the negation → trust it
                return {
                    "label": "Normal",
                    "confidence": round(sum(detector_scores) / max(len(detector_scores), 1), 3),
                    "evidence": all_evidence + ["[Aggregator]: Negation detected, sentiment confirms Normal"],
                    "per_detector": per_detector,
                    "needs_review": False,
                }
            else:
                # Negation present but sentiment isn't Normal → cap at Mild
                return {
                    "label": "Mild",
                    "confidence": round(sum(detector_scores) / max(len(detector_scores), 1), 3),
                    "evidence": all_evidence + ["[Aggregator]: Negation detected, capped at Mild"],
                    "per_detector": per_detector,
                    "needs_review": True,
                }

        # Explicit, first-person intent is a safety-critical signal.  It should
        # not be diluted by an abstaining or low-overlap auxiliary detector.
        message_text = " ".join(c.get("chunk_text", "") for c in chunk_results)
        if EXPLICIT_SELF_HARM.search(message_text):
            return {
                "label": "Severe",
                "confidence": 0.95,
                "evidence": all_evidence + ["[Aggregator]: Explicit first-person self-harm intent"],
                "per_detector": per_detector,
                "needs_review": True,
            }

        # -- RULE: If sentiment says Normal and majority agrees -> Normal --
        if sentiment_label == "Normal" and normal_count >= len(valid_labels) / 2:
            return {
                "label": "Normal",
                "confidence": round(sum(detector_scores) / max(len(detector_scores), 1), 3),
                "evidence": all_evidence,
                "per_detector": per_detector,
                "needs_review": False,
            }

        # ── RULE: Sarcasm/Hyperbole cap ──
        if ctx.is_sarcastic or ctx.is_hyperbolic:
            max_level = min(max(LEVEL_MAP.get(l, 0) for _, l in detector_labels if l in LEVEL_MAP), 2)
            all_evidence.append("[Aggregator]: Sarcasm/hyperbole detected, capped at Moderate")
        else:
            max_level = max(LEVEL_MAP.get(l, 0) for _, l in detector_labels if l in LEVEL_MAP)

        # ── RULE: Question/Command without personal statement ──
        if (ctx.is_question or ctx.is_command) and ctx.subject == "general":
            return {
                "label": "Normal",
                "confidence": 0.8,
                "evidence": all_evidence + ["[Aggregator]: Question/command, not personal distress"],
                "per_detector": per_detector,
                "needs_review": False,
            }

        # ── RULE: Severe requires 2+ sources ──
        needs_review = False
        if max_level == 3:  # Severe candidate
            # A curated high-precision acute phrase is safety-critical evidence.
            # Requiring a second, weak detector can otherwise miss direct intent.
            lexicon_vote = per_detector.get("lexicon", {})
            if (
                lexicon_vote.get("label") == "Severe"
                and lexicon_vote.get("score", 0.0) >= 0.9
                and ctx.subject not in ("other", "quote")
            ):
                final_label = "Severe"
                needs_review = True
                all_evidence.append("[Aggregator]: High-precision acute lexicon signal")
            elif severe_count >= 2:
                final_label = "Severe"
            elif severe_count == 1:
                # Only 1 detector says Severe -> downgrade to Moderate + needs_review
                final_label = "Moderate"
                needs_review = True
                all_evidence.append("[Aggregator]: Only 1 source flagged Severe -> Moderate + review")
            else:
                final_label = "Moderate"
        else:
            # Use majority vote for non-severe
            # Find the most common label
            sorted_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
            final_label = sorted_labels[0][0]

        # Average confidence
        avg_score = sum(detector_scores) / max(len(detector_scores), 1)

        conf_thresh = self.config.get("thresholds", {}).get("confidence_min_threshold", 0.60)
        if avg_score < conf_thresh and final_label not in ("Normal",):
            needs_review = True

        # -- RULE: Subject is "other" or "quote" -> cap at Mild --
        if ctx.subject in ("other", "quote") and max_level >= 2:
            final_label = "Mild"
            all_evidence.append(f"[Aggregator]: Subject is '{ctx.subject}', not self-referential")

        return {
            "label": final_label,
            "confidence": round(avg_score, 3),
            "evidence": all_evidence,
            "per_detector": per_detector,
            "needs_review": needs_review,
        }

    def _out_of_scope_response(self, gate_result: dict) -> dict:
        """Return a safe response for out-of-scope inputs."""
        return {
            "status": gate_result["status"],
            "predicted_class": "Out-of-scope",
            "confidence": 0,
            "uncertain": False,
            "tone_context": {},
            "translation": "",
            "chunk_results": [],
            "per_detector_results": {},
            "evidence": [],
            "shap_tokens": [],
            "needs_review": False,
            "suggested_reply_type": "neutral",
            "code_switching": {"ratio": 0, "status": "N/A"},
            "disclaimer": "Possible indicator, not a diagnosis.",
            "message": gate_result.get("message", ""),
        }

    def _suggest_reply_type(self, label: str) -> str:
        """Suggest the type of chatbot reply based on severity."""
        return {
            "Normal": "friendly",
            "Mild": "empathetic",
            "Moderate": "supportive",
            "Severe": "crisis",
            "Uncertain": "gentle_checkin",
            "Out-of-scope": "neutral",
        }.get(label, "neutral")
