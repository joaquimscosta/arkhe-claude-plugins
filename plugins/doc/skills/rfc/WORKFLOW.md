# RFC Workflows

Detailed per-operation workflows for the RFC skill.

## Common: RFC Directory Discovery

### Search Algorithm

Check all paths and merge results (deduplicate by filename):

1. `docs/rfcs/*.md`
2. `docs/20-architecture/rfcs/*.md` — jd-docs convention
3. `.arkhe/rfcs/*.md` — arkhe convention
4. `arkhe/rfcs/*.md`

### jd-docs Detection

Check for jd-docs structure:
- `.jd-config.json` exists in project root, OR
- `docs/20-architecture/` directory exists

### Write Directory Resolution (for create/update)

Use the first match:
1. If jd-docs detected → `docs/20-architecture/rfcs/`
2. Else if `docs/rfcs/` exists → `docs/rfcs/`
3. Else → create `docs/rfcs/` as default

---

## Create Workflow

### Step 1: Determine Topic
- Extract topic from arguments after `create`
- If empty, ask the user what the RFC should be about

### Step 2: Gather Context

Search for existing information before writing:

1. **Conversation context** — review the current conversation for discussion, decisions, and research already conducted
2. **Research artifacts** — search for related research documents:
   - `docs/30-research/`
   - `docs/50-research/`
   - `docs/research/`
3. **Memory files** — grep the memory directory for cached research on the topic
4. **Codebase** — scan relevant source files to understand the current state (the "before" picture)
5. **ADRs** — check for related architecture decisions:
   - `docs/20-architecture/22-adr/`
   - `docs/20-architecture/adr/`
   - `docs/adr/`

### Step 3: Confirm Scope

Present a brief summary of findings and proposed RFC scope. Ask the user to confirm or adjust. Use `AskUserQuestion` with key scoping choices if there are meaningful alternatives.

### Step 4: Read Template

Read `${CLAUDE_SKILL_DIR}/templates/rfc-template.md` for section structure.

### Step 5: Draft RFC

Fill every section with substantive content:

- **Summary**: 1-2 paragraph overview of the proposal
- **Motivation**: Real problems from the codebase/discussion, not placeholder text
- **Goals / Non-Goals**: Specific, actionable items
- **Architecture Overview**: Concrete technical approach with package names, file paths, patterns
- **Diagram**: Mermaid diagram showing the proposed architecture or data flow
- **Data Model**: Actual schema changes or "no changes required" with rationale
- **APIs**: Real endpoints or "no API changes" with rationale
- **Infrastructure**: Deployment impact assessment
- **Security Considerations**: Specific to this proposal
- **Scalability**: Realistic load assessment
- **Observability**: What to monitor
- **Risks and Mitigations**: Real risks with likelihood/impact assessment
- **Alternatives Considered**: At least 2 alternatives with clear rejection rationale
- **Migration Plan**: Step-by-step with rollback strategy
- **Open Questions**: Genuine unresolved decisions (not filler)

Set **Author** to the git user name, **Status** to `Draft`, **Date** to today.

### Step 6: Discover Directory

Use the Write Directory Resolution algorithm above.

### Step 7: Auto-Number and Write

1. Glob all convention paths to find the highest existing RFC number
2. Assign the next sequential number (zero-padded to 4 digits)
3. Ask user to confirm the title — generate a kebab-case filename slug
4. Write to `<resolved-dir>/NNNN-<slug>.md`

### Step 8: Suggest Next Steps

- `/rfc review <path-to-new-rfc>` — to get a design review
- Manual review by team members

---

## Review Workflow

### Context Loading

1. Read the RFC document at the given path
2. Discover architecture standards (check in order, use first found):
   - `.arkhe/roadmap/architecture.md` (arkhe convention)
   - `docs/20-architecture/` directory (jd-docs convention)
   - `docs/architecture.md` or `docs/architecture/` (generic)
   - If none found, review against general architecture best practices
3. Scan referenced modules/packages in the RFC to verify feasibility

### Review Dimensions

Evaluate each dimension, noting concerns with severity (Critical/Major/Minor):

#### 1. Problem Definition
Is the problem clearly stated? Are goals and non-goals explicit? Is the motivation compelling?

