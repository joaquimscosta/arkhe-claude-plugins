# Google Stitch Prompt Examples

This file provides before/after examples demonstrating how to transform natural language
or structured specs into optimized Stitch-ready prompts.

Claude uses these examples as reference for tone, structure, and style when authoring new prompts.

---

## Example 1 — SaaS Analytics Dashboard

**Input (natural language):**
> We need a web dashboard for our SaaS platform with metrics like MRR and churn rate.
> It should feel professional but not boring, and show charts and cards for KPIs.

**Optimized Stitch Prompt:**
> Design a responsive web dashboard for a SaaS analytics app.  
> Include:  
> - Left sidebar with logo and navigation (Overview, MRR, Churn, Cohorts, Settings)  
> - Top header with search, notifications, and user avatar  
> - Main dashboard with KPI cards (MRR, Active Users, Churn Rate, ARPU)  
> - Line chart for revenue over time and a table of recent subscriptions  
> Style: clean, minimal, enterprise-grade, neutral background with deep blue accents, sans-serif typography, subtle shadows.  
> Optimize for desktop first, single-column layout on mobile.

---

## Example 2 — Mobile Banking App (screen-based)

**Input (short brief):**
> Create a mobile banking interface with account overview, transaction list, and payments.

**Optimized Stitch Prompt:**
> Design a mobile banking app with the following screens:  
> - **Accounts Overview:** balance summary, account cards, quick links for transfers  
> - **Transactions:** scrollable list with categories, amounts, and icons  
> - **Payments:** form for bill payment with amount, payee, and schedule fields  
> Style: modern, clean, deep teal accents, white background, geometric sans-serif type.  
> Use consistent 8px spacing and smooth animations between screens.

---

## Example 3 — Dashboard Spec File Conversion

**Input (`specs/marketing.md`):**
```markdown
# Marketing Analytics Dashboard
- Sidebar: Campaigns, Performance, Budgets
- Header: date range filter, search, notifications
- Main: performance chart + campaign cards
- Style: editorial, warm beige background, bold serif headings
````

**Optimized Stitch Prompt:**

> Create a marketing analytics dashboard for a web app.
> Include:
>
> * Left sidebar with navigation (Campaigns, Performance, Budgets)
> * Top header with date range filter, search, and notifications
> * Main area with line chart of campaign performance and a 3-column grid of campaign cards
>   Style: editorial, warm beige background, bold serif headings, clean spacing, subtle shadows.
>   Optimize for desktop; single-column layout for mobile export.

---

## Example 4 — Prompt Refinement (iterative edit)

**Input (user revision):**

> On the dashboard, move the KPI cards above the chart and add a dropdown to filter by region.

**Optimized Stitch Prompt:**

> On the dashboard screen, reposition KPI cards above the revenue chart.
> Add a small dropdown labeled “Region” aligned right in the chart header.
> Maintain existing typography, colors, and layout proportions.
> Avoid regenerating the sidebar or other elements.

---

## Example 5 — Prompt with Image Reference

**Input:**

> Use the uploaded wireframe as base for a habit tracker app.
> Keep bottom navigation, but make it more colorful and rounded.

**Optimized Stitch Prompt:**

> Use the uploaded wireframe as the base layout for a mobile habit-tracking app.
> Retain bottom navigation with four icons, add subtle labels underneath.
> Use rounded cards for daily habits with progress rings.
> Style: friendly, pastel purple and teal color palette, playful rounded typography, light shadows.
> Focus on a calm, approachable tone suitable for everyday use.

---

## Example 6 — Form-Based Workflow

**Input (semi-structured spec):**

```yaml
screen: Onboarding
steps:
  - Welcome
  - Personal Info Form
  - Confirmation
