---
description: Ralph autonomous development loop with fresh context per iteration
argument-hint: run [iterations] | status | init | taskset <new|list|switch|delete> | add-task | remember | memories
---

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

**Arguments:**
- `<name>` - Task set name (lowercase, alphanumeric, hyphens only)

**Process:**
1. Validate name format (lowercase, alphanumeric, hyphens)
2. Check if task set already exists
3. Create `.ralph/tasksets/{name}/` directory
4. Create empty `tasks.json` with template
5. Create empty `memories.md` with template
6. Create empty `activity.log`
7. Update symlink: `ln -sfn tasksets/{name} .ralph/current-taskset`
8. Confirm creation and show next steps

**Example:**
```bash
/ralph taskset new auth-feature
# Creates: .ralph/tasksets/auth-feature/
# Updates: .ralph/current-taskset -> tasksets/auth-feature
```

### `/ralph taskset list`

List all task sets with their completion status.

**Output:**
```
Task Sets:
  * initial (4/6 complete) ← current
    auth-feature (0/3 complete)
    test-coverage (2/5 complete)
```

The asterisk (*) marks the currently active task set.

### `/ralph taskset switch <name>`

Switch to a different task set.

**Arguments:**
- `<name>` - Name of existing task set

**Process:**
1. Verify task set exists in `.ralph/tasksets/`
2. Update symlink: `ln -sfn tasksets/{name} .ralph/current-taskset`
3. Show status of newly active task set

**Example:**
```bash
/ralph taskset switch auth-feature
# Updates: .ralph/current-taskset -> tasksets/auth-feature
```

### `/ralph taskset delete <name>`

Remove a task set (with confirmation).

**Arguments:**
- `<name>` - Name of task set to delete

**Process:**
1. Verify task set exists
2. Prevent deletion of currently active task set
3. Show task set details and ask for confirmation
4. Remove `.ralph/tasksets/{name}/` directory

**Example:**
```bash
/ralph taskset delete old-feature
# Shows: "Delete 'old-feature' with 3 tasks (2 incomplete)? [y/N]"
```

### `/ralph add-task "description"`

Add a task to the current task set.

**Arguments:**
- `"description"` - Brief description of the task

**Process:**
1. Read current task set's tasks.json
2. Auto-generate task ID based on description:
   - `setup-NNN` for setup/init tasks
   - `feat-NNN` for feature tasks
   - `fix-NNN` for bug fixes
   - `test-NNN` for testing tasks
   - `style-NNN` for styling tasks
3. Append new task with `passes: false`
4. Confirm addition with task ID

**Example:**
```bash
/ralph add-task "Add user login form"
# Creates task: feat-004 - Add user login form
```

### `/ralph remember "insight"`

Save a learning or insight to the current task set's memories.

**Arguments:**
- `"insight"` - The pattern, decision, fix, or context to remember

**Format:** Use prefixes to categorize:
- `pattern: <insight>` - Code patterns/conventions
- `decision: <insight>` - Design/architecture decisions
- `fix: <insight>` - Solutions to problems
- `context: <insight>` - Important project context

**Process:**
1. Read `.ralph/current-taskset/memories.md`
2. Parse prefix to determine category (default: Context)
3. Append dated entry to appropriate section
4. Confirm save

**Example:**
```bash
/ralph remember "pattern: All API routes use /api/v1 prefix"
/ralph remember "fix: Tailwind colors must be in config, not inline"
/ralph remember "decision: Using JWT for stateless auth"
```

### `/ralph memories`

Display the current task set's memories.

**Output:** Contents of `.ralph/current-taskset/memories.md`

**Example output:**
```markdown
# Memories: auth-feature

## Patterns
### 2026-02-01: API route prefix
All API routes use /api/v1 prefix

## Decisions
### 2026-02-01: Auth method
Using JWT for stateless auth - no server-side sessions needed

## Fixes
### 2026-02-01: Tailwind colors
Tailwind colors must be in config, not inline - purging removes them
```

