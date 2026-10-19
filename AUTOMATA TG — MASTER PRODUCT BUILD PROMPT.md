# AUTOMATA TG — MASTER PRODUCT BUILD PROMPT

## ROLE

You are my senior full-stack engineer, software architect, UI/UX designer, and product engineer.

Your task is to begin building **Automata TG**, a production-ready, multi-tenant SaaS platform built specifically for Telegram channel owners.

You should think about this as a real commercial product that will eventually serve many users and many Telegram channels, not as a simple demo, mockup, or single-user bot.

Before writing code, first understand the product concept, architecture, user experience, and scope described below. Then translate this specification into a clean, scalable implementation.

---

# 1. WHAT IS AUTOMATA TG?

**Automata TG** is an AI-powered content management and automation platform for Telegram channel owners.

The fundamental problem we are solving is this:

Many Telegram channel owners need to consistently publish good content, maintain their channel's personality, engage their audience, promote products/services, and drive conversions — but creating content manually every day is time-consuming.

Automata TG allows a channel owner to connect their Telegram channel to the platform and configure an AI content manager that understands that specific channel.

The AI should not simply generate generic AI-written posts.

It should understand:

- What the channel is about
- The channel's niche
- The topics it focuses on
- Who the audience is
- What the channel owner wants to achieve
- How the owner writes
- The channel's writing personality
- Preferred post formats
- Content strategy
- Products and offers
- CTA methods
- Promotion schedules
- Rules and restrictions
- How frequently the channel should publish

The AI then generates content according to those instructions and can either:

1. Send the generated content to the channel owner for approval, OR
2. Automatically publish the content to the Telegram channel according to the configured schedule.

The long-term vision is for Automata TG to behave like an **AI content manager for Telegram channels**.

The user provides the strategy and teaches the AI how the channel should operate.

Automata TG handles the repetitive content creation and publishing work.

---

# 2. CORE PRODUCT PHILOSOPHY

The most important product principle is:

> **Simple for the channel owner. Sophisticated under the hood.**

The user should not need to understand:

- Prompt engineering
- AI APIs
- Model parameters
- Backend architecture
- Scheduling systems
- AI token usage
- Complex automation logic

Instead, the user should answer simple questions and configure simple options.

Automata TG should convert those settings into sophisticated AI instructions internally.

The system should therefore use a structured **Channel Brain / Channel DNA** architecture rather than storing one massive prompt as the only source of truth.

The Channel Brain should eventually contain things such as:

- Channel identity
- Niche
- Topics
- Audience
- Content strategy
- Writing personality
- Formatting preferences
- Content types
- Conversion goals
- Products/offers
- CTAs
- Rules/restrictions
- Publishing schedule
- Approval/auto-publish mode

The AI generation system should construct the appropriate instructions dynamically from these pieces.

---

# 3. TECHNOLOGY STACK

Use the following technology stack.

## Frontend

Use:

**TypeScript + React + TSX**

The frontend is a **Telegram Mini App**.

Use the existing/current React ecosystem appropriately.

For icons, use:

**Lucide React**

Do not use random icon libraries when a suitable Lucide React icon exists.

---

## Backend

Use:

**Python**

The backend should be designed as a proper API/service layer capable of handling:

- Users
- Telegram channels
- Channel configurations
- AI generation
- Subscription plans
- Usage limits
- Scheduling
- Publishing
- Authentication/session validation
- Settings
- Future automation workers

Use a clean architecture that can scale as the product grows.

---

## Database

Use:

**MongoDB**

The database should be designed for a multi-tenant SaaS.

Users must be isolated from one another.

A user may eventually have multiple Telegram channels.

Each channel must have its own configuration and automation state.

Do not design the database as if one user can only ever have one channel.

---

## AI

For the initial version, use:

**Google Gemini API**

Gemini will be the first AI provider for content generation.

However, do not tightly couple the entire application to Gemini-specific implementation details.

Create an AI service/abstraction layer so another model/provider can be added later without rewriting the entire product.

For example, conceptually:

