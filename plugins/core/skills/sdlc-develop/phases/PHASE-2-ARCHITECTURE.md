# Phase 2: Architecture

**Goal**: Design implementation approach with clear trade-offs

**Model tier**: sonnet (opus for complex architectures)

---

## Step 2a-pre: Design Asset Generation (if UI work)

**Skip this step if:** `skip_stitch_workflow = true` or no UI keywords detected in Phase 1.

### If `stitch_prompts_generated = true`:

Stitch prompts were generated in Phase 1. Now offer to generate actual screens:

1. Review the generated prompts (read from stored path)
2. Use `AskUserQuestion`:
   - **header**: "Stitch Generation"
   - **question**: "Stitch prompts are ready. Would you like to generate screens now?"
   - **options**:
     - { label: "Generate screens now (Recommended)", description: "Run generating-stitch-screens to create visual assets" }
     - { label: "Generate later", description: "Save prompts, I'll generate manually" }
     - { label: "Use prompts only", description: "Skip generation, use prompts as design reference" }

3. **Response handling:**
   - **Generate screens now**:
     1. Invoke `Skill` tool with `skill: "generating-stitch-screens"`
     2. Wait for generation to complete
     3. Store export paths: `stitch_exports_path = [generated path]`
   - **Generate later / Use prompts only**:
     1. Note in plan.md that Stitch screens should be generated before implementation
     2. Set `stitch_exports_path = null`

### If `existing_designs_path` was provided:

User provided existing design assets in Phase 1.

1. Verify the path exists using `Glob` tool
2. If path doesn't exist or is empty:
   - Warn user: "Design assets not found at [path]"
   - Offer to generate using Stitch or continue without
3. If path exists: Store for use in Phase 4

### Store in plan.md

Add to plan.md under `## Design Assets`:
```markdown
## Design Assets

**Source:** Stitch generated | User provided | None
**Prompts:** `{prompts_path}` (if applicable)
**Exports:** `{exports_path}` (if applicable)
**Status:** Ready | Pending generation | Skipped
```

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

## Step 2c-post: Save Architecture

After user approves architecture decision, persist to plan.md immediately:

1. **Read existing plan.md** from `{spec_path}/plan.md`
2. **Update with architecture:**
   - Selected approach and rationale
   - Technical architecture (components, data flow)
   - Implementation phases
   - Design assets section (if UI work)
3. **Write updated plan.md** using [plan.md.template](../templates/plan.md.template)
4. **Log:** "Architecture saved to `{spec_path}/plan.md`"

---

## Step 2d: Save Additional Artifacts (if applicable)

**Note:** Spec directory was created in Phase 0 (Step 0b-post). spec.md and plan.md were updated incrementally in Phase 1 and Step 2c-post.

Generate additional files when applicable:

1. **adr-{NNN}.md** - For significant architectural decisions (use [adr.md.template](../templates/adr.md.template))
2. **api-contract.md** - When feature includes API endpoints (use [api-contract.md.template](../templates/api-contract.md.template))
3. **data-models.md** - When feature involves database changes (use [data-models.md.template](../templates/data-models.md.template))

### First-Run Behavior

**Unless `--auto`:**
- If no `.arkhe.yaml` exists (checked in Phase 0), ask user for preferences
- Create `.arkhe.yaml` with chosen settings

---

## User Checkpoint (Architecture Decision)

**Gate: Tier 1** ⛔ (MANDATORY - cannot skip even with `--auto`)

This is a critical decision point. Architecture choices affect the entire implementation.

Present architecture options:
1. Summary of each approach
2. Trade-offs matrix
3. Your recommendation

**Ask using AskUserQuestion:**

Present architecture comparison, then use `AskUserQuestion` tool:
- **header**: "Architecture"
- **question**: "[Trade-offs summary]. Which approach do you prefer?"
- **options**: Dynamically generate 2-4 options based on approaches found:
  - For each approach: { label: "Option {A/B/C}: {name}", description: "{brief rationale}" }
  - Mark recommended option with "(Recommended)" in label
  - Always include: { label: "REQUEST CHANGES", description: "Modify requirements first" }

**Example with 2 approaches:**
```json
{
  "header": "Architecture",
  "question": "Option A optimizes for performance, Option B for simplicity. Which approach?",
  "options": [
    { "label": "Option A: Event-Driven (Recommended)", "description": "Best for scalability" },
    { "label": "Option B: Synchronous", "description": "Simpler implementation" },
    { "label": "REQUEST CHANGES", "description": "Modify requirements first" }
  ]
}
```

**CRITICAL: STOP AND WAIT for user response. This is a Tier 1 checkpoint - it CANNOT be skipped even with `--auto`.**

**Response Handling:**
- **Option A/B/C**: Proceed with selected architecture to Step 2d
- **REQUEST CHANGES**: Return to requirements phase for modifications

**CRITICAL: STOP AND WAIT for user response. This is a Tier 1 checkpoint - it CANNOT be skipped even with `--auto`.**

**Response Handling:**
- **1-3**: Proceed with selected architecture option to Step 2d
- **4**: Return to requirements phase for modifications

---

## Plan Saved Checkpoint

**Gate: Tier 3** ✅ (AUTOMATED - proceeds automatically, logs for review)

After saving plan files, automatically proceed to next phase.

Log: "Artifacts saved to `{spec_path}/`"

---

## PLAN_MODE Stop Point

**If `--plan-only` flag:**

Stop here with message:
```
Spec saved to `{spec_path}/`

Files created:
- spec.md (requirements)
- plan.md (architecture)

Run `/develop @{spec_path}/` when ready to implement.
```

---

## Output

Phase 2 produces:
- Codebase exploration findings
- Architecture design options
- Selected approach with rationale
- Saved spec.md and plan.md files

**Next:** Proceed to [PHASE-3-WORKSTREAMS.md](PHASE-3-WORKSTREAMS.md)
