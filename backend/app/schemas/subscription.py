"""Subscription API schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.subscription import SubscriptionStatus
from app.config.plans import Plan


class SubscriptionResponse(BaseModel):
    plan_id: str
    plan_name: str
    status: SubscriptionStatus
    max_channels: int
    posts_per_channel: int
    max_post_characters: int
    price_stars: int
    price_label: str
    features: list[str]
    renews_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        use_enum_values = True


class AllPlansResponse(BaseModel):
    plans: list[PlanResponse]
    current_plan_id: str


class PlanResponse(BaseModel):
    id: str
    name: str
    max_channels: int
    posts_per_channel: int
    max_post_characters: int
    price_stars: int
    price_label: str
    features: list[str]
    is_current: bool = False
