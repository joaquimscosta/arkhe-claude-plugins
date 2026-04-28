# Git Worktree Creation: Troubleshooting

Common issues and solutions for the worktree creation workflow.

---

## Quick Reference

| Issue | Cause | Solution |
|-------|-------|----------|
| Directory already exists | Previous worktree not cleaned up | Remove with `git worktree remove` |
| Branch already exists | Branch created by `/create-branch` or manually | Use different description or delete branch |
| Not git-ignored | `.worktrees/` not in `.gitignore` | Skill auto-adds it; manual: add to `.gitignore` |
| Base branch not found | Typo or branch not fetched | `git fetch` then retry |
| Worktree locked | Crash during previous operation | `git worktree unlock` then remove |
| Not a git repository | Running outside a git repo | `cd` to a git repository first |
| No changes detected | Auto-generate with clean working tree | Provide a description instead |

---

## Issue 1: Worktree Directory Already Exists

**Error**:
```
Worktree directory .worktrees/user-authentication already exists.
```

**Cause**: A previous worktree was not cleaned up, or a directory was manually created.

**Solution**:
```bash
# If it's a registered worktree, remove it properly
git worktree remove .worktrees/user-authentication

# If the directory is orphaned (not in git worktree list)
rm -rf .worktrees/user-authentication
git worktree prune
```

**Prevention**: Always clean up worktrees with `git worktree remove` when done.

---

## Issue 2: Branch Already Exists

**Error**:
```
fatal: a branch named 'feat/003-user-authentication' already exists
```

**Cause**: The branch was previously created by `/create-branch`, manually, or from a previous worktree that was removed without deleting the branch.

**Solutions**:

1. **Use a different description** to generate a different branch name
2. **Delete the existing branch** if it's no longer needed:
   ```bash
   git branch -d feat/003-user-authentication    # Safe delete (merged only)
   git branch -D feat/003-user-authentication    # Force delete
   ```
3. **The skill auto-handles this** by incrementing the number if the branch exists

---

## Issue 3: `.worktrees/` Not Git-Ignored

**Symptom**: Worktree contents appear in `git status`.

**Cause**: `.worktrees/` was not added to `.gitignore`.

**Solution**: The skill automatically detects and fixes this. If it didn't:
```bash
echo '\n# Worktrees\n.worktrees/' >> .gitignore
git add .gitignore && git commit -m "chore: add .worktrees/ to .gitignore"
```

**Verification**:
```bash
git check-ignore -v .worktrees
# .gitignore:5:.worktrees/    .worktrees
```

---

## Issue 4: Base Branch Not Found

**Error**:
```
fatal: not a valid object name: 'develop'
```

**Cause**: The specified base branch doesn't exist locally.

**Solution**:
```bash
# Fetch remote branches
git fetch origin

# Check available branches
git branch -a

# Create worktree from remote branch
git worktree add .worktrees/my-feature -b feat/001-my-feature origin/develop
```

---

## Issue 5: Worktree Locked

**Error**:
```
fatal: '.worktrees/user-authentication' is locked
```

**Cause**: A previous operation crashed or was interrupted, leaving a lock file.

**Solution**:
```bash
# Unlock the worktree
git worktree unlock .worktrees/user-authentication

# Then remove if needed
git worktree remove .worktrees/user-authentication
```

---

## Issue 6: Not a Git Repository

**Error**:
```
fatal: not a git repository (or any of the parent directories): .git
```

**Cause**: Running `/worktree` outside a git repository.

**Solution**: Navigate to a git repository first:
```bash
cd /path/to/your/repo
/worktree add my feature
```

---

## Issue 7: No Changes Detected (Auto-Generate Mode)

**Error**:
```
No arguments and no uncommitted changes. Provide a description: /worktree <description>
```

**Cause**: Running `/worktree` without arguments when the working tree is clean.

**Solutions**:

1. **Provide a description**:
   ```bash
   /worktree add my new feature
   ```

2. **Make changes first**, then run `/worktree` to auto-generate from them.

---

## Issue 8: Type Detection Not Working

**Symptom**: Expected `fix` type but got `feat`.

**Cause**: The type keyword wasn't the first matching word, or the word isn't in the keyword list.

**Recognized keywords**:
- feat: add, create, implement, new, update, improve
- fix: fix, bug, resolve, correct, repair
- refactor: refactor, rename, reorganize
- chore: remove, delete, clean, cleanup
- docs: docs, document, documentation

**Solution**: Place the type keyword at the beginning of the description:
```bash
/worktree fix the login validation    # Correctly detects "fix"
/worktree login validation issue      # Defaults to "feat" (no keyword)
```

---

## Issue 9: Keywords Too Generic

**Symptom**: Branch name like `feat/001-new-feature` which isn't descriptive.

**Cause**: Description used only generic words that get filtered as stopwords.

**Solution**: Use specific, meaningful words:
```bash
# Generic (poor)
/worktree add new feature for the system

# Specific (good)
/worktree add user authentication
/worktree add payment webhook handler
```

---

## Issue 10: Sequential Number Skips

**Symptom**: Numbers jump (e.g., 001, 002, 005).

**Cause**: Branches 003 and 004 were deleted. The numbering finds the max existing number and increments.

**This is expected behavior**. Numbers are globally unique identifiers, not a continuous sequence.

---

## Issue 11: Worktree Prune Needed

**Symptom**: `git worktree list` shows worktrees with missing directories.

**Cause**: Worktree directories were manually deleted instead of using `git worktree remove`.

**Solution**:
```bash
# Clean up stale worktree references
git worktree prune

# Verify
git worktree list
```

---

## Verification Commands

```bash
# List all worktrees
git worktree list

# Check if .worktrees/ is ignored
git check-ignore -v .worktrees

# Check current branches
git branch --list

# Check worktree status
cd .worktrees/<name> && git status

# Remove a worktree
git worktree remove .worktrees/<name>

# Prune stale worktree references
git worktree prune
```

---

*Last Updated: 2026-04-10*
