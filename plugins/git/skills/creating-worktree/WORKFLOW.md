# Git Worktree Creation: Detailed Workflow

This document provides a detailed step-by-step breakdown of the worktree creation process.

## Overview

The worktree creation process follows 9 main steps:

1. **Determine Mode** - Check for description, specs, or auto-generate
1b. **Spec Selection** - (Mode 3 only) Present available specs for selection
2. **Parse Description** - Extract user's task description
3. **Detect Commit Type** - Identify branch type from keywords
4. **Extract Keywords** - Filter meaningful words from description
5. **Find Next Number** - Auto-increment sequential number
6. **Validate Worktree Directory** - Ensure no conflicts
7. **Ensure Git Ignore** - Safety check for `.worktrees/`
8. **Ask Base Branch** - User selects base branch
9. **Create Worktree** - Generate names and create worktree

---

## Step 1: Determine Operation Mode

Check arguments and environment to determine mode:

```bash
# Check for arguments
if [ -n "$DESCRIPTION" ]; then
    MODE="manual"
    # Proceed to Step 2 (parse description)
else
    # Check for sdlc-develop integration
    if [ -f ".arkhe.yaml" ]; then
        SPECS_DIR=$(grep 'specs_dir:' .arkhe.yaml | awk '{print $2}')
        SPECS_DIR=${SPECS_DIR:-arkhe/specs}

        # Find existing spec directories
        SPECS=$(find "$SPECS_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)

        if [ -n "$SPECS" ]; then
            MODE="spec-select"
            # Proceed to Step 1b (spec selection)
        else
            MODE="auto-generate"
            # Proceed to auto-generate from changes
        fi
    else
        MODE="auto-generate"
        # Proceed to auto-generate from changes
    fi
fi
```

---

## Step 1b: Spec Selection (Mode 3 Only)

Present available specs for selection:

Use `AskUserQuestion` with options:
- Each spec directory as an option (e.g., "01-user-auth", "02-dashboard")
- "None - auto-generate from changes" as final option

If user selects a spec:
- Extract spec name (e.g., "01-user-auth")
- Detect type from spec name or default to "feat"
- Use spec name as keywords: worktree dir = `.worktrees/01-user-auth`, branch = `feat/01-user-auth`

If user selects "None":
- Set MODE="auto-generate"
- Proceed to auto-generate from changes

---

## Step 2: Parse Description

Extract and normalize the user's task description.

**Input**: Raw description from user command
```bash
/worktree add user authentication system
```

**Process**:
1. Remove command prefix (`/worktree`)
2. Trim whitespace
3. Convert to lowercase
4. Store as working description

**Output**: `"add user authentication system"`

---

## Step 3: Detect Commit Type

Analyze description keywords to determine branch type.

**Detection Logic**:

| Commit Type | Keywords | Priority |
|-------------|----------|----------|
| **feat** | add, create, implement, new, update, improve | High |
| **fix** | fix, bug, resolve, correct, repair | High |
| **refactor** | refactor, rename, reorganize | Medium |
| **chore** | remove, delete, clean, cleanup | Medium |
| **docs** | docs, document, documentation | Medium |

**Algorithm**:
1. Split description into words
2. Check each word against keyword lists
3. Return first matching type
4. Default to `feat` if no match

**Examples**:
- "add user auth" -> `feat` (keyword: "add")
- "fix login bug" -> `fix` (keyword: "fix")
- "refactor auth service" -> `refactor` (keyword: "refactor")
- "remove old code" -> `chore` (keyword: "remove")
- "document api" -> `docs` (keyword: "document")

**Output**: Commit type string (e.g., `feat`)

---

## Step 4: Extract Keywords

Filter meaningful words from description for naming.

**Filtering Process**:

**Remove common words** (stopwords):
- Articles: the, a, an
- Prepositions: for, to, in, on, at, by, with, from
- Conjunctions: and, or, but
- Pronouns: this, that, these, those
- Commit type keywords: add, fix, create, etc.

**Extract meaningful words**:
1. Split description into words
2. Remove stopwords
3. Keep first 2-3 meaningful words
4. Convert to lowercase
5. Replace spaces with hyphens

**Examples**:

Input: "add user authentication system"
- Remove: "add" (commit type keyword)
- Keep: "user", "authentication", "system"
- Limit: "user", "authentication" (first 2 words)
- **Output**: `user-authentication`

Input: "fix null pointer exception in login service"
- Remove: "fix", "in" (stopwords)
- Keep: "null", "pointer", "exception", "login", "service"
- Limit: "null", "pointer" (first 2 words)
- **Output**: `null-pointer`

Input: "refactor the authentication service module"
- Remove: "refactor", "the" (stopwords)
- Keep: "authentication", "service", "module"
- Limit: "authentication", "service" (first 2 words)
- **Output**: `authentication-service`

---

## Step 5: Find Next Number

Determine the next sequential branch number.

**Process**:

1. **Scan existing branches** (shared number space with `/create-branch`):
   ```bash
   git branch --list
   ```

2. **Extract numbers** from branches matching pattern:
   ```
   feat/001-user-auth
   feat/002-dashboard
   fix/003-login-bug
   ```
   Extract: [001, 002, 003]

3. **Find maximum**:
   ```
   Max = 003
   ```

4. **Increment**:
   ```
   Next = 004
   ```

5. **Format as 3-digit**:
   ```
   "004"
   ```

