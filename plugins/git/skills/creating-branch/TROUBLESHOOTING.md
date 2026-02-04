# Git Branch Creation: Troubleshooting

This document provides solutions to common issues when using the `creating-branch` skill.

---

## Common Issues

### Issue 1: Branch Already Exists

**Symptom**:
```
fatal: A branch named 'feat/003-user-auth' already exists.
```

**Cause**:
- A branch with the same name already exists (locally or remotely)
- Attempting to recreate a previously deleted branch with the same number

**Solutions**:

**Solution A: Use Different Description**
```bash
# Instead of:
/create-branch add user authentication

# Try:
/create-branch add user auth system
→ feat/003-user-auth-system (different keywords)
```

**Solution B: Delete Existing Branch**
```bash
# Delete local branch
git branch -d feat/003-user-auth

# Or force delete
git branch -D feat/003-user-auth

# Delete remote branch (if exists)
git push origin --delete feat/003-user-auth

# Then recreate
/create-branch add user authentication
```

**Solution C: Let Sequential Numbering Handle It**
The script will automatically find the next available number:
```bash
# Existing: feat/003-user-auth
# New command: /create-branch add user authentication
# Result: feat/004-user-authentication (incremented number)
```

---

### Issue 2: Invalid Characters in Branch Name

**Symptom**:
```
fatal: 'feat/003-user@auth' is not a valid branch name.
```

**Cause**:
- Description contains special characters that are not allowed in git branch names
- Characters like `@`, `#`, `~`, `^`, `:`, `\`, `*`, `?`, `[`, `]`

**Solution**:

The script automatically sanitizes branch names, but if you encounter this error:

**Remove special characters from description**:
```bash
# Instead of:
/create-branch add user@domain authentication

# Use:
/create-branch add user domain authentication
→ feat/003-user-domain
```

**Avoid punctuation**:
```bash
# Instead of:
/create-branch fix: login error!

# Use:
/create-branch fix login error
→ fix/003-login-error
```

---

### Issue 3: Script Not Found or Permission Denied

**Symptom**:
```
bash: /create-branch: No such file or directory
```
or
```
bash: /create-branch: Permission denied
```

**Causes & Solutions**:

**Cause A: Wrong Working Directory**

**Solution**: Run from project root
```bash
# Check current directory
pwd

# Navigate to project root
cd /path/to/arkhe-claude-plugins

# Then run
/create-branch "add user auth"
```

**Cause B: Script Not Executable**

**Solution**: Make script executable
```bash
chmod +x /create-branch
chmod +x git/skills/creating-branch/shared utilities
```

**Cause C: File Doesn't Exist**

**Solution**: Verify installation
```bash
# Check if skill files exist
ls -la plugins/git/skills/creating-branch/

# Expected output:
# SKILL.md  WORKFLOW.md  EXAMPLES.md  TROUBLESHOOTING.md
```

If files are missing, reinstall the git plugin:
```bash
/plugin uninstall git@arkhe-claude-plugins
/plugin install git@arkhe-claude-plugins
```

---

### Issue 4: Type Detection Not Working

**Symptom**:
Branch is created as `feat/` instead of expected type (e.g., `fix/`).

**Cause**:
- Type keyword not recognized
- Keyword appears later in description
- Typo in type keyword

**Solutions**:

**Solution A: Use Recognized Keywords**

Supported keywords by type:
- **feat**: add, create, implement, new, update, improve
- **fix**: fix, bug, resolve, correct, repair
- **refactor**: refactor, rename, reorganize
- **chore**: remove, delete, clean, cleanup
- **docs**: docs, document, documentation

```bash
# Instead of:
/create-branch solve the login issue
→ feat/001-solve-login  # "solve" not recognized

# Use:
/create-branch fix the login issue
→ fix/001-login-issue  # "fix" recognized
```

**Solution B: Put Type Keyword First**

The script checks keywords in order:
```bash
# Good:
/create-branch fix login validation error
→ fix/001-login-validation

# Less reliable:
/create-branch login validation error fix
→ feat/001-login-validation  # "fix" found too late, defaults to feat
```

**Solution C: Accept Default Type**

If no keyword is found, `feat` is used as default:
```bash
/create-branch user authentication
→ feat/001-user-authentication
```

This is acceptable for most feature work.

---

### Issue 5: Sequential Numbering Skips Numbers

**Symptom**:
Expected `feat/003-` but got `feat/005-`.

**Cause**:
- Branches were deleted but their numbers were the highest
- Mixed local and remote branches
- Manual branch creation with higher numbers

**Explanation**:

This is **expected behavior**. The script finds the highest number across all existing branches and increments:

```bash
# Existing branches:
feat/001-user-auth
feat/002-dashboard
fix/004-login-bug  # Note: 003 was deleted

