# Release Skill: Examples

## Example 1: Standard Release

Release version 1.6.0 after adding a CHANGELOG entry.

```bash
# 1. Generate CHANGELOG entry
/changelog --version 1.6.0

# 2. Execute release
/release 1.6.0
```

**What happens:**
1. Validates `1.6.0` is valid semver
2. Checks `## [1.6.0]` exists in CHANGELOG.md
3. Checks `v1.6.0` release doesn't exist on GitHub
4. Adds comparison link: `[1.6.0]: https://github.com/user/repo/compare/v1.5.0...v1.6.0`
5. Updates `[Unreleased]` link to `compare/v1.6.0...HEAD`
6. Asks to commit and push CHANGELOG.md changes
7. Triggers `release.yml` workflow
8. Monitors until completion
9. Reports: `Release v1.6.0 created successfully!`

## Example 2: First Release

Release the initial version of a new project.

```bash
# 1. Set up release infrastructure
/release --setup

# 2. Create CHANGELOG.md
/changelog --version 1.0.0

# 3. Commit scaffolded files and CHANGELOG
git add -A && git commit -m "chore: add release infrastructure"
git push origin main

# 4. Execute first release
/release 1.0.0
```

**Comparison link for first release:**
```markdown
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

## Example 3: Patch Release

Quick bug fix release.

```bash
# 1. Fix the bug and commit
/commit

# 2. Update CHANGELOG
/changelog --version 1.5.1

# 3. Release
/release 1.5.1
```

## Example 4: Release with v Prefix

The `v` prefix is automatically stripped.

```bash
/release v2.0.0
# Equivalent to: /release 2.0.0
```

## Example 5: Trigger Without Monitoring

Trigger the workflow and return immediately.

```bash
/release 1.6.0 --skip-monitor
```

**Output:**
```
Workflow triggered. Skipping monitoring.
View at: https://github.com/user/repo/actions
```

## Example 6: Setup Scaffolding

Scaffold the full release pipeline into a new project.

```bash
/release --setup
```

**Files created:**
```
scripts/
└── release.sh                              # Local release orchestrator

.github/
└── workflows/
    ├── release.yml                         # GitHub Actions workflow
    └── scripts/
        ├── validate-changelog.sh           # CHANGELOG validator
        ├── extract-release-notes.sh        # Release notes extractor
        └── create-github-release.sh        # GitHub release creator
```

## Example 7: Using release.sh Directly

After scaffolding, the release script can be run directly from the terminal.

```bash
# Interactive mode (prompts for confirmation)
./scripts/release.sh 1.6.0

# Non-interactive mode (for CI)
./scripts/release.sh 1.6.0 --yes

# Skip monitoring
./scripts/release.sh 1.6.0 --yes --skip-monitor
```

## Example 8: CHANGELOG Format Expected

The skill expects Keep a Changelog format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.6.0] - 2026-03-03

### Added
- New release automation skill in git plugin

### Changed
- Updated plugin description to include release

## [1.5.0] - 2026-02-15

### Added
- Previous feature

[Unreleased]: https://github.com/user/repo/compare/v1.6.0...HEAD
[1.6.0]: https://github.com/user/repo/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/user/repo/releases/tag/v1.5.0
```