Frontend
→ Backend
→ AI Service
→ Gemini

Later:

Frontend
→ Backend
→ AI Service
→ Gemini / OpenAI / Other Provider

---

# 4. TELEGRAM MINI APP UI

Automata TG is primarily designed to be used inside Telegram as a Mini App.

The interface must therefore feel native to Telegram.

Do not design it like a generic desktop SaaS dashboard squeezed into a mobile screen.

It should feel:

- Clean
- Modern
- Minimal
- Telegram-native
- Mobile-first
- Easy to navigate
- Spacious
- Professional

---

# 5. LIGHT/DARK MODE

The UI must support both:

- Light mode
- Dark mode

The application should detect the user's current/default Telegram theme and adapt accordingly.

If Telegram is using a dark theme, Automata TG should use the dark theme.

If Telegram is using a light theme, Automata TG should use the light theme.

Use Telegram Mini App theme parameters/CSS variables where appropriate rather than inventing a completely independent theme system.

The design should respect Telegram's environment and feel visually consistent with the Telegram client.

Do not force the user to manually select light/dark mode if Telegram already provides the appropriate theme information.

---

# 6. MAIN NAVIGATION

The primary navigation should be at the **bottom of the screen**.

It should use a Telegram-style **floating pill navigation format**.

There should initially be exactly two primary navigation items:

### Channels

Icon:
Lucide React channel/home-related icon that best represents the section.

Text:
**Channels**

The word "Channels" should appear underneath the icon.

### Settings

Icon:
Lucide React settings icon.

Text:
**Settings**

The word "Settings" should appear underneath the icon.

The navigation should be visually presented as a floating pill near the bottom of the Mini App.

It should feel lightweight rather than like a traditional web dashboard sidebar.

---

# 7. CHANNELS PAGE — HOME PAGE

The **Channels page is the default/home page** of Automata TG.

This is where the user sees and manages their connected/configured Telegram channels.

---

## 7.1 TOP HEADER

At the top of the page:

### Top-left

Display:

**Upgrade**

This should be a clear button.

Clicking it should take the user to the Automata TG subscription plans and tiers.

The upgrade button should be visually noticeable but should not make the UI feel like an aggressive advertisement.

---

### Top-right

Display the user's:

- Profile image
- Name
- Current plan badge

Example:

[Profile Image]  
Chinonye  
**PRO**

The plan badge should dynamically reflect the user's current subscription.

---

# 8. MY CHANNELS SECTION

The main content area should contain:

## My Channels

This section displays the Telegram channels that the user has configured/activated in Automata TG.

Each channel should appear inside a clean channel card/container.

---

# 9. NEW CHANNEL BUTTON

The My Channels section should have a clear:

**+ New Channel**

button.

Use a **Lucide React Plus icon**.

This button will eventually take the user through the new-channel onboarding flow.

IMPORTANT:

The detailed New Channel onboarding flow is defined in a separate specification/prompt.

Do NOT invent or fully implement the detailed onboarding logic yet.

For this stage, build the structure necessary for the New Channel flow to be plugged in cleanly later.

The subscription system should still enforce the maximum number of channels allowed by the user's plan.

For example:

Free:
1 channel

Starter:
1 channel

Pro:
3 channels

Agency:
10 channels

If a user has reached their channel limit, the UI should clearly communicate that they need to upgrade rather than silently allowing another channel.

---

# 10. CHANNEL CARD

Each configured/activated channel should appear as a clickable card/container.

The card should display:

### Channel image

Display the Telegram channel profile image where available.

### Channel name

Example:

**Football Hub**

### Username or ID

Example:

`@footballhub`

or, for a private channel:

`-1001234567890`

### Usage

Display the number of generated posts used versus the user's allowance.

Example:

**20 / 90 posts**

Meaning:

20 AI-generated posts have been used this month out of the 90 posts allowed for that channel under the current plan.

Another example:

**67 / 150 posts**

The usage indicator should be visually understandable.

Consider using a subtle progress bar/ring or similar UI element.

---

# 11. CHANNEL CARD INTERACTION

