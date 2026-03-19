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

**What happens**: Gathers context from conversation history, research artifacts, ADRs, and codebase. Confirms scope with you, then writes a fully populated RFC with auto-numbering.

## Review

```bash
# Review a specific RFC
/rfc review docs/rfcs/0003-event-driven-notifications.md

# If no path given, suggests globbing to find candidates
/rfc review
```

**What happens**: Loads the RFC and discovers architecture standards from the project. Evaluates across 7 dimensions (Problem Definition, Architecture Quality, Scalability, Data Architecture, Infrastructure, Security, Project Fit) and produces a verdict: Approve, Approve with changes, or Needs redesign.

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

**What happens**: Reads the existing RFC, identifies which sections to update (from your instructions, review findings, or asks you), re-drafts those sections with fresh context while preserving everything else, and shows a diff summary.

## Typical Workflow

```bash
# 1. Research and discuss a topic in conversation
"Let's discuss how to handle notifications in the system..."

# 2. Capture the discussion as an RFC
/rfc create event-driven notifications

# 3. Review the draft
/rfc review docs/rfcs/0003-event-driven-notifications.md

# 4. Address review findings
/rfc update docs/rfcs/0003-event-driven-notifications.md

# 5. Check the pipeline
/rfc list
```
