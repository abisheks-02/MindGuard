from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db
from app.models.user import User
from app.models.trusted_contact import TrustedContact
from app.models.mood_log import MoodLog
from app.models.chat import ChatSession
from app.models.alert import AlertEvent
from app.models.consent import ConsentRecord
from app.services.auth_service import AuthService
from app.utils.logger import logger
from app.config import get_settings

router = APIRouter(tags=["auth"])

class LoginRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


def _require_demo_auth() -> None:
    if not get_settings().ENABLE_DEMO_AUTH:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Demo authentication is disabled. Configure a verified identity provider.",
        )

@router.post("/login")
def request_otp(req: LoginRequest):
    # Mock OTP logic - in prod this calls Twilio/SNS
    _require_demo_auth()
    logger.info(f"OTP requested for {req.phone}")
    return {"message": "OTP sent successfully (Use '1234' for demo)"}

@router.post("/verify")
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    _require_demo_auth()
    if req.otp != "1234":
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Check if user exists (phone is encrypted in DB)
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user:
        # Implicit signup
        user = User(session_id=f"user_{datetime.now().timestamp()}", phone=req.phone)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = AuthService.create_access_token({"sub": user.session_id, "type": "user"})
    refresh_token = AuthService.create_refresh_token({"sub": user.session_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "session_id": user.session_id
    }

class EraseRequest(BaseModel):
    session_id: str

@router.delete("/me")
def right_to_erase(req: EraseRequest, db: Session = Depends(get_db)):
    """DPDP Act Right to Erase: Hard cascade deletion of all user data."""
    user = db.query(User).filter(User.session_id == req.session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    logger.info(f"Processing Right to Erase for user {req.session_id}")
    
    # Delete related records
    db.query(TrustedContact).filter(TrustedContact.user_id == req.session_id).delete()
    db.query(MoodLog).filter(MoodLog.session_id == req.session_id).delete()
    db.query(ChatSession).filter(ChatSession.session_id == req.session_id).delete()
    db.query(AlertEvent).filter(AlertEvent.user_id == req.session_id).delete()
    db.query(ConsentRecord).filter(ConsentRecord.session_id == req.session_id).delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return {"message": "All personal data has been permanently erased in compliance with DPDP 2023."}
