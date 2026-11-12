from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    language = Column(String, default="en")
    reminder_time = Column(String, nullable=True) # "09:00" format
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trusted_contacts = relationship("TrustedContact", back_populates="user", cascade="all, delete-orphan")
    consent_records = relationship("ConsentRecord", back_populates="user", cascade="all, delete-orphan")
    alert_events = relationship("AlertEvent", back_populates="user", cascade="all, delete-orphan")
