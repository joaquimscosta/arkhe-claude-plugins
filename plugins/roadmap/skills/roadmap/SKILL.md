---
name: roadmap
description: >
  Synthesize project documentation and codebase into comprehensive roadmap status, gaps analysis,
  and blockers. Use when assessing project health, identifying blockers, tracking progress,
  comparing plan vs reality, documenting risks, or planning next milestones.
  Triggers: "roadmap", "project status", "blockers", "risks", "progress", "next milestone",
  "gaps", "what's done".
argument-hint: "[--deep] [status [--focus=<gaps|blockers|risks|specs>] | update [--dry-run] [--incremental] | next [--force] | plan [scaffold|show|sync]]"
allowed-tools: Read, Glob, Grep, Write, Bash
---

# Roadmap Analyst

Synthesize project documentation and codebase state into actionable status reports.

## Context Discovery

Run the shared context discovery protocol in [CONTEXT_DISCOVERY.md](../../references/CONTEXT_DISCOVERY.md). Use the scan depth appropriate for the mode:

| Mode | Required Phases | Scan Depth |
|------|----------------|------------|
| `plan show` | 1 (config) | None — reads `{plan_file}` directly |
| `next` (cached) | 1 (config) | None — reads cached file + git drift check |
| `update --dry-run` | 1, 5, 7 | Medium — config, docs, codebase scan (no write) |
| `status` (with or without `--focus`) | 1-7 | Thorough — full protocol |
| `next` (recalc) | 1-7 | Thorough — full protocol |
| `update`, `update --incremental` | 1-7 | Thorough — full protocol |
| `plan scaffold`, `plan sync` | 1-7 | Thorough — full protocol |

Store results for analysis below.

## Arguments

Parse from `$ARGUMENTS`:

| Mode | Description |
|------|-------------|
| `status` | Overall dashboard — modules, phases, completion + drift detection. Renders Gaps, Blockers, Risks, and Specs as inline sections. Add `--focus=<gaps\|blockers\|risks\|specs>` to render only one section |
| `update` | Git-aware status doc update (Phase A: what shipped + Phase B: full scan + auto-chains `plan sync`). Add `--dry-run` to preview the diff without writing. Add `--incremental` for post-sprint targeted edits only |
| `next` | Prioritized recommendations with caching and smart merge. Saves to `{output_dir}/next-actions.md`. Returns cached results if <3 feat/fix commits and status doc unchanged; otherwise merge-based recalculation that preserves uncompleted items and user additions. Add `--force` to recalculate (still merges; delete file manually for clean slate) |
| `plan` | Project roadmap lifecycle — `scaffold` (create), `show` (read), `sync` (update). Defaults to `show` if roadmap exists, `scaffold` if not |
| _(none)_ | Defaults to `status`. Footer suggests `/roadmap next` if next-actions.md is stale |

## Module Maturity Scale

Rate each module using the shared vocabulary in [MATURITY_SCALE.md](../../references/MATURITY_SCALE.md).

## Mode Execution

### `status`

Produce a status dashboard with module maturity table, then detail: What's working, What's planned, What's missing.

After producing the dashboard, render four focus sections inline:
- **Gaps** — open/closed/in-progress with evidence (cross-references all gap analysis documents)
- **Blockers** — blocking chain analysis with critical path; for each blocker: what it blocks, owner, what's needed
- **Risks** — risk register with Likelihood (H/M/L) x Impact (H/M/L) scoring and suggested mitigations
- **Specs** — spec pipeline verification against codebase evidence (not just what the spec says). If `{plan_file}` exists, cross-reference to show which phase each spec belongs to and flag unlinked specs

With `--focus=<gaps|blockers|risks|specs>`, render only that section (skip the dashboard preamble and other sections).

After producing the dashboard, run drift detection: if 3+ feat/fix commits exist since last `{status_file}` update, append a staleness notice suggesting `/roadmap update`.

### `update`

Git-aware status document update. See [WORKFLOW.md](WORKFLOW.md) § `update` for the full Phase A (git history scan) + Phase B (codebase scan + write) protocol.

