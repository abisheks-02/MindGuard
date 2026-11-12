from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List

class DetectionResult(BaseModel):
    label: str           # Normal, Mild, Moderate, Severe
    score: float         # 0.0 to 1.0 confidence/severity score
    evidence: List[str]  # Matched phrases/tokens for the UI explainability
    detector_name: str   # Name of the detector producing the result

class Detector(ABC):
    """Abstract base class for all severity detectors."""
    
    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        """
        Processes text and returns a DetectionResult containing the label, 
        score, and any extracted evidence.
        """
        pass
