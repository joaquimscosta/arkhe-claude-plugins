# Roadmap Skill — Workflow

Detailed codebase scanning protocol and mode workflows for the Roadmap Analyst skill.

## Context Discovery Protocol

Run the shared context discovery protocol in [CONTEXT_DISCOVERY.md](../../references/CONTEXT_DISCOVERY.md). Execute all phases in order (use thorough scan mode for Phase 7). For tech-stack-aware module scanning, see [TECH_STACK_DETECTION.md](../../references/TECH_STACK_DETECTION.md). For module maturity assessment, see [MATURITY_SCALE.md](../../references/MATURITY_SCALE.md).

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
5. **Drift detection** — after producing the dashboard:
   - Get last `{status_file}` commit: `git log -1 --format="%H %ai" -- {status_file}`
   - Count `feat:`/`fix:` commits since that hash: `git log {hash}..HEAD --oneline --no-merges | grep -cE "^[a-f0-9]+ (feat|fix):"`
   - If >= 3, append a notice at the end of the output:
     ```
     ⚠️  Documentation may be stale: {N} feature/fix commits since last status update ({date}).
     Run `/roadmap update` to sync.
     ```

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

#### Phase A: Git History Scan

1. Read `.arkhe.yaml` for `status_file` path (default: `docs/PROJECT-STATUS.md`)
2. Get last status doc commit:
   ```
   git log -1 --format="%H %ai" -- {status_file}
   ```
3. If no previous commit found, skip Phase A (first-time setup — Phase B handles it)
4. List commits since last doc update:
   ```
   git log {last_hash}..HEAD --oneline --no-merges
   ```
5. Categorize commits:
   - `feat:` → new features (group by PR number if `(#NN)` present in message)
   - `fix:` → bug fixes
   - `docs(adr):` or new files in `docs/adr/` → ADR additions
   - Changes to `arkhe/specs/*/spec.md` → spec completions
   - New `*.test.*` or `*.spec.*` files → test count changes
6. For each feature group, check the diff for scope:
   ```
   git diff --stat {last_hash}..{feature_commit} -- packages/ src/
   ```
7. Present **"What Shipped"** summary to the user before proceeding
8. Also check CHANGELOG.md — flag if `[Unreleased]` is missing entries for any feature groups

#### Phase B: Full Codebase Scan + Write

1. Run full context discovery + full codebase scan (existing behavior)
2. Read existing status document
3. Preserve format and structure
4. Update all data points — now informed by Phase A findings:
   - Module maturity ratings
   - Phase completion entries (add rows for shipped phases identified in Phase A)
   - Spec pipeline entries (add rows for completed specs identified in Phase A)
   - ADR table entries (add new ADRs discovered in Phase A)
   - Test coverage section (update counts)
   - Header: commit count, date, branch hash
   - Risk register: close risks addressed by shipped features
   - Recommended next actions: refresh based on current state
5. Show diff preview to user and ask for confirmation
6. Write updated file to `{status_file}`
7. If CHANGELOG gaps were found in Phase A, suggest: "CHANGELOG.md is missing entries for {N} features. Add them? (y/N)"
   - On confirmation, add entries under `[Unreleased]` with appropriate categories
8. Report changes made

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

---

## Deep Pipeline (`--deep`)

When `$ARGUMENTS` contains `--deep`, execute this multi-agent pipeline -- the most complex in the roadmap plugin. Three Sonnet agents analyze the project simultaneously from PM, Architect, and Roadmap perspectives. A synthesizer then merges findings and surfaces contradictions.

### Phase 1: Context Gathering (2 Parallel Haiku Agents)

Launch **2 Haiku agents in parallel**:

**Agent A -- Config & Documentation**:
"Run the context discovery protocol from CONTEXT_DISCOVERY.md. Return: project name, configuration (output_dir, context_dir, status_file), personas, project phases, documentation inventory (categorized as: status docs, gap analyses, specs, ADRs, research), and key constraints. Read all documentation files discovered."

**Agent B -- Codebase Scan**:
"Detect tech stack from build files using TECH_STACK_DETECTION.md. Scan the codebase for: module inventory (name, source file count, test file count), directory structure, detected architecture patterns, migration count, TODO/FIXME count, and infrastructure files (Docker, CI/CD, deployment). Return structured results."

Provide each agent with the relevant reference files.

