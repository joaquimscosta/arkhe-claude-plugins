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

