from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import csv

from app.schemas.indicator import IndicatorsResponse
from app.db import get_db
from app.models.indicator import ExploratoryIndicator
from app.dependencies import get_voice_service
from app.services.indicators.indicator_service import IndicatorsService
import shutil
import tempfile
import os

router = APIRouter(tags=["indicators"])

@router.post("/analyze", response_model=IndicatorsResponse)
async def analyze_audio(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    voice_service = Depends(get_voice_service)
):
    # Save audio temporarily
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Transcribe with Whisper
        transcript = voice_service.transcribe(temp_path)
        
        # Analyze Indicators
        service = IndicatorsService(db)
        metrics = service.process_audio(user_id, temp_path, transcript)
        
        return metrics
    finally:
        os.remove(temp_path)

@router.get("/export")
def export_research_data(db: Session = Depends(get_db)):
    """Export raw metrics for research validation of thresholds."""
    indicators = db.query(ExploratoryIndicator).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "session_id", "timestamp", "wpm", "pause_ratio", 
        "mean_pause_length", "pitch_variance", "cmi", 
        "switch_point_freq", "tamil_roman_ratio"
    ])
    
    for ind in indicators:
        writer.writerow([
            ind.id, ind.session_id, ind.timestamp.isoformat(),
            ind.wpm, ind.pause_ratio, ind.mean_pause_length, 
            ind.pitch_variance, ind.cmi, ind.switch_point_freq, 
            ind.tamil_roman_ratio
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mindguard_research_export.csv"}
    )
