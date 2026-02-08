---
description: Create PRD and set up project for Ralph autonomous development loop
argument-hint: [project description]
---

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

The wizard will ask about:

0. **Task Set Name** - What should this collection be called? (default: "initial")
1. **Problem** - What are you solving?
2. **Audience** - Who is the user?
3. **Features** - What are the 3-5 core features?
4. **Tech Stack** - Framework, language, tools?
5. **Architecture** - Frontend only? Fullstack? API?
6. **UI/UX** - Design preferences?
7. **Auth** - Authentication needed?
8. **Integrations** - Third-party services?
9. **Success Criteria** - What defines "done"?

## Output Files

After completion, your project will have:

```
your-project/
├── PROMPT.md                          # Instructions for each iteration
├── ralph.sh                           # Loop runner (executable)
└── .ralph/
    ├── current-taskset -> tasksets/initial  # Symlink to active taskset
    └── tasksets/
        └── initial/                   # Your task set
            ├── tasks.json             # Task list (JSON)
            ├── prd.md                 # Requirements (Markdown)
            ├── memories.md            # Persistent learnings
            ├── config.json            # Ralph settings
            └── activity.log           # Empty, ready for logging
```

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

2. **Generate `.ralph/tasksets/${TASKSET_NAME}/tasks.json`** from discovery answers

3. **Generate `.ralph/tasksets/${TASKSET_NAME}/prd.md`** from discovery answers

4. **Generate `.ralph/tasksets/${TASKSET_NAME}/memories.md`** (empty template)

5. **Generate `PROMPT.md`** with tech-stack-specific commands (uses symlink paths)

6. **Copy `ralph.sh`** from plugin and make executable

7. **Generate `.ralph/tasksets/${TASKSET_NAME}/config.json`** with settings

8. **Create symlink:**
   ```bash
   ln -sfn tasksets/${TASKSET_NAME} .ralph/current-taskset
   ```

9. **Create empty activity log:**
   ```bash
   touch .ralph/tasksets/${TASKSET_NAME}/activity.log
   ```

### Step 6: Provide next steps

```markdown
## Setup Complete!

Task set: ${TASKSET_NAME}

Files created:
- .ralph/tasksets/${TASKSET_NAME}/tasks.json (X tasks)
- .ralph/tasksets/${TASKSET_NAME}/prd.md
- .ralph/tasksets/${TASKSET_NAME}/memories.md
- .ralph/tasksets/${TASKSET_NAME}/config.json
- .ralph/current-taskset (symlink)
- PROMPT.md
- ralph.sh

Next steps:
1. Review the generated tasks: cat .ralph/current-taskset/tasks.json
2. Start the loop: ./ralph.sh 20
3. Or run fewer iterations: ./ralph.sh 5

The loop will work through tasks until complete or max iterations reached.

To create another task set later:
/ralph taskset new "feature-name"
```

## Quick Mode

If a description is provided, skip some questions:

```bash
/create-prd "Build a React todo app with TypeScript"
```

In this case:
- Infer tech stack from description
- Ask only clarifying questions
- Generate minimal viable task list
- Use default task set name "initial"

## Task Categories

Generated tasks use these categories:

| Category | Description |
|----------|-------------|
| `setup` | Project initialization |
| `feature` | Core functionality |
| `integration` | External services |
| `styling` | UI/UX work |
| `testing` | Test coverage |

## Tech Stack Defaults

If not specified, default to:

| Component | Default |
|-----------|---------|
| Framework | React |
| Language | TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| Testing | Vitest |

## Notes

- Tasks should be atomic (completable in one iteration)
- Order tasks by dependency (setup first, then features)
- Keep scope tight for v1 (defer nice-to-haves)
- Success criteria should be testable
- Task set names should be descriptive and kebab-case
