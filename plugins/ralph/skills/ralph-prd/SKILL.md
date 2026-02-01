---
name: ralph-prd
description: Create PRD and setup for Ralph autonomous loop. Use when user runs /create-prd command, wants to set up a project for Ralph, mentions "ralph setup", "create prd", or needs to generate tasks for autonomous development.
---

# Ralph PRD Creation

Interactive wizard to create Product Requirements Document and Ralph project setup with task sets.

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
        └── initial/                   # Your task set (named during setup)
            ├── tasks.json             # Task list (JSON)
            ├── prd.md                 # Requirements (Markdown)
            ├── memories.md            # Persistent learnings
            ├── config.json            # Ralph settings
            └── activity.log           # Iteration log (empty)
```

## Discovery Questions

The wizard asks:

0. **Task Set Name** - What should this collection be called? (default: "initial")
1. **Problem** - What problem are you solving?
2. **Audience** - Who is the target user?
3. **Features** - What are the 3-5 core features?
4. **Tech Stack** - What technologies to use?
5. **Architecture** - Monolith, microservices, etc.?
6. **UI/UX** - Visual requirements and preferences?
7. **Auth** - Authentication needs?
8. **Integrations** - Third-party services?
9. **Success Criteria** - How do we know it's done?

## Task Generation

Converts features into atomic tasks:

```json
{
  "tasks": [
    {
      "id": "setup-001",
      "category": "setup",
      "description": "Initialize Next.js with TypeScript",
      "steps": ["Run create-next-app", "Install deps", "Verify dev server"],
      "passes": false
    }
  ]
}
```

**Task Categories:**
- `setup` - Project initialization
- `feature` - Core functionality
- `integration` - External services
- `styling` - UI/UX implementation
- `testing` - Test coverage

## Workflow

See [WORKFLOW.md](WORKFLOW.md) for detailed discovery flow.

## Examples

See [EXAMPLES.md](EXAMPLES.md) for PRD examples.

## After Setup

```bash
./ralph.sh 20    # Start autonomous loop
```

## Creating Additional Task Sets

After initial setup, create more task sets:

```bash
/ralph taskset new "auth-feature"    # Create new task set
/ralph taskset list                  # See all task sets
/ralph taskset switch "auth-feature" # Switch to it
```
