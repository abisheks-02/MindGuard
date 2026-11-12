import logging
import yaml
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.alert import AlertEvent
from app.models.consent import ConsentRecord
from app.models.trusted_contact import TrustedContact
from app.models.user import User
from app.services.escalation.providers import MessageProvider

logger = logging.getLogger(__name__)


class EscalationEngine:
    def __init__(self, config_path: str, provider: MessageProvider):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.provider = provider
        self.cooldown_hours = self.config["global"]["cooldown_hours"]
        self.grace_seconds = self.config["global"]["cancellation_grace_seconds"]
        
        # In-memory store for pending alerts during grace period: {user_id: True/False}
        self.pending_cancellations = {}

    async def evaluate(self, db: Session, user_session_id: str, severity: str, confidence: float, needs_review: bool):
        """Evaluates rules and triggers actions if conditions are met."""
        user = db.query(User).filter(User.session_id == user_session_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}

        for rule in self.config["rules"]:
            if rule["severity"] == severity:
                # Basic eval logic based on YAML conditions
                if severity == "Severe" and (confidence >= 0.7 or needs_review):
                    if self._is_in_cooldown(db, user.id, severity):
                        return {"status": "cooldown", "message": "Alert throttled by cooldown."}
                        
                    return await self._trigger_severe(db, user, rule["actions"])
                    
                elif severity == "Moderate":
                    count = self._count_recent(db, user.id, "Moderate", days=7)
                    if count >= 3:
                        if self._is_in_cooldown(db, user.id, severity):
                            return {"status": "cooldown", "message": "Alert throttled by cooldown."}
                        return await self._trigger_moderate(db, user, rule["actions"])

        return {"status": "no_action"}

    async def _trigger_severe(self, db: Session, user: User, actions: list):
        logger.info(f"Triggering Severe Escalation for user {user.session_id} in {self.grace_seconds}s")
        self.pending_cancellations[user.session_id] = False

        # Start background wait for grace period
        await asyncio.sleep(self.grace_seconds)

        if self.pending_cancellations.get(user.session_id):
            logger.info(f"Escalation cancelled by user {user.session_id}.")
            del self.pending_cancellations[user.session_id]
            return {"status": "cancelled"}
            
        del self.pending_cancellations[user.session_id]

        # Execute Actions
        results = []
        for action in actions:
            if action["type"] == "in_app_crisis_screen":
                # UI action logged as an event
                self._record_alert(db, user.id, "Severe", "in_app")
                results.append("in_app_screen_triggered")

            elif action["type"] == "notify_user":
                if self._has_consent(db, user.id, "support_messages") and user.phone:
                    self.provider.send_message(user.phone, action["template"], action.get("channel", "sms"))
                    self._record_alert(db, user.id, "Severe", action.get("channel", "sms"))
                    results.append("user_notified")

            elif action["type"] == "notify_trusted_contact":
                if self._has_consent(db, user.id, "notify_trusted"):
                    contact = db.query(TrustedContact).filter(TrustedContact.user_id == user.id, TrustedContact.verified == True).first()
                    if contact and contact.phone:
                        msg = action["template"].replace("{user_name}", "Your contact")
                        self.provider.send_message(contact.phone, msg, action.get("channel", "sms"))
                        self._record_alert(db, user.id, "Severe", "trusted_contact_sms")
                        results.append("trusted_contact_notified")

        return {"status": "executed", "actions": results}

    async def _trigger_moderate(self, db: Session, user: User, actions: list):
        for action in actions:
            if action["type"] == "notify_user":
                self._record_alert(db, user.id, "Moderate", "in_app")
        return {"status": "executed", "actions": ["moderate_nudge_sent"]}

    def cancel_alert(self, user_session_id: str):
        if user_session_id in self.pending_cancellations:
            self.pending_cancellations[user_session_id] = True
            return True
        return False

    def _is_in_cooldown(self, db: Session, user_id: int, severity: str) -> bool:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.cooldown_hours)
        recent = db.query(AlertEvent).filter(
            AlertEvent.user_id == user_id,
            AlertEvent.severity == severity,
            AlertEvent.created_at >= cutoff
        ).first()
        return recent is not None

    def _count_recent(self, db: Session, user_id: int, severity: str, days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return db.query(AlertEvent).filter(
            AlertEvent.user_id == user_id,
            AlertEvent.severity == severity,
            AlertEvent.created_at >= cutoff
        ).count()

    def _has_consent(self, db: Session, user_id: int, consent_type: str) -> bool:
        rec = db.query(ConsentRecord).filter(ConsentRecord.user_id == user_id, ConsentRecord.type == consent_type, ConsentRecord.revoked_at == None).first()
        return rec is not None

    def _record_alert(self, db: Session, user_id: int, severity: str, channel: str):
        event = AlertEvent(user_id=user_id, severity=severity, channel=channel, status="contacted")
        db.add(event)
        db.commit()
