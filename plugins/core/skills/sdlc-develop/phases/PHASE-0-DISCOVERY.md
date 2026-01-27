# Phase 0: Discovery & Existing System Analysis

**Goal**: Understand context and prevent duplicate implementations

**Model tier**: haiku for gating, sonnet for analysis

---

## Step 0a: Gating (haiku agent)

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

---

## Step 0b: Mode Detection (haiku agent)

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

---

## Step 0c: Existing System Analysis (MANDATORY)

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

---

## User Checkpoint

**Gate: Tier 2** ⚠️ (RECOMMENDED - skippable with `--auto`)

Present findings to user:
1. Summary of existing implementations found
2. REUSE/ENHANCE/CREATE classifications
3. Key files identified for further analysis

**Ask using AskUserQuestion:**

Present findings summary, then use `AskUserQuestion` tool:
- **header**: "Phase 0"
- **question**: "[Summary of REUSE/ENHANCE/CREATE findings]. How would you like to proceed?"
- **options**:
  - { label: "APPROVE", description: "Proceed to requirements gathering" }
  - { label: "REVIEW", description: "Show me more details about findings" }
  - { label: "MODIFY", description: "I want to change classifications" }
  - { label: "CANCEL", description: "Stop here" }

**Response Handling:**
- **APPROVE**: Proceed to Phase 1
- **REVIEW**: Show detailed findings, then re-present this checkpoint
- **MODIFY**: Allow user to change classifications, then re-present
- **CANCEL**: Stop pipeline

**STOP: Unless `--auto` is set, WAIT for user response before proceeding to Phase 1.**

---

## Output

Phase 0 produces:
- Mode determination (RESUME/PLAN/FULL)
- Feature slug for spec directory
- Existing implementation analysis
- Key files list for Phase 2

### Generate Reuse Matrix (if FULL_MODE)

Use [reuse-matrix.md.template](../templates/reuse-matrix.md.template) to document:
- REUSE/ENHANCE/CREATE classifications
- Integration points identified
- Similar components considered

Save as `{specs_dir}/{NN}-{feature_slug}/reuse-matrix.md`

**Next:** Proceed to [PHASE-1-REQUIREMENTS.md](PHASE-1-REQUIREMENTS.md)
