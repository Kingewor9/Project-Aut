"""Usage API schemas."""
from __future__ import annotations

from pydantic import BaseModel


class UsageResponse(BaseModel):
    channel_id: str
    month_key: str
    posts_generated: int
    posts_published: int
    posts_allowance: int
    remaining: int
    percentage: float
