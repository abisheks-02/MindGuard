import logging
import asyncio
import re
import json
from app.services.chatbot import ChatbotService

logger = logging.getLogger(__name__)

# Fallback response if the output guard triggers or model fails
FALLBACK_RESPONSE = (
    "Please take a deep breath. Count to 4, hold for 4, exhale for 4. "
    "This moment is tough, but you're not alone. I'm here to support you. "
    "If you feel overwhelmed, consider reaching out to a helpline."
)

# Output guard restricted words
BLOCKED_WORDS = [
    "diagnose", "cure", "prescribe", "treatment", "medicine", "pill",
    "method", "how to kill", "how to die", "commit suicide"
]


class LlamaChatbotService(ChatbotService):
    def __init__(self, model, tokenizer):
        self._model = model
        self._tokenizer = tokenizer
        
    def generate_response(self, text: str, severity: str, history_str: str) -> str:
        # We can implement a synchronous wrapper if needed, but we'll focus on the streaming method below.
        pass

    async def generate_response_stream(self, text: str, severity: str, history_str: str, themes: str):
        """
        Generates a CBT response and yields it chunk by chunk, applying a post-generation guard.
        Since it's local and we need to guard the full text, we'll generate the full text internally,
        guard it, and then yield it to simulate streaming to the client.
        """
        if self._model is None:
            for word in FALLBACK_RESPONSE.split():
                yield word + " "
                await asyncio.sleep(0.05)
            return

        # Build Prompt based on severity
        prompt = self._build_prompt(text, severity, history_str, themes)
        
        try:
            # We'll use synchronous generation here since the model is small and this is a prototype,
            # but in a real async environment we'd use run_in_executor.
            inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
            outputs = self._model.generate(**inputs, max_new_tokens=120, temperature=0.7)
            raw_response = self._tokenizer.decode(
                outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True
            ).strip()
            
            # Post-generation Output Guard
            if self._triggers_guard(raw_response):
                logger.warning("Output guard triggered. Falling back.")
                final_response = FALLBACK_RESPONSE
            else:
                final_response = raw_response
                
            # If Severe, append helpline
            if severity == "Severe":
                final_response += "\n\nImportant: Please call iCall at 9152987821. You are not alone."

        except Exception as e:
            logger.exception("CBT generation failed: %s", e)
            final_response = FALLBACK_RESPONSE

        # Yield via Server-Sent Events (SSE) format
        for chunk in final_response.split(" "):
            yield chunk + " "
            await asyncio.sleep(0.02) # Simulate typing delay

    def generate_quick_replies(self, text: str, severity: str) -> list[str]:
        """Generates 3 contextual quick replies."""
        if self._model is None or severity == "Severe":
            return ["I need to talk to someone", "Tell me more about the breathing exercise", "I'm feeling a bit better"]
            
        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
            "You are an AI generating 3 short suggested replies (under 5 words each) for a user to click, based on their last message. "
            "Return ONLY the 3 replies separated by a pipe (|). No numbering.\n"
            "<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
            f'User said: "{text}"'
            "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        )
        
        try:
            inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
            outputs = self._model.generate(**inputs, max_new_tokens=30, temperature=0.8)
            resp = self._tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True).strip()
            replies = [r.strip() for r in resp.split("|") if r.strip()][:3]
            if len(replies) < 3:
                return ["Yes", "Tell me more", "I don't know"]
            return replies
        except:
            return ["I need to talk to someone", "Tell me more about the breathing exercise", "I'm feeling a bit better"]

    def generate_weekly_plan(self, history: str) -> dict:
        """Generates a structured weekly JSON plan based on mood history."""
        if self._model is None:
            return {
                "days": [
                    {"day": "Monday", "activity": "Take a 10 min walk", "cbt": "Identify one negative thought today", "reflection": "What went well today?"},
                    {"day": "Tuesday", "activity": "Listen to calming music", "cbt": "Reframe the negative thought", "reflection": "Who can I reach out to?"}
                ]
            }

        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
            "You are an AI generating a 7-day CBT wellness plan. Output ONLY valid JSON containing an array 'days' where each object has 'day', 'activity', 'cbt', 'reflection'. Do NOT output markdown formatting like ```json.\n"
            "<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
            f'User History: "{history}"'
            "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        )
        try:
            inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
            outputs = self._model.generate(**inputs, max_new_tokens=300, temperature=0.5)
            resp = self._tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True).strip()
            # Clean possible markdown
            if resp.startswith("```json"): resp = resp[7:]
            if resp.startswith("```"): resp = resp[3:]
            if resp.endswith("```"): resp = resp[:-3]
            return json.loads(resp.strip())
        except Exception as e:
            logger.error(f"Failed to generate JSON plan: {e}")
            return {"days": [{"day": "Day 1", "activity": "Rest", "cbt": "Breathe", "reflection": "I am okay"}]}

    def _build_prompt(self, text: str, severity: str, history_str: str, themes: str) -> str:
        # Base Persona
        system_prompt = (
            "You are a compassionate CBT-trained counsellor. Respond in Tamil-English code-mixed language. "
            "Keep response under 100 words. Never diagnose. Always be warm.\n"
        )
        
        # Memory Injection
        memory_ctx = f"User's Recent States: {history_str}\nRecurring Themes: {themes}\n"
        
        # Severity Templates
        if severity == "Normal":
            template = "Provide a supportive check-in. One breathing exercise, one reframing, one affirmation."
        elif severity == "Mild":
            template = "Focus on cognitive reframing. One breathing exercise, one reframing, one affirmation."
        elif severity == "Moderate":
            template = "Focus on grounding techniques and reframing. Gently encourage professional help. One breathing exercise, one reframing, one affirmation."
        elif severity == "Severe":
            template = "Keep it very short, calm, and safety-first. Do NOT give CBT homework or exercises. Prioritize immediate safety and emphasize they are not alone."
        else:
            template = "One breathing exercise, one cognitive reframing technique, and one affirmation."
            
        full_system = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_prompt}{memory_ctx}INSTRUCTION: {template}<|eot_id|>"
        user_turn = f"<|start_header_id|>user<|end_header_id|>\nUser says: \"{text}\" (Severity: {severity})<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        
        return full_system + user_turn

    def _triggers_guard(self, text: str) -> bool:
        text_lower = text.lower()
        for word in BLOCKED_WORDS:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                return True
        return False
