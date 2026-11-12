"""
Risk Trajectory Router
========================
Novel endpoint that provides longitudinal risk analysis — 
tracking a user's severity score over time and detecting
acute drop patterns that predict crisis onset.

IEEE Contribution: Pattern-based crisis prediction using
time-series severity analysis and Code-Switching Index (CSI) trends.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timezone

from app.db import get_db
from app.models.risk_trajectory import RiskTrajectory

router = APIRouter(tags=["trajectory"])

SEVERITY_SCORE = {"Normal": 0, "Mild": 1, "Moderate": 2, "Severe": 3}


@router.get("/trajectory/{session_id}")
def get_trajectory(
    session_id: str,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
):
    """
    Returns a user's full risk trajectory over time.
    Also computes:
    - acute_drop_detected: True if 3 consecutive sessions declined
    - csi_trend: increasing/stable/decreasing CSI over time
    - trajectory_risk: computed from the slope of the last 5 records
    """
    records = (
        db.query(RiskTrajectory)
        .filter(RiskTrajectory.session_id == session_id)
        .order_by(desc(RiskTrajectory.created_at))
        .limit(limit)
        .all()
    )

    # Reverse to chronological order
    records = list(reversed(records))

    if not records:
        return {
            "session_id": session_id,
            "trajectory": [],
            "acute_drop_detected": False,
            "trajectory_risk": "Normal",
            "csi_trend": "stable",
            "total_records": 0,
        }

    # Build trajectory data
    trajectory = [
        {
            "id": r.id,
            "severity_label": r.severity_label,
            "severity_score": r.severity_score,
            "confidence": r.confidence,
            "csi": r.csi,
            "language": r.language,
            "timestamp": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]

    # ── Acute Drop Detector ──
    # If 3 consecutive entries decline in severity, flag it
    acute_drop_detected = False
    if len(records) >= 3:
        scores = [r.severity_score for r in records]
        for i in range(len(scores) - 2):
            if scores[i] < scores[i + 1] < scores[i + 2]:
                acute_drop_detected = True
                break

    # ── Trajectory Risk (last 5 records slope) ──
    recent = records[-5:] if len(records) >= 5 else records
    recent_scores = [r.severity_score for r in recent]
    avg_score = sum(recent_scores) / len(recent_scores)
    if avg_score >= 2.5:
        trajectory_risk = "Severe"
    elif avg_score >= 1.5:
        trajectory_risk = "Moderate"
    elif avg_score >= 0.5:
        trajectory_risk = "Mild"
    else:
        trajectory_risk = "Normal"

    # ── CSI Trend (Code-Switching Index) ──
    csi_values = [r.csi for r in records if r.csi is not None]
    csi_trend = "stable"
    if len(csi_values) >= 3:
        first_half = sum(csi_values[: len(csi_values) // 2]) / max(len(csi_values) // 2, 1)
        second_half = sum(csi_values[len(csi_values) // 2 :]) / max(len(csi_values) - len(csi_values) // 2, 1)
        diff = second_half - first_half
        if diff > 0.1:
            csi_trend = "increasing"  # More Tanglish over time = stress signal
        elif diff < -0.1:
            csi_trend = "decreasing"
        else:
            csi_trend = "stable"

    return {
        "session_id": session_id,
        "trajectory": trajectory,
        "acute_drop_detected": acute_drop_detected,
        "trajectory_risk": trajectory_risk,
        "csi_trend": csi_trend,
        "total_records": len(records),
        "note": "CSI (Code-Switching Index) increasing trend may indicate growing distress.",
    }


@router.get("/trajectory/{session_id}/summary")
def get_trajectory_summary(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Returns a compact clinical summary for the XAI Dashboard."""
    records = (
        db.query(RiskTrajectory)
        .filter(RiskTrajectory.session_id == session_id)
        .order_by(desc(RiskTrajectory.created_at))
        .limit(50)
        .all()
    )

    if not records:
        return {"total_messages": 0, "dominant_severity": "Normal", "avg_csi": 0.0}

    severity_counts = {}
    for r in records:
        severity_counts[r.severity_label] = severity_counts.get(r.severity_label, 0) + 1

    dominant = max(severity_counts, key=severity_counts.get)
    avg_csi = sum(r.csi or 0 for r in records) / len(records)
    severe_count = severity_counts.get("Severe", 0)
    moderate_count = severity_counts.get("Moderate", 0)

    return {
        "total_messages": len(records),
        "dominant_severity": dominant,
        "severity_distribution": severity_counts,
        "avg_csi": round(avg_csi, 3),
        "severe_events": severe_count,
        "moderate_events": moderate_count,
        "high_risk_ratio": round((severe_count + moderate_count) / len(records), 3),
    }
