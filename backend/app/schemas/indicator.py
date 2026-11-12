from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ZScoreMetric(BaseModel):
    value: float
    z_score: float
    status: str # "above_baseline", "below_baseline", "at_baseline"

class IndicatorsResponse(BaseModel):
    disclaimer: str = "These metrics are exploratory research tools to track personal baselines over time. They are NOT diagnostic indicators and should never replace clinical judgment."
    
    transcript: str
    
    wpm: Optional[ZScoreMetric]
    pause_ratio: Optional[ZScoreMetric]
    mean_pause_length: Optional[ZScoreMetric]
    pitch_variance: Optional[ZScoreMetric]
    
    cmi: Optional[ZScoreMetric]
    switch_point_freq: Optional[ZScoreMetric]
    tamil_roman_ratio: Optional[ZScoreMetric]

class IndicatorDump(BaseModel):
    id: int
    session_id: str
    wpm: Optional[float]
    pause_ratio: Optional[float]
    mean_pause_length: Optional[float]
    pitch_variance: Optional[float]
    cmi: Optional[float]
    switch_point_freq: Optional[float]
    tamil_roman_ratio: Optional[float]
    timestamp: datetime
