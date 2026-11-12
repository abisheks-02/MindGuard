"""Voice analysis router."""

import os
import tempfile
import logging

from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional

from app.services.detection import DetectionService
from app.services.voice import VoiceService
from app.dependencies import get_detection_service, get_voice_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["voice"])


@router.post("/analyze/voice")
async def analyze_voice(
    file: UploadFile = File(...),
    duration: Optional[float] = Form(None),
    detection: DetectionService = Depends(get_detection_service),
    voice: VoiceService = Depends(get_voice_service),
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        transcribed_text = voice.transcribe(tmp_path)
        analysis = detection.analyze(transcribed_text)
        analysis["transcribed_text"] = transcribed_text

        if duration and duration > 0:
            word_count = len(transcribed_text.split())
            wpm = round((word_count / duration) * 60)
            status = "Psychomotor Retardation (Slowed)" if wpm < 110 else "Normal Prosody"
            analysis["acoustic_biomarkers"] = {"wpm": wpm, "status": status}

        return analysis
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
