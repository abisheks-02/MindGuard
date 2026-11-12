"""Abstract interface for the severity-detection pipeline."""

from abc import ABC, abstractmethod


class DetectionService(ABC):
    """All detection implementations must satisfy this contract."""

    @abstractmethod
    def analyze(self, text: str) -> dict:
        """Return an AnalyzeResponse-compatible dict."""
        ...
