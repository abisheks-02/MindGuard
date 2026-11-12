"""
Llama 3.2-based 2-step detection pipeline.
Step 1: Tanglish → English translation
Step 2: English → Severity classification
"""

import logging
from app.services.detection import DetectionService

logger = logging.getLogger(__name__)

CLASSES = ["Normal", "Mild", "Moderate", "Severe"]

TAMIL_MARKERS = {
    "naan", "romba", "iruku", "illa", "mudiyala", "pola", "sethuduven",
    "da", "di", "kashtama", "enna", "yethu", "vazhkai", "mudinjiduchu",
    "kavalai", "payama", "kooda", "konjam", "sariya", "oru", "enaku",
}

TANGLISH_GLOSSARY = {
    "sagalam": "let's die / suicidal",
    "saagalam": "let's die / suicidal",
    "chagalam": "let's die / suicidal",
    "sethuduven": "I will die / suicidal",
    "mudiyala": "I cannot take it anymore",
    "kashtama": "very painful / suffering",
    "bayama": "fearful / anxious",
    "vazhkai": "life",
    "mudinjiduchu": "is over",
    "tension": "anxiety",
    "veri": "rage/anger",
}


class LlamaDetectionService(DetectionService):
    """Concrete implementation using Llama 3.2 3B-Instruct (4-bit)."""

    def __init__(self, model, tokenizer):
        self._model = model
        self._tokenizer = tokenizer

    # ── public API ───────────────────────────────────────

    def analyze(self, text: str) -> dict:
        if not text.strip():
            return self._empty_result()

        if self._model is None:
            return self._fallback_result()

        try:
            return self._run_pipeline(text)
        except Exception as e:
            logger.exception("LlamaDetectionService.analyze failed: %s", e)
            return self._empty_result()

    # ── private helpers ──────────────────────────────────

    def _run_pipeline(self, text: str) -> dict:
        hints = self._build_hints(text)
        hint_str = f" [Translation Hint: {', '.join(hints)}]" if hints else ""

        # STEP 1 — Tanglish → English
        translation_prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
            "You are an expert Tamil-English (Tanglish) to English translator.\n"
            "Your ONLY job is to accurately translate the user's text into plain English.\n"
            'Note: "sagalam", "saagalam", "chagalam" mean "let\'s die" or suicidal ideation.\n'
            "Output ONLY the English translation, nothing else."
            "<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
            f'Text: "{text}"{hint_str}<|eot_id|><|start_header_id|>assistant<|end_header_id|>'
        )
        translated_text = self._generate(translation_prompt, max_tokens=100)

        # STEP 2 — Classification
        class_prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
            "You are a highly advanced clinical AI. Analyze the translated English text.\n"
            "Classify the distress severity strictly as ONE of these exact words: Normal, Mild, Moderate, or Severe.\n"
            "Also identify up to 3 concerning keywords from the translated text.\n"
            "Format your output exactly like this:\n"
            "SEVERITY: [word]\n"
            "KEYWORDS: [comma separated words]"
            "<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
            f'Translated English Text: "{translated_text}"<|eot_id|><|start_header_id|>assistant<|end_header_id|>'
        )
        response_text = self._generate(class_prompt, max_tokens=80)

        predicted_class, shap_tokens = self._parse_classification(response_text)

        # Code-Switching metric
        code_switching = self._compute_code_switching(text)

        probs = {c: 0 for c in CLASSES}
        probs[predicted_class] = 100

        return {
            "predicted_class": predicted_class,
            "confidence": 100,
            "shap_tokens": shap_tokens,
            "class_probabilities": probs,
            "translation": translated_text,
            "code_switching": code_switching,
        }

    def _generate(self, prompt: str, max_tokens: int = 80, temperature: float = 0.1) -> str:
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        outputs = self._model.generate(**inputs, max_new_tokens=max_tokens, temperature=temperature)
        return self._tokenizer.decode(
            outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True
        ).strip()

    @staticmethod
    def _build_hints(text: str) -> list[str]:
        hints = []
        for word in text.lower().split():
            if word in TANGLISH_GLOSSARY:
                hints.append(f"'{word}' means '{TANGLISH_GLOSSARY[word]}'")
        return hints

    @staticmethod
    def _parse_classification(response_text: str) -> tuple[str, list[dict]]:
        predicted_class = "Normal"
        shap_tokens: list[dict] = []
        for line in response_text.split("\n"):
            line = line.strip()
            if line.startswith("SEVERITY:"):
                raw = line.replace("SEVERITY:", "").strip().title()
                if raw in CLASSES:
                    predicted_class = raw
            elif line.startswith("KEYWORDS:"):
                for w in line.replace("KEYWORDS:", "").split(","):
                    w = w.strip()
                    if w:
                        shap_tokens.append({"text": f"{w} ", "weight": 3})
        return predicted_class, shap_tokens

    @staticmethod
    def _compute_code_switching(text: str) -> dict:
        words = [w.lower() for w in text.split()]
        total = len(words)
        tamil_count = sum(1 for w in words if w in TAMIL_MARKERS)
        ratio = round((tamil_count / total) * 100) if total else 0
        return {
            "ratio": ratio,
            "status": "High Cognitive Load" if ratio >= 15 else "Standard Variance",
        }

    @staticmethod
    def _empty_result() -> dict:
        return {
            "predicted_class": "Normal",
            "confidence": 100,
            "shap_tokens": [],
            "class_probabilities": {"Normal": 100, "Mild": 0, "Moderate": 0, "Severe": 0},
            "translation": "",
            "code_switching": {"ratio": 0, "status": "Standard Variance"},
        }

    @staticmethod
    def _fallback_result() -> dict:
        return {
            "predicted_class": "Mild",
            "confidence": 100,
            "shap_tokens": [],
            "class_probabilities": {"Normal": 0, "Mild": 100, "Moderate": 0, "Severe": 0},
            "translation": "",
            "code_switching": {"ratio": 0, "status": "Standard Variance"},
        }