The entire channel card should be clickable.

Include a subtle **Chevron Right** Lucide icon to communicate that the card opens another page.

Clicking a channel should take the user to that channel's configuration/settings page.

This page will eventually allow the user to edit the Channel Brain, prompt/configuration, schedule, content settings, CTA library, etc.

IMPORTANT:

The detailed Channel Settings page will be designed separately based on the previously defined Channel Onboarding specification.

For this stage, create the routing/page architecture and appropriate placeholder structure so the page can later be expanded without restructuring the application.

---

# 12. EMPTY STATE

If the user has not connected any channels yet, do not show an empty-looking dashboard.

Create a proper empty state.

Example concept:

**Your channels live here**

Connect your first Telegram channel and let Automata TG handle your content.

[ + Add Your First Channel ]

The exact wording can be improved during implementation.

The empty state should clearly direct the user toward adding their first channel.

---

# 13. SETTINGS PAGE

The second primary navigation page is:

**Settings**

This page should be simple and account-focused.

Display the user's profile information:

- Profile image
- Name
- Telegram username where available

Then provide settings/actions such as:

---

## Language

Allow the user to select their preferred language.

The initial implementation can support the structure for language selection even if only one language is initially available.

The system should be built so additional languages can be added later.

---

## Current Plan

Display the user's current subscription.

Example:

**Current Plan**
PRO

Include relevant information such as:

- Plan name
- Monthly post allowance
- Channel allowance
- Renewal/subscription status where available

Provide a way to view/change/upgrade the plan.

---

## Contact Support

Clicking this should redirect/open the configured Automata TG support Telegram username/handle.

Do not hard-code the support destination throughout the frontend.

Keep external handles/links configurable.

---

## How to Use

When the user clicks this:

Automata TG should prompt the Telegram bot to send the user the Automata TG tutorial/how-to-use document.

The exact tutorial delivery mechanism can be implemented through the Telegram bot/backend.

For now, structure the application so this action can call the appropriate backend/bot flow.

---

## Subscribe to Our Announcement Channel

Clicking this should redirect the user to the official Automata TG announcement Telegram channel.

The destination should be configurable.

---

## Social Media

Provide a section for official Automata TG social media accounts.

Examples may include:

- X/Twitter
- Instagram
- TikTok
- Facebook
- Website

Each item should open the corresponding external platform/link.

Do not hard-code these links into multiple components.

Keep them centralized in configuration/backend data where appropriate.

---

# 14. SUBSCRIPTION PLANS

The initial subscription structure is:

| Plan | Channels | AI Posts | Price |
|---|---:|---:|---:|
| Free | 1 | 25 posts/month | Free |
| Starter | 1 | 90 posts/month | 500 Stars/month |
| Pro | 3 | 150 posts/channel/month | 750 Stars/month |
| Agency | 10 | 150 posts/channel/month | 1,500 Stars/month |

IMPORTANT:

These prices and limits are **initial values only**.

They must be easy to change later.

Do NOT scatter these values throughout the frontend/backend code.

Create a centralized subscription/plan configuration.

The architecture should support changing:

- Price
- Channel limit
- Monthly post allowance
- Other future limits
- Features

without requiring major code changes.

---

# 15. IMPORTANT INTERPRETATION OF POST LIMITS

The plans use different channel allowances.

For example:

### Free

1 channel

25 posts/month

### Starter

1 channel

90 posts/month

### Pro

3 channels

150 posts/channel/month

Therefore a Pro user with 3 active channels can potentially have:

150 × 3 = 450 AI posts/month

if each channel uses its full allowance.

The system should track usage at the **channel level** while also knowing the user's subscription-level limits.

For example:

User:
Pro

Channel A:
37 / 150

Channel B:
91 / 150

Channel C:
12 / 150

This is what the channel cards should display.

---

# 16. SUBSCRIPTION ARCHITECTURE

Although the exact payment implementation can be expanded later, design the application around the fact that Automata TG is a paid SaaS.

Telegram Stars will be used for subscriptions inside Telegram.

