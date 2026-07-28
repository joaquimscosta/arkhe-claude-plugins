---
name: sync-docs
description: >
  Sync official Anthropic documentation and analyze impact on project components.
  Runs docs/reference/update-claude-docs.sh, computes diffs, and reports impacts
  on the skill validator, plugins, and project documentation. Use when user
  mentions "sync docs", "update reference docs", "refresh docs", or "check doc changes".
argument-hint: "[--dry-run]"
---

# Sync Docs

Sync official Anthropic documentation into `docs/reference/` and produce an impact analysis report.

## Quick Start

Run the sync and diff script:

```bash
scripts/sync_and_diff.py
```

Preview changes without overwriting:

```bash
scripts/sync_and_diff.py --dry-run
```

## Execution

### Phase 1: Sync & Diff

1. Execute `scripts/sync_and_diff.py` (or with `--dry-run` if `$ARGUMENTS` contains `--dry-run`)

   Capture the **whole** JSON document. Never pipe it through `tail`/`head` — `sync_health` and `sync_result` are at the top of the output and are the first things to read.

2. **Gate on `sync_health` before anything else**:

   - If `sync_health.complete` is `true`, proceed to step 3.
   - If `sync_health.complete` is `false`, **stop and do not report impacts for the files in `sync_health.not_fetched`.** Their `"changed": false` only means "not downloaded", not "up to date". Print `sync_health.warning`, re-run the sync once to retry the failed files, and if they still fail, report them explicitly as UNVERIFIED in the summary table rather than as unchanged.

   > `update-claude-docs.sh` exits `0` when *at least one* file downloads, so a non-zero exit code is not the signal — a 1-of-8 sync also exits `0`. Trust `sync_health`, not `sync_result.exit_code`.

3. Parse the rest of the JSON output
4. Display a summary table of changed/unchanged files, using `download_status` to mark any file that was not fetched

### Phase 2: Impact Analysis

For each **changed** file, perform the following analysis. See [WORKFLOW.md](WORKFLOW.md) for detailed steps.

#### 2a. Skill Validator Impact (CRITICAL priority)

Check `discrepancies` in the JSON output:

- **`skill_frontmatter_keys.in_docs_not_validator`** (CRITICAL): New fields in SKILLS.md the validator will reject as unknown (FM009). Report exact fields and line in `validate_skill.py` to update (`ALLOWED_FRONTMATTER_KEYS`, ~line 151).
- **`skill_frontmatter_keys.in_validator_not_docs`** (WARNING): Fields the validator allows but SKILLS.md no longer documents. May be from SUBAGENTS.md (valid for `context: fork`) or deprecated.
- **`subagent_frontmatter_keys`** (INFO): New subagent fields from SUBAGENTS.md. Not all are valid in skill frontmatter — report for context. Only flag fields that overlap with skill usage (e.g., `maxTurns`, `mcpServers`, `memory`, `skills`).
- **`hook_events.in_docs_not_validator`** (CRITICAL): New hook events the validator will reject (HK001). Report the line to update (`VALID_HOOK_EVENTS`, ~line 1021).
- **`hook_events.in_validator_not_docs`** (WARNING): Hook events the validator knows but docs no longer list.
- **`memory_scopes`**: Review manually if SUBAGENTS.md changed — check if memory scope options expanded.

#### 2b. Plugin Component Impact (WARNING priority)

For each changed synced doc, identify the conceptual areas that changed (new fields, deprecated features, renamed concepts). Then:

1. Use Grep to search `plugins/*/` for references to changed concepts
2. Flag plugins using deprecated patterns
3. Note new capabilities not yet leveraged (as INFO)

#### 2c. Project Documentation Impact (WARNING priority)

Check these files for stale references to synced doc content:

- `CLAUDE.md` — Plugin Component Guidelines section, Key Documentation Files section
- `docs/README.md` — Synced Documentation section, learning paths
- `docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md` — Frontmatter reference, patterns

## Output Format

Present findings as a structured report:

```
=== Documentation Sync Impact Report ===

## Sync Summary
| File | Status | +Lines | -Lines | New Sections | Removed Sections |
|------|--------|--------|--------|--------------|-----------------|
...

## CRITICAL: Skill Validator Updates Required
(List each discrepancy with file, line number, and fix)

## WARNING: Plugin Components Affected
(List affected plugins and what changed)

## WARNING: Project Documentation Stale
(List affected doc files and what to update)

## INFO: New Capabilities Available
(List new features from updated docs that could be leveraged)
```

If no files changed, report: "All documentation is up to date. No impacts detected."

## References

- [WORKFLOW.md](WORKFLOW.md) — Detailed impact analysis steps
- [EXAMPLES.md](EXAMPLES.md) — Example report outputs
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues
