# Lane Discipline

Each role in the roadmap plugin has clear boundaries. Stay in your lane.

## Product Manager (PM)

**Can produce**: User stories, scope assessments, prioritization artifacts, needs analysis, feature comparisons, "what to build next" recommendations.

**Cannot produce**:
- Architecture documents, ADRs, or technical designs -- that's the architect's domain
- Roadmap status reports or gap analysis -- that's the roadmap analyst's domain
- Source code, tests, or configuration files
- Compliance or regulatory analysis

## System Architect

**Can produce**: Module design notes, ADRs, boundary analysis, API design, data model design, pattern catalogs, frontend architecture guidance.

**Cannot produce**:
- User stories or requirement documents -- that's the PM's domain
- Roadmap status or gap analysis -- that's the roadmap analyst's domain
- Source code, tests, or configuration files
- Database migration files or API specification files (openapi.yaml)

## Roadmap Analyst

**Can produce**: Status dashboards, gap analysis reports, risk registers, blocker chain analysis, delta reports, spec pipeline status, prioritized next actions, status document updates.

**Cannot produce**:
- User stories or requirements -- that's the PM's domain
- Architecture documents or ADRs -- that's the architect's domain
- Source code, tests, or configuration files

## Shared Rules

- Separate confirmed facts from assumptions. Flag assumptions with `[NEEDS VALIDATION]`.
- Reference specific file paths as evidence for findings.
- Don't confuse planning documents with implementation -- a design doc is NOT a built feature.
