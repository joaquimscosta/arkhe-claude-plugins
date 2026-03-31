# SDLC Develop: Multi-Agent Pattern Integration

**Date:** 2026-03-31
**Status:** Draft
**Scope:** Integrate 5 multi-agent orchestration patterns into the `sdlc-develop` skill

---

## Summary

Integrate 5 patterns from the multi-agent orchestration research (`docs/research/multi-agent-patterns-*.md`) into the `sdlc-develop` skill to improve implementation quality, reduce prescriptive token cost, and enable targeted review. The patterns are: Backpressure over Prescription, Confession Pattern, Critic-Actor per Wave, Fresh Context per Wave, and Persistent Memory.

## Motivation

The `sdlc-develop` skill already uses Pipeline, Specification-First, Human-in-the-Loop, Task Tracking, Supervisor-Worker, and Parallel Execution patterns effectively. However, Phase 4 (Implementation) is 389 lines of prescriptive step-by-step instructions, code review happens only after ALL waves complete (issues compound), builders have no mechanism to flag their own uncertainties, context drifts within long sessions, and project learnings are lost between features.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Post-wave steps 4b-4d | Collapse into per-wave critic | Per-wave critic makes post-implementation review redundant |
| Confession storage | wave-context.md | Natural fit — wave-context already captures per-wave state |
| Critic retry bound | 1 retry | Research recommendation: "after 1 rejection, approve with notes" |
| Persistent memory | Auto-evaluate, ask to save | Respects memory guidelines (only non-obvious, non-derivable info) |
| Quality gates | 6 gates | Task completion, file evidence, tests green, no placeholders, acceptance criteria, confessions recorded |
| Phase 4 structure | Full restructure (Approach B) | Clean numbered steps, each pattern visible, consistent with other phases |

---

## Pattern 1: Backpressure Over Prescription

**Research reference:** "Don't prescribe how; create gates that reject bad work."

**What changes:** Step 4.1c replaces the current prescriptive implementation guidelines (one task at a time, TDD when applicable, commit frequently, preserve existing code, etc.) with 6 quality gates.

### Quality Gates

All 6 gates must pass before proceeding from implementation to confession recording:

| # | Gate | Check Method | Pass Criteria |
|---|------|-------------|---------------|
| 1 | Task completion | Read tasks.md | All wave tasks have `Status: COMPLETED` |
| 2 | File evidence | `git diff --stat` | Changed files match task `Files` metadata |
| 3 | Tests green | Run test suite (auto-detect framework) | All tests pass |
| 4 | No placeholders | Grep changed files | Zero `TODO`/`FIXME`/`NotImplementedError` matches |
| 5 | Acceptance criteria | Map criteria to code | Each criterion in tasks.md has `file:line` evidence |
| 6 | Confessions recorded | Check wave-context.md | Each completed task has a confession block |

**Gate failure handling:** If a gate fails, fix and re-check. Gates are checked once after all wave tasks are implemented, not per-task.

**Builder freedom:** The builder chooses how to implement — one task at a time or in batches, TDD or implementation-first, frequent commits or one commit per wave. The gates enforce the outcome.

**Stitch UI integration:** The conditional Stitch/design-asset workflow from current Phase 4 stays as a conditional section within Step 4.1c. It only loads when `plan.md` has a `## Design Assets` section with status other than "Skipped". No changes to its behavior — it just lives inside the new step structure.

**`--validate` flag:** Currently triggers the removed Step 4c (opus deep validation). New behavior: `--validate` upgrades the wave critic agent (Step 4.1e) from sonnet to opus for deeper review. This preserves the flag's semantics (more thorough review) without adding a separate post-hoc step.

**Token impact:** Reduces PHASE-4-IMPLEMENTATION.md from ~389 lines to ~150 lines by removing prescriptive how-to guidelines.

---

## Pattern 2: Confession Pattern

**Research reference:** "The builder records shortcuts, assumptions, uncertainties. A separate auditor reads these confessions and calibrates trust."

**What changes:** New Step 4.1d (Confession Recording) added after implementation, before the wave critic.

### Confession Format

For each completed task in the wave, the builder writes a confession block to `{spec_path}/wave-{N}-context.md` under `## Confessions`:

```markdown
### T-{XX}: {Task Title}
- **Shortcuts**: [What was done expediently vs. ideally, or "None"]
- **Assumptions**: [Unverified beliefs the code depends on, or "None"]
- **Uncertainties**: [Areas where confidence is low, or "None"]
- **Deviations**: [Where implementation diverged from plan.md, or "None"]
```

