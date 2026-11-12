from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.schemas.escalation import ConsentRequest, TrustedContactRequest, TrustedContactVerifyRequest, AlertEventRequest, WebhookRequest, AlertEventResponse
from app.db import get_db
from app.models import User, ConsentRecord, TrustedContact, AlertEvent
from app.dependencies import get_escalation_engine
from app.services.escalation.engine import EscalationEngine
from app.config import get_settings

router = APIRouter(tags=["escalation"])


def _require_real_escalation() -> None:
    if get_settings().ENABLE_MOCK_ESCALATION:
        return
    raise HTTPException(
        status_code=503,
        detail="Escalation delivery is not configured. Do not imply that a contact was notified.",
    )

@router.post("/onboarding/consent")
def submit_consent(req: ConsentRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.session_id == req.user_id).first()
    if not user:
        user = User(session_id=req.user_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Clear existing
    db.query(ConsentRecord).filter(ConsentRecord.user_id == user.id).delete()
    
    if req.support_messages:
        db.add(ConsentRecord(user_id=user.id, type="support_messages"))
    if req.notify_trusted:
        db.add(ConsentRecord(user_id=user.id, type="notify_trusted"))
    if req.research_data:
        db.add(ConsentRecord(user_id=user.id, type="research_data"))
        
    db.commit()
    return {"status": "success", "message": "Consent recorded"}


@router.post("/onboarding/trusted-contact")
def add_trusted_contact(req: TrustedContactRequest, db: Session = Depends(get_db)):
    _require_real_escalation()
    user = db.query(User).filter(User.session_id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    contact = TrustedContact(user_id=user.id, name=req.name, phone=req.phone, relation=req.relation)
    db.add(contact)
    db.commit()
    return {"status": "success", "message": "OTP sent to contact (MOCK)"}


@router.post("/onboarding/trusted-contact/verify")
def verify_trusted_contact(req: TrustedContactVerifyRequest, db: Session = Depends(get_db)):
    _require_real_escalation()
    user = db.query(User).filter(User.session_id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    contact = db.query(TrustedContact).filter(TrustedContact.user_id == user.id).first()
    if contact and req.otp == "1234": # Mock OTP
        contact.verified = True
        contact.consent_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "success", "message": "Trusted contact verified."}
    return {"status": "error", "message": "Invalid OTP"}


@router.post("/escalation/trigger")
async def trigger_escalation(
    req: AlertEventRequest, 
    bg_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    engine: EscalationEngine = Depends(get_escalation_engine)
):
    _require_real_escalation()
    # We run evaluation in the background so we don't block the API for 60 seconds.
    bg_tasks.add_task(engine.evaluate, db, req.user_id, req.severity, req.confidence, req.needs_review)
    return {"status": "queued", "message": "Escalation evaluation started."}


@router.post("/escalation/cancel")
def cancel_escalation(user_id: str, engine: EscalationEngine = Depends(get_escalation_engine)):
    success = engine.cancel_alert(user_id)
    if success:
        return {"status": "success", "message": "Alert cancelled successfully within grace period."}
    return {"status": "failed", "message": "No pending alerts or grace period expired."}


@router.post("/escalation/webhook")
def delivery_webhook(req: WebhookRequest, db: Session = Depends(get_db)):
    # Log delivery status from Twilio/MSG91
    return {"status": "received"}


@router.get("/admin/alerts", response_model=list[AlertEventResponse])
def get_alerts(status: str = None, db: Session = Depends(get_db)):
    # Simple role-based access mock (normally would verify JWT scopes)
    query = db.query(AlertEvent)
    if status:
        query = query.filter(AlertEvent.status == status)
    return query.order_by(AlertEvent.created_at.desc()).all()
