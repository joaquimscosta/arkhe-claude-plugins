# Ralph Loop Workflow

Detailed step-by-step guide for each iteration in the Ralph autonomous loop.

## Iteration Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    RALPH ITERATION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ PHASE 1: ORIENT (5% of iteration)                       │   │
│  │                                                          │   │
│  │ 1. Read .ralph/current-taskset/activity.log (last 5)    │   │
│  │ 2. Read .ralph/current-taskset/tasks.json               │   │
│  │ 3. Read .ralph/current-taskset/memories.md              │   │
│  │ 4. Identify next incomplete task                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ PHASE 2: BUILD (60% of iteration)                       │   │
│  │                                                          │   │
│  │ 1. Select ONE task where passes=false                   │   │
│  │ 2. Read task description and steps                      │   │
│  │ 3. Implement the change                                 │   │
│  │ 4. Run verification:                                    │   │
│  │    - npm run lint (if available)                        │   │
│  │    - npm run typecheck (if available)                   │   │
│  │    - npm run build (if available)                       │   │
│  │    - npm run test (if available)                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ PHASE 3: VERIFY (25% of iteration)                      │   │
│  │                                                          │   │
│  │ 1. Review implementation against acceptance criteria    │   │
│  │ 2. Visual verification (optional, via agent-browser)    │   │
│  │ 3. Update task status in tasks.json                     │   │
│  │ 4. Append entry to activity.log                         │   │
│  │ 5. Stage and commit changes                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ PHASE 4: LEARN (5% of iteration) - OPTIONAL             │   │
│  │                                                          │   │
│  │ If you learned something useful:                        │   │
│  │ Append insight to .ralph/current-taskset/memories.md    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ PHASE 5: DECIDE (5% of iteration)                       │   │
│  │                                                          │   │
│  │ Check: All tasks have passes=true?                      │   │
│  │                                                          │   │
│  │ YES → Output "RALPH_COMPLETE: All tasks verified"       │   │
│  │ NO  → End iteration (fresh context on next loop)        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Hat-Lite Roles

Ralph uses a simplified "hat" system. You switch between two personas within a single iteration.

### Builder Hat (~65% of iteration)

**Role:** Implementation Executor

**Mindset:**
- "I build things that work"
- "I follow the plan precisely"
- "I verify my own work immediately"

**Responsibilities:**
1. Pick ONE task from the task list
2. Implement according to the steps provided
3. Run verification commands (lint, typecheck, tests)
4. Document what was done

**Does NOT:**
- Question the task requirements
- Work on multiple tasks
- Skip verification steps
- Leave partial work

### Verifier Hat (~35% of iteration)

**Role:** Quality Gate

**Mindset:**
- "I ensure the work meets standards"
- "I update state accurately"
- "I commit clean, atomic changes"

**Responsibilities:**
1. Review the Builder's implementation
2. Check against acceptance criteria
3. Update task status in tasks.json
4. Append entry to activity.log
5. Create git commit

**Does NOT:**
- Re-implement the solution
- Add features not in the task
- Mark incomplete work as done
- Skip the commit step

### Hat Switching

The switch happens naturally within each iteration:

```
Builder Hat → implement task → run verification
    ↓
Verifier Hat → review work → update state → commit
```

### Why Hat-Lite?

| Full Ralph | Hat-Lite |
|------------|----------|
| Separate Builder agent | Same agent, Builder mindset |
| Separate Verifier agent | Same agent, Verifier mindset |
| Separate Confessor agent | Not used |
| Complex event system | Simple phase progression |

### Common Anti-Patterns

**Builder:**
- Working on multiple tasks → One task per iteration only
- Skipping verification → Always run lint, typecheck, tests
- Partial implementation → Complete the task fully or don't start it

**Verifier:**
- Re-implementing instead of reviewing → Review what was built, don't rebuild
- Marking incomplete work as done → Only mark pass when ALL criteria are met
- Skipping the commit → One commit per task, always

---

## Phase 1: Orient

**Goal:** Quickly understand current state from previous iterations.

### Steps

1. **Read Activity Log**
   ```bash
   # Read last 5 entries
   tail -n 50 .ralph/current-taskset/activity.log
   ```

2. **Read Task State**
   ```bash
   cat .ralph/current-taskset/tasks.json
   ```

3. **Read Memories**
   ```bash
   cat .ralph/current-taskset/memories.md
   ```
   Review any patterns, decisions, or fixes from previous iterations.

4. **Identify Next Task**
   - Find first task where `passes: false`
   - Note any failed attempts from activity log
   - Consider relevant memories

### Output
- Clear understanding of what's been done
- Specific task to work on this iteration
- Awareness of project patterns from memories

---

## Phase 2: Build (Builder Hat)

**Goal:** Complete ONE task fully.

### Steps

1. **Read Task Details**
   - Description
   - Steps to complete
   - Acceptance criteria

2. **Implement**
   - Follow the steps exactly
   - Write clean, documented code
   - Follow project conventions (check memories)

3. **Self-Verify**
   - Run linter: `npm run lint` or equivalent
   - Run type checker: `npm run typecheck` or equivalent
   - Run build: `npm run build` or equivalent
   - Run tests: `npm run test` or equivalent

