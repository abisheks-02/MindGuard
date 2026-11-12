"""
MindGuard configuration — reads from .env via pydantic-settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "MindGuard AI Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENABLE_DEMO_AUTH: bool = True
    ENABLE_MOCK_ESCALATION: bool = True
    RETAIN_CHAT_CONTENT: bool = False

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./mindguard.db"

    # ── CORS ─────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Hugging Face ─────────────────────────────────────
    HF_TOKEN: str = ""

    # ── Model names ──────────────────────────────────────
    LLAMA_MODEL_NAME: str = "meta-llama/Llama-3.2-3B-Instruct"
    WHISPER_MODEL_NAME: str = "openai/whisper-tiny"

    # ── Auth & Encryption ────────────────────────────────
    SECRET_KEY: str = "fallback-secret-for-dev"
    MINDGUARD_PRIVACY_SECRET: str = "mindguard-dev-secret-change-in-prod"
    ENCRYPTION_KEY: str = "fallback-fernet-key-32bytes-min!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_runtime_settings(settings: Settings) -> None:
    """Fail closed when an obviously local configuration is used in production."""
    if settings.ENVIRONMENT.lower() != "production":
        return

    errors = []
    if settings.SECRET_KEY == "fallback-secret-for-dev":
        errors.append("SECRET_KEY must be supplied by a secret manager")
    if settings.MINDGUARD_PRIVACY_SECRET == "mindguard-dev-secret-change-in-prod":
        errors.append("MINDGUARD_PRIVACY_SECRET must be supplied by a secret manager")
    if settings.DATABASE_URL.startswith("sqlite"):
        errors.append("DATABASE_URL must use a managed production database")
    if any("localhost" in origin or "127.0.0.1" in origin for origin in settings.CORS_ORIGINS):
        errors.append("CORS_ORIGINS must contain only deployed origins")
    if settings.ENABLE_DEMO_AUTH:
        errors.append("ENABLE_DEMO_AUTH must be false")
    if settings.ENABLE_MOCK_ESCALATION:
        errors.append("ENABLE_MOCK_ESCALATION must be false")
    if settings.RETAIN_CHAT_CONTENT:
        errors.append("RETAIN_CHAT_CONTENT requires an approved consent and retention implementation")
    if errors:
        raise RuntimeError("Unsafe production configuration: " + "; ".join(errors))
