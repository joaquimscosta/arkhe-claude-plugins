# GitHub Pull Request Creation: Detailed Workflow

This document provides a detailed step-by-step breakdown of the PR creation process.

For quick start instructions, see [SKILL.md](SKILL.md).

## Overview

The PR creation process follows 6 main steps:

1. **Repository Detection** - Auto-detect root repository and submodules
2. **Branch Status Check** - Verify current branch and protection rules
3. **Push to Remote** - Ensure branch exists on GitHub
4. **PR Detection** - Check for existing PR on current branch
5. **PR Title/Body Generation** - Create content from commits
6. **PR Creation via gh** - Use GitHub CLI to create/update PR

---

## Step 1: Repository Detection

Automatically detect the repository structure.

### Root Repository Detection

**Process**:
1. Find root `.git` directory
2. Identify repository name from git remote
3. Determine if working in root or submodule

**Example**:
```bash
cd /Users/you/projects/myapp/
# Root repository: myapp
# Remote: origin git@github.com:user/myapp.git
```

### Submodule Detection

**Process**:
1. Check for `.gitmodules` in root
2. Identify current working directory location
3. Match against submodule paths
4. Determine if in submodule context

**Example**:
```bash
cd /Users/you/projects/myapp/plugins/arkhe-claude-plugins/
# Submodule: arkhe-claude-plugins
# Remote: origin git@github.com:user/arkhe-claude-plugins.git
```

### Scope Handling

**Interactive Mode** (no arguments):
- Auto-detect from current directory
- Use that repository for PR

**Direct Mode** (with scope):
```bash
/create-pr root
# Force PR for root repository

/create-pr arkhe-claude-plugins
# Force PR for specific submodule
```

---

## Step 2: Branch Status Check

Verify the current branch and protection rules.

### Current Branch Detection

```bash
git branch --show-current
```

**Example Output**: `feat/003-user-authentication`

### Protected Branch Check

**Protected branches** (prevented from creating PR):
- `main`
- `master`
- `production`
- `staging` (configurable)

**Check Logic**:
```bash
if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
    echo "❌ Cannot create PR from protected branch"
    echo "Suggestion: Create a feature branch first"
    exit 1
fi
```

**Error Message**:
```
❌ Error: Cannot create PR from main branch

Please create a feature branch:
  /create-branch <description>

Then commit your changes and try again.
```

### Branch Tracking Status

**Check if branch has remote tracking**:
```bash
git rev-parse --abbrev-ref @{upstream} 2>/dev/null
```

**Outcomes**:
- **Has upstream**: Branch already pushed to remote
- **No upstream**: Branch exists locally only (needs push)

---

## Step 3: Push to Remote

Ensure the current branch exists on GitHub.

### Local-Only Branch

**If branch not pushed**:
```bash
# Check tracking
git rev-parse @{upstream} 2>/dev/null
# Returns error if no upstream

# Push with upstream tracking
git push -u origin feat/003-user-authentication
```

**Output**:
```
Pushing branch to remote...
✅ Branch pushed: feat/003-user-authentication
```

### Already Pushed Branch

**If branch exists on remote**:
```bash
# Check if local is ahead
git rev-list @{upstream}..HEAD --count

# If ahead, push updates
git push
```

**Output**:
```
Branch already on remote
✅ Checking for updates...
✅ Remote is up to date
```

### Push Conflicts

**If remote has changes**:
```
❌ Remote has changes not in local branch

Options:
1. Pull and merge: git pull origin feat/003-user-authentication
2. Rebase: git pull --rebase origin feat/003-user-authentication
3. Force push (dangerous): git push --force
```

---

## Step 4: PR Detection

Check if a PR already exists for the current branch.

### GitHub CLI Query

```bash
gh pr list --head feat/003-user-authentication --json number,title,url,state
```

**Response (no PR)**:
```json
[]
```
→ Proceed to create new PR

**Response (PR exists)**:
```json
[
  {
    "number": 42,
    "title": "feat: add user authentication",
    "url": "https://github.com/user/myapp/pull/42",
    "state": "OPEN"
  }
]
```
→ Offer to update existing PR

