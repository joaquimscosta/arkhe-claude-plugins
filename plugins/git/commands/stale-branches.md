---
description: List stale git branches that are candidates for cleanup (merged or inactive)
argument-hint: [--threshold <months>] [--base <branch>] [--remote]
---

# Stale Branches

List local and remote git branches that are candidates for cleanup — merged but not deleted, and inactive branches with no recent commits.

## Usage

```bash
/stale-branches [options]
```

## Options

- `--threshold <months>` - Inactivity threshold in months (default: 3)
- `--base <branch>` - Base branch for merge check (default: main)
- `--remote` - Include remote branch analysis

## Examples

```bash
/stale-branches                          # Default: 3 months, main, local only
/stale-branches --threshold 1            # Stricter: 1 month inactivity
/stale-branches --remote                 # Include remote branches
/stale-branches --base develop           # Use develop as base branch
/stale-branches --threshold 1 --remote   # Combine flags
```

## Implementation

Invoke the Skill tool with skill name "git:listing-stale-branches" and arguments: `$ARGUMENTS`

The skill will detect merged branches, inactive unmerged branches, and optionally analyze remote branches. It is read-only and never deletes branches.

For detailed documentation, see `git/skills/listing-stale-branches/SKILL.md`.
