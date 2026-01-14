# HITL Gate System

Human-in-the-Loop gates ensure appropriate oversight at critical decision points.

## Three-Tier Framework

| Tier | Symbol | Behavior | Use Case |
|------|--------|----------|----------|
| **Tier 1** | ⛔ | MANDATORY approval via numbered prompt | Constitutional/security risk |
| **Tier 2** | ⚠️ | RECOMMENDED review, skippable with `--auto` | High risk but recoverable |
| **Tier 3** | ✅ | AUTOMATED, logs for post-review | Low risk, reversible |

---

## Gate Mapping by Phase

| Transition | Gate | Tier | Notes |
|------------|------|------|-------|
| Phase 0 → 1 | Existing System Findings | ⚠️ Tier 2 | REUSE/ENHANCE/CREATE decisions |
| Phase 1 → 2 | Requirements Summary | ⚠️ Tier 2 | Approval before architecture |
| Phase 2c | Architecture Decision | ⛔ Tier 1 | Cannot skip, even with `--auto` |
| Phase 2 → 3 | Plan Saved | ✅ Tier 3 | Auto-proceed, log only |
| Phase 3 → 4 | Task Breakdown | ⚠️ Tier 2 | Validate before implementation |
| Phase 4d | Quality Review | Conditional | Tier 1 if security/DB, else Tier 2 |
| Phase 4 → 5 | Completion | ⛔ Tier 1 | RULE ZERO verification |

---

## Conditional Tier 1 Triggers

These auto-elevate ANY checkpoint to Tier 1:

- [ ] Database schema changes (CREATE TABLE, ALTER TABLE, migrations)
- [ ] Security implementation (JWT, OAuth2, encryption, permissions)
- [ ] Breaking API changes (removed endpoints, changed contracts)
- [ ] New service/module creation
- [ ] Architecture decisions affecting multiple services
- [ ] Performance-critical algorithm changes

**Detection**: Check plan.md, spec.md, and implementation for keywords.

---

## Gate Decision Criteria

### Tier 1: Always Block ⛔

Must have explicit human approval before proceeding:

- Architecture decisions (approach selection)
- Implementation completion (RULE ZERO)
- Any conditional trigger detected
- Constitutional compliance concerns

### Tier 2: Recommend Review ⚠️

Review recommended but can skip with `--auto`:

- Requirements gathering complete
- Existing system analysis complete
- Task breakdown complete
- Refactoring >100 LOC
- New third-party dependencies
- Test coverage changes

### Tier 3: Auto-Proceed ✅

Proceed automatically, log for post-review:

- Plan file saved
- Documentation updates
- Code formatting
- Template generation

---

## Numbered Prompt Pattern

For Tier 1 and Tier 2 gates, use this format:

```
## Tier {N} Checkpoint: {Gate Name}

{Summary of what was done/proposed}

**Options:**
1. **APPROVE** - Proceed to next phase
2. **REVIEW** - Show me more details
3. **MODIFY** - I want to change something
4. **CANCEL** - Stop here

Enter your choice (1-4):
```

### Example: Architecture Decision (Tier 1)

```
## Tier 1 Checkpoint: Architecture Decision ⛔

I've analyzed three approaches for implementing user authentication:

| Approach | Pros | Cons |
|----------|------|------|
| A. JWT + Redis | Scalable, stateless | Redis dependency |
| B. Session-based | Simple, proven | Server state |
| C. OAuth2 only | Standards-based | External dependency |

**Recommendation:** Option A (JWT + Redis)

**Options:**
1. **Option A** - JWT + Redis (RECOMMENDED)
2. **Option B** - Session-based
3. **Option C** - OAuth2 only
4. **REQUEST CHANGES** - Modify requirements first

Enter your choice (1-4):
```

### Example: Completion Verification (Tier 1)

```
## Tier 1 Checkpoint: Implementation Complete ⛔

**RULE ZERO Verification:**
- [x] Files modified: 5 files changed
- [x] Tests passing: 12/12 tests green
- [x] No stubs/TODOs in changed files
- [x] git diff confirms changes persisted

**Summary:**
- Added UserAuthService with JWT handling
- Created 3 API endpoints
- Added integration tests

**Options:**
1. **APPROVE** - Mark implementation complete
2. **REVIEW** - Show me the git diff
3. **MODIFY** - I want to make changes
4. **CANCEL** - Keep working

Enter your choice (1-4):
```

---

## `--auto` Mode Behavior

| Tier | With `--auto` | Without `--auto` |
|------|---------------|------------------|
| Tier 1 ⛔ | Still blocks (cannot skip) | Blocks |
| Tier 2 ⚠️ | Auto-approves, logs decision | Prompts user |
| Tier 3 ✅ | Auto-proceeds | Auto-proceeds |

**Key**: Tier 1 gates ALWAYS require human approval, regardless of flags.

---

## Logging Gate Decisions

All gate decisions should be logged:

```markdown
## Gate Log

| Time | Gate | Tier | Decision | Mode |
|------|------|------|----------|------|
| 10:15 | Existing System | Tier 2 | APPROVED | interactive |
| 10:22 | Requirements | Tier 2 | APPROVED | interactive |
| 10:45 | Architecture | Tier 1 | Option A | interactive |
| 10:46 | Plan Saved | Tier 3 | AUTO | auto |
```

This log can be included in the spec directory for audit purposes.
