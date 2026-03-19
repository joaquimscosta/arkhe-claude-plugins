# RFC Workflows

Detailed per-operation workflows for the RFC skill.

## Common: RFC Directory Discovery

### Search Algorithm

Check all paths and merge results (deduplicate by filename). Exclude `*.spec.md` companion files from results:

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

### Step 4: Resolve Number and Slug

Compute the auto-number and slug early — both the spec and RFC files share the same `NNNN-<slug>`:

1. Discover the write directory (see Write Directory Resolution above)
2. Glob all convention paths for the highest existing RFC number
3. Assign the next sequential number (zero-padded to 4 digits)
4. Ask user to confirm the title, then generate a kebab-case filename slug
5. Both files will use this: `<dir>/NNNN-<slug>.spec.md` and `<dir>/NNNN-<slug>.md`

### Step 5: Write Spec File

Draft a lightweight spec to anchor the full RFC:

1. Read the spec template at `${CLAUDE_SKILL_DIR}/templates/rfc-spec-template.md`
2. Fill in all four sections with concrete content:
   - **Problem Statement**: 2-3 sentences describing the problem in terms of user/business impact. Include the cost of inaction.
   - **Key Constraints**: Technical, organizational, or timeline constraints that bound the solution space. Be specific — "must support Postgres" not "database compatibility".
   - **Success Criteria**: Measurable outcomes that indicate the RFC succeeded. Each criterion must be testable (e.g., "latency under 200ms at p99", "zero downtime migration").
   - **Scope Boundaries**: What is explicitly in scope and out of scope. Out-of-scope items must include a reason.
3. Write to `<dir>/NNNN-<slug>.spec.md` using the resolved number and slug
4. Present the spec to the user. Use `AskUserQuestion` to confirm or adjust.
5. Only proceed to the full RFC draft after user confirms the spec.

**Completeness test**: Could someone who hasn't seen the original conversation draft a correct RFC from this spec alone? If not, add more detail.

### Step 6: Read Template

Read `${CLAUDE_SKILL_DIR}/templates/rfc-template.md` for section structure.

### Step 7: Draft RFC

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

### Step 8: Append Author's Notes (Confession)

After completing all standard RFC sections, append `## Author's Notes` below Open Questions:

- **Shortcuts**: What was simplified or hand-waved? (e.g., "Assumed Redis cluster mode works with our VPC setup without testing")
- **Assumptions**: What did the author believe but not confirm from the codebase or documentation? (e.g., "Assuming the payment API returns sorted results")
- **Uncertainties**: Which sections had the least information available?
- **Low-confidence sections**: Which sections does the author consider weakest?

**Guidelines**:
- Be specific and honest. Vague confessions like "some parts may need more thought" are useless.
- Reference specific RFC sections (e.g., "The Scalability section assumes linear scaling — not verified").
- Aim for 3-8 confession items. Fewer suggests overconfidence; more suggests the RFC is not ready.
- These notes feed the adversarial review — they are features, not bugs.

### Step 9: Write RFC

Use the resolved number and slug from Step 4. Write to `<dir>/NNNN-<slug>.md`.

### Step 10: Suggest Next Steps

- `/rfc review <path-to-new-rfc>` — for adversarial design review (uses rfc-critic agent)
- Manual review by team members

---

## Review Workflow

### Context Loading

1. Read the RFC document at the given path
2. Check for a companion spec file: replace `.md` with `.spec.md` in the filename (e.g., `0003-event-driven.md` → `0003-event-driven.spec.md`). If found, read it.
3. Discover architecture standards (check in order, use first found):
   - `.arkhe/roadmap/architecture.md` (arkhe convention)
   - `docs/20-architecture/` directory (jd-docs convention)
   - `docs/architecture.md` or `docs/architecture/` (generic)
   - If none found, the agent reviews against general architecture best practices
4. Scan referenced modules/packages in the RFC to verify feasibility

### Agent Delegation

