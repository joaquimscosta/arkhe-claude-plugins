# Workflow Orchestration Patterns

Detailed patterns for coordinating complex tasks with structured thinking and multi-agent execution.

## The 6-Step Orchestration Model

### Step 1: Gating

**Purpose:** Determine if the request is actionable before investing resources.

**Questions to answer:**
- Is the request clear enough to proceed?
- Are there obvious blockers (missing context, permissions)?
- Should we proceed, ask clarifying questions, or decline?

**Outcomes:**
- **PROCEED** - Request is clear, move to context discovery
- **CLARIFY** - Ask specific questions before continuing
- **DECLINE** - Explain why and stop (out of scope, impossible, etc.)

**Model:** Use haiku for quick gating decisions.

### Step 2: Context Discovery

**Purpose:** Gather relevant project context before planning.

**Actions:**
1. Locate CLAUDE.md files for project guidelines
2. Check for spec-kit directories (`.specify/`, `plan/`, `specs/`)
3. Load constitutional principles if spec-kit exists
4. Identify key files related to the request
5. Note existing patterns and conventions

**Output:** List of relevant files, constraints, and principles.

**Model:** Use haiku for quick context gathering.

### Step 3: Analysis & Planning

**Purpose:** Understand the problem and create an execution plan.

**Produce:**
1. Clear understanding of what needs to be done
2. List of parallel tasks (can run simultaneously)
3. List of sequential tasks (dependencies)
4. Success criteria for each task

**Considerations:**
- What can be parallelized?
- What must wait for other tasks?
- What specialist skills are needed?
- What are the acceptance criteria?

**Model:** Use sonnet for standard planning, opus for complex analysis (with `--validate` flag).

### Step 4: Parallel Execution

**Purpose:** Deploy specialist agents efficiently.

**Wave Pattern:**
```
Wave 1: All independent tasks (parallel)
    ↓
Wave 2: Tasks depending on Wave 1 (parallel within wave)
    ↓
Wave N: Continue until all tasks complete
```

**Agent Assignment Template:**
```markdown
You are assigned to: [task description]

**Context:** [relevant files and background]
**Deliverables:** [specific outputs expected]
**Success Criteria:** [measurable completion conditions]

Complete your task and report results.
```

**Key principle:** Maximize parallelism with multiple Task tool calls in a single response.

### Step 5: Validation (Optional)

**Purpose:** Verify results meet quality standards.

**When to use:** With `--validate` flag or for high-stakes changes.

**Scoring:**
- **90+:** High confidence, meets all criteria → Report as complete
- **70-89:** Medium confidence, minor issues → Report with caveats
- **Below 70:** Needs revision → Flag for attention

**Model:** Use opus for validation (requires deeper analysis).

### Step 6: Report

**Purpose:** Summarize results clearly.

**Template:**
```markdown
## Workflow Complete

**Request:** [original request]
**Status:** [Complete | Partial | Blocked]

### Completed
- [Task 1]: [result summary]
- [Task 2]: [result summary]

### Issues (if any)
- [Issue description and recommendation]

### Next Steps (if any)
- [Recommended follow-up actions]
```

## Model Tier Strategy

| Model | Cost | Speed | Use For |
|-------|------|-------|---------|
| haiku | Low | Fast | Gating, routing, simple context gathering |
| sonnet | Medium | Medium | Standard implementation, documentation |
| opus | High | Slower | Deep analysis, validation, complex reasoning |

**Guidelines:**
- Start with haiku for quick decisions
- Use sonnet for the bulk of work
- Reserve opus for genuinely complex analysis
- `--validate` flag enables opus-level deep validation

## Parallelism Patterns

### Independent Tasks (Parallelize)

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Task A     │  │  Task B     │  │  Task C     │
│  (tests)    │  │  (docs)     │  │  (types)    │
└─────────────┘  └─────────────┘  └─────────────┘
       ↓                ↓                ↓
       └────────────────┴────────────────┘
                        ↓
                   [Continue]
```

### Dependent Tasks (Sequential)

```
┌─────────────┐
│  Task A     │
│  (schema)   │
└─────────────┘
       ↓
┌─────────────┐
│  Task B     │
│  (models)   │
└─────────────┘
       ↓
┌─────────────┐
│  Task C     │
│  (API)      │
└─────────────┘
```

### Mixed Pattern

```
Wave 1 (parallel):
┌─────────────┐  ┌─────────────┐
│  Schema     │  │  Research   │
└─────────────┘  └─────────────┘
       ↓                ↓
Wave 2 (parallel, depends on Wave 1):
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Models     │  │  Types      │  │  Tests      │
└─────────────┘  └─────────────┘  └─────────────┘
       ↓                ↓                ↓
Wave 3 (depends on Wave 2):
┌─────────────────────────────────────────────────┐
│               Integration                        │
└─────────────────────────────────────────────────┘
```

## High-Signal Issue Filtering

**Report these (objective problems):**
- Bugs and broken functionality
- Missing required functionality
- Broken dependencies
- Clear violations of CLAUDE.md guidelines
- Blockers preventing completion

**Skip these (noise):**
- Style preferences
- Subjective suggestions
- Potential/speculative issues
- Items linters or tests catch
- Minor improvements unrelated to task

## Flag Reference

| Flag | Effect |
|------|--------|
| `--plan-only` | Stop after Phase 2, save plan without implementing |
| `--validate` | Enable opus-level deep validation in Phase 4 |
| `--phase=N` | Execute specific phase only (composable mode) |
| `--auto` | Autonomous mode (no checkpoints, only stop on issues) |

**Common Patterns:**
- `--plan-only` - Create plan for review before implementing
- `--validate` - For high-stakes or security-sensitive implementations
- `--auto` - For well-defined tasks that don't need checkpoints
- `@arkhe/specs/01-feature/` - Resume existing spec
