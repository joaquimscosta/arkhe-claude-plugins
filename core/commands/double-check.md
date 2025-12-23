---
description: >
  Comprehensive verification of completed work from multiple angles with extended thinking.
  Reviews completeness, correctness, edge cases, and alignment with goals. Use after
  finishing implementation to ensure quality before committing.
argument-hint: "[optional: specific aspect to verify]"
---

# Double-Check Verification

Ultrathink!

Systematically verify the work just completed to ensure quality and completeness.

**Focus area (if specified):** $ARGUMENTS

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

**Goal:** [restate the original goal]

**Status:** [PASSED | ISSUES FOUND]

**Findings:**

| Angle | Status | Notes |
|-------|--------|-------|
| Completeness | pass/fail | ... |
| Correctness | pass/fail | ... |
| Integration | pass/fail | ... |
| Quality | pass/fail | ... |

**Issues (if any):**
1. [Issue description + fix recommendation]

**Conclusion:**
[Summary and recommendation to proceed or revise]
