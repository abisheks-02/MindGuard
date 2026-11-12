"""
Context Analyzer
================
Analyzes linguistic context: subject (self/other/quote), tense, negation,
sarcasm/hyperbole indicators, intensity, and tone.
This feeds into the aggregator to prevent false positives.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class ContextSignals:
    """Linguistic context signals extracted from user text."""
    subject: str          # "self", "other", "quote", "general"
    tense: str            # "present", "past", "future", "unknown"
    is_negated: bool      # True if the core intent is negated
    negation_words: List[str]
    is_sarcastic: bool    # Rough heuristic for sarcasm
    is_hyperbolic: bool   # "literally dying" type expressions
    intensity: float      # 0.0 (neutral) to 1.0 (extreme)
    tone: str             # "formal", "casual", "slang"
    is_question: bool     # "should I worry?" vs "I want to die"
    is_command: bool      # "tell me a joke" vs personal statement


class ContextAnalyzer:
    """Extracts linguistic context signals from text."""

    SELF_MARKERS = {
        "i", "me", "my", "myself", "i'm", "im", "i've", "ive",
        "naan", "na", "yennaku", "enaku", "ennaku", "en", "yenna", "enna",
        "iruken", "irukken", "poren", "azhuren",
    }

    OTHER_MARKERS = {
        "he", "she", "they", "him", "her", "them", "his",
        "friend", "avan", "aval", "avanga", "someone", "people",
    }

    QUOTE_MARKERS = {
        "said", "told", "says", "heard", "read", "quote",
        "sonnan", "sonnal", "sonnanga",
    }

    NEGATION_WORDS = {
        "not", "no", "never", "don't", "dont", "doesn't", "doesnt",
        "didn't", "didnt", "won't", "wont", "can't", "cant",
        "couldn't", "couldnt", "wouldn't", "wouldnt", "shouldn't",
        "illa", "illai", "illaiye", "mattan", "matten", "maatten",
        "maaten", "kidaiyathu", "venaam",
    }

    PAST_MARKERS = {
        "was", "were", "did", "had", "felt", "went", "thought",
        "irundhen", "ponaan", "vandhu",
    }

    FUTURE_MARKERS = {
        "will", "gonna", "going to", "plan to", "want to",
        "pannuven", "poven", "varuven",
    }

    SARCASM_PATTERNS = [
        r"oh\s+(great|wonderful|fantastic|amazing)",
        r"yeah\s+right",
        r"sure\s+sure",
        r"totally\s+(fine|okay|good)",
        r"like\s+I\s+care",
    ]

    HYPERBOLE_PATTERNS = [
        r"literally\s+dying",
        r"I\s+could\s+die",
        r"killing\s+me",
        r"death\s+of\s+me",
        r"I'm\s+dead",  # slang for laughter
    ]

    INTENSIFIERS = {
        "very", "really", "extremely", "so", "too", "absolutely",
        "completely", "totally", "incredibly", "terribly",
        "romba", "rombave", "romba romba", "migavum",
    }

    def analyze(self, text: str, translated_text: str = "") -> ContextSignals:
        """Analyze text for context signals. Uses both original and translated text."""
        lower = text.lower()
        trans_lower = translated_text.lower() if translated_text else lower
        words = set(re.findall(r'[a-zA-Z\']+', lower))
        all_words = set(re.findall(r'[a-zA-Z\']+', trans_lower)) | words

        # Subject detection
        subject = self._detect_subject(all_words)

        # Tense detection
        tense = self._detect_tense(all_words)

        # Negation detection
        negation_found = all_words & self.NEGATION_WORDS
        # A negation elsewhere must not erase a risk statement: “I don't know
        # what to do; I want to die” is not a negated wish.
        is_negated = self._is_risk_negated(lower) or self._is_risk_negated(trans_lower)

        # Sarcasm detection
        is_sarcastic = any(
            re.search(p, lower, re.IGNORECASE) or re.search(p, trans_lower, re.IGNORECASE)
            for p in self.SARCASM_PATTERNS
        )

        # Hyperbole detection
        is_hyperbolic = any(
            re.search(p, lower, re.IGNORECASE) or re.search(p, trans_lower, re.IGNORECASE)
            for p in self.HYPERBOLE_PATTERNS
        )

        # Intensity
        intensity_count = len(all_words & self.INTENSIFIERS)
        intensity = min(intensity_count / 3.0, 1.0)

        # Tone
        tone = self._detect_tone(lower)

        # Question detection
        is_question = lower.strip().endswith("?") or any(
            lower.strip().startswith(w) for w in ["what", "how", "why", "when", "where", "who", "is it", "can i", "should i"]
        )

        # Command detection
        is_command = any(
            lower.strip().startswith(w) for w in ["tell", "show", "give", "find", "search", "calculate", "explain"]
        )

        return ContextSignals(
            subject=subject,
            tense=tense,
            is_negated=is_negated,
            negation_words=list(negation_found),
            is_sarcastic=is_sarcastic,
            is_hyperbolic=is_hyperbolic,
            intensity=intensity,
            tone=tone,
            is_question=is_question,
            is_command=is_command,
        )

    def _detect_subject(self, words: set) -> str:
        if words & self.QUOTE_MARKERS:
            return "quote"
        if words & self.SELF_MARKERS:
            return "self"
        if words & self.OTHER_MARKERS:
            return "other"
        return "general"

    def _detect_tense(self, words: set) -> str:
        has_past = bool(words & self.PAST_MARKERS)
        has_future = bool(words & self.FUTURE_MARKERS)
        if has_future:
            return "future"
        if has_past:
            return "past"
        return "present"

    def _detect_tone(self, text: str) -> str:
        slang_markers = ["lol", "lmao", "bruh", "bro", "da", "dei", "macha", "dude"]
        if any(m in text.split() for m in slang_markers):
            return "slang"
        if re.search(r'[!]{2,}|[.]{3,}', text):
            return "casual"
        return "casual"  # default for chat

    def _is_risk_negated(self, text: str) -> bool:
        """Return true only when a negation scopes a self-harm risk term."""
        tokens = re.findall(r"[a-zA-Z']+", text.lower())
        risk_terms = {"die", "dying", "suicide", "kill", "sagalam", "saagalam", "sethuduven"}
        for index, token in enumerate(tokens):
            if token not in risk_terms:
                continue
            # Tanglish commonly places the negation after the thought, e.g.
            # “saagalam ... illa”, so include a short following window too.
            if any(word in self.NEGATION_WORDS for word in tokens[max(0, index - 4): index + 6]):
                return True
        return False