### Phase 2: Parallel Perspective Analysis (3 Parallel Sonnet Agents)

Launch **3 Sonnet agents simultaneously**, each with the combined context from Phase 1 but a different analytical lens:

**Agent C -- PM Perspective**:
"You are a product manager analyzing this project. Using the context provided, identify: requirement gaps (features needed but not built), unmet user needs, scope creep (features built that aren't in documented scope), missing user stories for existing features, user-facing risks, and priority recommendations. Focus on user value, not technical concerns. After your analysis, append a Builder Confessions block."

**Agent D -- Architect Perspective**:
"You are a systems architect analyzing this project. Using the context provided, identify: architectural risks (boundary violations, pattern drift, tech debt), module maturity imbalances, missing infrastructure (monitoring, error handling, security), data model concerns, scalability bottlenecks, and dependency risks. Focus on structural health, not user stories. After your analysis, append a Builder Confessions block."

**Agent E -- Roadmap Perspective**:
"You are a project analyst analyzing this project. Using the context provided, assess: phase/milestone completion status, gap closure rate, blocker chains, spec pipeline status, documentation freshness, velocity indicators, and timeline risk. Focus on project trajectory, not architecture or requirements. After your analysis, append a Builder Confessions block."

Each agent must end with a **Builder Confessions block**:
```markdown
## Builder Confessions
- **Assumption**: {what was assumed without verification}
- **Uncertainty**: {areas where confidence is low}
- **Shortcut**: {where a deeper analysis was skipped}
- **Missing data**: {what couldn't be found in the codebase}
```

### Phase 3: Cross-Reference Synthesis (Sonnet Agent)

Launch a **single Sonnet agent** to merge the three perspectives:

**Agent prompt**: "You are a project health synthesizer. You have three independent analyses of the same project -- from PM, Architect, and Roadmap perspectives. Your job is to:

1. **Merge findings** into a unified view -- deduplicate, consolidate related findings
2. **Surface contradictions** -- where perspectives disagree (e.g., PM says 'auth is ready' but Architect says 'boundary violations in auth module')
3. **Map cross-perspective dependencies** -- PM gap X requires architectural change Y which blocks roadmap milestone Z
4. **Build unified risk register** -- combine risks from all three perspectives, deduplicate, re-score with cross-perspective context
5. **Produce Cross-Perspective Insights** -- the unique findings that only emerge from comparing all three perspectives

Output format: A comprehensive Project Health Report using the template from TEMPLATES.md, with an additional 'Cross-Perspective Insights' section."

Provide the agent with:
- All three Phase 2 analyses (including their Builder Confessions)
- The Project Health Report template from [TEMPLATES.md](../../references/TEMPLATES.md)

### Phase 4: Confidence Scoring (Parallel Haiku Agents)

For each major finding in the synthesized report, launch a **parallel Haiku agent** to score confidence:

**Agent prompt**: "Score this finding 0-100. Consider: Is it backed by file paths or evidence? Was it flagged in Builder Confessions? Do multiple perspectives agree? Use rubric: 90-100 = strong evidence from multiple perspectives, 70-89 = good evidence but some uncertainty, 50-69 = single-perspective finding with limited evidence, below 50 = speculative."

**Filter**: Remove findings scoring below 70. Tag findings 70-89 with `[NEEDS VALIDATION]`.

### Phase 5: Report Generation

1. Produce the final **Project Health Report** with all confidence annotations
2. Include the **Cross-Perspective Insights** section (unique to `--deep`)
3. Include a **Methodology** footer noting this was a multi-agent analysis with 3 parallel perspectives
4. Every finding includes its source perspective (PM/Architect/Roadmap) and confidence score
5. Save to `{output_dir}/reports/{YYYY-MM-DD}-health-report.md` (ask user to confirm)

### Deep Pipeline Summary

| Phase | Agents | Model | Purpose |
|-------|--------|-------|---------|
| 1 | 2 parallel | Haiku | Config/docs gathering + codebase scanning |
| 2 | 3 parallel | Sonnet | PM + Architect + Roadmap perspectives (each with Confessions) |
| 3 | 1 | Sonnet | Cross-reference synthesis, contradiction detection, unified risk register |
| 4 | N parallel | Haiku | Per-finding confidence scoring, filter below 70 |
| 5 | -- | -- | Present with annotations, save health report |
