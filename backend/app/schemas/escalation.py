from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

class ConsentRequest(BaseModel):
    user_id: str = "demo_user_001"
    support_messages: bool
    notify_trusted: bool
    research_data: bool

class TrustedContactRequest(BaseModel):
    user_id: str = "demo_user_001"
    name: str
    phone: str
    relation: str

class TrustedContactVerifyRequest(BaseModel):
    user_id: str = "demo_user_001"
    otp: str

class AlertEventRequest(BaseModel):
    user_id: str = "demo_user_001"
    severity: str
    confidence: float
    needs_review: bool

class AlertEventResponse(BaseModel):
    id: int
    severity: str
    channel: str
    status: str
    created_at: datetime
    
class WebhookRequest(BaseModel):
    message_id: str
    status: str # 'delivered', 'failed'
    provider: str