#### 2. Architecture Quality
Does the design respect module boundaries? Is dependency direction correct? Does it follow established patterns from `architecture.md`?

#### 3. Scalability
Will this scale with user growth? Are there bottlenecks? Does it handle multi-tenant scenarios?

#### 4. Data Architecture
Is the data model sound? Are migrations safe? Are queries efficient? Does it maintain data integrity?

#### 5. Infrastructure
Is the deployment strategy clear? Are there new infrastructure requirements? Is rollback possible?

#### 6. Security
Are auth flows correct? Is input validated? Are there data privacy implications? Does it follow OWASP guidelines?

#### 7. Project Fit
Does it align with the project's domain and existing patterns? Does it integrate well with the current architecture?

### Output Format

```markdown
# RFC Review: [RFC Title]
**Reviewer**: Claude | **Date**: [date] | **RFC**: [path]

## Verdict: [Approve | Approve with changes | Needs redesign]

## Summary
[2-3 sentence assessment]

## Strengths
- [strength with reference to RFC section]

## Concerns

### Critical
- [concern] — Section: [ref] | Impact: [description]

### Major
- [concern] — Section: [ref] | Impact: [description]

### Minor
- [concern] — Section: [ref] | Suggestion: [fix]

## Suggested Improvements
1. [improvement with rationale]

## Verdict Rationale
[Why this verdict was chosen. What must change before approval (if applicable).]
```

### Verdict Criteria

- **Approve**: No critical concerns, minor issues only
- **Approve with changes**: No critical concerns, has major concerns with clear fixes
- **Needs redesign**: Has critical concerns or fundamental architecture issues

### Notes

- Flag missing sections from the standard RFC template as Minor concerns
- After review, suggest `/rfc update <path>` to address findings

---

## List Workflow

### Header Extraction

For each RFC file found, extract from the file header:

- **Number/Filename**: from the file path (e.g., `0003` from `0003-event-driven.md`)
- **Title**: from the `# RFC: [Title]` heading. If non-standard, use the first `#` heading.
- **Status**: from the `**Status**:` field. Valid values: Draft, Review, Approved, Rejected, Superseded. If missing, show "Unknown".
- **Author**: from the `**Author**:` field. If missing, show "—".
- **Date**: from the `**Date**:` field. If missing, show "—".

### Output Format

```markdown
# Architecture RFCs

| # | Title | Status | Author | Date |
|---|-------|--------|--------|------|
| 0003 | Event-Driven Notifications | Draft | Jane Doe | 2026-03-15 |
| 0002 | API Gateway Migration | Approved | John Smith | 2026-02-20 |
| 0001 | Database Consolidation | Approved | Jane Doe | 2026-01-10 |

**Summary**: 3 total — 1 Draft, 0 Review, 2 Approved
```

Sort by number descending (newest first).

---

## Update Workflow

### Section Identification

Determine which sections need updating:

1. **Explicit user request**: User specified sections in the conversation (e.g., "update the security section")
2. **Post-review context**: If invoked after `/rfc review`, parse review findings — update sections flagged with Critical or Major concerns
3. **Interactive**: If neither above applies, present the RFC's section list and ask the user which to revise

### Preservation Rules

- Read the entire RFC before making changes
- Only modify the identified sections — preserve all other sections byte-for-byte
- Maintain the same heading structure and nesting
- Do not reorder sections
- Do not add or remove sections unless the user explicitly requests it

### Context Gathering for Updates

For each section being updated:
1. Read the current section content
2. Search the conversation for relevant new information
3. Check for new research artifacts or codebase changes since the RFC was written
4. If the update was prompted by a review, reference the specific concern and suggested improvement

### Diff Summary

After updating, output a summary:

```markdown
## Update Summary

**RFC**: [path]
**Date**: [today]
**Sections updated**:
- **Security Considerations**: Added JWT token rotation strategy and OWASP references
- **Data Model**: Updated migration plan to handle backward compatibility
- **Open Questions**: Resolved 2 of 4 open questions based on team discussion
```

### Status Transitions

- Keep Status unchanged by default
- If user explicitly requests a status change (e.g., "move to Review"), update the `**Status**:` field
- Valid transitions: Draft → Review → Approved/Rejected, any → Superseded
