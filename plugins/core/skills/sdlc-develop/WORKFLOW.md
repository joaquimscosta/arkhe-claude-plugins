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
  |   +-- If wave context found -> Offer: Continue next wave / Re-review / Restart
  |   +-- If no wave context -> Ask which phase -> Jump to phase
  |
  +-- [PLAN/FULL] Read PHASE-0-DISCOVERY.md
  |   +-- Execute Phase 0 -> Checkpoint
  |
  +-- Read PHASE-1-REQUIREMENTS.md
  |   +-- Execute Phase 1 -> Checkpoint
  |
  +-- Read PHASE-2-ARCHITECTURE.md
  |   +-- Execute Phase 2 -> Save plan -> [PLAN stops here]
  |
  +-- [FULL] Read PHASE-3-WORKSTREAMS.md
  |   +-- Execute Phase 3 -> Checkpoint
  |
  +-- Read PHASE-4-IMPLEMENTATION.md
  |   +-- Step 4.0: Ticket Selection (select/defer tasks)
  |   +-- For each wave:
  |       +-- Step 4a.1: Wave Confirmation
  |       +-- Step 4a.2: Implement wave tasks
  |       +-- Step 4a.3: Wave Checkpoint -> CONTINUE or STOP
  |           +-- [CONTINUE] -> Next wave (4a.1)
  |           +-- [STOP] -> Save context, exit Phase 4
  |   +-- Step 4b-4d: Validation -> Quality Review
  |   +-- Step 4e: Completion Gate (Tier 1 - mandatory)
  |
  +-- Read PHASE-5-SUMMARY.md
      +-- Execute Phase 5 -> Complete
```

## Phase Dependencies

Each phase loads its file only when entered. See the phase routing table in SKILL.md for file paths and goals.

## Checkpoint Tiers

See [GATES.md](GATES.md) for the full checkpoint protocol, tier definitions, and decision criteria.
