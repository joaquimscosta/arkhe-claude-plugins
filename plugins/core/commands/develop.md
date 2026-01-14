---
description: Unified 6-phase SDLC with plan persistence, resume mode, and autonomous execution
argument-hint: <feature description> [--plan-only] [--validate] [--auto] [@path/to/plan]
---

# Develop

Guided feature development through a 6-phase SDLC pipeline with plan persistence.

## Quick Start

```bash
/develop add user authentication         # Full pipeline
/develop add logout button --auto        # Autonomous mode
/develop create plan for X --plan-only   # Plan only
/develop @arkhe/specs/01-auth/           # Resume existing
```

## Flags

| Flag | Effect |
|------|--------|
| `--plan-only` | Stop after Phase 2 (save plan, don't implement) |
| `--validate` | Enable opus-level validation in Phase 4 |
| `--phase=N` | Execute specific phase only |
| `--auto` | Autonomous mode (no checkpoints) |
| `@path` | Resume from existing plan |

## Implementation

Load the SDLC skill and execute with provided arguments:

**Read:** `plugins/core/skills/sdlc-develop/SKILL.md`

Follow the skill's execution flow, loading phase files progressively as each phase is entered.

**Arguments:** `$ARGUMENTS`

For detailed phase documentation, see [skill documentation](../skills/sdlc-develop/SKILL.md).
