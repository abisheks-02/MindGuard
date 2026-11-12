from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import json

from app.schemas.mood import MoodLogRequest, MoodLogResponse, MoodHistoryResponse, ReminderRequest
from app.services.detection import DetectionService
from app.services.tracking.tracking_service import TrackingService
from app.services.chatbot.llama_chatbot import LlamaChatbotService
from app.dependencies import get_detection_service, get_chatbot_service, get_escalation_engine
from app.services.escalation.engine import EscalationEngine
from app.db import get_db
from app.models.mood_log import MoodLog
from app.models.wellness_plan import WellnessPlan
from app.models.user import User

router = APIRouter(tags=["mood"])

@router.post("/log", response_model=MoodLogResponse)
def log_mood(
    request: MoodLogRequest,
    bg_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    detection: DetectionService = Depends(get_detection_service),
    escalation: EscalationEngine = Depends(get_escalation_engine)
):
    # Phase 1: Pipeline
    severity = "Normal"
    severity_score = 0
    cbt_feedback = None
    
    if request.text:
        res = detection.analyze(request.text)
        severity = res.get("predicted_class", "Normal")
        severity_score = {"Normal": 0, "Mild": 1, "Moderate": 2, "Severe": 3}.get(severity, 0)
        cbt_feedback = "I notice you're feeling this way. Consider a short breathing exercise."

    new_log = MoodLog(
        session_id=request.user_id,
        text=request.text or "Logged via sliders",
        severity=severity,
        severity_score=severity_score,
        tags=request.tags,
        emotions=request.emotions,
        triggers=request.triggers,
        sleep_hours=request.sleep_hours,
        energy=request.energy,
        cbt_feedback=cbt_feedback
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    # Trigger Early Warning (Phase 3 Nudge) in background
    if severity_score > 1:
        # Check slope
        tracker = TrackingService(db)
        trend, slope = tracker._calculate_trend(request.user_id, days=3)
        if trend == "worsening" or slope >= 1.0:
            # Fake needs_review trigger for escalation if worsening rapidly
            bg_tasks.add_task(escalation.evaluate, db, request.user_id, "Severe", 0.8, True)
            
    return MoodLogResponse(
        id=new_log.id,
        severity=new_log.severity,
        severity_score=new_log.severity_score,
        cbt_feedback=new_log.cbt_feedback,
        timestamp=new_log.timestamp
    )


@router.get("/history", response_model=MoodHistoryResponse)
def get_mood_history(range_days: int = 7, user_id: str = "demo_user_001", db: Session = Depends(get_db)):
    tracker = TrackingService(db)
    return tracker.get_history(user_id, range_days)


@router.get("/plan")
def get_weekly_plan(user_id: str = "demo_user_001", force: bool = False, db: Session = Depends(get_db), chatbot: LlamaChatbotService = Depends(get_chatbot_service)):
    # Check if a plan was generated within the last 7 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    existing = db.query(WellnessPlan).filter(WellnessPlan.session_id == user_id, WellnessPlan.generated_at >= cutoff).order_by(WellnessPlan.generated_at.desc()).first()
    
    if existing and not force:
        return existing.plan_data
        
    # Generate new one
    tracker = TrackingService(db)
    history_data = tracker.get_history(user_id, 7)
    # create simple text representation
    history_str = json.dumps([{"date": h["date"], "sev": h["avg_severity"]} for h in history_data["aggregates"]])
    
    new_plan_data = chatbot.generate_weekly_plan(history_str)
    
    plan = WellnessPlan(session_id=user_id, plan_data=new_plan_data)
    db.add(plan)
    db.commit()
    
    return new_plan_data


@router.get("/export")
def export_mood_history(user_id: str = "demo_user_001", db: Session = Depends(get_db)):
    tracker = TrackingService(db)
    buffer = tracker.generate_pdf_export(user_id)
    return StreamingResponse(
        buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=MindGuard_Report_{user_id}.pdf"}
    )

@router.post("/reminder")
def set_reminder(req: ReminderRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.session_id == req.user_id).first()
    if user:
        user.reminder_time = req.reminder_time
        db.commit()
        return {"status": "success", "reminder_time": req.reminder_time}
    raise HTTPException(404, "User not found")
