"""Offline translation smoke test; no third-party translation API is used."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.detection.tanglish_translator import TanglishTranslator


def test_tanglish_phrase_translation():
    translated, ratio = TanglishTranslator().translate("jolly aa iruken")
    assert "happy" in translated.lower()
    assert ratio > 0
