---

description: Extract and organize executable tasks for /speckit.tasks.
argument-hint: [plan-file] [optional-research-file] [mode: quick|strict]
---

# SpecPrep — Task Optimizer

You are the **Task Derivation Agent**.  
Transform the provided plan (and optionally research or data-model files) into a **structured, parallelizable, duplication-free task outline** ready for `/speckit.tasks`.

## Argument Parsing

Parse the command arguments as follows:
- First `@file` reference is the plan file (required)
- Second `@file` reference is the research file (optional)
- The **last positional argument** is the mode if it matches `quick` or `strict`
- If no mode is specified or the last argument is not a recognized mode, use **default behavior** (balanced extraction)

Examples:
- `/specprep:tasks @specs/002-feature/plan.md quick` → mode: quick
- `/specprep:tasks @specs/002-feature/plan.md @specs/002-feature/research.md strict` → mode: strict
- `/specprep:tasks @specs/002-feature/plan.md` → mode: default (balanced)

## Mode Behavior

- **quick** → Basic extraction of core tasks only
- **strict** → Full plan validation and coverage check
- *(default)* → Balanced extraction

## Instructions

1. **Parse input files** and extract concrete implementation actions.  
2. **Ensure tasks are**:
   - Action-oriented and specific  
   - Traced to plan sections or contracts  
   - Free of commentary or research text  
3. **Mark parallel tasks** with `[P]` and group under clear headers:  
   - Frontend / Backend / Tests / Infrastructure  
4. **Check completeness** — every phase of the plan represented; no redundancy.  
5. Output a single markdown list of tasks suitable for execution.

## Mode Examples

Here's how tasks are extracted from the same plan in each mode:

**Input Plan:**
```markdown
## Implementation Phases
1. Define data contracts and integration tests
2. Implement task storage (SQLite)
3. Build frontend task list UI
4. Add task creation form
5. Integration testing

## Technical Notes
- Use SQLite for local storage
- Frontend should be responsive
```

**Quick Mode Output:**
```markdown
## Backend
- [ ] Create SQLite schema
- [ ] Implement task CRUD operations

## Frontend
- [ ] Build task list component
- [ ] Build task creation form

## Tests
- [ ] Integration tests
```

**Strict Mode Output:**
```markdown
## Backend
- [ ] Define task data contract (Phase 1)
- [ ] Create SQLite schema for tasks (Phase 2)
- [ ] Implement task creation endpoint (Phase 2) [P]
- [ ] Implement task retrieval endpoint (Phase 2) [P]
- [ ] Implement task update endpoint (Phase 2) [P]
- [ ] Implement task deletion endpoint (Phase 2) [P]

## Frontend
- [ ] Build task list component with data contract (Phase 3)
- [ ] Connect task list to backend API (Phase 3)
- [ ] Build task creation form (Phase 4)
- [ ] Connect creation form to backend API (Phase 4)
- [ ] Add responsive styling (Phase 4) [P]

## Tests
- [ ] Write integration test for task contract (Phase 1)
- [ ] Test task creation flow (Phase 5)
- [ ] Test task retrieval flow (Phase 5) [P]
- [ ] Test task update flow (Phase 5) [P]
- [ ] Test task deletion flow (Phase 5) [P]
- [ ] E2E test: create and view tasks (Phase 5)

## Coverage Validation
✅ All phases represented
✅ All technical decisions traced to tasks
[NEEDS CLARIFICATION: Should responsive design support specific breakpoints?]
```

**Default Mode Output:**
```markdown
## Backend
- [ ] Define task data contract
- [ ] Create SQLite schema for tasks
- [ ] Implement task CRUD operations [P]

## Frontend
- [ ] Build task list component
- [ ] Build task creation form [P]
- [ ] Connect UI to backend API
- [ ] Add responsive design [P]

## Tests
- [ ] Write integration test for data contract
- [ ] Test task creation and retrieval
- [ ] E2E test: full task workflow

## Notes
[NEEDS CLARIFICATION: Priority for responsive breakpoints?]
```

## Interactive Correction (Strict Mode)

When using **strict mode**, after generating output with `[NEEDS CLARIFICATION]` markers:

1. Count the number of clarification markers
2. Ask the user: "Found N clarifications needed. Resolve interactively? [y/N]"
3. If user responds "y" or "yes":
   - Present each clarification as a question
   - Collect user responses
   - Regenerate the task list with resolved clarifications
4. If user responds "n" or "no":
   - Return the task list as-is with markers intact

### Example usage
`/specprep:tasks @specs/002-feature/plan.md @specs/002-feature/research.md`
`/specprep:tasks @specs/002-feature/plan.md strict`

### Expected output
`/speckit:tasks [optimized task text]`
