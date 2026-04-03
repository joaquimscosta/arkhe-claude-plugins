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
5. **Diff Preview (Required Format)**

   Present proposed changes using unified diff markers, grouped by document section:

   ```
   ## Proposed Updates to {status_file}

   ### Header
     ~ Last updated: {old_date} -> {new_date}
     ~ Branch: {old_hash} -> {new_hash}
     ~ Velocity: {old_count} -> {new_count} commits

   ### Module Maturity
     ~ {module}: {old_maturity} -> {new_maturity}

   ### Phases
     + Phase {id}: {title} -> Done

   ### Specs
     + Spec {id}: {title} -> Complete

   ### Risks
     - Risk {id}: {title} (closed: shipped in PR #{N})
   ```

   Markers: `+` = added, `-` = removed, `~` = modified. Do NOT use narrative descriptions -- show exact changes.

6. **Confirmation Gate**: "Apply updates to `{status_file}`? (y/N)"
   - If no: present the full updated document as a code block for manual application. Stop here.
7. Write updated file to `{status_file}`
8. If CHANGELOG gaps were found in Phase A, suggest: "CHANGELOG.md is missing entries for {N} features. Add them? (y/N)"
   - On confirmation, add entries under `[Unreleased]` with appropriate categories
9. Report changes made
10. If `{plan_file}` exists and updates included phase status changes or new specs completed, suggest: "Phase status changed. Run `/roadmap plan sync` to update the project plan."

### `update --incremental`

Lightweight post-sprint sync. Skips full codebase scan (Phase B). Uses git history + optional wave context to apply targeted edits. Designed to be fast enough to use after every sprint.

#### Step 1: Read Wave Context (Optional)

If `/core:develop` was used for the most recent sprint:
- Glob `{specs_dir}/*/wave-context-*.md` for completion summaries
- Read the most recent wave context file (by modification date)
- Extract: features built, files modified, tests added, validation results

**Fallback**: If no wave-context files found, skip this step and rely entirely on git history from Step 2. The incremental update works without `/core:develop` — wave context just provides richer detail.

#### Step 2: Phase A — Git History Scan

Same protocol as the full `update` Phase A:
1. Read `.arkhe.yaml` for `status_file` path
2. Get last status doc commit
3. List and categorize commits since
4. Present **"What Shipped"** summary

#### Step 3: Targeted Edits (Replaces Phase B)

Read existing `{status_file}`. Apply ONLY the following changes using the **Edit tool** (targeted edits, NOT a full rewrite):

- **Header**: Update date, commit count, branch hash
- **Sprint/Iteration Log**: Add entry for this sprint (if section exists)
- **Module Maturity**: Update ONLY for modules touched in Phase A commits (leave untouched modules as-is)
- **Phase Dashboard**: Mark phases complete if all their specs were delivered
- **Spec Pipeline**: Mark completed specs, add new specs discovered
- **ADR Table**: Add new ADR entries from Phase A
- **Risk Register**: Close risks addressed by shipped features

Do NOT recalculate untouched sections. Do NOT rewrite the entire document. The goal is surgical precision — change only what the git history tells you changed.

#### Step 4: Diff Preview + Confirmation

Use the same unified diff format as the full `update` (see § `update` Phase B step 5):
- Group changes by document section using `+`/`-`/`~` markers
- "Apply updates to `{status_file}`? (y/N)"
- If no: present as code block for manual application

#### Step 5: Write + Plan Sync Suggestion