### How Confessions Flow

1. Builder implements wave tasks (Step 4.1c)
2. Builder records confessions (Step 4.1d)
3. Wave critic reads confessions and focuses review on flagged areas (Step 4.1e)
4. Confessions persist in wave-context.md for cross-session visibility
5. Final gate (Step 4.2) displays confession summaries from all waves

### Incentive Design

The builder is rewarded for honesty, not for looking good. The prompt explicitly states: "The confessor is rewarded for surfacing problems, not for appearing competent." This is critical — without this framing, the builder will minimize confessions.

---

## Pattern 3: Critic-Actor per Wave

**Research reference:** "One agent proposes work, another critiques it. After 1 rejection, approve with notes rather than rejecting again."

**What changes:** New Step 4.1e (Wave Critic) added after confession recording. Replaces the old Steps 4b (Quick Validation), 4c (Deep Validation), and 4d (Code Review) which ran only after ALL waves completed.

### Wave Critic Agent

Launch a sonnet agent with:

**Input:**
- Git diff for this wave (`git diff` since wave start)
- Confessions from Step 4.1d
- Quality gate results from Step 4.1c
- Relevant FR-XXX requirements from spec.md

**Instructions:**
```
Review this wave's implementation. Focus your review on:
1. Confessed weak spots (shortcuts, assumptions, uncertainties)
2. Quality gate results (any gates that required re-checks)
3. Cross-task interactions within this wave

Return: PASS or ISSUES (list with file:line refs and severity).

Exclude: subjective style preferences, speculative issues, items that
linters/tests would catch (quality gates already handle those).
```

### Bounded Retry

- **If PASS:** Proceed to wave checkpoint (Step 4.1f)
- **If ISSUES:** Builder fixes the listed issues, then critic re-reviews
- **After 1 rejection:** Approve with notes rather than rejecting again. Record notes in wave-context.md under `## Wave Critic Result`

### Why This Replaces Steps 4b-4d

| Old Step | Why Removed | Replaced By |
|----------|-------------|-------------|
| 4b (Quick Validation) | Quality gates (Step 4.1c) cover the same checks | Gate 1-4 |
| 4c (Deep Validation) | Per-wave critic is more targeted than post-hoc opus review | Wave critic |
| 4d (Code Review) | Per-wave review catches issues before they compound | Wave critic |

Step 4.2 (Quality & Completion Gate) remains as the final mandatory Tier 1 gate. It aggregates per-wave critic results and confession summaries rather than running its own reviews.

---

## Pattern 4: Fresh Context per Wave

**Research reference:** "Each iteration starts with a clean slate. Re-read specs, plans, and code from disk rather than relying on accumulated context."

**What changes:** New Step 4.1a (Context Refresh) at the start of every wave, including Wave 1.

### Context Refresh Protocol

Before starting any wave, read from disk:

1. `{spec_path}/spec.md` — Extract FR-XXX requirements relevant to this wave's tasks
2. `{spec_path}/plan.md` — Extract architecture decisions and key patterns to follow
3. `{spec_path}/tasks.md` — Verify current Status fields, load this wave's task details
4. If `wave-{N-1}-context.md` exists — Read previous wave's summary, confessions, and critic notes

### Cost-Benefit

- **Cost:** 4 file reads per wave (~200-500 tokens each)
- **Benefit:** Prevents context drift across waves. Ensures the builder works from the spec, not from a degraded memory of the spec. Especially valuable when sessions run 3+ waves.

### Within-Session vs. Cross-Session

- **Cross-session:** Already handled by wave-context.md files and RESUME_MODE detection (no change needed)
- **Within-session:** This is the new addition — each wave reads from disk even if previous waves ran in the same session

---

## Pattern 5: Persistent Memory

**Research reference:** "Agents record learnings that persist across sessions. Future agents can benefit from past work."

**What changes:** New Step 4 in Phase 5 (Summary), after the completion summary.

### Learning Evaluation

After completing the feature summary, auto-evaluate whether discoveries should persist:

**Candidate sources:**
- Architecture trade-offs from Phase 2 (why option A over B)
- Gotchas discovered during implementation (framework limitations, API quirks)
- Domain knowledge from research phase (if Step 2a-res was conducted)
- Integration patterns established between existing and new code

**Filter criteria (only save if):**
- Not derivable from reading the code or git history
- Would be useful for future features in this project
- Represents a decision with non-obvious reasoning

