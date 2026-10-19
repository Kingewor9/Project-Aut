"""
Telegram Bot API service — send messages, publish content, send tutorials.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from app.config.settings import settings
from app.services.ai.base import PollPayload

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot"
TELEGRAM_FILE_BASE = "https://api.telegram.org/file/bot"


async def _call(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Make an async call to the Telegram Bot API."""
    url = f"{TELEGRAM_API_BASE}{settings.telegram_bot_token}/{method}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload)
        data = resp.json()
        if not data.get("ok"):
            logger.error(f"Telegram API error ({method}): {data}")
        return data


async def send_message(
    chat_id: int | str,
    text: str,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
) -> dict[str, Any]:
    return await _call("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    })


async def create_stars_invoice_link(
    title: str,
    description: str,
    payload: str,
    amount: int,
    subscription_period: int | None = None,
) -> str:
    """Create a recurring 30-day Telegram Stars invoice link."""
    invoice: dict[str, Any] = {
        "title": title,
        "description": description,
        "payload": payload,
        "provider_token": "",
        "currency": "XTR",
        "prices": [{"label": title, "amount": amount}],
    }
    if subscription_period is not None:
        invoice["subscription_period"] = subscription_period
    result = await _call("createInvoiceLink", invoice)
    if not result.get("ok") or not result.get("result"):
        raise RuntimeError("Telegram could not create the payment invoice")
    return result["result"]


async def answer_pre_checkout_query(query_id: str, ok: bool, error_message: str | None = None) -> bool:
    payload: dict[str, Any] = {"pre_checkout_query_id": query_id, "ok": ok}
    if error_message:
        payload["error_message"] = error_message
    result = await _call("answerPreCheckoutQuery", payload)
    return bool(result.get("ok"))


async def send_tutorial(user_telegram_id: int) -> None:
    """Send the Automata TG how-to tutorial message to a user."""
    text = (
        "👋 <b>Welcome to Automata TG!</b>\n\n"
        "Here's how to get started:\n\n"
        "1️⃣ Tap <b>Channels</b> and add your first Telegram channel\n"
        "2️⃣ Configure your Channel Brain — teach the AI your channel's identity\n"
        "3️⃣ Set your publishing schedule\n"
        "4️⃣ Let Automata TG generate and publish content for you!\n\n"
        "Need help? Contact @automata_support"
    )
    await send_message(user_telegram_id, text)


async def publish_to_channel(
    channel_id: str,
    text: str,
    parse_mode: str = "HTML",
    poll: PollPayload | None = None,
) -> dict[str, Any]:
    """Publish AI-generated text or a structured poll to a Telegram channel."""
    if poll is not None:
        payload: dict[str, Any] = {
            "chat_id": channel_id,
            "question": poll.question,
            "options": poll.options,
            "is_anonymous": poll.is_anonymous,
            "type": poll.poll_type,
            "allows_multiple_answers": poll.allows_multiple_answers,
        }
        if poll.poll_type == "quiz":
            payload["correct_option_id"] = poll.correct_option_id
            if poll.explanation:
                payload["explanation"] = poll.explanation
        return await _call("sendPoll", payload)
    return await _call("sendMessage", {
        "chat_id": channel_id,
        "text": text,
        "parse_mode": parse_mode,
    })


async def get_chat(channel_id: str) -> Optional[dict[str, Any]]:
    """Fetch channel info from Telegram."""
    result = await _call("getChat", {"chat_id": channel_id})
    if result.get("ok"):
        return result.get("result")
    return None


async def get_file(file_id: str) -> Optional[str]:
    """Resolve a Telegram file ID to its server-side file path."""
    result = await _call("getFile", {"file_id": file_id})
    if result.get("ok"):
        return result.get("result", {}).get("file_path")
    return None


async def download_file(file_path: str) -> tuple[bytes, str] | None:
    """Download a Telegram file without exposing the bot token to clients."""
    url = f"{TELEGRAM_FILE_BASE}{settings.telegram_bot_token}/{file_path}"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url)
        if response.is_success:
            return response.content, response.headers.get("content-type", "image/jpeg")
    return None


async def check_bot_admin(channel_id: str) -> bool:
    """Check if the bot is an admin in the given channel."""
    from app.config.settings import settings

    # Get chat member info for the bot
    bot_info = await _call("getMe", {})
    if not bot_info.get("ok"):
        return False

    bot_id = bot_info["result"]["id"]
    result = await _call("getChatMember", {
        "chat_id": channel_id,
        "user_id": bot_id,
    })

    if not result.get("ok"):
        return False

    status = result["result"].get("status", "")
    return status in ("administrator", "creator")
