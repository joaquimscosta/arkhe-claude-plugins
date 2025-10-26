---
name: Git Commit Workflow
description: Context-aware Git commit assistant with smart pre-commit checks, submodule support, and conventional commit message generation. Use when user requests to commit changes, run /commit command, or needs help creating git commits.
---

# Git Commit Workflow

Execute intelligent git commit workflows with automatic repository detection, smart pre-commit checks, and conventional commit message generation.

## Usage

This skill is invoked when:
- User runs `/commit` command
- User requests to commit changes
- User asks to create a git commit

## How It Works

The skill executes the commit workflow script which handles:

1. **Repository Detection** - Automatically detects root repository and submodules
2. **Change Analysis** - Identifies modified files and determines scope
3. **Pre-commit Checks** - Runs appropriate checks based on file types:
   - Kotlin files (`.kt`) → `./gradlew detekt`
   - TypeScript files (`.ts`/`.tsx`) → `npx tsc --noEmit`
   - Python files (`.py`) → Configurable linting
   - Rust files (`.rs`) → `cargo check`
4. **Commit Message Generation** - Creates conventional commit messages with emojis
5. **Submodule Handling** - Prompts to update submodule references in root repository

## Supported Arguments

- No arguments: Interactive mode (auto-detect changes)
- `<scope>`: Direct commit to specific repository (root, submodule-name)
- `--no-verify`: Skip all pre-commit checks
- `--full-verify`: Run full builds (backend + frontend)
- `<scope> --no-verify`: Combine scope with flags

## Examples

```bash
# Interactive mode - auto-detect changes
arguments: (none)

# Direct commit to root repository
arguments: root

# Commit to specific submodule
arguments: arkhe-claude-plugins

# Skip pre-commit checks
arguments: --no-verify

# Full verification with root scope
arguments: root --full-verify
```

## Execute the Workflow

Execute the commit workflow by running the bash script with the provided arguments.

**IMPORTANT**: Use the Bash tool to execute the script directly:

```bash
git/skills/commit/scripts/commit.sh $ARGUMENTS
```

The script will:
- Parse arguments and determine scope/flags
- Detect repositories with changes
- Run appropriate pre-commit checks
- Guide user through commit creation
- Handle submodule reference updates

**Note**: The script uses absolute path resolution internally, so it works from any directory in the project.

## Script Location

The commit workflow script is located at:
- `git/skills/commit/scripts/commit.sh` (main workflow script)
- `git/skills/commit/scripts/common.sh` (shared utilities)

## Output

The skill produces:
- Interactive prompts for repository selection (if needed)
- Pre-commit check results
- Suggested commit message with approval prompt
- Commit confirmation with hash
- Next steps and submodule update prompts

## Important Notes

- Works from any directory in the project
- Uses absolute paths for all git operations
- Respects branch protection rules
- Never includes Claude Code footer in commits
- Handles both clean and mixed submodule scenarios
