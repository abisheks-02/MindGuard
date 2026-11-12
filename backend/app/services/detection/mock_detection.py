"""
Mock / lexicon-based detection for running without a GPU.
"""

import logging
from app.services.detection import DetectionService

logger = logging.getLogger(__name__)

SEVERE_PHRASES = ["sethuduven", "vaazha pudikala", "end pannidalam", "suicide", "die", "sagalam"]
MODERATE_PHRASES = ["romba tension", "control panna mudiyala", "broken", "pain"]
MILD_PHRASES = ["romba tired", "bored", "mood off", "down", "sad"]


class MockDetectionService(DetectionService):
    """Fast lexicon-based fallback — no model required."""

    def analyze(self, text: str) -> dict:
        text_lower = text.lower()
        score = 0
        highlighted: list[dict] = []

        for w in text.split():
            w_l = w.lower()
            if any(p in w_l for p in SEVERE_PHRASES):
                score += 3
                highlighted.append({"text": f"{w} ", "weight": 3})
            elif any(p in w_l for p in MODERATE_PHRASES):
                score += 2
                highlighted.append({"text": f"{w} ", "weight": 2})
            elif any(p in w_l for p in MILD_PHRASES):
                score += 1
                highlighted.append({"text": f"{w} ", "weight": 1})
            else:
                highlighted.append({"text": f"{w} ", "weight": 0})

        if score >= 3:
            p_class, probs = "Severe", {"Normal": 5, "Mild": 15, "Moderate": 20, "Severe": 60}
        elif score == 2:
            p_class, probs = "Moderate", {"Normal": 10, "Mild": 20, "Moderate": 60, "Severe": 10}
        elif score == 1:
            p_class, probs = "Mild", {"Normal": 30, "Mild": 60, "Moderate": 10, "Severe": 0}
        else:
            p_class, probs = "Normal", {"Normal": 85, "Mild": 10, "Moderate": 5, "Severe": 0}

        return {
            "predicted_class": p_class,
            "confidence": probs[p_class],
            "shap_tokens": highlighted,
            "class_probabilities": probs,
            "translation": "",
            "code_switching": {"ratio": 0, "status": "Standard Variance"},
        }