# New branch:
/create-branch add payment
→ feat/005-payment  # Next after 004, not 003
```

**Solutions**:

**Solution A: Accept the Gap** (Recommended)

Gaps in numbering are acceptable and don't cause issues:
- Sequential order is maintained (005 > 004)
- Each branch has unique identifier
- History is preserved

**Solution B: Manually Create with Specific Number**

If you need a specific number:
```bash
git checkout -b feat/003-payment
```

Note: This bypasses the automatic numbering system.

**Solution C: Reset Numbering** (Not Recommended)

Only if absolutely necessary and no remote branches exist:
```bash
# Delete all local branches
git branch | grep -v "main\|master" | xargs git branch -D

# Start fresh
/create-branch add first feature
→ feat/001-first-feature
```

**Warning**: This destroys branch history.

---

### Issue 6: Keywords Too Generic

**Symptom**:
Branch names are not descriptive enough.

**Example**:
```bash
/create-branch add new feature
→ feat/001-new-feature  # Too generic
```

**Cause**:
Description uses generic terms without specifics.

**Solutions**:

**Be Specific**:
```bash
# Instead of:
/create-branch add new feature
→ feat/001-new-feature

# Use:
/create-branch add user authentication
→ feat/001-user-authentication
```

**Include Context**:
```bash
# Instead of:
/create-branch fix bug
→ fix/002-bug

# Use:
/create-branch fix login validation bug
→ fix/002-login-validation
```

**Use Domain Terms**:
```bash
# Instead of:
/create-branch update the system
→ feat/003-update-system

# Use:
/create-branch update payment gateway
→ feat/003-payment-gateway
```

---

### Issue 7: Branch Name Too Long

**Symptom**:
Expected longer branch name, but got shortened version.

**Example**:
```bash
/create-branch add comprehensive user authentication system with OAuth2 and JWT
→ feat/001-user-authentication  # Expected more keywords
```

**Cause**:
The script intentionally limits branch names to 2-3 meaningful keywords for readability.

**Explanation**:

This is **expected behavior** for good git practices:
- Short branch names are easier to read
- Terminal commands are more manageable
- Tab completion works better
- PR titles remain concise

**Solutions**:

**Solution A: Accept Short Name** (Recommended)

Short names are better for git workflows:
```bash
feat/001-user-authentication  # Clear and concise
```

Use commit messages and PR descriptions for details:
```bash
git commit -m "feat: implement comprehensive OAuth2 and JWT authentication"
```

**Solution B: Manual Branch Creation**

If you absolutely need a longer name:
```bash
git checkout -b feat/001-user-authentication-oauth2-jwt
```

**Warning**: This bypasses the naming convention.

---

### Issue 8: Specs Not Detected

**Symptom**:
Branch creation doesn't offer spec selection even though specs exist.

**Causes & Solutions**:

**Cause A: Missing .arkhe.yaml**

**Solution**: Create configuration or run `/develop` first
```bash
# Check for config
cat .arkhe.yaml

# If missing, create manually
echo "develop:
  specs_dir: arkhe/specs" > .arkhe.yaml
```

**Cause B: Empty specs directory**

**Solution**: Run `/develop` to create a spec first
```bash
/develop add user authentication --plan-only
# Creates arkhe/specs/01-user-auth/

# Now /create-branch will detect it
/create-branch
```

**Cause C: Custom specs_dir not matching**

**Solution**: Verify specs_dir in .arkhe.yaml matches actual location
```bash
# Check config
grep specs_dir .arkhe.yaml

# Verify directory exists
ls -la arkhe/specs/  # or your custom path
```

**Cause D: Spec directories have no subdirectories**

**Solution**: Ensure specs are proper directories
```bash
# Specs must be directories, not files
ls -la arkhe/specs/
# Should show:
# drwxr-xr-x  01-user-auth/
# drwxr-xr-x  02-dashboard/
```

---

### Issue 9: Wrong Git Repository

**Symptom**:
```
fatal: not a git repository (or any of the parent directories): .git
```

**Cause**:
Not running from within a git repository.

**Solutions**:

**Solution A: Navigate to Git Repository**

```bash
# Check if in git repo
git status

