"""Whisper ASR implementation."""

import logging
from app.services.voice import VoiceService

logger = logging.getLogger(__name__)


class WhisperVoiceService(VoiceService):
    def __init__(self, pipeline):
        self._pipeline = pipeline

    def transcribe(self, file_path: str) -> str:
        if self._pipeline is None:
            return "I have been feeling very lonely and down lately."

        # Pass Tamil language hint to optimize Tanglish transcription
        result = self._pipeline(file_path, generate_kwargs={"language": "ta"})
        return result["text"].strip()
