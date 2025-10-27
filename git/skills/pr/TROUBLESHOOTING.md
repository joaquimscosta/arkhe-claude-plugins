# GitHub Pull Request Creation: Troubleshooting

This document provides solutions to common issues when using the `creating-pr` skill.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).
For examples, see [EXAMPLES.md](EXAMPLES.md).

---

## Common Issues

### Issue 1: GitHub CLI Not Authenticated

**Symptom**:
```
❌ Error: gh: Not authenticated

To authenticate, please run: gh auth login
```

**Cause**: GitHub CLI not logged in

**Solutions**:

**Solution A: Authenticate with GitHub**
```bash
gh auth login
```

**Interactive prompts**:
```
? What account do you want to log into? GitHub.com
? What is your preferred protocol for Git operations? HTTPS/SSH
? Authenticate Git with your GitHub credentials? Yes
? How would you like to authenticate GitHub CLI? Login with a web browser

! First copy your one-time code: XXXX-XXXX
Press Enter to open github.com in your browser...
```

**Verification**:
```bash
gh auth status
```

**Expected output**:
```
✓ Logged in to github.com as username
✓ Git operations protocol: https/ssh
✓ Token: *******************
```

---

### Issue 2: Branch Not Pushed to Remote

**Symptom**:
```
❌ Error: Branch 'feat/003-user-auth' does not exist on remote

The script should have pushed it automatically, but failed.
```

**Cause**: Network issue or permission problem prevented push

**Solutions**:

**Solution A: Manual Push**
```bash
git push -u origin feat/003-user-auth
```

**Solution B: Check Remote Access**
```bash
# Verify remote URL
git remote -v

# Test connection
git fetch origin

# If permission denied, check SSH keys or HTTPS credentials
```

**Solution C: Check Branch Exists Locally**
```bash
# List local branches
git branch

# Ensure you're on the correct branch
git checkout feat/003-user-auth
```

---

### Issue 3: PR Already Exists

**Symptom**:
```
Found existing PR for this branch:
#42: feat(auth): add user authentication
```

**Cause**: PR was already created for this branch

**Solutions**:

**Solution A: Update Existing PR** (Recommended)
```
Choose option 1 when prompted

This will push your latest commits and
update the existing PR automatically.
```

**Solution B: View Existing PR**
```
Choose option 2 to open PR in browser
```

**Solution C: Close Old PR and Create New**
```bash
# Close existing PR
gh pr close 42

# Create new PR
git/skills/pr/scripts/pr.sh
```

**Note**: Updating is usually better than creating a new PR

---

### Issue 4: Permission Denied (Fork vs Origin)

**Symptom**:
```
❌ Error: Permission denied (publickey)
fatal: Could not read from remote repository

or

❌ Error: You don't have push access to user/repo
```

**Cause**: Trying to push to repository you don't have write access to

**Solutions**:

**Solution A: Push to Your Fork** (Correct workflow)
```bash
# Add your fork as remote if not already added
git remote add fork git@github.com:yourname/repo.git

# Push to your fork
git push -u fork feat/003-user-auth

# Create PR from fork to upstream
gh pr create --repo user/repo --head yourname:feat/003-user-auth
```

**Solution B: Verify Remote Configuration**
```bash
# Check remotes
git remote -v

# Should show:
origin  git@github.com:user/repo.git (upstream)
fork    git@github.com:yourname/repo.git (your fork)
```

**Solution C: Fix SSH Keys**
```bash
# Test SSH connection
ssh -T git@github.com

# If fails, add SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add key to GitHub: Settings → SSH Keys
```

---

### Issue 5: Base Branch Not Found

**Symptom**:
```
❌ Error: Base branch 'develop' not found in remote repository
```

**Cause**: Specified base branch doesn't exist on remote

**Solutions**:

**Solution A: Check Available Branches**
```bash
# List remote branches
git branch -r

# Common branch names:
# main, master, develop, staging, production
```

**Solution B: Use Correct Base Branch**
```bash
# If trying to use 'develop' but it doesn't exist, use 'main'
git/skills/pr/scripts/pr.sh --base main
```

**Solution C: Create Base Branch First** (If Needed)
```bash
# Checkout main
git checkout main

# Create and push develop branch
git checkout -b develop
git push -u origin develop

# Now create PR to develop
git checkout feat/003-user-auth
git/skills/pr/scripts/pr.sh --base develop
```

---

### Issue 6: Protected Branch Error

**Symptom**:
```
❌ Error: Cannot create PR from protected branch 'main'

Pull requests must be created from feature branches.
```

**Cause**: Attempting to create PR while on main/master branch

**Solutions**:

**Solution A: Create Feature Branch**
```bash
# From main, create feature branch
/create-branch add user authentication

# Make changes
vim src/file.ts

# Commit
/commit

# Now create PR
/create-pr
```

**Solution B: Move Changes to Feature Branch**
```bash
# If you already made changes on main
git checkout -b feat/003-user-auth

# Commit changes
/commit

# Create PR
/create-pr
```

---

### Issue 7: No Commits on Branch

**Symptom**:
```
❌ Error: No commits found on branch ahead of base

Cannot create PR without changes.
```

**Cause**: Feature branch has no commits that aren't in base branch

**Solutions**:

**Solution A: Ensure Changes Are Committed**
```bash
# Check for uncommitted changes
git status

# If changes exist, commit them
git add .
/commit

# Then create PR
/create-pr
```

**Solution B: Check Branch Status**
```bash
# Compare with base
git log main..HEAD

# Should show commits
# If empty, branch has no unique commits
```

