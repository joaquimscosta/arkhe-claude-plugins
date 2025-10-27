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
git/skills/pr/scripts/pr.sh root
# Force PR for root repository

git/skills/pr/scripts/pr.sh arkhe-claude-plugins
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

🤖 Generated with [Claude Code](https://claude.com/claude-code)
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

🤖 Generated with [Claude Code](https://claude.com/claude-code)
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
git/skills/pr/scripts/pr.sh
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
git/skills/pr/scripts/pr.sh
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
git/skills/pr/scripts/pr.sh --draft
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
git/skills/pr/scripts/pr.sh --base develop
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
../../git/skills/pr/scripts/pr.sh
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
git/skills/pr/scripts/pr.sh --base develop
```

### Custom PR Template

Edit script to customize body template:
```bash
# In pr.sh
BODY_TEMPLATE="## Changes\n...\n\n## Testing\n..."
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

*Last Updated: 2025-10-27*
