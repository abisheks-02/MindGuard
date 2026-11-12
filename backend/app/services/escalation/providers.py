import logging
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)

class MessageProvider(ABC):
    @abstractmethod
    def send_message(self, to_phone: str, message: str, channel: str = "sms") -> str:
        """Sends a message and returns a tracking ID."""
        pass


class MockProvider(MessageProvider):
    def send_message(self, to_phone: str, message: str, channel: str = "sms") -> str:
        msg_id = str(uuid.uuid4())
        logger.info(f"[{channel.upper()}] MOCK DISPATCH to {to_phone}: {message} (ID: {msg_id})")
        return msg_id


# Example placeholder for production:
# class TwilioProvider(MessageProvider):
#     def send_message(self, to_phone: str, message: str, channel: str = "sms") -> str:
#         ...
