"""
Input Gate
==========
Sanitizes, classifies, and guards all user input BEFORE it reaches any detector.
Handles: empty, gibberish, emoji-only, unsupported language, PII scrub,
prompt injection, and length capping.
"""

import re
import math
import unicodedata
from typing import Dict, Optional
from collections import Counter


class InputGate:
    """Pre-processes and classifies user input before detection."""

    MAX_CHARS = 2000

    # Common English words for dictionary check
    ENGLISH_WORDS = {
        "i", "me", "my", "am", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "can", "may", "might", "shall", "the", "a", "an", "and",
        "or", "but", "if", "then", "so", "not", "no", "yes", "it", "its",
        "he", "she", "they", "we", "you", "him", "her", "them", "us",
        "this", "that", "these", "those", "what", "which", "who", "whom",
        "how", "when", "where", "why", "all", "each", "every", "both",
        "few", "more", "most", "other", "some", "such", "very", "just",
        "only", "own", "same", "than", "too", "also", "here", "there",
        "now", "then", "always", "never", "often", "still", "already",
        "about", "after", "before", "between", "during", "from", "into",
        "through", "with", "without", "of", "for", "to", "at", "by", "in",
        "on", "up", "down", "out", "off", "over", "under", "again",
        "happy", "sad", "good", "bad", "great", "fine", "okay", "well",
        "feel", "feeling", "want", "need", "help", "think", "know",
        "like", "love", "hate", "life", "live", "die", "dead", "death",
        "pain", "hurt", "cry", "sleep", "eat", "work", "home", "family",
        "friend", "alone", "lonely", "tired", "stress", "anxiety",
        "depression", "suicide", "kill", "afraid", "scared", "worried",
    }

    # Known Tanglish words (romanized Tamil)
    TANGLISH_WORDS = {
        "naan", "na", "yennaku", "enaku", "ennaku", "en", "yenna", "enna",
        "nee", "unnaku", "avan", "aval", "avanga", "naanga",
        "iruken", "irukken", "iruku", "irukku", "poren", "poguthu",
        "mudiyala", "mudiyum", "mudiyathu", "theriyathu", "theriyum",
        "jolly", "santhosam", "nalla", "arumai", "nimmathi",
        "kavalai", "sogam", "sogama", "kaduppu", "kovam", "veruppu",
        "bayam", "bayama", "payam", "kastam", "kashtam",
        "valikithu", "vali", "vedanai", "azhugai", "azhuren",
        "sagalam", "saagalam", "saaga", "saga", "sethuralam", "sethukka",
        "tarkolai", "thookku", "vidam",
        "illa", "illai", "illaiye", "mattan", "matten", "maatten", "maaten",
        "romba", "rombave", "konjam", "ethukku", "yen", "epdi",
        "pola", "maadhiri", "aa", "um", "la", "ku", "thaan",
        "ippo", "ipo", "innaiku", "naalai", "nethiku",
        "veedu", "velai", "padippu", "panam", "amma", "appa",
        "manasu", "thookam", "saapaadu", "virupam",
        "super", "pannuven", "panren", "panna",
    }

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"you\s+are\s+now\s+a",
        r"act\s+as\s+(if|a)",
        r"system\s*:\s*",
        r"user\s*:\s*",
        r"assistant\s*:\s*",
        r"forget\s+(everything|all|your)",
        r"new\s+instructions?\s*:",
        r"override\s+(your|the|all)",
        r"disregard\s+(your|the|all|previous)",
        r"\[INST\]",
        r"\[/INST\]",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"###\s*(System|Human|Assistant)",
    ]

    def process(self, text: str) -> Dict:
        """
        Process input text through the gate.
        
        Returns:
            {
                "status": "ok" | "empty" | "gibberish" | "emoji_only" | 
                          "unsupported_language" | "injection_blocked",
                "cleaned_text": str,
                "language": "english" | "tanglish" | "mixed" | "unknown",
                "injection_detected": bool,
                "message": str | None  (soft message for non-ok status)
            }
        """
        # 1. Handle empty/whitespace
        if not text or not text.strip():
            return {
                "status": "empty",
                "cleaned_text": "",
                "language": "unknown",
                "injection_detected": False,
                "message": "Please type something so I can help you."
            }

        # 2. Strip control characters, cap length
        cleaned = self._sanitize(text)

        # 3. PII scrub (remove phone numbers, emails, URLs)
        cleaned = self._scrub_pii(cleaned)

        # 4. Check for prompt injection
        injection = self._check_injection(cleaned)
        if injection:
            return {
                "status": "ok",  # still process, but log the attempt
                "cleaned_text": cleaned,
                "language": self._detect_language(cleaned),
                "injection_detected": True,
                "message": None
            }

        # 5. Check emoji-only
        if self._is_emoji_only(cleaned):
            return {
                "status": "emoji_only",
                "cleaned_text": cleaned,
                "language": "unknown",
                "injection_detected": False,
                "message": "I see your emoji! Could you tell me a bit more about how you're feeling in words?"
            }

        # 6. Check gibberish (high entropy + low dictionary hit)
        if self._is_gibberish(cleaned):
            return {
                "status": "gibberish",
                "cleaned_text": cleaned,
                "language": "unknown",
                "injection_detected": False,
                "message": "I'm not sure I understood that. Could you try again?"
            }

        # 7. Detect language / script
        language = self._detect_language(cleaned)

        # 8. Check for Tamil script (unsupported — we only do Tanglish + English)
        if language == "tamil_script":
            return {
                "status": "unsupported_language",
                "cleaned_text": cleaned,
                "language": "tamil_script",
                "injection_detected": False,
                "message": "I currently support English and Tanglish (Tamil written in English letters). Please try typing in English or Tanglish. If you need help now, call Tele-MANAS: 14416."
            }

        if language == "other_script":
            return {
                "status": "unsupported_language",
                "cleaned_text": cleaned,
                "language": "other",
                "injection_detected": False,
                "message": "I currently support English and Tanglish only. If you need help, call Tele-MANAS: 14416."
            }

        return {
            "status": "ok",
            "cleaned_text": cleaned,
            "language": language,
            "injection_detected": False,
            "message": None
        }

    def _sanitize(self, text: str) -> str:
        """Strip control chars, normalize whitespace, cap length."""
        # Remove control characters except newlines
        text = "".join(
            c for c in text
            if unicodedata.category(c) not in ('Cc', 'Cf') or c in ('\n', '\t')
        )
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Cap length
        return text[:self.MAX_CHARS]

    def _scrub_pii(self, text: str) -> str:
        """Remove phone numbers, emails, URLs for privacy."""
        # Phone numbers (Indian and international)
        text = re.sub(r'\+?\d[\d\s\-]{8,}\d', '[PHONE]', text)
        # Email addresses
        text = re.sub(r'\b[\w.+-]+@[\w-]+\.[\w.]+\b', '[EMAIL]', text)
        # URLs
        text = re.sub(r'https?://\S+', '[URL]', text)
        text = re.sub(r'www\.\S+', '[URL]', text)
        return text

    def _check_injection(self, text: str) -> bool:
        """Check for prompt injection attempts."""
        lower = text.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, lower, re.IGNORECASE):
                return True
        return False

    def _is_emoji_only(self, text: str) -> bool:
        """Check if text is only emojis and whitespace."""
        non_emoji = re.sub(
            r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF'
            r'\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF'
            r'\U00002702-\U000027B0\U0000FE00-\U0000FE0F'
            r'\U0000200D\U00002640\U00002642\s]+',
            '', text
        )
        return len(non_emoji.strip()) == 0 and len(text.strip()) > 0

    def _is_gibberish(self, text: str) -> bool:
        """Detect gibberish using character entropy + dictionary check."""
        words = re.findall(r'[a-zA-Z]+', text.lower())
        if not words:
            return False
        
        # Check dictionary hit rate
        known_count = sum(
            1 for w in words 
            if w in self.ENGLISH_WORDS or w in self.TANGLISH_WORDS
        )
        hit_rate = known_count / len(words)
        
        # If more than 30% of words are recognized, it's not gibberish
        if hit_rate > 0.3:
            return False

        # Check character-level entropy
        all_chars = "".join(words)
        if len(all_chars) < 4:
            return False
        freq = Counter(all_chars)
        entropy = -sum(
            (c / len(all_chars)) * math.log2(c / len(all_chars))
            for c in freq.values()
        )
        
        # Very high entropy with no dictionary matches = gibberish
        return entropy > 3.5 and hit_rate < 0.15

    def _detect_language(self, text: str) -> str:
        """Detect if text is English, Tanglish, Tamil script, or other."""
        # Check for Tamil Unicode script (we don't support this)
        tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        if tamil_chars > len(text) * 0.3:
            return "tamil_script"

        # Check for other non-Latin scripts
        non_latin = sum(
            1 for c in text 
            if c.isalpha() and not c.isascii()
            and not ('\u0B80' <= c <= '\u0BFF')
        )
        if non_latin > len(text) * 0.3:
            return "other_script"

        # Count Tanglish vs English words
        words = re.findall(r'[a-zA-Z]+', text.lower())
        if not words:
            return "unknown"

        tanglish_count = sum(1 for w in words if w in self.TANGLISH_WORDS)
        english_count = sum(1 for w in words if w in self.ENGLISH_WORDS)

        total = len(words)
        if tanglish_count > 0 and english_count > 0:
            return "mixed"  # Tanglish + English
        elif tanglish_count > total * 0.3:
            return "tanglish"
        else:
            return "english"
