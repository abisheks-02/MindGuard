from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MoodLogRequest(BaseModel):
    user_id: str = "demo_user_001"
    text: Optional[str] = None
    tags: List[str] = []
    emotions: List[str] = []
    triggers: List[str] = []
    sleep_hours: Optional[float] = None
    energy: Optional[int] = None # 1-10

class MoodLogResponse(BaseModel):
    id: int
    severity: str
    severity_score: int
    cbt_feedback: Optional[str]
    timestamp: datetime
    
class HistoryAggregates(BaseModel):
    date: str
    avg_severity: float
    avg_energy: Optional[float]

class MoodHistoryResponse(BaseModel):
    aggregates: List[HistoryAggregates]
    streak_days: int
    trend: str # 'improving', 'stable', 'worsening'
    slope: float
    
class ReminderRequest(BaseModel):
    user_id: str = "demo_user_001"
    reminder_time: str # HH:MM format
