# HITL Gate System

Human-in-the-Loop gates ensure appropriate oversight at critical decision points.

## Three-Tier Framework

| Tier | Symbol | Behavior | Use Case |
|------|--------|----------|----------|
| **Tier 1** | ⛔ | MANDATORY approval via AskUserQuestion | Constitutional/security risk |
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

## AskUserQuestion Pattern

For Tier 1 and Tier 2 gates, use the `AskUserQuestion` tool:

```json
{
  "header": "{Short checkpoint name}",
  "question": "{Summary of what was done/proposed}. How would you like to proceed?",
  "options": [
    { "label": "APPROVE", "description": "Proceed to next phase" },
    { "label": "REVIEW", "description": "Show me more details" },
    { "label": "MODIFY", "description": "I want to change something" },
    { "label": "CANCEL", "description": "Stop here" }
  ]
}
```

**Tool Constraints:**
- 2-4 options per question (tool limit)
- "Other" option is automatically provided by the tool
- For dynamic options (architecture), generate at runtime

### Example: Architecture Decision (Tier 1)

Present the trade-offs summary, then use `AskUserQuestion`:

```json
{
  "header": "Architecture",
  "question": "JWT+Redis is scalable but adds Redis dependency. Session-based is simpler but stateful. OAuth2 is standards-based but external. Which approach?",
  "options": [
    { "label": "Option A: JWT + Redis (Recommended)", "description": "Scalable, stateless design" },
    { "label": "Option B: Session-based", "description": "Simple, proven pattern" },
    { "label": "Option C: OAuth2 only", "description": "Standards-based, external auth" },
    { "label": "REQUEST CHANGES", "description": "Modify requirements first" }
  ]
}
```

### Example: Completion Verification (Tier 1)

Present RULE ZERO status, then use `AskUserQuestion`:

```json
{
  "header": "Completion",
  "question": "5 files changed, 12/12 tests passing, no TODOs found. Mark implementation complete?",
  "options": [
    { "label": "APPROVE", "description": "Mark complete, proceed to Phase 5" },
    { "label": "REVIEW", "description": "Show me the git diff" },
    { "label": "FIX", "description": "I need to address something first" },
    { "label": "CANCEL", "description": "Keep working" }
  ]
}
```

### Example: Requirements (Tier 2)

```json
{
  "header": "Requirements",
  "question": "3 functional requirements defined with 8 acceptance criteria. How would you like to proceed?",
  "options": [
    { "label": "APPROVE", "description": "Proceed to architecture design" },
    { "label": "REVIEW", "description": "Show me full requirements" },
    { "label": "MODIFY", "description": "I want to change requirements" },
    { "label": "CANCEL", "description": "Stop here" }
  ]
}
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
