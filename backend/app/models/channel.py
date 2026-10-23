"""
Channel MongoDB document model.

Each channel belongs to exactly one user.
A user may have many channels (limited by plan).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional
from enum import Enum

from bson import ObjectId
from pydantic import BaseModel, Field, model_validator

from app.models.user import PyObjectId


class PublishMode(str, Enum):
    APPROVAL = "approval"       # AI sends draft; owner approves before publishing
    AUTO = "auto"               # AI publishes directly on schedule


class AutomationStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"


class WritingMode(str, Enum):
    MANUAL = "manual"
    SAMPLES = "samples"


class QuizPollExample(BaseModel):
    question: str
    options: list[str] = Field(min_length=2, max_length=10)
    correct_option_id: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_quiz_poll(self) -> "QuizPollExample":
        if not self.question.strip():
            raise ValueError("Quiz poll questions cannot be blank")
        if any(not option.strip() for option in self.options):
            raise ValueError("Quiz poll options cannot be blank")
        if self.correct_option_id >= len(self.options):
            raise ValueError("The correct answer must match one of the options")
        return self


class ChannelAudience(BaseModel):
    age_range: Optional[str] = None
    location: Optional[str] = None
    gender: Optional[str] = None
    experience_level: Optional[str] = None
    interests: list[str] = Field(default_factory=list)
    description: Optional[str] = None


class ChannelRules(BaseModel):
    always_do: list[str] = Field(default_factory=list)
    never_do: list[str] = Field(default_factory=list)
    forbidden_topics: list[str] = Field(default_factory=list)
    forbidden_words: list[str] = Field(default_factory=list)
    custom_rules: Optional[str] = None


class WritingDNA(BaseModel):
    mode: WritingMode = WritingMode.MANUAL
    content_style: Literal["text_only", "quiz_polls"] = "text_only"
    tone: list[str] = Field(default_factory=list)
    personality: list[str] = Field(default_factory=list)
    vocabulary: Optional[str] = None
    sentence_style: Optional[str] = None
    paragraph_structure: Optional[str] = None
    average_post_length: Optional[str] = None
    hook_style: Optional[str] = None
    formatting: list[str] = Field(default_factory=list)
    emoji_usage: Optional[str] = None
    post_length: Optional[str] = None
    cta_style: Optional[str] = None
    advanced_instructions: Optional[str] = None
    sample_posts: list[str] = Field(default_factory=list)
    sample_polls: list[QuizPollExample] = Field(default_factory=list)
    style_analysis: dict[str, Any] = Field(default_factory=dict)
    style_analysis_status: Optional[str] = None


class ProductOffer(BaseModel):
    name: str
    description: Optional[str] = None
    problem_solved: Optional[str] = None
    target_audience: Optional[str] = None
    price: Optional[str] = None
    selling_points: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    proof: Optional[str] = None


class CTAConfig(BaseModel):
    product_name: Optional[str] = None
    type: str
    telegram_username: Optional[str] = None
    keyword: Optional[str] = None
    destination_url: Optional[str] = None
    instruction: Optional[str] = None


class PromotionScheduleItem(BaseModel):
    day: str
    time: Optional[str] = None
    product_name: Optional[str] = None
    max_promotions: int = 1


class ChannelBrain(BaseModel):
    """
    The Channel Brain / Channel DNA.
    Structured representation of everything the AI needs to know about the channel.
    These fields are collected during onboarding and editable in Channel Settings.
    """
    niche: Optional[str] = None
    topics: list[str] = Field(default_factory=list)
    audience_description: Optional[str] = None
    writing_personality: Optional[str] = None
    post_formats: list[str] = Field(default_factory=list)
    content_strategy: Optional[str] = None
    products_and_offers: Optional[str] = None
    cta_library: list[str] = Field(default_factory=list)
    rules_and_restrictions: Optional[str] = None
    goals: Optional[str] = None
    # Future expansion fields can be added here without restructuring
    extra: dict[str, Any] = Field(default_factory=dict)
    niches: list[str] = Field(default_factory=list)
    audience: ChannelAudience = Field(default_factory=ChannelAudience)
    conversion_goals: list[str] = Field(default_factory=list)
    rules: ChannelRules = Field(default_factory=ChannelRules)
    content_types: list[str] = Field(default_factory=list)
    frequency: str = "daily"
    writing_dna: WritingDNA = Field(default_factory=WritingDNA)
    products: list[ProductOffer] = Field(default_factory=list)
    ctas: list[CTAConfig] = Field(default_factory=list)
    cta_enabled: bool = False
    promotion_style: Optional[str] = None
    promotion_schedule: list[PromotionScheduleItem] = Field(default_factory=list)
    max_promotions_per_week: int = 0


class ChannelSchedule(BaseModel):
    timezone: str = "UTC"
    posts_per_day: int = 1
    posting_times: list[str] = Field(default_factory=list)  # e.g. ["09:00", "18:00"]
    active_days: list[str] = Field(
        default_factory=lambda: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    )
    daily_times: dict[str, list[str]] = Field(default_factory=dict)


class ChannelModel(BaseModel):
    """Represents a row in the `channels` MongoDB collection."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str                            # Owner user _id (str)
    telegram_channel_id: str               # Telegram channel ID (e.g. -1001234567890 or @username)
    username: Optional[str] = None         # @handle if public
    name: str                              # Channel display name
    photo_url: Optional[str] = None        # Channel avatar

    # AI configuration
    brain: ChannelBrain = Field(default_factory=ChannelBrain)
    schedule: ChannelSchedule = Field(default_factory=ChannelSchedule)
    publish_mode: PublishMode = PublishMode.APPROVAL
    automation_status: AutomationStatus = AutomationStatus.INACTIVE

    # State
    is_bot_admin: bool = False             # Whether our bot has admin rights
    is_active: bool = False               # Fully set up and running

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        use_enum_values = True
