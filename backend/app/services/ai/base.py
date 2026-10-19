"""
Abstract base class for AI content generation providers.

New providers (OpenAI, Anthropic, etc.) implement this interface.
The rest of the application only depends on BaseAIProvider.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PollPayload:
    """Structured poll data accepted by Telegram's sendPoll method."""
    question: str
    options: list[str]
    poll_type: str = "regular"
    is_anonymous: bool = True
    allows_multiple_answers: bool = False
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None


@dataclass
class GenerationRequest:
    """All context needed to generate a Telegram post."""
    channel_name: str
    niche: str
    topics: list[str]
    audience: str
    writing_personality: str
    post_formats: list[str]
    content_strategy: str
    products_and_offers: str
    cta_library: list[str]
    rules: str
    goals: str
    max_post_characters: int
    extra_instructions: str = ""


@dataclass
class GenerationResult:
    content: str
    provider: str
    model: str
    tokens_used: int = 0
    poll: Optional[PollPayload] = None


class BaseAIProvider(ABC):
    """Abstract AI provider — all providers must implement generate()."""

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate a Telegram post based on the request context."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...
