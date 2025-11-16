# GitHub Pull Request Creation: Examples

This document provides real-world examples of PR creation with the `creating-pr` skill.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).

---

## Example 1: Simple Feature PR

### Scenario
Created a feature branch with authentication code, ready to create PR.

### Command
```bash
/create-pr
```

### Execution

**Repository Detection**:
```
Detected: myapp (root repository)
Branch: feat/003-user-authentication
Remote: origin
```

**Branch Status**:
```
✅ Not a protected branch
✅ Branch has 3 commits ahead of main
```

**Push to Remote**:
```
Branch not on remote, pushing...
✅ Pushed: origin/feat/003-user-authentication
```

**PR Detection**:
```
Checking for existing PR...
✅ No existing PR found
```

**Content Generation**:
```
Title: feat(auth): add user authentication

Body:
## Summary
- Implemented OAuth2 authentication flow
- Added token refresh mechanism
- Added comprehensive auth tests

## Test Plan
- [ ] Test OAuth2 login with Google provider
- [ ] Verify token refresh on expiration
- [ ] Run auth test suite: `npm test auth`
```

**PR Creation**:
```
Creating pull request for feat/003-user-authentication → main...

✅ Pull Request #43 created
   https://github.com/user/myapp/pull/43
```

### Output
```
──────────────────────────────────
✅ Pull Request Created Successfully

#43: feat(auth): add user authentication
URL: https://github.com/user/myapp/pull/43

Next steps:
- View PR: gh pr view 43 --web
- Request review: gh pr review 43 --request @teammate
──────────────────────────────────
```

---

## Example 2: Bug Fix PR

### Scenario
Fixed a critical bug, need to create PR quickly.

### Command
```bash
/create-pr
```

### Execution

**Commits on branch**:
```
3e2f1a9 fix(auth): resolve null pointer in token validation
7a8b3c4 test(auth): add test for null token case
```

**Generated PR**:
```
Title: fix(auth): resolve null pointer in token validation

Body:
## Summary
- Added null safety checks in TokenValidator
- Fixed NPE when token is expired
- Added test coverage for edge case

## Test Plan
- [ ] Verify fix with expired tokens
- [ ] Run unit tests: `npm test auth`
- [ ] Manual testing in staging
```

### Output
```
✅ PR #44 created
   URL: https://github.com/user/myapp/pull/44
   Labels: bug, auth
```

---

## Example 3: Update Existing PR

### Scenario
PR already exists, made additional commits after code review feedback.

### Command
```bash
/create-pr
```

### Execution

**PR Detection**:
```
Found existing PR for this branch:

#43: feat(auth): add user authentication
URL: https://github.com/user/myapp/pull/43
State: OPEN

Options:
1. Update PR (push new commits)
2. View PR in browser
3. Cancel

Choose (1/2/3): 1
```

**Updating**:
```
Pushing latest commits...

New commits:
  8g4b9c0 feat(auth): address PR feedback
  5h6c2d1 refactor(auth): improve error handling

✅ PR #43 updated
   2 new commits pushed
   Review comments preserved
```

### Output
```
──────────────────────────────────
✅ PR Updated Successfully

#43: feat(auth): add user authentication
New commits: 2
URL: https://github.com/user/myapp/pull/43

Reviewers have been notified of the update.
──────────────────────────────────
```

---

## Example 4: Draft PR (Work in Progress)

### Scenario
Feature is not complete, want to show progress with draft PR.

### Command
```bash
/create-pr --draft
```

### Execution

**Content Generation**:
```
Title: feat(dashboard): add real-time analytics (WIP)

Body:
## Summary
- Work in progress on WebSocket connection
- Basic dashboard layout implemented
- TODO: Error handling and reconnection logic

## Test Plan
- [ ] TODO: Add WebSocket tests
- [ ] TODO: Test reconnection logic
- [ ] TODO: Manual testing
```

**Draft Creation**:
```
Creating draft pull request...

✅ Draft PR #45 created
   Status: DRAFT
   CI workflows will not run until marked ready
```

### Output
```
──────────────────────────────────
✅ Draft Pull Request Created

#45: feat(dashboard): add real-time analytics (WIP)
URL: https://github.com/user/myapp/pull/45
Status: DRAFT

When ready for review:
  gh pr ready 45
──────────────────────────────────
```

---

## Example 5: PR to Non-Default Branch

### Scenario
Feature targets `develop` branch, not `main`.

### Command
```bash
/create-pr --base develop
```

### Execution

**Branch Status**:
```
Current: feat/005-dashboard
Base: develop (non-default)
Commits ahead: 4
```

**PR Creation**:
```
Creating PR: feat/005-dashboard → develop

✅ PR #46 created
   Base: develop
   Head: feat/005-dashboard
```

### Output
```
──────────────────────────────────
✅ Pull Request Created

#46: feat(dashboard): add analytics
Base: develop ← feat/005-dashboard
URL: https://github.com/user/myapp/pull/46

Note: This PR will merge into develop, not main
──────────────────────────────────
```

