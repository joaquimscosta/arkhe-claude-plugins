---
name: creating-branch
description: Creates feature branches with optimized short naming, auto-incrementing, and commit type detection (feat/fix/refactor). Supports manual descriptions and auto-generation from uncommitted git changes. Use when user requests to create branch, start new branch, make branch, checkout new branch, switch branch, new task, start working on, begin work on feature, begin feature, create feature branch, run /create-branch command, or mentions "branch", "feature", "new feature", "feat", "fix", or "checkout".
---

# Git Branch Workflow

Execute feature branch creation with intelligent naming, automatic type detection, and sequential numbering.

## Usage

This skill is invoked when:
- User runs `/create-branch` or `/git:create-branch` command
- User requests to create a new feature branch
- User asks to start a new branch for a task

## Two Operation Modes

### Mode 1: With Description (Manual)

The command takes a description and automatically detects the commit type.

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

### Mode 2: Auto-Generate from Changes (No Arguments)

When no arguments provided, analyze uncommitted changes to generate branch name automatically.

**Format**: `/create-branch` (no arguments)

**Process**:
1. Check for uncommitted changes (both staged and unstaged)
2. If no changes exist, display error and require description
3. If changes exist, analyze to generate description
4. Create branch with auto-generated name

**Examples**:
```bash
# After modifying authentication files
/create-branch
→ Auto-detected from changes: feat/006-authentication-system
→ (based on: login.py, auth_service.ts, user_model.py)

# After fixing payment bug
/create-branch
→ Auto-detected from changes: fix/007-payment-processing
→ (based on: payment.js, checkout.py)
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

## Auto-Generation Workflow (No Arguments Provided)

When no arguments are provided, follow this workflow to auto-generate branch name from changes:

### Step 1: Check for Uncommitted Changes

Run git commands to detect changes:
```bash
git diff --name-status
git diff --cached --name-status
git ls-files --others --exclude-standard
```

### Step 2: Handle No Changes Case

If all three commands return empty (no changes detected):
```
Display error message:
"Error: No uncommitted changes detected.

To create a branch, either:
1. Make some changes first, then run /create-branch
2. Provide a description: /create-branch <description>

Examples:
  /create-branch add user authentication
  /create-branch fix payment bug"
```

**IMPORTANT**: Stop execution and do not create a branch.

### Step 3: Analyze Changes (If Changes Exist)

Analyze the file paths from the git commands to determine:

**Goal**: Identify main purpose based on file names and paths

**Focus on**:
- File names and paths (e.g., `auth/login.py` suggests authentication)
- Change patterns (Added files = new feature, Modified = update/fix)
- Common themes across multiple files

**Determine**:
1. **Main purpose/goal**: What is being built or fixed? (2-3 words max)
2. **Commit type**: Based on patterns:
   - `feat`: New files added, new directories, substantial additions
   - `fix`: Modifications to existing files in critical paths (error handling, validation)
   - `refactor`: Renaming, reorganizing, restructuring files
   - `chore`: Deletions, cleanup, config changes
   - `docs`: Documentation files (.md, README, comments)
   - Default to `feat` if unclear

**Example analysis**:
```
Files changed:
  A  src/auth/login.py
  A  src/auth/service.ts
  M  src/models/user.py

Analysis:
- New auth directory with login functionality
- User model modifications (likely auth-related)
- Purpose: "authentication system"
- Type: feat (new files/directory)
- Generated description: "add authentication system"
```

### Step 4: Generate Description and Create Branch

Format the auto-generated description as:
```
<commit-type-keyword> <2-3-word-purpose>
```

Examples:
- "add authentication system"
- "fix payment processing"
- "refactor database queries"

Then pass this generated description to the standard workflow (Step 5 below).

### Step 5: Display Auto-Generation Summary

After branch creation succeeds, display:
```
Auto-detected from changes: <branch-name>
(based on: <file1>, <file2>, <file3>, ...)
```

Limit file list to 3-5 most relevant files.

## Execute the Workflow

Execute the branch creation workflow by running the bash script with the provided or generated description.

**IMPORTANT**: Use the Bash tool to execute the script directly:

```bash
# With manual description (Mode 1)
git/skills/branch/scripts/branch.sh $ARGUMENTS

# With auto-generated description (Mode 2)
git/skills/branch/scripts/branch.sh <generated-description>
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

**Spec Directory Creation**:
The workflow creates a spec directory at `$FEATURE_DIR/{branch-name}/` **only if spec-kit is installed** (checks for `.specify/` directory in repository root).

- **With spec-kit** (`.specify/` exists): Creates directory for specifications and notes
- **Without spec-kit**: No directory created (prevents unnecessary clutter)
- **Custom location**: Override with `FEATURE_DIR` environment variable

## Output

The skill produces:
- Detected commit type (feat, fix, refactor, etc.)
- Extracted keywords from description
- Next sequential number
- Generated branch name
- Branch creation confirmation
- Feature directory creation (only if `.specify/` exists)
- Success message with branch name

## Important Notes

1. **Sequential Numbering**: Automatically finds next available number by scanning existing branches

2. **Keyword Extraction**: Filters out common words (the, a, an, for, to, in, on, at, etc.)

3. **Short Names**: Uses first 2-3 meaningful words only (avoids long branch names)

4. **Lowercase Convention**: All branch names are lowercase with hyphens

5. **Conventional Commits**: Aligns with conventional commit types for consistency

6. **No Duplicates**: Increments number if similar branch name exists

7. **Works Anywhere**: Executes from any directory in the project

## Supporting Documentation

For detailed information, see:

- **[WORKFLOW.md](WORKFLOW.md)** - Step-by-step branch creation process with detailed explanations
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world examples covering all branch types and scenarios
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