### Existing PR Handling

**Options Presented**:
```
PR already exists: #42 "feat: add user authentication"
URL: https://github.com/user/myapp/pull/42

Options:
1. Update existing PR (push new commits)
2. View PR in browser
3. Cancel

Choose (1/2/3):
```

**Update PR** (Option 1):
- Push latest commits to branch
- GitHub automatically updates PR
- Comments and reviews preserved

**View PR** (Option 2):
- Open PR URL in browser
- Script exits

**Cancel** (Option 3):
- Exit without changes

---

## Step 5: PR Title/Body Generation

Generate PR content from recent commits.

### Title Generation

**Process**:
1. Get commits since branching from base
2. Analyze commit messages
3. Extract conventional commit type and scope
4. Create concise title

**Example**:

**Commits on branch**:
```
7f3a8b9 feat(auth): add OAuth2 login support
3e2f1a9 feat(auth): add token refresh logic
8g4b9c0 test(auth): add OAuth tests
```

**Generated Title**:
```
feat(auth): add user authentication
```

**Logic**:
- Use type from first commit (`feat`)
- Use scope from first commit (`auth`)
- Summarize overall changes in description
- Keep under 72 characters

### Body Generation

**Template**:
```markdown
## Summary
<1-3 bullet points summarizing changes>

## Test Plan
- [ ] TODO: Describe testing approach
- [ ] TODO: Manual testing steps
- [ ] TODO: Automated tests added
```

**Example Body**:
```markdown
## Summary
- Implemented OAuth2 authentication flow
- Added token refresh mechanism
- Added comprehensive auth tests

## Test Plan
- [ ] Test OAuth2 login with Google provider
- [ ] Verify token refresh on expiration
- [ ] Run auth test suite: `npm test auth`
- [ ] Manual testing in staging environment
```

### Interactive Approval

**Script Presents**:
```
Generated PR content:
──────────────────────────────────
Title: feat(auth): add user authentication

Body:
## Summary
- Implemented OAuth2 authentication flow
- Added token refresh mechanism
- Added comprehensive auth tests

## Test Plan
- [ ] Test OAuth2 login with Google provider
- [ ] Verify token refresh on expiration
- [ ] Run auth test suite
...
──────────────────────────────────

Proceed with this PR? (y/n/e):
```

**Options**:
- `y` → Create PR with this content
- `n` → Cancel
- `e` → Edit in text editor

---

## Step 6: PR Creation via gh

Use GitHub CLI to create the pull request.

### Basic PR Creation

```bash
gh pr create \
  --title "feat(auth): add user authentication" \
  --body "$(cat <<'EOF'
## Summary
...
EOF
)" \
  --base main
```

**Output**:
```
Creating pull request...

https://github.com/user/myapp/pull/43

✅ Pull request created: #43
```

### Draft PR Creation

**With `--draft` flag**:
```bash
gh pr create \
  --title "..." \
  --body "..." \
  --base main \
  --draft
```

**Output**:
```
✅ Draft pull request created: #43
   (Will not trigger CI until marked ready for review)
```

### Custom Base Branch

**With `--base` argument**:
```bash
gh pr create \
  --title "..." \
  --body "..." \
  --base develop
```

**Output**:
```
✅ Pull request created: #43
   Base: develop
   Head: feat/003-user-authentication
```

### PR URL Return

**Final Output**:
```
──────────────────────────────────
✅ Pull Request Created

Number: #43
Title: feat(auth): add user authentication
URL: https://github.com/user/myapp/pull/43
Base: main ← feat/003-user-authentication

Next steps:
1. Review PR in browser: gh pr view 43 --web
2. Request reviews: gh pr review 43 --request @teammate
3. Monitor CI: gh pr checks 43
──────────────────────────────────
```

---

## Complete Example Workflows

### Example 1: Simple Feature PR

**Context**: Feature branch with new authentication code

**Command**:
```bash
/create-pr
```

**Workflow**:

**Step 1: Detection**
```
Repository: myapp (root)
Branch: feat/003-user-authentication
```

