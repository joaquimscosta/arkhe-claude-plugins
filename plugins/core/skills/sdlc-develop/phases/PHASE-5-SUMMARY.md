# Phase 5: Summary

**Goal**: Document what was accomplished

**Model tier**: None (direct output)

---

## Actions

### 0. Sync tasks.md Acceptance Criteria

Before verifying completion, synchronize task status to tasks.md:

1. Read `{spec_path}/tasks.md`
2. Use `TaskList` to get all tasks and their status
3. For each task with status `completed`:
   - Find the corresponding `### T-XX:` section in tasks.md
   - Locate the "#### Acceptance Criteria" subsection
   - Replace all `- [ ]` with `- [x]` within that section
4. Use `Edit` tool to update tasks.md with the changes
5. Log: "Synced acceptance criteria: X checkboxes marked complete across Y tasks"

**Note:** This ensures tasks.md serves as a complete record of completed work, useful for handoffs and documentation.

### 1. Final Tasks Verification

**Task tracking confirmation:**
1. Use `TaskList` to verify all tasks are marked `completed`
2. If any tasks remain `in_progress` or `pending` (should not occur after Phase 4e gate):
   - Use `TaskUpdate` to mark them completed if the work was verified during Phase 4
   - Log a warning if tasks were completed but not updated during implementation

**spec.md confirmation:**
1. Read `{spec_path}/spec.md`
2. Confirm all acceptance criteria are marked complete

### 2. Provide Completion Summary

Generate summary in this format:

```markdown
## Development Complete

**Feature:** [what was requested]
**Plan:** [path to saved plan]
**Status:** Complete | Partial | Blocked

### What Was Built
- [Key deliverable 1]
- [Key deliverable 2]
- [Key deliverable 3]

### Files Modified
- `path/to/file1.ts` - [what changed]
- `path/to/file2.ts` - [what changed]
- `path/to/file3.ts` - [what changed]

### Validation Results
- Quick check: [PASS/issues]
- Deep validation: [score] (if --validate)
- Code review: [findings addressed]

### Verification Steps
1. [How to test the feature]
2. [Commands to run]
3. [Expected behavior]

### Next Steps

**Always include testing recommendations** (pull from `testing_recommendations` if set in Phase 3, otherwise generate based on implemented files):

- [ ] **Unit tests** for:
  - [hook/utility name] (`path/to/file`)
  - [hook/utility name] (`path/to/file`)
- [ ] **Integration tests** for:
  - [API endpoint/data flow] (`path/to/file`)
- [ ] **E2E tests** for:
  - [user flow description] (if UI work was done)

**Other follow-up items:**
- [Recommended follow-up actions]
- [Related features to consider]
- [Technical debt to address]
```

### 3. Update Spec Status

Update `{spec_path}/spec.md` status to "Complete".

---

## Verification Checklist (RULE ZERO)

Before marking complete, verify ALL items:

**Required Checks:**
- [ ] All tasks marked `completed` in TaskList
- [ ] All FR-XXX requirements have corresponding implementation
- [ ] Acceptance criteria are testable
- [ ] Files actually modified (git diff check)
- [ ] Tests pass (if applicable)
- [ ] No placeholder code (`TODO`, `UnsupportedOperationException`)
- [ ] Subagent recommendations were implemented (not just analyzed)

**Evidence Required:**
- `git diff` output showing actual changes
- Test results (if tests were written)
- File read-back confirming modifications persisted

**If ANY check fails:** Do NOT mark as complete. Return to Phase 4.

---

## Output

Phase 5 produces:
- Completion summary
- Updated spec status
- Verification steps
- Next steps recommendations

**End of SDLC Pipeline**
