"""Channels API router."""
from __future__ import annotations

import logging
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.api.deps import get_current_user
from app.models.user import UserModel
from app.schemas.channel import (
    ChannelCreateRequest,
    ActivationRequest,
    BrainOnboardingRequest,
    CTAOnboardingRequest,
    ChannelResolveRequest,
    ChannelResolveResponse,
    IdentityOnboardingRequest,
    TestGenerationFeedbackRequest,
    TestGenerationRequest,
    TestGenerationResponse,
    StyleAnalysisRequest,
    StyleAnalysisResponse,
    ChannelUpdateRequest,
    ChannelResponse,
    UsageSummary,
)
from app.services import channel_service, usage_service
from app.services import telegram_bot_service
from app.services.ai.base import GenerationRequest
from app.services.ai.prompt_builder import build_style_analysis_prompt
from app.services.subscription_service import get_user_plan
from app.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("", response_model=list[ChannelResponse])
async def list_channels(current_user: UserModel = Depends(get_current_user)):
    """List all channels belonging to the authenticated user, with current usage."""
    user_id = str(current_user.id)
    channels = await channel_service.list_channels(user_id)

    if not channels:
        return []

    # Batch-fetch usage
    channel_ids = [str(c.id) for c in channels]
    usages = await usage_service.get_usage_for_channels(channel_ids)

    responses = []
    for ch in channels:
        ch_id = str(ch.id)
        usage = usages.get(ch_id)
        responses.append(_to_response(ch, usage))
    return responses


@router.post("", response_model=ChannelResponse, status_code=201)
async def create_channel(
    body: ChannelCreateRequest,
    current_user: UserModel = Depends(get_current_user),
):
    user_id = str(current_user.id)
    channel = await channel_service.create_channel(user_id, body)
    return _to_response(channel, None)


@router.post("/resolve", response_model=ChannelResolveResponse)
async def resolve_channel(
    body: ChannelResolveRequest,
    current_user: UserModel = Depends(get_current_user),
):
    """Resolve the channel identity from Telegram for the onboarding preview."""
    del current_user
    channel_id = body.telegram_channel_id.strip()
    if not channel_id:
        raise HTTPException(status_code=422, detail="Enter a channel username or ID")

    chat = await telegram_bot_service.get_chat(channel_id)
    if not chat or chat.get("type") != "channel":
        raise HTTPException(status_code=404, detail="Telegram channel not found")

    photo_url = None
    photo = chat.get("photo") or {}
    file_id = photo.get("big_file_id") or photo.get("small_file_id")
    if file_id:
        photo_url = f"/api/v1/channels/photo/{file_id}"

    return ChannelResolveResponse(
        telegram_channel_id=str(chat["id"]),
        username=chat.get("username"),
        name=chat.get("title", "Untitled channel"),
        photo_url=photo_url,
    )


