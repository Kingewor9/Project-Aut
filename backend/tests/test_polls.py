import asyncio

from app.services.ai.base import GenerationRequest, PollPayload
from app.services.ai.gemini_provider import _parse_poll
from app.services.ai.prompt_builder import build_prompt
from app.services import telegram_bot_service


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