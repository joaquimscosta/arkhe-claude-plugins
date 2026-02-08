# Ralph PRD Creation Workflow

Step-by-step guide for creating a Product Requirements Document and Ralph project setup with task sets.

## Overview

The `/create-prd` command walks you through an interactive discovery session, then generates all files needed to run a Ralph autonomous loop with task set isolation.

## Discovery Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRD CREATION WORKFLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 0: TASK SET NAME                                    │   │
│  │                                                          │   │
│  │ Q: What should this task set be called?                 │   │
│  │ Default: "initial"                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 1: PROBLEM DEFINITION                               │   │
│  │                                                          │   │
│  │ Q: What problem are you solving?                        │   │
│  │ Q: Who experiences this problem?                        │   │
│  │ Q: What's the impact of not solving it?                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 2: TARGET AUDIENCE                                  │   │
│  │                                                          │   │
│  │ Q: Who is the primary user?                             │   │
│  │ Q: What's their technical level?                        │   │
│  │ Q: How will they use this?                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 3: CORE FEATURES (3-5 features)                     │   │
│  │                                                          │   │
│  │ Q: What are the must-have features?                     │   │
│  │ Q: What can be deferred to later?                       │   │
│  │ Q: What's the MVP scope?                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 4: TECH STACK                                       │   │
│  │                                                          │   │
│  │ Q: Preferred framework? (React, Vue, etc.)              │   │
│  │ Q: Preferred language? (TypeScript, JavaScript)         │   │
│  │ Q: Build tool? (Vite, Next.js, etc.)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 5: ARCHITECTURE                                     │   │
│  │                                                          │   │
│  │ Q: Frontend only, fullstack, or API?                    │   │
│  │ Q: Data storage needs?                                  │   │
│  │ Q: External services needed?                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 6: UI/UX                                            │   │
│  │                                                          │   │
│  │ Q: Design style? (minimal, modern, etc.)                │   │
│  │ Q: Responsive requirements?                             │   │
│  │ Q: Accessibility needs?                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 7: AUTHENTICATION (if needed)                       │   │
│  │                                                          │   │
│  │ Q: Auth required?                                       │   │
│  │ Q: Auth method? (email/password, OAuth, etc.)           │   │
│  │ Q: User roles needed?                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 8: INTEGRATIONS                                     │   │
│  │                                                          │   │
│  │ Q: Third-party APIs?                                    │   │
│  │ Q: Payment processing?                                  │   │
│  │ Q: Analytics?                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 9: SUCCESS CRITERIA                                 │   │
│  │                                                          │   │
│  │ Q: What defines "done"?                                 │   │
│  │ Q: Key acceptance criteria?                             │   │
│  │ Q: Quality requirements?                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ GENERATION                                               │   │
│  │                                                          │   │
│  │ 1. Create .ralph/tasksets/{name}/ directory             │   │
│  │ 2. Generate .ralph/tasksets/{name}/tasks.json           │   │
│  │ 3. Generate .ralph/tasksets/{name}/prd.md               │   │
│  │ 4. Generate .ralph/tasksets/{name}/memories.md          │   │
│  │ 5. Create symlink .ralph/current-taskset                │   │
│  │ 6. Generate PROMPT.md (with symlink paths)              │   │
│  │ 7. Copy ralph.sh                                        │   │
│  │ 8. Create .ralph/tasksets/{name}/config.json            │   │
│  │ 9. Create empty .ralph/tasksets/{name}/activity.log     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Question Details

### Step 0: Task Set Name

**Ask:**
- "What would you like to name this task set?"
- "Examples: 'initial', 'auth-feature', 'test-coverage'"

**Validation:**
- Lowercase only
- Alphanumeric and hyphens only
- No spaces
- Default: "initial"

### Step 1: Problem Definition

**Ask:**
- "What problem are you trying to solve with this project?"
- "Who currently experiences this problem?"
- "What happens if this problem isn't solved?"

**Good answers include:**
- Specific pain points
- Target user context
- Current workarounds

### Step 2: Target Audience

**Ask:**
- "Who is the primary user of this application?"
- "What's their technical level?"
- "In what context will they use this?"

**Consider:**
- Developers vs. end users
- Mobile vs. desktop
- Frequency of use