The architecture should therefore be capable of supporting:

- Free plan
- Paid plans
- Monthly subscriptions
- Plan upgrades
- Plan changes
- Usage limits
- Channel limits
- Subscription state
- Renewal/expiration state
- Payment history where appropriate

Do not build the plan system in a way that assumes today's prices can never change.

---

# 17. MULTI-TENANT ARCHITECTURE

This is extremely important.

Automata TG is NOT a single-user/single-channel application.

The architecture must support:

User A
→ Channel A
→ Channel B

User B
→ Channel C

User C
→ Channel D
→ Channel E
→ Channel F

Every channel belongs to a specific user.

Every channel must have its own:

- Telegram ID
- Username
- Name
- Image
- Niche
- Topics
- Audience
- Schedule
- Channel Brain
- Rules
- CTA Library
- Usage
- Publishing settings
- Automation status
- Generated content history

Tenant isolation is mandatory.

A user must never be able to access another user's channels, configuration, content, usage, or settings.

---

# 18. AUTHENTICATION

Because this is a Telegram Mini App, use the Telegram Mini App authentication/initialization data appropriately.

The backend must validate Telegram Mini App authentication data rather than trusting arbitrary user-provided Telegram IDs from the frontend.

The authenticated Telegram user should map to an Automata TG user record.

The frontend should never be the authority for:

- User identity
- Subscription
- Channel ownership
- Usage counts
- Plan limits
- Permissions

Those must be validated by the backend.

---

# 19. BACKEND RESPONSIBILITIES

The Python backend should eventually be responsible for:

### User management
- Create/find users
- Telegram identity
- User profile
- Language
- Subscription

### Channel management
- Connected channels
- Ownership
- Telegram metadata
- Channel activation
- Admin/bot permission status

### AI
- Gemini integration
- Prompt construction
- Channel Brain context
- Generation
- Usage tracking
- Validation

### Scheduling
- Determine when a channel needs content
- Respect channel timezone
- Respect posting limits
- Respect plan limits

### Publishing
- Telegram Bot API publishing
- Approval workflow
- Auto-publishing workflow

### Subscription
- Plans
- Usage limits
- Stars subscriptions/payment state

### Support/tutorial
- Trigger bot messages
- Tutorial delivery

---

# 20. FRONTEND RESPONSIBILITIES

The React/TSX frontend should primarily handle:

- Telegram Mini App UI
- Navigation
- Channel dashboard
- Settings
- Plan display
- Channel cards
- Usage visualization
- User interactions
- Forms
- Loading states
- Error states
- Empty states
- Theme adaptation
- Calls to backend APIs

Do not put business-critical subscription/usage logic exclusively in the frontend.

---

# 21. VISUAL DESIGN DIRECTION

The design should feel like a premium Telegram-native SaaS.

Avoid:

- Generic Bootstrap-looking dashboards
- Desktop-style sidebars
- Excessive cards everywhere
- Huge gradients
- Excessive animations
- Clutter
- Too many colors
- Unnecessary decorative elements

Prioritize:

- Clean typography
- Good spacing
- Clear hierarchy
- Rounded containers
- Subtle borders
- Telegram-native feel
- Floating bottom navigation
- Responsive mobile-first layout
- Excellent dark mode
- Excellent light mode
- Clear CTAs
- Fast perceived performance

Use Lucide React icons consistently.

Icons should support the meaning of actions rather than being decorative.

---

# 22. RESPONSIVE BEHAVIOR

Although this is a Telegram Mini App, it should still behave correctly across:

- Small mobile screens
- Large mobile screens
- Tablets
- Desktop Telegram clients where applicable

The primary design target is mobile.

Do not create a desktop-first interface and simply shrink it down.

---

# 23. IMPORTANT SCOPE BOUNDARY

There are two major areas that will be specified separately.

### NEW CHANNEL ONBOARDING

The detailed onboarding process for adding/configuring a new channel is defined in another prompt.

It consists conceptually of:

A. Channel Identity
B. Channel Brain / Train Your AI
C. CTA Library
D. Setup & Activate

