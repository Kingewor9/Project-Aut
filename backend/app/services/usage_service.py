"""
Usage service — track per-channel monthly AI post generations.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.core.exceptions import UsageLimitException
from app.db.mongo import get_db
from app.models.usage import UsageModel


def _current_month_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


async def get_usage(channel_id: str, month_key: Optional[str] = None) -> UsageModel:
    """Return usage record for a channel in the given month (default: current)."""
    if month_key is None:
        month_key = _current_month_key()
    db = get_db()
    doc = await db.usage.find_one({"channel_id": channel_id, "month_key": month_key})
    if doc is None:
        # Return a zero-usage model without persisting
        return UsageModel(
            user_id="",
            channel_id=channel_id,
            month_key=month_key,
            posts_generated=0,
            posts_published=0,
            posts_allowance=0,
        )
    return _doc_to_model(doc)


async def get_usage_for_channels(channel_ids: list[str]) -> dict[str, UsageModel]:
    """Batch-fetch current-month usage for multiple channels."""
    if not channel_ids:
        return {}
    month_key = _current_month_key()
    db = get_db()
    cursor = db.usage.find({"channel_id": {"$in": channel_ids}, "month_key": month_key})
    result: dict[str, UsageModel] = {}
    async for doc in cursor:
        model = _doc_to_model(doc)
        result[model.channel_id] = model
    return result


async def ensure_usage_record(
    user_id: str, channel_id: str, allowance: int
) -> UsageModel:
    """Create or refresh the current month's usage snapshot for a channel."""
    month_key = _current_month_key()
    now = datetime.now(timezone.utc)
    db = get_db()
    doc = await db.usage.find_one_and_update(
        {"channel_id": channel_id, "month_key": month_key},
        {
            "$set": {
                "user_id": user_id,
                "posts_allowance": allowance,
                "updated_at": now,
            },
            "$setOnInsert": {
                "channel_id": channel_id,
                "month_key": month_key,
                "posts_generated": 0,
                "posts_published": 0,
                "test_generations": 0,
                "test_generation_bonus": 0,
                "style_analyses": 0,
                "style_analysis_bonus": 0,
                "created_at": now,
            },
        },
        upsert=True,
        return_document=True,
    )
    return _doc_to_model(doc)


async def increment_generated(
    user_id: str,
    channel_id: str,
    allowance: int,
    count: int = 1,
) -> UsageModel:
    """Atomically consume generation quota and increment posts_generated."""
    month_key = _current_month_key()
    now = datetime.now(timezone.utc)
    db = get_db()
    doc = await db.usage.find_one_and_update(
        {
            "channel_id": channel_id,
            "month_key": month_key,
            "$expr": {
                "$lte": [
                    {"$add": ["$posts_generated", count]},
                    allowance,
                ]
            },
        },
        {
            "$inc": {"posts_generated": count},
            "$set": {
                "user_id": user_id,
                "posts_allowance": allowance,
                "last_generated_at": now,
                "updated_at": now,
            },
            "$setOnInsert": {
                "channel_id": channel_id,
                "month_key": month_key,
                "posts_published": 0,
                "created_at": now,
            },
        },
        upsert=False,
        return_document=True,
    )
    if doc is None:
        current = await get_usage(channel_id, month_key)
        if current.posts_generated >= allowance:
            raise UsageLimitException(
                "This channel has reached its monthly AI post allowance. "
                "Generation will resume when the next billing month begins."
            )
        raise UsageLimitException("The requested generation would exceed the monthly AI post allowance.")
    return _doc_to_model(doc)


async def increment_published(channel_id: str) -> UsageModel:
    """Increment posts_published count (called after Telegram publish)."""
    month_key = _current_month_key()
    now = datetime.now(timezone.utc)
    db = get_db()
    doc = await db.usage.find_one_and_update(
        {"channel_id": channel_id, "month_key": month_key},
        {
            "$inc": {"posts_published": 1},
            "$set": {"updated_at": now},
        },
        return_document=True,
    )
    if doc is None:
        raise ValueError(f"No usage record for channel {channel_id} in {month_key}")
    return _doc_to_model(doc)


async def consume_onboarding_credit(
    user_id: str,
    channel_id: str,
    used_field: str,
    bonus_field: str,
    allowance: int,
) -> UsageModel:
    """Consume one credit from one independent onboarding allowance."""
    month_key = _current_month_key()
    now = datetime.now(timezone.utc)
    db = get_db()
    doc = await db.usage.find_one_and_update(
        {
            "channel_id": channel_id,
            "month_key": month_key,
            "$expr": {"$lt": [
                {"$ifNull": [f"${used_field}", 0]},
                {"$add": [allowance, {"$ifNull": [f"${bonus_field}", 0]}]},
            ]},
        },
        {
            "$inc": {used_field: 1},
            "$set": {"user_id": user_id, "updated_at": now},
        },
        upsert=False,
        return_document=True,
    )
    if doc is None:
        raise ValueError("Onboarding allowance exhausted")
    return _doc_to_model(doc)


async def add_onboarding_credits(
    user_id: str, channel_id: str, bonus_field: str, credits: int
) -> UsageModel:
    """Add purchased credits to one onboarding allowance."""
    month_key = _current_month_key()
    now = datetime.now(timezone.utc)
    doc = await get_db().usage.find_one_and_update(
        {"channel_id": channel_id, "month_key": month_key},
        {
            "$inc": {bonus_field: credits},
            "$set": {"user_id": user_id, "updated_at": now},
            "$setOnInsert": {
                "channel_id": channel_id,
                "month_key": month_key,
                "posts_generated": 0,
                "posts_published": 0,
                "posts_allowance": 0,
                "test_generations": 0,
                "style_analyses": 0,
                "created_at": now,
            },
        },
        upsert=True,
        return_document=True,
    )
    return _doc_to_model(doc)


def _doc_to_model(doc: dict) -> UsageModel:
    doc["_id"] = str(doc["_id"])
    return UsageModel(**doc)