---

## Example 6: Submodule PR

### Scenario
Made changes in a submodule, need to create PR for submodule's repository.

### Command
```bash
cd plugins/arkhe-claude-plugins/
../..//create-pr
```

### Execution

**Repository Detection**:
```
Detected: arkhe-claude-plugins (submodule)
Remote: git@github.com:user/arkhe-claude-plugins.git
Branch: feat/add-pr-skill
```

**PR Creation**:
```
Creating PR in submodule repository...

✅ PR #12 created
   Repository: user/arkhe-claude-plugins
   URL: https://github.com/user/arkhe-claude-plugins/pull/12
```

### Output
```
──────────────────────────────────
✅ Submodule Pull Request Created

#12: feat(git): add PR creation skill
Repository: arkhe-claude-plugins
URL: https://github.com/user/arkhe-claude-plugins/pull/12

Don't forget to update the root repository
after this PR is merged!
──────────────────────────────────
```

---

## Example 7: Combined Options (Draft + Custom Base)

### Scenario
Creating WIP PR targeting staging branch.

### Command
```bash
/create-pr --draft --base staging
```

### Execution

**Configuration**:
```
Mode: Draft PR
Base: staging
Current: feat/006-payment-gateway
```

**PR Creation**:
```
✅ Draft PR #47 created
   Base: staging
   Status: DRAFT
   URL: https://github.com/user/myapp/pull/47
```

---

## Example 8: Protected Branch Error

### Scenario
Accidentally tried to create PR while on main branch.

### Command
```bash
git checkout main
/create-pr
```

### Execution

**Branch Check**:
```
Current branch: main

❌ Error: Cannot create PR from protected branch 'main'

Pull requests must be created from feature branches.

Suggested workflow:
1. Create feature branch:
   /create-branch <description>

2. Make your changes

3. Commit changes:
   /commit

4. Create PR:
   /create-pr
```

**Result**: Script exits, no PR created

---

## Example 9: Already Pushed Branch

### Scenario
Branch already exists on remote, has new local commits.

### Command
```bash
/create-pr
```

### Execution

**Branch Status**:
```
✅ Branch exists on remote
✅ Local has 2 new commits

Pushing updates...
✅ Remote updated
```

**PR Creation**:
```
✅ PR #48 created
   Includes latest 2 commits
```

---

## Example 10: View Existing PR

### Scenario
PR already exists, just want to view it.

### Command
```bash
/create-pr
```

### Execution

**PR Detection**:
```
Found existing PR:

#43: feat(auth): add user authentication
URL: https://github.com/user/myapp/pull/43

Options:
1. Update PR
2. View PR in browser
3. Cancel

Choose: 2
```

**Result**:
```
Opening PR in browser...
https://github.com/user/myapp/pull/43

(Browser opens to PR page)
```

---

## Common Workflows

### Daily Feature Development

```bash
# 1. Create feature branch
/create-branch add user dashboard

# 2. Make changes
vim src/dashboard.ts

# 3. Commit changes
/commit

# 4. Create PR
/create-pr
```

### Bug Fix Workflow

```bash
# 1. Create fix branch
/create-branch fix login validation bug

# 2. Fix the bug
vim src/auth/login.ts

# 3. Commit fix
/commit

# 4. Create PR (automatically labeled as bug fix)
/create-pr
```

### Draft → Ready Workflow

```bash
# 1. Create draft PR early
/create-pr --draft

# 2. Continue working, push commits
git push

# 3. When ready, convert to ready
gh pr ready <PR_NUMBER>
```

### Multi-Repository Workflow

```bash
# 1. Work in submodule
cd plugins/arkhe-claude-plugins/
# Make changes
/commit
/create-pr

# 2. After submodule PR merges, update root
cd ../..
git submodule update --remote
/commit
/create-pr
```

---

## Tips for Effective PRs

### ✅ Good Practices

1. **Create from feature branches**: Never from main/master
2. **Write clear commits**: PR title derived from commits
3. **Keep PRs focused**: One feature or fix per PR
4. **Use draft PRs**: For work in progress
5. **Update existing PRs**: Instead of creating duplicates
6. **Target correct base**: Use `--base` when needed

### ❌ Avoid

1. **PRs from main branch**: Will be rejected
2. **Large, unfocused PRs**: Split into smaller PRs
3. **Missing test plans**: Always include testing approach
4. **Duplicate PRs**: Check for existing PRs first
5. **Forgotten submodule PRs**: Remember to PR submodule changes

---

## Summary

The `creating-pr` skill automates:
- ✅ Repository and branch detection
- ✅ Branch pushing to remote
- ✅ Existing PR detection and updates
- ✅ PR title/body generation from commits
- ✅ Draft and custom base branch support

**Result**: Professional GitHub PRs with minimal manual effort.

For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

*Last Updated: 2025-10-27*
