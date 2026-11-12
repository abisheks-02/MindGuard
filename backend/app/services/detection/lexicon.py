import json
import re
import os
from rapidfuzz import process, fuzz
from typing import List

from app.services.detection.base import Detector, DetectionResult

class LexiconDetector(Detector):
    def __init__(self, lexicon_path: str = "data/lexicon.json", fuzz_threshold: float = 85.0):
        self.fuzz_threshold = fuzz_threshold
        self.name = "LexiconDetector"
        
        # Load lexicon
        if not os.path.exists(lexicon_path):
            lexicon_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", lexicon_path)
            
        with open(lexicon_path, 'r', encoding='utf-8') as f:
            lexicon = json.load(f)
            
        self.severe_terms = [self.normalize(t) for t in lexicon.get("Severe", [])]
        self.moderate_terms = [self.normalize(t) for t in lexicon.get("Moderate", [])]
        self.mild_terms = [self.normalize(t) for t in lexicon.get("Mild", [])]
        self.negations = [self.normalize(t) for t in lexicon.get("Negation", [])]

    def normalize(self, text: str) -> str:
        """Lowercases, collapses repeated chars (e.g. 'saagaaalaam' -> 'sagalam')."""
        text = text.lower()
        # Collapse 3 or more repeated characters into 1
        text = re.sub(r'(.)\1{2,}', r'\1', text)
        # Specific variants collapsing (e.g. double letters commonly misused)
        text = re.sub(r'(a)\1+', r'\1', text) # saaga -> saga
        text = re.sub(r'(e)\1+', r'\1', text)
        text = re.sub(r'(o)\1+', r'\1', text)
        return text.strip()

    def has_negation(self, text: str) -> bool:
        """Detect a negation only when it scopes a self-harm term.

        A global ``can't`` check incorrectly down-ranked statements such as
        “can't take this pain anymore”.  It is protective only near terms such
        as ``die`` or ``suicide``.
        """
        words = re.findall(r"[a-zA-Z']+", self.normalize(text))
        risk_terms = {"die", "dying", "suicide", "kill", "sagalam", "saagalam", "sethuduven", "seththudalam"}
        for index, word in enumerate(words):
            if word in risk_terms and any(neg in words[max(0, index - 4): index + 6] for neg in self.negations):
                return True
        return False

    def check_category(self, text: str, category_terms: List[str]) -> List[str]:
        """Fuzzy matches terms against the text."""
        matched = []
        text_words = text.split()
        for term in category_terms:
            # Substring exact match
            if term in text:
                matched.append(term)
                continue

            term_words = term.split()
            if len(term_words) == 1:
                # Single words may tolerate a close spelling variant.
                for word in text_words:
                    if len(word) >= 4 and fuzz.ratio(term, word) >= self.fuzz_threshold:
                        matched.append(word)
                        break
            else:
                # Never use partial_ratio against the complete message: a short
                # input such as “hi” can otherwise match a substring inside a
                # long crisis phrase. Compare only equal-length token windows.
                size = len(term_words)
                for start in range(max(0, len(text_words) - size + 1)):
                    candidate = " ".join(text_words[start:start + size])
                    if fuzz.ratio(term, candidate) >= self.fuzz_threshold:
                        matched.append(candidate)
                        break
                
        return list(set(matched))

    def detect(self, text: str) -> DetectionResult:
        norm_text = self.normalize(text)
        
        # If negated, aggressively downrank severe claims
        is_negated = self.has_negation(norm_text)
        
        severe_matches = self.check_category(norm_text, self.severe_terms)
        if severe_matches and not is_negated:
            return DetectionResult(
                label="Severe",
                score=0.9,
                evidence=severe_matches,
                detector_name=self.name
            )
            
        moderate_matches = self.check_category(norm_text, self.moderate_terms)
        if moderate_matches:
            # If severe was found but negated, it drops to Moderate/Mild.
            return DetectionResult(
                label="Moderate",
                score=0.7,
                evidence=moderate_matches + (severe_matches if is_negated else []),
                detector_name=self.name
            )
            
        mild_matches = self.check_category(norm_text, self.mild_terms)
        if mild_matches:
            return DetectionResult(
                label="Mild",
                score=0.4,
                evidence=mild_matches,
                detector_name=self.name
            )
            
        return DetectionResult(
            label="Normal",
            score=0.0,
            evidence=[],
            detector_name=self.name
        )
