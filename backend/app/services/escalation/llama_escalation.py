"""Llama-based crisis SMS drafting."""

import logging
from app.services.escalation import EscalationService

logger = logging.getLogger(__name__)

DEFAULT_DRAFT = "Hi, we are here for you. A counselor is available to speak with you right now."


class LlamaEscalationService(EscalationService):
    def __init__(self, model, tokenizer):
        self._model = model
        self._tokenizer = tokenizer

    def draft_intervention(self, text: str) -> str:
        if self._model is None:
            return DEFAULT_DRAFT

        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
            "You are a crisis intervention AI. Draft a highly empathetic, 2-sentence SMS "
            "to the user offering a free, immediate counseling appointment. "
            "Acknowledge their specific struggle briefly based on their text.\n"
            "Keep it extremely brief and warm."
            "<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
            f'User text: "{text}"'
            "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        )

        try:
            inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
            outputs = self._model.generate(**inputs, max_new_tokens=60, temperature=0.5)
            return self._tokenizer.decode(
                outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True
            ).strip()
        except Exception as e:
            logger.exception("SMS draft generation failed: %s", e)
            return DEFAULT_DRAFT
