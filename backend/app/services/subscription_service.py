"""
Subscription service — read and update user subscription/plan.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from bson import ObjectId

from app.config.plans import get_plan, PLANS, DEFAULT_PLAN_ID, Plan
from app.db.mongo import get_db
from app.models.subscription import SubscriptionModel, SubscriptionStatus


async def get_subscription(user_id: str) -> SubscriptionModel:
    """
    Return the user's subscription. Creates a free plan record if none exists.
    """
    db = get_db()
    now = datetime.now(timezone.utc)

    doc = await db.subscriptions.find_one_and_update(
        {"user_id": user_id},
        {
            "$setOnInsert": {
                "user_id": user_id,
                "plan_id": DEFAULT_PLAN_ID,
                "status": SubscriptionStatus.ACTIVE,
                "stars_amount": 0,
                "started_at": now,
                "created_at": now,
                "updated_at": now,
            }
        },
        upsert=True,
        return_document=True,
    )
    return _doc_to_model(doc)


async def get_user_plan(user_id: str) -> Plan:
    sub = await get_subscription(user_id)
    return get_plan(sub.plan_id)


async def change_plan(user_id: str, new_plan_id: str) -> SubscriptionModel:
    """Update user's plan (called after successful Stars payment)."""
    if new_plan_id not in PLANS:
        raise ValueError(f"Unknown plan: {new_plan_id}")
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = await db.subscriptions.find_one_and_update(
        {"user_id": user_id},
        {
            "$set": {
                "plan_id": new_plan_id,
                "status": SubscriptionStatus.ACTIVE,
                "updated_at": now,
            }
        },
        return_document=True,
        upsert=True,
    )
    return _doc_to_model(doc)


async def create_pending_payment(
    user_id: str,
    telegram_id: int,
    plan_id: str,
    payload: str,
) -> None:
    if plan_id not in PLANS or PLANS[plan_id].price_stars <= 0:
        raise ValueError("Only paid plans can be purchased")
    now = datetime.now(timezone.utc)
    await get_db().subscription_payments.update_one(
        {"payload": payload},
        {"$set": {
            "user_id": user_id,
            "telegram_id": telegram_id,
            "plan_id": plan_id,
            "amount": PLANS[plan_id].price_stars,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
        }},
        upsert=True,
    )


async def complete_payment(
    payload: str,
    telegram_id: int,
    charge_id: str,
    amount: int,
) -> bool:
    """Apply one verified Telegram payment exactly once."""
    db = get_db()
    payment = await db.subscription_payments.find_one_and_update(
        {
            "payload": payload,
            "telegram_id": telegram_id,
            "status": "pending",
            "amount": amount,
        },
        {"$set": {
            "status": "paid",
            "telegram_payment_charge_id": charge_id,
            "paid_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }},
        return_document=True,
    )
    if not payment:
        return False

    plan_id = payment["plan_id"]
    now = datetime.now(timezone.utc)
    subscription = await db.subscriptions.find_one({"user_id": payment["user_id"]})
    started_at = subscription.get("started_at", now) if subscription else now
    doc = await db.subscriptions.find_one_and_update(
        {"user_id": payment["user_id"]},
        {"$set": {
            "plan_id": plan_id,
            "status": SubscriptionStatus.ACTIVE,
            "stars_invoice_id": charge_id,
            "stars_amount": amount,
            "started_at": started_at,
            "renews_at": now + timedelta(days=30),
            "expires_at": now + timedelta(days=30),
            "updated_at": now,
        }, "$setOnInsert": {"user_id": payment["user_id"], "created_at": now}},
        upsert=True,
        return_document=True,
    )
    return bool(doc)


async def create_pending_usage_payment(
    user_id: str,
    telegram_id: int,
    channel_id: str,
    usage_type: str,
    payload: str,
    amount: int,
) -> None:
    now = datetime.now(timezone.utc)
    await get_db().usage_payments.update_one(
        {"payload": payload},
        {"$set": {
            "user_id": user_id,
            "telegram_id": telegram_id,
            "channel_id": channel_id,
            "usage_type": usage_type,
            "amount": amount,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
        }},
        upsert=True,
    )


async def complete_usage_payment(
    payload: str,
    telegram_id: int,
    charge_id: str,
    amount: int,
    credits: int,
) -> bool:
    """Verify and apply a one-time onboarding credit purchase exactly once."""
    payment = await get_db().usage_payments.find_one_and_update(
        {
            "payload": payload,
            "telegram_id": telegram_id,
            "status": "pending",
            "amount": amount,
        },
        {"$set": {
            "status": "paid",
            "telegram_payment_charge_id": charge_id,
            "paid_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }},
        return_document=True,
    )
    if not payment:
        return False

    from app.services import usage_service

    bonus_field = {
        "test_generation": "test_generation_bonus",
        "style_analysis": "style_analysis_bonus",
    }.get(payment["usage_type"])
    if not bonus_field:
        return False
    await usage_service.add_onboarding_credits(
        payment["user_id"], payment["channel_id"], bonus_field, credits
    )
    return True


def _doc_to_model(doc: dict) -> SubscriptionModel:
    doc["_id"] = str(doc["_id"])
    return SubscriptionModel(**doc)
