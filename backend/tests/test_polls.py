import asyncio
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.api.channels import _writing_dna_instructions
from app.config.plans import get_plan
from app.models.channel import ChannelModel
from app.services.ai.base import GenerationRequest, PollPayload
from app.services.ai.gemini_provider import _parse_poll
from app.services.ai.prompt_builder import build_prompt
from app.services import telegram_bot_service
from app.models.channel import WritingDNA
from app.services.posting_service import build_generation_request, due_slot


def test_quiz_training_examples_are_included_in_generation_instructions():
    dna = WritingDNA(
        mode="samples",
        content_style="quiz_polls",
        sample_polls=[{
            "question": "Which planet is the largest?",
            "options": ["Earth", "Jupiter"],
            "correct_option_id": 1,
        }],
    )

    instructions = _writing_dna_instructions(dna)

    assert "Quiz poll examples to imitate:" in instructions
    assert "Question: Which planet is the largest?" in instructions
    assert "[CORRECT] Jupiter" in instructions


def test_quiz_training_example_rejects_invalid_correct_answer():
    with pytest.raises(ValidationError):
        WritingDNA(
            content_style="quiz_polls",
            sample_polls=[{
                "question": "Which planet is the largest?",
                "options": ["Earth", "Jupiter"],
                "correct_option_id": 2,
            }],
        )


def test_due_slot_uses_channel_timezone_and_weekday():
    channel = ChannelModel(
        _id="64b000000000000000000001",
        user_id="user-1",
        telegram_channel_id="-1001",
        name="Trivia",
        schedule={
            "timezone": "Africa/Lagos",
            "posts_per_day": 1,
            "posting_times": ["09:00"],
            "active_days": ["fri"],
        },
    )

    assert due_slot(channel, datetime(2026, 10, 23, 8, 0, tzinfo=timezone.utc)) == datetime(
        2026, 10, 23, 8, 0, tzinfo=timezone.utc
    )
    assert due_slot(channel, datetime(2026, 10, 24, 8, 0, tzinfo=timezone.utc)) is None


def test_scheduled_generation_respects_selected_content_style():
    text_channel = ChannelModel(
        _id="64b000000000000000000001",
        user_id="user-1",
        telegram_channel_id="-1001",
        name="Trivia",
        brain={
            "content_types": ["Educational", "Poll"],
            "writing_dna": {"mode": "samples", "content_style": "text_only"},
        },
    )
    poll_channel = ChannelModel(
        _id="64b000000000000000000002",
        user_id="user-1",
        telegram_channel_id="-1002",
        name="Trivia",
        brain={
            "content_types": ["Educational"],
            "writing_dna": {"mode": "samples", "content_style": "quiz_polls"},
        },
    )

    assert build_generation_request(text_channel, get_plan("free")).post_formats == ["Educational"]
    assert build_generation_request(poll_channel, get_plan("free")).post_formats == ["Poll"]


def test_poll_only_prompt_requires_structured_poll_json():
    request = GenerationRequest(
        channel_name="Trivia",
        niche="Education",
        topics=["science"],
        audience="students",
        writing_personality="clear",
        post_formats=["Poll"],
        content_strategy="engage the audience",
        products_and_offers="",
        cta_library=[],
        rules="",
        goals="engagement",
        max_post_characters=500,
    )

    prompt = build_prompt(request)

    assert "Return ONLY valid JSON" in prompt
    assert "poll_type" in prompt
    assert "Write ONLY the post text" not in prompt


def test_parse_poll_accepts_quiz_configuration():
    poll = _parse_poll(
        '{"question":"Which is correct?","options":["A","B"],'
        '"poll_type":"quiz","is_anonymous":false,"correct_option_id":1,'
        '"explanation":"B is correct."}'
    )

    assert poll == PollPayload(
        question="Which is correct?",
        options=["A", "B"],
        poll_type="quiz",
        is_anonymous=False,
        correct_option_id=1,
        explanation="B is correct.",
    )


def test_publish_poll_uses_send_poll(monkeypatch):
    captured = {}

    async def fake_call(method, payload):
        captured["method"] = method
        captured["payload"] = payload
        return {"ok": True}

    monkeypatch.setattr(telegram_bot_service, "_call", fake_call)
    result = asyncio.run(telegram_bot_service.publish_to_channel(
        "-1001",
        "ignored",
        poll=PollPayload(
            question="Choose one",
            options=["One", "Two"],
            poll_type="regular",
            is_anonymous=False,
            allows_multiple_answers=True,
        ),
    ))

    assert result == {"ok": True}
    assert captured == {
        "method": "sendPoll",
        "payload": {
            "chat_id": "-1001",
            "question": "Choose one",
            "options": ["One", "Two"],
            "is_anonymous": False,
            "type": "regular",
            "allows_multiple_answers": True,
        },
    }


def test_publish_rejects_telegram_api_failure(monkeypatch):
    async def fake_call(method, payload):
        return {"ok": False, "description": "not enough rights"}

    monkeypatch.setattr(telegram_bot_service, "_call", fake_call)
    with pytest.raises(RuntimeError, match="not enough rights"):
        asyncio.run(telegram_bot_service.publish_to_channel("-1001", "A post"))