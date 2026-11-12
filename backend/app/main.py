"""
MindGuard — FastAPI Application Factory
========================================
All model loading, service wiring, and router mounting happens here.
Run with: uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings, validate_runtime_settings
from app.logging_config import setup_logging
from app.models import Base
from app.db import engine

# Service implementations
from app.services.detection.ensemble import EnsembleDetectionService
from app.services.detection.mock_detection import MockDetectionService
from app.services.chatbot.llama_chatbot import LlamaChatbotService
from app.services.escalation.engine import EscalationEngine
from app.services.escalation.providers import MockProvider
from app.services.voice.whisper_voice import WhisperVoiceService

# DI setters
from app.dependencies import (
    set_detection_service,
    set_chatbot_service,
    set_escalation_engine,
    set_voice_service,
)

from app.routers import health, analyze, chat, escalation, mood, voice, quest, indicators, auth, trajectory, privacy

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


# ── Lifespan (replaces deprecated @app.on_event) ───────

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    validate_runtime_settings(settings)

    # Create tables (Alembic preferred in prod)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")

    # ── Load ML models ──────────────────────────────────
    llama_model = None
    llama_tokenizer = None
    asr_pipeline = None

    logger.info("Loading Llama 3.2 3B-Instruct …")
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

        quantization_config = BitsAndBytesConfig(load_in_4bit=True)
        llama_tokenizer = AutoTokenizer.from_pretrained(
            settings.LLAMA_MODEL_NAME, token=settings.HF_TOKEN
        )
        llama_model = AutoModelForCausalLM.from_pretrained(
            settings.LLAMA_MODEL_NAME,
            quantization_config=quantization_config,
            device_map="auto",
            token=settings.HF_TOKEN,
        )
        logger.info("Llama loaded successfully.")
    except Exception as e:
        logger.warning("Llama failed to load — falling back to mock: %s", e)

    logger.info("Loading Whisper ASR …")
    try:
        from transformers import pipeline as hf_pipeline

        asr_pipeline = hf_pipeline(
            "automatic-speech-recognition", model=settings.WHISPER_MODEL_NAME
        )
        logger.info("Whisper ASR loaded successfully.")
    except Exception as e:
        logger.warning("Whisper failed to load: %s", e)

    # ── Wire services ───────────────────────────────────
    if llama_model is not None:
        set_detection_service(EnsembleDetectionService(
            llama_model, 
            llama_tokenizer,
            lexicon_path="data/lexicon.json",
            variants_path="data/variants_map.json",
            test_cases_path="data/test_cases.csv"
        ))
    else:
        # Fallback to mock if no LLM
        set_detection_service(EnsembleDetectionService(
            None, 
            None,
            lexicon_path="data/lexicon.json",
            variants_path="data/variants_map.json",
            test_cases_path="data/test_cases.csv"
        ))

    set_chatbot_service(LlamaChatbotService(llama_model, llama_tokenizer))
    
    # Init Escalation Engine
    mock_provider = MockProvider()
    set_escalation_engine(EscalationEngine("config/escalation_rules.yaml", mock_provider))
    
    set_voice_service(WhisperVoiceService(asr_pipeline))

    logger.info("All services wired. MindGuard is ready.")
    yield
    logger.info("MindGuard shutting down.")


# ── App factory ─────────────────────────────────────────

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global error handler ────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again."},
        )

    # ── Mount versioned routers ─────────────────────────
    prefix = "/api/v1"
    app.include_router(health.router, prefix=prefix)
    app.include_router(analyze.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)
    app.include_router(escalation.router, prefix=prefix)
    app.include_router(mood.router, prefix=prefix)
    app.include_router(voice.router, prefix=prefix)
    app.include_router(quest.router, prefix=prefix)
    app.include_router(indicators.router, prefix=prefix)
    app.include_router(auth.router, prefix=prefix)
    app.include_router(trajectory.router, prefix=prefix)
    app.include_router(privacy.router, prefix=prefix)

    return app


app = create_app()