Do not invent a different onboarding process.

Build the application architecture so this flow can be added cleanly.

---

### CHANNEL SETTINGS

The detailed channel settings page will also be designed later using the Channel Onboarding specification.

It will eventually allow the user to edit things such as:

- Channel identity
- Topics
- Audience
- Schedule
- Rules
- Channel Brain
- Writing style
- Products
- CTAs
- Publishing mode
- Automation

For now, establish the routing and page architecture for this area without making up functionality that has not yet been specified.

---

# 24. FUTURE PRODUCT VISION

The initial version should be designed with future expansion in mind.

Eventually Automata TG may support:

- Multiple content types
- AI-generated polls
- AI-generated images
- Content calendars
- Content queues
- News/source monitoring
- RSS sources
- Automated research
- Analytics
- Post performance analysis
- AI learning from successful posts
- Content recommendations
- Better sales/conversion optimization
- Multiple AI providers
- Agency management
- Multiple users/team members
- Advanced scheduling
- Content approval workflows
- Content history
- Post editing
- Regeneration
- A/B testing
- Channel growth insights

Do not build all of these now.

However, avoid architecture decisions that would make these future features unnecessarily difficult to add.

---

# 25. INITIAL PRODUCT FLOW

The initial high-level experience should be:

```text
Telegram User
      ↓
Open Automata TG Mini App
      ↓
Authenticate Telegram User
      ↓
Channels Home
      ↓
See My Channels
      ↓
[ + New Channel ]
      ↓
New Channel Onboarding
      ↓
Channel Activated
      ↓
Channel Appears on Home Dashboard
      ↓
User Can Open Channel Settings
      ↓
AI Generates Content
      ↓
Scheduled Automation
      ↓
Approval OR Auto Publish
      ↓
Telegram Channel
```

---

# 26. HOME PAGE CONCEPT

The home screen should visually communicate:

> “These are the Telegram channels Automata TG is managing for you.”

For example:

```text
┌──────────────────────────────────┐
│ Upgrade             [Avatar] Pro │
│                                  │
│ My Channels                  [+] │
│                                  │
│ ┌──────────────────────────────┐ │
│ │ [IMG] Football Hub        >  │ │
│ │       @footballhub           │ │
│ │       37 / 150 posts         │ │
│ │       ███████░░░             │ │
│ └──────────────────────────────┘ │
│                                  │
│ ┌──────────────────────────────┐ │
│ │ [IMG] Marketing Daily      > │ │
│ │       @marketingdaily         │ │
│ │       81 / 150 posts         │ │
│ │       █████████░             │ │
│ └──────────────────────────────┘ │
│                                  │
│                                  │
│       ┌──────────────────┐       │
│       │  ◉       ⚙       │       │
│       │ Channels Settings│       │
│       └──────────────────┘       │
└──────────────────────────────────┘
```

This is only a conceptual representation. Improve the actual UI rather than copying this literally.

---

# 27. SETTINGS PAGE CONCEPT

Conceptually:

```text
┌──────────────────────────────────┐
│                                  │
│          [Profile Image]         │
│             Name                 │
│          @username               │
│                                  │
│ ┌──────────────────────────────┐ │
│ │ Language                  >  │ │
│ └──────────────────────────────┘ │
│                                  │
│ ┌──────────────────────────────┐ │
│ │ Current Plan              >  │ │
│ │ PRO                          │ │
│ └──────────────────────────────┘ │
│                                  │
│ ┌──────────────────────────────┐ │
│ │ Contact Support           >  │ │
│ └──────────────────────────────┘ │
│                                  │
│ ┌──────────────────────────────┐ │
│ │ How to Use                >  │ │
│ └──────────────────────────────┘ │
│                                  │
│ ┌──────────────────────────────┐ │
│ │ Announcement Channel       > │ │
│ └──────────────────────────────┘ │
│                                  │
│ Social Media                     │
│ X · Instagram · TikTok · etc.   │
│                                  │
│       [ Floating Nav ]           │
└──────────────────────────────────┘
```

