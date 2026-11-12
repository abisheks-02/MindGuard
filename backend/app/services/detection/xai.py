import re
from typing import List, Dict

class XAIService:
    @staticmethod
    def occlusion_fallback(text: str, detector, baseline_score: float) -> List[Dict]:
        """
        Leave-one-word-out occlusion for texts under 40 tokens.
        Finds the words that caused the biggest drop in severity score.
        """
        words = text.split()
        if len(words) > 40:
            return [] # Too long for rapid fallback
            
        token_scores = []
        for i, word in enumerate(words):
            # Occlude word
            occluded_text = " ".join(words[:i] + words[i+1:])
            res = detector.detect(occluded_text)
            
            # Impact = Baseline - Occluded (high drop = high importance)
            impact = max(0, baseline_score - res.score)
            token_scores.append({"text": word + " ", "weight": impact})
            
        return XAIService.normalize_scores(token_scores)

    @staticmethod
    def extract_lexicon_offsets(text: str, matches: List[str]) -> List[Dict]:
        """Generates weights based on exact lexicon matches."""
        words = text.split()
        token_scores = []
        
        for w in words:
            # Simple match
            is_match = any(m in w.lower() for m in matches)
            weight = 1.0 if is_match else 0.0
            token_scores.append({"text": w + " ", "weight": weight})
            
        return XAIService.normalize_scores(token_scores)

    @staticmethod
    def normalize_scores(token_scores: List[Dict]) -> List[Dict]:
        """Normalizes weights strictly to 0.0 - 1.0 range for UI coloring."""
        if not token_scores:
            return []
            
        max_w = max(t["weight"] for t in token_scores)
        if max_w == 0:
            return token_scores
            
        return [{"text": t["text"], "weight": t["weight"] / max_w} for t in token_scores]
        
    @staticmethod
    def merge_explanations(ensemble_res, lex_matches: List[str], text: str) -> List[Dict]:
        """Merges XAI inputs into one token_scores list."""
        # For this implementation, if Lexicon matched, we use its offsets.
        # Otherwise, if we had a fallback occlusion, we'd run it here.
        # For speed, we just return the lexicon offsets.
        return XAIService.extract_lexicon_offsets(text, lex_matches)