**Step 2: Branch Check**
```
✅ Not a protected branch
✅ Safe to create PR
```

**Step 3: Push**
```
Branch not on remote, pushing...
✅ Pushed to origin/feat/003-user-authentication
```

**Step 4: PR Detection**
```
Checking for existing PR...
✅ No existing PR found
```

**Step 5: Content Generation**
```
Title: feat(auth): add user authentication
Body: (generated from 3 commits)
```

**Step 6: Creation**
```
✅ PR created: #43
URL: https://github.com/user/myapp/pull/43
```

---

### Example 2: Update Existing PR

**Context**: PR exists, made more commits

**Command**:
```bash
/create-pr
```

**Workflow**:

**Steps 1-3**: (same as Example 1)

**Step 4: PR Detection**
```
Found existing PR: #43 "feat(auth): add user authentication"

Options:
1. Update PR (push new commits)
2. View PR
3. Cancel

Choose: 1
```

**Updating**:
```
Pushing latest commits...
✅ PR #43 updated with 2 new commits

View updated PR:
https://github.com/user/myapp/pull/43
```

---

### Example 3: Draft PR

**Context**: Work in progress, not ready for review

**Command**:
```bash
/create-pr --draft
```

**Workflow**:

**Steps 1-5**: (same as Example 1)

**Step 6: Creation**
```
✅ Draft PR created: #44
   Status: DRAFT (CI will not run)

Convert to ready for review when done:
  gh pr ready 44
```

---

### Example 4: PR to Non-Default Branch

**Context**: Feature branch targets `develop` not `main`

**Command**:
```bash
/create-pr --base develop
```

**Workflow**:

**Steps 1-5**: (same as Example 1)

**Step 6: Creation**
```
✅ PR created: #45
   Base: develop ← feat/003-user-authentication

Note: Merging will update develop branch, not main
```

---

### Example 5: Submodule PR

**Context**: Working in submodule, want to create PR for submodule repo

**Command**:
```bash
cd plugins/arkhe-claude-plugins/
../..//create-pr
```

**Workflow**:

**Step 1: Detection**
```
Repository: arkhe-claude-plugins (submodule)
Remote: git@github.com:user/arkhe-claude-plugins.git
Branch: feat/add-pr-skill
```

**Steps 2-6**: Same as root PR, but targets submodule's GitHub repo

**Result**:
```
✅ PR created in submodule repository
URL: https://github.com/user/arkhe-claude-plugins/pull/12
```

---

## Advanced Features

### Conventional Commit Detection

**Automatic type/scope extraction**:

```
Commit: feat(auth): add OAuth2
→ Type: feat
→ Scope: auth
→ Title: feat(auth): add user authentication
```

**Supported types**:
- `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`

### Multi-Commit PRs

**When branch has multiple commits**:
- Title uses first commit's type/scope
- Body summarizes all commits
- Test plan includes all changes

### Branch Protection Awareness

**Checks before PR creation**:
- ✅ Not on `main` or `master`
- ✅ Not on `production`
- ✅ Has commits ahead of base

### GitHub CLI Integration

**Relies on `gh` for**:
- Authentication
- PR creation
- PR updates
- PR detection

**Requires**: `gh auth login` run once

---

## Configuration

### Environment Variables

**GH_REPO** (optional):
```bash
export GH_REPO=user/myapp
```
Explicitly set repository (useful for forks)

### Base Branch Configuration

**Default**: `main`

**Override**:
```bash
/create-pr --base develop
```

### Custom PR Template

Edit script to customize body template:
```bash
# In pr.sh
BODY_TEMPLATE="## Changes\n...\n\n## Testing\n..."
```

---

## Important: No Claude Code Footer Policy

**The pr.sh script generates clean PR content without any attribution.**

⚠️ **CRITICAL CONSTRAINT**: Never add Claude Code footers or attribution to PR titles or descriptions.

**Prohibited Content**:
- ❌ "🤖 Generated with [Claude Code]" in PR title
- ❌ "🤖 Generated with [Claude Code]" in PR body
- ❌ "Co-Authored-By: Claude <noreply@anthropic.com>"
- ❌ Any Claude Code branding or attribution

