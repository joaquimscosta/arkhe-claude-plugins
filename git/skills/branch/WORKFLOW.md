# Git Branch Creation: Detailed Workflow

This document provides a detailed step-by-step breakdown of the branch creation process.

For quick start instructions, see [SKILL.md](SKILL.md).

## Overview

The branch creation process follows 5 main steps:

1. **Parse Description** - Extract user's task description
2. **Detect Commit Type** - Identify branch type from keywords
3. **Extract Keywords** - Filter meaningful words from description
4. **Find Next Number** - Auto-increment sequential number
5. **Create Branch** - Generate name and create git branch

---

## Step 1: Parse Description

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

## Step 2: Detect Commit Type

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

## Step 3: Extract Keywords

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

## Step 4: Find Next Number

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

## Step 5: Create Branch

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

3. **Optional: Create feature directory** (if `FEATURE_DIR` configured):
   ```bash
   mkdir -p .claude/specs/feat-004-user-authentication/
   ```

**Output**:
- Success message with branch name
- Optional feature directory path
- Current branch confirmation

---

## Complete Example

**User Command**:
```bash
/create-branch add user authentication system
```

**Step-by-Step Execution**:

1. **Parse**: `"add user authentication system"`

2. **Detect Type**:
   - Found keyword: "add"
   - Type: `feat`

3. **Extract Keywords**:
   - Remove: "add"
   - Keep: "user", "authentication", "system"
   - Limit: "user", "authentication"
   - Result: `user-authentication`

4. **Find Number**:
   - Scan: feat/001-profile, feat/002-dashboard
   - Max: 002
   - Next: 003
   - Result: `003`

5. **Create Branch**:
   - Assemble: `feat/003-user-authentication`
   - Execute: `git checkout -b feat/003-user-authentication`
   - Confirm: Branch created successfully

**Final Output**:
```
✅ Created branch: feat/003-user-authentication
📁 Feature directory: .claude/specs/feat-003-user-authentication/ (if configured)
```

---

## Configuration Options

### Environment Variables

**FEATURE_DIR** (optional):
```bash
export FEATURE_DIR=".claude/specs"
```
Creates a directory at `$FEATURE_DIR/{branch-name}/` for specifications.

**BRANCH_PREFIX** (optional):
```bash
export BRANCH_PREFIX="myteam-"
```
Adds prefix to all branch names: `myteam-feat/001-user-auth`

### Script Location

The workflow is implemented in shell scripts:
- **Main**: `git/skills/branch/scripts/branch.sh`
- **Utilities**: `git/skills/branch/scripts/common.sh`

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

### Feature Directory Structure

When `FEATURE_DIR` is configured:
```
.claude/specs/
├── feat-001-user-auth/
│   ├── spec.md
│   └── notes.md
├── fix-002-login-bug/
│   └── investigation.md
└── feat-003-dashboard/
    ├── design.md
    └── requirements.md
```

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

5. **Use Feature Directories**: Configure `FEATURE_DIR` for complex features
   - Store specifications, designs, and notes
   - Keep branch-specific documentation organized

---

## Summary

The branch creation workflow automates:
1. ✅ Type detection from natural language
2. ✅ Keyword extraction with stopword filtering
3. ✅ Sequential numbering across all branches
4. ✅ Short, readable branch names
5. ✅ Optional feature directory creation

**Result**: Consistent, discoverable branch names that align with conventional commits and modern git workflows.

For examples, see [EXAMPLES.md](EXAMPLES.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

*Last Updated: 2025-10-27*
