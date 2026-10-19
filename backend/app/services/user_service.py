"""
User service — create/find Telegram users, update profile.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from app.db.mongo import get_db
from app.models.user import UserModel


async def get_or_create_user(telegram_user: dict[str, Any]) -> UserModel:
    """
    Find existing user by telegram_id, or create a new one.
    Updates profile fields (name, username, photo_url) on each login.
    """
    db = get_db()
    telegram_id = int(telegram_user["id"])
    now = datetime.now(timezone.utc)

    update_fields = {
        "first_name": telegram_user.get("first_name", ""),
        "last_name": telegram_user.get("last_name"),
        "username": telegram_user.get("username"),
        "photo_url": telegram_user.get("photo_url"),
        "language_code": telegram_user.get("language_code", "en"),
        "updated_at": now,
    }

    doc = await db.users.find_one_and_update(
        {"telegram_id": telegram_id},
        {
            "$set": update_fields,
            "$setOnInsert": {
                "telegram_id": telegram_id,
                "created_at": now,
            },
        },
        upsert=True,
        return_document=True,
    )

    return _doc_to_model(doc)


async def get_user_by_telegram_id(telegram_id: int) -> Optional[UserModel]:
    db = get_db()
    doc = await db.users.find_one({"telegram_id": telegram_id})
    return _doc_to_model(doc) if doc else None


async def get_user_by_id(user_id: str) -> Optional[UserModel]:
    from bson import ObjectId
    db = get_db()
    doc = await db.users.find_one({"_id": ObjectId(user_id)})
    return _doc_to_model(doc) if doc else None


async def update_user_language(user_id: str, language_code: str) -> Optional[UserModel]:
    from bson import ObjectId
    db = get_db()
    doc = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"language_code": language_code, "updated_at": datetime.now(timezone.utc)}},
        return_document=True,
    )
    return _doc_to_model(doc) if doc else None


def _doc_to_model(doc: dict) -> UserModel:
    doc["_id"] = str(doc["_id"])
    return UserModel(**doc)
