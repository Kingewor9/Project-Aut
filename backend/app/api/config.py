"""
Public configuration endpoint.

Returns non-sensitive configuration values the frontend needs:
- Support Telegram handle
- Announcement channel link
- Social media links
These are loaded from environment variables (not hard-coded in frontend).
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.config.settings import settings

router = APIRouter(prefix="/config", tags=["config"])


class PublicConfig(BaseModel):
    support_username: str
    announce_channel: str
    social_twitter: str
    social_instagram: str
    social_tiktok: str
    social_website: str


@router.get("", response_model=PublicConfig)
async def get_public_config():
    """Return public configuration values for the Mini App frontend."""
    return PublicConfig(
        support_username=settings.telegram_support_username,
        announce_channel=settings.telegram_announce_channel,
        social_twitter=settings.social_twitter,
        social_instagram=settings.social_instagram,
        social_tiktok=settings.social_tiktok,
        social_website=settings.social_website,
    )
