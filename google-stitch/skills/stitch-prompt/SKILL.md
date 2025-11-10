name: stitch-prompt
description: >
  Converts natural-language descriptions or UI spec files into optimized Google Stitch prompts.
  Use when creating, refining, or validating design directives for Google Stitch.
  The Skill follows Stitch best practices—short, directive prompts focused on screens, structure,
  and visual hierarchy with clear UI vocabulary, concise style cues, and one primary intent per prompt.
  Trigger when the user wants to prepare or improve prompts for Stitch.
allowed-tools: Read, Grep, Write
---

# Stitch Prompt

## Quick Start
1. **Collect context** – accept natural language, specs, or referenced files describing the screen/app.
2. **Parse essentials** – identify app type, screen focus, layout elements, and visual cues.
3. **Condense** – rewrite into one atomic Stitch directive using “Design/Create/Add…” phrasing.
4. **Structure output** – follow the Stitch prompt template (screen summary → layout bullets → 3–6 style cues → constraints).
5. **Validate** – ensure UI nouns are present, word count <1,000, and tone stays directive before returning the prompt.

Use this Skill whenever users need Stitch-ready wording, prompt refinements, or style-consistent rewrites.

---

## Input Types

**Accepted**
- Natural-language descriptions (single screen or short flows)
- Markdown/YAML/JSON specs (`/specs/dashboard.md`)
- Revision directives (“move KPI cards above chart”)
- References to uploaded wireframes or images

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

Reference [templates/stitch-prompt-template.md](templates/stitch-prompt-template.md) for wording patterns.

---

## Examples

Representative before/after samples (SaaS dashboard, banking app, iterative edits, spec conversions) are in [EXAMPLES.md](EXAMPLES.md). Use them to mirror tone and formatting; keep this file lean by not re-embedding the full transcripts here.

---

## Implementation Notes

* Keep SKILL.md under 500 lines; detailed prompt transformation logic can go in `REFERENCE.md` or `templates/stitch-prompt-template.md`.
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
* [templates/stitch-prompt-template.md](templates/stitch-prompt-template.md) — Output format template

---

## Version History

* v1.0.0 (2025-11-10): Initial release — authoring assistant for Stitch prompt optimization.
