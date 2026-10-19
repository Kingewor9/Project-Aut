"""
FastAPI dependency — validates Telegram initData and returns the current user.
All protected routes use: current_user: UserModel = Depends(get_current_user)
"""
from __future__ import annotations

from fastapi import Depends, Header
from typing import Optional

from app.core.exceptions import UnauthorizedException
from app.core.security import verify_telegram_init_data
from app.models.user import UserModel
from app.services import user_service
from app.config.settings import settings


async def get_current_user(
    x_init_data: Optional[str] = Header(default=None, alias="X-Init-Data"),
) -> UserModel:
    """
    Extract and validate Telegram initData from the X-Init-Data header.
    Returns the authenticated UserModel (created if not seen before).
    """
    if not x_init_data:
        raise UnauthorizedException("Missing X-Init-Data header")

    # In non-production with an empty bot token, skip validation for dev
    if not settings.telegram_bot_token and not settings.is_production:
        # Dev-only: parse without signature validation
        import urllib.parse
        import json
        params = dict(urllib.parse.parse_qsl(x_init_data, keep_blank_values=True))
        user_data = json.loads(params.get("user", "{}"))
        if not user_data.get("id"):
            raise UnauthorizedException("No user data in initData")
    else:
        payload = verify_telegram_init_data(x_init_data)
        user_data = payload.get("user")
        if not user_data:
            raise UnauthorizedException("No user in initData")

    return await user_service.get_or_create_user(user_data)
