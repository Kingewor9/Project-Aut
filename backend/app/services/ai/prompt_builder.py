"""
Prompt builder — constructs structured AI instructions from Channel Brain data.

The prompt is assembled dynamically from the channel's configured DNA.
A simple configuration → a sophisticated, context-rich AI prompt.
"""
from __future__ import annotations

from app.services.ai.base import GenerationRequest


def build_style_analysis_prompt(channel_name: str, sample_posts: list[str]) -> str:
        """Build a strict analysis prompt that turns examples into editable Writing DNA."""
        examples = "\n\n".join(
                f"--- SAMPLE POST {index} ---\n{post.strip()}"
                for index, post in enumerate(sample_posts, start=1)
        )
        return f"""You are a writing-style analyst for a Telegram channel named \"{channel_name}\".

Analyze the author's writing from the sample posts below. Your job is to identify repeatable patterns, not to praise the author and not to rewrite the posts.

Pay close attention to:
- tone and emotional attitude
- personality and level of confidence
- vocabulary and language variety
- sentence length and sentence rhythm
- paragraph spacing and line-break habits
- hook/opening patterns
- storytelling structure
- formatting, punctuation, headings, lists, quotes, and separators
- emoji frequency, placement, and meaning
- post length and information density
- questions and engagement devices
- CTA and promotional style
- level of formality
- distinctive language patterns

These findings will become direct instructions for another AI that must write new posts in the same voice without copying any sample word-for-word.

Return ONLY valid JSON. Do not use Markdown fences. Use exactly this shape:
{{
    \"mode\": \"samples\",
    \"tone\": [\"...\"],
    \"personality\": [\"...\"],
    \"vocabulary\": \"...\",
    \"sentence_style\": \"...\",
    \"paragraph_structure\": \"...\",
    \"average_post_length\": \"...\",
    \"hook_style\": \"...\",
    \"formatting\": [\"...\"],
    \"emoji_usage\": \"...\",
    \"post_length\": \"short|medium|long\",
    \"cta_style\": \"...\",
    \"advanced_instructions\": \"Write new posts using these observed patterns. Preserve the author's spacing, rhythm, and formatting. Never copy a sample verbatim.\",
    \"sample_posts\": [],
    \"style_analysis\": {{
        \"overall_voice\": \"...\",
        \"sentence_length\": \"...\",
        \"line_break_pattern\": \"...\",
        \"storytelling_pattern\": \"...\",
        \"emoji_pattern\": \"...\",
        \"cta_pattern\": \"...\",
        \"confidence_notes\": \"...\"
    }},
    \"style_analysis_status\": \"analyzed\"
}}

{examples}"""


def build_prompt(req: GenerationRequest) -> str:
    """Build the full system + user prompt for a Telegram post generation."""

    topics_str = ", ".join(req.topics) if req.topics else "general topics related to the channel"
    formats_str = ", ".join(req.post_formats) if req.post_formats else "text posts"
    cta_str = "\n".join(f"- {c}" for c in req.cta_library) if req.cta_library else "- None specified"
    poll_only = len(req.post_formats) == 1 and req.post_formats[0].strip().lower() == "poll"
    output_instructions = (
        """Return ONLY valid JSON with this exact shape:
{"question":"...","options":["...","..."],"poll_type":"regular|quiz","is_anonymous":true,"allows_multiple_answers":false,"correct_option_id":null,"explanation":null}
Choose the poll kind, anonymity, and whether multiple answers are allowed based on the user's prompt. Use poll_type=quiz and a zero-based correct_option_id only when the prompt calls for a quiz or a correct answer. For regular polls, correct_option_id and explanation must be null. Include 2-10 concise, distinct options. Do not include Markdown fences or any text outside the JSON object."""
        if poll_only else
        """Write ONLY the post text. No meta-commentary, no explanations, no extra labels.
- Write a complete, publish-ready post with a clear beginning, middle, and ending.
- Use 3–7 short paragraphs unless the channel's observed style clearly uses another structure.
- Never stop mid-sentence. End with complete punctuation and a natural conclusion.
- Use one of the preferred formats."""
    )

    prompt = f"""You are the AI content manager for a Telegram channel called "{req.channel_name}".

## Channel Identity
- **Niche**: {req.niche or "Not specified"}
- **Topics**: {topics_str}
- **Target Audience**: {req.audience or "Not specified"}
- **Goals**: {req.goals or "Engage and grow the audience"}

## Writing Personality
{req.writing_personality or "Professional, engaging, and conversational."}

## Content Strategy
{req.content_strategy or "Produce valuable, engaging content that the audience will find useful and shareable."}

## Preferred Post Formats
{formats_str}

## Products & Offers
{req.products_and_offers or "No specific products to promote right now."}

## CTA Library
{cta_str}

## Rules & Restrictions
{req.rules or "No specific restrictions."}

## Your Task
Create ONE Telegram channel publication right now.

Requirements:
- {output_instructions}
- {f"Additional instructions: {req.extra_instructions}" if req.extra_instructions else "No additional instructions."}
- Match the channel's writing personality exactly.
- Keep it appropriate for Telegram (paragraphs, emojis where fitting, no excessive length).
- The final post must not exceed {req.max_post_characters} characters, including spaces, line breaks, and emojis.
- Generate the post naturally from the channel context. Do not add unnecessary words simply to approach the limit.
- Include a relevant CTA from the library if appropriate.
- The post should feel native to Telegram — NOT like a blog article or generic social media post.
- Do NOT use markdown headers. Use plain text, line breaks, and emojis naturally.

Write the post now:"""

    return prompt
