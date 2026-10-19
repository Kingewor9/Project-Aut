"""
Telegram Mini App authentication / HMAC-SHA256 validation.

The backend validates Telegram's initData string so the frontend cannot
forge or spoof a user identity.
"""
from __future__ import annotations

import hashlib
import hmac
import urllib.parse
from typing import Any

from app.config.settings import settings
from app.core.exceptions import UnauthorizedException


def _build_data_check_string(params: dict[str, str]) -> str:
    """
    Sort keys alphabetically, join as key=value\\n lines,
    excluding the 'hash' key itself.
    """
    pairs = sorted(
        (k, v) for k, v in params.items() if k != "hash"
    )
    return "\n".join(f"{k}={v}" for k, v in pairs)


def verify_telegram_init_data(raw_init_data: str) -> dict[str, Any]:
    """
    Validate Telegram Mini App initData and return the parsed payload.

    Raises UnauthorizedException on failure.
    """
    if not raw_init_data:
        raise UnauthorizedException("Missing initData")

    # Parse the URL-encoded initData
    params: dict[str, str] = dict(urllib.parse.parse_qsl(raw_init_data, keep_blank_values=True))

    received_hash = params.get("hash", "")
    if not received_hash:
        raise UnauthorizedException("Missing initData hash")

    # Build the secret key: HMAC-SHA256(bot_token, "WebAppData")
    secret_key = hmac.new(
        b"WebAppData",
        settings.telegram_bot_token.encode(),
        hashlib.sha256,
    ).digest()

    # Build the expected hash
    data_check_string = _build_data_check_string(params)
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise UnauthorizedException("Invalid initData signature")

    # Parse the user JSON field
    import json as _json

    result: dict[str, Any] = dict(params)
    if "user" in result:
        try:
            result["user"] = _json.loads(result["user"])
        except Exception:
            raise UnauthorizedException("Malformed user field in initData")

    return result
