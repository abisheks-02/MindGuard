from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.models.base import Base


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # e.g., 'support_messages', 'notify_trusted', 'research_data'
    granted_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="consent_records")
