"""Subscriptions API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.api.deps import get_current_user
from app.config.plans import PLANS, get_plan
from app.models.user import UserModel
from app.schemas.subscription import SubscriptionResponse, AllPlansResponse, PlanResponse
from app.services import subscription_service
from app.services import telegram_bot_service
from app.services import channel_service
from app.config.settings import settings
import secrets
from pydantic import BaseModel

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(current_user: UserModel = Depends(get_current_user)):
    sub = await subscription_service.get_subscription(str(current_user.id))
    plan = get_plan(sub.plan_id)
    return SubscriptionResponse(
        plan_id=sub.plan_id,
        plan_name=plan.name,
        status=sub.status,
        max_channels=plan.max_channels,
        posts_per_channel=plan.posts_per_channel,
        max_post_characters=plan.max_post_characters,
        price_stars=plan.price_stars,
        price_label=plan.price_label,
        features=plan.features,
        renews_at=sub.renews_at,
        expires_at=sub.expires_at,
    )


@router.get("/plans", response_model=AllPlansResponse)
async def get_all_plans(current_user: UserModel = Depends(get_current_user)):
    sub = await subscription_service.get_subscription(str(current_user.id))
    plans = [
        PlanResponse(
            id=p.id,
            name=p.name,
            max_channels=p.max_channels,
            posts_per_channel=p.posts_per_channel,
            max_post_characters=p.max_post_characters,
            price_stars=p.price_stars,
            price_label=p.price_label,
            features=p.features,
            is_current=(p.id == sub.plan_id),
        )
        for p in PLANS.values()
    ]
    return AllPlansResponse(plans=plans, current_plan_id=sub.plan_id)


class ChangePlanRequest(BaseModel):
    plan_id: str
    stars_invoice_id: str | None = None


class UsageCreditRequest(BaseModel):
    channel_id: str
    usage_type: str


@router.post("/invoice")
async def change_plan(
    body: ChangePlanRequest,
    current_user: UserModel = Depends(get_current_user),
):
    """Create a server-owned recurring Stars invoice for a paid plan."""
    plan = PLANS.get(body.plan_id)
    if not plan or plan.price_stars <= 0:
        raise HTTPException(status_code=400, detail="Choose a paid plan")
    payload = f"automata:subscription:{current_user.telegram_id}:{body.plan_id}:{secrets.token_urlsafe(12)}"
    await subscription_service.create_pending_payment(
        str(current_user.id), current_user.telegram_id, body.plan_id, payload
    )
    invoice_link = await telegram_bot_service.create_stars_invoice_link(
        f"Automata TG {plan.name}",
        f"30-day {plan.name} subscription for Automata TG",
        payload,
        plan.price_stars,
    )
    return {"invoice_link": invoice_link, "plan_id": body.plan_id}


@router.post("/usage-credit-invoice")
async def create_usage_credit_invoice(
    body: UsageCreditRequest,
    current_user: UserModel = Depends(get_current_user),
):
    if body.usage_type not in {"test_generation", "style_analysis"}:
        raise HTTPException(status_code=400, detail="Choose a valid onboarding allowance")
    await channel_service.get_channel(body.channel_id, str(current_user.id))
    payload = f"automata:usage:{current_user.telegram_id}:{body.usage_type}:{body.channel_id}:{secrets.token_urlsafe(12)}"
    await subscription_service.create_pending_usage_payment(
        str(current_user.id), current_user.telegram_id, body.channel_id,
        body.usage_type, payload, settings.usage_credit_pack_price_stars,
    )
    invoice_link = await telegram_bot_service.create_stars_invoice_link(
        "Automata TG AI credits",
        f"{settings.usage_credit_pack_size} extra {body.usage_type.replace('_', ' ')} credits",
        payload,
        settings.usage_credit_pack_price_stars,
        subscription_period=None,
    )
    return {
        "invoice_link": invoice_link,
        "usage_type": body.usage_type,
        "credits": settings.usage_credit_pack_size,
    }


@router.post("/webhook")
async def subscription_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    """Receive Telegram's verified successful_payment update."""
    if settings.telegram_webhook_secret and not secrets.compare_digest(
        x_telegram_bot_api_secret_token or "", settings.telegram_webhook_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    update = await request.json()
    pre_checkout = update.get("pre_checkout_query")
    if pre_checkout:
        payload = pre_checkout.get("invoice_payload", "")
        is_automata_payment = payload.startswith(("automata:subscription:", "automata:usage:"))
        await telegram_bot_service.answer_pre_checkout_query(
            pre_checkout["id"],
            is_automata_payment,
            None if is_automata_payment else "This invoice is no longer valid.",
        )
        return {"ok": True}
    payment = update.get("message", {}).get("successful_payment")
    telegram_user_id = update.get("message", {}).get("from", {}).get("id")
    if not payment or not telegram_user_id:
        return {"ok": True}
    payment_payload = payment["invoice_payload"]
    if payment_payload.startswith("automata:usage:"):
        completed = await subscription_service.complete_usage_payment(
            payment_payload, telegram_user_id, payment["telegram_payment_charge_id"],
            payment["total_amount"], settings.usage_credit_pack_size,
        )
    else:
        completed = await subscription_service.complete_payment(
            payment_payload, telegram_user_id,
            payment["telegram_payment_charge_id"], payment["total_amount"],
        )
    if not completed:
        raise HTTPException(status_code=400, detail="Unknown or already processed payment")
    return {"ok": True}


@router.post("/change-plan", response_model=SubscriptionResponse)
async def change_plan_legacy(
    body: ChangePlanRequest,
    current_user: UserModel = Depends(get_current_user),
):
    raise HTTPException(status_code=410, detail="Use the Stars invoice flow")


def _subscription_response(sub):
    plan = get_plan(sub.plan_id)
    return SubscriptionResponse(
        plan_id=sub.plan_id,
        plan_name=plan.name,
        status=sub.status,
        max_channels=plan.max_channels,
        posts_per_channel=plan.posts_per_channel,
        max_post_characters=plan.max_post_characters,
        price_stars=plan.price_stars,
        price_label=plan.price_label,
        features=plan.features,
        renews_at=sub.renews_at,
        expires_at=sub.expires_at,
    )
