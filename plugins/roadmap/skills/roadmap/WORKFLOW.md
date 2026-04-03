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
6. **Plan reference** — if `{plan_file}` exists, append: "Full project plan: `{plan_file}`". Apply the same drift detection to `{plan_file}` and suggest `/roadmap plan sync` if stale.

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
3. If `{plan_file}` exists, also consult:
   - The Backlog section for prioritized themes with dependencies
   - The Timeline for the next "Not Started" phase
   - Use these as additional inputs when ranking
4. Rank by: impact, effort, dependencies, urgency
5. Recommend 3-5 prioritized next actions

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
9. If `{plan_file}` exists and updates included phase status changes or new specs completed, suggest: "Phase status changed. Run `/roadmap plan sync` to update the project plan."

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
5. If `{plan_file}` exists, cross-reference: show which phase each spec belongs to from the plan's Spec Traceability section. Flag specs that are Complete but not linked to any phase.

### `plan`

#### `plan scaffold`

1. Read `.arkhe.yaml` for `plan_file` path (default: `docs/PROJECT-PLAN.md`)
2. Check if `{plan_file}` exists:
   - If yes: warn "Plan document already exists at `{plan_file}`. Overwrite / sync instead / cancel?"
   - If user chooses sync, redirect to `plan sync`; if cancel, stop
3. Run full context discovery (CONTEXT_DISCOVERY.md Phases 1–7)
4. **Gather planning artifacts:**
   - Read `{status_file}` — extract: phase table (ID, scope, status, evidence), module maturity, spec pipeline, risk register
   - Glob `docs/**/roadmap.md` — extract: phase lists, backlog themes, known risks
   - Glob `docs/**/backlog.md` — extract: themes with status, priorities, dependencies
   - Glob `docs/superpowers/plans/*.md` — extract: implementation plan titles and dates
5. **Scan specs:**
   - Glob `{specs_dir}/*/spec.md` (specs_dir from `.arkhe.yaml`, default: `arkhe/specs`)
   - For each: extract ID (directory name), title (first `#` heading), status (`Status:` field or frontmatter)
   - Build inventory: `{id, title, status}`
6. **Scan ADRs:**
   - Glob `docs/adr/[0-9]*.md`
   - For each: extract number (filename), title (first `#` heading), status (`Status` section or `_Status:_` line)
   - Build inventory: `{number, title, status}`
7. **Run hybrid linking algorithm** (see § Hybrid Linking Algorithm below)
8. **Generate plan document** using the PROJECT-PLAN.md template from [TEMPLATES.md](../../references/TEMPLATES.md):
   - Fill Timeline from phases found in status doc and roadmaps
   - Fill Phase Details with scope, status, linked specs, linked ADRs, evidence
   - Fill Backlog from themes with priority and dependencies
   - Fill Spec Traceability from inventory + phase mappings
   - Fill ADR Traceability from inventory + phase mappings
   - Include Sprint/Iteration Log only if sprint data found in existing docs
   - Fill References with paths to all source documents read
9. **Present proposed plan** in chat with confidence markers:
   - `[AUTO-LINKED]` on phase-to-spec and phase-to-ADR mappings detected from git
   - `[MANUAL]` on mappings found explicitly in existing docs
   - `[UNLINKED]` on specs/ADRs that couldn't be mapped to any phase
10. **Confirm**: "Review the proposed plan. Adjust any linkages? (Type corrections or 'approve')"
    - Apply user corrections to linkage mappings
11. **Write** to `{plan_file}`
12. Report: "Plan created at `{plan_file}` with N phases, M specs linked, K ADRs linked, J backlog themes."

#### `plan show`

1. Read `.arkhe.yaml` for `plan_file` path
2. If `{plan_file}` doesn't exist:
   - "No plan document found at `{plan_file}`. Run `/roadmap plan scaffold` to create one."
   - Stop
3. Read `{plan_file}`
4. Parse and present summary view:
   ```
   ## Project Plan Summary
   _Source: {plan_file} (last synced: {date from git})_

   ### Timeline
   | Phase | Status | Specs | ADRs |
   |-------|--------|-------|------|
   | {id} | {status} | {count} | {count} |

   ### Progress
   - Phases: {done}/{total} complete ({percent}%)
   - Specs: {linked}/{total} linked to phases
   - ADRs: {linked}/{total} linked to phases
   - Backlog: {count} themes ({in_progress} active)

   ### Active Phase(s)
   {Details for phases with status "In Progress"}

   ### Next Up
   {First "Not Started" phase or top backlog item}
   ```
5. **Drift detection**:
   - Get last `{plan_file}` commit: `git log -1 --format="%H %ai" -- {plan_file}`
   - Count `feat:`/`fix:` commits since: `git log {hash}..HEAD --oneline --no-merges | grep -cE "^[a-f0-9]+ (feat|fix):"`
   - If >= 3, append: `"⚠️ Plan may be stale: {N} feature/fix commits since last sync ({date}). Run /roadmap plan sync to update."`

#### `plan sync`

