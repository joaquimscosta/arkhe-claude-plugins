# Phase 4: Implementation

**Goal**: Build the feature

**Model tier**: sonnet for implementation, opus for deep validation

---

## Step 4a: Execute Tasks

For each wave:

1. Read all relevant files identified in previous phases
2. Implement following chosen architecture
3. Follow codebase conventions strictly
4. Write clean, well-documented code
5. Use TaskUpdate to mark tasks complete as you progress

### Implementation Guidelines

- **One task at a time** - Complete and verify before moving to next
- **TDD when applicable** - Write tests before implementation
- **Commit frequently** - Small, atomic commits after each task
- **Preserve existing code** - Enhance, don't replace working logic

### Task Tracking

Use Claude Code's native task tools for progress tracking:
- `TaskCreate` - Create tasks at start of implementation
- `TaskUpdate` - Mark tasks `in_progress` when starting, `completed` when done
- `TaskList` - Review remaining work

**Note:** The `tasks.md` file in spec directories captures the INITIAL task definitions and acceptance criteria. Progress tracking happens via TaskCreate/TaskUpdate, not by editing checkboxes in tasks.md.

### UI Implementation with Stitch

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

## Step 4d: Quality Review

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

## User Checkpoint (Quality Review)

**Gate: Conditional** - Tier 1 ⛔ if security/DB changes detected, otherwise Tier 2 ⚠️

Check for Tier 1 triggers:
- [ ] Database schema changes in implementation
- [ ] Security-related code (auth, encryption, permissions)
- [ ] Breaking API changes
- [ ] New service/module creation

**If Tier 1 triggers detected:** Cannot skip, even with `--auto`

Present validation results:
1. Quick validation status (PASS/ISSUES)
2. Deep validation score (if `--validate`)
3. Code review findings

**Ask using AskUserQuestion:**

Present validation results, then use `AskUserQuestion` tool:
- **header**: "Quality Review"
- **question**: "[Validation results summary]. How would you like to proceed?"
- **options**:
  - { label: "APPROVE", description: "Proceed to completion" }
  - { label: "REVIEW", description: "Show me the code diff" }
  - { label: "FIX ISSUES", description: "Address the findings first" }
  - { label: "VERIFY UI", description: "Test UI changes with Playwright" }
  - { label: "CANCEL", description: "Stop here" }

**STOP: Unless `--auto` is set AND no Tier 1 triggers, WAIT for user response.**

**Response Handling:**
- **APPROVE**: Proceed to Step 4e (Completion Gate)
- **REVIEW**: Show `git diff` output, then re-present this checkpoint
- **FIX ISSUES**: Address issues, re-run validation, then re-present this checkpoint
- **VERIFY UI**: Run UI verification workflow (see below), then re-present this checkpoint
- **CANCEL**: Stop pipeline, remain in Phase 4

### UI Verification Workflow (when VERIFY UI selected)

Live UI verification using Playwright MCP tools:

1. **Ask for verification type:**
   - **SCREENSHOT** - Navigate to URL and capture screenshot for visual review
   - **INTERACTIVE** - Take accessibility snapshot, explore and interact with elements
   - **TEST SCENARIO** - Run specific test steps (navigate, click, fill, verify)

2. **Execute based on selection:**

   **SCREENSHOT:**
   - Ask for URL to verify
   - Use `mcp__playwright__browser_navigate` to open the page
   - Use `mcp__playwright__browser_take_screenshot` to capture
   - Present screenshot to user for visual confirmation

   **INTERACTIVE:**
   - Ask for URL to verify
   - Navigate to the URL
   - Use `mcp__playwright__browser_snapshot` to capture accessibility tree
   - Present snapshot and offer to interact with elements
   - User can request clicks, fills, or navigation

   **TEST SCENARIO:**
   - Ask user to describe test steps (or reference from task acceptance criteria)
   - Execute each step using Playwright tools (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_fill_form`, `browser_take_screenshot`)
   - Report pass/fail for each step

3. **After verification:** Return to Quality Review checkpoint with results included

---

## Step 4e: Completion Gate

### ⛔ TIER 1 CHECKPOINT - MANDATORY STOP

**This checkpoint CANNOT be skipped, even with `--auto`.**

Before proceeding to Phase 5:
1. Verify all RULE ZERO items
2. Present the checkpoint prompt below
3. **STOP AND WAIT** for user response
4. Do NOT proceed until user selects APPROVE

**Ask using AskUserQuestion:**

Present RULE ZERO verification status, then use `AskUserQuestion` tool:
- **header**: "Completion"
- **question**: "[RULE ZERO checklist status summary]. Mark implementation complete?"
- **options**:
  - { label: "APPROVE", description: "Mark complete, proceed to Phase 5" }
  - { label: "REVIEW", description: "Show me the git diff" }
  - { label: "FIX", description: "I need to address something first" }
  - { label: "CANCEL", description: "Keep working, do not mark complete" }

**CRITICAL: STOP HERE. DO NOT PROCEED TO PHASE 5 UNTIL USER RESPONDS.**

**Response Handling:**
- **APPROVE**: Proceed to Phase 5 (PHASE-5-SUMMARY.md)
- **REVIEW**: Execute `git diff` and display output, then re-present this checkpoint
- **FIX**: Return to implementation work, then re-present this checkpoint when ready
- **CANCEL**: Remain in Phase 4 implementation mode, await instructions

---

## Output

Phase 4 produces:
- Implemented feature code
- Quick validation results
- Deep validation score (if `--validate`)
- Code review findings
- UI verification status (if performed)
- List of addressed vs deferred issues

**Next:** Proceed to [PHASE-5-SUMMARY.md](PHASE-5-SUMMARY.md)
