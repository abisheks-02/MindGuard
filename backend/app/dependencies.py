"""
FastAPI dependency injection for services and DB sessions.
Services are singletons wired at startup; routers get them via Depends().
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.chatbot import ChatbotService
from app.services.escalation.engine import EscalationEngine
from app.services.voice import VoiceService
from app.services.memory import MemoryService
from app.services.memory.sqlalchemy_memory import SQLAlchemyMemoryService
from app.services.detection import DetectionService

_detection_service: DetectionService | None = None
_chatbot_service: ChatbotService | None = None
_escalation_engine: EscalationEngine | None = None
_voice_service: VoiceService | None = None


def set_detection_service(svc: DetectionService) -> None:
    global _detection_service
    _detection_service = svc


def set_chatbot_service(svc: ChatbotService) -> None:
    global _chatbot_service
    _chatbot_service = svc


def set_escalation_engine(svc: EscalationEngine) -> None:
    global _escalation_engine
    _escalation_engine = svc


def set_voice_service(svc: VoiceService) -> None:
    global _voice_service
    _voice_service = svc


# ── FastAPI Depends() functions ─────────────────────────

def get_detection_service() -> DetectionService:
    assert _detection_service is not None, "DetectionService not initialized"
    return _detection_service


def get_chatbot_service() -> ChatbotService:
    assert _chatbot_service is not None, "ChatbotService not initialized"
    return _chatbot_service


def get_escalation_engine() -> EscalationEngine:
    assert _escalation_engine is not None, "EscalationEngine not initialized"
    return _escalation_engine


def get_voice_service() -> VoiceService:
    assert _voice_service is not None, "VoiceService not initialized"
    return _voice_service


def get_memory_service(db: Session = Depends(get_db)) -> MemoryService:
    """Scoped per-request because it wraps a DB session."""
    return SQLAlchemyMemoryService(db)
