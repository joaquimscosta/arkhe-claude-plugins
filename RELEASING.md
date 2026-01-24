# Releasing

This document describes the release process for arkhe-claude-plugins.

## Quick Start

### Step 1: Add CHANGELOG Entry

Add an entry for the new version following [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.6.0] - 2026-01-24

### Added
- New feature description

### Changed
- Change description

### Fixed
- Bug fix description
```

**Tip:** Use `/changelog` in Claude Code to generate the entry from commit history.

### Step 2: Run the Release Script

```bash
scripts/release.sh 1.6.0
```

The script will:

- Validate version format
- Check CHANGELOG entry exists
- Add comparison link to CHANGELOG (if missing)
- Commit and push changes (prompts for confirmation)
- Trigger the GitHub Actions workflow
- Monitor and report the result

## Version Format

Use semantic versioning (X.Y.Z):

- **Major (X)**: Breaking changes
- **Minor (Y)**: New features, backwards compatible
- **Patch (Z)**: Bug fixes, backwards compatible

## Troubleshooting

### "No CHANGELOG entry found for version X.Y.Z"

Add an entry to CHANGELOG.md with the header:

```markdown
## [X.Y.Z] - YYYY-MM-DD
```

### "Release vX.Y.Z already exists"

A release with this version already exists. Either:

- Use a different version number
- Delete the existing release: `gh release delete vX.Y.Z --yes`

### "Invalid version format"

The version must follow semantic versioning. Examples:

- Valid: `1.4.0`, `2.0.0`, `1.10.5`
- Invalid: `1.4`, `v1`, `1.4.0-beta`

## Manual Release (Alternative)

If you prefer not to use the release script:

1. Add CHANGELOG entry (as above)
2. Add comparison link at bottom of CHANGELOG.md:

   ```markdown
   [1.6.0]: https://github.com/joaquimscosta/arkhe-claude-plugins/compare/v1.5.0...v1.6.0
   ```

3. Commit and push: `git add CHANGELOG.md && git commit -m "docs: prepare release 1.6.0" && git push`
4. Trigger workflow: `gh workflow run release.yml -f version=1.6.0`

## Files

| File | Purpose |
| ---- | ------- |
| `scripts/release.sh` | Local release automation (run this) |
| `.github/workflows/release.yml` | GitHub Actions workflow |
| `.github/workflows/scripts/validate-changelog.sh` | Verifies CHANGELOG entry exists |
| `.github/workflows/scripts/extract-release-notes.sh` | Extracts version section from CHANGELOG |
| `.github/workflows/scripts/create-github-release.sh` | Creates GitHub Release via gh CLI |