---

### Issue 8: gh Command Not Found

**Symptom**:
```
bash: gh: command not found
```

**Cause**: GitHub CLI not installed

**Solutions**:

**Solution A: Install GitHub CLI (macOS)**
```bash
brew install gh
```

**Solution B: Install GitHub CLI (Linux)**
```bash
# Debian/Ubuntu
sudo apt install gh

# Fedora/RHEL
sudo dnf install gh
```

**Solution C: Install GitHub CLI (Windows)**
```powershell
winget install --id GitHub.cli
```

**Verification**:
```bash
gh --version
```

---

### Issue 9: Script Not Found

**Symptom**:
```
bash: git/skills/pr/scripts/pr.sh: No such file or directory
```

**Causes & Solutions**:

**Solution A: Navigate to Project Root**
```bash
# Check current directory
pwd

# Navigate to project root
cd /path/to/your/project

# Verify file exists
ls -la git/skills/pr/scripts/pr.sh
```

**Solution B: Reinstall Plugin**
```bash
/plugin uninstall git@arkhe-claude-plugins
/plugin install git@arkhe-claude-plugins
```

**Solution C: Fix Permissions**
```bash
chmod +x git/skills/pr/scripts/pr.sh
chmod +x git/skills/pr/scripts/common.sh
```

---

### Issue 10: Network Timeout

**Symptom**:
```
❌ Error: Operation timed out
fatal: unable to access 'https://github.com/user/repo.git/'
```

**Cause**: Network connection issues

**Solutions**:

**Solution A: Check Network Connection**
```bash
# Test GitHub connectivity
ping github.com

# Test HTTPS
curl -I https://github.com
```

**Solution B: Use SSH Instead of HTTPS**
```bash
# Switch remote to SSH
git remote set-url origin git@github.com:user/repo.git

# Retry
git/skills/pr/scripts/pr.sh
```

**Solution C: Increase Timeout**
```bash
# Increase git timeout
git config --global http.postBuffer 524288000
git config --global http.timeout 300
```

---

### Issue 11: Diverged Branches

**Symptom**:
```
❌ Error: Local branch has diverged from remote

Local and remote have different commits.
```

**Cause**: Branch history differs between local and remote

**Solutions**:

**Solution A: Pull and Merge**
```bash
git pull origin feat/003-user-auth
# Resolve any conflicts
git push

# Then create PR
git/skills/pr/scripts/pr.sh
```

**Solution B: Rebase** (Cleaner history)
```bash
git pull --rebase origin feat/003-user-auth
# Resolve conflicts if any
git push --force-with-lease

# Then create PR
git/skills/pr/scripts/pr.sh
```

**Solution C: Force Push** (Use with caution)
```bash
# Only if you're sure local is correct
git push --force origin feat/003-user-auth

# Then create PR
git/skills/pr/scripts/pr.sh
```

---

### Issue 12: Rate Limit Exceeded

**Symptom**:
```
❌ Error: API rate limit exceeded

GitHub API rate limit: 60 requests per hour (unauthenticated)
```

**Cause**: Too many API requests without authentication or with low limit

**Solutions**:

**Solution A: Authenticate with gh**
```bash
gh auth login
```

Authenticated users get 5,000 requests/hour instead of 60.

**Solution B: Wait for Rate Limit Reset**
```bash
# Check rate limit status
gh api rate_limit

# Shows when limit resets
```

**Solution C: Use Personal Access Token**
```bash
# Create token at: github.com/settings/tokens
# Use with gh auth login
```

---

## Quick Reference

### Error Messages

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `Not authenticated` | gh not logged in | `gh auth login` |
| `Branch not on remote` | Not pushed | `git push -u origin <branch>` |
| `PR already exists` | Duplicate attempt | Update existing PR (option 1) |
| `Permission denied` | No write access | Push to fork, create from fork |
| `Base branch not found` | Invalid base | Check with `git branch -r` |
| `Protected branch` | On main/master | Create feature branch first |
| `gh: command not found` | gh not installed | `brew install gh` |
| `No commits` | No changes | Commit changes first |

### Verification Commands

```bash
# Check GitHub CLI
gh auth status
gh --version

# Check git status
git status
git log main..HEAD

# Check remotes
git remote -v
git branch -r

# Check existing PRs
gh pr list
gh pr status

# Verify script
ls -la git/skills/pr/scripts/pr.sh
```

### Debugging

**Enable Verbose Output**:
```bash
# Run with debugging
bash -x git/skills/pr/scripts/pr.sh
```

**Check GitHub CLI**:
```bash
# Test gh commands
gh repo view
gh pr list
```

---

## Prevention Tips

1. **Authenticate gh first**: Run `gh auth login` once
2. **Work on feature branches**: Never on main/master
3. **Commit before creating PR**: Ensure changes are committed
4. **Check for existing PRs**: Use `gh pr list` first
5. **Keep branches synced**: Pull regularly from base branch
6. **Use SSH keys**: More reliable than HTTPS for push operations

---

## Getting Help

If issues persist:

1. **Check Skill Documentation**: Review [SKILL.md](SKILL.md)
2. **Review Examples**: See [EXAMPLES.md](EXAMPLES.md)
3. **Verify Installation**:
   ```bash
   gh --version
   /plugin list
   ```
4. **Check GitHub Status**: https://www.githubstatus.com/
5. **Reinstall Plugin**:
   ```bash
   /plugin uninstall git@arkhe-claude-plugins
   /plugin install git@arkhe-claude-plugins
   ```

---

*Last Updated: 2025-10-27*