@router.get("/photo/{file_id}")
async def channel_photo(file_id: str):
    """Proxy a Telegram channel photo so the bot token stays private."""
    file_path = await telegram_bot_service.get_file(file_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Channel photo not found")
    downloaded = await telegram_bot_service.download_file(file_path)
    if not downloaded:
        raise HTTPException(status_code=404, detail="Channel photo not found")
    content, media_type = downloaded
    return Response(content=content, media_type=media_type, headers={"Cache-Control": "public, max-age=3600"})


@router.put("/{channel_id}/onboarding/identity", response_model=ChannelResponse)
async def save_identity(
    channel_id: str,
    body: IdentityOnboardingRequest,
    current_user: UserModel = Depends(get_current_user),
):
    channel = await channel_service.save_identity(channel_id, str(current_user.id), body)
    return _to_response(channel)


@router.put("/{channel_id}/onboarding/brain", response_model=ChannelResponse)
async def save_brain(
    channel_id: str,
    body: BrainOnboardingRequest,
    current_user: UserModel = Depends(get_current_user),
):
    channel = await channel_service.save_brain(channel_id, str(current_user.id), body)
    return _to_response(channel)


@router.post("/{channel_id}/onboarding/analyze-style", response_model=StyleAnalysisResponse)
async def analyze_style(
    channel_id: str,
    body: StyleAnalysisRequest,
    current_user: UserModel = Depends(get_current_user),
):
    channel = await channel_service.get_channel(channel_id, str(current_user.id))
    samples = [sample.strip() for sample in body.sample_posts if sample.strip()]
    if len(samples) < 3:
        raise HTTPException(status_code=422, detail="Add at least 3 non-empty posts for a reliable style analysis")
    if len(samples) > 5:
        samples = samples[:5]

    try:
        from app.services.ai.gemini_provider import get_gemini_provider
        usage = await usage_service.get_usage(channel_id)
        remaining = max(0, settings.style_analysis_allowance - usage.style_analyses + usage.style_analysis_bonus)
        if remaining <= 0:
            raise HTTPException(status_code=429, detail="Your AI analysis allowance is exhausted")
        prompt = build_style_analysis_prompt(channel.name, samples)
        try:
            result = await get_gemini_provider().generate_text(
                prompt,
                max_output_tokens=4096,
                response_mime_type="application/json",
            )
        except Exception:
            logger.warning("Strict JSON style analysis failed; retrying without response MIME type", exc_info=True)
            result = await get_gemini_provider().generate_text(
                prompt,
                max_output_tokens=4096,
            )
    except HTTPException:
        raise
    except ModuleNotFoundError as exc:
        if exc.name == "google.generativeai":
            raise HTTPException(status_code=503, detail="AI provider is not installed on the backend") from exc
        raise
    except Exception as exc:
        logger.exception("Style analysis failed for channel %s", channel_id)
        raise HTTPException(status_code=502, detail="Gemini could not analyze these posts") from exc

    try:
        raw = result.strip()
        if "```" in raw:
            fenced_parts = raw.split("```")
            raw = next((part for part in fenced_parts if "{" in part), raw)
            raw = raw.removeprefix("json").strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("No JSON object in Gemini response")
        payload = json.loads(raw[start:end + 1])
        if not isinstance(payload, dict):
            raise ValueError("Gemini response was not a JSON object")
        for field in ("tone", "personality", "formatting", "sample_posts"):
            if payload.get(field) is None:
                payload[field] = []
        if not isinstance(payload.get("style_analysis"), dict):
            payload["style_analysis"] = {}
        analysis = StyleAnalysisResponse.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Invalid style analysis JSON: %s", exc)
        raise HTTPException(status_code=502, detail="Gemini returned an incomplete style analysis. Please try again.") from exc

    try:
        updated_usage = await usage_service.consume_onboarding_credit(
            str(current_user.id), channel_id, "style_analyses", "style_analysis_bonus", settings.style_analysis_allowance
        )
    except ValueError as exc:
        raise HTTPException(status_code=429, detail="Your AI analysis allowance is exhausted") from exc
    analysis.remaining_analyses = max(0, settings.style_analysis_allowance - updated_usage.style_analyses + updated_usage.style_analysis_bonus)
    analysis.sample_posts = samples
    return analysis


@router.put("/{channel_id}/onboarding/cta", response_model=ChannelResponse)
async def save_cta(
    channel_id: str,
    body: CTAOnboardingRequest,
    current_user: UserModel = Depends(get_current_user),
):
    channel = await channel_service.save_cta(channel_id, str(current_user.id), body)
    return _to_response(channel)


@router.post("/{channel_id}/onboarding/activate", response_model=ChannelResponse)
async def activate_channel(
    channel_id: str,
    body: ActivationRequest,
    current_user: UserModel = Depends(get_current_user),
):
    channel = await channel_service.activate_channel(channel_id, str(current_user.id), body)
    return _to_response(channel)


@router.post("/{channel_id}/onboarding/test-generation", response_model=TestGenerationResponse)
async def test_generation(
    channel_id: str,
    body: TestGenerationRequest,
    current_user: UserModel = Depends(get_current_user),
):
    channel = await channel_service.get_channel(channel_id, str(current_user.id))
    try:
        from app.services.ai.gemini_provider import get_gemini_provider
    except ModuleNotFoundError as exc:
        if exc.name == "google.generativeai":
            raise HTTPException(status_code=503, detail="AI provider is not installed on the backend") from exc
        raise
    usage = await usage_service.get_usage(channel_id)
    remaining = max(0, settings.test_generation_allowance - usage.test_generations + usage.test_generation_bonus)
    if remaining <= 0:
        raise HTTPException(status_code=429, detail="Your onboarding test-generation allowance is exhausted")

    dna = channel.brain.writing_dna
    plan = await get_user_plan(str(current_user.id))
    audience = channel.brain.audience.description or channel.brain.audience_description or "the channel audience"
    writing_personality = _writing_dna_instructions(dna, channel.brain.writing_personality)
    rules = "\n".join(
        [*(f"Always: {item}" for item in channel.brain.rules.always_do), *(f"Never: {item}" for item in channel.brain.rules.never_do)]
    ) or channel.brain.rules_and_restrictions or "No additional rules"
    try:
        result = await get_gemini_provider().generate(GenerationRequest(
            channel_name=channel.name,
            niche=", ".join(channel.brain.niches) or channel.brain.niche or "general",
            topics=[body.topic],
            audience=audience,
            writing_personality=writing_personality,
            post_formats=channel.brain.content_types or channel.brain.post_formats,
            content_strategy=f"Create a {body.content_type} post",
            products_and_offers="; ".join(product.name for product in channel.brain.products) or channel.brain.products_and_offers or "None",
            cta_library=[cta.instruction or cta.destination_url or cta.type for cta in channel.brain.ctas],
            rules=rules,
            goals=", ".join(channel.brain.conversion_goals) or channel.brain.goals or "Engage the audience",
            max_post_characters=plan.max_post_characters,
            extra_instructions=body.context or dna.advanced_instructions or "",
        ))
    except Exception as exc:
        logger.exception("Test generation failed for channel %s", channel_id)
        raise HTTPException(status_code=502, detail="Gemini could not generate content. Check the configured model and API key.") from exc
    try:
        updated_usage = await usage_service.consume_onboarding_credit(
            str(current_user.id), channel_id, "test_generations", "test_generation_bonus", settings.test_generation_allowance
        )
    except ValueError as exc:
        raise HTTPException(status_code=429, detail="Your onboarding test-generation allowance is exhausted") from exc
    return TestGenerationResponse(
        content=result.content,
        remaining_tests=max(0, settings.test_generation_allowance - updated_usage.test_generations + updated_usage.test_generation_bonus),
    )


def _writing_dna_instructions(dna, legacy_personality: str | None = None) -> str:
    """Turn structured Writing DNA into explicit instructions for post generation."""
    analysis = "\n".join(
        f"- {key.replace('_', ' ').title()}: {value}"
        for key, value in dna.style_analysis.items()
        if value
    )
    return "\n".join(filter(None, [
        f"Tone: {', '.join(dna.tone)}" if dna.tone else None,
        f"Personality: {', '.join(dna.personality)}" if dna.personality else None,
        f"Vocabulary: {dna.vocabulary}" if dna.vocabulary else None,
        f"Sentence style: {dna.sentence_style}" if dna.sentence_style else None,
        f"Paragraph spacing: {dna.paragraph_structure}" if dna.paragraph_structure else None,
        f"Post length: {dna.post_length or dna.average_post_length}" if (dna.post_length or dna.average_post_length) else None,
        f"Hooks: {dna.hook_style}" if dna.hook_style else None,
        f"Formatting: {', '.join(dna.formatting)}" if dna.formatting else None,
        f"Emoji usage: {dna.emoji_usage}" if dna.emoji_usage else None,
        f"CTA style: {dna.cta_style}" if dna.cta_style else None,
        f"Observed writing profile:\n{analysis}" if analysis else None,
        dna.advanced_instructions,
        legacy_personality,
    ])) or "Write clearly and conversationally."


@router.post("/{channel_id}/onboarding/test-generation/feedback", status_code=204)
async def test_generation_feedback(
    channel_id: str,
    body: TestGenerationFeedbackRequest,
    current_user: UserModel = Depends(get_current_user),
):
    await channel_service.get_channel(channel_id, str(current_user.id))
    feedback = body.feedback.strip()
    if not feedback:
        raise HTTPException(status_code=422, detail="Feedback cannot be empty")
    db = channel_service.get_db()
    from datetime import datetime, timezone

    await db.generation_feedback.insert_one({
        "user_id": str(current_user.id),
        "channel_id": channel_id,
        "feedback": feedback,
        "created_at": datetime.now(timezone.utc),
    })
    return None


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: str,
    current_user: UserModel = Depends(get_current_user),
):
    user_id = str(current_user.id)
    channel = await channel_service.get_channel(channel_id, user_id)
    usage = await usage_service.get_usage(channel_id)
    return _to_response(channel, usage)


