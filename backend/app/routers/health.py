"""Health-check endpoint."""

from fastapi import APIRouter

from app.config import get_settings
from app.dependencies import _detection_service, _voice_service
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        llama_loaded=_detection_service is not None,
        whisper_loaded=_voice_service is not None,
        database=settings.DATABASE_URL.split("://")[0],
    )