## Implementation Details

### For `taskset new`:
```bash
# Validate name
if [[ ! "$name" =~ ^[a-z0-9-]+$ ]]; then
  echo "Error: Name must be lowercase, alphanumeric, hyphens only"
  exit 1
fi

# Check exists
if [[ -d ".ralph/tasksets/$name" ]]; then
  echo "Error: Task set '$name' already exists"
  exit 1
fi

# Create structure
mkdir -p ".ralph/tasksets/$name"
cat > ".ralph/tasksets/$name/tasks.json" << EOF
{
  "project": "$(basename $(pwd))",
  "taskset": "$name",
  "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "tasks": []
}
EOF

# Create memories from template
cat > ".ralph/tasksets/$name/memories.md" << EOF
# Memories: $name

> Persistent learnings that survive across iterations within this task set.

## Patterns
<!-- Code patterns, conventions, and standards discovered -->

## Decisions
<!-- Architectural and design decisions made -->

## Fixes
<!-- Solutions to problems encountered -->

## Context
<!-- Important project context -->
EOF

# Create empty activity log
touch ".ralph/tasksets/$name/activity.log"

# Update symlink
ln -sfn "tasksets/$name" .ralph/current-taskset
```

### For `taskset list`:
```bash
echo "Task Sets:"
for dir in .ralph/tasksets/*/; do
  name=$(basename "$dir")
  total=$(jq '.tasks | length' "$dir/tasks.json")
  done=$(jq '[.tasks[] | select(.passes == true)] | length' "$dir/tasks.json")

  if [[ "$(readlink .ralph/current-taskset)" == "tasksets/$name" ]]; then
    echo "  * $name ($done/$total complete) ← current"
  else
    echo "    $name ($done/$total complete)"
  fi
done
```

### For `add-task`:
```bash
# Determine category from description
if [[ "$desc" =~ ^(init|setup|install|config) ]]; then
  category="setup"
elif [[ "$desc" =~ ^(fix|bug|patch) ]]; then
  category="fix"
elif [[ "$desc" =~ ^(test|spec) ]]; then
  category="test"
elif [[ "$desc" =~ ^(style|css|design) ]]; then
  category="style"
else
  category="feat"
fi

# Get next ID
count=$(jq "[.tasks[] | select(.id | startswith(\"$category\"))] | length" .ralph/current-taskset/tasks.json)
id=$(printf "%s-%03d" "$category" $((count + 1)))

# Add task
jq --arg id "$id" --arg cat "$category" --arg desc "$desc" \
  '.tasks += [{"id": $id, "category": $cat, "description": $desc, "steps": [], "passes": false, "iteration_completed": null}]' \
  .ralph/current-taskset/tasks.json > tmp.json && mv tmp.json .ralph/current-taskset/tasks.json
```

### For `remember`:
```bash
# Parse category prefix
if [[ "$insight" =~ ^pattern: ]]; then
  section="Patterns"
  content="${insight#pattern: }"
elif [[ "$insight" =~ ^decision: ]]; then
  section="Decisions"
  content="${insight#decision: }"
elif [[ "$insight" =~ ^fix: ]]; then
  section="Fixes"
  content="${insight#fix: }"
else
  section="Context"
  content="${insight#context: }"
fi

# Append to memories.md under appropriate section
date=$(date +"%Y-%m-%d")
# (Use sed or awk to insert after section header)
```

## Notes

- The `/ralph run` command executes an external bash script for true fresh context isolation
- Each iteration runs `claude -p "$(cat PROMPT.md)"` which starts with no prior context
- Progress is tracked in `.ralph/current-taskset/tasks.json` and `.ralph/current-taskset/activity.log`
- Memories persist across iterations within a task set via `.ralph/current-taskset/memories.md`
- Task sets allow focused work efforts on the same project (features, test coverage, refactoring)
