# Git Worktree Creation: Examples

Real-world examples demonstrating all worktree creation modes and scenarios.

---

## Example 1: Feature Worktree

**Command**:
```bash
/worktree add user authentication
```

**Result**:
```
Worktree created successfully!

  Path:   .claude/worktrees/user-authentication
  Branch: feat/001-user-authentication (based on main)

  List worktrees:  git worktree list
  Remove when done: git worktree remove .claude/worktrees/user-authentication
```

**What happened**:
- Detected "add" -> `feat` type
- Extracted keywords: "user", "authentication"
- Found next number: 001
- Created worktree at `.claude/worktrees/user-authentication`
- Created branch `feat/001-user-authentication` from `main`

---

## Example 2: Bug Fix Worktree

**Command**:
```bash
/worktree fix login validation error
```

**Result**:
```
Worktree created successfully!

  Path:   .claude/worktrees/login-validation
  Branch: fix/002-login-validation (based on main)

  List worktrees:  git worktree list
  Remove when done: git worktree remove .claude/worktrees/login-validation
```

**What happened**:
- Detected "fix" -> `fix` type
- Extracted keywords: "login", "validation" (filtered "error" as 3rd word limit)
- Sequential number: 002

---

## Example 3: Refactoring Worktree

**Command**:
```bash
/worktree refactor auth service
```

**Result**:
```
Worktree created successfully!

  Path:   .claude/worktrees/auth-service
  Branch: refactor/003-auth-service (based on main)
```

---

## Example 4: Documentation Worktree

**Command**:
```bash
/worktree document api endpoints
```

**Result**:
```
Worktree created successfully!

  Path:   .claude/worktrees/api-endpoints
  Branch: docs/004-api-endpoints (based on main)
```

---

## Example 5: Auto-Generate from Changes

**Scenario**: You have uncommitted changes to authentication files.

```bash
git status
# modified:   src/auth/login.ts
# modified:   src/auth/session.ts
# new file:   src/auth/oauth.ts
```

**Command**:
```bash
/worktree
```

**Result**:
```
Auto-detected from changes: auth module modifications

Worktree created successfully!

  Path:   .claude/worktrees/auth-login
  Branch: feat/005-auth-login (based on main)
  (based on: src/auth/login.ts, src/auth/session.ts, src/auth/oauth.ts)
```

---

## Example 6: Base Branch Selection

**Command**:
```bash
/worktree add payment integration
```

**Prompt**:
```
Which branch should this worktree be based on?
  > main (Recommended)
    Current branch (feat/001-user-authentication)
    Other
```

**User selects "Current branch"**:
```
Worktree created successfully!

  Path:   .claude/worktrees/payment-integration
  Branch: feat/006-payment-integration (based on feat/001-user-authentication)
```

---

## Example 7: From SDLC-Develop Spec

**Scenario**: Project has `.arkhe.yaml` with specs:
```
arkhe/specs/
  01-user-auth/
  02-dashboard/
  03-payment/
```

**Command**:
```bash
/worktree
```

**Prompt**:
```
Select a feature spec for this worktree:
  > 01-user-auth
    02-dashboard
    03-payment
    None (auto-generate from changes)
```

**User selects "02-dashboard"**:
```
Worktree created successfully!

  Path:   .claude/worktrees/02-dashboard
  Branch: feat/02-dashboard (based on main)
```

---

## Example 8: Long Description with Keyword Limiting

**Command**:
```bash
/worktree add comprehensive user authentication system with OAuth2 and JWT support
```

**Result**:
```
Worktree created successfully!

  Path:   .claude/worktrees/user-authentication
  Branch: feat/007-user-authentication (based on main)
```

**What happened**: Keywords limited to first 2 meaningful words after filtering stopwords and type keywords.

---

## Example 9: Sequential Numbering Across Types

Starting state:
```
feat/001-user-auth
fix/002-login-bug
feat/003-dashboard
```

**Command**: `/worktree refactor api cleanup`

**Result**: Branch `refactor/004-api-cleanup` -- numbers are global, not per-type.

---

## Example 10: Multiple Simultaneous Worktrees

```bash
/worktree add user authentication    # .claude/worktrees/user-authentication
/worktree fix payment validation     # .claude/worktrees/payment-validation
/worktree refactor api endpoints     # .claude/worktrees/api-endpoints
```

**Verify all worktrees**:
```bash
git worktree list
# /Users/you/project                     abc1234 [main]
# /Users/you/project/.claude/worktrees/user-authentication  def5678 [feat/008-user-authentication]
# /Users/you/project/.claude/worktrees/payment-validation    ghi9012 [fix/009-payment-validation]
# /Users/you/project/.claude/worktrees/api-endpoints         jkl3456 [refactor/010-api-endpoints]
```

---

## Example 11: Full Development Workflow

### Create worktree
```bash
/worktree add newsletter signup
# Path:   .claude/worktrees/newsletter-signup
# Branch: feat/011-newsletter-signup (based on main)
```

### Switch to worktree and work
```bash
cd .claude/worktrees/newsletter-signup
# ... make changes ...
```

### Commit and create PR
```bash
/commit
/create-pr
# PR created: https://github.com/org/repo/pull/42
```

### Return to main workspace
```bash
cd ../..
```

### Clean up after merge
```bash
git worktree remove .claude/worktrees/newsletter-signup
git branch -d feat/011-newsletter-signup
```

---

## Example 12: Chore Worktree

**Command**:
```bash
/worktree remove deprecated endpoints
```

**Result**:
```
Worktree created successfully!

  Path:   .claude/worktrees/deprecated-endpoints
  Branch: chore/012-deprecated-endpoints (based on main)
```

---

## Example 13: Default Type (No Keyword Match)

**Command**:
```bash
/worktree dashboard analytics
```

**Result**:
```
Worktree created successfully!

  Path:   .claude/worktrees/dashboard-analytics
  Branch: feat/013-dashboard-analytics (based on main)
```

**What happened**: No type keyword detected, defaulted to `feat`.

---

## Dual Naming Summary

| Input | Worktree Directory | Git Branch |
|-------|-------------------|------------|
| `add user auth` | `.claude/worktrees/user-auth` | `feat/001-user-auth` |
| `fix login bug` | `.claude/worktrees/login-bug` | `fix/002-login-bug` |
| `refactor api` | `.claude/worktrees/api` | `refactor/003-api` |
| `remove old code` | `.claude/worktrees/old-code` | `chore/004-old-code` |
| `document endpoints` | `.claude/worktrees/endpoints` | `docs/005-endpoints` |

The directory name is short for easy navigation. The branch name includes the full conventional prefix for git consistency.

---

*Last Updated: 2026-04-10*
