"""Channel request/response schemas (separate from DB models)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.channel import (
    AutomationStatus,
    ChannelAudience,
    ChannelBrain,
    ChannelRules,
    ChannelSchedule,
    CTAConfig,
    ProductOffer,
    PublishMode,
    WritingDNA,
)


# ─── Requests ─────────────────────────────────────────────────────────────────

class ChannelCreateRequest(BaseModel):
    telegram_channel_id: str


class ChannelResolveRequest(BaseModel):
    telegram_channel_id: str


class ChannelResolveResponse(BaseModel):
    telegram_channel_id: str
    username: Optional[str] = None
    name: str
    photo_url: Optional[str] = None


class ChannelUpdateRequest(BaseModel):
    name: Optional[str] = None
    photo_url: Optional[str] = None
    brain: Optional[ChannelBrain] = None
    schedule: Optional[ChannelSchedule] = None
    publish_mode: Optional[PublishMode] = None
    automation_status: Optional[AutomationStatus] = None


class IdentityOnboardingRequest(BaseModel):
    niches: list[str] = []
    topics: list[str] = []
    audience: ChannelAudience = ChannelAudience()
    conversion_goals: list[str] = []
    rules: ChannelRules = ChannelRules()
    frequency: str = "daily"
    schedule: ChannelSchedule = ChannelSchedule()


class BrainOnboardingRequest(BaseModel):
    writing_dna: WritingDNA
    content_types: list[str] = []


class StyleAnalysisRequest(BaseModel):
    sample_posts: list[str]


class StyleAnalysisResponse(WritingDNA):
    remaining_analyses: int = 0


class CTAOnboardingRequest(BaseModel):
    enabled: bool = False
    products: list[ProductOffer] = []
    ctas: list[CTAConfig] = []
    promotion_style: Optional[str] = None
    max_promotions_per_week: int = 0


class ActivationRequest(BaseModel):
    publish_mode: PublishMode = PublishMode.APPROVAL


class TestGenerationRequest(BaseModel):
    content_type: str = "Educational"
    topic: str
    context: Optional[str] = None


class TestGenerationResponse(BaseModel):
    content: str
    remaining_tests: int


class TestGenerationFeedbackRequest(BaseModel):
    feedback: str


# ─── Responses ────────────────────────────────────────────────────────────────

class UsageSummary(BaseModel):
    posts_generated: int
    posts_published: int
    posts_allowance: int
    month_key: str

    @property
    def remaining(self) -> int:
        return max(0, self.posts_allowance - self.posts_generated)

    @property
    def percentage(self) -> float:
        if self.posts_allowance == 0:
            return 0.0
        return min(100.0, (self.posts_generated / self.posts_allowance) * 100)


class ChannelResponse(BaseModel):
    id: str
    user_id: str
    telegram_channel_id: str
    username: Optional[str]
    name: str
    photo_url: Optional[str]
    brain: ChannelBrain
    schedule: ChannelSchedule
    publish_mode: PublishMode
    automation_status: AutomationStatus
    is_bot_admin: bool
    is_active: bool
    usage: Optional[UsageSummary] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True
