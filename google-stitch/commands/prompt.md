---
description: Generate Google Stitch-ready prompts from briefs or spec files using the authoring skill
argument-hint: <brief or @/path/to/spec>
---

# Prompt Command

Convert natural-language descriptions, revision notes, or spec files into Stitch-optimized prompts in one step. This command guarantees the **`authoring-stitch-prompts`** Skill runs with your latest instructions.

## Usage

```bash
/prompt "Design a fintech dashboard with KPI cards and charts"
/prompt @specs/mobile-app.md
/prompt "Move the KPI cards above the chart and add a region filter"
```

Attach files or reference repository paths as needed; the Skill will read them before rewriting the prompt.

## Inputs

- `$ARGUMENTS`: user-provided brief, iteration note, or file path(s) to parse.
- Attached files (optional): wireframes, specs, or references to include during analysis.

## Behavior

1. Collects your text + referenced files.
2. Routes everything to the Google Stitch prompt skill.
3. The skill automatically applies smart defaults for split decisions (split if >2 screens/intents).
4. Returns a Stitch-ready prompt following the template (screen summary → layout bullets → style cues → constraints).
5. You can request regeneration with different approach if needed ("combine" or "split into N").

---

## Execution

- Treat `$ARGUMENTS` as the exact brief or spec path to optimize.
- Invoke the Skill tool with name **`authoring-stitch-prompts`** and arguments `$ARGUMENTS`.
- The Skill handles parsing, condensing, formatting, and validation. Reference `skills/authoring-stitch-prompts/SKILL.md` for the full workflow.
