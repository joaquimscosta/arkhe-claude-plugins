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

## Quick Start
1. **Collect context** – accept natural language, specs, or referenced files describing the screen/app.
2. **Parse essentials** – identify app type, screen focus, layout elements, and visual cues.
3. **Detect split points** – analyze if input contains multiple screens or distinct intents (>2). Apply smart defaults: split if >2 screens/intents, else combine. Users can request regeneration with different approach.
4. **Filter aggressively** – strip ALL non-UI concerns (backend, auth, APIs, caching, error handling, performance metrics, code-level specs). Focus EXCLUSIVELY on visual layout, components, colors, typography, spacing, and interaction patterns.
5. **Condense** – rewrite into one atomic Stitch directive using "Design/Create/Add…" phrasing.
6. **Structure output** – follow the Stitch prompt template (directive sentence → bullet list → 3–6 style cues → constraints). Do NOT use multi-section headings.
7. **Validate** – ensure UI nouns are present, word count <250, NO technical implementation terms, and format matches EXAMPLES.md structure before returning the prompt.

Use this Skill whenever users need Stitch-ready wording, prompt refinements, or style-consistent rewrites.

---

## File Output (.google-stitch/prompts)

Generate optimized prompts as standalone Markdown files:

1. **Component Slug**:
   - Derive from the prompt's header text
   - Lowercase, replace whitespace with hyphens
   - Strip non `a-z0-9-` characters, collapse duplicate hyphens, trim ends
   - Keep concise (prefer last 1-2 key words: "Content Engagement Toolbar" → "toolbar")
   - If <3 chars or ambiguous, ask user for descriptive slug

2. **Version**:
   - Scan `.google-stitch/prompts/{component-slug}-v*.md`
   - Find highest version number, increment
   - Start at v1 if no matches

3. **Filename**: `{component-slug}-v{version}.md`

4. **Directory**:
   - Resolve repo root via `git rev-parse --show-toplevel`
   - Create `{root}/.google-stitch/prompts/` if needed
   - Write Markdown prompt to file

5. **Report**:
   - After presenting prompt inline, append:
     `Saved to .google-stitch/prompts/{component-slug}-v{version}.md`

**Examples:**

Split scenario:
```
Input: "Cultural heritage page with toolbar and grid"
Prompts:
  1. Header: "Content Engagement Toolbar" → File: toolbar-v1.md
  2. Header: "Related Content Grid" → File: grid-v1.md
```

Single prompt:
```
Input: "Login form with email and password"
Prompt header: "Login Form" → File: login-form-v1.md
```

Iteration:
```
Updating "toolbar-v1.md"
New version → File: toolbar-v2.md
```

**Grouping split prompts:**
- Use git commits (prompts from same split committed together)
- Check file timestamps (`ls -lt` shows recent files)
- Rely on conversation context

Keep the storage single-file-per-prompt; no nested folders or additional metadata needed in this directory.

---

## Input Types

**Accepted**
- Natural-language descriptions (single screen or short flows)
- Markdown/YAML/JSON specs (`/specs/dashboard.md`)
- Revision directives ("move KPI cards above chart", "convert to French", "change button to green")
- References to uploaded wireframes or images
- Language conversion requests ("switch to Spanish", "German version")

**Input Detail Levels**

All detail levels are valid—Stitch infers patterns from minimal descriptions:

- **High-level** (minimal): "fitness tracker app", "professional project management dashboard"
- **Medium**: "fitness tracker with daily goals and progress charts"
- **Detailed**: Full component list with specific features and interactions

Use adjectives to convey vibe when details are sparse ("vibrant fitness app", "minimal meditation app").

---

## Workflow Overview

High-level loop: parse → condense → format → validate.  
Detailed branching logic, including cue extraction and revision handling, lives in [WORKFLOW.md](WORKFLOW.md).

---

## Output Structure

Prompts must follow the Stitch-friendly template:
- One-sentence description of the app/screen + primary intent.
- Bullet list (3–6 items) covering layout, components, or flows.
- Visual style cues (palette, typography, density, tone).
- Optional behavior/constraint reminders (responsiveness, export format).

Reference [templates/authoring-stitch-prompts-template.md](templates/authoring-stitch-prompts-template.md) for wording patterns.

---

## Examples

Representative before/after samples (SaaS dashboard, banking app, iterative edits, spec conversions) are in [EXAMPLES.md](EXAMPLES.md). Use them to mirror tone and formatting; keep this file lean by not re-embedding the full transcripts here.

---

## Implementation Notes

* Keep SKILL.md under 500 lines; detailed prompt transformation logic can go in `REFERENCE.md` or `templates/authoring-stitch-prompts-template.md`.
* Use concise, declarative language.
* Avoid narrative, meta, or conversational phrasing in outputs.
* Always output one atomic, Stitch-compatible prompt per request.

---

## Common Issues

- **Prompts too verbose** – Re-run formatting with the template and trim narration. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)#L1 for guidance.
- **Missing style cues** – Derive palette/typography keywords from user input or prior session context before finalizing. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)#L25.
- **Multi-goal briefs** – Split into multiple prompts; re-emphasize Stitch’s atomic focus. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)#L43.

---

## Reference Files

For advanced usage:

* [REFERENCE.md](REFERENCE.md) — Overview of Stitch best practices
* [EXAMPLES.md](EXAMPLES.md) — Sample transformations
* [WORKFLOW.md](WORKFLOW.md) — Detailed processing loop
* [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Error-handling guidance
* [templates/authoring-stitch-prompts-template.md](templates/authoring-stitch-prompts-template.md) — Output format template

---

## Version History

* v1.0.0 (2025-11-10): Initial release — authoring assistant for Stitch prompt optimization.
