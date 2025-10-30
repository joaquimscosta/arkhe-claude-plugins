---
description: Generate comprehensive changelogs from git commit history with semantic versioning analysis and conventional commit support
argument-hint: [--since <ref>] [--until <ref>] [--version <ver>] [--format <style>] [--output <file>] [--append] [--no-group]
---

# Changelog

Generate professional changelogs from git commit history with automatic categorization and semantic versioning.

## Usage

```bash
/changelog [options]
```

## Options

- `--since <commit/tag>` - Generate since specific commit/tag (default: last tag)
- `--until <commit/tag>` - Generate until specific commit/tag (default: HEAD)
- `--output <file>` - Output file path (default: CHANGELOG.md)
- `--format <style>` - Output format: keepachangelog, conventional, github
- `--version <version>` - Version number (auto-detected if not provided)
- `--append` - Append to existing changelog
- `--no-group` - Don't group commits by type

## Examples

```bash
/changelog                           # Generate since last tag
/changelog --since v1.0.0 --version 1.1.0  # Specific version range
/changelog --format github           # GitHub-style format
```

## Implementation

Invoke the Skill tool with skill name "git:changelog" and arguments: `$ARGUMENTS`

The skill will handle git history analysis, commit categorization, semantic versioning detection, and multiple output formats.

For detailed documentation, see `git/skills/changelog/SKILL.md`.
