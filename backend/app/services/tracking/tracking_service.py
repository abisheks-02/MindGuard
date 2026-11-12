import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from scipy.stats import linregress
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json

from app.models.mood_log import MoodLog
from app.models.user import User

logger = logging.getLogger(__name__)

class TrackingService:
    def __init__(self, db: Session):
        self._db = db

    def get_history(self, session_id: str, days: int):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        logs = (
            self._db.query(MoodLog)
            .filter(MoodLog.session_id == session_id, MoodLog.timestamp >= cutoff)
            .order_by(MoodLog.timestamp.asc())
            .all()
        )

        aggregates = {}
        for log in logs:
            date_str = log.timestamp.strftime("%Y-%m-%d")
            if date_str not in aggregates:
                aggregates[date_str] = {"scores": [], "energy": []}
            
            aggregates[date_str]["scores"].append(log.severity_score)
            if log.energy is not None:
                aggregates[date_str]["energy"].append(log.energy)

        # Build response payload
        agg_list = []
        for d, data in aggregates.items():
            avg_sev = sum(data["scores"]) / len(data["scores"])
            avg_eng = sum(data["energy"]) / len(data["energy"]) if data["energy"] else None
            agg_list.append({
                "date": d,
                "avg_severity": round(avg_sev, 2),
                "avg_energy": round(avg_eng, 2) if avg_eng else None
            })

        # Calculate Streaks
        streak = self._calculate_streak(session_id)

        # Calculate Trend
        trend, slope = self._calculate_trend(session_id, days=3)

        return {
            "aggregates": agg_list,
            "streak_days": streak,
            "trend": trend,
            "slope": slope
        }

    def _calculate_streak(self, session_id: str) -> int:
        logs = (
            self._db.query(MoodLog.timestamp)
            .filter(MoodLog.session_id == session_id)
            .order_by(MoodLog.timestamp.desc())
            .all()
        )
        if not logs:
            return 0

        dates = sorted(list(set(log[0].date() for log in logs)), reverse=True)
        streak = 0
        current_date = datetime.now(timezone.utc).date()

        for d in dates:
            if d == current_date or d == current_date - timedelta(days=1):
                streak += 1
                current_date = d
            else:
                break
        return streak

    def _calculate_trend(self, session_id: str, days: int = 3):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        logs = (
            self._db.query(MoodLog.severity_score, MoodLog.timestamp)
            .filter(MoodLog.session_id == session_id, MoodLog.timestamp >= cutoff)
            .order_by(MoodLog.timestamp.asc())
            .all()
        )

        if len(logs) < 2:
            return "stable", 0.0

        # severity_score: 0 (Normal) to 3 (Severe). Slope > 0 means getting worse.
        x = list(range(len(logs)))
        y = [log[0] for log in logs]
        
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        
        if slope > 0.5:
            trend = "worsening"
        elif slope < -0.5:
            trend = "improving"
        else:
            trend = "stable"

        return trend, round(slope, 2)

    def generate_pdf_export(self, session_id: str) -> io.BytesIO:
        logs = (
            self._db.query(MoodLog)
            .filter(MoodLog.session_id == session_id)
            .order_by(MoodLog.timestamp.desc())
            .limit(30)
            .all()
        )
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, f"Mood History Report - Last 30 Check-ins")
        c.drawString(100, 735, f"Date Generated: {datetime.now().strftime('%Y-%m-%d')}")
        
        y = 700
        for log in logs:
            if y < 50:
                c.showPage()
                y = 750
                
            date_str = log.timestamp.strftime('%Y-%m-%d %H:%M')
            sev_str = ["Normal", "Mild", "Moderate", "Severe"][log.severity_score] if log.severity_score is not None else log.severity
            c.drawString(100, y, f"[{date_str}] Severity: {sev_str} | Energy: {log.energy or 'N/A'}")
            y -= 15
            
            tags_str = ", ".join(log.tags) if log.tags else "None"
            c.drawString(120, y, f"Tags: {tags_str}")
            y -= 25

        c.save()
        buffer.seek(0)
        return buffer
