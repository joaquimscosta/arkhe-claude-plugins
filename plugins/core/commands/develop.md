---
description: Unified 6-phase SDLC with plan persistence, resume mode, and autonomous execution
argument-hint: <feature description> [--plan-only] [--validate] [--auto] [--verify-arch] [--verify-impl] [@path/to/plan]
---

# Develop

Guided feature development through a 6-phase SDLC pipeline with plan persistence.

## Quick Start

```bash
/develop add user authentication         # Full pipeline
/develop add logout button --auto        # Autonomous mode
/develop create plan for X --plan-only   # Plan only
/develop @arkhe/specs/01-auth/           # Resume existing
/develop @arkhe/specs/01-auth/ --verify-arch   # Verify architecture alignment
/develop @arkhe/specs/01-auth/ --verify-impl   # Verify implementation completeness
/develop @arkhe/specs/01-auth/ --verify-arch --verify-impl  # Full audit
```

## Flags

| Flag | Effect |
|------|--------|
| `--plan-only` | Stop after Phase 2 (save plan, don't implement) |
| `--validate` | Enable opus-level validation in Phase 4 |
| `--phase=N` | Execute specific phase only |
| `--auto` | Autonomous mode (no checkpoints) |
| `@path` | Resume from existing plan |
| `--verify-arch` | Verify implementation matches plan.md architecture |
| `--verify-impl` | Verify implementation meets spec.md requirements |

## Implementation

Invoke the Skill tool with skill name "core:sdlc-develop" and arguments: `$ARGUMENTS`

The skill handles all six phases: Discovery → Requirements → Architecture → Workstreams → Implementation → Summary.

For detailed phase documentation, see `core/skills/sdlc-develop/SKILL.md`.
