"""Safety regressions for the detector used by the API."""

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.detection.context_analyzer import ContextAnalyzer
from app.services.detection.embedding_knn import EmbeddingKNNDetector
from app.services.detection.ensemble import EnsembleDetectionService


def test_knn_abstains_when_the_anchor_bank_has_no_evidence():
    result = EmbeddingKNNDetector().detect("qxzv blorpt zzzz")
    assert result.label == "Uncertain"
    assert result.score == 0.0


def test_negation_must_be_scoped_to_a_risk_phrase():
    analyzer = ContextAnalyzer()
    assert analyzer.analyze("I do not want to die").is_negated is True
    assert analyzer.analyze("I don't know what to do. I want to die").is_negated is False


def test_explicit_first_person_intent_is_not_diluted_by_abstention():
    result = EnsembleDetectionService().analyze("I want to die")
    assert result["predicted_class"] == "Severe"
    assert result["needs_review"] is True


def test_chat_request_contract_uses_text_not_message():
    from app.schemas.chat import ChatMessageRequest

    request = ChatMessageRequest.model_validate({
        "session_id": "test", "text": "Hello", "severity": "Normal"
    })
    assert request.text == "Hello"


def test_production_configuration_rejects_demo_switches():
    from app.config import Settings, validate_runtime_settings

    settings = Settings(
        ENVIRONMENT="production",
        DATABASE_URL="postgresql://example",
        CORS_ORIGINS=["https://app.example.com"],
        SECRET_KEY="real-secret",
        MINDGUARD_PRIVACY_SECRET="real-privacy-secret",
        ENABLE_DEMO_AUTH=True,
        ENABLE_MOCK_ESCALATION=False,
    )
    try:
        validate_runtime_settings(settings)
    except RuntimeError as error:
        assert "ENABLE_DEMO_AUTH" in str(error)
    else:
        raise AssertionError("unsafe production configuration was accepted")
