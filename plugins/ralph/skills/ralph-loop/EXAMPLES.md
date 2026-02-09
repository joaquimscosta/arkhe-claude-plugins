# Ralph Loop Examples

## Example 1: Simple Web App

### Setup

```bash
mkdir my-todo-app && cd my-todo-app
/create-prd
# Answer: "Build a simple todo app with React"
```

### Generated tasks.json

```json
{
  "project": "my-todo-app",
  "created": "2026-02-01T10:00:00Z",
  "tasks": [
    {
      "id": "setup-001",
      "category": "setup",
      "description": "Initialize React project with Vite",
      "steps": [
        "Run npm create vite@latest",
        "Select React + TypeScript",
        "Install dependencies",
        "Verify dev server starts"
      ],
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "feat-001",
      "category": "feature",
      "description": "Create Todo list component",
      "steps": [
        "Create TodoList component",
        "Add state for todo items",
        "Render list of todos"
      ],
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "feat-002",
      "category": "feature",
      "description": "Add new todo functionality",
      "steps": [
        "Create AddTodo component",
        "Add input field and submit button",
        "Connect to TodoList state"
      ],
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "feat-003",
      "category": "feature",
      "description": "Add complete/delete functionality",
      "steps": [
        "Add checkbox for completion",
        "Add delete button",
        "Style completed items"
      ],
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "style-001",
      "category": "styling",
      "description": "Add CSS styling",
      "steps": [
        "Style the todo list",
        "Add responsive layout",
        "Ensure accessibility"
      ],
      "passes": false,
      "iteration_completed": null
    }
  ]
}
```

### Running the Loop

```bash
./ralph.sh 10
```

### Activity Log After 3 Iterations

```
=== ITERATION 1 | 2026-02-01 10:15:00 ===
TASK: setup-001 - Initialize React project with Vite
ACTIONS:
- Ran: npm create vite@latest . -- --template react-ts
- Ran: npm install
- Verified: Dev server starts on localhost:5173
STATUS: PASS
COMMIT: a1b2c3d "feat: initialize React project with Vite and TypeScript"
---

=== ITERATION 2 | 2026-02-01 10:25:00 ===
TASK: feat-001 - Create Todo list component
ACTIONS:
- Created src/components/TodoList.tsx
- Added useState for todo items
- Implemented list rendering with map()
- Ran lint and typecheck - all pass
STATUS: PASS
COMMIT: e4f5g6h "feat: create TodoList component with state management"
---

=== ITERATION 3 | 2026-02-01 10:35:00 ===
TASK: feat-002 - Add new todo functionality
ACTIONS:
- Created src/components/AddTodo.tsx
- Added input field with controlled state
- Connected to parent via onAdd prop
- Ran lint and typecheck - all pass
STATUS: PASS
COMMIT: i7j8k9l "feat: add AddTodo component with form handling"
---
```

---

## Example 2: API Development

### Setup

```bash
mkdir my-api && cd my-api
/create-prd
# Answer: "Build a REST API for user management with Node.js and Express"
```

### Generated tasks.json

```json
{
  "project": "my-api",
  "tasks": [
    {
      "id": "setup-001",
      "category": "setup",
      "description": "Initialize Node.js project",
      "steps": ["npm init", "Install Express and TypeScript", "Configure tsconfig"],
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "feat-001",
      "category": "feature",
      "description": "Create user CRUD endpoints",
      "steps": ["GET /users", "GET /users/:id", "POST /users", "PUT /users/:id", "DELETE /users/:id"],
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "feat-002",
      "category": "feature",
      "description": "Add request validation",
      "steps": ["Install zod", "Create user schema", "Add validation middleware"],
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "test-001",
      "category": "testing",
      "description": "Add API tests",
      "steps": ["Install vitest and supertest", "Write endpoint tests", "Achieve >80% coverage"],
      "passes": false,
      "iteration_completed": null
    }
  ]
}
```

---

## Example 3: Resuming After Interruption

If the loop is interrupted (Ctrl+C, error, etc.), simply run it again:

```bash
# Loop was interrupted at iteration 5
./ralph.sh 20
```

Ralph reads the activity log and tasks.json to understand the current state and continues from where it left off.

---

## Example 4: Running with Limited Iterations

For testing or when you want more control:

```bash
# Run only 3 iterations
./ralph.sh 3

# Check progress
cat .ralph/current-taskset/tasks.json | jq '.tasks[] | select(.passes == false)'

# Continue with more iterations
./ralph.sh 10
```

---

## Example 5: Checking Status Mid-Loop

While the loop is running (in another terminal):

```bash
# See current task state
cat .ralph/current-taskset/tasks.json | jq '.tasks[] | {id, passes}'

# See recent activity
tail -n 20 .ralph/current-taskset/activity.log

# Check screenshots
ls -la screenshots/
```
