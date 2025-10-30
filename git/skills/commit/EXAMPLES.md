# Git Commit Creation: Examples

This document provides real-world examples of commit creation with the `creating-commit` skill.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).

---

## Example 1: Simple Feature Commit (Root Repository)

### Scenario
Adding a new authentication feature in the root repository.

### Command
```bash
git/skills/commit/scripts/commit.sh
```

### Execution

**Step 1: Repository Detection**
```
Detected repositories:
- Root: myapp
  Changes: src/auth/login.ts, src/auth/oauth.ts
```

**Step 2: Change Analysis**
```
File types: TypeScript (2 files)
Pre-commit check: npx tsc --noEmit
```

**Step 3: Pre-commit Checks**
```bash
Running TypeScript type checking...
✅ TypeScript compilation successful
```

**Step 4: Commit Message**
```
Suggested commit:
──────────────────────────────────
feat(auth): add OAuth2 login support

Implemented OAuth2 authentication flow with
token refresh and secure session management.
──────────────────────────────────

Proceed? (y/n): y
```

### Output
```
✅ Committed: [myapp 7f3a8b9] feat(auth): add OAuth2 login support
   2 files changed, 145 insertions(+)
```

---

## Example 2: Bug Fix with Pre-commit Checks

### Scenario
Fixing a null pointer exception in Kotlin code.

### Command
```bash
git/skills/commit/scripts/commit.sh
```

### Execution

**Changes Detected**:
```
Root: backend-service
  M src/main/kotlin/auth/UserService.kt
  M src/main/kotlin/auth/TokenValidator.kt
```

**Pre-commit Check**:
```bash
Running Detekt...
✅ Detekt analysis passed
   0 issues found
```

**Commit Message**:
```
fix(auth): resolve null pointer in token validation

Added null safety checks in TokenValidator.validateToken()
to prevent NPE when token is expired.
```

### Output
```
✅ Committed: [backend-service 3e2f1a9] fix(auth): resolve null pointer
   2 files changed, 12 insertions(+), 4 deletions(-)
```

---

## Example 3: Submodule Commit Only

### Scenario
Updating documentation in a plugin submodule.

### Command
```bash
git/skills/commit/scripts/commit.sh arkhe-claude-plugins
```

### Execution

**Scope**: Directly commit to `arkhe-claude-plugins` submodule

**Changes**:
```
Submodule: arkhe-claude-plugins
  M git/skills/commit/SKILL.md
  A git/skills/commit/WORKFLOW.md
```

**Pre-commit**: None required (documentation)

**Commit**:
```
docs(commit): add comprehensive workflow documentation

Added detailed 5-step process covering repository detection,
change analysis, pre-commit checks, message generation, and
submodule handling.
```

### Output
```
✅ Committed in submodule: [arkhe-claude-plugins def5678]
   2 files changed, 420 insertions(+)
```

---

## Example 4: Submodule Commit with Root Update

### Scenario
Commit to submodule, then update the submodule reference in root.

### Command
```bash
git/skills/commit/scripts/commit.sh
```

### Execution

**Step 1: Detection**
```
Detected changes:
1. arkhe-claude-plugins (submodule)

Select repository: 1
```

**Step 2: Commit to Submodule**
```
✅ Committed: [arkhe-claude-plugins abc1234] feat(git): add commit skill
```

**Step 3: Root Update Prompt**
```
Submodule reference updated in root repository.

Root repository now shows:
  modified: plugins/arkhe-claude-plugins (new commits)

Update submodule reference in root? (y/n): y
```

**Step 4: Root Commit**
```
Committing to root...

chore: update arkhe-claude-plugins submodule

Updated to include:
- feat(git): add commit skill
```

### Output
```
✅ Submodule committed: [arkhe-claude-plugins abc1234]
✅ Root updated: [myapp 8g4b9c0] chore: update submodule
```

---

## Example 5: Skip Verification (Fast Commit)

### Scenario
Documentation-only changes, want to skip all checks for speed.

### Command
```bash
git/skills/commit/scripts/commit.sh --no-verify
```

### Execution

**Changes**:
```
Root: myapp
  M README.md
  M docs/installation.md
```

**Pre-commit Checks**:
```
--no-verify flag detected
⏭️  Skipping all pre-commit checks
```

**Commit**:
```
docs: update installation guide

Added troubleshooting section and clarified
dependency requirements.
```

### Output
```
✅ Committed: [myapp 5c7d2e1] docs: update installation guide
   (no checks run)
```

---

## Example 6: Full Verification Mode

### Scenario
Before pushing to production, want comprehensive checks.

### Command
```bash
git/skills/commit/scripts/commit.sh --full-verify
```

### Execution

**Changes**:
```
Root: myapp
  M src/api/endpoints.ts
  M src/ui/components/Dashboard.tsx
```

**Pre-commit Checks**:
```bash
Running full verification...

Backend checks:
  ✅ TypeScript compilation (API)
  ✅ Unit tests passed

Frontend checks:
  ✅ TypeScript compilation (UI)
  ✅ React component tests passed
  ✅ Lint checks passed

All checks passed ✅
```

