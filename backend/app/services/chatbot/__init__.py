"""Abstract interface for the CBT chatbot."""

from abc import ABC, abstractmethod


class ChatbotService(ABC):
    @abstractmethod
    def generate_response(self, text: str, severity: str, history_str: str) -> str:
        ...
