MASTER BUILD PROMPT — TELEGRAM AI CHANNEL CONTENT MANAGER

Editable specification for an AI coding/design Agent

## ROLE

You are my senior product engineer, software architect, UX/UI designer, and AI product strategist. I am building a multi-tenant SaaS platform for Telegram channel admins. The product should allow many different users to connect their Telegram channels and have an AI content manager generate and publish channel-specific content automatically according to each channel’s identity, audience, writing style, content strategy, CTAs, rules, and schedule.

Do not treat this as a simple “AI post generator.” The product should feel like an AI content manager/channel brain that understands a specific Telegram channel and operates it according to the owner’s strategy.

## CORE PRODUCT CONCEPT

A user:

1. Creates/accesses their account.

2. Connects one or more Telegram channels.

3. Gives the platform’s Telegram bot the required admin permission to post.

4. Configures each channel independently.

5. Defines the channel identity, audience, topics, goals, rules, and posting schedule.

6. Teaches the AI how the channel should write.

7. Optionally adds products/offers and CTA instructions.

8. Tests the AI.

9. Chooses whether generated posts require approval or can be auto-published.

10. Activates automation.

The architecture must be multi-tenant: every user can have one or more channels, and each channel must have its own configuration, AI personality, schedule, CTA library, rules, generation history, and publishing settings.

## IMPORTANT PRODUCT PRINCIPLE

Keep the user experience simple. The user should not need to know how to write complex AI prompts. The interface should collect structured information through questions, selections, inputs, examples, and simple controls. Under the hood, the system should convert these settings into sophisticated model instructions.

Do NOT store one giant prompt as the primary source of truth. Store structured Channel DNA/Channel Brain data and dynamically construct generation instructions from it.

## ONBOARDING — EXACTLY 4 PARTS

## PART A — CHANNEL IDENTITY

Purpose: Understand what the channel is, who it serves, what it should achieve, when it should post, and what the AI must never/always do.

### A1. CONNECT CHANNEL

The user should be able to enter:

- Public Telegram channel username, e.g. @mychannel

- Public Telegram channel link

- Private channel ID

Provide a clear “Find/Connect Channel” action.

After finding the channel, display useful channel information returned by Telegram where available, such as:

- Channel name

- Username/link

- Profile photo

- Description

- Public/private status

- Subscriber/member count where available

The system must verify that the platform bot has the required channel admin permission to publish messages. If not, clearly tell the user what permission is required and guide them to add/promote the bot before continuing.

### A2. CHANNEL NICHE

Ask:

“What is your channel about?”

Provide selectable niche categories such as:

- Sports

- Finance

- Education

- Relationships

- Marketing

- Masculinity

- Entertainment

- Technology

- Gaming

- Lifestyle

- Products/Services

- Other

Allow multiple selections where appropriate.

### A3. MAIN TOPICS

Ask:

“What topics should your AI regularly create content about?”

Allow users to select suggested topics and add custom topics.

Example:

Niche = Marketing

Topics = Facebook Ads, TikTok Ads, Sales, Lead Generation, Copywriting, Digital Marketing, Business Growth, Other.

The AI should use these topics as its content boundaries/preferences.

### A4. AUDIENCE

Ask who the content is intended for.

Possible fields:

- Age range

- Location

- Gender (optional)

- Experience/knowledge level

- Interests

- Free-text description of the ideal audience

Example:

“Young Nigerian entrepreneurs aged 18–35 who want to learn how to make money online and grow their businesses.”

### A5. CONTENT/POST ALLOWANCE

The number of AI-generated posts must respect the user’s subscription plan.

Show the user’s plan allowance clearly.

Example:

“Your plan allows 90 AI posts/month.”

Then let the user choose the desired frequency within that allowance:

- Posts per day

- Posts per week/month where appropriate

The UI must prevent or clearly warn against configurations exceeding the subscription allowance.

### A6. POSTING SCHEDULE

Allow the user to define when the AI should publish.

Provide simple options such as:

- Same schedule every day

- Different schedule for each day

- Custom schedule

Allow selection of days and times.

Example:

Monday: 8:00 AM, 1:00 PM, 7:00 PM

Tuesday: 8:00 AM, 1:00 PM, 7:00 PM

The system must store timezone information and use the channel/user’s configured timezone for scheduling.

### A7. CONVERSION GOALS

Ask:

“What do you want your content to help achieve?”

Allow multiple goals:

- Grow the channel

- Increase engagement

- Get reactions/comments

- Get link clicks

- Get Telegram DMs

- Generate leads

- Sell products/services

- Promote another channel

- Get subscribers

- Drive traffic

- Other

These goals must influence later content strategy and CTA behavior.

