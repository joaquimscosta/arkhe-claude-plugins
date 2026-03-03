# Release Workflow: Detailed Process

## Overview

The release workflow operates in 7 phases for creating releases, plus a separate scaffolding workflow for setting up new projects.

## Phase 1: Input Validation

Parse and validate all arguments before any side effects.

**Arguments:**
- `<version>` — Semantic version (e.g., `1.6.0` or `v1.6.0`)
- `--yes` / `-y` — Skip interactive confirmation (for CI/automation)
- `--skip-monitor` — Trigger workflow without waiting for completion
- `--setup` — Switch to scaffolding mode

**Validation Rules:**
- Version must match `^[0-9]+\.[0-9]+\.[0-9]+$` after stripping `v` prefix
- Version argument is required (unless `--setup` mode)

## Phase 2: Pre-flight Checks

Verify all prerequisites before making changes.

1. **CHANGELOG entry exists** — `grep -qE "^## \[$VERSION\]" CHANGELOG.md`
2. **Release doesn't exist** — `gh release view "v$VERSION"` returns non-zero
3. **gh CLI authenticated** — `gh auth status` succeeds
4. **Git remote accessible** — `gh repo view` returns repo URL

If any check fails, report the issue and exit with clear instructions.

## Phase 3: CHANGELOG Link Management

Add comparison links to the bottom of CHANGELOG.md.

### Previous Version Detection

```bash
# Find the second ## [X.Y.Z] header (first is current version)
PREV_VERSION=$(grep -E "^## \[[0-9]+\.[0-9]+\.[0-9]+\]" CHANGELOG.md \
    | head -2 | tail -1 | sed 's/.*\[\([0-9.]*\)\].*/\1/')
```

### Link Format

- **With previous version:** `[1.6.0]: https://github.com/user/repo/compare/v1.5.0...v1.6.0`
- **First version:** `[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0`

### Idempotency

Skip if `grep -qE "^\[$VERSION\]:" CHANGELOG.md` already matches.

### Unreleased Link Update

The `[Unreleased]` link is updated to compare from the new version to HEAD:
```
[Unreleased]: https://github.com/user/repo/compare/v1.6.0...HEAD
```

## Phase 4: Git Operations

Commit and push CHANGELOG.md changes if modified.

1. Check for uncommitted changes: `git diff --quiet CHANGELOG.md`
2. **Confirm with user** before committing (unless `--yes` flag)
3. Stage: `git add CHANGELOG.md`
4. Commit: `git commit -m "docs: prepare release $VERSION"`
5. Push: `git push origin main`

## Phase 5: Workflow Triggering

Trigger the GitHub Actions release workflow.

```bash
gh workflow run release.yml -f version="$VERSION"
```

The workflow must:
- Accept a `version` input via `workflow_dispatch`
- Have `contents: write` permission
- Use `actions/checkout@v4` with `fetch-depth: 0`

## Phase 6: Workflow Monitoring

Poll workflow status until completion (unless `--skip-monitor`).

1. Wait 5 seconds for workflow to register
2. Get run ID: `gh run list --workflow=release.yml --limit=1 --json databaseId`
3. Poll every 5 seconds: `gh run view "$RUN_ID" --json status -q '.status'`
4. On completion, check conclusion: `gh run view "$RUN_ID" --json conclusion`

### Status Values
- `queued` — Waiting for runner
- `in_progress` — Running
- `completed` — Finished (check conclusion)

### Conclusion Values
- `success` — Release created
- `failure` — Step failed
- `cancelled` — Manually cancelled

## Phase 7: Post-Release

Report result with actionable URLs.

**On success:**
```
Release v1.6.0 created successfully!
View: https://github.com/user/repo/releases/tag/v1.6.0
```

**On failure:**
```
Workflow failed: failure
Logs: https://github.com/user/repo/actions/runs/12345
```

## Setup Mode Workflow

When `--setup` is specified, scaffold the full release pipeline.

### Step 1: Check Existing Files

Before scaffolding, check if any target files already exist:
- `scripts/release.sh`
- `.github/workflows/release.yml`
- `.github/workflows/scripts/validate-changelog.sh`
- `.github/workflows/scripts/extract-release-notes.sh`
- `.github/workflows/scripts/create-github-release.sh`

If files exist, warn the user and ask whether to overwrite.

### Step 2: Create Directories

```bash
mkdir -p scripts
mkdir -p .github/workflows/scripts
```

### Step 3: Copy Templates

Read each template from the skill's directories and write to target locations:

| Source (in skill) | Target (in project) |
|-------------------|---------------------|
| `scripts/release.sh` | `scripts/release.sh` |
| `scripts/validate-changelog.sh` | `.github/workflows/scripts/validate-changelog.sh` |
| `scripts/extract-release-notes.sh` | `.github/workflows/scripts/extract-release-notes.sh` |
| `scripts/create-github-release.sh` | `.github/workflows/scripts/create-github-release.sh` |
| `templates/release.yml` | `.github/workflows/release.yml` |

### Step 4: Set Permissions

```bash
chmod +x scripts/release.sh
chmod +x .github/workflows/scripts/*.sh
```

### Step 5: Report

List all created files and provide next steps:
1. Ensure CHANGELOG.md exists
2. Commit the scaffolded files
3. Run `/release <version>` for the first release

## Script Templates Reference

### release.sh

Local release orchestrator that wraps the full workflow. Supports `--yes` for non-interactive use and `--skip-monitor` to skip polling.

### release.yml (GitHub Actions)

Workflow triggered by `workflow_dispatch` with a `version` input. Steps:
1. Checkout with full history
2. Validate semver format
3. Check release doesn't exist
4. Check/create git tag
5. Validate CHANGELOG entry
6. Extract release notes
7. Create GitHub Release

### validate-changelog.sh

Verifies `## [VERSION]` header exists in CHANGELOG.md. Uses Keep a Changelog format.

### extract-release-notes.sh

Extracts content between `## [VERSION]` and the next `## [` header using awk. Outputs to `release_notes.md`.

### create-github-release.sh

Creates a GitHub Release via `gh release create` using the extracted release notes. Requires `GH_TOKEN` environment variable.

## Integration with Other Skills

- **`/changelog`** (generating-changelog) — Generate CHANGELOG entries before releasing
- **`/commit`** (creating-commit) — Commit changes during release preparation
- **`/create-pr`** (creating-pr) — Create PRs if releasing from a branch
