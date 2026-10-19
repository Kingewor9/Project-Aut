"""
Centralized subscription plan definitions.

All plan limits, prices, and metadata live here.
Change these values to update the entire system — nothing else needs updating.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Plan:
    id: str                         # e.g. "free", "starter", "pro", "agency"
    name: str                       # Display name
    max_channels: int               # Number of channels allowed
    posts_per_channel: int          # AI posts per channel per month
    max_post_characters: int        # Maximum characters in one generated post
    price_stars: int                # Telegram Stars price (0 = free)
    price_label: str                # Human-readable price
    features: list[str] = field(default_factory=list)

    @property
    def total_posts(self) -> int:
        return self.max_channels * self.posts_per_channel


# ─── Plan Definitions ─────────────────────────────────────────────────────────
PLANS: dict[str, Plan] = {
    "free": Plan(
        id="free",
        name="Free",
        max_channels=1,
        posts_per_channel=25,
        max_post_characters=750,
        price_stars=0,
        price_label="Free",
        features=[
            "1 Telegram channel",
            "25 AI posts / month",
            "Basic scheduling",
        ],
    ),
    "starter": Plan(
        id="starter",
        name="Starter",
        max_channels=1,
        posts_per_channel=90,
        max_post_characters=1500,
        price_stars=500,
        price_label="500 Stars / month",
        features=[
            "1 Telegram channel",
            "90 AI posts / month",
            "Full scheduling",
            "Approval mode",
        ],
    ),
    "pro": Plan(
        id="pro",
        name="Pro",
        max_channels=3,
        posts_per_channel=150,
        max_post_characters=2500,
        price_stars=750,
        price_label="750 Stars / month",
        features=[
            "3 Telegram channels",
            "150 AI posts / channel / month",
            "Auto-publish mode",
            "Priority support",
        ],
    ),
    "agency": Plan(
        id="agency",
        name="Agency",
        max_channels=10,
        posts_per_channel=150,
        max_post_characters=4000,
        price_stars=1500,
        price_label="1,500 Stars / month",
        features=[
            "10 Telegram channels",
            "150 AI posts / channel / month",
            "Auto-publish mode",
            "Multi-channel management",
            "Priority support",
        ],
    ),
}

DEFAULT_PLAN_ID = "free"


def get_plan(plan_id: str) -> Plan:
    """Return a Plan by ID, falling back to free."""
    return PLANS.get(plan_id, PLANS[DEFAULT_PLAN_ID])
