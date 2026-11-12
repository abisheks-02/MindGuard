"""Repository-level smoke tests for the current FastAPI backend layout."""

import sys
from pathlib import Path

BACKEND = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND))

from app.services.detection.ensemble import EnsembleDetectionService


def test_detector_returns_the_public_response_contract():
    result = EnsembleDetectionService().analyze("I feel low after work today")

    assert result["status"] == "ok"
    assert result["predicted_class"] in {"Normal", "Mild", "Moderate", "Severe", "Uncertain"}
    assert isinstance(result["confidence"], int)
    assert "disclaimer" in result
