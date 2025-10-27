# Git Commit Creation: Troubleshooting

This document provides solutions to common issues when using the `creating-commit` skill.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).
For examples, see [EXAMPLES.md](EXAMPLES.md).

---

## Common Issues

### Issue 1: Pre-commit Checks Failing

**Symptom**:
```
❌ Pre-commit checks failed:
  - TypeScript compilation errors
  - Detekt found 3 issues
```

**Causes**:
- Code has compilation errors
- Linting violations
- Test failures

**Solutions**:

**Solution A: Fix the Errors** (Recommended)
```bash
# View detailed error output
npx tsc --noEmit

# Fix errors in your code
vim src/file.ts

# Try committing again
git/skills/commit/scripts/commit.sh
```

**Solution B: Skip Verification** (Use Sparingly)
```bash
# Only for documentation or minor changes
git/skills/commit/scripts/commit.sh --no-verify
```

**Warning**: Skipping checks can lead to broken code in repository.

---

### Issue 2: TypeScript Compilation Errors

**Symptom**:
```
❌ TypeScript errors found:

src/auth/login.ts:42:15 - error TS2345
  Argument of type 'string' is not assignable to parameter of type 'number'.
```

**Cause**: Type mismatch or TypeScript configuration issue

**Solutions**:

**Solution A: Fix Type Error**
```typescript
// Before (error)
function authenticate(id: number) { }
authenticate(userId);  // userId is string

// After (fixed)
authenticate(Number(userId));
// or
authenticate(parseInt(userId, 10));
```

**Solution B: Check TypeScript Config**
```bash
# Verify tsconfig.json exists
cat tsconfig.json

# Test compilation manually
npx tsc --noEmit
```

**Solution C: Install Dependencies**
```bash
# Missing type definitions
npm install --save-dev @types/node
npm install --save-dev @types/react
```

---

### Issue 3: Detekt Errors (Kotlin)

**Symptom**:
```
❌ Detekt found issues:

UserService.kt:15: MagicNumber
  Magic number found: 42

TokenValidator.kt:28: ComplexMethod
  Method complexity is 12, max allowed is 10
```

**Cause**: Code style violations in Kotlin files

**Solutions**:

**Solution A: Fix Issues**
```kotlin
// Before (magic number)
val timeout = 42

// After (named constant)
private const val DEFAULT_TIMEOUT = 42
val timeout = DEFAULT_TIMEOUT
```

**Solution B: Configure Detekt**
```yaml
# detekt.yml
complexity:
  ComplexMethod:
    threshold: 15  # Increase if needed

style:
  MagicNumber:
    ignoreNumbers: [-1, 0, 1, 2, 42]  # Whitelist specific numbers
```

**Solution C: Skip for This Commit**
```bash
git/skills/commit/scripts/commit.sh --no-verify
```

---

### Issue 4: Cargo Check Fails (Rust)

**Symptom**:
```
❌ Cargo check failed:

error[E0308]: mismatched types
  --> src/parser.rs:42:5
   |
42 |     "hello"
   |     ^^^^^^^ expected `i32`, found `&str`
```

**Cause**: Type error or compilation issue in Rust code

**Solutions**:

**Solution A: Fix Rust Error**
```rust
// Before (error)
fn get_value() -> i32 {
    "hello"  // Wrong type
}

// After (fixed)
fn get_value() -> i32 {
    42
}
```

**Solution B: Run Cargo Manually**
```bash
# Get detailed error information
cargo check

# Run with verbose output
cargo check --verbose

# Fix errors then commit
git/skills/commit/scripts/commit.sh
```

---

### Issue 5: Submodule Conflicts

**Symptom**:
```
❌ Submodule has conflicts:

plugins/arkhe-claude-plugins:
  Conflicting changes between local and remote
```

**Cause**: Submodule HEAD differs from what root expects

**Solutions**:

**Solution A: Update Submodule**
```bash
# Navigate to submodule
cd plugins/arkhe-claude-plugins

# Pull latest
git pull origin main

# Return to root
cd ../..

# Try commit again
git/skills/commit/scripts/commit.sh
```

**Solution B: Reset Submodule**
```bash
# Reset submodule to commit referenced by root
git submodule update --init --recursive

# Then commit
git/skills/commit/scripts/commit.sh
```

**Solution C: Commit Submodule First**
```bash
# Explicitly commit to submodule
git/skills/commit/scripts/commit.sh arkhe-claude-plugins

# Then update root
# (prompted automatically)
```

---

### Issue 6: Script Not Found

**Symptom**:
```
bash: git/skills/commit/scripts/commit.sh: No such file or directory
```

**Causes**:
- Wrong working directory
- Plugin not installed
- File permissions

**Solutions**:

**Solution A: Navigate to Project Root**
```bash
# Check current directory
pwd

# Find project root
cd /path/to/your/project

# Verify file exists
ls -la git/skills/commit/scripts/commit.sh
```

**Solution B: Reinstall Plugin**
```bash
/plugin uninstall git@arkhe-claude-plugins
/plugin install git@arkhe-claude-plugins
```

**Solution C: Fix Permissions**
```bash
chmod +x git/skills/commit/scripts/commit.sh
chmod +x git/skills/commit/scripts/common.sh
```

---

### Issue 7: No Changes to Commit

**Symptom**:
```
❌ No changes detected in any repository
```

**Cause**: All changes are already committed or not staged

**Solutions**:

