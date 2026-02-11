# Ralph PRD Examples

## Example 1: Todo App PRD

### Discovery Session

```
Q: What problem are you solving?
A: I need a simple way to track daily tasks without complex features.

Q: Who is the target audience?
A: Just me - a developer who wants a minimal todo app.

Q: What are the 3-5 core features?
A: Add todos, mark complete, delete todos, persist to localStorage.

Q: Tech stack?
A: React with TypeScript, Vite, Tailwind CSS.

Q: Architecture?
A: Frontend only, localStorage for persistence.

Q: UI/UX?
A: Minimal, clean, works on desktop.

Q: Auth needed?
A: No.

Q: Integrations?
A: None.

Q: Success criteria?
A: I can add, complete, and delete todos. Data persists on refresh.
```

### Generated tasks.json

(timestamps are generated at creation time)

```json
{
  "project": "simple-todo",
  "created": "2026-02-01T10:00:00Z",
  "tasks": [
    {
      "id": "setup-001",
      "category": "setup",
      "description": "Initialize Vite + React + TypeScript project",
      "steps": [
        "Run npm create vite@latest . -- --template react-ts",
        "Install dependencies",
        "Install Tailwind CSS",
        "Verify dev server starts"
      ],
      "verificationTier": "build",
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "feat-001",
      "category": "feature",
      "description": "Create TodoList component with state",
      "steps": [
        "Create src/components/TodoList.tsx",
        "Add useState for todos array",
        "Render list of todo items"
      ],
      "verificationTier": "build",
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "feat-002",
      "category": "feature",
      "description": "Add todo creation functionality",
      "steps": [
        "Create AddTodo component",
        "Add input field and submit handler",
        "Connect to parent state"
      ],
      "verificationTier": "build",
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "feat-003",
      "category": "feature",
      "description": "Add complete and delete functionality",
      "steps": [
        "Add toggle complete handler",
        "Add delete handler",
        "Style completed items differently"
      ],
      "verificationTier": "build",
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "feat-004",
      "category": "feature",
      "description": "Add localStorage persistence",
      "steps": [
        "Save todos to localStorage on change",
        "Load todos from localStorage on mount",
        "Verify persistence across page refresh"
      ],
      "verificationTier": "build",
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "style-001",
      "category": "styling",
      "description": "Apply Tailwind CSS styling",
      "steps": [
        "Style the layout",
        "Style todo items",
        "Add hover and focus states"
      ],
      "verificationTier": "visual",
      "passes": false,
      "iteration_completed": null
    },
    {
      "id": "verify-001",
      "category": "verification",
      "description": "Final visual verification of complete todo app",
      "steps": [
        "Start dev server",
        "Open http://localhost:5173 with playwright-cli",
        "Take snapshot to verify layout renders correctly",
        "Add a todo item, mark it complete, delete another",
        "Screenshot final state",
        "Verify localStorage persistence by refreshing",
        "Stop dev server"
      ],
      "verificationTier": "e2e",
      "passes": false,
      "iteration_completed": null
    }
  ]
}
```

---

## Example 2: REST API PRD

### Discovery Session

```
Q: What problem are you solving?
A: Need a user management API for a mobile app.

Q: Target audience?
A: Mobile app developers consuming this API.

Q: Core features?
A: User CRUD, authentication, password reset.

Q: Tech stack?
A: Node.js, Express, TypeScript, PostgreSQL.

Q: Architecture?
A: REST API with JWT auth, deployed to Railway.

Q: UI/UX?
A: N/A - API only.

Q: Auth?
A: JWT tokens, email/password login.

Q: Integrations?
A: SendGrid for email.

Q: Success criteria?
A: All endpoints work, JWT auth functional, documented with OpenAPI.
```

### Generated tasks.json

```json
{
  "project": "user-api",
  "tasks": [
    {
      "id": "setup-001",
      "category": "setup",
      "description": "Initialize Express + TypeScript project",
      "steps": [
        "npm init",
        "Install Express, TypeScript, dependencies",
        "Configure tsconfig.json",
        "Create basic server.ts"
      ],
      "verificationTier": "build",
      "passes": false
    },
    {
      "id": "setup-002",
      "category": "setup",
      "description": "Set up PostgreSQL with Prisma",
      "steps": [
        "Install Prisma",
        "Create user schema",
        "Run initial migration"
      ],
      "verificationTier": "build",
      "passes": false
    },
    {
      "id": "feat-001",
      "category": "feature",
      "description": "Create user CRUD endpoints",
      "steps": [
        "GET /users",
        "GET /users/:id",
        "POST /users",
        "PUT /users/:id",
        "DELETE /users/:id"
      ],
      "verificationTier": "api",
      "passes": false
    },
    {
      "id": "feat-002",
      "category": "feature",
      "description": "Implement JWT authentication",
      "steps": [
        "POST /auth/login",
        "POST /auth/register",
        "JWT token generation",
        "Auth middleware"
      ],
      "verificationTier": "api",
      "passes": false
    },
    {
      "id": "feat-003",
      "category": "feature",
      "description": "Add password reset flow",
      "steps": [
        "POST /auth/forgot-password",
        "POST /auth/reset-password",
        "Token generation and validation"
      ],
      "verificationTier": "build",
      "passes": false
    },
    {
      "id": "int-001",
      "category": "integration",
      "description": "Integrate SendGrid for email",
      "steps": [
        "Install SendGrid SDK",
        "Create email service",
        "Send verification and reset emails"
      ],
      "verificationTier": "build",
      "passes": false
    },
    {
      "id": "test-001",
      "category": "testing",
      "description": "Add API tests",
      "steps": [
        "Install Jest and Supertest",
        "Test auth endpoints",
        "Test user CRUD"
      ],
      "verificationTier": "build",
      "passes": false
    },
    {
      "id": "verify-001",
      "category": "verification",
      "description": "Final API verification of all endpoints",
      "steps": [
        "Start server",
        "curl POST /auth/register with test user",
        "curl POST /auth/login and capture JWT",
        "curl GET /users with JWT header, verify 200",
        "curl POST /users, PUT /users/:id, DELETE /users/:id",
        "Verify all status codes and response bodies",
        "Stop server"
      ],
      "verificationTier": "api",
      "passes": false
    }
  ]
}
```

