"""
Create MongoDB indexes on startup to ensure query performance and uniqueness.
"""
from __future__ import annotations

import logging

from pymongo import ASCENDING, DESCENDING, IndexModel

from app.db.mongo import get_db

logger = logging.getLogger(__name__)


async def create_indexes() -> None:
    db = get_db()

    # ── users ──────────────────────────────────────────────────────────────
    await db.users.create_indexes([
        IndexModel([("telegram_id", ASCENDING)], unique=True),
        IndexModel([("username", ASCENDING)]),
    ])

    # ── channels ───────────────────────────────────────────────────────────
    await db.channels.create_indexes([
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("telegram_channel_id", ASCENDING)]),
        IndexModel([("user_id", ASCENDING), ("telegram_channel_id", ASCENDING)], unique=True),
    ])

    # ── subscriptions ──────────────────────────────────────────────────────
    await db.subscriptions.create_indexes([
        IndexModel([("user_id", ASCENDING)], unique=True),
        IndexModel([("plan_id", ASCENDING)]),
    ])

    # ── usage ──────────────────────────────────────────────────────────────
    await db.usage.create_indexes([
        IndexModel([("channel_id", ASCENDING), ("month_key", ASCENDING)], unique=True),
        IndexModel([("user_id", ASCENDING)]),
    ])

    # Generation feedback is tenant-scoped for later AI/style improvements.
    await db.generation_feedback.create_indexes([
        IndexModel([("channel_id", ASCENDING), ("created_at", DESCENDING)]),
        IndexModel([("user_id", ASCENDING)]),
    ])

    # Scheduled slots are unique so multiple scheduler workers cannot create
    # duplicate daily posts for the same channel and posting time.
    await db.scheduled_posts.create_indexes([
        IndexModel([("channel_id", ASCENDING), ("scheduled_for", ASCENDING)], unique=True),
        IndexModel([("user_id", ASCENDING), ("status", ASCENDING), ("scheduled_for", ASCENDING)]),
    ])

    logger.info("MongoDB indexes created/verified.")
