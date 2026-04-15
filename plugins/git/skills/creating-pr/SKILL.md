---
name: creating-pr
description: "Creates GitHub Pull Requests with existing PR detection, branch pushing, and intelligent title/body generation. Use when user requests to create pull request, open PR, update PR, push for review, ready for review, send for review, get this reviewed, make a PR, share code, request review, create draft PR, submit for review, run /create-pr command, or mentions PR, pull request, merge request, code review, GitHub PR, or draft."
model: haiku
---

# No Claude Code Footer Policy

**Never add Claude Code attribution to pull requests.**

- No "Generated with Claude Code" in PR titles or descriptions
- No "Co-Authored-By: Claude" in PR content
- No Claude Code attribution, footer, or branding of any kind

PRs are public code review documents and must remain clean and professional.

---

# PR Creation Workflow

Execute the complete PR workflow: detect repository context, validate branch, push to remote, check for existing PRs, generate title/body from commits, and create or update the PR via `gh`.

## Arguments

Parse from user input:

- **No arguments**: Auto-detect repository, target main branch
- **`<scope>`**: Target specific repository (root, submodule-name)
- **`--draft`**: Create as draft PR
- **`--base <branch>`**: Target branch (default: main)
- **Combinations**: `<scope> --draft`, `root --base staging`, etc.

## Workflow Overview

1. **Detect repository** - Find monorepo root, resolve scope to repo path (root or submodule)
2. **Validate branch** - Reject if on main/master, reject if uncommitted changes, reject if no commits ahead of base
3. **Push branch** - Push to origin if not on remote, or update remote if local differs
4. **Check existing PR** - Query `gh pr view` for current branch; if PR exists, offer to update or view it
5. **Generate PR title** - Extract conventional commit type/scope from commits; fall back to keyword analysis (fix/feat/docs/refactor/test)
6. **Generate PR body** - Build Summary from commit messages, Test Plan checklist, and Changed Files list
7. **Create or update PR** - Run `gh pr create` (with `--draft` if requested) or `gh pr edit` for existing PRs

**Quick reference:**

```bash
# Standard PR
gh pr create --title "feat(auth): add OAuth2 login" --body "## Summary\n..." --base main

# Draft PR
gh pr create --title "fix(api): resolve timeout" --body "..." --draft --base main

# Update existing
gh pr edit --title "updated title" --body "updated body"
```

See [WORKFLOW.md](WORKFLOW.md) for detailed step-by-step instructions and bash implementation reference.

## PR Title Convention

Titles follow conventional commit format: `type(scope): description`

- Extract type/scope from the latest conventional commit if present
- Otherwise infer type from commit message keywords: "bug/fix" -> `fix`, "feat/feature/add" -> `feat`, "docs" -> `docs`, "refactor" -> `refactor`, "test" -> `test`
- Default to `feat` when no pattern matches

## Critical Constraints

- **Branch protection**: Reject PR creation from main/master branches
- **Clean working tree**: Require all changes committed before creating PR
- **Commits required**: Branch must have commits ahead of base branch
- **Submodule support**: Detect superproject vs submodule context and target correct remote
- **Existing PR detection**: Always check for existing PR before creating a new one; offer update option

## Common Issues

**"gh: not found"** - Install and authenticate GitHub CLI: `gh auth login`

**"Cannot create PR from protected branch"** - Create a feature branch first with `/create-branch`

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete error handling.

## Supporting Documentation

- **[WORKFLOW.md](WORKFLOW.md)** - Detailed step-by-step process with bash implementation reference
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world PR scenarios: features, bug fixes, drafts, submodule PRs, updates
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions for GitHub CLI errors, authentication, and branch conflicts
