# git — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

Git workflow automation (commit, PR, branching, changelog, release)

## Skills

- **cleaning-up-branches** — Deletes merged git branches (local and remote) and flags stale unmerged branches for manual review. Use when user mentions "cleanup branches", "delete merged branches", "prune old branches", "remove…
- **creating-branch** — Creates feature branches with optimized short naming, auto-incrementing, and commit type detection (feat/fix/refactor). Supports manual descriptions and auto-generation from uncommitted git changes.…
- **creating-commit** — Creates context-aware git commits with smart pre-commit checks, submodule support, and conventional commit message generation. Use when user requests to commit changes, stage and commit, check in cod…
- **creating-pr** — Creates GitHub Pull Requests with existing PR detection, branch pushing, and intelligent title/body generation. Use when user requests to create pull request, open PR, update PR, push for review, rea…
- **creating-worktree** — Creates isolated git worktrees in .worktrees/ with intelligent branch naming, auto-incrementing, and commit type detection (feat/fix/refactor). Supports manual descriptions and auto-generation from u…
- **dependabot-review** — Reviews open Dependabot PRs, classifies by risk (patch/minor/major, security, lockfile-only), and merges safe ones or advises on what to do. Use when user mentions "dependabot", "dependabot PRs", "de…
- **generating-changelog** — Analyzes git commit history and generates professional changelogs with semantic versioning, conventional commit support, and multiple output formats (Keep a Changelog, Conventional, GitHub). Use when…
- **listing-stale-branches** — Lists local and remote git branches that are candidates for cleanup — merged but not deleted, and inactive branches with no commits in a configurable period (default 3 months). Use when user mentions…
- **releasing** — Automate semantic versioning releases with CHANGELOG validation, comparison link management, GitHub Actions workflow triggering, and monitoring. Scaffold release infrastructure for new projects. Use…
- **resolving-pr-issues** — Multi-agent review resolution with trust-but-verify methodology. Accepts a PR number/URL or a local code-review report file. Extracts review comments, verifies each with parallel agents using confide…

## Commands as Trigger Phrases

### When the user says "/git:changelog" (args: [--since <ref>] [--until <ref>] [--version <ver>] [--format <style>] [--output <file>] [--append] [--no-group])

Generate comprehensive changelogs from git commit history with semantic versioning analysis and conventional commit support

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

Invoke the Skill tool with skill name "git:generating-changelog" and arguments: `$ARGUMENTS`

The skill will handle git history analysis, commit categorization, semantic versioning detection, and multiple output formats.

For detailed documentation, see `git/skills/generating-changelog/SKILL.md`.

### When the user says "/git:cleanup-branches" (args: [--base <branch>] [--threshold <months>] [--remote] [--dry-run])

Delete merged branches and flag stale unmerged branches for cleanup

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

### When the user says "/git:commit" (args: [scope] [--no-verify | --full-verify])

Context-aware Git commit assistant with smart pre-commit checks

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

⚠️ **CRITICAL**: Do NOT add Claude Code footers, attribution, or "Generated with Claude Code" text to commit messages. The skill generates clean commit messages internally. See `git/skills/creating-commit/SKILL.md` for details.

Invoke the Skill tool with skill name "git:creating-commit" and arguments: `$ARGUMENTS`

The skill will handle repository detection, pre-commit checks, commit message generation, and submodule reference updates.

For detailed documentation, see `git/skills/creating-commit/SKILL.md`.

### When the user says "/git:create-branch" (args: [feature_description])

Create a new feature branch with optimized short naming, or auto-generate from uncommitted changes

# Branch Creation Command

Creates feature branches with intelligent naming and auto-incrementing.

## Usage

```bash
# Create from description
/create-branch <feature_description>

# Auto-generate from uncommitted changes
/create-branch
```

## Examples

```bash
/create-branch add newsletter signup
# Creates: feat/003-newsletter-signup

/create-branch fix authentication bug
# Creates: fix/004-authentication-bug

/create-branch
# Auto-detected from changes: feat/005-authentication-system
```

## Implementation

Invoke the Skill tool with skill name "git:creating-branch" and arguments: `$ARGUMENTS`

The skill will handle commit type detection, branch naming, auto-increment numbering, and can auto-generate from uncommitted changes when no arguments are provided.

For detailed documentation, see `git/skills/creating-branch/SKILL.md`.

### When the user says "/git:create-pr" (args: [scope] [--draft] [--base <branch>])

Context-aware GitHub Pull Request creation and update assistant

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

### When the user says "/git:release" (args: <version> | --setup [--skip-monitor])

Automate semantic versioning releases or scaffold release infrastructure

# Release Command

Automate the full release process: validate CHANGELOG, update comparison links, commit, trigger GitHub Actions workflow, and monitor completion. Or scaffold release infrastructure for new projects.

## Usage

```bash
/release <version>                 # Execute release (e.g., /release 1.6.0)
/release --setup                   # Scaffold release infrastructure
/release <version> --skip-monitor  # Trigger without monitoring
```

## Examples

```bash
/release 1.6.0                    # Release version 1.6.0
/release v2.0.0                   # Works with 'v' prefix too
/release --setup                  # Create release.sh, workflow, and helper scripts
```

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- CHANGELOG.md entry for the version (use `/changelog` first)
- `.github/workflows/release.yml` exists (use `--setup` to create)

## Implementation

Invoke the Skill tool with skill name "git:releasing" and arguments: $ARGUMENTS

The skill handles version validation, CHANGELOG checks, comparison link management, commit/push, workflow triggering, and monitoring.

### When the user says "/git:resolve-review" (args: [PR-number | URL | file-path])

Analyze, verify, and resolve review suggestions from a GitHub PR or local code-review report

# PR Issue Resolver

Multi-agent review resolution with trust-but-verify methodology and confidence-based filtering.

## Usage

```bash
/resolve-review 123                              # Resolve PR review comments by number
/resolve-review https://github.com/org/repo/42   # Resolve PR review comments by URL
/resolve-review reviews/code/2026-03-18_review.md # Resolve findings from a local review file
```

## What It Does

1. Extracts review comments (PR) or findings (file)
2. Verifies each with parallel agents using confidence scoring (0-100)
3. Filters false positives (below 80)
4. Presents a triage report for your approval
5. Applies approved fixes and replies to comments

## Implementation

Invoke the Skill tool with skill name "git:resolving-pr-issues" and arguments: `$ARGUMENTS`

For detailed documentation, see `git/skills/resolving-pr-issues/SKILL.md`.

### When the user says "/git:stale-branches" (args: [--threshold <months>] [--base <branch>] [--remote])

List stale git branches that are candidates for cleanup (merged or inactive)

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

### When the user says "/git:worktree" (args: [description])

Create a git worktree in the .worktrees/ directory for isolated parallel development

# Worktree Command

Creates isolated git worktrees with intelligent branch naming and auto-incrementing.

## Usage

```bash
# Create from description
/worktree <description>

# Auto-generate from uncommitted changes
/worktree
```

## Examples

```bash
/worktree add user authentication
# Worktree: .worktrees/user-authentication
# Branch:   feat/003-user-authentication

/worktree fix login bug
# Worktree: .worktrees/login-bug
# Branch:   fix/004-login-bug

/worktree
# Auto-detected from changes: .worktrees/authentication-system
# Branch: feat/005-authentication-system
```

## Implementation

Invoke the Skill tool with skill name "git:creating-worktree" and arguments: $ARGUMENTS

The skill will handle commit type detection, branch naming, auto-increment numbering, base branch selection, and gitignore safety checks.

For detailed documentation, see `git/skills/creating-worktree/SKILL.md`.
