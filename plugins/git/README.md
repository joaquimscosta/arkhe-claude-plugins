# Git Plugin

> Git workflow automation for commit, pull request, and branching operations

## Overview

The Git plugin provides intelligent Git workflow automation with context-aware repository detection, smart pre-commit checks, and seamless submodule handling. All commands support automatic detection of repositories and submodules, making Git operations faster and more reliable.

## Components

### Commands (7)

#### 1. /commit
Context-aware Git commit assistant with smart pre-commit checks and submodule support.

**Features**:
- Auto-detect changes across root repository and submodules
- Interactive repository selection when multiple have changes
- Smart pre-commit checks based on file types detected
- Conventional commit message generation with emojis
- Seamless submodule reference updates
- Branch protection enforcement

**Pre-commit Checks** (Auto-detected):
- **Kotlin files** (`.kt`) → `./gradlew detekt`
- **TypeScript files** (`.ts`/`.tsx`) → `npx tsc --noEmit`
- **Python files** (`.py`) → Configurable linting
- **Rust files** (`.rs`) → `cargo check` (if Cargo.toml present)

**Usage**:
```bash
/commit                         # Interactive mode
/commit root                    # Direct commit to root
/commit submodule-name          # Direct commit to submodule
/commit --no-verify             # Skip all checks
/commit --full-verify           # Run full builds
/commit root --no-verify        # Combine scope + flag
```

**Flags**:
- `--no-verify`: Skip all pre-commit checks
- `--full-verify`: Run full builds (backend + frontend)

**Skill**: `git/skills/creating-commit/` (creating-commit)

---

#### 2. /create-pr
GitHub Pull Request creation and update assistant with existing PR detection.

**Features**:
- Auto-detect repository from current directory
- Automatic branch pushing if not on remote
- Existing PR detection with update capability
- Intelligent PR title/body generation from commits
- Draft PR support
- Custom base branch selection
- Conventional commit format for titles

**Usage**:
```bash
/create-pr                             # Auto-detect, PR to main
/create-pr root                        # PR for root repository
/create-pr submodule-name              # PR for submodule
/create-pr --draft                     # Create draft PR
/create-pr --base staging              # PR to staging branch
/create-pr root --draft                # Combine options
```

**Flags**:
- `--draft`: Create as draft PR
- `--base <branch>`: Target branch (default: main)

**Requirements**: GitHub CLI (`gh`) installed and authenticated

**Skill**: `git/skills/creating-pr/` (creating-pr)

---

#### 3. /create-branch
Feature branch creation with optimized naming and auto-incrementing.

**Features**:
- Auto-detect commit type from description
- Generate short, readable branch names
- Auto-increment feature numbers
- Optional feature directory creation
- Conventional commits standard
- Compatible with `/commit` and `/create-pr`

**Commit Type Detection**:
- `feat`: add, create, implement, new, update, improve
- `fix`: fix, bug, resolve, correct, repair
- `refactor`: refactor, rename, reorganize
- `chore`: remove, delete, clean, cleanup
- `docs`: docs, document, documentation

**Branch Format**: `{type}/{number}-{word1}-{word2}`

**Usage**:
```bash
/create-branch add user authentication          # Creates: feat/001-user-authentication
/create-branch fix login bug                    # Creates: fix/002-login-bug
/create-branch refactor auth service            # Creates: refactor/003-auth-service
```

**Configuration** (Optional):
```bash
export FEATURE_DIR=".claude/specs"   # Where to create feature dirs (optional)
export BRANCH_PREFIX=""               # Additional prefix (optional)
```

**Skill**: `git/skills/creating-branch/` (creating-branch)

---

#### 4. /changelog
Generate comprehensive changelogs from git commit history with semantic versioning analysis and conventional commit support.

**Features**:
- Automatic commit categorization by type (feat, fix, docs, etc.)
- Semantic versioning detection (MAJOR, MINOR, PATCH)
- Multiple output formats (Keep a Changelog, Conventional, GitHub)
- Breaking changes detection
- Existing CHANGELOG.md append support
- Monorepo support (service-specific changelogs)

