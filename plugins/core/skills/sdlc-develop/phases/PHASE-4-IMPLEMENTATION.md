# Phase 4: Implementation

**Goal**: Build the feature using quality gates, confession-driven review, and per-wave critique

**Model tier**: sonnet for implementation, sonnet for wave critic (opus if `--validate`)

---

## Step 4.0: Ticket Selection

**Gate: Tier 2** (skippable with `--auto` — auto-selects all tasks)

**Skip if:** RESUME_MODE and user selected "All remaining tasks" at the Resume gate (tasks already marked SELECTED, `selection_scope = ALL`, proceed directly to Step 4.1).

Before executing any wave, allow the user to select which tasks to implement in this session.

### 1. Load and Present Tasks

Read `tasks.md` and present all tasks grouped by wave. Show COMPLETED waves as read-only context:

```markdown
## Wave 1 (3 tasks) — COMPLETED
- T-01: [title] (Effort: M) — Status: COMPLETED
- T-02: [title] (Effort: S) — Status: COMPLETED
- T-03: [title] (Effort: S) — Status: COMPLETED

## Wave 2 (2 tasks, depends on Wave 1)
- T-04: [title] (Effort: L) — Status: SELECTED
- T-05: [title] (Effort: M) — Status: SELECTED
```

**Note:** Completed waves are shown for context but are not selectable. Only non-COMPLETED tasks can be selected or deferred.

### 2. Ask for Selection

Use `AskUserQuestion`:

- **header**: "Task Selection"
- **question**: "{total_count} tasks across {wave_count} waves. Which tasks to implement this session?"
- **options**:
  - { label: "Select All (Recommended)", description: "Implement all tasks across all waves" }
  - { label: "Select by Wave", description: "Choose which waves to include" }
  - { label: "Custom Selection", description: "Provide specific task IDs via text input" }

**Response Handling:**

- **Select All**: Mark all tasks as `Status: SELECTED`. Set `selection_scope = ALL` (Step 4.1b will auto-proceed for each wave).
- **Select by Wave**: Set `selection_scope = BY_WAVE`. For each wave, use `AskUserQuestion` with yes/no:
  - **header**: "Wave {N}"
  - **question**: "Wave {N} has {count} tasks ({effort}). Include this wave?"
  - **options**:
    - { label: "Include", description: "Select all tasks in Wave {N}" }
    - { label: "Skip", description: "Defer all tasks in Wave {N}" }
- **Custom Selection**: Set `selection_scope = CUSTOM`. User provides task IDs (e.g., "T-01, T-02, T-04") via "Other" text input

### 3. Update tasks.md

For each task, update the `**Status**:` field:

- Selected tasks → `Status: SELECTED`
- Non-selected tasks → `Status: DEFERRED`
- Previously completed tasks remain → `Status: COMPLETED`

### 4. Handle Edge Cases

- **All tasks already COMPLETED**: Skip to Step 4.2 (Quality & Completion Gate)
- **Resume with completed waves**: Show completed waves as read-only context, only allow selection on remaining (non-COMPLETED) waves
- **Resume with no Status fields**: Auto-add `Status: SELECTED` to all tasks (backward compatibility)
- **`--auto` mode**: Auto-select all non-COMPLETED tasks, skip this step

---

## Step 4.1: Wave Execution Loop

Execute selected tasks wave by wave. Each wave iterates through sub-steps 4.1a → 4.1f.

### Step 4.1a: Context Refresh (Fresh Context Pattern)

**Every wave starts here, including Wave 1.**

Re-read from disk to prevent context drift:

1. `{spec_path}/spec.md` — Extract FR-XXX requirements relevant to this wave's tasks
2. `{spec_path}/plan.md` — Extract architecture decisions and key patterns to follow
3. `{spec_path}/tasks.md` — Verify current Status fields, load this wave's task details
4. If `wave-{N-1}-context.md` exists — Read previous wave's summary, confessions, and critic notes

This ensures each wave works from disk truth, not accumulated context.

### Step 4.1b: Wave Confirmation

**Gate: Conditional**

- **Tier 3 (auto-proceed, log only)** if `selection_scope = ALL` — log "Wave {N}: auto-proceeded (Select All)" and continue to Step 4.1c
- **Tier 2 (skippable with `--auto`)** if `selection_scope = BY_WAVE` or `CUSTOM`

**Auto-skip if:** Wave has no SELECTED tasks (all DEFERRED or COMPLETED).

Present the wave's selected tasks:

```markdown
## Wave {N}: {selected_count} tasks

| Task | Title | Effort | Files |
|------|-------|--------|-------|
| T-XX | [title] | M | `path/to/file` |
| T-YY | [title] | S | `path/to/file` |

**Total effort:** {effort_sum}
```

Use `AskUserQuestion`:

- **header**: "Wave {N}"
- **question**: "Wave {N} has {selected_count} selected tasks ({effort}). How to proceed?"
- **options**:
  - { label: "PROCEED (Recommended)", description: "Implement all selected tasks in this wave" }
  - { label: "SKIP TASKS", description: "Defer specific tasks from this wave" }
  - { label: "SKIP WAVE", description: "Defer entire wave, move to next" }

