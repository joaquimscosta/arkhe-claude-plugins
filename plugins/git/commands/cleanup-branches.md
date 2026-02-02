---
description: Delete merged branches and flag stale unmerged branches for cleanup
argument-hint: [--base <branch>] [--threshold <months>] [--remote] [--dry-run]
---

# Cleanup Branches

Delete local (and optionally remote) branches that are merged into the base branch, and flag stale unmerged branches for manual review.

## Usage

```bash
/cleanup-branches [options]
```

## Options

- `--base <branch>` - Base branch for merge check (default: main)
- `--threshold <months>` - Inactivity threshold in months for stale detection (default: 3)
- `--remote` - Also delete merged remote branches from origin
- `--dry-run` - Preview what would be deleted without acting

## Examples

```bash
/cleanup-branches                                # Delete local merged, flag stale
/cleanup-branches --remote                       # Include remote branch deletion
/cleanup-branches --base develop --threshold 1   # Custom base and threshold
/cleanup-branches --dry-run                      # Preview only, no deletions
/cleanup-branches --remote --dry-run             # Preview including remote
```

## Implementation

Invoke the Skill tool with skill name "git:cleaning-up-branches" and arguments: `$ARGUMENTS`

The skill will delete merged branches (with user confirmation), flag stale unmerged branches, and produce a cleanup summary. It never deletes unmerged branches automatically.

For detailed documentation, see `git/skills/cleaning-up-branches/SKILL.md`.
