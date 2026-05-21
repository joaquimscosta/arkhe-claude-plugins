# Output Templates

Canonical output templates shared by roadmap plugin skills and agents. Use these formats for consistent, structured output.

---

## Product Manager Templates

### User Story

```markdown
## US-{NNN}: {Title}

**As a** {persona}
**I want to** {action}
**So that** {business value}

### Acceptance Criteria

- **Given** {precondition}
  **When** {action}
  **Then** {expected result}

### Constraints
- **Dependencies:** {what must exist first}
- **Phase:** {which roadmap phase, if applicable}

### Notes
{Additional context, edge cases, validation needed}
```

### Scope Assessment

```markdown
# Scope Assessment: {Feature}
_Author: product-manager agent | Date: {date}_

## User Value
{Why does this matter to users?}

## Project Fit
{Does this align with current goals? Which phase?}

## User Stories
{3-5 user stories for this feature}

## Dependencies
{What must exist before this can be built?}

## Effort Estimate
{S / M / L with justification}

## Risks
{Product risks}

## Open Questions
{Questions needing answers}

## Recommendation
{Build now / Defer / Needs research}
```

### Prioritization

```markdown
# Feature Prioritization
_Author: product-manager agent | Date: {date}_

## Prioritization Matrix

| Rank | Feature | MoSCoW | User Value | Effort | Dependencies | Status |
|------|---------|--------|-----------|--------|--------------|--------|

## Criteria
{How features were scored}

## Recommendations
{Top 3-5 actions with rationale}
```

---

## System Architect Templates

### Module Design

```markdown
# Module Design: {Module Name}
_Author: system-architect agent | Date: {date}_

## Context
{Why this module exists, what business problem it solves}

## Domain Model

### Entities / Models
| Name | Fields | Relationships | Notes |
|------|--------|---------------|-------|

### Value Objects
| Name | Fields | Used By | Notes |
|------|--------|---------|-------|

### Events
| Event | Published By | Consumed By | Payload |
|-------|-------------|-------------|---------|

## API Surface
| Method | Path | Request | Response | Auth | Notes |
|--------|------|---------|----------|------|-------|

## Data Model
| Table/Collection | Columns/Fields | Indexes | Constraints |
|-----------------|----------------|---------|-------------|

## Module Dependencies
{What this module depends on and what depends on it}

## Risks & Trade-offs
| Risk | Impact | Mitigation |
|------|--------|------------|

## Open Questions
{Questions that need answers before implementation}
```

### ADR (Architecture Decision Record)

```markdown
# ADR-{NNN}: {Title}
_Status: Proposed | Date: {date}_

## Context
{What is the issue that we're seeing that is motivating this decision?}

## Decision
{What is the change that we're proposing?}

## Consequences

### Positive
- ...

### Negative
- ...

### Neutral
- ...

## Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|------------|------|------|-------------|
```

### Boundary Analysis

```markdown
# Module Boundary Analysis
_Author: system-architect agent | Date: {date}_

## Dependency Graph
{Mermaid diagram showing module relationships}

## Module Inventory
| Module | Responsibility | Public API | Events |
|--------|---------------|-----------|--------|

## Boundary Violations
| Source | Target | Type | File | Recommendation |
|--------|--------|------|------|----------------|

## Coupling Assessment
| Module Pair | Coupling Type | Strength | Risk |
|-------------|---------------|----------|------|

## Recommendations
{Prioritized list of improvements}
```

---

## Roadmap Analyst Templates

### Project Health Report

```markdown
# Project Health Report
_Deep analysis generated: {date}_

## 1. Executive Summary
{3-5 sentences on overall project health, trajectory, and key concerns}

## 2. Phase/Milestone Status

| Phase | Description | Status | Completion | Blocker | Next Milestone |
|-------|-------------|--------|------------|---------|----------------|

## 3. Module Implementation Matrix

| Module | Source Files | Test Files | Maturity | Key Gaps |
|--------|------------|-----------|----------|----------|

## 4. Decision Traceability

| Decision | Description | Code Evidence | Status | Notes |
|----------|------------|---------------|--------|-------|

## 5. Documentation Health

| Document | Purpose | Current? | Actionable? | Notes |
|----------|---------|----------|-------------|-------|

## 6. Gap Analysis Risk Map

| Gap Source | Gap | Current Status | Risk | Likelihood | Impact | Mitigation |
|-----------|-----|---------------|------|-----------|--------|------------|

## 7. Dependency Graph
{What blocks what -- trace the critical path}

## 8. Blocking Chain
{Ordered list of blockers with downstream impact}

## 9. Risk Register

| # | Risk | Likelihood | Impact | Score | Mitigation | Owner |
|---|------|-----------|--------|-------|------------|-------|

## 10. Prioritized Action Plan
{Numbered list of next actions, ordered by impact and urgency}

## 11. Recommendations
{Strategic recommendations for the project}
```

