"""Recovery quests router."""

import logging

from fastapi import APIRouter, Depends

from app.schemas.quest import QuestGenerateRequest, QuestCompleteRequest, QuestResponse
from app.services.chatbot import ChatbotService
from app.services.memory import MemoryService
from app.dependencies import get_chatbot_service, get_memory_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["quests"])


@router.post("/quest", response_model=QuestResponse)
def generate_quest(
    request: QuestGenerateRequest,
    chatbot: ChatbotService = Depends(get_chatbot_service),
    memory: MemoryService = Depends(get_memory_service),
):
    history = memory.get_mood_history(request.session_id, limit=1)
    severity_context = history[0]["severity"] if history else "Unknown"

    quest_text = chatbot.generate_response(
        text=f"Generate a recovery quest for severity: {severity_context}",
        severity=severity_context,
        history_str="None",
    )
    # Trim to a single quest line
    quest_text = quest_text.split("\n")[0].strip()[:200]

    memory.save_quest(request.session_id, quest_text)
    return QuestResponse(quest=quest_text)


@router.get("/quests/{session_id}")
def get_quests(
    session_id: str,
    memory: MemoryService = Depends(get_memory_service),
):
    return memory.get_quests(session_id)


@router.post("/quests/complete")
def complete_quest(
    request: QuestCompleteRequest,
    memory: MemoryService = Depends(get_memory_service),
):
    memory.complete_quest(request.quest_id)
    return {"status": "success"}
