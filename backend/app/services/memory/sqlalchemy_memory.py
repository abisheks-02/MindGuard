"""SQLAlchemy-backed memory service."""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import User, MoodLog, AlertEvent, WellnessPlan, Quest, ChatSession, ChatMessage
from app.services.memory import MemoryService

logger = logging.getLogger(__name__)


class SQLAlchemyMemoryService(MemoryService):
    def __init__(self, db: Session):
        self._db = db

    def ensure_user(self, session_id: str) -> None:
        existing = self._db.query(User).filter(User.session_id == session_id).first()
        if not existing:
            self._db.add(User(session_id=session_id))
            self._db.commit()

    def log_mood(self, session_id: str, text: str, severity: str) -> None:
        self.ensure_user(session_id)
        entry = MoodLog(session_id=session_id, text=text, severity=severity)
        self._db.add(entry)
        self._db.commit()

    def get_mood_history(self, session_id: str, limit: int = 7) -> list[dict]:
        rows = (
            self._db.query(MoodLog)
            .filter(MoodLog.session_id == session_id)
            .order_by(MoodLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "session_id": r.session_id,
                "text": r.text,
                "severity": r.severity,
                "timestamp": r.timestamp.isoformat() if r.timestamp else "",
                "cbt_feedback": r.cbt_feedback,
            }
            for r in rows
        ]

    def log_alert(self, text: str) -> None:
        self._db.add(AlertEvent(text=text))
        self._db.commit()

    def save_wellness_plan(self, session_id: str, plan_text: str) -> None:
        self.ensure_user(session_id)
        self._db.add(WellnessPlan(session_id=session_id, plan_text=plan_text))
        self._db.commit()

    def get_latest_wellness_plan(self, session_id: str) -> dict | None:
        row = (
            self._db.query(WellnessPlan)
            .filter(WellnessPlan.session_id == session_id)
            .order_by(WellnessPlan.generated_at.desc())
            .first()
        )
        if row is None:
            return None
        return {"plan_text": row.plan_text, "generated_at": row.generated_at.isoformat()}

    def save_quest(self, session_id: str, quest_text: str) -> None:
        self.ensure_user(session_id)
        self._db.add(Quest(session_id=session_id, quest_text=quest_text))
        self._db.commit()

    def get_quests(self, session_id: str) -> list[dict]:
        rows = (
            self._db.query(Quest)
            .filter(Quest.session_id == session_id)
            .order_by(Quest.generated_at.desc())
            .limit(10)
            .all()
        )
        return [
            {
                "id": r.id,
                "session_id": r.session_id,
                "quest_text": r.quest_text,
                "status": r.status,
                "generated_at": r.generated_at.isoformat() if r.generated_at else "",
            }
            for r in rows
        ]

    def complete_quest(self, quest_id: int) -> None:
        quest = self._db.query(Quest).filter(Quest.id == quest_id).first()
        if quest:
            quest.status = "completed"
            self._db.commit()

    # ── Chat Memory ──────────────────────────────────────

    def get_or_create_chat_session(self, user_id: str, session_id: str) -> ChatSession:
        self.ensure_user(user_id)
        session = self._db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(id=session_id, user_id=user_id)
            self._db.add(session)
            self._db.commit()
            self._db.refresh(session)
        return session

    def save_chat_message(self, session_id: str, role: str, content: str, severity: str = None) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, role=role, content=content, severity=severity)
        self._db.add(msg)
        self._db.commit()
        self._db.refresh(msg)
        return msg

    def get_chat_history(self, session_id: str, limit: int = 50) -> list[dict]:
        messages = (
            self._db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp.asc())
            .limit(limit)
            .all()
        )
        return [{"id": m.id, "role": m.role, "content": m.content, "timestamp": m.timestamp} for m in messages]

    def clear_memory(self, user_id: str) -> None:
        # Delete chat sessions
        self._db.query(ChatSession).filter(ChatSession.user_id == user_id).delete(synchronize_session=False)
        # Delete mood logs
        self._db.query(MoodLog).filter(MoodLog.session_id == user_id).delete(synchronize_session=False)
        self._db.commit()

    def get_rolling_summary(self, user_id: str) -> str:
        # Simple frequency extraction of themes from mood logs and chats
        logs = self._db.query(MoodLog.text).filter(MoodLog.session_id == user_id).all()
        texts = [log[0].lower() for log in logs]
        
        themes = ["sleep", "exam", "family", "work", "stress", "lonely", "health", "relationship"]
        found = []
        for text in texts:
            for theme in themes:
                if theme in text and theme not in found:
                    found.append(theme)
                    
        return ", ".join(found) if found else "None identified"
