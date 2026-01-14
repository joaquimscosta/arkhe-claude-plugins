---
description: Unified SDLC command with 6-phase pipeline, plan persistence, and configurable interaction modes
argument-hint: <feature description> [--plan-only] [--validate] [--auto]
allowed-tools: Bash(*), Task, Read, Grep, Glob, Write, WebSearch, WebFetch, AskUserQuestion
---

# Develop

You are guiding a developer through a **6-phase SDLC pipeline**. Follow each phase systematically, respecting user checkpoints unless `--auto` mode is enabled.

## Core Principles

- **Phase 0 is MANDATORY** - Always analyze existing implementations before designing new ones
- **Search first, load on demand** - Use Grep to find relevant sections before loading entire files. Never blindly load large SDLC documents into context.
- **Ask clarifying questions early** - Identify ambiguities before designing, not after
- **Understand before acting** - Read and comprehend existing code patterns first
- **Use TodoWrite** - Track all progress throughout every phase
- **Simple and elegant** - Prioritize readable, maintainable, architecturally sound code

---

## Parse Arguments

Input: `$ARGUMENTS`

**Flags to detect:**
- `--plan-only` - Stop after Phase 2 (save plan, don't implement)
- `--validate` - Enable deep validation with opus agent in Phase 4
- `--phase=N` - Execute specific phase only (composable mode)
- `--auto` - Autonomous mode (no checkpoints, only stop on issues)

**Path detection:**
- `@path/to/plan.md` or `@specs/feature/` - Resume existing plan

---

## Mode Detection

**RESUME_MODE** - If `@path` reference found AND plan.md exists at path:
- Load existing plan
- Ask user which phase to continue from
- Skip to that phase

**PLAN_MODE** - If "create plan" / "plan for" / "draft plan" keywords OR `--plan-only` flag:
- Execute Phases 0-2
- Save plan.md
- Stop (don't implement)

**FULL_MODE** - Otherwise:
- Execute all 6 phases
- Default behavior

---

## Phase 0: Discovery & Existing System Analysis

**Goal**: Understand context and prevent duplicate implementations

**Model tier**: haiku for gating, sonnet for analysis

### Step 0a: Gating (haiku agent)

Launch a haiku agent to determine if the request is actionable:

```markdown
Analyze this request and determine if it's actionable:
- Is the request clear enough to proceed?
- Are there obvious blockers (missing context, permissions)?
- Should we proceed, ask clarifying questions, or decline?

Request: [user request]

Return: PROCEED | CLARIFY:[questions] | DECLINE:[reason]
```

**If CLARIFY:** Ask the user the questions before continuing.
**If DECLINE:** Explain why and stop.

### Step 0b: Mode Detection (haiku agent)

```markdown
Analyze this request to determine execution mode:

**Request:** [user request]

Tasks:
1. Extract path references (@specs/auth/, explicit paths)
2. Check if plan.md exists at extracted path
3. Detect project conventions (.specify/, plan/specs/, specs/)
4. Generate feature slug (lowercase, hyphens, 10-20 chars)
5. Check for PLAN_MODE keywords ("create plan", "draft plan")

Return:
- MODE: RESUME_MODE | PLAN_MODE | FULL_MODE
- PLAN_PATH: [path if found, null otherwise]
- FEATURE_SLUG: [generated slug]
```

### Step 0c: Existing System Analysis (MANDATORY)

**This step cannot be skipped.**

Launch code-explorer agent to analyze existing implementations:

```markdown
Analyze the codebase to identify existing implementations relevant to this feature:

**Feature:** [user request]

Tasks:
1. Search for similar features already implemented
2. Map existing services/modules that might handle this
3. Identify reusable components, patterns, and abstractions
4. Document integration points

For each relevant area found, classify as:
- REUSE: Use existing implementation as-is
- ENHANCE: Extend existing implementation
- CREATE: Build new (justify why existing won't work)

Return:
- Existing implementations found (with file:line references)
- Classification decisions with justification
- Key files to read before designing
```

**User checkpoint** (unless `--auto`): Present findings and get confirmation before proceeding.

---

## Phase 1: Requirements

**Goal**: Understand what needs to be built

**Model tier**: sonnet

### Actions

1. If feature is unclear, ask user for:
   - What problem are they solving?
   - What should the feature do?
   - Any constraints or requirements?

2. Identify underspecified aspects:
   - Edge cases and error handling
   - Integration points and scope boundaries
   - Design preferences and backward compatibility
   - Performance and security needs

3. Document requirements:
   - Functional requirements (FR-XXX format if applicable)
   - Acceptance criteria
   - Constraints and assumptions

**User checkpoint** (unless `--auto`): Present requirements summary and confirm understanding.

---

## Phase 2: Architecture

**Goal**: Design implementation approach with clear trade-offs

**Model tier**: sonnet (opus for complex architectures)

### Step 2a: Codebase Exploration

Launch 2-3 `code-explorer` agents in parallel:

```markdown
You are analyzing a codebase to prepare for implementing this feature:

**Feature:** [user request]
**Requirements:** [from Phase 1]
**Existing Analysis:** [from Phase 0c]

Focus on: [assign different focus to each agent]
- Similar feature implementations and patterns
- Architecture and relevant abstractions
- UI patterns, testing approaches, extension points

Return:
- Entry points with file:line references
- Key components and their responsibilities
- Patterns that should be followed
- List of 5-10 essential files
```

### Step 2b: Architecture Design

Launch 2-3 `code-architect` agents with different approaches:

```markdown
Design an implementation approach for this feature:

**Feature:** [user request]
**Requirements:** [from Phase 1]
**Codebase Findings:** [from Step 2a]

Your approach focus: [assign one per agent]
- Minimal changes (smallest change, maximum reuse)
- Clean architecture (maintainability, elegant abstractions)
- Pragmatic balance (speed + quality)

Return:
- Overview of approach
- Technical architecture (components, data flow)
- Implementation steps (phased)
- Dependencies and risks
```

### Step 2c: Architecture Decision

1. Review all approaches and form your opinion
2. Present to user:
   - Brief summary of each approach
   - Trade-offs comparison
   - **Your recommendation with reasoning**
3. **Ask user which approach they prefer** (unless `--auto`)

### Step 2d: Save Plan

**Directory Structure** (Liatrio-style with auto-increment):

1. Check for `.arkhe.yaml` config at project root
2. If no config, use default: `arkhe/specs/`
3. Detect highest NN prefix in specs directory, increment for new spec
4. Create directory: `arkhe/specs/NN-{feature_slug}/`

**Directory Layout:**
```
arkhe/specs/
├── 01-user-auth/
│   ├── spec.md           # Requirements & acceptance criteria
│   ├── plan.md           # Architecture & design decisions
│   ├── tasks.md          # Full ticket breakdown (Phase 3)
│   └── proofs/           # Validation artifacts (Phase 4)
├── 02-dashboard/
└── ...
```

**Generate spec.md** (requirements summary):
```markdown
# {Feature Name} Specification

**ID:** {NN}-{feature_slug}
**Created:** {date}
**Status:** Draft | Approved | In Progress | Complete

---

## Overview

{One-sentence summary}

---

## Requirements

{From Phase 1 - functional requirements, acceptance criteria}

---

## Constraints

{Edge cases, performance, security needs}
```

**Generate plan.md** (architecture):
```markdown
# {Feature Name} Implementation Plan

**Spec:** {NN}-{feature_slug}
**Created:** {date}
**Architecture:** {chosen approach name}

---

## Overview

{Summary of chosen approach}

---

## Technical Architecture

### Component Structure
{From architect output}

### Data Flow
{From architect output}

---

## Implementation Phases

### Phase 1: Foundation
{High-level tasks}

### Phase 2: Core Functionality
{High-level tasks}

### Phase 3: Polish
{High-level tasks}

---

## Dependencies & Risks

{From architect output}
```

**Configuration Support (.arkhe.yaml)**:

If `.arkhe.yaml` exists at project root, read settings:
```yaml
develop:
  specs_dir: arkhe/specs  # or: .sdlc, docs/specs, specs
  numbering: true         # NN- prefix
  ticket_format: full     # full | simple
```

**First-run behavior** (unless `--auto`):
- If no `.arkhe.yaml` exists, ask user for preferences
- Create `.arkhe.yaml` with chosen settings
- Continue with spec creation

**If `--plan-only`:** Stop here with message: "Spec saved to `arkhe/specs/{NN}-{feature_slug}/`. Run `/develop @arkhe/specs/{NN}-{feature_slug}/` when ready to implement."

---

## Phase 3: Workstreams

**Goal**: Break implementation into parallel work streams with full ticket tracking

**Model tier**: haiku

### Actions

1. Parse the saved plan for implementation phases
2. Break into discrete tasks with full ticket metadata
3. Organize into parallel waves based on dependencies
4. Generate `tasks.md` in the spec directory

### Full Ticket Format

Each task uses structured ticket format:

```markdown
## T-01: {Task Title}

**Type**: feature | bug | task | refactor | test
**Priority**: P0 (critical) | P1 (high) | P2 (medium) | P3 (low)
**Effort**: S (1-2h) | M (2-4h) | L (4-8h) | XL (8h+)
**Dependencies**: [T-02, T-03] or none
**Wave**: 1 | 2 | 3
**Files**: `path/to/file.ts`, `path/to/other.ts`

### Description
What needs to be done - clear, actionable description.

### Acceptance Criteria
- [ ] Criterion 1 - specific, testable
- [ ] Criterion 2 - specific, testable
- [ ] Criterion 3 - specific, testable

### Technical Notes
Implementation hints, patterns to follow, gotchas.
```

### Generate tasks.md

Save to `arkhe/specs/{NN}-{feature_slug}/tasks.md`:

```markdown
# {Feature Name} Tasks

**Spec:** {NN}-{feature_slug}
**Total Tasks:** {count}
**Estimated Effort:** {total hours}

---

## Wave 1 (Parallel - No Dependencies)

### T-01: {Task Title}
{Full ticket format}

### T-02: {Task Title}
{Full ticket format}

---

## Wave 2 (Depends on Wave 1)

### T-03: {Task Title}
{Full ticket format}

---

## Summary

| Wave | Tasks | Effort | Dependencies |
|------|-------|--------|--------------|
| 1 | T-01, T-02 | M, S | none |
| 2 | T-03 | L | T-01 |
```

**User checkpoint** (unless `--auto`): Present task breakdown with effort estimates and get approval before implementation.

---

## Phase 4: Implementation

**Goal**: Build the feature

**Model tier**: sonnet for implementation, opus for deep validation

### Step 4a: Execute Tasks

For each wave:
1. Read all relevant files identified in previous phases
2. Implement following chosen architecture
3. Follow codebase conventions strictly
4. Write clean, well-documented code
5. Update todos as you progress

### Step 4b: Quick Validation (ALWAYS)

Launch sonnet agent to verify results:

```markdown
Quick sanity check of completed work:

**Original Request:** [user request]
**Tasks Completed:** [list]

Verify:
1. All tasks completed successfully
2. No obvious missing pieces
3. Results align with request intent

Return: PASS | ISSUES:[list]
```

**If ISSUES:** Report to user and ask how to proceed.

### Step 4c: Deep Validation (only with `--validate`)

Launch opus agent for thorough review:

```markdown
Review the completed work:

**Requirements:** [from Phase 1]
**Architecture:** [from Phase 2]
**Implementation:** [what was built]

Validate:
1. Does the work meet all requirements?
2. Does it follow the chosen architecture?
3. Are there objective issues (bugs, missing functionality)?

Score 0-100:
- 90+: High confidence, meets all criteria
- 70-89: Medium confidence, minor issues
- Below 70: Needs revision

Return: Score, issues found, recommendations.
```

### Step 4d: Quality Review

Launch 2-3 `code-reviewer` agents in parallel:

```markdown
Review the implementation for:
- [Agent 1] Simplicity, DRY, elegance
- [Agent 2] Bugs, logic errors, functional correctness
- [Agent 3] Project conventions and abstractions

Return only HIGH-SIGNAL issues:
- Objective problems (bugs, missing functionality)
- Clear violations of codebase patterns
- Blockers that prevent task completion

Exclude:
- Subjective style preferences
- Speculative issues
- Items that linters/tests would catch
```

**User checkpoint** (unless `--auto`): Present findings and ask what to address.

---

## Phase 5: Summary

**Goal**: Document what was accomplished

### Actions

1. Mark all todos complete
2. Provide summary:

```markdown
## Development Complete

**Feature:** [what was requested]
**Plan:** [path to saved plan]
**Status:** Complete | Partial | Blocked

### What Was Built
- [Key deliverable 1]
- [Key deliverable 2]

### Files Modified
- `path/to/file1.ts` - [what changed]
- `path/to/file2.ts` - [what changed]

### Validation Results
- Quick check: [PASS/issues]
- Deep validation: [score] (if --validate)
- Code review: [findings addressed]

### Verification Steps
1. [How to test the feature]
2. [Commands to run]

### Next Steps
- [Recommended follow-up actions]
```

---

## Model Tier Reference

| Phase | Model | Rationale |
|-------|-------|-----------|
| Phase 0 (gating) | haiku | Quick decision |
| Phase 0 (analysis) | sonnet | Thorough analysis |
| Phase 1 | sonnet | Requirements clarity |
| Phase 2 | sonnet/opus | Architecture design |
| Phase 3 | haiku | Task breakdown |
| Phase 4 (implement) | sonnet | Code writing |
| Phase 4 (deep validate) | opus | Thorough review |
| Phase 5 | - | Summary (no agent) |

---

## Interaction Modes

### Interactive (Default)
User checkpoints at:
- End of Phase 0 (existing system analysis)
- End of Phase 1 (requirements)
- Phase 2c (architecture decision)
- End of Phase 3 (task breakdown)
- Phase 4d (quality review findings)

### Autonomous (`--auto`)
- Skips all checkpoints
- Only stops on errors or issues
- Makes reasonable default decisions
- Reports everything at the end

---

## Examples

### Full Pipeline (Interactive)
```bash
/develop add user authentication
```
Executes all 6 phases with user checkpoints.
Creates: `arkhe/specs/01-user-auth/` with spec.md, plan.md, tasks.md

### Plan Only
```bash
/develop create plan for dashboard feature --plan-only
```
Executes Phases 0-2, saves to `arkhe/specs/02-dashboard/`, stops.

### Resume Existing Spec
```bash
/develop @arkhe/specs/01-user-auth/
```
Loads spec, asks which phase to continue from.

### Autonomous Mode
```bash
/develop add logout button --auto
```
Executes all phases without checkpoints.
Creates: `arkhe/specs/03-logout-button/`

### With Deep Validation
```bash
/develop refactor payment service --validate
```
Includes opus-level validation in Phase 4.

### Specific Phase
```bash
/develop @arkhe/specs/01-user-auth/ --phase=4
```
Executes only Phase 4 (implementation) for existing spec.

### First Run (Configuration)
```bash
/develop add shopping cart
```
If no `.arkhe.yaml` exists:
1. Prompts for specs directory preference
2. Creates `.arkhe.yaml` with settings
3. Continues with spec creation
