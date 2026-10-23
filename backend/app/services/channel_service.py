"""
Channel service — CRUD with ownership enforcement.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from app.config.plans import get_plan
from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException, PlanLimitException
from app.db.mongo import get_db
from app.models.channel import ChannelModel
from app.schemas.channel import ChannelCreateRequest, ChannelUpdateRequest
from app.schemas.channel import (
    ActivationRequest,
    BrainOnboardingRequest,
    CTAOnboardingRequest,
    IdentityOnboardingRequest,
)
from app.services import subscription_service, usage_service
from app.services import telegram_bot_service


async def list_channels(user_id: str) -> list[ChannelModel]:
    db = get_db()
    cursor = db.channels.find({"user_id": user_id}).sort("created_at", 1)
    channels = []
    async for doc in cursor:
        channels.append(_doc_to_model(doc))
    return channels


async def get_channel(channel_id: str, user_id: str) -> ChannelModel:
    """Get a channel and enforce ownership."""
    db = get_db()
    doc = await db.channels.find_one({"_id": ObjectId(channel_id)})
    if not doc:
        raise NotFoundException(f"Channel {channel_id} not found")
    model = _doc_to_model(doc)
    if model.user_id != user_id:
        raise ForbiddenException("You do not own this channel")
    return model


async def create_channel(user_id: str, data: ChannelCreateRequest) -> ChannelModel:
    """Create a new channel after validating plan limits."""
    plan = await subscription_service.get_user_plan(user_id)
    existing = await list_channels(user_id)

    if len(existing) >= plan.max_channels:
        raise PlanLimitException(
            f"Your {plan.name} plan allows up to {plan.max_channels} channel(s). "
            "Please upgrade to add more."
        )

    chat = await telegram_bot_service.get_chat(data.telegram_channel_id.strip())
    if not chat or chat.get("type") != "channel":
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Telegram channel not found")

    telegram_channel_id = str(chat["id"])
    photo = chat.get("photo") or {}
    file_id = photo.get("big_file_id") or photo.get("small_file_id")
    photo_url = f"/api/v1/channels/photo/{file_id}" if file_id else None

    db = get_db()
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "telegram_channel_id": telegram_channel_id,
        "username": chat.get("username"),
        "name": chat.get("title", "Untitled channel"),
        "photo_url": photo_url,
        "brain": {},
        "schedule": {},
        "publish_mode": "approval",
        "automation_status": "inactive",
        "is_bot_admin": False,
        "is_active": False,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.channels.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    await usage_service.ensure_usage_record(
        user_id,
        str(result.inserted_id),
        (await subscription_service.get_user_plan(user_id)).posts_per_channel,
    )
    return _doc_to_model(doc)


async def update_channel(
    channel_id: str,
    user_id: str,
    data: ChannelUpdateRequest,
) -> ChannelModel:
    """Update channel configuration (ownership enforced)."""
    await get_channel(channel_id, user_id)  # raises if not found/owned

    db = get_db()
    update: dict = {"updated_at": datetime.now(timezone.utc)}

    if data.name is not None:
        update["name"] = data.name
    if data.photo_url is not None:
        update["photo_url"] = data.photo_url
    if data.brain is not None:
        update["brain"] = data.brain.model_dump()
    if data.schedule is not None:
        update["schedule"] = data.schedule.model_dump()
    if data.publish_mode is not None:
        update["publish_mode"] = data.publish_mode
    if data.automation_status is not None:
        update["automation_status"] = data.automation_status

    doc = await db.channels.find_one_and_update(
        {"_id": ObjectId(channel_id)},
        {"$set": update},
        return_document=True,
    )
    return _doc_to_model(doc)


async def save_identity(
    channel_id: str, user_id: str, data: IdentityOnboardingRequest
) -> ChannelModel:
    channel = await get_channel(channel_id, user_id)
    brain = channel.brain.model_dump()
    brain.update({
        "niches": data.niches,
        "topics": data.topics,
        "audience": data.audience.model_dump(),
        "conversion_goals": data.conversion_goals,
        "rules": data.rules.model_dump(),
        "frequency": data.frequency,
    })
    db = get_db()
    doc = await db.channels.find_one_and_update(
        {"_id": ObjectId(channel_id), "user_id": user_id},
        {"$set": {
            "brain": brain,
            "schedule": data.schedule.model_dump(),
            "updated_at": datetime.now(timezone.utc),
        }},
        return_document=True,
    )
    return _doc_to_model(doc)


async def save_brain(
    channel_id: str, user_id: str, data: BrainOnboardingRequest
) -> ChannelModel:
    channel = await get_channel(channel_id, user_id)
    brain = channel.brain.model_dump()
    brain.update({
        "writing_dna": data.writing_dna.model_dump(),
        "content_types": data.content_types,
    })
    db = get_db()
    doc = await db.channels.find_one_and_update(
        {"_id": ObjectId(channel_id), "user_id": user_id},
        {"$set": {"brain": brain, "updated_at": datetime.now(timezone.utc)}},
        return_document=True,
    )
    return _doc_to_model(doc)


async def save_cta(
    channel_id: str, user_id: str, data: CTAOnboardingRequest
) -> ChannelModel:
    channel = await get_channel(channel_id, user_id)
    brain = channel.brain.model_dump()
    brain.update({
        "cta_enabled": data.enabled,
        "products": [item.model_dump() for item in data.products],
        "ctas": [item.model_dump() for item in data.ctas],
        "promotion_style": data.promotion_style,
        "max_promotions_per_week": data.max_promotions_per_week,
    })
    db = get_db()
    doc = await db.channels.find_one_and_update(
        {"_id": ObjectId(channel_id), "user_id": user_id},
        {"$set": {"brain": brain, "updated_at": datetime.now(timezone.utc)}},
        return_document=True,
    )
    return _doc_to_model(doc)


async def activate_channel(
    channel_id: str, user_id: str, data: ActivationRequest
) -> ChannelModel:
    channel = await get_channel(channel_id, user_id)
    brain = channel.brain
    if not brain.niches or not brain.topics or not brain.audience.description:
        raise ConflictException("Complete channel identity before activating AI")
    if (
        not brain.writing_dna.tone
        and not any(post.strip() for post in brain.writing_dna.sample_posts)
        and not brain.writing_dna.sample_polls
    ):
        raise ConflictException("Teach your AI a writing style before activating")

    is_bot_admin = await telegram_bot_service.check_bot_admin(channel.telegram_channel_id)
    if not is_bot_admin:
        raise ConflictException(
            "Add Automata TG Bot as a channel administrator with permission to post messages"
        )

    db = get_db()
    doc = await db.channels.find_one_and_update(
        {"_id": ObjectId(channel_id), "user_id": user_id},
        {"$set": {
            "publish_mode": data.publish_mode,
            "automation_status": "active",
            "is_bot_admin": True,
            "is_active": True,
            "updated_at": datetime.now(timezone.utc),
        }},
        return_document=True,
    )
    return _doc_to_model(doc)


async def delete_channel(channel_id: str, user_id: str) -> None:
    await get_channel(channel_id, user_id)
    db = get_db()
    await db.channels.delete_one({"_id": ObjectId(channel_id)})


def _doc_to_model(doc: dict) -> ChannelModel:
    doc["_id"] = str(doc["_id"])
    return ChannelModel(**doc)
