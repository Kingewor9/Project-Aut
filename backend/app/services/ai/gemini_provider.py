"""
Google Gemini implementation of BaseAIProvider.
"""
from __future__ import annotations

import json
import logging

import google.generativeai as genai

from app.config.settings import settings
from app.services.ai.base import BaseAIProvider, GenerationRequest, GenerationResult, PollPayload
from app.services.ai.prompt_builder import build_prompt

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Generates Telegram post content using Google Gemini."""

    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(settings.gemini_model)

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        content = await self.generate_text(build_prompt(request))
        if _is_poll_only(request.post_formats):
            poll = _parse_poll(content)
            return GenerationResult(
                content=poll.question,
                provider=self.provider_name,
                model=settings.gemini_model,
                poll=poll,
            )
        content = _enforce_character_limit(content, request.max_post_characters)
        return GenerationResult(
            content=content,
            provider=self.provider_name,
            model=settings.gemini_model,
        )

    async def generate_text(
        self,
        prompt: str,
        max_output_tokens: int | None = None,
        response_mime_type: str | None = None,
    ) -> str:
        """Generate raw text for structured tasks such as style analysis."""

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.85,
                **({"max_output_tokens": max_output_tokens} if max_output_tokens else {}),
                **({"response_mime_type": response_mime_type} if response_mime_type else {}),
            )
            response = await self._model.generate_content_async(
                prompt,
                generation_config=generation_config,
            )
            if not response.candidates:
                feedback = getattr(response, "prompt_feedback", None)
                raise RuntimeError(f"Gemini returned no candidates. Prompt feedback: {feedback}")
            finish_reason = response.candidates[0].finish_reason
            logger.info("Gemini generation finished with reason: %s", finish_reason)
            content = "".join(
                part.text
                for part in response.candidates[0].content.parts
                if getattr(part, "text", None)
            ).strip()
            if not content:
                raise RuntimeError(f"Gemini returned an empty response. Finish reason: {finish_reason}")
            return content
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

# Singleton instance
_gemini_provider: GeminiProvider | None = None


def _enforce_character_limit(content: str, max_characters: int) -> str:
    """Apply the plan limit if the model ignores the prompt instruction."""
    if len(content) <= max_characters:
        return content
    shortened = content[:max_characters].rstrip()
    boundary = shortened.rfind(" ")
    return shortened[:boundary].rstrip() if boundary > 0 else shortened


def _is_poll_only(post_formats: list[str]) -> bool:
    return len(post_formats) == 1 and post_formats[0].strip().lower() == "poll"


def _parse_poll(raw: str) -> PollPayload:
    cleaned = raw.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        cleaned = next((part for part in parts if "{" in part), cleaned)
        cleaned = cleaned.removeprefix("json").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Gemini did not return a poll JSON object")
    data = json.loads(cleaned[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError("Gemini poll response was not an object")
    question = str(data.get("question", "")).strip()
    options = [str(option).strip() for option in data.get("options", [])]
    poll_type = str(data.get("poll_type", "regular")).lower()
    if not question or not 2 <= len(options) <= 10:
        raise ValueError("A Telegram poll needs a question and 2 to 10 options")
    if poll_type not in {"regular", "quiz"}:
        raise ValueError("Telegram poll_type must be regular or quiz")
    correct_option_id = data.get("correct_option_id")
    if poll_type == "quiz":
        if not isinstance(correct_option_id, int) or not 0 <= correct_option_id < len(options):
            raise ValueError("Quiz polls need a valid zero-based correct_option_id")
        allows_multiple_answers = False
    else:
        correct_option_id = None
        allows_multiple_answers = bool(data.get("allows_multiple_answers", False))
    return PollPayload(
        question=question,
        options=options,
        poll_type=poll_type,
        is_anonymous=bool(data.get("is_anonymous", True)),
        allows_multiple_answers=allows_multiple_answers,
        correct_option_id=correct_option_id,
        explanation=data.get("explanation") if poll_type == "quiz" else None,
    )


def get_gemini_provider() -> GeminiProvider:
    global _gemini_provider
    if _gemini_provider is None:
        _gemini_provider = GeminiProvider()
    return _gemini_provider
