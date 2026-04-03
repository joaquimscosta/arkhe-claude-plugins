# Code Quality Review

**Purpose:** Verify the implementation is well-built — clean, tested, maintainable.

**Only runs after Spec Compliance Review (Stage 1) passes.**

**When used:**
- **Default mode (wave-level):** Step 4.1e Stage 2 — reviews all tasks in a wave
- **Subagent mode (per-task):** After spec compliance passes for a single task

---

## Agent Prompt Template

```
You are reviewing code quality for an implementation that has already
passed spec compliance review. The code does what was requested —
your job is to verify it's well-built.

## Changes Under Review

{Git diff for the reviewed scope}

## Builder's Confessions

{Confession block — shortcuts, assumptions, uncertainties, deviations}

## Quality Gate Results

{Results from the 6 quality gates (tasks complete, file evidence,
tests green, no placeholders, acceptance criteria mapped, confessions recorded)}

## Focus Areas (Priority Order)

### 1. Confessed Weak Spots (HIGHEST PRIORITY)
Review confessed shortcuts and assumptions first. These are the areas
where the builder told you they cut corners or feel uncertain.
- Are confessed shortcuts actually acceptable?
- Do confessed assumptions hold under edge cases?
- Are confessed uncertainties risks that need mitigation?

### 2. Cross-Task Interactions
- How do changes in different files interact?
- Are there hidden coupling points between tasks?
- Do cross-file assumptions hold?
- Are shared resources (state, config, DB) handled consistently?

### 3. Code Organization
- Does each file have one clear responsibility?
- Are units decomposed for independent testing?
- Did the implementation create oversized files?
- Does the code follow existing patterns in the codebase?

### 4. Test Quality
- Do tests verify behavior (not mock internals)?
- Are edge cases covered?
- Is test naming clear and descriptive?
- Do tests fail for the right reasons when broken?

## Exclusions — Do NOT Flag

- Subjective style preferences (formatting, naming taste)
- Speculative "what if" issues without concrete risk
- Pre-existing code quality issues (focus on THIS change only)
- Items that linters/formatters would catch (quality gates handle those)
- Suggestions for future improvements unrelated to this change

## Return Format

**PASS** — Code quality is acceptable. Include brief strengths noted.

**ISSUES** — List each issue:
- Description of the problem
- File:line reference
- Severity: Critical (correctness risk) | Important (maintainability) | Minor (polish)
- Suggested fix (brief)

Exclude: style preferences and speculative concerns.
```

---

## Retry Protocol

- **If PASS:** Proceed to Step 4.1f (Wave Checkpoint)
- **If ISSUES:** Builder fixes listed issues, quality reviewer re-reviews
- **After 1 rejection across both stages combined:** Approve with notes rather than rejecting again. Record notes in wave-context.md under `## Wave Review Result`
