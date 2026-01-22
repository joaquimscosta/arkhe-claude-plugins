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
5. Update todos as you progress

### Implementation Guidelines

- **One task at a time** - Complete and verify before moving to next
- **TDD when applicable** - Write tests before implementation
- **Commit frequently** - Small, atomic commits after each task
- **Preserve existing code** - Enhance, don't replace working logic

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

## Step 4d-ui: UI Verification (Optional)

After code review, offer live UI verification using Playwright MCP.

**Always ask using AskUserQuestion:**
```
Would you like to verify the UI changes with Playwright?

1. **SKIP** - No UI verification needed
2. **SCREENSHOT** - Navigate to URL and capture screenshot for visual review
3. **INTERACTIVE** - Take accessibility snapshot, explore and interact with elements
4. **TEST SCENARIO** - Run specific test steps (navigate, click, fill, verify)
```

**Response Handling:**

- **1 (SKIP)**: Proceed to Quality Review checkpoint with `UI Verification: SKIPPED`

- **2 (SCREENSHOT)**:
  1. Ask for URL to verify
  2. Use `mcp__playwright__browser_navigate` to open the page
  3. Use `mcp__playwright__browser_take_screenshot` to capture
  4. Present screenshot to user for visual confirmation
  5. Ask: "Does this look correct? (y/n)"
  6. Set status: `UI Verification: PASSED` or `UI Verification: ISSUES:[user feedback]`

- **3 (INTERACTIVE)**:
  1. Ask for URL to verify
  2. Navigate to the URL
  3. Use `mcp__playwright__browser_snapshot` to capture accessibility tree
  4. Present snapshot and offer to interact with elements
  5. User can request clicks, fills, or navigation
  6. Continue until user says "done"
  7. Set status based on user's final assessment

- **4 (TEST SCENARIO)**:
  1. Ask user to describe test steps (or reference from task acceptance criteria)
  2. Execute each step using Playwright tools:
     - `browser_navigate` - Go to URL
     - `browser_snapshot` - Capture current state
     - `browser_click` - Click elements
     - `browser_type` - Enter text
     - `browser_fill_form` - Fill form fields
     - `browser_take_screenshot` - Capture result
  3. Report pass/fail for each step
  4. Present final screenshot
  5. Set status: `UI Verification: PASSED` or `UI Verification: FAILED:[step details]`

**After UI verification:** Proceed to Quality Review checkpoint with UI verification status included.

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
4. UI verification status (from Step 4d-ui)

**Numbered Prompt:**
```
## Tier {1|2} Checkpoint: Quality Review

{Validation results summary}
{UI Verification: PASSED | SKIPPED | ISSUES:[list] | FAILED:[details]}

1. **APPROVE** - Proceed to completion
2. **REVIEW** - Show me the code diff
3. **FIX ISSUES** - Address the findings first
4. **UI VERIFY** - Run UI verification (again)
5. **CANCEL** - Stop here

Enter choice (1-5):
```

**STOP: Unless `--auto` is set AND no Tier 1 triggers, WAIT for user response.**

**Response Handling:**
- **1**: Proceed to Step 4e (Completion Gate)
- **2**: Show `git diff` output, then re-present this prompt
- **3**: Address issues, re-run validation, then re-present this prompt
- **4**: Return to Step 4d-ui for UI verification, then re-present this prompt
- **5**: Stop pipeline, remain in Phase 4

---

## Step 4e: Completion Gate

### ⛔ TIER 1 CHECKPOINT - MANDATORY STOP

**This checkpoint CANNOT be skipped, even with `--auto`.**

Before proceeding to Phase 5:
1. Verify all RULE ZERO items
2. Present the checkpoint prompt below
3. **STOP AND WAIT** for user response
4. Do NOT proceed until user responds with "1"

**Numbered Prompt:**

```
## Tier 1 Checkpoint: Implementation Complete ⛔

**RULE ZERO Verification:**
- [ ] Files modified (git diff confirms changes)
- [ ] Tests passing (if applicable)
- [ ] No stubs/TODOs in changed files
- [ ] Subagent recommendations implemented

1. **APPROVE** - Mark implementation complete, proceed to Phase 5
2. **REVIEW** - Show me the git diff
3. **FIX** - I need to address something first
4. **CANCEL** - Keep working, do not mark complete

Enter choice (1-4):
```

**CRITICAL: STOP HERE. DO NOT PROCEED TO PHASE 5 UNTIL USER RESPONDS.**

**Response Handling:**
- **1**: Proceed to Phase 5 (PHASE-5-SUMMARY.md)
- **2**: Execute `git diff` and display output, then re-present this prompt
- **3**: Return to implementation work, then re-present this prompt when ready
- **4**: Remain in Phase 4 implementation mode, await instructions

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