1. Read `.arkhe.yaml` for `plan_file` path
2. If `{plan_file}` doesn't exist: suggest `scaffold` and stop
3. **Phase A: Git History Scan**
   - Get last plan doc commit: `git log -1 --format="%H %ai" -- {plan_file}`
   - If no previous commit, warn and suggest `scaffold` instead
   - List commits since: `git log {last_hash}..HEAD --oneline --no-merges`
   - Categorize:
     - New/modified specs: changes in `{specs_dir}/` paths
     - New ADRs: new files in `docs/adr/`
     - Phase signals: `feat:` commits grouped by PR, phase references in messages
     - Backlog changes: modifications to `docs/**/backlog.md` or `docs/**/roadmap.md`
   - Present **"What Changed"** summary to user
4. **Phase B: Auto-detect new links**
   - For new specs from Phase A: run hybrid linking (git-based phase mapping)
   - For new ADRs from Phase A: run hybrid linking
   - For phase completion signals: propose status changes ("Not Started" → "In Progress" or "Done")
5. **Phase C: Read and merge**
   - Read existing `{plan_file}`
   - Identify user-edited sections (content not matching auto-generated patterns)
   - Propose changes as a diff:
     ```
     ## Proposed Updates to {plan_file}

       ~ Phase 4 status: In Progress → Done
       + Spec 026: {title} → linked to Phase 4 [AUTO-LINKED]
       + ADR 0011: {title} → linked to Phase 5 [AUTO-LINKED]
       ~ Backlog Theme 1: In Progress → Done
     ```
6. **Phase D: Confirm and write**
   - "Apply updates to `{plan_file}`? (y/N)"
   - On confirmation: write updated file preserving user-edited content
   - Report changes made

---

## Hybrid Linking Algorithm

Maps specs and ADRs to project phases using git history + document content analysis. Used by `plan scaffold` and `plan sync`.

### Step 1: Collect Phase Definitions

Extract phases from existing planning documents:
- `{status_file}` phase tables — each row has a phase ID, scope, status, and PR/commit references
- `docs/**/roadmap.md` — completed phases lists with PR/commit evidence

These define the canonical phase list with date ranges (inferred from PR merge dates or commit dates in evidence).

### Step 2: Build Phase Commit Ranges

For each phase that has PR or commit evidence:

```bash
# For phases with PR references (e.g., "PRs #19, #21")
git log --oneline --format="%H %ai" -- . | grep "(#19)" | tail -1   # first commit
git log --oneline --format="%H %ai" -- . | grep "(#21)" | head -1   # last commit

# For phases with commit references (e.g., "2fa521a")
git log -1 --format="%ai" 2fa521a   # get date
```

Build a timeline: `{phase_id, start_date, end_date}` for each phase. For phases without explicit evidence, estimate ranges from surrounding phases.

### Step 3: Map Specs to Phases

For each spec in `{specs_dir}/*/spec.md`:

1. **Explicit match** (highest confidence): Check if the spec ID is mentioned in a phase's scope/evidence column in the status doc. Mark as `[MANUAL]`.
2. **Git-based match** (medium confidence): Find the spec file's creation commit:
   ```bash
   git log --diff-filter=A --format="%H %ai" -- {specs_dir}/{spec_dir}/spec.md
   ```
   Map the creation date to the phase whose date range contains it. Mark as `[AUTO-LINKED]`.
3. **Content-based match** (low confidence): Search spec content for phase references, PR numbers, or feature keywords matching a phase's scope.
4. **Unmatched**: Mark as `[UNLINKED]`.

### Step 4: Map ADRs to Phases

Same cascade as Step 3, but for ADR files in `docs/adr/`:

1. **Explicit match**: ADR referenced in status doc's ADR table with phase context → `[MANUAL]`
2. **Git-based match**: ADR creation date falls within a phase's date range → `[AUTO-LINKED]`
3. **Content-based match**: ADR `## Context` references specific features or phases
4. **Unmatched** → `[UNLINKED]`

### Step 5: Present for Confirmation

Group by confidence level:

```
## Proposed Linkages

### Confirmed (from existing docs)
- Spec 022 → Phase 3e [MANUAL] — listed in PROJECT-STATUS.md
- ADR-0007 → Phase ASR-1 [MANUAL] — referenced in papia-asr/roadmap.md

### Auto-Detected (from git history)
- Spec 020 → Phase 3d [AUTO-LINKED] — created 2026-03-08, during Phase 3d window
- ADR-0010 → Phase 3b [AUTO-LINKED] — created 2026-03-01, during Phase 3b window

### Unlinked
- Spec 000 → ? [UNLINKED] — created before any defined phase
```

User can approve all, adjust individual mappings, or skip unlinked items.

### Step 6: Persist Mappings

Store confirmed mappings in the plan document's Phase Details sections:

```markdown
### Phase 3e: Glossary Management + Dictionary Browser
- **Status:** Done
- **Specs:** 022 (Glossary Management UX), 023 (Glossary UX Polish), 024 (Glossary Gap Detection), 025 (Dictionary Browser)
- **ADRs:** _(none)_
- **Evidence:** PRs #32, #33
```

These explicit listings become the source of truth for future `sync` operations — already-linked items are not re-analyzed.

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
