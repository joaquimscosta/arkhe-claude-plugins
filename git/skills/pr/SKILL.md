---
name: creating-pr
description: Creates GitHub Pull Requests with existing PR detection, branch pushing, and intelligent title/body generation. Use when user requests to create/update pull requests or runs /create-pr command.
---

# Git PR Workflow

Execute GitHub Pull Request workflows with automatic repository detection, branch management, and intelligent PR content generation.

## Usage

This skill is invoked when:
- User runs `/create-pr` or `/git:create-pr` command
- User requests to create a pull request
- User asks to open a PR or push changes for review

## Supported Arguments

- **No arguments**: Auto-detect repository and create PR to main branch
- **`<scope>`**: Direct PR for specific repository (root, submodule-name)
- **`--draft`**: Create as draft PR
- **`--base <branch>`**: Target branch (default: main)
- **Combinations**: `<scope> --draft`, `root --base staging`, etc.

## Examples

```bash
# Interactive mode - auto-detect repository
arguments: (none)

# Create PR for root repository
arguments: root

# Create PR for specific submodule
arguments: arkhe-claude-plugins

# Create draft PR
arguments: --draft

# PR to staging branch
arguments: --base staging

# Combine options
arguments: root --draft --base develop
```

## Execute the Workflow

Execute the PR workflow by running the bash script with the provided arguments.

**IMPORTANT**: Use the Bash tool to execute the script directly:

```bash
git/skills/pr/scripts/pr.sh $ARGUMENTS
```

The script will:
- Detect repository from current directory
- Verify current branch is not protected (not main/master)
- Push branch to remote if not already pushed
- Check for existing PR on current branch
  - If found: Offer to update, view, or cancel
  - If not found: Create new PR
- Generate PR title from recent commits (conventional commit format)
- Generate PR body with summary and test plan
- Create PR using GitHub CLI (`gh pr create`)
- Return PR URL for viewing

**Requirements**: GitHub CLI (`gh`) must be installed and authenticated

## Script Location

The PR workflow script is located at:
- `git/skills/pr/scripts/pr.sh` (main workflow)
- `git/skills/pr/scripts/common.sh` (shared utilities)

## Output

The skill produces:
- Repository detection confirmation
- Branch status (local/remote sync)
- Existing PR detection results (if any)
- Generated PR title (from commits)
- Generated PR body (summary + test plan)
- PR creation/update confirmation
- PR URL for browser viewing
- Next steps guidance

## Important Notes

1. **GitHub CLI Required**: Must have `gh` installed and authenticated
   ```bash
   gh auth login
   ```

2. **Branch Protection**: Cannot create PR from main/master branch

3. **Existing PRs**: Automatically detects and offers to update existing PRs

4. **Commit-Based Title**: PR title generated from commit messages using conventional commit format

5. **Works Anywhere**: Executes from any directory, resolves paths absolutely

6. **Submodule Support**: Can create PRs for both root repository and submodules

## Supporting Documentation

For detailed information, see:

- **[WORKFLOW.md](WORKFLOW.md)** - Step-by-step PR creation process including repository detection, branch management, and GitHub CLI integration
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world PR scenarios covering features, bug fixes, drafts, and submodule PRs
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions for GitHub CLI errors, authentication, and branch conflicts
