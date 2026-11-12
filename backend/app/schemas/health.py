from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    llama_loaded: bool
    whisper_loaded: bool
    database: str
