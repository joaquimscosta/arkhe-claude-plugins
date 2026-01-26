# Phase 2: Architecture

**Goal**: Design implementation approach with clear trade-offs

**Model tier**: sonnet (opus for complex architectures)

---

## Step 2a: Codebase Exploration

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

---

## Step 2b: Architecture Design

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

---

## Step 2c: Architecture Decision

1. Review all approaches and form your opinion
2. Present to user:
   - Brief summary of each approach
   - Trade-offs comparison
   - **Your recommendation with reasoning**
3. **Ask user which approach they prefer** (unless `--auto`)

---

## Step 2d: Save Plan

### Load Configuration

**MANDATORY: Read `.arkhe.yaml` from project root first.**

1. If `.arkhe.yaml` exists, read `develop.specs_dir` value
2. If no config, use default: `arkhe/specs`
3. Store this value as `{specs_dir}` for all subsequent path operations
4. Detect highest NN prefix in `{specs_dir}/`, increment for new spec
5. Create directory: `{specs_dir}/NN-{feature_slug}/`

### Files to Generate

Use templates from [../templates/](../templates/):

**Always generate:**
1. **spec.md** - Requirements summary (use [spec.md.template](../templates/spec.md.template))
2. **plan.md** - Architecture design (use [plan.md.template](../templates/plan.md.template))

**Generate when applicable:**
3. **adr-{NNN}.md** - For significant architectural decisions (use [adr.md.template](../templates/adr.md.template))
4. **api-contract.md** - When feature includes API endpoints (use [api-contract.md.template](../templates/api-contract.md.template))
5. **data-models.md** - When feature involves database changes (use [data-models.md.template](../templates/data-models.md.template))

### First-Run Behavior

**Unless `--auto`:**
- If no `.arkhe.yaml` exists, ask user for preferences
- Create `.arkhe.yaml` with chosen settings
- Continue with spec creation

---

## User Checkpoint (Architecture Decision)

**Gate: Tier 1** ⛔ (MANDATORY - cannot skip even with `--auto`)

This is a critical decision point. Architecture choices affect the entire implementation.

Present architecture options:
1. Summary of each approach
2. Trade-offs matrix
3. Your recommendation

**Numbered Prompt:**
```
## Tier 1 Checkpoint: Architecture Decision ⛔

{Architecture options summary with trade-offs}

**Recommendation:** Option {X} because {reason}

1. **Option A** - {name} (RECOMMENDED)
2. **Option B** - {name}
3. **Option C** - {name}
4. **REQUEST CHANGES** - Modify requirements first

Enter choice (1-4):
```

**CRITICAL: STOP AND WAIT for user response. This is a Tier 1 checkpoint - it CANNOT be skipped even with `--auto`.**

**Response Handling:**
- **1-3**: Proceed with selected architecture option to Step 2d
- **4**: Return to requirements phase for modifications

---

## Plan Saved Checkpoint

**Gate: Tier 3** ✅ (AUTOMATED - proceeds automatically, logs for review)

After saving plan files, automatically proceed to next phase.

Log: "Plan saved to `{specs_dir}/{NN}-{feature_slug}/`"

---

## PLAN_MODE Stop Point

**If `--plan-only` flag:**

Stop here with message:
```
Spec saved to `{specs_dir}/{NN}-{feature_slug}/`

Files created:
- spec.md (requirements)
- plan.md (architecture)

Run `/develop @{specs_dir}/{NN}-{feature_slug}/` when ready to implement.
```

---

## Output

Phase 2 produces:
- Codebase exploration findings
- Architecture design options
- Selected approach with rationale
- Saved spec.md and plan.md files

**Next:** Proceed to [PHASE-3-WORKSTREAMS.md](PHASE-3-WORKSTREAMS.md)
