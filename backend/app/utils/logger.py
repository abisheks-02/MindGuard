import logging
import re

class PIIFilter(logging.Filter):
    """
    Strips Indian Phone Numbers and basic Emails from logs.
    Ensures sensitive data never persists to log aggregators.
    """
    # Naive patterns for demonstration (Indian phone numbers and emails)
    PHONE_REGEX = re.compile(r'\b(?:\+?91[\-\s]?)?[6-9]\d{9}\b')
    EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = self.PHONE_REGEX.sub("[REDACTED_PHONE]", record.msg)
            record.msg = self.EMAIL_REGEX.sub("[REDACTED_EMAIL]", record.msg)
        return True

def setup_logger():
    logger = logging.getLogger("mindguard")
    logger.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add PII Filter
    ch.addFilter(PIIFilter())
    
    logger.addHandler(ch)
    return logger

logger = setup_logger()