### Rules
- **ONE task only** - Do not work on multiple tasks
- **Complete fully** - Don't leave partial work
- **Fix verification issues** - Don't proceed with failures

---

## Phase 3: Verify (Verifier Hat)

**Goal:** Ensure quality before marking complete.

### Steps

1. **Review Implementation**
   - Does it meet all acceptance criteria?
   - Is the code clean and documented?
   - Did all verification commands pass?

2. **Visual Verification (Optional)**
   ```bash
   # If UI changes, use agent-browser
   agent-browser open http://localhost:3000
   agent-browser screenshot screenshots/task-name.png
   ```

3. **Update Task Status**
   ```json
   // In .ralph/current-taskset/tasks.json
   {
     "id": "feat-001",
     "passes": true,
     "iteration_completed": 3
   }
   ```

4. **Log Activity**
   Append to `.ralph/current-taskset/activity.log`:
   ```
   === ITERATION 3 | 2026-02-01 14:30:00 ===
   TASK: feat-001 - Add user login form
   ACTIONS:
   - Created LoginForm component
   - Added form validation
   - Connected to auth API
   - Ran lint, typecheck, tests - all pass
   STATUS: PASS
   COMMIT: abc1234 "feat: add user login form with validation"
   ---
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: descriptive commit message"
   ```

---

## Phase 4: Learn (Optional)

**Goal:** Save useful insights for future iterations.

### When to Save a Memory

- Discovered a project pattern that's not obvious
- Found a solution to a tricky problem
- Made an architectural decision
- Learned something about a library or tool

### How to Save

Append to `.ralph/current-taskset/memories.md`:

```markdown
## 2026-02-01: Tailwind requires explicit color config

When using custom colors in Tailwind, you must add them to tailwind.config.js.
Just using `text-[#123456]` doesn't work in this project because purging removes them.

Solution: Add colors to `theme.extend.colors` in the config.

---
```

### Examples of Good Memories

- "Next.js API routes require explicit return types"
- "The project uses barrel exports - add new components to index.ts"
- "Database migrations must be run manually with `npm run migrate`"
- "Auth tokens expire after 1 hour - refresh logic is in utils/auth.ts"

---

## Phase 5: Decide

**Goal:** Determine if loop should continue or complete.

### Decision Logic

```
IF all tasks have passes=true THEN
    Output: "RALPH_COMPLETE: All tasks verified"
    EXIT
ELSE
    End iteration (loop continues with fresh context)
ENDIF
```

### Completion Signal

The exact output must be:
```
RALPH_COMPLETE: All tasks verified
```

This is detected by `ralph.sh` to exit the loop successfully.

---

## State Files

### .ralph/current-taskset/tasks.json

```json
{
  "project": "my-app",
  "taskset": "initial",
  "created": "2026-02-01T10:00:00Z",
  "tasks": [
    {
      "id": "setup-001",
      "category": "setup",
      "description": "Initialize Next.js project",
      "steps": [
        "Run create-next-app with TypeScript",
        "Install dependencies",
        "Verify dev server starts"
      ],
      "passes": true,
      "iteration_completed": 1
    },
    {
      "id": "feat-001",
      "category": "feature",
      "description": "Add user authentication",
      "steps": [
        "Create auth API endpoints",
        "Add login form",
        "Implement session management"
      ],
      "passes": false,
      "iteration_completed": null
    }
  ]
}
```

### .ralph/current-taskset/activity.log

```
=== ITERATION 1 | 2026-02-01 10:15:00 ===
TASK: setup-001 - Initialize Next.js project
ACTIONS:
- Ran: npx create-next-app@latest my-app --typescript
- Ran: npm install
- Verified: Dev server starts on localhost:3000
STATUS: PASS
COMMIT: abc1234 "feat: initialize Next.js project with TypeScript"
---

=== ITERATION 2 | 2026-02-01 10:25:00 ===
TASK: feat-001 - Add user authentication
ACTIONS:
- Created /api/auth/login endpoint
- Created /api/auth/logout endpoint
- Added JWT token handling
STATUS: IN_PROGRESS (continuing next iteration)
---
```

### .ralph/current-taskset/memories.md

```markdown
# Memories: initial

> Persistent learnings that survive across iterations.

## Patterns

## 2026-02-01: Next.js requires explicit TypeScript config

When using create-next-app, the TypeScript config isn't fully set up.
Need to manually add strict mode and paths to tsconfig.json.

---

## Decisions

## 2026-02-01: Using JWT for auth instead of sessions

Chose JWT because this is a frontend-only app with API routes.
No need for session storage on the server side.

---

## Fixes

## 2026-02-01: Tailwind utilities conflict with custom CSS

Found that using @apply with custom utilities causes build issues.
Better to use Tailwind classes directly or use CSS-in-JS.

---

## Context
```

---

## Important Principles

### One Task Per Iteration
- Prevents context exhaustion
- Ensures focused work
- Makes debugging easier

### Fresh Context Per Iteration
- Each iteration starts clean
- No accumulated context bloat
- Prevents hallucination buildup

### Memories for Continuity
- Learnings persist across iterations
- Future iterations can avoid past mistakes
- Project patterns are documented

### Verification Before Completion
- Never mark pass without verification
- Run all available checks
- Visual verification for UI changes

### Atomic Commits
- One commit per completed task
- Clear, descriptive messages
- Easy to review and revert