- Write if confirmed
- If `{plan_file}` exists and phase status changed, suggest: "Phase status changed. Run `/roadmap plan sync` to update the project plan."

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
5. **Drift detection** (both conditions must be true):
   - Get last `{plan_file}` commit: `git log -1 --format="%H %ai" -- {plan_file}`
   - Check age: was the plan last committed more than 7 days ago?
   - Count `feat:`/`fix:` commits since: `git log {hash}..HEAD --oneline --no-merges | grep -cE "^[a-f0-9]+ (feat|fix):"`
   - If plan is >7 days old AND >= 3 feat/fix commits exist since, append: `"⚠️ Plan may be stale: {N} feature/fix commits since last sync ({date}). Run /roadmap plan sync to update."`
   - Both conditions prevent false positives: active development weeks with recent syncs won't trigger, and quiet weeks with no commits won't trigger.

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
5. **Phase C: Diff and confirm**
   - Read existing `{plan_file}`
   - Identify user-edited sections (content not matching auto-generated patterns)
   - Present proposed changes using the unified diff format defined in § `update` Phase B step 5 (use `+`/`-`/`~` markers grouped by section). Example:
     ```
     ## Proposed Updates to {plan_file}

     ### Timeline
       ~ Phase 4 status: In Progress -> Done

     ### Spec Traceability
       + Spec 026: {title} -> linked to Phase 4 [AUTO-LINKED]

     ### ADR Traceability
       + ADR 0011: {title} -> linked to Phase 5 [AUTO-LINKED]

     ### Backlog
       ~ Theme 1: In Progress -> Done
     ```
   - Do NOT use narrative descriptions -- show exact changes with markers.
6. **Phase D: Confirm and write**
   - "Apply updates to `{plan_file}`? (y/N)"
   - If yes: write updated file preserving user-edited content
   - If no: present proposed changes as a code block for manual application
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

Build a timeline: `{phase_id, start_date, end_date}` for each phase.

For phases without explicit evidence, estimate the date range as:
- **start** = preceding phase's end date (or first project commit if no predecessor)
- **end** = following phase's start date (or HEAD if no successor)
- If multiple consecutive phases lack evidence, divide the gap equally between them

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

### Phase 1.5: Context Compression (Single Haiku Agent)

Before distributing to Phase 2, compress Phase 1 outputs to reduce token duplication. Launch a **single Haiku agent** receiving both Phase 1 outputs.

**Agent prompt**: "Compress these two context reports into the structured formats below. Preserve ALL data points but eliminate prose. Target: <1,600 tokens total."

**Agent A Compressed Output** (target: <800 tokens):
```
PROJECT: {name}
CONFIG: output_dir={}, context_dir={}, status_file={}, plan_file={}
PERSONAS: {comma-separated list}
PHASES: {id: status} (table, one line per phase)
DOCS: {category: count} (status:N, gaps:N, specs:N, adrs:N, research:N)
CONSTRAINTS: {bullet list of 3-5 key constraints}
```

**Agent B Compressed Output** (target: <800 tokens):
```
STACK: {language, framework, build tool}
MODULES: {name: src_files/test_files/maturity} (table)
ARCH_PATTERN: {detected pattern}
INFRA: {docker:y/n, ci:y/n, deploy:y/n}
TODOS: {count}
MIGRATIONS: {count}
```

Phase 2 agents receive the compressed output from Phase 1.5, not the raw Phase 1 output. This reduces per-agent context from ~8,000 tokens to ~1,600 tokens.

### Phase 2: Parallel Perspective Analysis (3 Parallel Sonnet Agents)

Launch **3 Sonnet agents simultaneously**, each with the compressed context from Phase 1.5 but a different analytical lens:

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

Output format: A comprehensive Project Health Report using ALL 11 sections from the template in TEMPLATES.md. Do not skip sections -- if a section has no findings, include it with 'No issues found in this area.' Every section MUST be present:

1. Executive Summary
2. Phase/Milestone Status
3. Module Implementation Matrix
4. Decision Traceability
5. Documentation Health
6. Gap Analysis Risk Map
7. Dependency Graph (Mermaid)
8. Blocking Chain
9. Risk Register
10. Prioritized Action Plan
11. Recommendations

Additionally, include a 'Cross-Perspective Insights' section for findings that only emerge when all three perspectives are compared."

Provide the agent with:
- All three Phase 2 analyses (including their Builder Confessions)
- The Project Health Report template from [TEMPLATES.md](../../references/TEMPLATES.md)

**Note**: The synthesis agent MAY read codebase files to verify claims from Phase 2 analyses (called "Synthesis Verification"). Limit to 10 file reads maximum -- this is a verification step, not original research. Note any verification reads in the methodology footer.

### Phase 4: Independent Confidence Scoring (Parallel Haiku Agents)

