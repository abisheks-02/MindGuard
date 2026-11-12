from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatMessageRequest(BaseModel):
    text: str
    severity: str
    session_id: str = "demo_user_001"


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime


class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime


class QuickReplyResponse(BaseModel):
    replies: List[str]


class MemoryClearResponse(BaseModel):
    status: str
    message: str