Again, use this only as a conceptual reference.

---

# 28. CODE QUALITY REQUIREMENTS

Build the application using clean, maintainable code.

The project should have:

- Clear folder structure
- Reusable components
- Reusable UI primitives
- Proper TypeScript types
- Proper API typing
- Environment variables for secrets/configuration
- Centralized configuration
- Error handling
- Loading states
- Empty states
- Backend validation
- Database indexes where appropriate
- Secure authentication
- Tenant isolation
- Clear separation between UI, business logic, and data access

Do not duplicate logic unnecessarily.

Do not hard-code:

- Telegram usernames
- Support handles
- Announcement channel links
- Social links
- API keys
- Subscription prices
- Plan limits
- Bot tokens
- Database credentials

Use environment/configuration management appropriately.

---

# 29. SECURITY REQUIREMENTS

Never expose:

- Gemini API keys
- Telegram bot token
- MongoDB credentials
- Backend secrets

to the frontend.

All sensitive operations must happen on the backend.

The frontend should communicate with the backend through authenticated API requests.

Validate all user input on the backend.

Enforce ownership checks for every channel-related operation.

For example:

A request to:

GET /channels/123

must verify that channel 123 actually belongs to the authenticated user.

Never trust the frontend to provide a valid owner ID.

---

# 30. USAGE TRACKING

The system needs reliable usage tracking.

At minimum track:

- Posts generated this month
- Posts published this month
- Test generations used
- Current monthly allowance
- Remaining allowance

The displayed value:

**20 / 90 posts**

must come from backend-controlled usage data.

Do not simply calculate it from a frontend counter.

The backend should be the source of truth.

---

# 31. PLAN CONFIGURATION

Create a centralized plan configuration similar in concept to:

```text
FREE
channels: 1
posts_per_channel: 25
price_stars: 0

STARTER
channels: 1
posts_per_channel: 90
price_stars: 500

PRO
channels: 3
posts_per_channel: 150
price_stars: 750

AGENCY
channels: 10
posts_per_channel: 150
price_stars: 1500
```

This is conceptual.

Use an appropriate implementation for the actual project.

The important requirement is that these values are centralized and editable.

---

# 32. DO NOT OVERBUILD THE FIRST VERSION

Build the core product foundation properly.

Do not spend time implementing speculative features that are not part of the current scope.

The immediate priority is:

1. Telegram Mini App foundation
2. Authentication
3. Theme detection
4. Main navigation
5. Channels home page
6. Settings page
7. User profile display
8. Subscription/plan foundation
9. Channel model
10. Channel usage display
11. New Channel entry point
12. Channel Settings entry point
13. Gemini service architecture
14. Backend API foundation
15. MongoDB data model
16. Multi-tenant architecture
17. Configuration architecture
18. Clean UI system

The detailed New Channel onboarding and Channel Settings implementation will be supplied separately.

---

# 33. HOW YOU SHOULD WORK

Do not blindly start generating hundreds of files.

First analyze the requirements and determine:

- Application architecture
- Frontend architecture
- Backend architecture
- MongoDB collections/models
- Authentication flow
- API structure
- Telegram integration approach
- AI service architecture
- Subscription architecture
- Usage tracking architecture
- Routing structure
- Component structure
- Configuration strategy

Then implement the product foundation in logical stages.

Before making major architectural decisions that could significantly affect the future product, explain the decision and why it is appropriate.

However, do not stop unnecessarily for minor decisions. Use good engineering judgment for implementation details that are not explicitly specified.

---

# 34. MOST IMPORTANT PRODUCT RULE

Always remember what Automata TG actually is:

> **Automata TG is an AI content manager for Telegram channels, not merely an AI text generator.**

The channel owner should feel that they are configuring an AI employee/assistant that understands their channel and can consistently create and publish content according to their instructions.

The interface should therefore make the product feel:

**Powerful → but simple.**

**Automated → but controllable.**

**AI-powered → but personalized.**

**Built for Telegram → not a generic social media scheduler.**

Build the foundation with this product vision in mind.