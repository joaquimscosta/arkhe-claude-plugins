---
name: ralph-prd
description: "Create Product Requirements Document (PRD) and setup for Ralph autonomous loop. Use when user runs /create-prd command, wants to set up a project for Ralph, mentions \"ralph setup\", \"create prd\", \"product requirements\", or needs to generate tasks for autonomous development."
---

# Ralph PRD Creation

Interactive wizard to create a Product Requirements Document and Ralph project setup with task sets.

## Quick Start

```bash
/create-prd                    # Start interactive wizard
/create-prd "Build a todo app" # Start with description
```

## What It Creates

```
project/
├── PROMPT.md                          # Instructions for each iteration
├── ralph.sh                           # Loop runner (executable)
└── .ralph/
    ├── current-taskset -> tasksets/initial  # Symlink to active taskset
    └── tasksets/
        └── initial/                   # Task set (named during setup)
            ├── tasks.json             # Task list (JSON)
            ├── prd.md                 # Requirements (Markdown)
            ├── memories.md            # Persistent learnings
            ├── config.json            # Ralph settings
            └── activity.log           # Iteration log (empty)
```

## Discovery Questions

Ask these questions in order:

0. **Task Set Name** - Collection name? (default: "initial")
1. **Problem** - What problem are you solving?
2. **Audience** - Who is the target user?
3. **Features** - What are the 3-5 core features?
4. **Tech Stack** - What technologies to use?
5. **Architecture** - Monolith, microservices, etc.?
6. **UI/UX** - Visual requirements and preferences?
7. **Auth** - Authentication needs?
8. **Integrations** - Third-party services?
9. **Success Criteria** - How do we know it's done?

> **Destructive operations:** When questions involve deleting files or removing dependencies, always include full paths, state scope (file/line count), confirm what will NOT be affected, and frame as confirmation ("Deleting X, Y, Z. Proceed?"). See [EXAMPLES.md](EXAMPLES.md) for anti-patterns.

## Task Generation

Convert features into atomic tasks with categories: `setup`, `feature`, `integration`, `styling`, `testing`, `verification`. See [WORKFLOW.md](WORKFLOW.md) for task format and ordering.

Always include a final `verification` task with `verificationTier: "visual"` (UI) or `"api"` (API-only) that validates the complete application end-to-end.

## Templates (MANDATORY)

Read and use these templates verbatim via the Read tool. Fill in `{{placeholders}}` -- never hand-write output files from memory.

> **WARNING:** Hand-writing PROMPT.md or using wrong field names causes the loop to run forever. The `ralph.sh` loop checks for `RALPH_COMPLETE:` (defined in `prompt.md.template` Step 5) and tasks use `"passes": false/true` (NOT `"status"`).

| Template | Purpose |
|----------|---------|
| `prompt.md.template` | Iteration instructions -- contains the `RALPH_COMPLETE:` stop signal |
| `tasks.json.template` | Task list -- uses `"passes"` field, not `"status"` |
| `prd.md.template` | PRD document structure |
| `config.json.template` | Ralph configuration |
| `memories.md.template` | Persistent learnings file |

**ralph.sh:** Always copy from this plugin's `scripts/ralph.sh` directory. It contains required flags (`--dangerously-skip-permissions`, `--disallowedTools`) essential for non-interactive execution.

## After Setup

```bash
./ralph.sh 20    # Start autonomous loop
```

## Creating Additional Task Sets

```bash
/ralph taskset new "auth-feature"    # Create new task set
/ralph taskset list                  # See all task sets
/ralph taskset switch "auth-feature" # Switch to it
```

## Supporting Docs

- [WORKFLOW.md](WORKFLOW.md) -- Detailed discovery flow and file generation
- [EXAMPLES.md](EXAMPLES.md) -- PRD examples and anti-patterns
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) -- Common issues and debugging
