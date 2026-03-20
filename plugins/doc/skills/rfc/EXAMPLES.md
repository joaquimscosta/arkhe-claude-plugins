# RFC Examples

## Create

```bash
# Draft a new RFC from a topic
/rfc create event-driven architecture for notifications

# Multi-word topics work naturally
/rfc create migration from REST to gRPC for internal services

# If no topic given, you'll be asked
/rfc create
```

**What happens**: Gathers context from conversation history, research artifacts, ADRs, and codebase. Confirms scope with you. Writes a lightweight spec file (`NNNN-<slug>.spec.md`) for your approval. Then drafts a fully populated RFC with auto-numbering, including an Author's Notes section recording shortcuts, assumptions, and areas of uncertainty.

## Review

```bash
# Review a specific RFC
/rfc review docs/rfcs/0003-event-driven-notifications.md

# If no path given, suggests globbing to find candidates
/rfc review
```

**What happens**: Loads the RFC and its companion spec file (if present). Discovers architecture standards from the project. Spawns the `rfc-critic` agent for an adversarial review — the critic reads the Author's Notes as prioritized attack vectors, evaluates 7 dimensions with a red-team mindset, checks RFC-vs-spec alignment, and produces a verdict with confidence score: Approve, Approve with changes, or Needs redesign. Every concern must cite evidence.

## List

```bash
# List all RFCs with their status
/rfc list
```

**Example output**:

```markdown
# Architecture RFCs

| # | Title | Status | Author | Date |
|---|-------|--------|--------|------|
| 0003 | Event-Driven Notifications | Draft | Jane Doe | 2026-03-15 |
| 0002 | API Gateway Migration | Approved | John Smith | 2026-02-20 |
| 0001 | Database Consolidation | Approved | Jane Doe | 2026-01-10 |

**Summary**: 3 total — 1 Draft, 0 Review, 2 Approved
```

## Update

```bash
# Update specific sections after a review
/rfc update docs/rfcs/0003-event-driven-notifications.md

# Works best when:
# 1. You just ran /rfc review and want to address findings
# 2. You specify which sections to update in conversation
```

**What happens**: Reads the existing RFC, identifies which sections to update (from your instructions, review findings, or asks you), re-drafts those sections with fresh context while preserving everything else. Handles Author's Notes lifecycle — strips them on Approved status, refreshes after major re-drafts. Checks spec alignment if scope-related sections were changed. Shows a diff summary.

## Status

```bash
# Transition RFC status with validation
/rfc status 3 review
/rfc status 3 approved
/rfc status 3 rejected
```

**What happens**: Finds the RFC by number, reads current status, validates the transition. Warns on unusual paths (e.g., Draft → Approved skips Review). If transitioning to Approved, strips the Author's Notes section entirely. Shows confirmation with old → new status and side effects applied.

**Example: Normal transition**:
```
RFC-0003: Draft → Review
```

**Example: Warned transition (skipping Review)**:
```
⚠️ Warning: Skipping Review phase — consider getting review feedback first.

Proceed anyway?
  1. Yes, approve directly
  2. No, move to Review first
```

**Example: Approval with side effects**:
```
RFC-0003: Review → Approved
✓ Author's Notes stripped
```

## Typical Workflow

```bash
# 1. Research and discuss a topic in conversation
"Let's discuss how to handle notifications in the system..."

# 2. Capture the discussion as an RFC (writes spec first, then full RFC)
/rfc create event-driven notifications

# 3. Adversarial review (uses rfc-critic agent)
/rfc review docs/rfcs/0003-event-driven-notifications.md

# 4. Address review findings
/rfc update docs/rfcs/0003-event-driven-notifications.md

# 5. Re-review after updates
/rfc review docs/rfcs/0003-event-driven-notifications.md

# 6. Approve the RFC (validates, strips Author's Notes)
/rfc status 3 approved

# 7. Check the pipeline
/rfc list
```
