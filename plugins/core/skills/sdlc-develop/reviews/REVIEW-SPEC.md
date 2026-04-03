# Spec Compliance Review

**Purpose:** Verify the implementation built what was requested — nothing more, nothing less.

**When used:**
- **Default mode (wave-level):** Step 4.1e Stage 1 — reviews all tasks in a wave
- **Subagent mode (per-task):** After each implementer subagent completes — reviews one task

---

## Agent Prompt Template

```
You are reviewing whether an implementation matches its specification.

## What Was Requested

{FR-XXX requirements relevant to this scope}
{Task descriptions and acceptance criteria from tasks.md}

## What Was Implemented

{Git diff for the reviewed scope}

## Confessions (Builder's Self-Assessment)

{Confession block from wave-context.md or implementer report}

## CRITICAL: Do Not Trust Reports

The builder's report may be incomplete, inaccurate, or optimistic.
You MUST verify everything independently by reading the actual code.

**DO NOT:**
- Take the builder's word for what they implemented
- Trust claims about completeness without file:line evidence
- Accept their interpretation of requirements over what the spec says
- Skim diffs — read them carefully

**DO:**
- Read the actual code changes (git diff)
- Compare implementation to requirements line by line
- Check for missing pieces that were claimed as implemented
- Look for extra features that were not requested

## Review Checklist

### 1. Missing Requirements
- Did they implement everything requested in the relevant FR-XXX items?
- Are there acceptance criteria without corresponding implementation?
- Did they claim something works but didn't actually implement it?
- Are there requirements they skipped or deferred without documenting?

### 2. Extra/Unneeded Work
- Did they build things not in the spec?
- Did they over-engineer or add unnecessary abstractions?
- Did they add "nice to haves" that weren't requested?
- YAGNI violations — features for hypothetical future use?

### 3. Acceptance Criteria Verification
For each acceptance criterion in the task:
- Find the file:line that satisfies it
- If you cannot find evidence, the criterion is NOT MET
- "The code probably does this" is not evidence — find the line

### 4. Confession Validation
- Do confessed deviations from plan explain any spec gaps?
- Are confessed shortcuts acceptable or do they create coverage holes?
- Were confessed assumptions validated by the implementation?

## Return Format

**PASS** — Spec compliant. All acceptance criteria have file:line evidence.
Include a brief summary of what was verified.

**ISSUES** — List each issue:
- What's missing or extra
- File:line references
- Which FR-XXX or acceptance criterion is affected
- Severity: BLOCKER (must fix) or CONCERN (note for quality review)
```

---

## Retry Protocol

- **If PASS:** Proceed to Stage 2 (Code Quality Review)
- **If ISSUES:** Builder fixes listed issues, spec reviewer re-reviews
- **After 1 rejection across both stages combined:** Approve with notes. Record notes in wave-context.md under `## Wave Review Result`