### Step 3: Core Features

**Ask:**
- "What are the 3-5 must-have features for v1?"
- "What features can wait for v2?"
- "What's the absolute minimum for a working product?"

**Goal:** Keep scope tight for Ralph to complete autonomously.

### Step 4: Tech Stack

**Ask:**
- "Do you have a preferred framework?"
- "TypeScript or JavaScript?"
- "Any specific tools you want to use?"

**Defaults if not specified:**
- React + TypeScript
- Vite for bundling
- Tailwind for styling

### Step 5: Architecture

**Ask:**
- "Frontend only, fullstack, or API only?"
- "Do you need a database?"
- "Any external services or APIs?"

**Options:**
- Static site / SPA
- Full-stack with backend
- API only
- Serverless

### Step 6: UI/UX

**Ask:**
- "What visual style? (minimal, playful, corporate)"
- "Does it need to work on mobile?"
- "Any accessibility requirements?"

### Step 7: Authentication

**Ask:**
- "Does this need user authentication?"
- "What auth method? (email/password, OAuth, magic links)"
- "Different user roles needed?"

### Step 8: Integrations

**Ask:**
- "Any third-party APIs to integrate?"
- "Payment processing needed?"
- "Analytics or tracking?"

### Step 9: Success Criteria

**Ask:**
- "What makes this project 'done'?"
- "Key things that must work?"
- "Quality bar? (tests, accessibility, performance)"

---

## Task Generation

After discovery, generate tasks following this structure:

### Task Categories

| Category | Description | Example |
|----------|-------------|---------|
| `setup` | Project initialization | "Initialize React project" |
| `feature` | Core functionality | "Add user login form" |
| `integration` | External services | "Connect to Stripe API" |
| `styling` | UI/UX work | "Add responsive styles" |
| `testing` | Test coverage | "Write unit tests" |

### Task Ordering

1. **Setup tasks first** - Must complete before features
2. **Core features** - In dependency order
3. **Integrations** - After related features
4. **Styling** - Can often be last
5. **Testing** - Parallel or at end

### Task Granularity

Each task should be:
- Completable in ONE iteration
- Independently verifiable
- Clear in scope

**Too big:**
> "Build the entire authentication system"

**Right size:**
> "Create login form component"
> "Add login API endpoint"
> "Connect form to API"
> "Add session management"

---

## File Generation

### .ralph/tasksets/{name}/tasks.json

```json
{
  "project": "{project-name}",
  "taskset": "{taskset-name}",
  "created": "{ISO-timestamp}",
  "tasks": [
    {
      "id": "setup-001",
      "category": "setup",
      "description": "{description}",
      "steps": ["{step1}", "{step2}"],
      "passes": false,
      "iteration_completed": null
    }
  ]
}
```

### .ralph/tasksets/{name}/prd.md

Human-readable requirements document with:
- Problem statement
- Target audience
- Feature list
- Tech stack decisions
- Success criteria

### .ralph/tasksets/{name}/memories.md

Empty template for persistent learnings:
```markdown
# Memories: {taskset-name}

> Persistent learnings that survive across iterations.

## Patterns
<!-- Code patterns discovered -->

## Decisions
<!-- Design decisions made -->

## Fixes
<!-- Solutions to problems -->

## Context
<!-- Project context -->
```

### PROMPT.md

Instructions for each iteration, including:
- Reference to current-taskset/tasks.json and activity.log
- Reference to current-taskset/memories.md
- Start commands for the tech stack
- Verification commands
- Hat-lite workflow instructions
- Completion signal format

### ralph.sh

Copy from plugin's scripts directory, or generate if needed.

### .ralph/tasksets/{name}/config.json

```json
{
  "project": "{project-name}",
  "taskset": "{taskset-name}",
  "ralph_version": "2.0.0",
  "max_iterations": 20,
  "tech_stack": "{stack}",
  "verification_commands": {
    "lint": "npm run lint",
    "typecheck": "npm run typecheck",
    "test": "npm run test"
  }
}
```

### .ralph/current-taskset

Symlink pointing to the active task set:
```bash
ln -sfn tasksets/{name} .ralph/current-taskset
```
