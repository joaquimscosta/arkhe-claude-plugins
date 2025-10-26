---
description: Create a new feature branch with optimized short naming
---

# Branch Creation Command

Creates a new feature branch with optimized short naming following the pattern: `{type}/{number}-{word1}-{word2}`

## Usage

- `/create-branch <feature_description>` - Create a new feature branch

## Examples

```bash
/create-branch add newsletter signup
# Creates: feat/003-newsletter-signup

/create-branch fix authentication bug
# Creates: fix/004-authentication-bug

/create-branch refactor content planner agent
# Creates: refactor/005-content-planner

/create-branch update design system colors
# Creates: feat/006-design-system

/create-branch remove deprecated api endpoints
# Creates: chore/007-deprecated-api
```

## Commit Type Auto-Detection

The command automatically detects the commit type from your description:

- **feat**: add, create, implement, new, update, improve, enhance, optimize
- **fix**: fix, bug, resolve, correct, repair
- **refactor**: refactor, rename, reorganize, restructure, rewrite
- **chore**: remove, delete, clean, cleanup
- **docs**: docs, document, documentation

If no keyword is detected, defaults to `feat`.

## Branch Name Format

- **Pattern**: `{type}/{number}-{word1}-{word2}`
- **Number**: Auto-incremented based on existing feature branches or configurable directory
- **Words**: First 2 meaningful words after removing commit type keywords

## What It Does

1. Auto-detects commit type from feature description
2. Removes commit type keywords from name
3. Extracts 2 descriptive words
4. Finds next feature number (configurable via FEATURE_DIR)
5. Creates branch with format: `{type}/{number}-{word1}-{word2}`
6. Optionally creates feature directory (if FEATURE_DIR is set)

## Configuration (Optional)

Set via environment variables or project config:

```bash
export FEATURE_DIR=".claude/specs"    # Where to create feature directories (optional)
export BRANCH_PREFIX=""                # Additional prefix for branch names (optional)
```

If `FEATURE_DIR` is not set, only the branch is created (no directory).

## Important Notes

- Branch names are **shorter and more readable**
- Compatible with `/commit` and `/pr` commands
- Feature numbering is configurable via FEATURE_DIR
- Follows conventional commits standard

## Implementation

Use the **Git Branch Workflow** skill to execute the branch creation workflow with arguments: `$ARGUMENTS`

The skill handles:
- Automatic commit type detection from description keywords
- Short, readable branch name generation (2-3 words)
- Auto-incrementing feature numbers
- Optional feature directory creation (if FEATURE_DIR configured)
- Conventional commits standard compatibility

**Skill location**: `git/skills/branch/`
**Script execution**: The skill executes `./scripts/branch.sh` with the provided arguments