theme: light, minimal, blue accents
layout: centered card
```

**Optimized Stitch Prompt:**

> Design a 3-step onboarding flow for a web app.
> Include:
>
> * Step 1: Welcome screen with app logo and “Get Started” button
> * Step 2: Personal info form with name, email, and password fields
> * Step 3: Confirmation screen with success message and login link
>   Style: light, minimal, blue accents, centered card layout, rounded inputs, soft shadows.
>   Ensure consistent transitions between steps.

---

## Usage Notes

When testing this Skill, you can use these example inputs directly:

```bash
Optimize this input into a Google Stitch prompt:
"A dashboard for subscription analytics with revenue chart and customer table."
```

Claude should automatically invoke the **authoring-stitch-prompts** Skill and return a concise, directive, and visually structured Stitch-ready output.

---

## Example 7 — Multi-Prompt Split (Dashboard + Settings)

**Input (natural language):**
> Create a SaaS app with a dashboard showing metrics and a settings page for user preferences.

**Split Detection & Auto-Application:**
> This input contains 2 distinct screens:
> 1. Dashboard (metrics visualization)
> 2. Settings page (user preferences)
>
> Applying smart default: Generate as 2 separate prompts for better atomicity.

**Optimized Prompt 1 (Dashboard):**
> Design a responsive web dashboard for a SaaS analytics app.
> Include: left sidebar (logo, navigation links), top header (search, notifications, user avatar), main section with KPI cards (MRR, Active Users, Churn Rate, ARPU), line chart for revenue over time.
> Style: clean, minimal, enterprise-grade, neutral background with deep blue accents, sans-serif typography, subtle shadows.
> Optimize for desktop first, single-column layout on mobile.

**File Created:**
`.google-stitch/prompts/dashboard-v1.md`

**Note:**
```
---
Additional prompts needed:
2. Settings page: User preferences with profile, notifications, billing
   → Will save as: settings-v1.md
