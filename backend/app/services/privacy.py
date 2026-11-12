"""
Privacy Service
================
Centralizes all privacy-related operations for MindGuard.

Privacy Architecture:
1. TEXT ANONYMIZATION — raw user text is never stored. Only a SHA-256 hash
   of the first 80 chars is logged (used only for deduplication, not recovery).
2. SESSION ANONYMIZATION — session IDs are never stored raw. They are hashed
   with HMAC-SHA256 using a server-side secret, making them pseudonymous.
3. AUTO-DELETION — trajectory records older than DATA_RETENTION_DAYS are
   automatically purged on each analyze call (rolling window).
4. DATA MINIMIZATION — only severity label, score, CSI ratio, and language
   are stored. No text content, no PII, no location.
5. CONSENT GATE — the service checks if the session has granted 'research_data'
   consent before storing any trajectory data at all.
"""

import hashlib
import hmac
import os
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import delete

logger = logging.getLogger(__name__)

# Server-side secret for HMAC pseudonymization.
# In production this MUST come from an environment variable / secrets manager.
_HMAC_SECRET = os.environ.get("MINDGUARD_PRIVACY_SECRET", "mindguard-dev-secret-change-in-prod").encode()

# How many days to retain trajectory data before auto-purge
DATA_RETENTION_DAYS = int(os.environ.get("DATA_RETENTION_DAYS", "90"))


def pseudonymize_session(session_id: str) -> str:
    """
    Converts a raw session ID into a pseudonymous one-way hash.
    The original session_id cannot be recovered from the stored value.
    This satisfies GDPR pseudonymization requirements.
    """
    return hmac.new(_HMAC_SECRET, session_id.encode(), hashlib.sha256).hexdigest()[:32]


def anonymize_text(text: str) -> str:
    """
    Returns a SHA-256 fingerprint of the text (first 80 chars).
    Used only for deduplication in audit logs — the original text is NOT stored.
    """
    snippet = (text or "")[:80].strip()
    return "sha256:" + hashlib.sha256(snippet.encode()).hexdigest()[:16]


def purge_expired_records(db: Session, session_id_hash: str) -> int:
    """
    Deletes trajectory records older than DATA_RETENTION_DAYS for a session.
    Called automatically on each analyze request (rolling purge).
    Returns number of deleted records.
    """
    from app.models.risk_trajectory import RiskTrajectory
    cutoff = datetime.now(timezone.utc) - timedelta(days=DATA_RETENTION_DAYS)
    try:
        result = db.execute(
            delete(RiskTrajectory).where(
                RiskTrajectory.session_id == session_id_hash,
                RiskTrajectory.created_at < cutoff
            )
        )
        deleted = result.rowcount
        if deleted > 0:
            db.commit()
            logger.info("Privacy purge: removed %d expired records for session hash %s...", deleted, session_id_hash[:8])
        return deleted
    except Exception as e:
        db.rollback()
        logger.warning("Privacy purge failed: %s", e)
        return 0


def get_privacy_headers() -> dict:
    """Returns HTTP headers that enforce privacy best practices."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Cache-Control": "no-store, no-cache, must-revalidate",
    }
