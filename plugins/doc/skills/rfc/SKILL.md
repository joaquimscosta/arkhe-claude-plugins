---
name: rfc
description: >-
  Manage architecture RFCs: create, review, list, and update.
  Use when user mentions "RFC", "technical proposal", "architecture proposal",
  or wants to draft, review, list, or update RFCs.
argument-hint: "<action> [args]  (create <topic> | review <path> | list | update <path>)"
disable-model-invocation: true
---

# RFC Manager

Manage architecture RFCs with 4 operations: create, review, list, update.

## Argument Parsing

Parse `$ARGUMENTS` to determine the action:

| First word | Remaining args | Operation |
|------------|---------------|-----------|
| `create` | `<topic>` | Draft a new RFC |
| `review` | `<path-to-rfc>` | Review an existing RFC |
| `list` | (none) | List all RFCs |
| `update` | `<path-to-rfc>` | Update specific RFC sections |
| (empty) | | Ask the user which action to perform |

If the first word does not match any action, treat the entire `$ARGUMENTS` as a topic and default to `create`.

## RFC Directory Discovery

Used by all operations. Search for RFC files across all convention paths:

1. `docs/rfcs/*.md`
2. `docs/20-architecture/rfcs/*.md` (jd-docs — detected via `.jd-config.json` or `docs/20-architecture/` directory)
3. `.arkhe/rfcs/*.md` (arkhe convention)
4. `arkhe/rfcs/*.md`

For **create** and **update**, resolve a write directory:
- If jd-docs detected → `docs/20-architecture/rfcs/`
- Else if `docs/rfcs/` exists → `docs/rfcs/`
- Else → create `docs/rfcs/` as default

## Operation: create

Draft a populated RFC — NOT a blank template. Gather context and write a real first draft.

1. **Determine topic** from args after `create` (or ask if empty)
2. **Gather context** — search conversation, research artifacts (`docs/30-research/`, `docs/50-research/`, `docs/research/`), memory files, relevant source code, and ADRs (`docs/20-architecture/22-adr/`, `docs/20-architecture/adr/`, `docs/adr/`). See [WORKFLOW.md](WORKFLOW.md) for detail.
3. **Confirm scope** with user before drafting — present what you found and proposed scope. Use `AskUserQuestion` for meaningful alternatives.
4. **Read template** at `${CLAUDE_SKILL_DIR}/templates/rfc-template.md` for section structure
5. **Draft populated RFC** filling every section with substantive content. See [WORKFLOW.md](WORKFLOW.md) for per-section guidance. Set Author to git user name, Status to `Draft`, Date to today.
6. **Discover directory** using RFC Directory Discovery above
7. **Auto-number** — glob all convention paths for highest existing number, assign next (zero-padded 4 digits). Confirm title with user, generate kebab-case slug. Write to `<dir>/NNNN-<slug>.md`
8. **Suggest next steps**: `/rfc review <path>` for design review

## Operation: review

Review the RFC against architecture standards and best practices.

1. **Read RFC** at the given path (if empty, ask — suggest globbing `docs/rfcs/*.md` and `docs/20-architecture/rfcs/*.md`)
2. **Discover architecture standards** (check in order, use first found):
   - `.arkhe/roadmap/architecture.md` (arkhe convention)
   - `docs/20-architecture/` directory (jd-docs convention)
   - `docs/architecture.md` or `docs/architecture/` (generic)
   - Fall back to general best practices
3. **Scan referenced modules** in the RFC to verify feasibility
4. **Evaluate 7 dimensions** (Critical/Major/Minor severity): Problem Definition, Architecture Quality, Scalability, Data Architecture, Infrastructure, Security, Project Fit. See [WORKFLOW.md](WORKFLOW.md) for dimension details.
5. **Output** using the review format in [WORKFLOW.md](WORKFLOW.md): verdict, summary, strengths, concerns by severity, improvements, rationale
6. **Verdict criteria**:
   - **Approve**: No critical concerns, minor issues only
   - **Approve with changes**: No critical concerns, has major concerns with clear fixes
   - **Needs redesign**: Has critical concerns or fundamental architecture issues
7. Flag missing RFC template sections as Minor concerns
8. **Suggest next steps**: `/rfc update <path>` to address findings

## Operation: list

List all architecture RFCs with their current status.

1. Search all convention paths (see RFC Directory Discovery)
2. For each RFC, extract from headers: Number/Filename, Title (from `# RFC: [Title]` or first `#` heading), Status (`Draft`/`Review`/`Approved`/`Rejected`/`Superseded` — default "Unknown"), Author (default "—"), Date (default "—")
3. Output markdown table sorted by number descending (newest first):

```markdown
# Architecture RFCs

| # | Title | Status | Author | Date |
|---|-------|--------|--------|------|

**Summary**: X total — Y Draft, Z Review, W Approved
```

4. If no RFCs found, suggest `/rfc create <topic>`

## Operation: update

Re-draft specific sections of an existing RFC based on new context or feedback.

1. **Read RFC** at the given path (if empty, ask for path)
2. **Identify sections to update**:
   - If user specified sections in conversation, update those
   - If invoked after a `/rfc review`, use review findings to identify sections needing changes
   - Otherwise, ask the user which sections to revise
3. **Gather fresh context** from conversation, research, and codebase for the sections being updated
4. **Re-draft sections** — rewrite identified sections with improved content. Preserve all unchanged sections exactly as-is.
5. **Update Date** to today. Keep Status unchanged unless user requests a transition.
6. **Show diff summary** — list which sections were changed and a brief description of each change
7. **Suggest next steps**: `/rfc review <path>` to verify the updates

## Quality Standards

- Every section must contain real content, not placeholder text like `[describe here]`
- Reference specific files, packages, and patterns from the codebase
- If a section doesn't apply, state that explicitly with a one-line rationale
- Drafts should be good enough to review immediately, not skeletons to fill in later

## Progressive Disclosure

- [WORKFLOW.md](WORKFLOW.md) — detailed per-operation workflows
- [EXAMPLES.md](EXAMPLES.md) — usage examples for all operations
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — common issues and solutions
