# ralph — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

Autonomous development loop with fresh context per iteration, Hat-lite builder/verifier system, task sets, and persistent memories

## Skills

- **ralph-loop** — Execute an autonomous development loop that picks one task per iteration, implements it, verifies it, and commits the result — each iteration in a fresh context window. Use when user runs /ralph, men…
- **ralph-prd** — Create Product Requirements Document (PRD) and setup for Ralph autonomous loop. Use when user runs /create-prd command, wants to set up a project for Ralph, mentions "ralph setup", "create prd", "pro…

## Commands as Trigger Phrases

### When the user says "/ralph:create-prd" (args: [project description])

Create PRD and set up project for Ralph autonomous development loop

# Create PRD Command

Interactive wizard to create a Product Requirements Document and set up your project for Ralph.

## Usage

```bash
/create-prd                           # Start interactive wizard
/create-prd "Build a todo app"        # Start with description
```

## What It Does

1. **Asks for task set name** (default: "initial")
2. **Asks discovery questions** about your project
3. **Generates task list** in `.ralph/tasksets/{name}/tasks.json`
4. **Creates PRD** in `.ralph/tasksets/{name}/prd.md`
5. **Creates memories file** in `.ralph/tasksets/{name}/memories.md`
6. **Creates PROMPT.md** with iteration instructions
7. **Copies ralph.sh** loop runner script
8. **Creates symlink** `.ralph/current-taskset`

## Discovery Questions

Ask 10 discovery questions (task set name, problem, audience, features, tech stack, architecture, UI/UX, auth, integrations, success criteria). See the ralph-prd skill's [WORKFLOW.md](../skills/ralph-prd/WORKFLOW.md) for question details and good answer examples.

## Output Files

See the ralph-prd skill's [SKILL.md](../skills/ralph-prd/SKILL.md#what-it-creates) "What It Creates" section for the full directory structure. Use [templates/](../skills/ralph-prd/templates/) for generating each file.

## Implementation

When the user runs `/create-prd`:

### Step 1: Ask for task set name

```markdown
## Task Set Name

What would you like to name this task set?

Examples: "initial", "auth-feature", "test-coverage"

(Default: "initial" if you press Enter)
```

Validate the name:
- Lowercase only
- Alphanumeric and hyphens only
- No spaces

### Step 2: Check for existing setup

```bash
TASKSET_NAME="${1:-initial}"

if [[ -d ".ralph/tasksets/${TASKSET_NAME}" ]]; then
  echo "Task set '${TASKSET_NAME}' already exists."
  echo "Run /ralph taskset switch ${TASKSET_NAME} to use it."
  echo "Or choose a different name."
  exit 0
fi
```

### Step 3: Run discovery questions

Use `AskUserQuestion` tool for each discovery step:

```markdown
## Discovery: Problem Definition

What problem are you solving with this project?

(Describe the pain point you're addressing)
```

### Step 4: Generate tasks from features

Convert each feature into atomic tasks:

- Each task completable in ONE iteration
- Clear steps provided
- Verification criteria included

### Step 5: Create files

1. **Create directory structure:**
   ```bash
   mkdir -p .ralph/tasksets/${TASKSET_NAME} screenshots
   ```

_…full command body at `plugins/ralph/commands/create-prd.md`._

### When the user says "/ralph:ralph" (args: run [iterations] | status | init | taskset <new|list|switch|delete> | add-task | remember | memories)

Ralph autonomous development loop with fresh context per iteration

# Ralph Command

Autonomous development loop with Hat-lite builder/verifier system and task set isolation.

## Usage

```bash
/ralph run [N]              # Start loop with N iterations (default: 20)
/ralph status               # Show task completion progress
/ralph init                 # Initialize Ralph in existing project

# Task Set Management
/ralph taskset new <name>   # Create new task set and switch to it
/ralph taskset list         # List all task sets with status
/ralph taskset switch <name> # Switch active task set
/ralph taskset delete <name> # Remove a task set

# Task Management
/ralph add-task "description" # Add task to current task set

# Memory Management
/ralph remember "insight"   # Save learning to memories
/ralph memories             # View current task set's memories
```

## Subcommands

### `/ralph run [iterations]`

Start the Ralph autonomous loop.

**Requirements:**
- `PROMPT.md` must exist (created by `/create-prd`)
- `.ralph/current-taskset` symlink must exist
- `.ralph/current-taskset/tasks.json` must exist

**Process:**
1. Verify required files exist
2. Display loop configuration
3. Execute `./ralph.sh {iterations}`

**Example:**
```bash
/ralph run 10     # Run up to 10 iterations
/ralph run        # Run up to 20 iterations (default)
```

### `/ralph status`

Show current progress of the Ralph loop.

**Output:**
- Current task set name
- Total tasks
- Completed tasks
- Remaining tasks
- Last activity timestamp
- Current/next task

**Example output:**
```
Ralph Status
============
Task Set: initial (active)
Project: my-todo-app
Tasks: 4/6 complete (66%)

Completed:
  ✓ setup-001: Initialize project
  ✓ feat-001: Create todo list
  ✓ feat-002: Add todo creation
  ✓ feat-003: Add complete/delete

Remaining:
  ○ feat-004: Add localStorage
  ○ style-001: Apply styling

Last activity: 2026-02-01 14:30:00
```

### `/ralph init`

Initialize Ralph in an existing project (without running `/create-prd`).

**Creates:**
- `.ralph/tasksets/initial/` directory structure
- Empty `.ralph/tasksets/initial/tasks.json` with template
- Empty `.ralph/tasksets/initial/memories.md`
- Empty `.ralph/tasksets/initial/activity.log`
- Symlink `.ralph/current-taskset -> tasksets/initial`
- Default `PROMPT.md`
- Copy of `ralph.sh`

**Use when:** You want to set up Ralph manually or already have a task list.

### `/ralph taskset new <name>`

Create a new task set for focused work.

_…full command body at `plugins/ralph/commands/ralph.md`._
