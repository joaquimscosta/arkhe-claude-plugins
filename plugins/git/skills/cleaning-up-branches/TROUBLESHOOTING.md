# Branch Cleanup Troubleshooting

Common issues and solutions for the `cleaning-up-branches` skill.

## Cannot Delete Current Branch

**Error:**
```
error: Cannot delete branch 'feat/001-user-auth' checked out at '/path/to/repo'
```

**Cause:** You are currently on the branch you're trying to delete.

**Solution:**
```bash
# Switch to the base branch first
git checkout main
# Then run cleanup again
/cleanup-branches
```

The skill automatically excludes the current branch from deletion candidates, but if you manually attempt to delete it, git will refuse.

## Remote Branch Deletion Permission Denied

**Error:**
```
remote: Permission to org/repo.git denied
fatal: unable to delete 'feat/001-user-auth': remote ref does not exist
```

**Cause:** You don't have push access to the remote, or the branch was already deleted on the remote.

**Solution:**
1. Verify you have push access:
   ```bash
   gh repo view --json viewerPermission
   ```
2. If the branch was already deleted remotely, run:
   ```bash
   git fetch --prune
   ```
3. If you lack permissions, ask a repository admin to delete the remote branches.

## Squash-Merged Branch Not Detected Automatically

**Symptom:** A branch shows up as "stale unmerged" even though its changes were merged via squash-and-merge on GitHub. It does NOT appear in the "SQUASH-MERGED BRANCHES" section.

**Note:** As of v1.1.0, most squash-merged branches are detected automatically using `git cherry` (patch-id comparison). However, edge cases exist.

**Cause of false negatives:**
- The squash commit on base was **amended** after merge, changing the patch-id
- Only **some** commits were cherry-picked (partial merge)
- The branch was **rebased and modified** before squash-merge

**Solution:** Verify manually and force-delete if confirmed:
```bash
# Check git cherry output — all '-' lines means squash-merged
git cherry main <branch-name>

# Cross-reference with GitHub
gh pr list --state merged --head <branch-name>

# If confirmed squash-merged, safe to delete
git branch -D <branch-name>          # Force-delete local
git push origin --delete <branch-name> # Delete remote
```

## Protected Branch Errors

**Error:**
```
error: refusing to delete the current branch 'main'
```

**Cause:** Attempting to delete a protected branch (main, master, or the specified base branch).

**Solution:** The skill automatically excludes `main`, `master`, and the `--base` branch from deletion. If you see this error, it indicates an edge case — report it as a bug.

## Base Branch Not Found

**Error:**
```
fatal: Not a valid object name: 'main'
```

**Cause:** The specified base branch doesn't exist in the repository.

**Solution:**
```bash
# Check available branches
git branch -a

# Use the correct base branch
/cleanup-branches --base develop
/cleanup-branches --base master
```

## Network Errors During Remote Operations

**Error:**
```
fatal: unable to access 'https://github.com/org/repo.git/': Could not resolve host
```

**Cause:** No network access or the remote URL is incorrect.

**Solution:**
1. Check network connectivity
2. Verify the remote URL:
   ```bash
   git remote -v
   ```
3. Run without `--remote` to clean up local branches only:
   ```bash
   /cleanup-branches
   ```

## xargs: Argument List Too Long

**Error:**
```
xargs: argument list too long
```

**Cause:** Extremely large number of branches to delete.

**Solution:** Delete branches in batches:
```bash
# Delete first 50 merged branches
git branch --merged main | grep -v main | head -50 | xargs git branch -d
# Repeat as needed
```

## Branch Deleted Locally But Still Shows on Remote

**Symptom:** After deleting local merged branches, you still see them on the remote.

**Cause:** Local deletion does not affect remote branches. The `--remote` flag is required for remote cleanup.

**Solution:**
```bash
/cleanup-branches --remote
```

## Version

1.1.0