Spawn the `rfc-critic` agent (subagent_type: `doc:rfc-critic`) via the Agent tool. Provide in the prompt:

1. The full RFC content
2. The spec file content (if found), with instruction: "Check RFC-vs-spec alignment for each success criterion and scope boundary"
3. Architecture standards content (if found)
4. Instruction: "Read the Author's Notes section first and use confessions as prioritized attack vectors"

The agent independently evaluates all 7 dimensions with adversarial framing and returns a structured review. It has read-only codebase access (Read, Grep, Glob, Bash) to verify claims made in the RFC.

### Output Format

The agent produces output in this format:

```markdown
# RFC Review: [RFC Title]
**Reviewer**: rfc-critic | **Date**: [date] | **RFC**: [path] | **Confidence**: [0-100]

## Verdict: [Approve | Approve with changes | Needs redesign]

## Summary
[2-3 sentence assessment]

## Strengths
- [strength with reference to RFC section]

## Concerns

### Critical
- [concern] — Section: [ref] | Evidence: [citation] | Impact: [description]

### Major
- [concern] — Section: [ref] | Evidence: [citation] | Impact: [description]

### Minor
- [concern] — Section: [ref] | Evidence: [citation] | Suggestion: [fix]

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

### Status Transitions (within update)

- Keep Status unchanged by default
- If user explicitly requests a status change (e.g., "move to Review"), update the `**Status**:` field
- Valid transitions: Draft → Review → Approved/Rejected, any → Superseded
- For dedicated status changes with validation, prefer `/rfc status` which validates transitions and handles side effects automatically

### Author's Notes Handling

- **Status transition to Approved**: Remove the `## Author's Notes` section and all its content entirely.
- **User requests "refresh confessions"**: Regenerate the Author's Notes based on the current RFC state, replacing the old section.
- **Major sections re-drafted**: After re-drafting, review the existing Author's Notes. If confessions reference sections that were substantially changed, update or remove those specific confession items.
- **Otherwise**: Preserve Author's Notes as-is, like any other section.

### Spec Alignment on Update

If a companion `.spec.md` file exists and the update touches Goals, Non-Goals, Architecture Overview, or Scope-related content:

1. Re-read the spec file
2. Verify the updated RFC still aligns with the spec's Problem Statement, Key Constraints, Success Criteria, and Scope Boundaries
3. If drift is detected, flag it to the user and suggest updating either the spec or the RFC to restore alignment

---

## Status Transition Workflow

Dedicated workflow for changing RFC status with validation and side effects. Invoked by `/rfc status <number> <status>`.

### Find RFC

1. Resolve RFC number to file path by globbing all convention paths for `NNNN-*.md` (exclude `*.spec.md`)
2. Read the file and extract current status from `**Status**:` field
3. If RFC not found, report error with the number and searched paths

### Validate Transition

Check current → target transition and warn on unusual paths:

| Current | Target | Behavior |
|---------|--------|----------|
| Draft | Review | Normal |
| Review | Approved | Normal |
| Review | Rejected | Normal |
| Draft | Approved | Warn: "Skipping Review phase — consider getting review feedback first" |
| Approved | Draft | Warn: "Going backwards — this will re-open an approved proposal" |
| Approved | Review | Warn: "Going backwards — this will re-open an approved proposal" |
| Rejected | Draft | Warn: "Reviving a rejected proposal — ensure concerns are addressed" |
| any | Superseded | Normal |

On warning: use `AskUserQuestion` to ask user to confirm. If user declines, abort.

### Apply Status Change

1. **Update `**Status**:` field** in the RFC file
2. **Side effects by target status**:
   - **→ Approved**: Strip the entire `## Author's Notes` section and all its content. This is the primary enforcement mechanism for the confession lifecycle.
3. **Preserve everything else** — only modify the Status field and (if applicable) remove Author's Notes

### Post-Transition

Show confirmation:
```
RFC-0003: Review → Approved
✓ Author's Notes stripped
```
