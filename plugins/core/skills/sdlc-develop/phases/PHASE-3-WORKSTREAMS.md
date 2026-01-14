# Phase 3: Workstreams

**Goal**: Break implementation into parallel work streams with full ticket tracking

**Model tier**: haiku

---

## Actions

### 1. Parse Implementation Phases

Read the saved plan.md for implementation phases from Phase 2.

### 2. Break into Discrete Tasks

Convert each phase into discrete tasks with full ticket metadata.

### 3. Organize into Parallel Waves

Group tasks based on dependencies:
- **Wave 1**: Tasks with no dependencies (can run in parallel)
- **Wave 2**: Tasks depending on Wave 1
- **Wave 3**: Tasks depending on Wave 2
- etc.

### 4. Generate tasks.md

Save to `arkhe/specs/{NN}-{feature_slug}/tasks.md`

Use template: [tasks.md.template](../templates/tasks.md.template)

---

## Full Ticket Format

Each task uses structured ticket format:

```markdown
## T-01: {Task Title}

**Type**: feature | bug | task | refactor | test
**Priority**: P0 (critical) | P1 (high) | P2 (medium) | P3 (low)
**Effort**: S (1-2h) | M (2-4h) | L (4-8h) | XL (8h+)
**Dependencies**: [T-02, T-03] or none
**Wave**: 1 | 2 | 3
**Files**: `path/to/file.ts`, `path/to/other.ts`

### Description
What needs to be done - clear, actionable description.

### Acceptance Criteria
- [ ] Criterion 1 - specific, testable
- [ ] Criterion 2 - specific, testable
- [ ] Criterion 3 - specific, testable

### Technical Notes
Implementation hints, patterns to follow, gotchas.
```

---

## Effort Estimation

| Size | Hours | Typical Scope |
|------|-------|---------------|
| S | 1-2h | Single function, simple change |
| M | 2-4h | Single component, moderate complexity |
| L | 4-8h | Multiple files, integration work |
| XL | 8h+ | Major feature, cross-cutting concerns |

---

## User Checkpoint

**Unless `--auto` mode:**

Present task breakdown:
1. Total task count by wave
2. Estimated total effort
3. Dependency graph visualization
4. Any questions about scope

Ask: "Does this task breakdown look right? Ready to start implementation?"

---

## Output

Phase 3 produces:
- tasks.md with full ticket breakdown
- Wave-organized implementation plan
- Effort estimates
- Dependency mapping

**Next:** Proceed to [PHASE-4-IMPLEMENTATION.md](PHASE-4-IMPLEMENTATION.md)
