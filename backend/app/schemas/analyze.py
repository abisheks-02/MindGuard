from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class AnalyzeRequest(BaseModel):
    text: str
    session_id: str = "demo_user_001"


class CodeSwitchingResult(BaseModel):
    ratio: int
    status: str


class DetectorResult(BaseModel):
    predicted_class: str
    confidence: float
    details: Dict[str, Any] = {}


class AnalyzeResponse(BaseModel):
    predicted_class: str
    confidence: int
    shap_tokens: List[dict]
    class_probabilities: Dict[str, int]
    translation: str = ""
    code_switching: Optional[CodeSwitchingResult] = None
    
    # New fields for ensemble
    needs_review: bool = False
    matched_lexicon_terms: List[str] = []
    per_detector_results: Dict[str, DetectorResult] = {}
    
    # Voice-only fields
    transcribed_text: Optional[str] = None
    acoustic_biomarkers: Optional[dict] = None


class FeedbackRequest(BaseModel):
    analysis_id: int
    correct_label: str