**Usage**:
```bash
/changelog                                # Since last tag
/changelog --since v1.0.0 --version 1.1.0 # Specific range
/changelog --append                        # Append to existing
/changelog --format github                # GitHub format
```

**Flags**:
- `--since <commit/tag>`: Start commit (default: last tag)
- `--until <commit/tag>`: End commit (default: HEAD)
- `--output <file>`: Output file (default: CHANGELOG.md)
- `--format <style>`: keepachangelog, conventional, github
- `--version <version>`: Version number for release
- `--append`: Append instead of overwrite
- `--no-group`: Flat list without type grouping

---

#### 5. /pr-issue-resolve
Analyze and systematically resolve GitHub PR review suggestions.

**Features**:
- Fetch complete PR context (details, diff, comments)
- Categorize comments (Bugs, Code Changes, Style/Nitpicks, Questions, Approvals)
- Create resolution plan with prioritization
- Apply changes with incremental commits
- Run tests and verification
- Reply to comments and re-request reviews

**Usage**:
```bash
/pr-issue-resolve 123                          # Resolve PR #123
/pr-issue-resolve https://github.com/org/repo/pull/123  # With full URL
```

**Process**:
1. Fetch PR context with `gh` CLI
2. Analyze and categorize all review comments
3. Plan resolutions (Blockers → Features → Style → Questions)
4. Checkout branch, apply fixes in small commits
5. Test and verify changes
6. Update PR and request re-review

**Requirements**: GitHub CLI (`gh`) installed and authenticated

---

#### 6. /stale-branches
List stale git branches that are candidates for cleanup (merged or inactive).

**Features**:
- Detect branches merged into base but not deleted
- Find inactive unmerged branches with configurable threshold
- Show last commit date for merged branches
- Show ahead/behind divergence counts for unmerged branches
- Optional remote branch analysis with `git fetch --prune`
- Cross-platform date calculation (macOS and Linux)
- Read-only — never deletes branches, only suggests commands

**Usage**:
```bash
/stale-branches                          # Default: 3 months, main, local only
/stale-branches --threshold 1            # Stricter: 1 month inactivity
/stale-branches --remote                 # Include remote branches
/stale-branches --base develop           # Use develop as base branch
/stale-branches --threshold 1 --remote   # Combine flags
```

**Flags**:
- `--threshold <months>`: Inactivity threshold in months (default: 3)
- `--base <branch>`: Base branch for merge check (default: main)
- `--remote`: Include remote branch analysis

**Skill**: `git/skills/listing-stale-branches/` (listing-stale-branches)

---

#### 7. /cleanup-branches
Delete merged branches and flag stale unmerged branches for cleanup.

**Features**:
- Delete local branches merged into base with explicit confirmation
- Optionally delete remote merged branches from origin
- Flag stale unmerged branches for manual review (never auto-deletes)
- Dry-run mode to preview actions without deleting
- Cross-platform date handling (macOS and Linux)
- Safety: always asks before each destructive step

**Usage**:
```bash
/cleanup-branches                                # Delete local merged, flag stale
/cleanup-branches --remote                       # Include remote branch deletion
/cleanup-branches --base develop --threshold 1   # Custom base and threshold
/cleanup-branches --dry-run                      # Preview only, no deletions
/cleanup-branches --remote --dry-run             # Preview including remote
```

**Flags**:
- `--base <branch>`: Base branch for merge check (default: main)
- `--threshold <months>`: Inactivity threshold for stale detection (default: 3)
- `--remote`: Also delete merged remote branches from origin
- `--dry-run`: Preview what would be deleted without acting

**Skill**: `git/skills/cleaning-up-branches/` (cleaning-up-branches)

---

### Skills (6)

All commands are implemented as **Skills** - slash commands delegate to skills that contain inline Bash workflows executed by Claude.

