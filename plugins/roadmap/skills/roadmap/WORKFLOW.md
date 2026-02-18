# Roadmap Skill — Workflow

Detailed codebase scanning protocol and mode workflows for the Roadmap Analyst skill.

## Context Discovery Protocol

Same protocol as the PM skill. Execute before any analysis.

### Phase 1: Configuration

Read `.arkhe.yaml` → extract `roadmap:` section (output_dir, context_dir, status_file).

### Phase 2: Rich Context

Read `{context_dir}/*.md` if the directory exists. Key files:
- `documents.md` — Document map with roles
- `architecture.md` — Module structure and tech stack
- `project.md` — Project overview and phases

### Phase 3: Project Identity

Read `CLAUDE.md` + `README.md` for scope, conventions, and constraints.

### Phase 4: Documentation Inventory

Glob for all documentation and planning files:

```
docs/**/*.md
plan/**/*.md
specs/**/*.md
arkhe/specs/*/spec.md
```

Categorize each file:
- **Status documents**: PROJECT-STATUS.md, roadmap.md, CHANGELOG.md
- **Gap analyses**: Documents identifying missing features or capabilities
- **Specs**: Feature specifications with requirements
- **ADRs**: Architecture Decision Records
- **Research**: Technical research and investigation documents
- **Reports**: Generated analysis reports

### Phase 5: Build File Detection

Same as PM skill — detect tech stack from build files.

### Phase 6: Codebase Scanning

This phase is more thorough for the roadmap skill than for PM.

#### Tech-Stack-Aware Module Scan

**Java/Kotlin (Gradle/Maven):**
```
apps/*/src/main/kotlin/**/*.kt OR apps/*/src/main/java/**/*.java
apps/*/src/test/**/*.kt OR apps/*/src/test/**/*.java
apps/*/src/main/resources/db/migration/*.sql
```
Count: entities, services, controllers, repositories, tests, migrations.

**JavaScript/TypeScript (Node):**
```
src/components/**/*.tsx OR src/components/**/*.vue
src/pages/**/*.tsx OR src/app/**/page.tsx
src/hooks/**/*.ts
src/api/**/*.ts OR src/routes/**/*.ts
```
Count: components, pages, hooks, API routes.

**Python:**
```
src/**/*.py OR app/**/*.py
tests/**/*.py
migrations/**/*.py OR alembic/versions/*.py
```
Count: models, views/routes, services, tests, migrations.

**Go:**
```
cmd/**/*.go
internal/**/*.go OR pkg/**/*.go
*_test.go
```
Count: handlers, services, models, tests.

**Rust:**
```
src/**/*.rs
tests/**/*.rs
```
Count: modules, structs, traits, tests.

#### Module Maturity Assessment

For each discovered module, assess maturity:

1. **Stub**: Directory exists, placeholder files only
2. **Domain Started**: Models/entities/types defined
3. **Service Layer**: Business logic present
4. **API Ready**: Routes/endpoints exposed
5. **Tested**: Test files exist and cover key paths
6. **Production Ready**: Comprehensive tests, docs, monitoring

Evidence checklist:
- Count source files vs test files
- Check for TODOs, FIXMEs, stubs
- Verify tests actually run (not just exist)
- Check for documentation

## Mode Workflows

### `status`

1. Run full context discovery
2. Build module inventory with maturity ratings
3. Cross-reference docs against codebase:
   - Features described in docs → find implementation evidence
   - Implementation found → verify it matches documentation
4. Produce dashboard:
   - Module maturity table
   - What's working (evidence-backed)
   - What's planned (doc-backed)
   - What's missing (no docs, no code)

### `gaps`

1. Run context discovery
2. Find all gap analysis documents
3. For each gap:
   - Extract the original finding
   - Search codebase for closure evidence
   - Classify: Open / In Progress / Closed
4. Produce gap tracking table with evidence

### `next`

1. Run full context discovery (thorough)
2. Collect all open items:
   - Unclosed gaps
   - Unstarted specs
   - Module maturity imbalances
   - Frontend-backend parity issues
3. Rank by: impact, effort, dependencies, urgency
4. Recommend 3-5 prioritized next actions

### `delta`

1. Read the status document (from config or default path)
2. Run codebase scan
3. Compare current state vs documented state:
   - New files, modules, migrations since last update
   - Gaps that have been addressed
   - New issues or regressions
   - Metric changes (file counts, test counts)
4. Produce delta report

### `blockers`

1. Run context discovery
2. Identify blocking items from:
   - Gap analyses (dependencies marked as blocking)
   - Specs (prerequisites not met)
   - Research (unanswered questions blocking decisions)
   - External dependencies (APIs, services, approvals)
3. Trace blocking chains:
   - A blocks B blocks C
   - External X blocks internal Y
4. Identify critical path (longest blocking chain)

### `risks`

1. Run context discovery
2. Extract risks from:
   - Gap analyses
   - Research documents
   - Module maturity assessment (immature critical modules = risk)
   - Missing tests (untested code = risk)
   - External dependencies
3. Score each: Likelihood (H/M/L) x Impact (H/M/L)
4. Suggest mitigations
5. Produce risk register

### `update`

1. Run full context discovery + full codebase scan
2. Read existing status document
3. Preserve format and structure
4. Update all data points:
   - Module maturity ratings
   - Completion percentages
   - Gap closure status
   - New developments
5. Show diff preview to user and ask for confirmation
6. Write updated file to `{status_file}`
7. Report changes made

### `specs`

1. Run context discovery
2. Find all spec files:
   - `arkhe/specs/*/spec.md`
   - `specs/**/*.md`
   - Any path configured in context
3. For each spec:
   - Extract title and requirements
   - Search codebase for implementation evidence
   - Classify: Proposed / Ready / In Progress / Complete
4. Produce pipeline table with evidence

## Output Templates

### Status Dashboard

```
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

```
## Risk Register
_Generated: {date}_

| # | Risk | Likelihood | Impact | Score | Mitigation | Owner |
|---|------|-----------|--------|-------|------------|-------|
| 1 | {risk} | H/M/L | H/M/L | {LxI} | {action} | {team/person} |
```
