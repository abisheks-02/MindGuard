"""CBT chatbot router with SSE streaming."""

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatMessageRequest, ChatSessionResponse, ChatMessageResponse, QuickReplyResponse, MemoryClearResponse
from app.services.chatbot import ChatbotService
from app.services.memory import MemoryService
from app.dependencies import get_chatbot_service, get_memory_service
from app.utils.injection_guard import check_prompt_injection
from app.config import get_settings

router = APIRouter(tags=["chat"])


@router.post("/chat/stream")
async def chat_stream(
    request: ChatMessageRequest,
    chatbot: ChatbotService = Depends(get_chatbot_service),
    memory: MemoryService = Depends(get_memory_service),
):
    user_id = "demo_user_001"
    session_id = request.session_id
    
    # Check for prompt injection
    check_prompt_injection(request.text)
    
    # 1. Initialize session and save user message
    memory.get_or_create_chat_session(user_id, session_id)
    # Chat content is sensitive health-adjacent data. Retention is opt-in at
    # deployment level; the default keeps the session functional without
    # writing the user's words to the database.
    retained_user_text = request.text if get_settings().RETAIN_CHAT_CONTENT else "[User message not retained]"
    memory.save_chat_message(session_id, "user", retained_user_text, severity=request.severity)
    
    # 2. Get history & themes
    history = memory.get_mood_history(user_id, limit=3)
    history_str = "None"
    if history:
        history_str = " | ".join([f"{h['text']} (Severity: {h['severity']})" for h in history])
        
    themes = memory.get_rolling_summary(user_id)

    # 3. Stream generator wrapper
    async def event_generator():
        full_response = ""
        # The generator from chatbot is async, we iterate over it
        async for chunk in chatbot.generate_response_stream(request.text, request.severity, history_str, themes):
            full_response += chunk
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            
        # Save assistant message at the end
        retained_reply = full_response.strip() if get_settings().RETAIN_CHAT_CONTENT else "[Assistant message not retained]"
        memory.save_chat_message(session_id, "assistant", retained_reply)
        yield "event: end\ndata: [DONE]\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/chat/quick-replies", response_model=QuickReplyResponse)
def get_quick_replies(
    request: ChatMessageRequest,
    chatbot: ChatbotService = Depends(get_chatbot_service),
):
    replies = chatbot.generate_quick_replies(request.text, request.severity)
    return QuickReplyResponse(replies=replies)


@router.get("/sessions", response_model=list[ChatSessionResponse])
def get_sessions(
    user_id: str = "demo_user_001",
    memory: MemoryService = Depends(get_memory_service)
):
    # Retrieve sessions from db
    sessions = memory._db.query(memory._db.class_mapper(memory.get_or_create_chat_session(user_id, "tmp").__class__)).filter_by(user_id=user_id).all()
    # Note: query(ChatSession) requires importing ChatSession, so we do it explicitly:
    from app.models.chat import ChatSession
    sessions = memory._db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    
    return [ChatSessionResponse(
        id=s.id, user_id=s.user_id, title=s.title, created_at=s.created_at
    ) for s in sessions]


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
def get_session_messages(
    session_id: str,
    memory: MemoryService = Depends(get_memory_service)
):
    history = memory.get_chat_history(session_id)
    return [ChatMessageResponse(
        id=m["id"], role=m["role"], content=m["content"], timestamp=m["timestamp"]
    ) for m in history]


@router.post("/memory/clear", response_model=MemoryClearResponse)
def clear_memory(
    user_id: str = "demo_user_001",
    memory: MemoryService = Depends(get_memory_service)
):
    memory.clear_memory(user_id)
    return MemoryClearResponse(status="success", message="All memory and chat context cleared.")