@router.patch("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: str,
    body: ChannelUpdateRequest,
    current_user: UserModel = Depends(get_current_user),
):
    user_id = str(current_user.id)
    channel = await channel_service.update_channel(channel_id, user_id, body)
    usage = await usage_service.get_usage(channel_id)
    return _to_response(channel, usage)


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: str,
    current_user: UserModel = Depends(get_current_user),
):
    await channel_service.delete_channel(channel_id, str(current_user.id))


def _to_response(channel, usage=None) -> ChannelResponse:
    from app.services.subscription_service import get_user_plan
    usage_summary = None
    if usage and usage.posts_allowance > 0:
        usage_summary = UsageSummary(
            posts_generated=usage.posts_generated,
            posts_published=usage.posts_published,
            posts_allowance=usage.posts_allowance,
            month_key=usage.month_key,
        )
    return ChannelResponse(
        id=str(channel.id),
        user_id=channel.user_id,
        telegram_channel_id=channel.telegram_channel_id,
        username=channel.username,
        name=channel.name,
        photo_url=channel.photo_url,
        brain=channel.brain,
        schedule=channel.schedule,
        publish_mode=channel.publish_mode,
        automation_status=channel.automation_status,
        is_bot_admin=channel.is_bot_admin,
        is_active=channel.is_active,
        usage=usage_summary,
        created_at=channel.created_at,
        updated_at=channel.updated_at,
    )
