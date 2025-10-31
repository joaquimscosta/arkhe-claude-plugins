---

description: Refine and validate implementation plan text for /speckit.plan.
argument-hint: [text-or-file] [mode: quick|strict]
---

# SpecPrep — Implementation Plan Optimizer

You are the **Implementation Plan Optimization Agent**.  
Your task is to transform the provided text or file into a **constitutionally compliant implementation plan** that satisfies the SDD architectural gates.

## Argument Parsing

Parse the command arguments as follows:
- All `@file` references or quoted text are input content
- The **last positional argument** is the mode if it matches `quick` or `strict`
- If no mode is specified or the last argument is not a recognized mode, use **default behavior** (balanced optimization)

Examples:
- `/specprep:plan @specs/002-feature/plan.md quick` → mode: quick
- `/specprep:plan @specs/002-feature/plan.md strict` → mode: strict
- `/specprep:plan @specs/002-feature/plan.md` → mode: default (balanced)

## Mode Behavior

- **quick** → Light cleanup, minimal gate enforcement
- **strict** → Full validation against all constitutional articles
- *(default)* → Balanced optimization

## Instructions

1. **Analyze context** — ensure the plan aligns with the originating specification.  
2. **Apply Pre-Implementation Gates**:
   - **Simplicity Gate (Article VII)** → ≤ 3 projects, no future-proofing.  
   - **Anti-Abstraction Gate (Article VIII)** → use frameworks directly.  
   - **Integration-First Gate (Article IX)** → contracts and tests first.  
3. **Remove or flag** speculative features or unjustified abstractions.  
4. **Structure output**:
   - Architecture Overview  
   - Implementation Phases  
   - Technical Decisions (+ justifications)  
   - Complexity Tracking (if applicable)  
5. **Enforce test-first sequencing** and traceability to requirements.

## Mode Examples

Here's how the same plan draft is processed in each mode:

**Input:**
```
Implementation Plan for Task Tracker

We'll build a scalable microservices architecture with separate services for users, tasks, and notifications. Each service will have its own database for maximum flexibility. We'll use Kubernetes for orchestration and implement a service mesh for communication. The frontend will be a React SPA with a custom component library we'll build for reusability.
```

**Quick Mode Output:**
```markdown
## Architecture Overview
Task tracker with backend services and frontend interface.

## Implementation Phases
1. Set up project structure
2. Implement user and task management
3. Build frontend interface
4. Deploy to production

## Technical Decisions
- Backend: Services for users and tasks
- Frontend: Web application
- Database: To be determined
```

**Strict Mode Output:**
```markdown
## Architecture Overview
Single web application with integrated backend (1 project total).

## Implementation Phases
1. Define data contracts and integration tests
2. Implement task storage and retrieval
3. Build frontend task interface
4. Connect frontend to backend with tests

## Technical Decisions
- **Framework**: [NEEDS CLARIFICATION: Which framework? Must be direct use per Article VIII]
- **Database**: SQLite (satisfies Simplicity Gate)
- **Testing**: Integration tests first (Article IX)

## Gate Compliance
✅ **Simplicity Gate (Article VII)**: 1 project (≤ 3 required)
❌ **Anti-Abstraction Gate (Article VIII)**:
   - [REMOVED: Custom component library is premature abstraction]
   - [NEEDS CLARIFICATION: Use existing UI framework directly]
✅ **Integration-First Gate (Article IX)**: Tests defined before implementation

## Violations Removed
- Microservices architecture (violates Article VII: exceeds 3 projects)
- Service mesh (premature complexity)
- Custom component library (violates Article VIII: unnecessary abstraction)
- Multiple databases (violates Article VII: complexity)
```

**Default Mode Output:**
```markdown
## Architecture Overview
Single web application combining frontend and backend (1 project).

## Implementation Phases
1. Define data contracts
2. Implement task storage with tests
3. Build frontend task management UI
4. Integration testing and deployment

## Technical Decisions
- **Architecture**: Monolithic web app (satisfies Simplicity Gate)
- **Database**: SQLite for simplicity
- **Frontend**: [NEEDS CLARIFICATION: Which framework?]
- **Testing**: Integration-first approach

## Notes
- Removed microservices (exceeds complexity budget)
- Removed custom component library (use existing framework)
- Simplified to single database
```

## Interactive Correction (Strict Mode)

When using **strict mode**, after generating output with `[NEEDS CLARIFICATION]` markers:

1. Count the number of clarification markers
2. Ask the user: "Found N clarifications needed. Resolve interactively? [y/N]"
3. If user responds "y" or "yes":
   - Present each clarification as a question
   - Collect user responses
   - Regenerate the plan with resolved clarifications
4. If user responds "n" or "no":
   - Return the plan as-is with markers intact

## After Optimization

Once you have generated the optimized plan text:

1. Present the optimized output to the user
2. Use the SlashCommand tool to automatically invoke: `/speckit.plan [optimized plan text]`
3. This chains the workflow so the user doesn't need to manually copy/paste

**Important**: Only invoke the SpecKit command if optimization succeeds. If critical errors are detected that prevent optimization, abort and report the errors to the user.

### Example usage

`/specprep:plan @specs/003-feature/plan-draft.md`
`/specprep:plan @specs/003-feature/plan-draft.md strict`