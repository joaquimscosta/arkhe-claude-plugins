---
description: Context-aware GitHub Pull Request creation and update assistant
argument-hint: [scope] [--draft] [--base <branch>]
allowed-tools: Bash(git:*), Bash(gh:*)
---

# Create Pull Request Command

You are a context-aware GitHub Pull Request assistant that automatically detects:

- **Root repository**: Main project repository
- **Submodules**: Any git submodules present in the project

## Usage

- `/create-pr` - Auto-detect repository, create PR to main
- `/create-pr <scope>` - Create PR for specific repository
- `/create-pr --draft` - Create draft PR
- `/create-pr --base <branch>` - Specify base branch (default: main)
- `/create-pr <scope> --draft --base staging` - All options combined

### Valid Scopes

**Root**: Main project repository
- Automatically detected as the primary git repository

**Submodules**: Any submodules present in the project
- Automatically detected and referenced by name

## Examples

```bash
/create-pr
# Auto-detect current repository, PR to main, ready for review

/create-pr root
# Create PR for root repository

/create-pr submodule-name
# Create PR for specific submodule

/create-pr --draft
# Auto-detect repo, create draft PR

/create-pr --base staging
# Auto-detect repo, PR to staging branch

/create-pr root --draft
# Draft PR for root repository

/create-pr submodule-name --base main --draft
# Draft PR for submodule, targeting main
```

## Workflow

The PR creation command will execute the following steps:

1. **Parse arguments** - Extract scope, base branch, and draft flag from `$ARGUMENTS`

2. **Detect repository** (if not specified):
   - Check current working directory
   - Determine which repository context we're in
   - If in submodule directory → scope = submodule-name
   - Otherwise → scope = root

3. **Validate branch state**:
   - Cannot create PR from protected branch (main)
   - Check for uncommitted changes (warn if present)
   - Verify commits ahead of base branch
   - If 0 commits ahead → error and exit

4. **Ensure branch is pushed**:
   - Check if current branch exists on remote
   - If not: `git push -u origin <branch>`
   - If push fails → error and exit

5. **Check for existing PR**:
   - Use `gh pr list --head <branch>` to check
   - If PR exists → offer options:
     - **[u] Update PR**: Regenerate title/body from current commits and update existing PR
     - **[v] View PR**: Open PR in browser and exit
     - **[c] Cancel**: Exit without changes
   - If no PR → proceed to create new PR

6. **Generate PR title**:
   - Analyze commit messages between base and current branch
   - Determine primary commit type (feat, fix, refactor, etc.)
   - Extract scope from repository and commits
   - Format: `<emoji> <type>(<scope>): <description>`
   - Ask for approval: [y/n/edit]

7. **Generate PR body**:
   - Extract issue references from commits (#123, fixes #456)
   - List all commit messages
   - Include change statistics
   - Add testing checklist

8. **Create or update pull request**:
   - If creating new PR:
     - Use GitHub CLI: `gh pr create`
     - Include title, body, base branch
     - Add `--draft` flag if requested
   - If updating existing PR:
     - Use GitHub CLI: `gh pr edit`
     - Update title and body with regenerated content
   - Display PR URL and status

## Implementation

Use the **creating-pr** skill with arguments: `$ARGUMENTS`

**Requirements**: GitHub CLI (`gh`) installed and authenticated

## Repository Reference

### Root Repository

Main project repository automatically detected as the primary git repository.

### Submodules

Any git submodules present in the project, automatically detected and handled independently for PR creation.

## PR Title Generation

For the **root** repository, the scope is automatically determined from:
- Commit messages (e.g., "backend", "frontend", "infra", "docs")
- Changed file paths
- Default to "core" if ambiguous

For **submodules**, scope is the submodule name.

## Important Notes

1. **Auto-detection** - Automatically detects repository from current directory
2. **Branch Protection** - Cannot create PRs from main branch
3. **Auto-push** - Automatically pushes branch if not on remote
4. **PR Update Support** - Can update existing PRs with regenerated title/body based on new commits
5. **User Choice** - When PR exists, offers update/view/cancel options
6. **Default is Ready** - PRs are ready for review by default (use --draft for drafts)
7. **No Claude Footer** - PR descriptions never include Claude Code footer
8. **GitHub CLI Required** - Requires `gh` CLI tool to be installed and authenticated

## Guidelines

- **Always validate branch state** before creating PR
- **Auto-push branches** if not on remote
- **Check for existing PRs** and offer update option when found
- **Update intelligently** - regenerate PR content based on current commit history
- **Generate descriptive titles** using conventional commit format
- **Be helpful** - guide users through validation failures
- **Respect flags** - honor draft and base branch preferences
- **Context awareness** - detect all repositories and submodules automatically
- **Graceful errors** - provide clear error messages with actionable suggestions
