---
name: authoring-stitch-prompts
description: >
  Converts natural-language descriptions or UI spec files into optimized Google Stitch prompts.
  Use when creating, refining, or validating design directives for Google Stitch.
  The Skill follows Stitch best practices—short, directive prompts focused on screens, structure,
  and visual hierarchy with clear UI vocabulary, concise style cues, and one primary intent per prompt.
  Trigger when the user wants to prepare or improve prompts for Stitch.
allowed-tools: Read, Grep, Write
---

# Authoring Stitch Prompts

## Purpose

This Skill transforms freeform natural language or structured UI specifications into Stitch-ready prompts that follow Google Stitch best practices for UI design generation.

Use when you want to:
- Turn product ideas or design specs into Stitch-compatible prompts.
- Refine verbose or unclear descriptions into concise, directive language.
- Align with Stitch's recommended atomic prompting style (one screen or major concern per prompt).
- Ensure outputs include concrete UI terminology and structured style cues.

---

## Input Types

**Accepted:**
- Natural-language descriptions (e.g., "A mobile app for course management with a dashboard and lessons page.")
- Design or feature specs (Markdown, YAML, JSON fragments describing screens, flows, or layout structure)
- Uploaded reference docs, e.g. `/specs/dashboard.md`

---

## Processing Workflow

1. **Parse Input Context**
   - Identify app type, primary screens, flows, and design goals.
   - Detect visual language, color, and typography hints.

2. **Condense & Reframe**
   - Rewrite long or mixed-content text into a focused, directive Stitch-style instruction.
   - Use Stitch’s preferred “Create / Add / Change / Replace” phrasing.
   - Keep one major concern per prompt.

3. **Structure Output**
   - Format using Stitch’s ideal prompting pattern:
     - concise description of app or screen
     - UI layout instructions
     - visual style and brand cues (3–6)
     - optional interactivity/flow hints
     - end with short constraints (e.g., responsiveness, export notes)

4. **Validate for Stitch Compatibility**
   - Verify that:
     - prompt length < 1,000 words
     - uses clear UI nouns (cards, nav, grid, modal, etc.)
     - avoids overlong narrative explanations
     - includes implementation awareness (componentization, layout, responsiveness)
   - Add missing elements as needed.

---

## Example Usage

**Example 1 — From natural text**

**Input:**
> We’re designing a learning dashboard for students. It should show progress, upcoming lessons, and achievements with a bright, playful style.

**Output (optimized Stitch prompt):**
> Design a responsive student learning dashboard web app.  
> Include:  
> - Header with student name and profile dropdown  
> - Section for “Current Progress” with a circular progress indicator  
> - List of upcoming lessons in cards  
> - Row of badges for achievements  
> Visual style: playful, colorful, rounded shapes, pastel palette, sans-serif typography, friendly illustrations.  
> Optimize for desktop, single-column layout on mobile.

---

**Example 2 — From spec file**

**Input (`specs/dashboard.md`):**
```markdown
# Dashboard
- Sidebar: navigation (Home, Reports, Settings)
- Header: search, user avatar
- Main: metrics cards + revenue chart
- Style: clean, enterprise, deep blue accents
````

**Output (optimized Stitch prompt):**

> Create a responsive web dashboard for business analytics.
> Include:
>
> * Left sidebar with navigation (Home, Reports, Settings)
> * Top header with search and user avatar
> * Main section with KPI cards (revenue, conversion rate, churn) and a line chart for revenue over time
>   Visual style: clean, minimal, enterprise-grade, deep blue accents, modern sans-serif font, subtle card shadows.
>   Optimize for desktop first.

---

## Implementation Notes

* Keep SKILL.md under 500 lines; detailed prompt transformation logic can go in `reference.md` or `templates/stitch-prompt-template.md`.
* Use concise, declarative language.
* Avoid narrative, meta, or conversational phrasing in outputs.
* Always output one atomic, Stitch-compatible prompt per request.

---

## Reference Files

For advanced usage:

* [reference.md](reference.md) — Overview of Stitch best practices
* [examples.md](examples.md) — Sample transformations
* [templates/stitch-prompt-template.md](templates/stitch-prompt-template.md) — Output format template

---

## Version History

* v1.0.0 (2025-11-10): Initial release — authoring assistant for Stitch prompt optimization.