**Why This Matters**:
- PRs should reflect actual contributors
- Professional appearance for code review
- Clean, focused content without marketing material

**Runtime Verification**:
The `pr.sh` script automatically verifies that no footer was added to PR titles or descriptions. If detected, the script will fail with an error message.

**Example of Correct PR**:
```
Title: feat(auth): add OAuth2 login support

Body:
## Issue
- resolves: #123

## Why is this change needed?
This PR includes the following changes:
- feat(auth): implement OAuth2 flow
- feat(auth): add token refresh

## Testing
- [x] Tests added/updated
- [x] Manual testing completed
```

**Example of Incorrect PR** (will be rejected):
```
Title: feat(auth): add OAuth2 login support

Body:
## Issue
- resolves: #123

## Why is this change needed?
...

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Best Practices

1. **Create feature branches**: Never PR from `main`
2. **Write clear commits**: PR title derived from commits
3. **Keep PRs focused**: One feature per PR
4. **Use draft PRs**: For work-in-progress
5. **Update existing PRs**: Push new commits rather than creating duplicates
6. **Target correct base**: Use `--base` for non-main branches

---

## Summary

The PR creation workflow automates:
1. ✅ Repository and branch detection
2. ✅ Branch pushing to remote
3. ✅ Existing PR detection
4. ✅ PR title/body generation from commits
5. ✅ GitHub CLI integration
6. ✅ Draft and custom base branch support

**Result**: Professional PRs with minimal manual effort.

For examples, see [EXAMPLES.md](EXAMPLES.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Bash Implementation Reference

The following bash snippets provide the reference implementation for each workflow step.

### Argument Parsing

```bash
SCOPE=""
DRAFT_FLAG=""
BASE_BRANCH="main"

# Example parsing:
# "root --draft" → SCOPE="root", DRAFT_FLAG="--draft", BASE_BRANCH="main"
# "--base staging" → SCOPE="", DRAFT_FLAG="", BASE_BRANCH="staging"
# "my-service --draft --base develop" → SCOPE="my-service", DRAFT_FLAG="--draft", BASE_BRANCH="develop"
```

### Repository Context Detection

```bash
# Find monorepo root (handles submodules)
if SUPERPROJECT=$(git rev-parse --show-superproject-working-tree 2>/dev/null) && [ -n "$SUPERPROJECT" ]; then
    MONOREPO_ROOT="$SUPERPROJECT"
else
    MONOREPO_ROOT=$(git rev-parse --show-toplevel)
fi

CURRENT_DIR=$(pwd)

if [ -n "$SCOPE" ]; then
    if [ "$SCOPE" = "root" ]; then
        REPO_PATH="$MONOREPO_ROOT"
    else
        REPO_PATH="$MONOREPO_ROOT/$SCOPE"
    fi
else
    if [[ "$CURRENT_DIR" == "$MONOREPO_ROOT" ]]; then
        REPO_PATH="$MONOREPO_ROOT"
    else
        REPO_PATH=$(git -C "$CURRENT_DIR" rev-parse --show-toplevel)
    fi
fi

if [ ! -d "$REPO_PATH/.git" ]; then
    echo "❌ Error: Not a valid git repository: $REPO_PATH" >&2
    exit 1
fi
```

### Branch Validation

```bash
cd "$REPO_PATH"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo "❌ Cannot create PR from protected branch: $CURRENT_BRANCH" >&2
    echo "Please create a feature branch first:" >&2
    echo "  git checkout -b feature/your-feature-name" >&2
    exit 1
fi

UNCOMMITTED=$(git status --porcelain)
if [ -n "$UNCOMMITTED" ]; then
    echo "❌ Error: You have uncommitted changes" >&2
    git status --short
    exit 1
fi

COMMITS_AHEAD=$(git rev-list --count "$BASE_BRANCH..HEAD" 2>/dev/null || echo "0")
if [ "$COMMITS_AHEAD" = "0" ]; then
    echo "❌ Error: No commits to create PR from" >&2
    exit 1
