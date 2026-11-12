"""
Privacy & Data Rights Router
==============================
Provides GDPR/DPDP (India Data Protection) compliant endpoints:
- GET  /privacy/policy     — Returns the data handling policy
- POST /privacy/delete     — User can request deletion of all their data
- GET  /privacy/my-data    — User can see what data is stored about them
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from app.db import get_db
from app.models.risk_trajectory import RiskTrajectory
from app.services.privacy import pseudonymize_session, purge_expired_records, DATA_RETENTION_DAYS

router = APIRouter(prefix="/privacy", tags=["privacy"])


class DeleteRequest(BaseModel):
    session_id: str
    confirm: bool = False


@router.get("/policy")
def get_privacy_policy():
    """Returns the data handling policy in machine-readable form."""
    return {
        "app": "MindGuard",
        "version": "2.0",
        "policy_summary": {
            "what_we_store": [
                "Severity label (Normal / Mild / Moderate / Severe)",
                "AI confidence score (numeric)",
                "Code-Switching Index — Tanglish ratio (numeric)",
                "Detected language (English / Tanglish / Mixed)",
                "Anonymous session hash (HMAC-SHA256 pseudonym, not reversible)",
                "Timestamp of each message",
            ],
            "what_we_never_store": [
                "Your raw message text",
                "Your phone number or email",
                "Your name or address",
                "Your IP address",
                "Device identifiers",
            ],
            "text_handling": "Raw user text is PII-scrubbed and analyzed in memory only. It is NEVER written to disk or database. Only a one-way SHA-256 fingerprint is kept for audit integrity.",
            "session_handling": "Session IDs are pseudonymized using HMAC-SHA256 before any database write. The original session ID cannot be recovered from stored data.",
            "data_retention": f"All records are automatically deleted after {DATA_RETENTION_DAYS} days.",
            "your_rights": [
                "Right to see what data is stored (GET /privacy/my-data)",
                "Right to delete all your data immediately (POST /privacy/delete)",
                "Right to withdraw from research data collection (revoke consent)",
            ],
            "legal_basis": "India Digital Personal Data Protection Act, 2023 (DPDPA)",
        },
        "contact": "For privacy concerns, contact: mindguard-privacy@example.com",
        "last_updated": "2025-09-25",
    }


@router.get("/my-data/{session_id}")
def get_my_data(session_id: str, db: Session = Depends(get_db)):
    """
    Returns all stored data for a session (pseudonymized view).
    The user can audit exactly what MindGuard has stored about them.
    """
    session_hash = pseudonymize_session(session_id)
    records = (
        db.query(RiskTrajectory)
        .filter(RiskTrajectory.session_id == session_hash)
        .order_by(RiskTrajectory.created_at)
        .all()
    )

    return {
        "session_id_hash": f"{session_hash[:8]}...{session_hash[-4:]}",  # partial reveal only
        "total_records": len(records),
        "data_retention_days": DATA_RETENTION_DAYS,
        "records": [
            {
                "severity_label": r.severity_label,
                "severity_score": r.severity_score,
                "confidence": r.confidence,
                "csi": r.csi,
                "language": r.language,
                "timestamp": r.created_at.isoformat() if r.created_at else None,
                "text_stored": "NO — only anonymous hash fingerprint",
            }
            for r in records
        ],
        "note": "Your raw message text is NEVER stored. Only the above metadata is kept.",
    }


@router.post("/delete")
def delete_my_data(request: DeleteRequest, db: Session = Depends(get_db)):
    """
    Permanently and immediately deletes ALL stored data for a session.
    This is the Right to Erasure (GDPR Article 17 / DPDPA Section 13).
    """
    if not request.confirm:
        raise HTTPException(
            status_code=400,
            detail="Set 'confirm: true' to permanently delete all your data."
        )

    session_hash = pseudonymize_session(request.session_id)

    # Delete all trajectory records
    deleted_count = (
        db.query(RiskTrajectory)
        .filter(RiskTrajectory.session_id == session_hash)
        .delete(synchronize_session=False)
    )
    db.commit()

    return {
        "status": "deleted",
        "records_deleted": deleted_count,
        "message": f"All {deleted_count} records for your session have been permanently deleted.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": "This action is irreversible. Your session hash has been removed from all MindGuard databases.",
    }