### A8. RULES & RESTRICTIONS — MOVED TO PART A

This is a global channel-level configuration and must be placed in Part A.

Ask the user what the AI should always do and never do.

Examples of “Always” rules:

- Use Nigerian English

- Keep paragraphs short

- Verify statistics before mentioning them

- Ask a question at the end of engagement posts

- Include sources for news content

- Use simple language

Examples of “Never” rules:

- Do not use profanity

- Do not discuss politics

- Do not make medical claims

- Do not insult competitors

- Do not use clickbait

- Do not make financial promises

- Do not mention specific brands

- Do not discuss forbidden topics

Support custom rules.

Rules should be treated as high-priority constraints during generation.

## PART B — CHANNEL BRAIN / TRAIN YOUR AI

Purpose: Teach the AI how the channel should SOUND and WRITE.

This section should strongly emphasize writing style and personality.

Do NOT force users to write a sophisticated prompt.

Give them two options:

### OPTION A — BUILD MANUALLY

For users who want to configure the writing style themselves.

Collect structured settings such as:

Tone/personality:

- Casual

- Professional

- Friendly

- Funny

- Bold

- Authoritative

- Motivational

- Conversational

- Educational

- Opinionated

- Other

Writing style:

- Short and punchy

- Detailed and educational

- Storytelling

- News-style

- Conversational

- Opinionated

- Inspirational

- Other

Formatting:

- Short paragraphs

- Headings

- Bullet points

- Numbered lists

- Bold text

- Quotes

- Questions

- Separators

- Telegram-friendly formatting

Emoji usage:

- None

- Minimal

- Moderate

- Heavy

Post length:

- Short

- Medium

- Long

- Custom

Also allow an optional Advanced Instructions field for users who want to provide additional instructions manually.

### OPTION B — LEARN FROM MY POSTS

This should be a major product feature.

Explain:

“Show your AI how you write. Paste 3–5 examples of your previous posts and we’ll analyze your writing style.”

Allow 3–5 sample posts.

The AI should analyze the examples and produce a structured writing personality/style profile, including where inferable:

- Tone

- Personality

- Vocabulary

- Sentence style

- Sentence length

- Paragraph structure

- Average post length

- Hook style

- Formatting patterns

- Emoji frequency/style

- Use of questions

- Storytelling style

- CTA style

- Promotional style

- Level of formality

- Language patterns

- Overall writing personality

Example result:

“Your writing personality:

Tone: Casual, confident and slightly provocative

Style: Short, punchy paragraphs

Vocabulary: Simple conversational English

Sentence length: Short-medium

Emoji usage: Moderate

Hooks: Curiosity-based openings

Formatting: Frequent line breaks

CTA: Direct but not aggressive

Overall personality: Confident + educational + conversational”

The user must be able to:

- Review the analysis

- Edit individual settings

- Approve the result

- Re-run the analysis if needed

The system should turn the approved result into the channel’s structured “Writing DNA.”

IMPORTANT:

This is not model fine-tuning. It is structured channel-specific context/instructions that are supplied to the AI during generation.

## PART C — CTA LIBRARY

Purpose: Store products, offers, destinations, and CTA instructions that the AI can use when appropriate.

This part is OPTIONAL/CONDITIONAL.

If the user’s conversion goals do not involve:

- Selling a product/service

- Promoting an offer

- Promoting another channel/list

- Redirecting traffic

- Generating leads through a CTA

then allow the user to skip Part C.

Show a clear “Skip for now” option.

### C1. PRODUCTS & OFFERS

Allow users to create multiple products/offers.

Example:

Product: Facebook Ads Masterclass

Fields can include:

- Product/offer name

- Description

- What problem it solves

- Target audience

- Price

- Selling points

- Benefits

- Features

- Proof/testimonials/case studies where supplied by the user

- Offer details

- Other relevant sales information

The AI should use this information to create relevant promotional content without inventing product claims.

### C2. CTA CONFIGURATION

For each product/offer, configure how users should take action.

Possible CTA types:

- Telegram DM

- Link click

- Button

- Join a channel

- Purchase link

- Other

For Telegram DM CTAs, support:

- Telegram username

- Keyword

- Example: “Send ADS to @JohnSupport.”

For link CTAs, support:

- Destination URL

- CTA style

The CTA library should allow different CTAs for different products.

### C3. CTA/PROMOTION STYLE

Allow the user to define how aggressively the AI should promote.

Examples:

- Soft sell

- Educational before selling

- Direct

- Urgent

- Curiosity-driven

- Story-based

- Conversational

Allow custom instructions.

### C4. PROMOTION SCHEDULE

Allow promotion schedules by:

- Day

- Time