# If not, navigate to your project
cd /path/to/your/project

# Verify
git status
```

**Solution B: Initialize Git Repository**

If this is a new project:
```bash
# Initialize repository
git init

# Add remote (if needed)
git remote add origin <url>

# Then create branch
/create-branch add initial feature
```

---

### Issue 10: Script Fails Silently

**Symptom**:
No error message, but branch is not created.

**Causes & Solutions**:

**Cause A: Shell Not Supporting Script**

**Solution**: Use bash explicitly
```bash
bash /create-branch "add user auth"
```

**Cause B: Missing Dependencies**

**Solution**: Verify git is installed
```bash
# Check git installation
git --version

# If not installed (macOS):
xcode-select --install

# If not installed (Linux):
sudo apt-get install git  # Debian/Ubuntu
sudo yum install git       # RHEL/CentOS
```

**Cause C: Script Syntax Error**

**Solution**: Check script integrity
```bash
# Verify script syntax
bash -n /create-branch

# If errors appear, reinstall plugin
/plugin uninstall git@arkhe-claude-plugins
/plugin install git@arkhe-claude-plugins
```

---

### Issue 11: Branch Created but Not Checked Out

**Symptom**:
Branch is created but you're still on the previous branch.

**Cause**:
Script execution was interrupted or failed after branch creation.

**Solutions**:

**Solution A: Manually Checkout**
```bash
# List branches
git branch

# Checkout the new branch
git checkout feat/003-user-authentication
```

**Solution B: Verify Current Branch**
```bash
# Check current branch
git branch --show-current

# Or
git status
```

**Solution C: Recreate with Checkout**
```bash
# Delete the branch
git branch -d feat/003-user-authentication

# Recreate
/create-branch add user authentication
```

---

### Issue 12: Conflict with Remote Branch

**Symptom**:
```
fatal: A branch named 'feat/003-user-auth' already exists on remote.
```

**Cause**:
Branch with same name exists on remote repository.

**Solutions**:

**Solution A: Fetch and Check**
```bash
# Fetch remote branches
git fetch origin

# List remote branches
git branch -r

# If branch exists remotely, checkout instead
git checkout feat/003-user-auth
```

**Solution B: Use Different Description**
```bash
# Create with different keywords
/create-branch add user authentication system
→ feat/004-user-authentication-system
```

**Solution C: Delete Remote Branch** (If You Own It)
```bash
# Delete remote branch
git push origin --delete feat/003-user-auth

# Recreate locally
/create-branch add user authentication
```

---

## Quick Reference

### Error Messages

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `fatal: A branch named '...' already exists` | Branch exists | Use different description or delete existing |
| `fatal: not a git repository` | Not in git repo | Navigate to git project |
| `Permission denied` | Script not executable | `chmod +x the branch creation workflow` |
| `No such file or directory` | Wrong working directory | Navigate to project root |
| `fatal: '...' is not a valid branch name` | Invalid characters | Remove special characters from description |
| No spec selection offered | Missing `.arkhe.yaml` or empty specs | Run `/develop` first or create config manually |

### Verification Commands

```bash
# Check current branch
git branch --show-current

# List all branches
git branch -a

# Check skill files
ls -la plugins/git/skills/creating-branch/

# Verify git repository
git status

# Check for SDLC-develop specs
cat .arkhe.yaml
ls -la arkhe/specs/
```

### Debugging

**Enable Verbose Output**:
```bash
# Run script directly with bash -x for debugging
bash -x /create-branch "add user auth"
```

**Check Script Execution**:
```bash
# Verify script runs
bash /create-branch --help
```

---

## Getting Help

If issues persist:

1. **Verify Installation**:
   ```bash
   /plugin list
   # Ensure git@arkhe-claude-plugins is installed
   ```

2. **Reinstall Plugin**:
   ```bash
   /plugin uninstall git@arkhe-claude-plugins
   /plugin install git@arkhe-claude-plugins
   ```

3. **Check Git Status**:
   ```bash
   git status
   git branch -a
   ```

---

## Prevention Tips

1. **Use Clear Descriptions**: Specific, descriptive branch names prevent confusion
2. **Check Existing Branches**: Run `git branch` before creating new branches
3. **Keep Branch Names Short**: Let the script handle keyword extraction
4. **Use Conventional Keywords**: Stick to recognized type keywords
5. **Delete Merged Branches**: Clean up after merging to prevent clutter
6. **Fetch Regularly**: Stay synced with remote branches

---

*Last Updated: 2025-10-27*