**CRITICAL**: The Phase 3 synthesis agent MUST NOT score its own findings. Phase 4 uses independent agents with NO access to the Phase 3 synthesis narrative or rationale. This separation prevents self-reinforcing confidence where the agent that produced a finding rates its own work highly.

**Option A (Standard, >= 10 findings): Batched Parallel Haiku Agents**

Group findings into batches of 3-5. For each batch, launch a Haiku agent with ONLY:
- The finding text (stripped of synthesis commentary)
- The original evidence (file paths, code references)
- The scoring rubric below

Do NOT provide the Phase 3 synthesis narrative, rationale, or cross-perspective analysis.

**Agent prompt**: "Score each finding 0-100 using ONLY the evidence provided. You have NO knowledge of why these findings were selected or how they relate to each other.

Rubric:
- 90-100: Evidence from multiple independent sources (e.g., PM gap confirmed by Architect code review)
- 70-89: Evidence from one source with corroboration (e.g., file path exists + doc mentions it)
- 50-69: Single-source finding with limited evidence (e.g., only one perspective flagged it)
- Below 50: Speculative or based on assumptions

For each finding, return: score, evidence summary (1 sentence), and action (Include / [NEEDS VALIDATION] / Remove)."

**Option B (Lite, < 10 findings): Single Batch Haiku Agent**

If total findings < 10, use a single Haiku agent receiving ALL findings as a flat list. Same restriction: NO access to Phase 3 synthesis rationale. Same rubric and output format.

**Required Output: Confidence Scoreboard**

Both options MUST produce this table:

```
| # | Finding | Source(s) | Score | Evidence Summary | Action |
|---|---------|-----------|-------|-----------------|--------|
| 1 | {finding} | PM, Arch | 92 | Confirmed by code + docs | Include |
| 2 | {finding} | Roadmap | 78 | Git evidence, no code check | [NEEDS VALIDATION] |
| 3 | {finding} | PM | 55 | Doc-only, not verified | Remove |
```

**Filtering Rules (Non-Negotiable)**:
- Below 70: REMOVE from final report entirely
- 70-89: Tag with `[NEEDS VALIDATION]` and include
- 90+: Include as-is

### Phase 5: Report Generation

1. Produce the final **Project Health Report** with all confidence annotations
2. Include the **Cross-Perspective Insights** section (unique to `--deep`)
3. Include a **Methodology** footer noting this was a multi-agent analysis with 3 parallel perspectives
4. Every finding includes its source perspective (PM/Architect/Roadmap) and confidence score
5. Save to `{output_dir}/reports/{YYYY-MM-DD}-health-report.md` by default. Ask: "Report saved to `{path}`. Keep it? (Y/n)". If user says no, delete the file. Default is SAVE -- `--deep` analysis is expensive and its output should persist.
6. **Actionable Follow-up** — after saving, offer:
   ```
   The health report identified {N} risks and {M} action items. Would you like to:
   1. Update {status_file} risk register with new findings
   2. Generate prioritized backlog items from findings
   3. Both
   4. Skip
   ```
   - Option 1: Read `{status_file}`, find Risk Register section, append new risks (source: "health report {date}"). Show diff preview using the unified diff format (see § `update` Phase B step 5). Confirm before writing.
   - Option 2: Generate markdown backlog items from findings scored 70+: `| # | Item | Source | Priority | Finding |`. Output to chat (not auto-saved).
   - Option 3: Both in sequence.
   - Option 4: Skip.

### Deep Pipeline Summary

| Phase | Agents | Model | Purpose |
|-------|--------|-------|---------|
| 1 | 2 parallel | Haiku | Config/docs gathering + codebase scanning |
| 1.5 | 1 | Haiku | Compress Phase 1 context to structured inventories (<1,600 tokens) |
| 2 | 3 parallel | Sonnet | PM + Architect + Roadmap perspectives (each with Confessions) |
| 3 | 1 | Sonnet | Cross-reference synthesis, contradiction detection, unified risk register |
| 4 | N parallel | Haiku | Independent confidence scoring, scoreboard output, filter below 70 |
| 5 | -- | -- | Save report (default), offer actionable follow-up |
