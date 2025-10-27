---
name: changelog
description: Generate comprehensive changelogs from git commit history with semantic versioning analysis and conventional commit support. Use this command to create release notes, changelog files, or update existing CHANGELOG.md files.
---

# Changelog

Generate professional changelogs from git commit history with automatic categorization and semantic versioning.

## Usage

```bash
/changelog [options]
```

## Options

- `--since <commit/tag>` - Generate changelog since specific commit or tag (default: last tag)
- `--until <commit/tag>` - Generate changelog until specific commit or tag (default: HEAD)
- `--output <file>` - Output file path (default: CHANGELOG.md)
- `--format <style>` - Output format: keepachangelog, conventional, github (default: keepachangelog)
- `--version <version>` - Version number for this release (auto-detected from commits if not provided)
- `--append` - Append to existing changelog instead of overwriting
- `--no-group` - Don't group commits by type (flat list)

## Examples

```bash
# Generate changelog since last tag
/changelog

# Generate changelog for specific version range
/changelog --since v1.0.0 --until HEAD --version 1.1.0

# Append to existing changelog
/changelog --append --output CHANGELOG.md

# Use GitHub-style format
/changelog --format github

# Generate for specific date range
/changelog --since "2025-01-01" --until "2025-10-22"
```

## Commit Message Conventions

This command recognizes [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features (MINOR version bump)
- `fix:` - Bug fixes (PATCH version bump)
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Test additions/changes
- `build:` - Build system changes
- `ci:` - CI/CD changes
- `chore:` - Other changes
- `BREAKING CHANGE:` - Breaking changes (MAJOR version bump)

## Output Formats

### Keep a Changelog (default)

```markdown
# Changelog

## [1.1.0] - 2025-10-22

### Added
- New feature A
- New feature B

### Fixed
- Bug fix A
- Bug fix B

### Changed
- Refactoring A
```

### Conventional

```markdown
# Changelog

## 1.1.0 (2025-10-22)

#### Features
* feat: add new feature A (abc123)
* feat: add new feature B (def456)

#### Bug Fixes
* fix: resolve bug A (ghi789)
```

### GitHub

```markdown
## What's Changed

**Features:**
- Add new feature A by @username in #123
- Add new feature B by @username in #124

**Bug Fixes:**
- Resolve bug A by @username in #125

**Full Changelog**: v1.0.0...v1.1.0
```

## Semantic Versioning

The command automatically suggests version bumps based on commit types:

- **MAJOR** (x.0.0): Contains `BREAKING CHANGE:` in commit message
- **MINOR** (0.x.0): Contains `feat:` commits
- **PATCH** (0.0.x): Contains `fix:` commits only

## Integration with Git

The command analyzes:
- Commit messages
- Commit authors
- Commit timestamps
- Git tags
- Pull request numbers (from GitHub-style commit messages)

## Implementation

Use the **generating-changelog** skill to execute the changelog workflow with arguments: `$ARGUMENTS`

The skill handles:
- Git history analysis from commit range
- Automatic commit categorization by type
- Semantic version bump detection (MAJOR/MINOR/PATCH)
- Multiple output format support (Keep a Changelog, Conventional, GitHub)
- CHANGELOG.md updates (append or overwrite)

**Skill location**: `git/skills/changelog/`
**Auto-invoke**: Automatically activates when editing CHANGELOG.md or mentioning "changelog", "release notes"

## See Also

- `/commit` - Smart commit message creation
- `/create-pr` - Create pull requests with changelog integration
- `/create-branch` - Create feature branches with proper naming
