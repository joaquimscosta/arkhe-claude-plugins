---
description: >
  Comprehensive verification of completed work with confidence-based issue filtering.
  Use when finishing implementation, before committing, after fixing bugs, or to validate
  feature completeness. Reviews completeness, correctness, edge cases, and alignment.
argument-hint: "[optional: specific aspect to verify]"
---

# Double-Check Verification

Ultrathink!

Systematically verify the work just completed to ensure quality and completeness.

**Focus area (if specified):** $ARGUMENTS

---

## Pre-Verification Scope Detection

Before verifying, establish what was completed:

1. **Check git status**: !`git status --short`
2. **Check staged changes**: !`git diff --cached --stat`
3. **Check unstaged changes**: !`git diff --stat`
4. **Check recent commits** (if no uncommitted changes): !`git log -3 --oneline`
5. **Check todo list**: Review any in-progress or recently completed todos

**Scope Summary**: Summarize what will be verified (files changed, features affected).
If the user specified a focus area, prioritize that scope.

---

## Verification Process

### Step 1: Goal Clarity

Before checking anything, establish:
- What was the original goal or request?
- What does "complete" mean for this task?
- What are the success criteria?

### Step 2: Multi-Angle Review

Verify from these angles:

**Completeness Check**
- Does the implementation address all requirements?
- Are there any TODO comments or placeholder code left?
- Were all requested changes made?

**Correctness Check**
- Does the logic handle expected inputs correctly?
- Are there edge cases that could cause failures?
- Do error paths behave appropriately?

**Integration Check**
- Does this work with existing code?
- Are there breaking changes to existing functionality?
- Do imports, exports, and dependencies align?

**Quality Check**
- Is the code readable and maintainable?
- Does it follow project conventions (check CLAUDE.md)?
- Are there obvious simplifications or improvements?

### Step 2.5: Confidence Scoring

Rate each potential issue on a 0-100 scale:

| Score | Meaning |
|-------|---------|
| 0-25  | Likely false positive or pre-existing issue |
| 26-50 | Possible issue, but may be a nitpick |
| 51-75 | Real issue, but may not happen often in practice |
| 76-89 | Verified real issue that will impact functionality |
| 90-100| Confirmed critical issue requiring immediate fix |

**Only report issues with confidence >= 75.**

### Step 3: Issue Summary

If issues found:
- List each issue with severity (critical/moderate/minor)
- Provide specific fix recommendations
- Prioritize what must be fixed vs. nice-to-have

If no issues found:
- Confirm verification passed
- Note any caveats or assumptions made

---

## Output Format

### Verification Results

**Scope Verified:** [files/features reviewed]

**Goal:** [restate the original goal]

**Status:** [PASSED | ISSUES FOUND]

**Verification Summary:**

| Angle | Status | Notes |
|-------|--------|-------|
| Completeness | :white_check_mark:/:x: | ... |
| Correctness | :white_check_mark:/:x: | ... |
| Integration | :white_check_mark:/:x: | ... |
| Quality | :white_check_mark:/:x: | ... |

**Issues (if any):**

| Severity | Confidence | Issue | Fix Recommendation |
|----------|------------|-------|-------------------|
| Critical | 95% | [description] | [fix] |
| Moderate | 82% | [description] | [fix] |

**Conclusion:**
[Summary and recommendation to proceed or revise]