**Response Handling:**

- **PROCEED**: Continue to Step 4.1c
- **SKIP TASKS**: User provides task IDs to defer, update `tasks.md`, re-present wave
- **SKIP WAVE**: Mark all wave tasks as DEFERRED in `tasks.md`, skip to next wave's Step 4.1a

### Step 4.1c: Implementation (Backpressure Pattern)

Implement all SELECTED tasks in this wave. The builder chooses HOW — the quality gates define WHAT must be true when done.

#### Wave Quality Gates

All 6 gates must pass before proceeding to Step 4.1d:

| # | Gate | Check Method | Pass Criteria |
|---|------|-------------|---------------|
| 1 | Task completion | Read tasks.md | All wave tasks: `Status: COMPLETED` |
| 2 | File evidence | `git diff --stat` | Changed files match task `Files` metadata |
| 3 | Tests green | Run test suite (auto-detect framework) | All tests pass |
| 4 | No placeholders | Grep changed files | Zero `TODO`/`FIXME`/`NotImplementedError` matches |
| 5 | Acceptance criteria | Map criteria to code | Each criterion has `file:line` evidence |
| 6 | Confessions recorded | Check wave-context.md | Each task has a confession block |

**Gate failure:** Fix and re-check. Gates are checked once after all wave tasks are implemented, not per-task.

**Task tracking:** Use `TaskCreate`/`TaskUpdate` for real-time progress visibility. Update `tasks.md` Status fields as tasks complete.

#### UI Implementation with Stitch (Conditional)

**Skip this section if:** No `## Design Assets` section in plan.md or status is "Skipped".

When starting a UI-related task, check if Stitch exports are available:

1. Read plan.md and locate `## Design Assets` section
2. If exports exist (`stitch_exports_path` is set):
   - For each UI component task, match to corresponding Stitch export
   - Use `AskUserQuestion` to offer `stitch-to-react` conversion
   - If accepted: invoke `Skill` tool with `skill: "stitch-to-react"`
3. If exports don't exist but were expected (status "Pending generation"):
   - Warn user, continue with manual implementation

### Step 4.1d: Confession Recording (Confession Pattern)

After implementation passes quality gates, record confessions before the wave critic reviews.

For each completed task in this wave, write a confession block to `{spec_path}/wave-{N}-context.md` under `## Confessions — Wave {N}`:

```markdown
### T-{XX}: {Task Title}
- **Shortcuts**: [What was done expediently vs. ideally, or "None"]
- **Assumptions**: [Unverified beliefs the code depends on, or "None"]
- **Uncertainties**: [Areas where confidence is low, or "None"]
- **Deviations**: [Where implementation diverged from plan.md, or "None"]
```

**Incentive framing:** The confessor is rewarded for surfacing problems, not for appearing competent. Honest confessions lead to focused, efficient review. Minimal confessions lead to broader, slower review.

### Step 4.1e: Wave Critic (Critic-Actor Pattern)

Launch a wave critic agent to review this wave's implementation. The critic focuses on confessed weak spots rather than reviewing everything equally.

**Agent model:** sonnet (or opus if `--validate` flag is set)

**Agent input:**

- Git diff for this wave (`git diff` since wave start)
- Confessions from Step 4.1d
- Quality gate results from Step 4.1c
- Relevant FR-XXX requirements from spec.md

**Agent instructions:**

```
Review this wave's implementation. Focus your review on:
1. Confessed weak spots (shortcuts, assumptions, uncertainties)
2. Quality gate results (any gates that required re-checks)
3. Cross-task interactions within this wave

Return: PASS or ISSUES (list with file:line refs and severity).

Exclude: subjective style preferences, speculative issues, items that
linters/tests would catch (quality gates already handle those).
```

**Bounded retry:**

- **If PASS:** Proceed to Step 4.1f
- **If ISSUES:** Builder fixes the listed issues, then critic re-reviews
- **After 1 rejection:** Approve with notes rather than rejecting again. Record notes in wave-context.md under `## Wave Critic Result`

### Step 4.1f: Wave Checkpoint

**Gate: Tier 2** (skippable with `--auto` — auto-continues to next wave)

**Skip if:** Wave was entirely skipped (no tasks executed).

After completing all selected tasks and passing the wave critic:

#### 1. Collect Wave Metrics

- Tasks completed in this wave (count and IDs)
- Files changed (`git diff --stat` since wave start)
- Test status (run test suite, count passing/failing)
- Commits made during this wave (`git log --oneline` since wave start)
- Wave critic verdict (PASS or notes)

#### 2. Generate Wave Context File

Use [wave-context.md.template](../templates/wave-context.md.template) to generate `{spec_path}/wave-{N}-context.md`:

- Fill in feature summary from `spec.md`
- Fill in architecture overview from `plan.md`
- Fill in completed wave data from collected metrics
- Fill in confessions from Step 4.1d
- Fill in wave critic result from Step 4.1e
- Fill in next wave details from `tasks.md` (SELECTED tasks in Wave {N+1})
- Fill in git state (branch, last commit, diff stat)
- Fill in resume instructions with `{spec_path}`