### User Approval

If candidates found, use AskUserQuestion:
- **header:** "Project Learnings"
- **question:** "{N} learnings identified. Save to project memory?"
- **options:**
  - "Save all" — Write each as a project-type memory file
  - "Review first" — Show candidates, let user select
  - "Skip" — Don't save

**Gate: Tier 3** (auto-skip with `--auto`; no memories saved in autonomous mode)

### Memory Format

Each saved learning follows the auto-memory format:

```markdown
---
name: {feature-slug}-{learning-topic}
description: {one-line description}
type: project
---

{Learning content}

**Why:** {motivation or constraint}
**How to apply:** {when this should shape future decisions}
```

---

## File Change Summary

### PHASE-4-IMPLEMENTATION.md (Major Rewrite)

**Remove:** Current Steps 4a.1, 4a.2, 4a.3 (prescriptive), Steps 4b, 4c, 4d (collapsed)
**Add:** Steps 4.0 (unchanged), 4.1a-f (wave loop with patterns), 4.2 (final gate)
**Estimated size:** ~150 lines (down from 389)

### PHASE-5-SUMMARY.md (Addition)

**Add:** Step 4 — Save Project Learnings (Persistent Memory pattern)
**Estimated impact:** ~30 lines added

### GATES.md (Update)

**Update:** Gate mapping table to reflect new step numbers
**Add:** Wave Critic gate (Step 4.1e, Tier 2, bounded 1 retry)
**Remove:** Entries for Steps 4b, 4c, 4d

### wave-context.md.template (Update)

**Add:** `## Confessions` section (per-task confession blocks)
**Add:** `## Wave Critic Result` section (verdict, notes, fix cycles)

### WORKFLOW.md (Update)

**Update:** Execution flow diagram to show new Phase 4 structure (4.0 → 4.1a-f → 4.2)

### SKILL.md (Minor Updates)

**Update:** Checkpoints section (reference Step 4.2 instead of 4e)
**Update:** Model Tiers table (remove 4b-4d rows, add wave critic row)
**Update:** Core Principles (mention the 5 patterns)
**No structural changes** — SKILL.md remains the lightweight hub

### Files NOT Changed

- PHASE-0-DISCOVERY.md
- PHASE-1-REQUIREMENTS.md
- PHASE-2-ARCHITECTURE.md
- PHASE-3-WORKSTREAMS.md
- VERIFY-ARCH.md
- VERIFY-IMPL.md
- EXAMPLES.md
- TROUBLESHOOTING.md
- All templates except wave-context.md.template
- scripts/next_spec_number.py

---

## Pattern Composition

The 5 new patterns compose with the existing patterns to create two recognized compositions from the research docs:

| Composition | Patterns |
|-------------|----------|
| **Feature Development** | Specification-First + Pipeline + Critic-Actor + Confidence-Gated Completion |
| **Autonomous Coding** | Fresh Context + Persistent Memory + Task Tracking + Backpressure |

sdlc-develop after this change uses both compositions, with the Confession Pattern as the glue connecting the builder (Backpressure) to the critic (Critic-Actor).

### Full Pattern Inventory (Post-Integration)

| Pattern | Phase | Status |
|---------|-------|--------|
| Pipeline | 0→1→2→3→4→5 | Existing |
| Specification-First | 1-2 | Existing |
| Human-in-the-Loop | All (three-tier gates) | Existing |
| Task Tracking | 3-4 (tasks.md, Status fields) | Existing |
| Supervisor-Worker | 2 (explorer/architect agents) | Existing |
| Parallel Execution | 2 (parallel agent launches) | Existing |
| **Backpressure** | **4.1c (quality gates)** | **New** |
| **Confession Pattern** | **4.1d (confession recording)** | **New** |
| **Critic-Actor** | **4.1e (wave critic)** | **New** |
| **Fresh Context** | **4.1a (context refresh)** | **New** |
| **Persistent Memory** | **5.4 (save learnings)** | **New** |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Builder writes empty/minimal confessions | Prompt explicitly rewards honesty; Gate 6 requires confessions exist |
| Wave critic loops forever | Bounded to 1 retry; approve with notes after that |
| Fresh context reads add latency | 4 small file reads (~1-2 seconds total) — negligible vs. implementation time |
| Memory system spam | Auto-evaluate + user approval gate; auto-skip in `--auto` mode |
| Step renumbering breaks references | Update all references in GATES.md, WORKFLOW.md, SKILL.md (tracked in file change summary) |
