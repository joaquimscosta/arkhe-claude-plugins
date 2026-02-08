# Ralph Plugin

> "Me fail English? That's unpossible!" - Ralph Wiggum

Autonomous development loop with fresh context per iteration, Hat-lite builder/verifier system, and task set isolation.

## What is Ralph?

Ralph Wiggum is a method for running Claude Code in a continuous autonomous loop. Each iteration runs in a **fresh context window**, allowing the agent to work through a series of tasks until completion without context bloat.

### When to Use Ralph

**Ideal for:**
- Starting projects from scratch (greenfield development)
- Building proof of concepts (POCs) with clearly defined scope
- Adding focused features to existing projects
- Running test coverage campaigns
- Refactoring tasks with clear boundaries
- Projects where you can define "done" precisely

**Not ideal for:**
- Exploratory work without clear goals
- Projects with ambiguous requirements
- Situations requiring frequent human judgment

## Quick Start

### 1. Install the Plugin

```bash
/plugin install ralph@arkhe-claude-plugins
```

### 2. Create Your PRD

```bash
cd my-project
/create-prd
```

Answer the discovery questions about your project. You'll be asked for a **task set name** (default: "initial").

### 3. Run the Loop

```bash
./ralph.sh 20
```

Ralph will iterate until all tasks are complete or max iterations reached.

## Commands

| Command | Description |
|---------|-------------|
| `/ralph run [N]` | Start loop with N iterations (default: 20) |
| `/ralph status` | Show task completion progress |
| `/ralph init` | Initialize Ralph in existing project |
| `/create-prd` | Interactive PRD creation wizard |

### Task Set Management

| Command | Description |
|---------|-------------|
| `/ralph taskset new <name>` | Create new task set and switch to it |
| `/ralph taskset list` | List all task sets with status |
| `/ralph taskset switch <name>` | Switch active task set |
| `/ralph taskset delete <name>` | Remove a task set |

### Task & Memory Management

| Command | Description |
|---------|-------------|
| `/ralph add-task "description"` | Add task to current task set |
| `/ralph remember "insight"` | Save learning to memories |
| `/ralph memories` | View current task set's memories |

## How It Works

### Fresh Context Per Iteration

Each iteration runs `claude -p "$(cat PROMPT.md)"` which starts with **no prior context**. This prevents:
- Context bloat over time
- Hallucination buildup
- Accumulated confusion

### Task Sets

Task sets allow you to use Ralph for multiple focused efforts on the same project:

```bash
# Initial project setup
/create-prd                          # Creates "initial" task set

# Later: Add authentication feature
/ralph taskset new auth-feature      # Creates and switches to new task set
/ralph add-task "Create login API"
/ralph add-task "Add login form"
./ralph.sh 10

# Switch back to check on initial work
/ralph taskset switch initial
/ralph status
```

### Memories System

Each task set has a `memories.md` file where learnings persist across iterations:

```bash
# Save a discovery
/ralph remember "pattern: All API routes use /api/v1 prefix"
/ralph remember "fix: Tailwind colors must be in config, not inline"

# View memories
/ralph memories
```

Categories:
- **Patterns**: Code conventions, project standards
- **Decisions**: Why a particular approach was chosen
- **Fixes**: Solutions to problems
- **Context**: Important project knowledge

### Hat-Lite System

Each iteration follows two phases:

| Phase | Role | Responsibility |
|-------|------|----------------|
| **Build** | Builder | Pick ONE task, implement, verify |
| **Verify** | Verifier | Review, update status, commit |

### JSON Task Tracking

Tasks are tracked in `.ralph/current-taskset/tasks.json`:

```json
{
  "tasks": [
    {
      "id": "feat-001",
      "description": "Add user login",
      "passes": false
    }
  ]
}
```

### Completion Signal

When all tasks pass, the loop outputs:

```
RALPH_COMPLETE: All tasks verified
```

## Project Structure

After running `/create-prd`:

```
your-project/
├── PROMPT.md                          # Instructions per iteration
├── ralph.sh                           # Loop runner script
└── .ralph/
    ├── current-taskset -> tasksets/initial  # Symlink to active task set
    └── tasksets/
        └── initial/                   # Your first task set
            ├── tasks.json             # Task state (source of truth)
            ├── prd.md                 # Requirements document
            ├── memories.md            # Persistent learnings
            ├── config.json            # Ralph settings
            └── activity.log           # Iteration history
```

## Components

### Skills

| Skill | Purpose |
|-------|---------|
| `ralph-loop` | Execution protocol for each iteration |
| `ralph-prd` | PRD authoring and project setup |

### Agent

| Agent | Purpose |
|-------|---------|
| `ralph-agent` | Autonomous development with Hat-lite workflow |

## Example Session

### Greenfield Project

```bash
# Create a new project
mkdir my-todo-app && cd my-todo-app

# Set up for Ralph
/create-prd
# Answer: "Build a simple todo app with React"
# Task set name: "initial" (default)

# Start autonomous development
./ralph.sh 20

# Check progress (in another terminal)
/ralph status

# Output:
# Task Set: initial (active)
# Tasks: 4/6 complete (66%)
# ...

# Loop completes
# RALPH_COMPLETE: All tasks verified
```

### Adding a Feature to Existing Project

```bash
# In existing project with Ralph already set up
cd my-todo-app

# Create a new task set for the feature
/ralph taskset new user-auth

# Add tasks for the feature
/ralph add-task "Create auth API endpoints"
/ralph add-task "Add login form component"
/ralph add-task "Implement session management"
/ralph add-task "Add protected routes"

# Run the loop
./ralph.sh 15

# Save a learning for future iterations
/ralph remember "decision: Using JWT for stateless auth"
```

### Test Coverage Campaign

```bash
# Create task set for testing
/ralph taskset new test-coverage

# Add testing tasks
/ralph add-task "Add tests for auth API"
/ralph add-task "Add tests for todo CRUD"
/ralph add-task "Add integration tests"

# Run
./ralph.sh 10
```

## Configuration

Ralph settings in `.ralph/current-taskset/config.json`:

```json
{
  "project": "my-todo-app",
  "taskset": "initial",
  "ralph_version": "2.0.0",
  "max_iterations": 20,
  "verification_commands": {
    "lint": "npm run lint",
    "typecheck": "npm run typecheck",
    "test": "npm run test"
  }
}
```

## Best Practices

### 1. Plan Thoroughly

Use `/create-prd` carefully. A well-defined PRD is the difference between success and wasted iterations.

### 2. Keep Scope Tight

Define the minimum viable version for each task set. Focused task sets complete faster.

### 3. Use Task Sets for Isolation

Create separate task sets for different concerns:
- `initial` - Project setup
- `auth-feature` - Authentication
- `test-coverage` - Test suite
- `refactor-api` - API improvements

### 4. Leverage Memories

Save useful discoveries to help future iterations:
```bash
/ralph remember "pattern: Components use named exports"
/ralph remember "fix: Run migrations before tests"
```

### 5. Start with Fewer Iterations

Use 10-20 iterations initially. You can always run more.

### 6. Monitor First Iterations

Watch the first 2-3 iterations to ensure things work correctly.

## Troubleshooting

See `skills/ralph-loop/TROUBLESHOOTING.md` for common issues.

### Quick Fixes

**Loop exits immediately:**
- Check `PROMPT.md` exists
- Check `.ralph/current-taskset` symlink exists
- Check `.ralph/current-taskset/tasks.json` exists
- Run `/create-prd` first

**Tasks not completing:**
- Check verification commands in config
- Review activity.log for errors
- Consider breaking large tasks into smaller ones

**Wrong task set active:**
- Run `/ralph taskset list` to see all task sets
- Run `/ralph taskset switch <name>` to change

## Credits

- **[Geoffrey Huntley](https://ghuntley.com/ralph/)** - Creator of the Ralph Wiggum technique
- **[Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)** - Best practices for long-running agents

## License

MIT
