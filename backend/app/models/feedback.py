from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime, timezone

from app.models.base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("users.session_id"), nullable=False, index=True)
    analysis_id = Column(Integer, nullable=True) # Optional link to a specific analysis
    text = Column(Text, nullable=False)
    predicted_label = Column(String, nullable=False)
    correct_label = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