Key behaviors:
- Shows "What Shipped" summary before scanning
- Diff preview with `+`/`-`/`~` markers, requires confirmation before writing
- Checks CHANGELOG.md for gaps (offers to add entries)
- Auto-chains into `plan sync` when phase/spec status changes detected
- Next `/roadmap next` will detect status doc changes and trigger merge-based recalculation (preserves uncompleted items)
- `--dry-run` variant: runs Phase A + Phase B but stops at the diff preview without prompting or writing — read-only comparison of status doc vs current codebase
- `--incremental` variant: surgical targeted edits only (skips Phase B full scan)

### `next`

Prioritized recommendations with git-aware caching and smart merge. See [WORKFLOW.md](WORKFLOW.md) § `next` for the full merge protocol.

Key behaviors:
- Saves recommendations to `{output_dir}/next-actions.md`
- Returns cached results if <3 feat/fix commits and status doc unchanged since last calculation
- On recalculation, merges new recommendations with existing items — preserves uncompleted items, removes items with completion evidence
- User-added items in `### User-Added` section always preserved across recalculations
- Shows merge diff preview with `+`/`-`/`~`/`=` markers before writing (confirmation required)
- Combines: unclosed gaps, unstarted specs, maturity imbalances, plan backlog themes

### `plan`

Consolidated project roadmap lifecycle. Read `plan_file` from `.arkhe.yaml` (default: `docs/PROJECT-ROADMAP.md`).

| Subcommand | Description |
|------------|-------------|
| `scaffold` | Create initial PROJECT-ROADMAP.md using hybrid linking algorithm — see [WORKFLOW.md](WORKFLOW.md) § `plan scaffold` |
| `show` | Read-only summary with timeline, progress stats, active phases, drift detection |
| `sync` | Git-aware update with auto-detected links — see [WORKFLOW.md](WORKFLOW.md) § `plan sync` |
| _(none)_ | Default to `show` if roadmap exists; `scaffold` if not |

**Legacy file fallback**: If `{plan_file}` is unset in `.arkhe.yaml` and `docs/PROJECT-PLAN.md` exists while `docs/PROJECT-ROADMAP.md` does not, treat the legacy path as `{plan_file}` for this run and emit a one-time migration notice suggesting `mv docs/PROJECT-PLAN.md docs/PROJECT-ROADMAP.md` (or pinning `plan_file` in `.arkhe.yaml`).

## Output Rules

- **Evidence-based** — every claim backed by a file path, migration, or component
- **Tabular** — use tables for at-a-glance status; prose for analysis
- **Actionable** — always end with recommended next actions
- **Honest** — distinguish between "verified working" and "files exist but untested"
- `update` and `plan scaffold`/`plan sync` show unified diff preview and require explicit confirmation before writing
- `--deep` reports are saved by default to `{output_dir}/reports/`; user can opt out

## Deep Mode (`--deep`)

When `$ARGUMENTS` contains `--deep`, run the full multi-agent pipeline with **parallel cross-perspective analysis**. Three Sonnet agents analyze the project simultaneously from PM, Architect, and Roadmap perspectives, then a synthesizer merges findings and surfaces contradictions.

See [WORKFLOW.md](WORKFLOW.md) § Deep Pipeline for the 5-phase execution protocol.

Phase 4 produces a **Confidence Scoreboard** table with independent scores per finding. Findings below 70 are removed; 70-89 are tagged `[NEEDS VALIDATION]`.

**Patterns applied**: Pipeline, Supervisor-Worker, Parallel Execution, Confession, Confidence-Gated Completion.

## Lane Discipline

See the Roadmap Analyst section of [LANE_DISCIPLINE.md](../../references/LANE_DISCIPLINE.md). Stay in your lane.

## References

- [WORKFLOW.md](WORKFLOW.md) — Detailed discovery and mode workflows
- [EXAMPLES.md](EXAMPLES.md) — Usage examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues and fixes