```

**Optimized Prompt 2 (Settings):**
> Design a settings page for user preferences in a SaaS app.
> Include: left sidebar (Profile, Notifications, Billing, Security), main area with form sections for each category, save/cancel buttons at bottom.
> Style: clean, minimal, neutral background, deep blue accents, sans-serif typography, clear section dividers.
> Optimize for desktop, stack sections on mobile.

**File Created:**
`.google-stitch/prompts/settings-v1.md`

---

## Example 8 — Single Screen, Multiple Intents

**Input:**
> Article page with reading pane, comment section, and related articles grid.

**Split Detection:**
> This input contains 3 distinct intents:
> 1. Content consumption (reading pane)
> 2. User engagement (comment section)
> 3. Content discovery (related articles grid)
>
> Recommendation: Generate as 3 separate prompts for better atomicity.
> Proceed with split? [Split / Combine]

**User Response:** Split

**Optimized Prompt 1 (Reading Pane):**
> Design a reading pane for long-form article content on web.
> Include: article title, author byline with avatar, publish date, featured image, formatted text with headings and paragraphs, inline images.
> Style: editorial, serif headings (Georgia), sans-serif body (Helvetica), generous line spacing (1.6), max-width 720px, cream background.
> Optimize for readability, responsive images.

**Optimized Prompt 2 (Comment Section):**
> Design a comment section below article content.
> Include: comment count header, comment thread with avatars and timestamps, nested replies (1 level), "Add Comment" form with textarea and submit button.
> Style: clean, minimal, neutral gray background, sans-serif typography, subtle borders between comments.
> Optimize for threaded discussions, keyboard navigation.

**Optimized Prompt 3 (Related Articles Grid):**
> Design a related articles grid at page bottom.
> Include: "Related Articles" heading, 3-column grid (stack on mobile) with thumbnail, title, excerpt (80 chars), read time badge.
> Style: clean, neutral background, subtle card shadows, sans-serif typography, Ocean Blue (#005A8D) accents.
> Optimize for mobile-first responsive layout.

**Files Created:**
- `.google-stitch/prompts/reading-pane-v1.md`
- `.google-stitch/prompts/comments-v1.md`
- `.google-stitch/prompts/related-grid-v1.md`

---

## Example 9 — Keep Together (Single Intent)

**Input:**
> Login form with email, password, submit button, "Forgot password?" link, and "Sign up" link.

**Split Detection:**
> This input contains 1 intent:
> 1. User authentication (login workflow)
>
> All components serve a single goal. Recommendation: Keep as 1 prompt.

**Optimized Prompt:**
> Design a login form for a web app.
> Include: centered card with logo, email input field, password input field, "Sign In" button, "Forgot password?" link below, "Don't have an account? Sign up" link at bottom.
> Style: clean, modern, centered layout, Ocean Blue (#005A8D) primary button, rounded inputs, subtle card shadow.
> Optimize for mobile-first, full keyboard navigation.

**File Created:**
`.google-stitch/prompts/login-form-v1.md`

---

## Example 10 — Language Localization

**Input:**
> Convert the login form prompt to Spanish

**Optimized Prompt:**
> Design a login form for a web app with Spanish text.
> Include: centered card with logo, email input field labeled "Correo electrónico", password input field labeled "Contraseña", "Iniciar sesión" button, "¿Olvidaste tu contraseña?" link below, "¿No tienes cuenta? Regístrate" link at bottom.
> Style: clean, modern, centered layout, Ocean Blue (#005A8D) primary button, rounded inputs, subtle card shadow.
> Optimize for mobile-first, full keyboard navigation.

**File Created:**
`.google-stitch/prompts/login-form-es-v1.md`

**Note:** Technical UI terms (button, input field, card) remain in English—only user-facing labels are translated.

---

## Example 11 — Image Modification

**Input (Scenario 1):**
> On the dashboard, make the hero image smaller and add a subtle gradient overlay to match the blue theme

**Optimized Prompt:**
> On the dashboard screen, resize the hero image to 60% width, add a subtle blue-to-transparent gradient overlay (Ocean Blue #005A8D at 20% opacity).
> Maintain existing layout proportions for other elements.
> Ensure image coordinates with the deep blue accent theme and modern aesthetic.

**File Updated:**
`.google-stitch/prompts/dashboard-v2.md`

---

**Input (Scenario 2):**
> Replace all profile thumbnails with rounded versions and add a blue border

**Optimized Prompt:**
> Update all user profile thumbnails to circular shape (border-radius: 50%).
> Apply consistent 2px border in Ocean Blue (#005A8D).
> Maintain existing thumbnail sizes and grid layout.

**File Updated:**
`.google-stitch/prompts/user-grid-v2.md`

**Note:** Image modifications should be specific (which images), precise (what changes), and coordinated with the overall theme.

---

## Example 12 — Minimal Input (High-Level)

**Input (very minimal):**
> A professional project management dashboard

**Optimized Prompt:**
> Design a responsive web dashboard for a professional project management tool.
> Include: left sidebar with navigation (Projects, Tasks, Team, Reports), top header with search and notifications, main area with project cards showing status and progress bars, task timeline chart below cards.
> Style: clean, professional, neutral gray background with blue accents, modern sans-serif typography, organized grid layout, subtle shadows.
> Optimize for desktop first, mobile-responsive single-column layout.

**Note:** Stitch accepts minimal inputs—adjectives like "professional" guide visual direction when specific details aren't provided. The skill infers common patterns for the app type.

**File Created:**
`.google-stitch/prompts/pm-dashboard-v1.md`

---

## Example 13 — Micro-Refinements (Small Changes)

**Input (Scenario 1):**
> Change the primary button color to green

**Optimized Prompt:**
> Update the primary "Sign In" button color to Forest Green (#228B22).
> Maintain all other colors, layout, and typography.

**File Updated:**
`.google-stitch/prompts/login-form-v2.md`

---

**Input (Scenario 2):**
> Move the search bar to the left side of the header

**Optimized Prompt:**
> Reposition the search bar to the left side of the header, before the logo.
> Keep all other header elements (notifications, user avatar) in current positions.

**File Updated:**
`.google-stitch/prompts/header-v3.md`

**Note:** Micro-refinements focus on single, specific changes while explicitly maintaining all other existing elements.
