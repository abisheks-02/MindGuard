import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.services.detection.lexicon import LexiconDetector

@pytest.fixture
def detector():
    return LexiconDetector(lexicon_path="data/lexicon.json")

def test_normalization(detector):
    assert detector.normalize("saagaaalaam") == "sagalam"
    assert detector.normalize("heeeelllppp") == "help"

def test_exact_matches(detector):
    res = detector.detect("I want to kill myself")
    assert res.label == "Severe"
    assert "kill myself" in res.evidence

def test_tanglish_variants(detector):
    # Misspellings and variants of "sagalam pola iruku"
    variants = [
        "sagalam pola iruku",
        "saagalam pola irukku",
        "sagalm pola irku",
        "seththudalam"
    ]
    for v in variants:
        res = detector.detect(v)
        assert res.label == "Severe", f"Failed on variant: {v}"

def test_negation_handling(detector):
    res = detector.detect("I would never kill myself")
    assert res.label != "Severe"
    
    res2 = detector.detect("saagalam nu thonuchu aana illa")
    assert res2.label != "Severe"

def test_mild_moderate(detector):
    assert detector.detect("I am feeling very tired").label == "Mild"
    assert detector.detect("I am a huge burden to my family").label == "Moderate"

def test_short_greeting_does_not_fuzzy_match_a_crisis_phrase(detector):
    assert detector.detect("hi").label == "Normal"
