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
2. If any tasks remain `in_progress` or `pending` (should not occur after Step 4.2 gate):
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
- Quality gates: [PASS/issues per wave]
- Wave critic: [verdicts and notes]
- RULE ZERO: [N/6 checks passed]

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

### 4. Save Project Learnings (Persistent Memory Pattern)

Evaluate whether discoveries from this feature should persist as project memory.

**Auto-evaluate candidates from:**
- Architecture trade-offs from Phase 2 (why option A over B)
- Gotchas discovered during implementation (framework limitations, API quirks)
- Domain knowledge from research phase (if Step 2a-res was conducted)
- Integration patterns established between existing and new code

**Filter criteria (only save if):**
- Not derivable from reading the code or git history
- Would be useful for future features in this project
- Represents a decision with non-obvious reasoning

**If candidates found**, use `AskUserQuestion`:
- **header**: "Project Learnings"
- **question**: "{N} learnings identified from this feature. Save to project memory?"
- **options**:
  - { label: "Save all", description: "Write each as a project-type memory file" }
  - { label: "Review first", description: "Show candidates, select which to save" }
  - { label: "Skip", description: "Don't save any memories" }

**Gate: Tier 3** (auto-skip with `--auto`; no memories saved in autonomous mode)

**Response handling:**
- **Save all**: For each learning, write a memory file:
  ```markdown
  ---
  name: {feature-slug}-{learning-topic}
  description: {one-line description}
  type: project
  ---

  {Learning content}

  **Why:** {motivation or constraint}
  **How to apply:** {when this should shape future decisions}
  ```
  Then add a pointer to `MEMORY.md`.
- **Review first**: Present each candidate, let user approve/reject individually, save approved ones
- **Skip**: No memories saved

**If no candidates found**: Skip silently, no user interaction.

---

## Verification Record (RULE ZERO)

RULE ZERO was verified and approved at the Quality & Completion Gate (Step 4.2) before entering Phase 5. This section records the confirmed state for audit purposes.

**Verified at gate approval:**
- [x] All tasks marked `completed` in TaskList
- [x] All FR-XXX requirements have corresponding implementation
- [x] Acceptance criteria are testable
- [x] Files actually modified (git diff check)
- [x] Tests pass (if applicable)
- [x] No placeholder code (`TODO`, `UnsupportedOperationException`)
- [x] Subagent recommendations were implemented (not just analyzed)

**Evidence recorded:**
- `git diff` output reviewed at Quality & Completion gate
- Test results confirmed
- File read-back confirmed modifications persisted

_If any items were noted as exceptions during gate approval, they are documented in the gate log._

---

## Output

Phase 5 produces:
- Completion summary
- Updated spec status
- Verification steps
- Next steps recommendations
- Project learnings saved to memory (if applicable)

**End of SDLC Pipeline**
