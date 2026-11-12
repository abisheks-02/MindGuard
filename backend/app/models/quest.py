from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime, timezone

from app.models.base import Base


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("users.session_id"), nullable=False, index=True)
    quest_text = Column(Text, nullable=False)
    status = Column(String, default="pending")
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
