"""Abstract interface for persistent memory (mood logs, quests, plans)."""

from abc import ABC, abstractmethod


class MemoryService(ABC):
    @abstractmethod
    def ensure_user(self, session_id: str) -> None: ...

    @abstractmethod
    def log_mood(self, session_id: str, text: str, severity: str) -> None: ...

    @abstractmethod
    def get_mood_history(self, session_id: str, limit: int = 7) -> list[dict]: ...

    @abstractmethod
    def log_alert(self, text: str) -> None: ...

    @abstractmethod
    def save_wellness_plan(self, session_id: str, plan_text: str) -> None: ...

    @abstractmethod
    def get_latest_wellness_plan(self, session_id: str) -> dict | None: ...

    @abstractmethod
    def save_quest(self, session_id: str, quest_text: str) -> None: ...

    @abstractmethod
    def get_quests(self, session_id: str) -> list[dict]: ...

    @abstractmethod
    def complete_quest(self, quest_id: int) -> None: ...