- Product/offer

- Frequency/maximum promotions

Example:

Monday → TikTok Ads

Tuesday → Facebook Ads

Wednesday → No promotion

Thursday → Facebook Ads

Friday → Digital marketing course

The system should prevent the channel from becoming excessively promotional and should respect the user’s configured limits.

The AI should not automatically attach a CTA to every post unless the user explicitly configures that behavior.

## PART D — SETUP & ACTIVATE

Purpose: Test the configured AI, select publishing behavior, review settings, and activate automation.

### D1. TEST AI

Before activation, allow the user to test the configured AI.

The user should be able to select or provide:

- Content type

- Topic

- Optional context

Then generate a sample post.

Because AI generation costs API tokens, TEST AI MUST HAVE A LIMITED ALLOWANCE.

For example:

- Show remaining test generations

- Limit the number of tests according to product/business rules

- Do not allow unlimited free generation

The exact allowance should be configurable from the backend/admin settings rather than hard-coded into the UI.

The test experience should allow feedback such as:

- Sounds like me

- Doesn’t sound like me

- Too formal

- Too long

- Too many emojis

- CTA too aggressive

- Other feedback

If useful, feedback can lead the user back to the relevant Channel Brain setting.

### D2. PUBLISHING MODE

Give the user two options:

AUTO PUBLISH

AI generates and publishes posts automatically according to the configured schedule.

APPROVE BEFORE PUBLISH

AI generates the post and sends it to the user for approval before it is published.

The UI should clearly explain the difference.

### D3. FINAL REVIEW

Before activation, show a concise summary:

Channel

Niche

Topics

Audience

Posts/frequency

Schedule

Writing personality

Conversion goals

CTA/products if configured

Rules & restrictions

Publishing mode

Allow the user to go back and edit any section.

### D4. ACTIVATE

Provide a clear final action:

“Activate AI”

Once activated:

- Save configuration

- Enable scheduler/automation

- Begin following the configured schedule

- Track generation and publishing events

- Notify the user of relevant failures/errors

## CHANNEL DNA / INTERNAL DATA MODEL

Do NOT make the entire system dependent on one giant prompt.

Store structured data approximately like:

Channel

├── Identity

│   ├── telegram_channel_id

│   ├── username/link

│   ├── name

│   ├── niche

│   ├── topics

│   └── audience

│

├── Content Strategy

│   ├── post_allowance

│   ├── frequency

│   ├── content_types

│   ├── content_mix

│   ├── conversion_goals

│   └── schedule

│

├── Rules

│   ├── always_do

│   ├── never_do

│   ├── forbidden_topics

│   ├── forbidden_words

│   └── custom_rules

│

├── Channel Brain

│   ├── mode

│   ├── tone

│   ├── personality

│   ├── vocabulary

│   ├── sentence_style

│   ├── formatting

│   ├── emoji_usage

│   ├── post_length

│   ├── hook_style

│   ├── cta_style

│   ├── advanced_instructions

│   └── sample_posts/style_analysis

│

├── CTA Library

│   ├── products

│   ├── offers

│   ├── selling_points

│   ├── CTA types

│   ├── destinations

│   └── promotion schedules

│

└── Publishing

├── approval_mode

├── active

├── test_generation_allowance

└── automation status

Adapt the exact database schema to the chosen technology stack, but preserve this separation of concerns.

## AI GENERATION ARCHITECTURE

Every generated post should be assembled from multiple layers rather than one permanent prompt.

Conceptually:

CHANNEL DNA

+

CONTENT JOB

+

CONTENT TYPE

+

CURRENT TOPIC/CONTEXT

+

AUDIENCE

+

CONVERSION GOAL

+

CTA RULES

+

GLOBAL RULES/RESTRICTIONS

+

OUTPUT FORMAT

+

SCHEDULE CONTEXT

→ AI MODEL

→ VALIDATION/QUALITY CHECK

→ FINAL POST

→ APPROVAL OR TELEGRAM PUBLISH

Do not use the exact same generation instruction for every post.

Create different content-job strategies/templates, such as:

- Educational

- News/update

- Tips

- Story

- Engagement

- Question

- Poll

- Promotional

- Product recommendation

- Testimonial/case study

- Offer

- Announcement

The Channel Brain defines HOW the AI writes.

The Content Job defines WHAT the AI is currently trying to accomplish.

## DIGITAL PRODUCT / SALES USE CASE

The system must work especially well for users who sell digital products/services.

Example configuration:

Channel:

Digital marketing education

Audience:

Young Nigerian entrepreneurs

Voice:

Casual + educational

Content mix:

40% education

30% value/tips

20% engagement

10% promotion

Product:

Facebook Ads Masterclass

