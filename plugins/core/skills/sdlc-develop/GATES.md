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
| Phase 0 (RESUME) | Wave Resume + Task Selection | ⚠️ Tier 2 | Continue next wave; "All remaining tasks" skips Step 4.0 |
| Phase 1 → 2 | Requirements Summary | ⚠️ Tier 2 | Approval before architecture |
| Phase 2c | Architecture Decision | ⛔ Tier 1 | Cannot skip, even with `--auto` |
| Phase 2 → 3 | Plan Saved | ✅ Tier 3 | Auto-proceed, log only |
| Phase 3 → 4 | Task Breakdown | ⚠️ Tier 2 | Validate before implementation |
| Phase 4.0 | Ticket Selection | ⚠️ Tier 2 | Select tasks for session (skipped in RESUME + "All remaining tasks") |
| Phase 4a.1 | Wave Confirmation | Conditional | Tier 3 auto-proceed when `selection_scope=ALL`; Tier 2 otherwise |
| Phase 4a.3 | Wave Checkpoint | ⚠️ Tier 2 | Wave complete, continue or stop |
| Phase 4e | Quality & Completion | ⛔ Tier 1 | Combined RULE ZERO + code review; VERIFY UI option available |

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

**Note:** The Quality & Completion Gate (Phase 4e) is always Tier 1 regardless of triggers. The presence of conditional triggers is recorded in the gate log for audit purposes but does not change gate behavior.

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

### Example: Quality & Completion (Tier 1)

Present combined quality review + RULE ZERO status, then use `AskUserQuestion`:

```json
{
  "header": "Quality & Completion",
  "question": "RULE ZERO: 6/6 checks passed. Validation: PASS. Code review: 0 issues. Mark implementation complete?",
  "options": [
    { "label": "APPROVE — Mark Complete", "description": "All checks pass, proceed to Phase 5 summary" },
    { "label": "REVIEW — Show diff & details", "description": "Show git diff and full validation report" },
    { "label": "FIX — Return to implementation", "description": "Address issues, then re-present this gate" },
    { "label": "VERIFY UI — Test in browser", "description": "Run Playwright verification before approving" }
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

### Example: Wave Checkpoint (Tier 2)

Present wave completion metrics, then use `AskUserQuestion`:

```json
{
  "header": "Wave Complete",
  "question": "Wave 2 complete: 4 tasks done, 8 files changed, 15/15 tests passing. Wave 3 has 3 remaining tasks (T-05, T-06, T-07). How to proceed?",
  "options": [
    { "label": "CONTINUE", "description": "Proceed to Wave 3 in current session" },
    { "label": "STOP", "description": "Save context, copy resume command to clipboard, and exit" }
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
