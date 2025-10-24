# Git Plugin

> Git workflow automation for commit, pull request, and branching operations

## Overview

The Git plugin provides intelligent Git workflow automation with context-aware repository detection, smart pre-commit checks, and seamless submodule handling. All commands support automatic detection of repositories and submodules, making Git operations faster and more reliable.

## Components

### Commands (4)

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

**Script**: `.claude/scripts/commit.sh`

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

**Script**: `.claude/scripts/pr.sh`

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

**Script**: `.claude/scripts/branch.sh`

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

### Skills (1)

#### changelog (Auto-Invoke)

Automatically generates changelogs when editing changelog files or mentioning release-related keywords.

**Auto-Invoke Triggers**:
- Editing files: `CHANGELOG.md`, `CHANGELOG.txt`, `HISTORY.md`
- Keywords: "changelog", "release notes", "version", "semantic versioning"
- Git tagging operations
- Release preparation discussions

**Delivers**:
1. **Git History Analysis** - Commit categorization and semantic version detection
2. **Formatted Changelog** - Industry-standard formats (Keep a Changelog, Conventional, GitHub)
3. **Update Strategy** - Append/overwrite options with version management

**Documentation**: See `skills/changelog/` directory for WORKFLOW, EXAMPLES, and TROUBLESHOOTING guides.

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
```

### Namespaced Invocation

When command name conflicts exist with other plugins:

```bash
/git:commit
/git:create-pr
/git:create-branch add authentication
/git:changelog
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

## Scripts

The plugin includes 4 shell scripts in `scripts/` directory:

### 1. commit.sh
Handles the commit workflow:
- Repository detection
- Change analysis
- Pre-commit check execution
- Commit message generation
- Submodule reference updates

### 2. pr.sh
Handles PR creation and updates:
- Repository detection
- Branch pushing
- Existing PR detection
- PR title/body generation
- GitHub CLI integration

### 3. branch.sh
Handles branch creation:
- Commit type detection
- Feature numbering
- Branch creation
- Optional feature directory setup

### 4. common.sh
Shared utilities:
- Path resolution
- Repository detection
- Output formatting
- Error handling

All scripts are executable and use absolute paths for reliability.

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
- **Bash**: Version 4.0+ (for scripts)

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

### Script Permission Issues

If scripts aren't executable:
```bash
chmod +x .claude/scripts/*.sh
```

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

See individual plugin directories for licensing information.

## Version

1.0.0