Selling points:

Practical tutorials, Nigerian examples, templates, etc.

CTA:

Send “ADS” to @JohnSupport

Rule:

Teach something valuable before selling. Do not sound desperate.

Schedule:

08:00 educational

13:00 tip

19:00 engagement

Friday 18:00 promotional

The AI should be capable of generating content that provides genuine value while naturally leading the audience toward the configured CTA when a promotional objective is appropriate.

Do not make every post a sales post.

## UX/UI REQUIREMENTS

The onboarding should feel simple, modern, and guided.

Use exactly four top-level onboarding steps:

1. Channel Identity

2. Channel Brain

3. CTA Library

4. Setup & Activate

Use progress indication.

Each part should have:

- Clear title

- Short explanation

- Helpful examples

- Sensible defaults

- Validation

- Save/continue

- Back/edit capability

Avoid overwhelming users with technical AI terminology.

Prefer:

“Teach Your AI”

“Channel Brain”

“Writing Style”

“Show us how you write”

instead of:

“Prompt engineering”

“Model configuration”

“Fine-tuning”

The interface should make advanced complexity optional.

## SUBSCRIPTION / USAGE CONSIDERATIONS

The product is paid.

AI generation usage must be connected to the user’s subscription/plan.

At minimum, the architecture should be able to track:

- Monthly post allowance

- Posts generated

- Posts published

- Test generations used

- Remaining generation allowance

- Number of connected channels

- Plan limits

Do not hard-code plan limits throughout the frontend. Centralize plan/usage rules in the backend.

The system must prevent users from exceeding their allowed generation quota unless the business logic explicitly permits overage.

## MULTI-TENANCY

The system is NOT a single-channel bot.

Design for:

User A

├── Channel A

└── Channel B

User B

├── Channel C

└── Channel D

└── Channel E

Every channel must have isolated:

- Identity

- Brain

- Rules

- Products

- CTAs

- Schedule

- Usage

- Generated posts

- Publishing history

Never allow one tenant/channel’s configuration or content to leak into another tenant.

## EXPECTED PRODUCT BEHAVIOR

After activation, the platform should operate roughly like this:

1. Scheduler detects that a channel has a post due.

2. System checks channel activation status and subscription/usage limits.

3. System determines the appropriate content job/content type.

4. System loads that channel’s Channel DNA.

5. System loads current topics/context and relevant content information.

6. System checks conversion goals and CTA/promotion schedule.

7. System constructs the generation instructions.

8. AI generates the draft.

9. System performs validation/quality checks against channel rules and required format.

10. If approval mode is enabled, send the draft to the user for approval.

11. If auto-publish is enabled, publish through Telegram.

12. Record the generation/publishing event and usage.

13. Handle failures gracefully and notify the user when necessary.

## IMPORTANT DESIGN PRINCIPLES

1. Simple for the admin, sophisticated under the hood.

2. The user answers simple questions; the platform builds sophisticated AI instructions.

3. Channel Brain/Channel DNA is the core intelligence layer.

4. Writing style is a first-class product feature.

5. Sample-post analysis should create an editable writing profile.

6. CTA Library is optional and should only appear as necessary.

7. Rules & Restrictions belong to Part A as global channel rules.

8. Test AI must have controlled usage because generations cost API tokens.

9. Publishing must support both approval and auto-publish modes.

10. Subscription limits must be enforced centrally.

11. The architecture must support multiple users and multiple channels per user.

12. The system should be model-agnostic enough to switch AI providers later.

13. Do not invent product claims, statistics, testimonials, or facts supplied neither by the user nor by an approved source/context.

14. The AI should preserve the channel’s writing personality without blindly copying sample posts word-for-word.

15. The product should prioritize consistency, usefulness, natural writing, and the channel owner’s goals.

## YOUR TASK AS MY AGENT

Use this specification as the product source of truth for the initial design/build.

Before implementing, translate the specification into:

- Product architecture

- User flows

- Database/data model

- Frontend pages/components

- Backend services/API endpoints

- Authentication and tenant isolation

- Telegram channel connection flow

- Telegram bot/admin permission flow

- AI generation pipeline

- Channel Brain/AI analysis pipeline

- CTA/product management

- Scheduler/worker architecture

- Subscription and usage tracking

- Test-generation limits

- Approval workflow

- Auto-publishing workflow

- Error handling

- Logging and generation history

- Admin/configuration capabilities

Do not remove important functionality merely to simplify the implementation. If a technical implementation detail is not specified here, choose a sensible scalable approach that fits the product’s architecture and explain the decision before making major irreversible choices.

The goal is to build a real multi-tenant SaaS product, not a demo or single-user prototype.
