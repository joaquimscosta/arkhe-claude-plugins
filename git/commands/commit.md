---
description: Context-aware Git commit assistant with smart pre-commit checks
argument-hint: [scope] [--no-verify | --full-verify]
---

# Commit Command

Context-aware Git commit assistant that automatically detects root repository and submodules, runs smart pre-commit checks, and generates conventional commit messages.

## Usage

```bash
/commit                              # Interactive mode (auto-detect)
/commit <scope>                      # Direct commit to specific repo
/commit --no-verify                  # Skip pre-commit checks
/commit --full-verify                # Run full build verification
/commit <scope> --no-verify          # Combine scope + flag
```

## Examples

```bash
/commit                              # Auto-detect and select repo
/commit root                         # Commit to root repository
/commit mobile                       # Commit to mobile submodule
```

## Implementation

⚠️ **CRITICAL**: Do NOT add Claude Code footers, attribution, or "Generated with Claude Code" text to commit messages. The skill generates clean commit messages internally. See `git/skills/commit/SKILL.md` for details.

Invoke the Skill tool with skill name "git:commit" and arguments: `$ARGUMENTS`

The skill will handle repository detection, pre-commit checks, commit message generation, and submodule reference updates.

For detailed documentation, see `git/skills/commit/SKILL.md`.
