"""Scheduled AI generation, approval, and Telegram publishing."""
from __future__ import annotations

import html
import logging
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.config.plans import Plan
from app.config.settings import settings
from app.db.mongo import get_db
from app.models.channel import ChannelModel
from app.services import subscription_service, telegram_bot_service, usage_service
from app.services.ai.base import GenerationRequest, GenerationResult, PollPayload
from app.services.ai.prompt_builder import writing_dna_instructions

logger = logging.getLogger(__name__)


def due_slot(channel: ChannelModel, now: datetime) -> datetime | None:
    """Return this minute's scheduled slot in UTC, if the channel is due."""
    schedule = channel.schedule
    try:
        local_now = now.astimezone(ZoneInfo(schedule.timezone))
    except (ZoneInfoNotFoundError, ValueError):
        logger.error("Invalid timezone %r for channel %s", schedule.timezone, channel.id)
        return None

    weekday = local_now.strftime("%a").lower()
    if weekday not in {day.lower() for day in schedule.active_days}:
        return None

    times = schedule.daily_times.get(weekday) or schedule.posting_times
    if local_now.strftime("%H:%M") not in times:
        return None

    return local_now.replace(second=0, microsecond=0).astimezone(timezone.utc)


def build_generation_request(channel: ChannelModel, plan: Plan) -> GenerationRequest:
    """Build the same channel-aware generation context for every scheduled post."""
    brain = channel.brain
    dna = brain.writing_dna
    formats = brain.content_types or brain.post_formats
    if dna.mode == "samples" and dna.content_style == "quiz_polls":
        formats = ["Poll"]
    elif dna.mode == "samples":
        formats = [post_format for post_format in formats if post_format.strip().lower() != "poll"]
        if not formats:
            formats = ["Educational"]

    rules = "\n".join([
        *(f"Always: {item}" for item in brain.rules.always_do),
        *(f"Never: {item}" for item in brain.rules.never_do),
        *(f"Forbidden topic: {item}" for item in brain.rules.forbidden_topics),
        *(f"Forbidden word: {item}" for item in brain.rules.forbidden_words),
        *([brain.rules.custom_rules] if brain.rules.custom_rules else []),
    ]) or brain.rules_and_restrictions or "No specific restrictions."

    return GenerationRequest(
        channel_name=channel.name,
        niche=", ".join(brain.niches) or brain.niche or "general",
        topics=brain.topics or ["general topics related to the channel"],
        audience=brain.audience.description or brain.audience_description or "the channel audience",
        writing_personality=writing_dna_instructions(dna, brain.writing_personality),
        post_formats=formats,
        content_strategy=brain.content_strategy or "Create a valuable, engaging scheduled channel post.",
        products_and_offers="; ".join(product.name for product in brain.products) or brain.products_and_offers or "None",
        cta_library=[
            cta.instruction or cta.destination_url or cta.type
            for cta in brain.ctas
        ] or brain.cta_library,
        rules=rules,
        goals=", ".join(brain.conversion_goals) or brain.goals or "Engage and grow the audience",
        max_post_characters=plan.max_post_characters,
        extra_instructions=dna.advanced_instructions or "",
    )


async def run_due_posts(now: datetime | None = None) -> None:
    """Generate and publish content for each active channel whose slot is due."""
    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    db = get_db()
    unsent_cursor = db.scheduled_posts.find({
        "status": "pending",
        "notification_sent": {"$ne": True},
        "notification_attempts": {"$lt": 10},
    })
    async for pending_post in unsent_cursor:
        await notify_approval(pending_post)

    cursor = db.channels.find({
        "is_active": True,
        "automation_status": "active",
    })
    async for doc in cursor:
        try:
            channel = ChannelModel(**doc)
            scheduled_for = due_slot(channel, current_time)
            if scheduled_for is not None:
                await process_scheduled_slot(channel, scheduled_for)
        except Exception:
            logger.exception("Could not process scheduled channel %s", doc.get("_id"))


