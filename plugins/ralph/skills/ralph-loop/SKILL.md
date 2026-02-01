---
name: ralph-loop
description: Autonomous development loop with fresh context per iteration. Use when user runs /ralph command, mentions "ralph loop", "autonomous loop", "hat-lite", "builder verifier", or wants iterative autonomous development with task tracking.
---

# Ralph Loop Execution Protocol

Autonomous development with fresh context per iteration and Hat-lite builder/verifier workflow.

## Quick Start

```bash
# From project directory (after /create-prd)
./ralph.sh 20          # Run up to 20 iterations
./ralph.sh 5           # Quick test with 5 iterations
```

## How It Works

Each iteration runs in a **fresh context window**:

```
┌─────────────────────────────────────────────────────┐
│ ITERATION (Fresh Context)                           │
├─────────────────────────────────────────────────────┤
│ 1. ORIENT: Read activity.log + tasks.json + memories│
│ 2. BUILD:  Pick ONE task, implement, verify        │
│ 3. VERIFY: Review, update status, commit           │
│ 4. LEARN:  (Optional) Save insights to memories    │
│ 5. DECIDE: All done? → RALPH_COMPLETE              │
└─────────────────────────────────────────────────────┘
```

## Hat-Lite System

| Role | When | Responsibility |
|------|------|----------------|
| **Builder** | 70% of iteration | Implement ONE task |
| **Verifier** | 30% of iteration | Review, update, commit |

## Key Files

| File | Purpose |
|------|---------|
| `.ralph/current-taskset/tasks.json` | Task state (source of truth) |
| `.ralph/current-taskset/activity.log` | Iteration history |
| `.ralph/current-taskset/memories.md` | Persistent learnings |
| `.ralph/current-taskset` | Symlink to active task set |
| `PROMPT.md` | Instructions per iteration |
| `ralph.sh` | Loop runner script |

## Task JSON Format

Tasks are stored in `.ralph/current-taskset/tasks.json`:

```json
{
  "tasks": [
    {
      "id": "setup-001",
      "description": "Initialize project",
      "passes": false,
      "iteration_completed": null
    }
  ]
}
```

## Completion Signal

When all tasks pass, output:

```
RALPH_COMPLETE: All tasks verified
```

## Commands

| Command | Action |
|---------|--------|
| `/ralph run [N]` | Start loop with N iterations |
| `/ralph status` | Show task completion progress |
| `/ralph init` | Initialize Ralph in existing project |
| `/ralph taskset new` | Create new task set |
| `/ralph taskset list` | List all task sets |
| `/ralph taskset switch` | Switch active task set |
| `/ralph add-task` | Add task to current set |
| `/ralph remember` | Save insight to memories |
| `/ralph memories` | View memories |

## Workflow Details

See [WORKFLOW.md](WORKFLOW.md) for detailed iteration steps.

## Hat Definitions

See [HATS.md](HATS.md) for Builder/Verifier persona details.

## Examples

See [EXAMPLES.md](EXAMPLES.md) for usage scenarios.

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.