fi
```

### Push Branch to Remote

```bash
REMOTE_BRANCH=$(git ls-remote --heads origin "$CURRENT_BRANCH" 2>/dev/null)

if [ -z "$REMOTE_BRANCH" ]; then
    git push -u origin "$CURRENT_BRANCH" || { echo "❌ Failed to push" >&2; exit 1; }
else
    LOCAL_HASH=$(git rev-parse HEAD)
    REMOTE_HASH=$(git rev-parse "origin/$CURRENT_BRANCH" 2>/dev/null || echo "")
    if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        git push origin "$CURRENT_BRANCH" || { echo "❌ Failed to push" >&2; exit 1; }
    fi
fi
```

### Existing PR Detection

```bash
EXISTING_PR=$(gh pr view "$CURRENT_BRANCH" --json number,title,url 2>/dev/null || echo "")

if [ -n "$EXISTING_PR" ]; then
    PR_NUMBER=$(echo "$EXISTING_PR" | jq -r '.number')
    PR_URL=$(echo "$EXISTING_PR" | jq -r '.url')
    # Offer to update or view existing PR
fi
```

### PR Title Generation (Conventional Commits)

```bash
COMMITS=$(git log "$BASE_BRANCH..HEAD" --oneline)
LATEST_COMMIT=$(git log -1 --pretty=%B)

if echo "$LATEST_COMMIT" | grep -qE '^(feat|fix|docs|refactor|test|chore|perf|ci|build):'; then
    COMMIT_TYPE=$(echo "$LATEST_COMMIT" | grep -oE '^[a-z]+' | head -1)
    COMMIT_DESC=$(echo "$LATEST_COMMIT" | sed -E 's/^[a-z]+(\([^)]+\))?:\s*//')
else
    ALL_COMMITS=$(git log "$BASE_BRANCH..HEAD" --pretty=%B)
    if echo "$ALL_COMMITS" | grep -qi "fix\|bug"; then COMMIT_TYPE="fix"
    elif echo "$ALL_COMMITS" | grep -qi "feat\|feature\|add"; then COMMIT_TYPE="feat"
    elif echo "$ALL_COMMITS" | grep -qi "docs\|documentation"; then COMMIT_TYPE="docs"
    elif echo "$ALL_COMMITS" | grep -qi "refactor"; then COMMIT_TYPE="refactor"
    elif echo "$ALL_COMMITS" | grep -qi "test"; then COMMIT_TYPE="test"
    else COMMIT_TYPE="feat"
    fi
    COMMIT_DESC=$(echo "$LATEST_COMMIT" | head -1 | sed 's/^\s*//')
fi

PR_TITLE="$COMMIT_TYPE: $COMMIT_DESC"
```

### PR Body Generation

```bash
PR_BODY="## Summary

"
if [ "$COMMIT_COUNT" -eq 1 ]; then
    PR_BODY+="$LATEST_COMMIT

"
else
    PR_BODY+="This PR includes $COMMIT_COUNT commits:

"
    while IFS= read -r commit; do
        PR_BODY+="- $commit
"
    done <<< "$COMMITS"
fi

PR_BODY+="## Test Plan

- [ ] Code builds successfully
- [ ] Tests pass
- [ ] Manual testing completed
- [ ] Documentation updated (if needed)

## Changes

"
CHANGED_FILES=$(git diff --name-only "$BASE_BRANCH..HEAD")
while IFS= read -r file; do
    PR_BODY+="- \`$file\`
"
done <<< "$CHANGED_FILES"
```

### PR Creation and Update

```bash
# Create new PR
GH_CMD="gh pr create --title \"$PR_TITLE\" --body \"$PR_BODY\" --base \"$BASE_BRANCH\""
if [ "$DRAFT_FLAG" = "--draft" ]; then
    GH_CMD+=" --draft"
fi
eval "$GH_CMD"

# Or update existing PR
gh pr edit "$PR_NUMBER" --title "$PR_TITLE" --body "$PR_BODY"
```

---

*Last Updated: 2025-10-27*
