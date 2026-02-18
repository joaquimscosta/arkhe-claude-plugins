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

## Step 0b-resume: Wave Progress Detection (RESUME_MODE only)

**Skip if:** FULL_MODE or PLAN_MODE

When RESUME_MODE is detected (`@path` + plan.md exists), check for wave-level progress:

### 1. Check for Wave Context Files

Use `Glob` to find `{spec_path}/wave-*-context.md` files.

### 2. Check Task Status Fields

Read `tasks.md` and check for `**Status**:` fields on each task:
- If Status fields exist: count SELECTED, DEFERRED, COMPLETED tasks
- If Status fields are missing: treat all tasks as `Status: SELECTED` (backward compatibility)

### 3. Determine Resume Point

- **If wave context files found:**
  - Find the highest numbered `wave-{N}-context.md` → Wave N is complete
  - Read the latest wave context file for summary data
  - Count remaining SELECTED tasks in subsequent waves
  - Present summary:
    ```
    "Previous session completed Wave {N} ({completed_count} tasks: T-XX to T-YY).
     Wave {N+1} has {remaining_count} remaining tasks: T-ZZ, T-AA, T-BB."
    ```

- **If no wave context files found:**
  - Fall through to existing behavior (ask which phase to continue from)
  - Skip to the existing RESUME_MODE handling below

### 4. Wave Resume Checkpoint

**Gate: Tier 2** ⚠️ (skippable with `--auto` — auto-selects "Continue next wave")

Use `AskUserQuestion`:
- **header**: "Resume"
- **question**: "{Wave progress summary}. How would you like to continue?"
- **options**:
  - { label: "Continue Wave {N+1} (Recommended)", description: "Jump to Phase 4, re-select tasks, then continue" }
  - { label: "Re-review completed work", description: "Show git diff of previous waves" }
  - { label: "Restart from a phase", description: "Choose which phase to continue from" }

**Response Handling:**
- **Continue Wave {N+1}**: Load PHASE-4-IMPLEMENTATION.md, start at Step 4.0 (Ticket Selection) for remaining waves — this lets users re-select which waves/tasks to implement before continuing
- **Re-review completed work**: Run `git diff` for previous wave commits, then re-present this checkpoint
- **Restart from a phase**: Fall through to existing phase selection behavior

---

## Step 0b-post: Create Spec Directory (FULL_MODE/PLAN_MODE only)

**Skip if:** RESUME_MODE (spec directory already exists)

For new features, create the spec directory immediately after mode detection:

### 1. Load Configuration

Read `.arkhe.yaml` from project root:
- Extract `develop.specs_dir` value (default: `arkhe/specs`)
- Extract `develop.numbering` value (default: `true`)

### 2. Determine Spec Path

If `numbering: true`:
- Use `Glob` to find existing `{specs_dir}/NNN-*/` directories (handles 2 or 3 digit prefixes)
- Detect highest numeric prefix
- Increment and zero-pad to 3 digits: NNN+1
- Full path: `{specs_dir}/{NNN+1}-{feature_slug}/`

If `numbering: false`:
- Full path: `{specs_dir}/{feature_slug}/`

### 3. Create Directory and Initial Files

Use `Bash` to create the directory structure:
```bash
mkdir -p {specs_dir}/{NNN}-{feature_slug}
```

Use `Write` tool to create placeholder files:

**spec.md** (initial):
```markdown
# {Feature Name} Specification

**Spec ID:** {NNN}-{feature_slug}
**Status:** In Progress
**Created:** {date}

---

## Summary

{Brief description from user request}

---

_Requirements will be populated in Phase 1._
```

**plan.md** (initial):
```markdown
# {Feature Name} Implementation Plan

**Spec:** {NNN}-{feature_slug}
**Status:** In Progress
**Created:** {date}

---

_Architecture will be populated in Phase 2._
```

### 4. Store Path for Later Phases

Set `spec_path = {specs_dir}/{NNN}-{feature_slug}` for use in subsequent phases.

**Log:** "Created spec directory: `{spec_path}/`"

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

Save as `{spec_path}/reuse-matrix.md` (directory was created in Step 0b-post)

**Next:** Proceed to [PHASE-1-REQUIREMENTS.md](PHASE-1-REQUIREMENTS.md)
