# Phase 5: Summary

**Goal**: Document what was accomplished

**Model tier**: None (direct output)

---

## Actions

### 1. Mark All Tasks Complete

**tasks.md verification:**
1. Read `{specs_dir}/{NN}-{slug}/tasks.md`
2. Verify ALL acceptance criteria checkboxes are `[x]` (not `[ ]`)
3. If any remain unchecked, either:
   - Mark them complete if the work was done
   - Return to Phase 4 to complete the work

**spec.md verification:**
1. Read `{specs_dir}/{NN}-{slug}/spec.md`
2. Verify all acceptance criteria are marked complete

If using TodoWrite/TaskUpdate tools, ensure those are also marked complete.

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
- [Recommended follow-up actions]
- [Related features to consider]
- [Technical debt to address]
```

### 3. Update Spec Status

Update `{specs_dir}/{NN}-{slug}/spec.md` status to "Complete".

---

## Verification Checklist (RULE ZERO)

Before marking complete, verify ALL items:

**Required Checks:**
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
