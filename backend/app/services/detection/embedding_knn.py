"""
Embedding kNN Detector
======================
Uses sentence embeddings over a bank of labeled anchor sentences.
For each input, finds the k nearest anchors and votes on severity.
This is fast, doesn't need a GPU, and generalizes better than lexicon alone.
"""

import numpy as np
from typing import List, Tuple
from app.services.detection.base import Detector, DetectionResult


class EmbeddingKNNDetector(Detector):
    """kNN detector using simple TF-IDF sentence vectors as embeddings."""

    def __init__(self):
        self.name = "EmbeddingKNNDetector"
        self.k = 5  # number of neighbors

        # Anchor bank: labeled reference sentences
        self.anchors: list = [
            # ── Normal (Tanglish translations) ──
            ("I am happy", "Normal"),
            ("I feel good today", "Normal"),
            ("I am fine", "Normal"),
            ("I am feeling great", "Normal"),
            ("today was a good day", "Normal"),
            ("I am okay", "Normal"),
            ("everything is going well", "Normal"),
            ("I had a nice day", "Normal"),
            ("I am excited", "Normal"),
            ("life is good", "Normal"),
            ("I feel wonderful", "Normal"),
            ("I am at peace", "Normal"),
            ("I do not want to die", "Normal"),
            ("I have no desire to die", "Normal"),
            ("I will not commit suicide", "Normal"),
            ("I am not sad", "Normal"),
            ("I have no worry", "Normal"),
            ("I am feeling peaceful", "Normal"),
            ("I enjoyed my day", "Normal"),
            ("I love my family", "Normal"),
            ("I am very happy today", "Normal"),
            ("I feel joyful and content", "Normal"),
            ("feeling relaxed and calm", "Normal"),
            ("I will not die I want to live", "Normal"),
            ("suicide is not something I want", "Normal"),

            # ── Mild ──
            ("I am a bit stressed", "Mild"),
            ("I feel tired", "Mild"),
            ("I am bored", "Mild"),
            ("I feel a little down", "Mild"),
            ("work is stressful", "Mild"),
            ("I am nervous about exams", "Mild"),
            ("I feel low today", "Mild"),
            ("I am worried about something", "Mild"),
            ("I could not sleep well", "Mild"),
            ("I feel restless", "Mild"),
            ("I am slightly anxious", "Mild"),
            ("I feel uneasy", "Mild"),
            ("today was tiring", "Mild"),
            ("I have some tension", "Mild"),
            ("feeling a bit off", "Mild"),
            ("I am a little lonely", "Mild"),
            ("things are a bit hard right now", "Mild"),
            ("I feel uncomfortable today", "Mild"),

            # ── Moderate ──
            ("I feel very sad", "Moderate"),
            ("I am depressed", "Moderate"),
            ("I feel hopeless", "Moderate"),
            ("I cannot handle this anymore", "Moderate"),
            ("I feel like a burden", "Moderate"),
            ("nothing makes me happy", "Moderate"),
            ("I cry every day", "Moderate"),
            ("I feel worthless", "Moderate"),
            ("I am very lonely", "Moderate"),
            ("everything is falling apart", "Moderate"),
            ("I cannot take this pain", "Moderate"),
            ("my heart is very troubled", "Moderate"),
            ("I have no motivation", "Moderate"),
            ("I feel empty inside", "Moderate"),
            ("life feels meaningless", "Moderate"),
            ("I hate myself", "Moderate"),
            ("I cannot get out of bed", "Moderate"),
            ("nobody understands me", "Moderate"),
            ("I feel completely alone", "Moderate"),
            ("I am breaking down inside", "Moderate"),
            ("my mind is full of darkness", "Moderate"),
            ("I feel like dying inside but I will not act on it", "Moderate"),

            # ── Severe ──
            ("I want to die", "Severe"),
            ("I want to kill myself", "Severe"),
            ("I want to end my life", "Severe"),
            ("I feel like dying", "Severe"),
            ("I want to commit suicide", "Severe"),
            ("I have a plan to end it", "Severe"),
            ("there is no point in living", "Severe"),
            ("I am going to hang myself", "Severe"),
            ("I will take poison", "Severe"),
            ("I am better off dead", "Severe"),
            ("I should not be alive", "Severe"),
            ("nobody will miss me if I die", "Severe"),
            ("I cannot live anymore", "Severe"),
            ("I must die", "Severe"),
            ("I will die today", "Severe"),
            ("I feel like ending everything", "Severe"),
            ("I am going to end my life tonight", "Severe"),
            ("I have decided to die", "Severe"),
            ("I want to disappear forever", "Severe"),
            ("I am ready to die", "Severe"),
            ("dying seems like the only way out", "Severe"),
            ("I feel like I should not be here", "Severe"),
            ("I am thinking about suicide seriously", "Severe"),
        ]

        # Build simple word-overlap vectors (no external library needed)
        self._build_index()

    def _build_index(self):
        """Build vocabulary and TF vectors for all anchors."""
        # Build vocabulary from all anchors
        all_words = set()
        for text, _ in self.anchors:
            all_words.update(text.lower().split())
        self.vocab = sorted(all_words)
        self.word_to_idx = {w: i for i, w in enumerate(self.vocab)}

        # Vectorize all anchors
        self.anchor_vectors = []
        for text, _ in self.anchors:
            self.anchor_vectors.append(self._vectorize(text))
        self.anchor_vectors = np.array(self.anchor_vectors)

    def _vectorize(self, text: str) -> np.ndarray:
        """Convert text to a simple TF vector."""
        vec = np.zeros(len(self.vocab))
        words = text.lower().split()
        for w in words:
            if w in self.word_to_idx:
                vec[self.word_to_idx[w]] += 1
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def _cosine_sim(self, a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity between two vectors."""
        dot = np.dot(a, b)
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(dot / (na * nb))

    def detect(self, text: str, **kwargs) -> DetectionResult:
        """Find k nearest anchors and vote on label."""
        query = self._vectorize(text)

        # No shared vocabulary means the anchor bank has no evidence.  Previously
        # this could accidentally select the last (Severe) anchors on a zero vector.
        if not np.any(query):
            return DetectionResult(
                label="Uncertain", score=0.0,
                evidence=["No vocabulary overlap with the reference anchors"],
                detector_name=self.name,
            )

        # Compute similarities
        sims = [self._cosine_sim(query, av) for av in self.anchor_vectors]

        # Get top-k
        top_k_indices = np.argsort(sims)[-self.k:][::-1]
        top_k_labels = [self.anchors[i][1] for i in top_k_indices]
        top_k_sims = [sims[i] for i in top_k_indices]
        top_k_texts = [self.anchors[i][0] for i in top_k_indices]

        if not top_k_sims or top_k_sims[0] < 0.12:
            return DetectionResult(
                label="Uncertain", score=round(top_k_sims[0] if top_k_sims else 0.0, 3),
                evidence=["No sufficiently similar reference example"],
                detector_name=self.name,
            )

        # Vote (weighted by similarity)
        label_scores = {}
        for label, sim in zip(top_k_labels, top_k_sims):
            label_scores[label] = label_scores.get(label, 0) + sim

        # Winner
        best_label = max(label_scores, key=label_scores.get)
        best_score = label_scores[best_label] / sum(label_scores.values()) if label_scores else 0.0

        evidence = [f"Nearest: '{top_k_texts[0]}' ({top_k_labels[0]}, sim={top_k_sims[0]:.2f})"]

        return DetectionResult(
            label=best_label,
            score=round(best_score, 3),
            evidence=evidence,
            detector_name=self.name
        )
