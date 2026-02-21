# Roadmap Skill — Troubleshooting

Common issues and fixes for the Roadmap Analyst skill.

## Status Report Shows No Modules

**Symptom:** Module table is empty or shows only root-level files.

**Cause:** Codebase structure doesn't match expected patterns.

**Fix:**
1. Create `.arkhe/roadmap/architecture.md` describing your module structure:
   ```markdown
   ## Modules
   - `services/auth/` — Authentication service
   - `services/api/` — API gateway
   - `web/` — Frontend application
   ```
2. Or ensure modules follow standard patterns: `src/`, `apps/`, `packages/`, `libs/`

## Gap Analysis Returns Empty

**Symptom:** Gaps mode says "No gap analysis documents found."

**Cause:** No documents matching gap analysis patterns found.

**Fix:**
1. Create `.arkhe/roadmap/documents.md` listing your gap analyses:
   ```markdown
   ## Gap Analyses
   - `docs/reports/api-gaps.md` — API completeness assessment
   - `docs/reports/security-review.md` — Security findings
   ```
2. Or place gap analysis docs in standard locations: `docs/reports/`, `docs/gaps/`

## Delta Report Says "No Previous Status"

**Symptom:** Delta mode can't find a previous status document to compare against.

**Cause:** No `PROJECT-STATUS.md` or configured status file exists.

**Fix:**
1. Run `update` mode first to create a baseline: `/roadmap:roadmap update`
2. Or set the status file path in `.arkhe.yaml`:
   ```yaml
   roadmap:
     status_file: docs/PROJECT-STATUS.md
   ```

## Update Mode Overwrites Custom Sections

**Symptom:** Running `update` removes custom sections from the status doc.

**Cause:** Custom sections don't match expected format.

**Fix:** The skill preserves existing structure. If custom sections are lost:
1. Use version control to restore: `git diff docs/PROJECT-STATUS.md`
2. Add custom sections under a `## Custom` heading — the skill won't modify unknown headings

## Maturity Ratings Seem Wrong

**Symptom:** Module rated as "Stub" but has real code.

**Cause:** Files don't match tech-stack-aware scan patterns.

**Fix:**
1. Check that your tech stack was correctly detected (build file present at root)
2. Describe module structure in `.arkhe/roadmap/architecture.md`
3. Verify files are in expected locations for your framework

## Blockers Mode Misses External Dependencies

**Symptom:** Known external blockers (API keys, approvals) not shown.

**Cause:** External dependencies aren't documented in discoverable files.

**Fix:** Document blockers in:
1. `.arkhe/roadmap/project.md` under a `## Blockers` section
2. Or in your status document under a `## Blockers` heading
3. Or in gap analysis documents

## Specs Mode Can't Find Specs

**Symptom:** Spec pipeline is empty despite having spec files.

**Cause:** Specs are in a non-standard location.

**Fix:**
1. Standard locations: `arkhe/specs/*/spec.md`, `specs/**/*.md`, `docs/specs/**/*.md`
2. Or configure in `.arkhe.yaml`:
   ```yaml
   roadmap:
     context_dir: .arkhe/roadmap
   ```
   And in `.arkhe/roadmap/documents.md`:
   ```markdown
   ## Specs
   - `planning/features/*/requirements.md` — Feature specs
   ```

## Risk Scores Seem Arbitrary

**Symptom:** Risk likelihood/impact ratings don't match project context.

**Cause:** Insufficient context about project priorities and constraints.

**Fix:**
1. Define project constraints in `.arkhe/roadmap/project.md`:
   ```markdown
   ## Constraints
   - Launch deadline: Q2 2026
   - Single developer
   - Budget: limited cloud spend
   ```
2. These constraints inform risk scoring (tight deadline = higher impact for delays)
