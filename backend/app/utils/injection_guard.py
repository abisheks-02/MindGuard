import re
from fastapi import HTTPException

# A basic prompt injection blocklist.
# In a production system, this could be backed by a smaller dedicated LLM or a more exhaustive regex engine.
SUSPICIOUS_PATTERNS = [
    r"ignore\s+all\s+previous\s+instructions",
    r"you\s+are\s+now\s+a",
    r"system\s+prompt",
    r"forget\s+everything\s+i\s+said",
    r"disregard\s+the\s+above"
]

def check_prompt_injection(text: str):
    text_lower = text.lower()
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text_lower):
            raise HTTPException(
                status_code=400, 
                detail="Security Guard: Suspicious prompt injection pattern detected. Request blocked."
            )
    return True
