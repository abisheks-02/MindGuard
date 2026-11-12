"""
Tanglish-to-English Translator
===============================
Comprehensive word-by-word and phrase-level translation for romanized Tamil (Tanglish).
Handles spelling variants, phonetic normalization, negation phrases, and common slang.
This is the single source of truth for Tanglish understanding in MindGuard.
"""

import re
from typing import Tuple


class TanglishTranslator:
    """Translates Tanglish (romanized Tamil written in English) to English."""

    def __init__(self):
        # ── Phrase-level translations (checked FIRST, order matters) ────────
        # Negated phrases must come before their positive counterparts
        self.phrases = [
            # Negated death/suicide phrases
            ("saga virupam illa", "I do not want to die"),
            ("saga virupam illai", "I do not want to die"),
            ("saaga virupam illa", "I do not want to die"),
            ("saaga virupam illai", "I do not want to die"),
            ("suicide panna mattan", "I will not commit suicide"),
            ("suicide panna matten", "I will not commit suicide"),
            ("saaga maatten", "I will not die"),
            ("saaga maaten", "I will not die"),
            ("saga maaten", "I will not die"),
            ("saga maatten", "I will not die"),
            ("sethukka maatten", "I will not kill myself"),
            ("sethukka maaten", "I will not kill myself"),

            # Negated distress
            ("kavalai illai", "I have no worry"),
            ("kavalai illa", "I have no worry"),
            ("bayam illai", "I have no fear"),
            ("bayam illa", "I have no fear"),
            ("sogam illai", "I am not sad"),
            ("sogam illa", "I am not sad"),
            ("tension illai", "I have no tension"),
            ("tension illa", "I have no tension"),
            ("problem illai", "no problem"),
            ("problem illa", "no problem"),

            # Positive compound phrases
            ("jolly aa iruken", "I am feeling happy"),
            ("jolly aa irukken", "I am feeling happy"),
            ("jolly a iruken", "I am feeling happy"),
            ("nalla iruken", "I am fine"),
            ("nalla irukken", "I am fine"),
            ("nalla iruku", "it is good"),
            ("romba nalla", "very good"),
            ("romba happy", "very happy"),
            ("super aa iruken", "I am feeling great"),
            ("santhosam aa iruken", "I am feeling happy"),
            ("nimmathi aa iruken", "I am feeling peaceful"),
            ("arumai aa iruken", "I am feeling wonderful"),
            
            # Distress compound phrases
            ("manasu romba kashtama iruku", "my heart is very troubled"),
            ("manasu kashtama iruku", "my heart is troubled"),
            ("uyir poguthu", "I am dying inside"),
            ("uyir poga", "to die"),
            ("saagalam pola iruku", "I feel like dying"),
            ("sagalam pola iruku", "I feel like dying"),
            ("sagalam pola", "feel like dying"),
            ("saagalam pola", "feel like dying"),
            # -- Additional phonetic variants added for accuracy --
            ("saaganum pola iruku", "I feel like dying"),
            ("saganum pola iruku", "I feel like dying"),
            ("saaganum pola", "feel like dying"),
            ("saganum pola", "feel like dying"),
            ("sagaanum pola iruku", "I feel like dying"),
            ("inaiku setha nalla irukum", "dying today would be good"),
            ("setha nalla irukum", "dying would be good"),
            ("setha irukalam", "could just die"),
            ("setha poidalam", "could just die"),
            ("sethu poiduven", "I will die"),
            ("sethuralam", "I feel like dying"),
            ("sethudalam", "let me die"),
            ("naan saaga poren", "I am going to die"),
            ("naan saga poren", "I am going to die"),
            ("ellame mudichukanum", "I want to end everything"),
            ("uyir vittuviduven", "I will end my life"),
            ("thookku pottukkanum", "I want to hang myself"),
            ("jeevikka mudiyala", "I cannot live"),
            ("vaazha mudiyala", "I cannot live"),
            ("vaazha virupam illa", "I have no desire to live"),
            ("endha hope um illai", "there is no hope"),
            ("evvalavu naal thaan", "how long can I endure"),
            ("enna pannalum sari aagala", "nothing I do works"),
            ("yaarum illai", "I have nobody"),
            ("yaaru kum theriyathu", "nobody knows"),
            ("payama iruku", "I am scared"),
            ("bayama iruku", "I am scared"),
            ("thoongi ezhunthukka mudiyala", "I cannot get out of bed"),
            ("thookam varathu", "I cannot sleep"),
            ("thookam varala", "I cannot sleep"),
            ("saapaadu pogala", "I have no appetite"),
            ("oru naalum nimmathi illa", "I never have peace"),
            ("yennoda life la meaning illa", "there is no meaning in my life"),
            ("life ku meaning illa", "life has no meaning"),
            ("ennaku kovam aa iruken", "I am very angry"),
            ("kovam aa iruku", "I am angry"),
            ("kanna katti", "feeling blindfolded by sadness"),
        ]

        # ── Word-level Tanglish→English dictionary ─────────────────────────
        self.word_map = {
            # ── Pronouns / subject ──
            "naan": "I", "na": "I", "yennaku": "to me", "enaku": "to me",
            "ennaku": "to me", "en": "my", "yenna": "me", "enna": "me",
            "nee": "you", "unnaku": "to you", "avan": "he", "aval": "she",
            "avanga": "they", "naanga": "we", "yaarum": "nobody",
            "ellorum": "everyone", "yaaru": "who",

            # ── Verbs / states ──
            "iruken": "I am", "irukken": "I am", "iruku": "it is",
            "irukku": "it is", "irundhen": "I was",
            "poren": "I am going", "poguthu": "it is going",
            "varum": "will come", "vandhu": "came",
            "solla": "to say", "sollu": "tell", "solren": "I say",
            "panna": "to do", "pannuven": "I will do", "panren": "I do",
            "mudiyala": "I cannot", "mudiyum": "I can", "mudiyathu": "cannot",
            "theriyathu": "I don't know", "theriyum": "I know",
            "venam": "I want", "vendum": "I want", "venaam": "I don't want",

            # ── Positive emotions ──
            "jolly": "happy", "santhosam": "happiness", "nalla": "good",
            "super": "great", "arumai": "wonderful", "nimmathi": "peace",
            "aasai": "desire", "love": "love", "happy": "happy",
            "fun": "fun", "enjoy": "enjoy",

            # ── Negative emotions ──
            "kavalai": "worry", "sogam": "sadness", "sogama": "sadly",
            "kaduppu": "anger", "kovam": "anger", "veruppu": "hatred",
            "bayam": "fear", "bayama": "fearfully", "payam": "fear",
            "lonely": "lonely", "alone": "alone", "hopeless": "hopeless",
            "kastam": "difficulty", "kashtam": "difficulty",
            "valikithu": "it hurts", "vali": "pain", "vedanai": "agony",
            "azhugai": "crying", "azhuren": "I am crying",
            "thanimai": "loneliness", "depression": "depression",
            "stress": "stress", "tension": "tension", "anxiety": "anxiety",
            "tired": "tired", "bored": "bored", "sad": "sad",
            "upset": "upset", "frustrated": "frustrated", "angry": "angry",

            # ── Severe / crisis ──
            "sagalam": "die", "saagalam": "die", "saaga": "die", "saga": "die",
            "suicide": "suicide", "sethuralam": "die", "sethukka": "kill myself",
            "sethiduven": "I will die", "saaganam": "I must die",
            "thookku": "hanging", "vidam": "poison",
            "tarkolai": "suicide", "kolai": "murder",
            "uyir": "life", "saavu": "death",

            # ── Negation ──
            "illa": "not", "illai": "not", "illaiye": "not at all",
            "mattan": "will not", "matten": "will not",
            "maatten": "will not", "maaten": "will not",
            "kidaiyathu": "not available",

            # ── Intensifiers ──
            "romba": "very", "rombave": "very much", "romba romba": "extremely",
            "oru": "one", "konjam": "a little", "konjamum": "not even a little",
            "ethukku": "why", "yen": "why", "epdi": "how",
            "evalavu": "how much", "evvalavu": "how much",

            # ── Connectors ──
            "pola": "like", "maadhiri": "like", "aal": "person",
            "aa": "", "um": "also", "la": "in", "ku": "to",
            "thaan": "only", "kuda": "even", "mattum": "only",
            "virupam": "desire", "aasai": "desire",

            # ── Time ──
            "ippo": "now", "ipo": "now", "innaiku": "today", "naalai": "tomorrow",
            "nethiku": "yesterday", "eppo": "when", "eppothum": "always",
            "oru naalum": "never",

            # ── Misc everyday ──
            "veedu": "home", "velai": "work", "padippu": "studies",
            "panam": "money", "friend": "friend", "family": "family",
            "amma": "mother", "appa": "father", "life": "life",
            "manasu": "heart", "thookam": "sleep", "saapaadu": "food",
        }

        # ── Phonetic normalization rules ───────────────────────────────────
        self._normalization_rules = [
            (r'(.)\1{2,}', r'\1'),     # collapse 3+ repeated chars → 1
            (r'aa+', 'a'),             # saaga → saga
            (r'ee+', 'e'),
            (r'oo+', 'o'),
            (r'ii+', 'i'),
            (r'uu+', 'u'),
            (r'th', 'th'),             # keep th digraph
        ]

    def normalize(self, text: str) -> str:
        """Phonetic normalization: collapse repeated vowels/chars."""
        text = text.lower().strip()
        for pattern, replacement in self._normalization_rules:
            text = re.sub(pattern, replacement, text)
        return text

    def translate(self, text: str) -> Tuple[str, float]:
        """
        Translate Tanglish text to English.
        
        Returns:
            (translated_text, tanglish_ratio)
            tanglish_ratio: fraction of words that were translated (0.0 = pure English)
        """
        if not text or not text.strip():
            return ("", 0.0)

        working = text.lower().strip()

        # 1. Replace known phrases first (longest match first)
        for tanglish_phrase, eng_phrase in self.phrases:
            if tanglish_phrase in working:
                working = working.replace(tanglish_phrase, eng_phrase)

        # 2. Word-by-word translation for remaining Tanglish words
        words = working.split()
        translated = []
        tanglish_count = 0
        total_words = 0

        for word in words:
            clean = re.sub(r'[^\w]', '', word)
            if not clean:
                continue
            total_words += 1

            # Try exact match first
            if clean in self.word_map:
                eng = self.word_map[clean]
                if eng:  # skip empty translations (particles like "aa")
                    translated.append(eng)
                tanglish_count += 1
                continue

            # Try normalized match
            norm = self.normalize(clean)
            if norm in self.word_map:
                eng = self.word_map[norm]
                if eng:
                    translated.append(eng)
                tanglish_count += 1
                continue

            # Keep English words as-is
            translated.append(clean)

        result = " ".join(translated)
        ratio = tanglish_count / max(total_words, 1)
        return (result, ratio)

    def is_tanglish(self, text: str) -> bool:
        """Returns True if text contains significant Tanglish content."""
        _, ratio = self.translate(text)
        return ratio > 0.2
