# Git Branch Creation: Detailed Workflow

This document provides a detailed step-by-step breakdown of the branch creation process.

## Overview

The branch creation process follows 6 main steps:

1. **Determine Mode** - Check for description, specs, or auto-generate
1b. **Spec Selection** - (Mode 3 only) Present available specs for selection
2. **Parse Description** - Extract user's task description
3. **Detect Commit Type** - Identify branch type from keywords
4. **Extract Keywords** - Filter meaningful words from description
5. **Find Next Number** - Auto-increment sequential number
6. **Create Branch** - Generate name and create git branch

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
- Skip to Step 5 (branch name is `{type}/{spec-name}`)

If user selects "None":
- Set MODE="auto-generate"
- Proceed to auto-generate from changes

---

## Step 2: Parse Description

Extract and normalize the user's task description.

**Input**: Raw description from user command
```bash
/create-branch add user authentication system
```

**Process**:
1. Remove command prefix (`/create-branch`)
2. Trim whitespace
3. Convert to lowercase
4. Store as working description

**Output**: `"add user authentication system"`

---

## Step 3: Detect Commit Type

Analyze description keywords to determine branch type.

**Detection Logic**:

The script scans for specific keywords in the description:

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
- "add user auth" → `feat` (keyword: "add")
- "fix login bug" → `fix` (keyword: "fix")
- "refactor auth service" → `refactor` (keyword: "refactor")
- "remove old code" → `chore` (keyword: "remove")
- "document api" → `docs` (keyword: "document")

**Output**: Commit type string (e.g., `feat`)

---

## Step 4: Extract Keywords

Filter meaningful words from description for branch name.

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

**Output**: Hyphenated keyword string

---

## Step 5: Find Next Number

Determine the next sequential branch number.

**Process**:

1. **Scan existing branches**:
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
- **Non-sequential numbers**: Find max and increment (e.g., 001, 005 → next is 006)
- **Different types**: Numbers are global across all types

**Output**: 3-digit number string (e.g., `"004"`)

---

## Step 6: Create Branch

Generate branch name and execute git command.

**Branch Name Assembly**:

```
{type}/{number}-{keywords}
```

**Example Construction**:
- Type: `feat`
- Number: `004`
- Keywords: `user-authentication`
- **Branch**: `feat/004-user-authentication`

**Git Operations**:

1. **Create branch**:
   ```bash
   git checkout -b feat/004-user-authentication
   ```

2. **Verify creation**:
   ```bash
   git branch --show-current
   ```

**Output**:
- Success message with branch name
- If spec-select mode: shows linked spec directory
- Current branch confirmation

---

## Complete Example

**User Command**:
```bash
/create-branch add user authentication system
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

6. **Create Branch**:
   - Assemble: `feat/003-user-authentication`
   - Execute: `git checkout -b feat/003-user-authentication`
   - Confirm: Branch created successfully

**Final Output**:
```
✅ Created branch: feat/003-user-authentication
```

---

## Configuration Options

### Environment Variables

**BRANCH_PREFIX** (optional):
```bash
export BRANCH_PREFIX="myteam-"
```
Adds prefix to all branch names: `myteam-feat/001-user-auth`

### SDLC-Develop Configuration

When `.arkhe.yaml` exists, the skill reads:
```yaml
develop:
  specs_dir: arkhe/specs  # Default if not specified
```

The skill scans this directory for existing spec directories to offer as branch name options.

---

## Integration with Git Workflow

### Typical Development Flow

1. **Start new task**:
   ```bash
   /create-branch add payment integration
   → feat/015-payment-integration
   ```

2. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat: implement payment gateway"
   ```

3. **Push to remote**:
   ```bash
   git push -u origin feat/015-payment-integration
   ```

4. **Create pull request** (use `/create-pr` skill)

### Branch Naming Consistency

The branch names align with conventional commits:
- Branch: `feat/001-user-auth`
- Commits: `feat: add user authentication`
- PR title: `feat: user authentication`

---

## Advanced Use Cases

### Custom Branch Types

While the script supports 5 default types, you can manually create branches with custom types:

```bash
git checkout -b perf/001-optimize-queries
git checkout -b test/002-add-unit-tests
git checkout -b ci/003-github-actions
```

### Sequential Numbering Across Types

Numbers increment globally, not per-type:
```
feat/001-user-auth
fix/002-login-bug
feat/003-dashboard
refactor/004-auth-service
```

This ensures unique identifiers across the entire project.

### SDLC-Develop Integration

When `.arkhe.yaml` exists and contains specs:
```
arkhe/specs/
├── 01-user-auth/
│   ├── spec.md
│   └── plan.md
├── 02-dashboard/
│   └── spec.md
└── 03-payment/
    ├── spec.md
    └── plan.md
```

Running `/create-branch` without arguments will offer spec selection:
```
Select a feature spec for this branch:
- 01-user-auth
- 02-dashboard
- 03-payment
- None (auto-generate from changes)
```

Selected spec becomes the branch name: `feat/01-user-auth`

---

## Best Practices

1. **Descriptive Names**: Use clear, descriptive task descriptions
   - ✅ Good: `/create-branch add user authentication with OAuth`
   - ❌ Poor: `/create-branch new feature`

2. **Consistent Keywords**: Use conventional commit keywords
   - Use "add" or "create" for new features
   - Use "fix" for bug fixes
   - Use "refactor" for code improvements

3. **Keep Names Short**: The script automatically limits to 2-3 keywords
   - Input: "add comprehensive user authentication system with OAuth2"
   - Output: `feat/001-user-authentication` (first 2 meaningful words)

4. **Review Generated Name**: Check the generated branch name before committing
   - The script shows the branch name before creating it
   - Adjust description if needed

5. **Use SDLC-Develop Integration**: For complex features, use `/develop` first
   - Creates structured specs in `arkhe/specs/`
   - `/create-branch` will detect and offer spec selection

---

## Summary

The branch creation workflow automates:
1. ✅ Type detection from natural language
2. ✅ Keyword extraction with stopword filtering
3. ✅ Sequential numbering across all branches
4. ✅ Short, readable branch names
5. ✅ SDLC-develop spec detection and selection

**Result**: Consistent, discoverable branch names that align with conventional commits and modern git workflows.

---

*Last Updated: 2025-10-27*