async def process_scheduled_slot(channel: ChannelModel, scheduled_for: datetime) -> None:
    """Create a scheduled post once; retry unsent approval notifications."""
    db = get_db()
    scheduled_for = scheduled_for.astimezone(timezone.utc)
    slot_filter = {
        "channel_id": str(channel.id),
        "scheduled_for": scheduled_for,
    }
    now = datetime.now(timezone.utc)
    post = await db.scheduled_posts.find_one(slot_filter)
    if post:
        if post.get("status") == "pending" and not post.get("notification_sent"):
            await notify_approval(post)
        return

    post = {
        **slot_filter,
        "user_id": channel.user_id,
        "channel_name": channel.name,
        "telegram_channel_id": channel.telegram_channel_id,
        "publish_mode": channel.publish_mode,
        "status": "generating",
        "notification_sent": False,
        "notification_attempts": 0,
        "created_at": now,
        "updated_at": now,
    }
    try:
        inserted = await db.scheduled_posts.insert_one(post)
        post["_id"] = inserted.inserted_id
    except DuplicateKeyError:
        return

    try:
        plan = await subscription_service.get_user_plan(channel.user_id)
        await usage_service.ensure_usage_record(
            channel.user_id, str(channel.id), plan.posts_per_channel
        )
        from app.services.ai.gemini_provider import get_gemini_provider

        result = await get_gemini_provider().generate(build_generation_request(channel, plan))
        await usage_service.increment_generated(
            channel.user_id, str(channel.id), plan.posts_per_channel
        )
        post_fields: dict[str, Any] = {
            "content": result.content,
            "provider": result.provider,
            "model": result.model,
            "status": "pending" if channel.publish_mode == "approval" else "publishing",
            "updated_at": datetime.now(timezone.utc),
        }
        if result.poll is not None:
            post_fields["poll"] = _poll_to_dict(result.poll)
        await db.scheduled_posts.update_one({"_id": post["_id"]}, {"$set": post_fields})
        post.update(post_fields)

        if channel.publish_mode == "approval":
            await notify_approval(post)
            return

        await publish_post(post)
    except Exception as exc:
        logger.exception("Scheduled generation/publishing failed for channel %s", channel.id)
        await db.scheduled_posts.update_one(
            {"_id": post["_id"]},
            {"$set": {
                "status": "failed",
                "error": str(exc)[:500],
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        await notify_scheduling_failure(channel, channel.publish_mode == "auto")


async def notify_approval(post: dict[str, Any]) -> None:
    """Tell the owner a generated post is ready for review in the mini app."""
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(post["user_id"])})
    if not user:
        logger.error("Could not notify owner for scheduled post %s: user is missing", post["_id"])
        await db.scheduled_posts.update_one({"_id": post["_id"]}, {"$inc": {"notification_attempts": 1}})
        return

    name = html.escape(post["channel_name"])
    text = (
        f"📝 <b>A scheduled post is ready for review</b>\n\n"
        f"Channel: <b>{name}</b>\n"
        "Open Automata TG to preview it, then approve or decline."
    )
    reply_markup = None
    if settings.telegram_mini_app_url:
        reply_markup = {
            "inline_keyboard": [[{
                "text": "Review post",
                "web_app": {"url": settings.telegram_mini_app_url},
            }]]
        }
    try:
        result = await telegram_bot_service.send_message(
            user["telegram_id"],
            text,
            reply_markup=reply_markup,
        )
        if not result.get("ok"):
            logger.error(
                "Telegram approval notification failed for post %s: %s",
                post["_id"],
                result.get("description", "unknown error"),
            )
            await db.scheduled_posts.update_one({"_id": post["_id"]}, {"$inc": {"notification_attempts": 1}})
            return
        await db.scheduled_posts.update_one(
            {"_id": post["_id"], "status": "pending"},
            {"$set": {"notification_sent": True, "updated_at": datetime.now(timezone.utc)}},
        )
    except Exception:
        logger.exception("Could not send approval notification for post %s", post["_id"])
        await db.scheduled_posts.update_one({"_id": post["_id"]}, {"$inc": {"notification_attempts": 1}})


async def notify_scheduling_failure(channel: ChannelModel, is_publish_failure: bool) -> None:
    """Tell the owner when a scheduled post could not be completed."""
    try:
        user = await get_db().users.find_one({"_id": ObjectId(channel.user_id)})
        if not user:
            logger.error("Could not notify owner for channel %s: user is missing", channel.id)
            return
        action = "publish" if is_publish_failure else "generate"
        text = (
            f"⚠️ <b>Automata couldn't {action} your scheduled post</b>\n\n"
            f"Channel: <b>{html.escape(channel.name)}</b>\n"
            "Please check your AI configuration, monthly post allowance, and that the bot can post in the channel."
        )
        reply_markup = None
        if settings.telegram_mini_app_url:
            reply_markup = {
                "inline_keyboard": [[{
                    "text": "Open Automata TG",
                    "web_app": {"url": settings.telegram_mini_app_url},
                }]]
            }
        result = await telegram_bot_service.send_message(
            user["telegram_id"],
            text,
            reply_markup=reply_markup,
        )
        if not result.get("ok"):
            logger.error(
                "Scheduled-post failure notification failed for channel %s: %s",
                channel.id,
                result.get("description", "unknown error"),
            )
    except Exception:
        logger.exception("Could not notify owner about scheduled-post failure for channel %s", channel.id)


async def list_pending_posts(user_id: str) -> list[dict[str, Any]]:
    cursor = get_db().scheduled_posts.find({
        "user_id": user_id,
        "status": "pending",
    }).sort("scheduled_for", 1)
    posts = []
    async for post in cursor:
        post["id"] = str(post.pop("_id"))
        posts.append(post)
    return posts


async def decide_post(post_id: str, user_id: str, approve: bool) -> dict[str, Any]:
    """Approve and publish, or decline, a pending post owned by the user."""
    if not ObjectId.is_valid(post_id):
        raise ValueError("Scheduled post not found")
    db = get_db()
    post = await db.scheduled_posts.find_one_and_update(
        {"_id": ObjectId(post_id), "user_id": user_id, "status": "pending"},
        {"$set": {
            "status": "publishing" if approve else "rejected",
            "updated_at": datetime.now(timezone.utc),
        }},
        return_document=True,
    )
    if post is None:
        raise ValueError("This post is no longer awaiting a decision")

    if approve:
        try:
            await publish_post(post)
        except Exception:
            await db.scheduled_posts.update_one(
                {"_id": post["_id"], "status": "publishing"},
                {"$set": {"status": "pending", "updated_at": datetime.now(timezone.utc)}},
            )
            raise
        post["status"] = "published"
    else:
        post["status"] = "rejected"

    post["id"] = str(post.pop("_id"))
    return post


async def publish_post(post: dict[str, Any]) -> None:
    """Publish a post, then record the successful Telegram delivery."""
    poll_data = post.get("poll")
    poll = PollPayload(**poll_data) if poll_data else None
    result = await telegram_bot_service.publish_to_channel(
        post["telegram_channel_id"],
        post.get("content", ""),
        poll=poll,
    )
    if not result.get("ok"):
        raise RuntimeError(f"Telegram rejected the post: {result.get('description', 'unknown error')}")

    now = datetime.now(timezone.utc)
    await get_db().scheduled_posts.update_one(
        {"_id": post["_id"], "status": "publishing"},
        {"$set": {
            "status": "published",
            "published_at": now,
            "telegram_message_id": result.get("result", {}).get("message_id"),
            "updated_at": now,
        }},
    )
    try:
        await usage_service.increment_published(post["channel_id"])
    except Exception:
        logger.exception("Post %s published but usage could not be incremented", post["_id"])


def _poll_to_dict(poll: PollPayload) -> dict[str, Any]:
    return {
        "question": poll.question,
        "options": poll.options,
        "poll_type": poll.poll_type,
        "is_anonymous": poll.is_anonymous,
        "allows_multiple_answers": poll.allows_multiple_answers,
        "correct_option_id": poll.correct_option_id,
        "explanation": poll.explanation,
    }
