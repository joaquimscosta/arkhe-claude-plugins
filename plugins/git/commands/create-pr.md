---
description: Context-aware GitHub Pull Request creation and update assistant
argument-hint: [scope] [--draft] [--base <branch>]
---

# Create Pull Request Command

Context-aware GitHub Pull Request assistant that automatically detects root repository and submodules, handles existing PRs, and generates conventional PR titles and descriptions.

## Usage

```bash
/create-pr                           # Auto-detect repository
/create-pr <scope>                   # Create PR for specific repo
/create-pr --draft                   # Create draft PR
/create-pr --base <branch>           # Specify base branch
/create-pr <scope> --draft --base staging  # All options combined
```

## Examples

```bash
/create-pr                           # Auto-detect, PR to main
/create-pr root                      # PR for root repository
/create-pr mobile                    # PR for mobile submodule
/create-pr --draft                   # Create as draft
```

## Implementation

⚠️ **CRITICAL**: Do NOT add Claude Code footers, attribution, or "Generated with Claude Code" text to PR titles or descriptions. The skill generates clean PR content internally. See `git/skills/creating-pr/SKILL.md` for details.

Invoke the Skill tool with skill name "git:creating-pr" and arguments: `$ARGUMENTS`

The skill will handle repository detection, existing PR handling, branch pushing, and PR title/body generation.

**Requirements**: GitHub CLI (`gh`) installed and authenticated

For detailed documentation, see `git/skills/creating-pr/SKILL.md`.
