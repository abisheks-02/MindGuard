from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from datetime import datetime, timezone

from app.models.base import Base


class ExploratoryIndicator(Base):
    __tablename__ = "exploratory_indicators"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("users.session_id"), nullable=False, index=True)
    
    # Speech Metrics
    wpm = Column(Float, nullable=True)
    pause_ratio = Column(Float, nullable=True)
    mean_pause_length = Column(Float, nullable=True)
    pitch_variance = Column(Float, nullable=True)
    
    # Linguistic / Code-Switching Metrics
    cmi = Column(Float, nullable=True)
    switch_point_freq = Column(Float, nullable=True)
    tamil_roman_ratio = Column(Float, nullable=True)
    
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
