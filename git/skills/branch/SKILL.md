---
name: Git Branch Workflow
description: Feature branch creation with optimized short naming, auto-incrementing, and commit type detection. Use when user requests to create new branches or runs /create-branch command.
---

# Git Branch Workflow

Execute feature branch creation with intelligent naming, automatic type detection, and sequential numbering.

## Usage

This skill is invoked when:
- User runs `/create-branch` or `/git:create-branch` command
- User requests to create a new feature branch
- User asks to start a new branch for a task

## Supported Arguments

The command takes a description and automatically detects the commit type:

**Format**: `/create-branch <description>`

**Examples**:
```bash
/create-branch add user authentication
→ Creates: feat/001-user-authentication

/create-branch fix login bug
→ Creates: fix/002-login-bug

/create-branch refactor auth service
→ Creates: refactor/003-auth-service

/create-branch remove deprecated code
→ Creates: chore/004-remove-deprecated

/create-branch document api endpoints
→ Creates: docs/005-document-api
```

## Commit Type Detection

The workflow automatically detects commit types from keywords in the description:

| Type | Keywords |
|------|----------|
| **feat** | add, create, implement, new, update, improve |
| **fix** | fix, bug, resolve, correct, repair |
| **refactor** | refactor, rename, reorganize |
| **chore** | remove, delete, clean, cleanup |
| **docs** | docs, document, documentation |

If no keyword is detected, defaults to `feat`.

## Branch Naming Format

**Pattern**: `{type}/{number}-{keyword1}-{keyword2}`

**Components**:
- **type**: Auto-detected commit type (feat, fix, refactor, chore, docs)
- **number**: Auto-incremented 3-digit number (001, 002, 003...)
- **keywords**: First 2-3 meaningful words from description (lowercase, hyphenated)

**Examples**:
- Input: "add user authentication system"
- Output: `feat/001-user-authentication`

- Input: "fix null pointer in login"
- Output: `fix/002-null-pointer`

## Execute the Workflow

Execute the branch creation workflow by running the bash script with the provided arguments.

**IMPORTANT**: Use the Bash tool to execute the script directly:

```bash
git/skills/branch/scripts/branch.sh $ARGUMENTS
```

The script will:
- Parse description and extract keywords
- Detect commit type from keywords
- Find next sequential branch number
- Generate short, readable branch name
- Create and checkout the new branch
- Optionally create feature directory (if configured)

## Script Location

The branch creation script is located at:
- `git/skills/branch/scripts/branch.sh` (main workflow)
- `git/skills/branch/scripts/common.sh` (shared utilities)

## Configuration

Optional environment variables for customization:

```bash
# Feature directory location (optional)
export FEATURE_DIR=".claude/specs"

# Additional branch prefix (optional)
export BRANCH_PREFIX=""
```

If `FEATURE_DIR` is set, the workflow creates a directory at `$FEATURE_DIR/{branch-name}/` for specifications or notes.

## Output

The skill produces:
- Detected commit type (feat, fix, refactor, etc.)
- Extracted keywords from description
- Next sequential number
- Generated branch name
- Branch creation confirmation
- Feature directory creation (if configured)
- Success message with branch name

## Important Notes

1. **Sequential Numbering**: Automatically finds next available number by scanning existing branches

2. **Keyword Extraction**: Filters out common words (the, a, an, for, to, in, on, at, etc.)

3. **Short Names**: Uses first 2-3 meaningful words only (avoids long branch names)

4. **Lowercase Convention**: All branch names are lowercase with hyphens

5. **Conventional Commits**: Aligns with conventional commit types for consistency

6. **No Duplicates**: Increments number if similar branch name exists

7. **Works Anywhere**: Executes from any directory in the project
