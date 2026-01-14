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

**Numbered Prompt:**
```
## Tier {1|2} Checkpoint: Quality Review

{Validation results summary}

1. **APPROVE** - Proceed to completion
2. **REVIEW** - Show me the code diff
3. **FIX ISSUES** - Address the findings first
4. **CANCEL** - Stop here

Enter choice (1-4):
```

---

## Completion Gate

**Gate: Tier 1** ⛔ (MANDATORY - RULE ZERO enforcement)

Before proceeding to Phase 5, verify:

```
## Tier 1 Checkpoint: Implementation Complete ⛔

**RULE ZERO Verification:**
- [ ] Files modified (git diff confirms changes)
- [ ] Tests passing (if applicable)
- [ ] No stubs/TODOs in changed files
- [ ] Subagent recommendations implemented

1. **APPROVE** - Mark implementation complete
2. **REVIEW** - Show me the git diff
3. **FIX** - I need to address something
4. **CANCEL** - Keep working

Enter choice (1-4):
```

---

## Output

Phase 4 produces:
- Implemented feature code
- Quick validation results
- Deep validation score (if `--validate`)
- Code review findings
- List of addressed vs deferred issues

**Next:** Proceed to [PHASE-5-SUMMARY.md](PHASE-5-SUMMARY.md)
