"""
Subscription MongoDB document model.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from enum import Enum

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.user import PyObjectId


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class SubscriptionModel(BaseModel):
    """One subscription record per user (upserted on plan change)."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str                            # str(ObjectId) of parent user
    plan_id: str = "free"                  # "free" | "starter" | "pro" | "agency"
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE

    # Telegram Stars payment tracking
    stars_invoice_id: Optional[str] = None
    stars_amount: int = 0

    # Dates
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    renews_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        use_enum_values = True
