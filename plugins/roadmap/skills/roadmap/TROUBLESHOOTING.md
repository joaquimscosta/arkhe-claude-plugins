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

## Update Phase A Shows "No Commits Since Last Update" But Docs Seem Wrong

**Symptom:** Phase A (git history scan) reports no drift, but the status doc has incorrect or outdated content.

**Cause:** The status file was recently committed (perhaps with errors or incomplete data), so git history shows no gap.

**Fix:** Phase B (full codebase scan) still runs regardless of Phase A results. Phase A is additive context that helps Phase B be more targeted — but Phase B catches discrepancies whether or not git shows drift. If the content is wrong despite a recent commit, Phase B will propose corrections based on the actual codebase state.

## When to Use `update` vs `delta`

| Mode | What it does | Writes files? |
|------|-------------|---------------|
| `update` | Phase A (git history) + Phase B (full codebase scan) → writes updated status doc | Yes (with confirmation) |
| `delta` | Compares status doc against codebase state → read-only report | No (chat output only) |

Use `delta` when you want to **see** what's stale without changing anything. Use `update` when you want to **fix** the staleness.

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

## When to Use `update` vs `update --incremental`

| Mode | What it does | Speed | Best for |
|------|-------------|-------|----------|
| `update` | Phase A (git history) + Phase B (full codebase scan) → writes full status doc | Slow (~5 min) | Monthly health checks, first-time setup, correcting accumulated drift |
| `update --incremental` | Phase A (git history) + targeted edits only → surgical updates | Fast (~1 min) | Post-sprint sync, after `/core:develop`, quick status updates |

Use `--incremental` when you know what changed (just finished a sprint) and want to quickly record it. Use full `update` when you suspect the document has drifted and need a comprehensive reconciliation.

**Note:** `--incremental` reads wave-context files from `/core:develop` if available, but works with git-only when they aren't present.

## Plan Scaffold Produces Empty Phases

**Symptom:** Timeline section has few or no phases after scaffolding.

**Cause:** No status document or roadmap files with phase tables found. The scaffold requires at least one source of phase information.

**Fix:**
1. Ensure `{status_file}` exists and contains a phase table (run `/roadmap update` to create one)
2. Or ensure `docs/**/roadmap.md` files exist with phase lists
3. If starting from scratch, create a minimal phase table in your status doc first, then scaffold

## Plan Sync Says "No Changes" But Plan Seems Stale

**Symptom:** `/roadmap plan sync` reports no changes, but the plan document has incorrect or outdated data.

**Cause:** The plan doc was recently synced (git shows no gap between sync and HEAD), but content was already wrong at last sync time.

**Fix:** Run `/roadmap plan scaffold` to regenerate from current state. Scaffold always rebuilds from scratch (with overwrite confirmation), while sync only applies incremental changes from git history since the last sync.

## Next Actions Seem Outdated

**Symptom:** `/roadmap next` returns recommendations that don't reflect recent work.

**Cause:** Cache hasn't been invalidated. Recalculation triggers when either: 3+ feat/fix commits since last save, or the status doc was updated more recently than next-actions.md. If neither condition is met, the cached file is served.

**Fix:**
1. Force recalculation with merge: `/roadmap next --force`
2. Or run `/roadmap update` first — the status drift check will trigger merge-based recalculation on next `/roadmap next`
3. For a completely fresh start (discard all existing items): `rm arkhe/roadmap/next-actions.md` then run `/roadmap next`

## Merge Matched Wrong Items

**Symptom:** During merge, the diff preview shows an item being updated (`~`) when it should be a different item, or two unrelated items were matched.

**Cause:** The title-based matching found a false positive (similar titles referencing different work).

**Fix:**
1. Decline the merge at the confirmation gate ("Apply merged recommendations? N")
2. Manually edit `next-actions.md` to correct item titles or content
3. Run `/roadmap next --force` again — the corrected titles will produce better matches

## User-Added Items Keep Accumulating

**Symptom:** The `### User-Added` section in `next-actions.md` grows with items that are no longer relevant.

**Cause:** User-added items are always preserved across recalculations. The merge will flag items that appear completed (with `?` in the diff preview), but never auto-removes them.

**Fix:** Manually edit `next-actions.md` and remove completed or irrelevant items from the `### User-Added` section. The next merge will not re-add them.
