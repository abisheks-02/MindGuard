from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from datetime import datetime, timezone

from app.models.base import Base


class WellnessPlan(Base):
    __tablename__ = "wellness_plans"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("users.session_id"), nullable=False, index=True)
    plan_data = Column(JSON, nullable=False) # Stores the weekly plan JSON structure
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
