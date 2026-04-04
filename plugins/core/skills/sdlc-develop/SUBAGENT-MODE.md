# Subagent Mode — Per-Task Execution Protocol

**Activates when:** `--subagent` flag is set in the `/core:develop` command.

**Default behavior (no flag):** Wave-based execution remains unchanged. This document only applies when `--subagent` is active.

---

## Overview

Instead of the orchestrator implementing all tasks in a wave, dispatch a **fresh subagent per task**. Each subagent gets isolated context and implements exactly one task.

**Why subagents:**
- **Fresh context** per task prevents context pollution across tasks
- **Escalation** — subagents can report BLOCKED/NEEDS_CONTEXT instead of silently producing bad work
- **Per-task review** — two-stage review after each task catches issues earlier
- **Model flexibility** — choose the right model tier per task complexity

---

## Execution Flow (per task within a wave)

### 1. Prepare Task Context

Assemble the context package for the implementer subagent:

- **Full task text** from tasks.md (paste into prompt, don't make subagent read the file)
- **Relevant FR-XXX requirements** from spec.md
- **Architecture decisions** from plan.md relevant to this task
- **Previous wave context** (if Wave N > 1) from wave-{N-1}-context.md
- **Files to modify** (from task metadata)
- **Verification command** (from task's `#### Verification` section, if present)

### 2. Dispatch Implementer Subagent

Use the prompt template from [reviews/implementer-prompt.md](reviews/implementer-prompt.md).

**Model selection:**

| Task Complexity | Model | When |
|----------------|-------|------|
| Simple (1-2 files, clear spec) | haiku | Isolated, mechanical changes |
| Integration (multi-file, dependencies) | sonnet | Cross-file coordination needed |
| Judgment (design decisions, broad context) | opus | Architecture-sensitive work |

### 3. Handle Implementer Status

| Status | Action |
|--------|--------|
| **DONE** | Proceed to per-task two-stage review (Step 4) |
| **DONE_WITH_CONCERNS** | Read concerns. If correctness/scope issue: address before review. If observational: note and proceed to review |
| **NEEDS_CONTEXT** | Provide missing context, re-dispatch subagent with additional information |
| **BLOCKED** | Assess the block: context problem (re-dispatch with more context), capability problem (re-dispatch with stronger model), task too large (break into sub-tasks), plan wrong (escalate to user) |

**Rules:**
- Never ignore an escalation or retry without changes
- Never re-dispatch with the same context that caused BLOCKED
- If 2 re-dispatches fail for the same task, escalate to user

### 4. Two-Stage Review (per task)

Same two-stage review as wave-level (Step 4.1e), but scoped to one task:

**Stage 1: Spec Compliance** — Read [reviews/REVIEW-SPEC.md](reviews/REVIEW-SPEC.md)
- Scoped to this task's requirements and acceptance criteria only
- 1 retry bound (shared across both stages for this task)

**Stage 2: Code Quality** — Read [reviews/REVIEW-QUALITY.md](reviews/REVIEW-QUALITY.md)
- Only runs after Stage 1 passes
- Scoped to this task's changed files only
- 1 retry bound (shared across both stages for this task)

**After 1 rejection across both stages:** Approve with notes. Record notes alongside the task's confession.

### 5. Record Task Confession

Same fields as wave-level confession (Step 4.1d), recorded per task:

```markdown
### T-{XX}: {Task Title}
- **Shortcuts**: [What was done expediently vs. ideally, or "None"]
- **Assumptions**: [Unverified beliefs the code depends on, or "None"]
- **Uncertainties**: [Areas where confidence is low, or "None"]
- **Deviations**: [Where implementation diverged from plan.md, or "None"]
```

**Source:** Confessions come from the implementer's report (required in the report format). Augment with any findings from the two-stage review.

### 6. Update Task Status

Mark task `COMPLETED` in tasks.md, record files changed.

---

## Wave-Level Aggregation

After all tasks in a wave complete in subagent mode:

1. **Skip Step 4.1e** — wave-level two-stage review is unnecessary (already done per task)
2. **Proceed to Step 4.1d** — aggregate all task confessions into `wave-{N}-context.md`
3. **Proceed to Step 4.1f** — wave checkpoint with aggregated metrics:
   - Tasks completed (count and IDs)
   - Aggregate review verdicts (per-task results)
   - Combined confession summary
   - Files changed across all tasks

---

## Combining with Other Flags

| Flag | Behavior with `--subagent` |
|------|---------------------------|
| `--auto` | Subagent mode with auto-approved Tier 2 gates. Tier 1 gates still block. |
| `--validate` | Upgrades review agents from sonnet to opus |
| `--plan-only` | No effect (subagent mode only applies to Phase 4) |
| `--phase=4` | Subagent mode active for Phase 4 execution |

---

## Backward Compatibility

- Default mode (no `--subagent`) is completely unchanged
- Wave-based execution and wave-level two-stage review remain the default
- Existing plans work with either mode — task structure is the same
- `--subagent` can be combined with any other flags
