"""Abstract interface for voice/ASR processing."""

from abc import ABC, abstractmethod


class VoiceService(ABC):
    @abstractmethod
    def transcribe(self, file_path: str) -> str:
        ...
