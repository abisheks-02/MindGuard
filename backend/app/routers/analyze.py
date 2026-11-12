"""
Text analysis router — Privacy-hardened.
Every request:
  1. Pseudonymizes the session ID (HMAC-SHA256) before any DB write
  2. Stores NO raw text — only severity label, confidence, CSI, language
  3. Auto-purges trajectory records older than DATA_RETENTION_DAYS
  4. Returns privacy-enforcing HTTP headers
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Response
from sqlalchemy.orm import Session

from app.schemas.analyze import AnalyzeRequest, FeedbackRequest
from app.services.detection import DetectionService
from app.dependencies import get_detection_service
from app.db import get_db
from app.models.feedback import Feedback
from app.models.risk_trajectory import RiskTrajectory
from app.services.privacy import (
    pseudonymize_session,
    anonymize_text,
    purge_expired_records,
    get_privacy_headers,
)

router = APIRouter(tags=["analyze"])

SEVERITY_SCORE = {"Normal": 0, "Mild": 1, "Moderate": 2, "Severe": 3}


def _save_trajectory_private(db: Session, raw_session_id: str, result: dict, raw_text: str):
    """
    Background task: persist analysis result with full privacy protection.
    - Session ID is pseudonymized (HMAC hash) — original is NOT stored
    - Text is NOT stored — only its anonymized fingerprint for audit
    - Auto-purges expired records (rolling retention window)
    """
    try:
        # 1. Pseudonymize session
        session_hash = pseudonymize_session(raw_session_id)

        # 2. Auto-purge old records first (rolling window)
        purge_expired_records(db, session_hash)

        # 3. Store ONLY non-sensitive metadata
        label = result.get("predicted_class", "Normal")
        csi_ratio = result.get("code_switching", {}).get("ratio", 0) / 100.0

        entry = RiskTrajectory(
            session_id=session_hash,           # pseudonymized
            severity_label=label,
            severity_score=SEVERITY_SCORE.get(label, 0),
            confidence=result.get("confidence", 0) / 100.0,
            csi=round(csi_ratio, 3),
            # text_snippet stores only an anonymous hash fingerprint, NOT the raw text
            text_snippet=anonymize_text(raw_text),
            language=result.get("code_switching", {}).get("status", "English"),
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()


@router.post("/analyze")
def analyze_text(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    detection: DetectionService = Depends(get_detection_service),
    db: Session = Depends(get_db),
):
    result = detection.analyze(request.text)

    # Add privacy HTTP headers to every response
    for key, value in get_privacy_headers().items():
        response.headers[key] = value

    # Persist trajectory privately in background
    raw_session_id = getattr(request, "session_id", "anonymous")
    background_tasks.add_task(
        _save_trajectory_private, db, raw_session_id, result, request.text
    )

    return result


@router.post("/feedback")
def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    fb = Feedback(
        session_id="demo_user_001",
        analysis_id=request.analysis_id,
        text="",
        predicted_label="Unknown",
        correct_label=request.correct_label
    )
    db.add(fb)
    db.commit()
    return {"status": "success", "message": "Feedback recorded for retraining."}
