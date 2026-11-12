from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from datetime import datetime, timezone

from app.models.base import Base


class MoodLog(Base):
    __tablename__ = "mood_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("users.session_id"), nullable=False, index=True)
    text = Column(Text, nullable=True) # Text or Slider
    severity = Column(String, nullable=False) # 'Normal', 'Mild', 'Moderate', 'Severe'
    severity_score = Column(Integer, default=0) # 0-3
    tags = Column(JSON, default=list)
    emotions = Column(JSON, default=list)
    triggers = Column(JSON, default=list)
    sleep_hours = Column(Float, nullable=True)
    energy = Column(Integer, nullable=True) # 1-10
    cbt_feedback = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
