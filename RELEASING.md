# Releasing

This document describes the release process for arkhe-claude-plugins.

## Overview

Releases are created via a manual GitHub Actions workflow that:

1. Validates the version format (semantic versioning)
2. Verifies a CHANGELOG.md entry exists
3. Creates a git tag (if needed)
4. Creates a GitHub Release with release notes extracted from CHANGELOG.md

## Prerequisites

- Push access to the repository
- CHANGELOG.md entry for the version you're releasing

## Release Process

### Step 1: Update CHANGELOG.md

Add an entry for the new version following [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.4.0] - 2026-01-23

### Added
- New feature description

### Changed
- Change description

### Fixed
- Bug fix description
```

**Tips:**

- Use the `/changelog` skill in Claude Code to generate the entry
- Move content from `## [Unreleased]` to the new version section
- Update the comparison links at the bottom of CHANGELOG.md

### Step 2: Commit and Push

```bash
git add CHANGELOG.md
git commit -m "docs: prepare release 1.4.0"
git push origin main
```

### Step 3: Trigger the Release Workflow

1. Go to the repository on GitHub
2. Navigate to **Actions** tab
3. Select **"Create Release"** workflow from the left sidebar
4. Click **"Run workflow"** button
5. Enter the version (e.g., `1.4.0` or `v1.4.0`)
6. Click **"Run workflow"**

The workflow will:

- Validate the version format
- Check that the release doesn't already exist
- Verify CHANGELOG.md has an entry for the version
- Extract release notes from CHANGELOG.md
- Create a git tag (e.g., `v1.4.0`)
- Create a GitHub Release with the extracted notes

## Version Format

Use semantic versioning (X.Y.Z):

- **Major (X)**: Breaking changes
- **Minor (Y)**: New features, backwards compatible
- **Patch (Z)**: Bug fixes, backwards compatible

The workflow accepts versions with or without the `v` prefix:

- `1.4.0` → creates tag `v1.4.0`
- `v1.4.0` → creates tag `v1.4.0`

## Troubleshooting

### "No CHANGELOG entry found for version X.Y.Z"

The workflow requires a CHANGELOG.md entry before creating a release. Add an entry with the header:

```markdown
## [X.Y.Z] - YYYY-MM-DD
```

### "Release vX.Y.Z already exists"

A release with this version already exists. Either:

- Use a different version number
- Delete the existing release if it was created in error

### "Invalid version format"

The version must follow semantic versioning (X.Y.Z). Examples:

- Valid: `1.4.0`, `2.0.0`, `1.10.5`
- Invalid: `1.4`, `v1`, `1.4.0-beta`

## Files

| File | Purpose |
| ---- | ------- |
| `.github/workflows/release.yml` | Main workflow orchestration |
| `.github/workflows/scripts/validate-changelog.sh` | Verifies CHANGELOG entry exists |
| `.github/workflows/scripts/extract-release-notes.sh` | Extracts version section from CHANGELOG |
| `.github/workflows/scripts/create-github-release.sh` | Creates GitHub Release via gh CLI |