---

## Example 3: Quick PRD with Description

If you provide a description directly:

```bash
/create-prd "Build a markdown note-taking app with React"
```

The wizard will pre-fill assumptions and ask only clarifying questions:

```
Based on "Build a markdown note-taking app with React", I'll assume:
- React + TypeScript + Vite
- Markdown editor with preview
- localStorage for persistence
- Minimal styling

Is this correct? (y/n/modify)
```

---

## Anti-Patterns to Avoid

### Too Many Features

❌ **Bad:**
```
Features: User auth, real-time collaboration, version history,
AI suggestions, export to PDF, mobile app, team workspaces...
```

✅ **Good:**
```
Features: Create notes, edit with markdown, save to localStorage.
```

### Vague Descriptions

❌ **Bad:**
```
Description: Make a modern web app
```

✅ **Good:**
```
Description: Create a note-taking app that supports markdown
formatting with live preview
```

### Missing Success Criteria

❌ **Bad:**
```
Success: It works
```

✅ **Good:**
```
Success:
- Can create, edit, delete notes
- Markdown renders correctly
- Notes persist across sessions
- Works on Chrome and Firefox
```

---

## Anti-Patterns: Discovery Question Specificity

When discovery involves destructive operations, vague questions lead to user confusion about scope.

### File Deletion

❌ **Vague:**
```
Q: Should I clean up the old components?
A: Yes, go ahead.
```

✅ **Specific:**
```
Q: I will delete these 3 files (47 lines total):
   - src/components/OldHeader.tsx (18 lines)
   - src/components/OldFooter.tsx (22 lines)
   - src/components/OldNav.tsx (7 lines)
   The new Header.tsx, Footer.tsx, and Nav.tsx are NOT affected.
   Should I proceed?
A: Yes, delete those 3 files.
```

### Dependency Removal

❌ **Vague:**
```
Q: Should I remove the unused packages?
A: Sure.
```

✅ **Specific:**
```
Q: I found 2 unused dependencies to remove:
   - lodash (used nowhere after refactor)
   - moment (replaced by date-fns in src/utils/date.ts)
   Keeping: react, react-dom, date-fns, tailwindcss (all actively used).
   Should I run `npm uninstall lodash moment`?
A: Yes, remove both.
```

### Route/Page Removal

❌ **Vague:**
```
Q: The old pages aren't needed anymore, right?
```

✅ **Specific:**
```
Q: Task says to remove the legacy dashboard. This will delete:
   - src/pages/Dashboard.tsx (142 lines) — the old dashboard
   - src/pages/DashboardSettings.tsx (89 lines) — old settings panel
   NOT affected: src/pages/NewDashboard.tsx (the replacement)
   The sidebar link in Layout.tsx will be updated to point to NewDashboard.
   Should I proceed?
```

---

## Example: Final Verification Task

Every task set should end with a verification task that confirms the complete application works.

### UI Project (verificationTier: "visual" or "e2e")

```json
{
  "id": "verify-001",
  "category": "verification",
  "description": "Final visual verification of complete application",
  "steps": [
    "Start dev server",
    "Open http://localhost:5173 with playwright-cli",
    "Take snapshot to verify page structure",
    "Screenshot the main page",
    "Navigate to each route and screenshot",
    "Verify no blank pages or broken layouts",
    "Stop dev server"
  ],
  "verificationTier": "visual",
  "passes": false,
  "iteration_completed": null
}
```

### API Project (verificationTier: "api")

```json
{
  "id": "verify-001",
  "category": "verification",
  "description": "Final API verification of all endpoints",
  "steps": [
    "Start server",
    "curl each endpoint with valid auth",
    "Verify all return expected status codes",
    "Verify response bodies match schema",
    "Test error cases (401, 404, 422)",
    "Stop server"
  ],
  "verificationTier": "api",
  "passes": false,
  "iteration_completed": null
}
```
