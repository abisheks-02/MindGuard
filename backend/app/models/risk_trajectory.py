"""
RiskTrajectory Model
=====================
Stores a time-series of risk assessments per session.
This is the core data source for the Longitudinal Risk Trajectory feature —
the novel IEEE contribution that enables pattern-based crisis prediction
beyond single-message analysis.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from datetime import datetime, timezone

from app.models.base import Base


class RiskTrajectory(Base):
    __tablename__ = "risk_trajectory"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)

    # Risk label: Normal=0, Mild=1, Moderate=2, Severe=3
    severity_label = Column(String, nullable=False)
    severity_score = Column(Integer, nullable=False)  # 0-3

    # Confidence of the ensemble
    confidence = Column(Float, nullable=True)

    # Code-Switching Index — Tanglish ratio (0.0 = pure English, 1.0 = pure Tanglish)
    # THIS is the novel CSI clinical biomarker stored per message
    csi = Column(Float, nullable=True, default=0.0)

    # Raw text snippet (first 200 chars, PII-scrubbed)
    text_snippet = Column(Text, nullable=True)

    # Language detected
    language = Column(String, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
