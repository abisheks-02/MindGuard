# MindGuard Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                      Frontend (React/Vite)                   │
│  pages/  →  hooks/  →  api/client.js  →  HTTP  →  Backend   │
└──────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   FastAPI Gateway   │
                    │   /api/v1/*         │
                    │   CORS · Logging    │
                    │   Error Handler     │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
    ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
    │  Routers  │      │  Routers  │      │  Routers  │
    │ analyze   │      │  chat     │      │  mood     │
    │ voice     │      │  quest    │      │ escalation│
    └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
          │                   │                   │
          └───────────┬───────┘───────────┬───────┘
                      │                   │
              ┌───────▼───────┐   ┌───────▼───────┐
              │   Services    │   │   Services    │
              │ (Interfaces)  │   │ (Memory)      │
              │ DetectionSvc  │   │ SQLAlchemy     │
              │ ChatbotSvc    │   │ Session        │
              │ EscalationSvc │   └───────┬───────┘
              │ VoiceSvc      │           │
              └───────┬───────┘   ┌───────▼───────┐
                      │           │   Database     │
              ┌───────▼───────┐   │   SQLite/PG    │
              │   ML Models   │   └───────────────┘
              │   Llama 3.2   │
              │   Whisper     │
              └───────────────┘
```

## Service Interface Pattern

Every service is defined as an abstract base class (ABC). Routers depend on
the interface, never the implementation. Implementations are wired at
startup in `app/main.py` via dependency injection.

### Example: Detection Service

```python
# Interface (app/services/detection/__init__.py)
class DetectionService(ABC):
    @abstractmethod
    def analyze(self, text: str) -> dict: ...

# Llama implementation (app/services/detection/llama_detection.py)
class LlamaDetectionService(DetectionService): ...

# Mock implementation (app/services/detection/mock_detection.py)
class MockDetectionService(DetectionService): ...
```

## Database

- **Dev**: SQLite via `sqlite:///./mindguard.db`
- **Prod**: PostgreSQL via `DATABASE_URL` env var
- **ORM**: SQLAlchemy 2.0 with Alembic migrations
- **Models**: User, MoodLog, Alert, WellnessPlan, Quest

## API Versioning

All endpoints are prefixed with `/api/v1/`. When breaking changes are
needed, a `/api/v2/` prefix can be added alongside v1.

## Configuration

All settings are managed via `pydantic-settings` in `app/config.py`,
reading from a `.env` file. No secrets are hardcoded.
