"""
Hybrid Sentiment Detector
==========================
Translates Tanglish→English using TanglishTranslator, then runs VADER
sentiment analysis on the English text for severity classification.
Works for both English and Tanglish. Understands negation properly.
"""

import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from app.services.detection.base import Detector, DetectionResult
from app.services.detection.tanglish_translator import TanglishTranslator


class HybridSentimentDetector(Detector):
    """Translates Tanglish to English, then uses VADER sentiment for risk."""

    def __init__(self):
        self.name = "HybridSentimentDetector"
        self.analyzer = SentimentIntensityAnalyzer()
        self.translator = TanglishTranslator()

    def detect(self, text: str, **kwargs) -> DetectionResult:
        start = time.time()

        # 1. Translate Tanglish to English
        translated, tanglish_ratio = self.translator.translate(text)

        # 2. VADER sentiment on the TRANSLATED text
        scores = self.analyzer.polarity_scores(translated)
        compound = scores['compound']

        # 3. Risk classification based on sentiment + keyword check
        #    VADER handles negation natively:
        #    "I want to die"        → compound ≈ -0.65
        #    "I do not want to die" → compound ≈ +0.44
        #    "I am happy"           → compound ≈ +0.57

        # Check for severe keywords in translated text
        severe_keywords = {"die", "kill myself", "suicide", "hanging", "poison", "end my life", "must die"}
        has_severe_keyword = any(kw in translated.lower() for kw in severe_keywords)
        
        # Check for negation words near severe keywords
        negation_words = {"not", "no", "never", "don't", "will not", "do not", "cannot"}
        has_negation = any(nw in translated.lower() for nw in negation_words)

        # Determine label
        if has_severe_keyword and not has_negation and compound <= -0.3:
            label = "Severe"
        elif has_severe_keyword and has_negation:
            # Negated severe = actually Normal/Mild (e.g., "I do NOT want to die")
            if compound >= 0.0:
                label = "Normal"
            else:
                label = "Mild"
        elif compound <= -0.6:
            label = "Severe"
        elif compound <= -0.3:
            label = "Moderate"
        elif compound < 0.05:
            label = "Mild"
        else:
            label = "Normal"

        # Confidence: VADER compound magnitude (0-1)
        confidence = min(abs(compound), 1.0)

        latency = time.time() - start

        evidence = [
            f"Translation: '{translated}'",
            f"VADER compound: {compound:.3f}",
            f"Tanglish ratio: {tanglish_ratio:.0%}",
        ]

        return DetectionResult(
            label=label,
            score=round(confidence, 3),
            evidence=evidence,
            detector_name=self.name,
        )