**Edge Cases**:

- **No existing branches**: Start with `001`
- **Non-sequential numbers**: Find max and increment (e.g., 001, 005 -> next is 006)
- **Different types**: Numbers are global across all types

**Output**: 3-digit number string (e.g., `"004"`)

---

## Step 6: Validate Worktree Directory

Check that the target worktree directory doesn't conflict.

**Process**:

1. **Check directory exists**:
   ```bash
   ls .worktrees/$KEYWORDS 2>/dev/null
   ```

2. **If exists**: Report conflict and stop:
   ```
   Worktree directory .worktrees/user-authentication already exists.
   - Remove it: git worktree remove .worktrees/user-authentication
   - Or use a different description
   ```

3. **Check branch name**:
   ```bash
   git branch --list "$TYPE/$NEXT_NUM-$KEYWORDS"
   ```

4. **If branch exists**: Increment number and retry. If still conflicts, ask user for guidance.

---

## Step 7: Ensure Git Ignore

Verify `.worktrees/` is excluded from version control.

**Process**:

1. **Check if ignored**:
   ```bash
   git check-ignore -q .worktrees 2>/dev/null
   ```

2. **If NOT ignored** (exit code non-zero):
   ```bash
   echo '\n# Worktrees\n.worktrees/' >> .gitignore
   git add .gitignore && git commit -m "chore: add .worktrees/ to .gitignore"
   ```

3. **If already ignored**: Proceed silently.

---

## Step 8: Ask Base Branch

Use `AskUserQuestion` with three options:

- **main (Recommended)** -- Create from the main branch
- **Current branch** -- Create from the currently checked out branch (`HEAD`)
- **Other** -- User specifies a different branch name

If main/master doesn't exist, adjust to whichever default branch is present:
```bash
git rev-parse --verify main 2>/dev/null && echo "main" || echo "master"
```

---

## Step 9: Create Worktree

Generate the worktree and branch.

**Assembly**:

| Component | Value |
|-----------|-------|
| Worktree directory | `.worktrees/user-authentication` |
| Git branch | `feat/004-user-authentication` |
| Base branch | `main` |

**Commands**:

```bash
mkdir -p .worktrees
git worktree add ".worktrees/$KEYWORDS" -b "$TYPE/$NEXT_NUM-$KEYWORDS" "$BASE_BRANCH"
```

**Verify creation**:
```bash
git worktree list
```

**Report**:
```
Worktree created successfully!

  Path:   .worktrees/user-authentication
  Branch: feat/004-user-authentication (based on main)

  List worktrees:  git worktree list
  Remove when done: git worktree remove .worktrees/user-authentication
```

---

## Complete Example

**User Command**:
```bash
/worktree add user authentication system
```

**Step-by-Step Execution**:

1. **Determine Mode**: Manual (description provided)

2. **Parse**: `"add user authentication system"`

3. **Detect Type**:
   - Found keyword: "add"
   - Type: `feat`

4. **Extract Keywords**:
   - Remove: "add"
   - Keep: "user", "authentication", "system"
   - Limit: "user", "authentication"
   - Result: `user-authentication`

5. **Find Number**:
   - Scan: feat/001-profile, feat/002-dashboard
   - Max: 002
   - Next: 003
   - Result: `003`

6. **Validate**: `.worktrees/user-authentication` does not exist

7. **Git Ignore**: `.worktrees/` already in `.gitignore`

8. **Ask Base Branch**: User selects "main"

9. **Create Worktree**:
   ```bash
   git worktree add .worktrees/user-authentication -b feat/003-user-authentication main
   ```

**Final Output**:
```
Worktree created successfully!

  Path:   .worktrees/user-authentication
  Branch: feat/003-user-authentication (based on main)

  List worktrees:  git worktree list
  Remove when done: git worktree remove .worktrees/user-authentication
```

---

## Integration with Git Workflow

### Typical Development Flow

1. **Create worktree**:
   ```bash
   /worktree add payment integration
   # Path:   .worktrees/payment-integration
   # Branch: feat/015-payment-integration
   ```

2. **Switch to worktree** (in your terminal or IDE):
   ```bash
   cd .worktrees/payment-integration
   ```

3. **Work, commit, and push** (using `/commit` and `/create-pr`):
   ```bash
   /commit
   /create-pr
   ```

4. **Return to main workspace**:
   ```bash
   cd ../..
   ```

5. **Remove worktree when done**:
   ```bash
   git worktree remove .worktrees/payment-integration
   ```

### Multiple Simultaneous Worktrees

You can have multiple worktrees active at the same time:

```bash
/worktree add user authentication   # .worktrees/user-authentication
/worktree fix payment validation    # .worktrees/payment-validation
/worktree refactor api endpoints    # .worktrees/api-endpoints
```

Each operates independently with its own branch and working directory.

---

## Best Practices

1. **Descriptive Names**: Use clear, descriptive task descriptions
   - Good: `/worktree add user authentication with OAuth`
   - Poor: `/worktree new feature`

2. **Clean Up**: Remove worktrees when done to avoid clutter
   ```bash
   git worktree remove .worktrees/<name>
   ```

3. **Use for Isolation**: Worktrees are ideal for:
   - Parallel feature development
   - Reviewing PRs while working on another task
   - Running tests on one branch while coding on another
   - Hot-fixing production while mid-feature

---

*Last Updated: 2026-04-10*
