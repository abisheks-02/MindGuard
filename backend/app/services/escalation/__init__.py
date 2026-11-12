"""Abstract interface for crisis escalation."""

from abc import ABC, abstractmethod


class EscalationService(ABC):
    @abstractmethod
    def draft_intervention(self, text: str) -> str:
        ...