**Commit**:
```
feat(dashboard): add real-time analytics

Implemented WebSocket connection for live data
updates on dashboard with automatic reconnection.
```

### Output
```
✅ Full verification passed
✅ Committed: [myapp 9h5c3f2] feat(dashboard): add real-time analytics
```

---

## Example 7: Pre-commit Check Failure

### Scenario
TypeScript compilation error prevents commit.

### Command
```bash
git/skills/commit/scripts/commit.sh
```

### Execution

**Changes**:
```
Root: myapp
  M src/auth/login.ts
```

**Pre-commit Check**:
```bash
Running TypeScript check...

❌ TypeScript compilation failed:

src/auth/login.ts:42:15 - error TS2345
  Argument of type 'string' is not assignable to parameter of type 'number'.

  42     authenticate(userId);
                      ~~~~~~

Found 1 error.
```

**Result**: Commit **aborted**

### Resolution Options

**Option 1: Fix the error**
```typescript
// Before
authenticate(userId);  // userId is string

// After
authenticate(Number(userId));  // Convert to number
```

**Option 2: Skip verification** (if confident)
```bash
git/skills/commit/scripts/commit.sh --no-verify
```

---

## Example 8: Rust Project Commit

### Scenario
Committing changes to a Rust project.

### Command
```bash
git/skills/commit/scripts/commit.sh
```

### Execution

**Changes**:
```
Root: rust-cli
  M src/main.rs
  M src/parser.rs
```

**Pre-commit Check**:
```bash
Running cargo check...

   Compiling rust-cli v0.1.0
   Finished dev [unoptimized + debuginfo] target(s) in 2.34s

✅ Cargo check passed
```

**Commit**:
```
feat(parser): add JSON parsing support

Implemented serde-based JSON parser with
error handling and validation.
```

### Output
```
✅ Committed: [rust-cli 4f8a2b3] feat(parser): add JSON parsing
   2 files changed, 87 insertions(+)
```

---

## Example 9: Mixed Changes (Interactive Selection)

### Scenario
Changes in both root and submodule, need to choose which to commit.

### Command
```bash
git/skills/commit/scripts/commit.sh
```

### Execution

**Detection**:
```
Multiple repositories with changes detected:

1. myapp (root)
   - src/api/server.ts
   - src/config/database.ts

2. arkhe-claude-plugins (submodule)
   - git/skills/commit/SKILL.md

Select repository to commit (1 or 2): 2
```

**Selected**: Commit to submodule first

**Submodule Commit**:
```
✅ Committed: [arkhe-claude-plugins xyz7890] docs(commit): update SKILL.md
```

**Root Update Prompt**:
```
Update submodule reference in root? (y/n): n
```

**Result**: Submodule committed, root changes remain staged

---

## Example 10: Scope-Specific Commit

### Scenario
Commit directly to root, ignoring submodule changes.

### Command
```bash
git/skills/commit/scripts/commit.sh root
```

### Execution

**Scope**: `root` (explicit)

**Changes**:
```
Root: myapp
  M package.json
  M src/index.ts
```

**Note**: Submodule changes ignored (will remain staged)

**Commit**:
```
feat: upgrade to Node.js 20

Updated dependencies and TypeScript target
to support Node.js 20 features.
```

### Output
```
✅ Committed to root: [myapp 2c9f5a1]
   Submodule changes remain staged
```

---

## Common Workflows

### Daily Development

```bash
# Morning: Pull latest
git pull

# Work on feature
vim src/feature.ts

# Commit with checks (interactive)
git/skills/commit/scripts/commit.sh

# Repeat throughout day
```

### Documentation Updates

```bash
# Edit docs
vim README.md docs/guide.md

# Fast commit (skip checks)
git/skills/commit/scripts/commit.sh --no-verify
```

### Pre-Production Checklist

```bash
# Final commit before release
git/skills/commit/scripts/commit.sh --full-verify

# Ensure all tests pass before pushing
git push origin main
```

### Plugin Development

```bash
# Work in submodule
cd plugins/arkhe-claude-plugins
vim git/skills/commit/SKILL.md

# Commit submodule
cd ../..
git/skills/commit/scripts/commit.sh arkhe-claude-plugins

# Update root reference
# (prompted automatically)
```

---

## Tips for Effective Commits

### ✅ Good Practices

1. **Commit frequently**: Small, focused commits
2. **Run checks**: Let pre-commit checks catch errors early
3. **Use conventional commits**: Script generates proper format
4. **Keep submodules in sync**: Always update root after submodule commits
5. **Review before committing**: Check `git diff` first

### ❌ Avoid

1. **Large, mixed commits**: Split into focused commits
2. **Skipping checks unnecessarily**: Only use `--no-verify` for docs
3. **Committing broken code**: Fix pre-commit failures first
4. **Forgetting submodule updates**: Can cause deployment issues

---

## Summary

The `creating-commit` skill automates:
- ✅ Repository detection (root + submodules)
- ✅ Language-specific pre-commit checks
- ✅ Conventional commit message generation
- ✅ Submodule reference management

**Result**: Consistent, high-quality commits with minimal manual effort.

For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

*Last Updated: 2025-10-27*