Write the file using the `Write` tool.

#### 3. Check for More Waves

- **If more waves with SELECTED tasks remain**: Present continue/stop choice
- **If all waves complete**: Log "All waves complete", proceed to Step 4.2

#### 4. Continue or Stop

Use `AskUserQuestion`:

- **header**: "Wave Complete"
- **question**: "Wave {N} complete: {tasks_done} tasks, {files_changed} files changed, {tests_passing}/{tests_total} tests passing. Critic: {verdict}. {next_wave_summary}. How to proceed?"
- **options**:
  - { label: "CONTINUE (Recommended)", description: "Proceed to Wave {N+1} in current session" }
  - { label: "STOP", description: "Save context, copy resume command to clipboard, and exit" }

**Response Handling:**

- **CONTINUE**: Proceed to Step 4.1a for Wave {N+1}
- **STOP**: Save wave context, copy resume command to clipboard, display resume instructions, and exit Phase 4 (skip Step 4.2):
  1. Use `Bash` tool: `printf '/core:develop @{spec_path}/' | pbcopy` (macOS) or equivalent
  2. Display:

  ```
  Wave {N} context saved to {spec_path}/wave-{N}-context.md
  Resume command copied to clipboard.

  To resume in this session:
  /core:develop @{spec_path}/

  For a fresh context window (recommended for large features):
  1. Run /clear (or start a new conversation)
  2. Paste and run: /core:develop @{spec_path}/
  ```

**`--auto` mode**: Auto-continue to next wave without stopping.

---

## Step 4.2: Quality & Completion Gate

### TIER 1 CHECKPOINT — MANDATORY STOP

**This checkpoint CANNOT be skipped, even with `--auto`.**

Before presenting this gate:

1. Aggregate wave critic results from all waves (verdicts + notes)
2. Aggregate confessions from all waves
3. Run RULE ZERO verification:
   - [ ] All tasks marked `completed` in TaskList
   - [ ] All FR-XXX requirements have corresponding implementation
   - [ ] Files actually modified (`git diff --stat` check)
   - [ ] Tests pass (if applicable)
   - [ ] No placeholder code (`TODO`, `UnsupportedOperationException`)
   - [ ] Subagent recommendations were implemented (not just analyzed)

**Ask using AskUserQuestion:**

Present combined quality review + RULE ZERO status, then use `AskUserQuestion` tool:

- **header**: "Quality & Completion"
- **question**: "[RULE ZERO: N/6 checks passed]. [Wave critics: N waves passed, N approved with notes]. Mark implementation complete?"
- **options**:
  - { label: "APPROVE — Mark Complete", description: "All checks pass, proceed to Phase 5 summary" }
  - { label: "REVIEW — Show diff & details", description: "Show git diff, full confession report, and critic notes" }
  - { label: "FIX — Return to implementation", description: "Address issues, then re-present this gate" }
  - { label: "VERIFY UI — Test in browser", description: "Run Playwright verification before approving" }

**CRITICAL: STOP HERE. DO NOT PROCEED TO PHASE 5 UNTIL USER SELECTS "APPROVE — Mark Complete".**

**Response Handling:**

- **APPROVE — Mark Complete**: Proceed to Phase 5 (PHASE-5-SUMMARY.md)
- **REVIEW — Show diff & details**: Execute `git diff`, display confessions and critic notes from all waves, then re-present this gate
- **FIX — Return to implementation**: Return to implementation work. When done, re-run quality gates and wave critic, then re-present this gate
- **VERIFY UI — Test in browser**: Run UI verification workflow (see below), then re-present this gate

### UI Verification Workflow (when VERIFY UI selected)

Live UI verification using Playwright CLI. Refer to the `playwright:playwright-cli` skill for the full command reference.

1. **Ask for verification type:**
   - **SCREENSHOT** - Navigate to URL and capture screenshot for visual review
   - **INTERACTIVE** - Take accessibility snapshot, explore and interact with elements
   - **TEST SCENARIO** - Run specific test steps (navigate, click, fill, verify)

2. **Execute based on selection:**
   - **SCREENSHOT:** Ask for URL, open page, capture screenshot, present for confirmation
   - **INTERACTIVE:** Ask for URL, navigate, capture accessibility snapshot, offer interaction
   - **TEST SCENARIO:** Ask for test steps (or reference task acceptance criteria), execute each step, report pass/fail

3. **After verification:** Return to Quality & Completion gate with results included

---

## Output

Phase 4 produces:

- Implemented feature code
- Wave context files (`wave-{N}-context.md`) with confessions and critic results for each completed wave
- Updated `tasks.md` with Status fields (SELECTED/DEFERRED/COMPLETED)
- Quality gate results per wave
- Wave critic verdicts per wave
- UI verification status (if performed)

**Next:** Proceed to [PHASE-5-SUMMARY.md](PHASE-5-SUMMARY.md)
