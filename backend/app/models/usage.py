"""
Usage MongoDB document model.

Tracks AI post generation counts per channel per calendar month.
One document per (channel_id, month_key) pair.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.user import PyObjectId


class UsageModel(BaseModel):
    """Usage record per channel per month."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str                    # Owner user ID (for quick queries)
    channel_id: str                 # Channel _id (str)
    month_key: str                  # "YYYY-MM" e.g. "2026-09"

    posts_generated: int = 0        # AI generations this month
    posts_published: int = 0        # Actually published to channel
    posts_allowance: int = 0        # Snapshot of plan allowance at record creation
    test_generations: int = 0       # AI test-post generations used this month
    test_generation_bonus: int = 0  # Purchased AI test-post generations
    style_analyses: int = 0         # Analyze-my-post calls used this month
    style_analysis_bonus: int = 0   # Purchased Analyze-my-post calls

    last_generated_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
