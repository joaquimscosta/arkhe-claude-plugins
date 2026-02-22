# Phase 4: Implementation

**Goal**: Build the feature

**Model tier**: sonnet for implementation, opus for deep validation

---

## Step 4.0: Ticket Selection

**Gate: Tier 2** ⚠️ (skippable with `--auto` — auto-selects all tasks)

**Skip if:** RESUME_MODE and user selected "All remaining tasks" at the Resume gate (tasks already marked SELECTED, `selection_scope = ALL`, proceed directly to Step 4a.1).

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
- **Select All**: Mark all tasks as `Status: SELECTED`. **Set `selection_scope = ALL`** (Step 4a.1 will auto-proceed for each wave).
- **Select by Wave**: **Set `selection_scope = BY_WAVE`**. For each wave, use `AskUserQuestion` with yes/no:
  - **header**: "Wave {N}"
  - **question**: "Wave {N} has {count} tasks ({effort}). Include this wave?"
  - **options**:
    - { label: "Include", description: "Select all tasks in Wave {N}" }
    - { label: "Skip", description: "Defer all tasks in Wave {N}" }
- **Custom Selection**: **Set `selection_scope = CUSTOM`**. User provides task IDs (e.g., "T-01, T-02, T-04") via "Other" text input

### 3. Update tasks.md

For each task, update the `**Status**:` field:
- Selected tasks → `Status: SELECTED`
- Non-selected tasks → `Status: DEFERRED`
- Previously completed tasks remain → `Status: COMPLETED`

### 4. Handle Edge Cases

- **All tasks already COMPLETED**: Skip to Step 4b (validation)
- **Resume with completed waves**: Show completed waves as read-only context, only allow selection on remaining (non-COMPLETED) waves. Selection options (Select All, Select by Wave, Custom) apply only to non-COMPLETED tasks.
- **Resume with no Status fields**: Auto-add `Status: SELECTED` to all tasks (backward compatibility)
- **`--auto` mode**: Auto-select all non-COMPLETED tasks, skip this step

---

## Step 4a: Wave Execution Loop

Execute selected tasks wave by wave. Each wave follows sub-steps 4a.1 → 4a.2 → 4a.3.

### Step 4a.1: Wave Confirmation

**Gate: Conditional**
- **Tier 3 ✅ (auto-proceed, log only)** if `selection_scope = ALL` — log "Wave {N}: auto-proceeded (Select All)" and continue to Step 4a.2
- **Tier 2 ⚠️ (skippable with `--auto`)** if `selection_scope = BY_WAVE` or `CUSTOM`

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
- **PROCEED**: Continue to Step 4a.2
- **SKIP TASKS**: User provides task IDs to defer, update `tasks.md`, re-present wave
- **SKIP WAVE**: Mark all wave tasks as DEFERRED in `tasks.md`, skip to Step 4a.3 (no checkpoint generated for empty waves), then proceed to next wave's Step 4a.1

### Step 4a.2: Implement Wave Tasks

Execute tasks within the current wave. This is the core implementation step.

#### Implementation Guidelines

- **One task at a time** - Complete and verify before moving to next
- **TDD when applicable** - Write tests before implementation
- **Commit frequently** - Small, atomic commits after each task
- **Preserve existing code** - Enhance, don't replace working logic

#### Task Tracking

Use Claude Code's native task tools for progress tracking:
- `TaskCreate` - Create tasks at start of implementation
- `TaskUpdate` - Mark tasks `in_progress` when starting, `completed` when done
- `TaskList` - Review remaining work

Update `tasks.md` as tasks complete: set `**Status**: COMPLETED` for each finished task.

**Note:** The `tasks.md` file captures task definitions, acceptance criteria, and Status. Progress tracking also happens via TaskCreate/TaskUpdate for real-time visibility.

#### For Each Task in the Wave

1. Read all relevant files identified in previous phases
2. Implement following chosen architecture
3. Follow codebase conventions strictly
4. Write clean, well-documented code
5. Use TaskUpdate to mark tasks complete as you progress
6. Commit after each task

#### UI Implementation with Stitch

**Skip this section if:** No `## Design Assets` section in plan.md or status is "Skipped".

When starting a UI-related task, check if Stitch exports are available:

1. **Read plan.md** and locate `## Design Assets` section
2. **If exports exist** (`stitch_exports_path` is set):

   **For each UI component task:**

   a. Identify corresponding Stitch export by matching:
      - Task title to export filename (e.g., "Record Button" → `02-record-button.png/html`)
      - Component name to export name

   b. Present to user:
   ```markdown
   **UI Task:** [task title]
   **Stitch Export:** [matched export path]

   Would you like to use stitch-to-react for this component?
   ```

   c. Use `AskUserQuestion`:
      - **header**: "Stitch Convert"
      - **question**: "Stitch export found for [component]. Use stitch-to-react skill?"
      - **options**:
        - { label: "Yes, convert with Stitch (Recommended)", description: "Generate React component from Stitch export" }
        - { label: "No, implement manually", description: "Use export as visual reference only" }

   d. **If convert selected:**
      1. Invoke `Skill` tool with `skill: "stitch-to-react"`
      2. Provide export path and target component location
      3. Review generated component, adjust as needed

3. **If exports don't exist but were expected** (status "Pending generation"):
   - Warn user: "Stitch exports were not generated. Implementing from design docs."
   - Continue with manual implementation using any available design documentation