#### 1. creating-commit

Executes the commit workflow with repository detection, pre-commit checks, and conventional commit generation.

**Location**: `skills/creating-commit/`
**Implementation**: Inline Bash workflow in SKILL.md
**Invoked by**: `/commit` command

#### 2. creating-pr

Handles PR creation and updates with GitHub CLI integration.

**Location**: `skills/creating-pr/`
**Implementation**: Inline Bash workflow in SKILL.md
**Invoked by**: `/create-pr` command

#### 3. creating-branch

Creates feature branches with smart naming and auto-incrementing.

**Location**: `skills/creating-branch/`
**Implementation**: Inline Bash workflow in SKILL.md
**Invoked by**: `/create-branch` command

#### 4. generating-changelog (Auto-Invoke)

Automatically generates changelogs when editing changelog files or mentioning release-related keywords.

**Location**: `skills/generating-changelog/`
**Invoked by**: `/changelog` command and auto-triggers

**Auto-Invoke Triggers**:
- Editing files: `CHANGELOG.md`, `CHANGELOG.txt`, `HISTORY.md`
- Keywords: "changelog", "release notes", "version", "semantic versioning"
- Git tagging operations
- Release preparation discussions

**Delivers**:
1. **Git History Analysis** - Commit categorization and semantic version detection
2. **Formatted Changelog** - Industry-standard formats (Keep a Changelog, Conventional, GitHub)
3. **Update Strategy** - Append/overwrite options with version management

**Documentation**: See `skills/generating-changelog/` directory for WORKFLOW, EXAMPLES, and TROUBLESHOOTING guides.

#### 5. listing-stale-branches (Auto-Invoke)

Identifies local and remote branches that are candidates for cleanup — merged-but-not-deleted and inactive branches.

**Location**: `skills/listing-stale-branches/`
**Invoked by**: `/stale-branches` command and auto-triggers

**Auto-Invoke Triggers**:
- Keywords: "stale branches", "old branches", "branch cleanup", "prune branches", "dead branches", "unused branches", "inactive branches", "branch hygiene"
- Actions: "list branches to delete", "find stale branches", "clean up branches"

**Delivers**:
1. **Merged Branch Report** — Branches merged into base with last commit dates
2. **Inactive Branch Report** — Unmerged branches past threshold with ahead/behind counts
3. **Remote Analysis** — Optional remote branch detection (with `--remote` flag)
4. **Cleanup Suggestions** — Deletion commands shown as suggestions, never executed

**Documentation**: See `skills/listing-stale-branches/` directory for WORKFLOW, EXAMPLES, and TROUBLESHOOTING guides.

#### 6. cleaning-up-branches

Deletes merged branches (local and remote) with explicit confirmation, and flags stale unmerged branches for manual review.

**Location**: `skills/cleaning-up-branches/`
**Invoked by**: `/cleanup-branches` command and auto-triggers

**Auto-Invoke Triggers**:
- Keywords: "cleanup branches", "delete merged branches", "prune old branches", "remove stale branches", "branch cleanup", "remove dead branches"

**Delivers**:
1. **Branch Status Summary** — Overview of local and remote branch counts
2. **Local Merged Cleanup** — Delete merged branches with user confirmation
3. **Remote Merged Cleanup** — Optional remote deletion with user confirmation
4. **Stale Branch Report** — Inactive unmerged branches flagged for manual review
5. **Cleanup Summary** — Audit trail of all actions taken

**Documentation**: See `skills/cleaning-up-branches/` directory for WORKFLOW, EXAMPLES, and TROUBLESHOOTING guides.

---

## Installation

### Add the Marketplace

```bash
/plugin marketplace add /path/to/arkhe-claude-plugins
```

### Install the Plugin

```bash
/plugin install git@arkhe-claude-plugins
```

After installation, restart Claude Code.

## Usage

### Direct Invocation

When no command conflicts exist:

```bash
/commit
/create-pr
/create-branch add authentication
/changelog
/stale-branches
/cleanup-branches
```

### Namespaced Invocation

When command name conflicts exist with other plugins:

```bash
/git:commit
/git:create-pr
/git:create-branch add authentication
/git:changelog
/git:stale-branches
/git:cleanup-branches
```

## Configuration

### Environment Variables

Set these in your shell profile or project `.envrc`:

```bash
# Feature directory for /create-branch command (optional)
export FEATURE_DIR=".claude/specs"

# Branch prefix (optional)
export BRANCH_PREFIX=""

# Branch protection (default: main)
export PROTECTED_BRANCH="main"
```

### Project Detection

The plugin automatically detects:
- **Root repository**: Primary git repository
- **Submodules**: Via `.gitmodules` file
- **File types**: For smart pre-commit checks
- **Project structure**: Backend, frontend, infrastructure

### Pre-commit Check Configuration

Pre-commit checks are automatically detected based on file changes:

| File Type | Check Command | Configuration Required |
|-----------|---------------|----------------------|
| `.kt` (Kotlin) | `./gradlew detekt` | `gradlew` in backend/ |
| `.ts`/`.tsx` (TypeScript) | `npx tsc --noEmit` | `tsconfig.json` in frontend/ |
| `.py` (Python) | Configurable | `.python-version` or venv |
| `.rs` (Rust) | `cargo check` | `Cargo.toml` present |

**Skip checks**: Use `--no-verify` flag
**Full verification**: Use `--full-verify` flag

## Architecture

The plugin uses a **Commands + Skills** pattern where:

1. **Commands** (`commands/*.md`) - User interface via slash commands
2. **Skills** (`skills/*/`) - Implementation with inline Bash workflows and documentation

### Skill Organization

Each skill contains workflow documentation and inline Bash:

**skills/creating-commit/**
- `SKILL.md` - Complete inline Bash workflow for commits
- `WORKFLOW.md` - Detailed step-by-step process
- `EXAMPLES.md` - Real-world usage examples
- `TROUBLESHOOTING.md` - Common issues and solutions

**skills/creating-pr/**
- `SKILL.md` - Complete inline Bash workflow for PRs
- `WORKFLOW.md`, `EXAMPLES.md`, `TROUBLESHOOTING.md`

**skills/creating-branch/**
- `SKILL.md` - Complete inline Bash workflow for branch creation
- `WORKFLOW.md`, `EXAMPLES.md`, `TROUBLESHOOTING.md`

**skills/generating-changelog/**
- `SKILL.md` - Complete inline Bash workflow for changelogs
- `WORKFLOW.md`, `EXAMPLES.md`, `TROUBLESHOOTING.md`

**skills/listing-stale-branches/**
- `SKILL.md` - Complete inline Bash workflow for stale branch detection
- `WORKFLOW.md`, `EXAMPLES.md`, `TROUBLESHOOTING.md`

**skills/cleaning-up-branches/**
- `SKILL.md` - Complete inline Bash workflow for branch cleanup
- `WORKFLOW.md`, `EXAMPLES.md`, `TROUBLESHOOTING.md`

### Key Features

- **Transparent**: All logic visible in SKILL.md files
- **Maintainable**: No hidden scripts to track
- **Multi-repo Support**: Full submodule and monorepo awareness
- **Progressive Disclosure**: Supporting docs loaded on-demand
- **Documented**: Each skill includes comprehensive documentation

## Examples

### Commit Workflow

```bash
# Interactive commit (detects changes)
/commit

# Multiple repositories with changes?
# → Shows selection menu with file counts

# Select repository
# → Runs appropriate pre-commit checks
# → Suggests commit message
# → Creates commit

# Submodule committed?
# → Prompts to update reference in root
```

### PR Workflow

```bash
# Create PR from current branch
/create-pr

# Auto-detects repository
# → Pushes branch if needed
# → Checks for existing PR
#   - Found? Offer update/view/cancel
#   - Not found? Create new PR
# → Generates title from commits
# → Creates PR
# → Returns PR URL
```

### Branch Creation Workflow

```bash
# Create feature branch
/create-branch add user authentication system

# Auto-detects commit type (feat)
# → Extracts keywords: "user authentication"
# → Finds next number: 005
# → Creates: feat/005-user-authentication
# → Optionally creates spec directory
```

## Submodule Handling

### Automatic Detection

The plugin automatically detects submodules via `.gitmodules`:

```bash
# If you have submodules:
/commit                 # Shows: root + all submodules with changes
/commit submodule-name  # Direct commit to submodule
/create-pr submodule-name      # Create PR for submodule
```

### Seamless Reference Updates

After committing to a submodule:

**Clean case** (only submodule modified in root):
```
📤 Commit submodule reference to root? [Y/n]:
```
Default: Yes → Auto-commits reference update

**Mixed case** (root has other changes):
```
⚠️  Root repository has other uncommitted changes.
📤 Commit submodule reference separately? [y/N]:
```
Default: No → Commit later with other changes

## Requirements

### Required

- **Git**: Version 2.0+ (for submodule support)
- **Bash**: Standard bash (for inline workflows)

### Optional (for specific features)

- **GitHub CLI (`gh`)**: For `/create-pr` command
  ```bash
  # Install gh
  brew install gh          # macOS
  # or
  sudo apt install gh      # Ubuntu/Debian

  # Authenticate
  gh auth login
  ```

- **Pre-commit Tools**: For smart checks
  - Kotlin: `gradle` or `gradlew`
  - TypeScript: `npm` and `tsconfig.json`
  - Python: `pylint`, `flake8`, `black` (configurable)
  - Rust: `cargo`

## Troubleshooting

### Command Not Found

If commands aren't recognized after installation:
1. Restart Claude Code
2. Verify plugin is enabled: `/plugin`
3. Check marketplace: `/plugin marketplace list`

### Command Conflicts

If another plugin provides the same command:
- Use namespaced invocation: `/git:command-name`

### GitHub CLI Issues

If `/create-pr` command fails:
```bash
# Check gh installation
gh --version

# Re-authenticate
gh auth login

# Test gh access
gh repo view
```

### Pre-commit Check Failures

If checks fail unexpectedly:
```bash
# Skip checks temporarily
/commit --no-verify

# Or run full verification
/commit --full-verify
```

### Submodule Issues

If submodule detection fails:
```bash
# Verify .gitmodules exists
cat .gitmodules

# Update submodules
git submodule update --init --recursive

# Commit with explicit scope
/commit submodule-name
```

### Skills Not Loading

If skills aren't executing workflows:

1. **Verify plugin installation**: Run `/plugin` to check if git plugin is installed
2. **Restart Claude Code**: Skills are loaded at startup
3. **Check skill files**: Verify SKILL.md files exist in plugin storage
4. **Review error messages**: Look for syntax errors in Bash workflows

## Best Practices

### Commit Messages

Use conventional commit format:
```
<emoji> <type>(<scope>): <description>

Examples:
✨ feat(auth): add JWT authentication
🐛 fix(api): handle null response
♻️ refactor(db): optimize query performance
```

### Branch Names

Keep branch names short and descriptive:
```
Good:
- feat/001-user-auth
- fix/002-login-bug
- refactor/003-api-cleanup

Avoid:
- feat/001-add-a-new-user-authentication-system-with-jwt
- fix-the-login-bug-that-was-reported-yesterday
```

### Pull Requests

- Use descriptive titles matching commit messages
- Include issue references (#123)
- Update PR descriptions when adding commits
- Use draft PRs for work-in-progress

### Submodules

- Commit submodule changes first
- Update root reference immediately after
- Keep submodule commits atomic
- Document submodule purpose

## Contributing

Issues and pull requests welcome at the arkhe-claude-plugins repository.

## License

MIT License

## Version

1.0.0
