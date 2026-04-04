# SDLC Develop — Execution Flow

Detailed execution flow diagram for the 6-phase SDLC pipeline.

```
START
  |
  +-- Parse arguments (flags, path references)
  +-- Detect mode (RESUME/PLAN/FULL)
  |
  +-- [RESUME] Load plan.md
  |   +-- Check for wave-*-context.md files
  |   +-- If wave context found -> Offer: All remaining / Choose tasks / Re-review / Restart
  |   |   +-- [All remaining] -> Skip Step 4.0, proceed to Step 4.1 (auto-proceeds)
  |   |   +-- [Choose tasks] -> Step 4.0 (Ticket Selection for remaining waves)
  |   +-- If no wave context -> Ask which phase -> Jump to phase
  |
  +-- [PLAN/FULL] Read PHASE-0-DISCOVERY.md
  |   +-- Execute Phase 0 -> Checkpoint
  |
  +-- Read PHASE-1-REQUIREMENTS.md
  |   +-- Execute Phase 1 -> Checkpoint
  |
  +-- Read PHASE-2-ARCHITECTURE.md
  |   +-- Step 2a-pre: Design Asset Generation (if UI work)
  |   +-- Step 2a: Codebase Exploration (2-3 code-explorer agents)
  |   +-- Step 2a-res: Domain Research (Tier 2 gate)
  |   +-- Step 2b: Architecture Design (2-3 code-architect agents)
  |   +-- Step 2c: Architecture Decision (Tier 1 - mandatory)
  |   +-- Step 2c-post: Save Architecture + research refs to plan.md
  |   +-- Step 2d: Save Artifacts (ADR, API, data models, conditional RFC)
  |   +-- Save plan -> [PLAN stops here]
  |
  +-- [FULL] Read PHASE-3-WORKSTREAMS.md
  |   +-- Execute Phase 3 -> Checkpoint
  |
  +-- Read PHASE-4-IMPLEMENTATION.md
  |   +-- Step 4.0: Ticket Selection (select/defer tasks)
  |   +-- For each wave (Step 4.1):
  |       +-- 4.1a: Context Refresh (re-read spec, plan, tasks from disk)
  |       +-- 4.1b: Wave Confirmation
  |       +-- 4.1c: Implementation (evidence-based quality gates, TDD recommended)
  |       |       +-- [--subagent] Per-task: dispatch implementer -> two-stage review -> confession
  |       +-- 4.1d: Confession Recording
  |       +-- 4.1e: Two-Stage Wave Review (skip if --subagent, already done per task)
  |       |       +-- Stage 1: Spec Compliance (pass required)
  |       |       +-- Stage 2: Code Quality (only if Stage 1 passes)
  |       +-- 4.1f: Wave Checkpoint -> CONTINUE or STOP
  |           +-- [CONTINUE] -> Next wave (4.1a)
  |           +-- [STOP] -> Save context, exit Phase 4
  |   +-- Step 4.2: Quality & Completion Gate (Tier 1 - mandatory, evidence-based)
  |
  +-- Read PHASE-5-SUMMARY.md
      +-- Execute Phase 5 -> Complete
```

## Phase Dependencies

Each phase loads its file only when entered. See the phase routing table in SKILL.md for file paths and goals.

## Checkpoint Tiers

See [GATES.md](GATES.md) for the full checkpoint protocol, tier definitions, and decision criteria.