**Solution A: Stage Changes First**
```bash
# View unstaged changes
git status

# Stage files
git add src/file.ts

# Then commit
git/skills/commit/scripts/commit.sh
```

**Solution B: Check for Untracked Files**
```bash
# View all files including untracked
git status

# Add untracked files
git add .

# Commit
git/skills/commit/scripts/commit.sh
```

---

### Issue 8: Commit Message Validation Fails

**Symptom**:
```
❌ Commit message validation failed:
  - Subject line too long (82 characters, max 72)
  - Missing blank line after subject
```

**Cause**: Generated message doesn't meet repository's commit-msg hook requirements

**Solutions**:

**Solution A: Edit Message**
```bash
# When prompted, choose 'e' to edit
Proceed? (y/n/e): e

# Editor opens, modify message to meet requirements
```

**Solution B: Bypass Hook** (If Confident)
```bash
git/skills/commit/scripts/commit.sh --no-verify
```

**Note**: This skips all hooks, including commit-msg validation

---

### Issue 9: Wrong Repository Selected

**Symptom**:
Committed to root when intended to commit to submodule (or vice versa).

**Cause**: Interactive mode selected wrong repository

**Solutions**:

**Solution A: Undo Last Commit**
```bash
# Undo commit but keep changes
git reset --soft HEAD~1

# Re-run with explicit scope
git/skills/commit/scripts/commit.sh arkhe-claude-plugins
```

**Solution B: Use Explicit Scope**
```bash
# Always specify scope to avoid selection
git/skills/commit/scripts/commit.sh root
git/skills/commit/scripts/commit.sh arkhe-claude-plugins
```

---

### Issue 10: Branch Protection Warning

**Symptom**:
```
⚠️  Warning: You are committing to a protected branch (main)
   Consider creating a feature branch instead.

Proceed anyway? (y/n):
```

**Cause**: Attempting to commit directly to protected branch

**Solutions**:

**Solution A: Create Feature Branch** (Recommended)
```bash
# Create and checkout feature branch
/create-branch add my feature

# Then commit
git/skills/commit/scripts/commit.sh
```

**Solution B: Proceed with Caution**
```bash
# Only if you have permission
Proceed anyway? y
```

**Best Practice**: Always work on feature branches, not directly on main/master

---

### Issue 11: Submodule Not Initialized

**Symptom**:
```
❌ Submodule directory exists but git repository not initialized:
   plugins/arkhe-claude-plugins
```

**Cause**: Submodule cloned but not initialized

**Solutions**:

**Solution A: Initialize Submodule**
```bash
git submodule update --init --recursive
```

**Solution B: Clone with Submodules**
```bash
# When first cloning repository
git clone --recursive <repository-url>
```

---

### Issue 12: Multiple Git Instances Detected

**Symptom**:
```
⚠️  Warning: Multiple .git directories detected in parent path
   This may cause unexpected behavior
```

**Cause**: Nested git repositories (unusual setup)

**Solutions**:

**Solution A: Verify Repository Structure**
```bash
# Find all .git directories
find . -name ".git" -type d

# Expected:
# ./git (root)
# ./plugins/submodule/.git (submodule)
```

**Solution B: Use Explicit Paths**
```bash
# Specify exact repository
cd /path/to/intended/repository
../../git/skills/commit/scripts/commit.sh
```

---

## Quick Reference

### Error Messages

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `Pre-commit checks failed` | Code errors | Fix errors or use `--no-verify` |
| `No such file or directory` | Wrong directory | Navigate to project root |
| `Permission denied` | Not executable | `chmod +x scripts/commit.sh` |
| `No changes detected` | Nothing staged | `git add` files first |
| `Submodule conflicts` | Outdated submodule | `git submodule update` |
| `TypeScript errors` | Type mismatch | Fix types or check config |
| `Detekt issues` | Code style | Fix issues or configure detekt |

### Verification Commands

```bash
# Check git status
git status

# View staged changes
git diff --cached

# List submodules
git submodule status

# Test TypeScript
npx tsc --noEmit

# Test Kotlin (Detekt)
./gradlew detekt

# Test Rust
cargo check

# Verify script exists
ls -la git/skills/commit/scripts/commit.sh
```

### Debugging

**Enable Verbose Output**:
```bash
# Run script with bash -x for debugging
bash -x git/skills/commit/scripts/commit.sh
```

**Check Script Logs**:
```bash
# If script creates logs
cat /tmp/commit-script.log
```

---

## Prevention Tips

1. **Run `git status` before committing**: Know what you're committing
2. **Stage changes deliberately**: Use `git add` selectively
3. **Keep submodules updated**: Run `git submodule update` regularly
4. **Fix pre-commit errors**: Don't routinely skip checks
5. **Use feature branches**: Avoid committing directly to main
6. **Test locally first**: Run checks manually before committing
7. **Keep dependencies updated**: Ensure build tools are installed

---

## Getting Help

If issues persist:

1. **Check Skill Documentation**: Review [SKILL.md](SKILL.md) for usage
2. **Review Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
3. **Verify Installation**:
   ```bash
   /plugin list
   # Ensure git@arkhe-claude-plugins is installed
   ```
4. **Reinstall Plugin**:
   ```bash
   /plugin uninstall git@arkhe-claude-plugins
   /plugin install git@arkhe-claude-plugins
   ```
5. **Check Git Status**:
   ```bash
   git status
   git log --oneline -5
   git submodule status
   ```

---

*Last Updated: 2025-10-27*