### Step 4a.3: Wave Checkpoint

**Gate: Tier 2** ⚠️ (skippable with `--auto` — auto-continues to next wave)

**Skip if:** Wave was entirely skipped (no tasks executed, no checkpoint generated).

After completing all selected tasks in the current wave:

#### 1. Collect Wave Metrics

- Tasks completed in this wave (count and IDs)
- Files changed (`git diff --stat` since wave start)
- Test status (run test suite, count passing/failing)
- Commits made during this wave (`git log --oneline` since wave start)

#### 2. Generate Wave Context File

Use [wave-context.md.template](../templates/wave-context.md.template) to generate `{spec_path}/wave-{N}-context.md`:

- Fill in feature summary from `spec.md`
- Fill in architecture overview from `plan.md`
- Fill in completed wave data from collected metrics
- Fill in next wave details from `tasks.md` (SELECTED tasks in Wave {N+1})
- Fill in git state (branch, last commit, diff stat)
- Fill in resume instructions with `{spec_path}`

Write the file using the `Write` tool.

#### 3. Check for More Waves

- **If more waves with SELECTED tasks remain**: Present continue/stop choice
- **If all waves complete**: Log "All waves complete", proceed to Step 4b

#### 4. Continue or Stop

Use `AskUserQuestion`:
- **header**: "Wave Complete"
- **question**: "Wave {N} complete: {tasks_done} tasks, {files_changed} files changed, {tests_passing}/{tests_total} tests passing. {next_wave_summary}. How to proceed?"
- **options**:
  - { label: "CONTINUE (Recommended)", description: "Proceed to Wave {N+1} in current session" }
  - { label: "STOP", description: "Save context, copy resume command to clipboard, and exit" }

**Response Handling:**
- **CONTINUE**: Proceed to Step 4a.1 for Wave {N+1}
- **STOP**: Save wave context, copy resume command to clipboard, display resume instructions, and exit Phase 4 (skip Steps 4b-4e):
  1. Use `Bash` tool: `printf '/core:develop @{spec_path}/' | pbcopy` (macOS) or equivalent for the current platform
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

## Step 4b: Quick Validation (ALWAYS)

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

---

## Step 4c: Deep Validation (only with `--validate`)

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

---

## Step 4d: Code Review (agent launch)

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

---

## Step 4e: Quality & Completion Gate

### ⛔ TIER 1 CHECKPOINT - MANDATORY STOP

**This checkpoint CANNOT be skipped, even with `--auto`.**

Before presenting this gate:
1. Collect validation results (Step 4b output, Step 4c score if `--validate`)
2. Collect code review findings (from parallel reviewer agents in Step 4d)
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
- **question**: "[RULE ZERO: N/6 checks passed]. [Validation: PASS/score]. [Code review: N issues found]. Mark implementation complete?"
- **options**:
  - { label: "APPROVE — Mark Complete", description: "All checks pass, proceed to Phase 5 summary" }
  - { label: "REVIEW — Show diff & details", description: "Show git diff and full validation report" }
  - { label: "FIX — Return to implementation", description: "Address issues, then re-present this gate" }
  - { label: "VERIFY UI — Test in browser", description: "Run Playwright verification before approving" }

**CRITICAL: STOP HERE. DO NOT PROCEED TO PHASE 5 UNTIL USER SELECTS "APPROVE — Mark Complete".**

**Response Handling:**
- **APPROVE — Mark Complete**: Proceed to Phase 5 (PHASE-5-SUMMARY.md)
- **REVIEW — Show diff & details**: Execute `git diff`, display output and full code review findings, then re-present this gate
- **FIX — Return to implementation**: Return to implementation work. When user indicates work is done, re-run Steps 4b–4d agents, then re-present this gate
- **VERIFY UI — Test in browser**: Run UI verification workflow (see below), then re-present this gate with updated results

### UI Verification Workflow (when VERIFY UI selected)

Live UI verification using Playwright CLI. Refer to the `playwright:playwright-cli` skill for the full command reference.

1. **Ask for verification type:**
   - **SCREENSHOT** - Navigate to URL and capture screenshot for visual review
   - **INTERACTIVE** - Take accessibility snapshot, explore and interact with elements
   - **TEST SCENARIO** - Run specific test steps (navigate, click, fill, verify)

2. **Execute based on selection:**

   **SCREENSHOT:**
   - Ask for URL to verify
   - Open the page, capture a screenshot, present to user for visual confirmation

   **INTERACTIVE:**
   - Ask for URL to verify
   - Navigate to the URL, capture accessibility snapshot
   - Present snapshot and offer to interact with elements

   **TEST SCENARIO:**
   - Ask user to describe test steps (or reference from task acceptance criteria)
   - Execute each step using Playwright CLI (open, snapshot, click, type, fill, screenshot)
   - Report pass/fail for each step

3. **After verification:** Return to Quality & Completion gate with results included

---

## Output

Phase 4 produces:
- Implemented feature code
- Wave context files (`wave-{N}-context.md`) for each completed wave
- Updated `tasks.md` with Status fields (SELECTED/DEFERRED/COMPLETED)
- Quick validation results
- Deep validation score (if `--validate`)
- Code review findings
- UI verification status (if performed)
- List of addressed vs deferred issues

**Next:** Proceed to [PHASE-5-SUMMARY.md](PHASE-5-SUMMARY.md)