### Status Dashboard

```markdown
## Project Status Dashboard
_Generated: {date}_

### Module Overview

| Module | Backend | Frontend | Maturity | Notes |
|--------|---------|----------|----------|-------|

### Working Features
- {feature}: {evidence}

### Planned Features
- {feature}: {document reference}

### Missing / Not Started
- {feature}: {gap reference or "not yet considered"}

### Recommended Next Actions
1. {action with rationale}
```

### Risk Register

```markdown
## Risk Register
_Generated: {date}_

| # | Risk | Likelihood | Impact | Score | Mitigation | Owner |
|---|------|-----------|--------|-------|------------|-------|
| 1 | {risk} | H/M/L | H/M/L | {LxI} | {action} | {team/person} |
```

### Project Roadmap

```markdown
# {Project Name} — Project Roadmap
_Generated by /roadmap plan scaffold on {date}. Maintained by /roadmap plan sync._
_Last synced: {date} | Branch: `{branch}` (`{short_hash}`)_

---

## Timeline

| Phase | Scope | Status | Specs | ADRs | Evidence |
|-------|-------|--------|-------|------|----------|
| {id} | {one-line scope} | Done / In Progress / Not Started / Deferred | {count or list} | {count or list} | {PRs, commits} |

---

## Phase Details

### Phase {id}: {Title}
- **Status:** {Done / In Progress / Not Started / Deferred}
- **Scope:** {2-3 sentence description}
- **Specs:** {comma-separated spec IDs with titles, or "none"}
- **ADRs:** {comma-separated ADR numbers with titles, or "none"}
- **Evidence:** {PR numbers, commit hashes, deployed URLs}
- **Delivered:** {date or date range}

{Repeat for each phase}

---

## Backlog

Unsequenced themes with priority and dependencies. Source: product roadmaps and backlog documents.

| # | Theme | Priority | Dependencies | Status |
|---|-------|----------|--------------|--------|
| {n} | {theme name} | High / Medium / Low | {theme IDs or "none"} | Not Started / In Progress / Done |

---

## Spec Traceability

| Spec | Title | Phase | Impl Status | Evidence |
|------|-------|-------|-------------|----------|
| {id} | {title} | {phase id or "—"} | Proposed / Ready / In Progress / Complete | {file paths, PRs} |

**Summary:** {complete}/{total} complete, {linked}/{total} linked to phases

---

## ADR Traceability

| ADR | Title | Phase | Status | Impact |
|-----|-------|-------|--------|--------|
| {number} | {title} | {phase id or "—"} | Active / Superseded / Proposed | {one-line impact summary} |

**Summary:** {linked}/{total} linked to phases

---

## Sprint / Iteration Log

_Optional: include if the project uses time-boxed iterations._

| Sprint | Dates | Delivered | Notes |
|--------|-------|-----------|-------|
| {id} | {start} – {end} | {phase/spec IDs completed} | {retrospective notes} |

---

## References

| Document | Role |
|----------|------|
| `{status_file}` | Module maturity, risk register, test coverage |
| `{path}` | {one-line description of what this doc provides} |
```

---

## File Naming Conventions

### Product Manager Artifacts

| Artifact Type | Path |
|---------------|------|
| User stories | `{output_dir}/requirements/{feature-slug}-stories.md` |
| Scope assessment | `{output_dir}/requirements/scope-{feature-slug}.md` |
| Prioritization | `{output_dir}/requirements/{YYYY-MM-DD}-priorities.md` |
| Feature analysis | `{output_dir}/requirements/feature-{name-slug}.md` |
| Needs analysis | `{output_dir}/requirements/{YYYY-MM-DD}-needs.md` |
| Comparison | `{output_dir}/requirements/{a-slug}-vs-{b-slug}.md` |

### System Architect Artifacts

| Artifact Type | Path |
|---------------|------|
| Module design | `{output_dir}/architecture/module-{name}.md` |
| ADR | `{output_dir}/architecture/adr-{NNN}-{title-slug}.md` |
| Boundary analysis | `{output_dir}/architecture/boundary-analysis.md` |
| API design | `{output_dir}/architecture/api-{feature-slug}.md` |
| Data model | `{output_dir}/architecture/data-model-{feature-slug}.md` |
| Pattern catalog | `{output_dir}/architecture/pattern-catalog.md` |

### Roadmap Analyst Artifacts

| Artifact Type | Path |
|---------------|------|
| Health report | `{output_dir}/reports/{YYYY-MM-DD}-health-report.md` |
| Status update | `{status_file}` (from config) |
| Project roadmap | `{plan_file}` (from config, default: `docs/PROJECT-ROADMAP.md`) |
