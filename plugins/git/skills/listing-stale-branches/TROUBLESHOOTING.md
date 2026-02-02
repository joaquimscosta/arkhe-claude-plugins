# Stale Branch Detection Troubleshooting

Common issues and solutions when listing stale branches.

## Common Issues

### Issue 1: "Not a git repository"

**Symptom:**
```
Error: fatal: not a git repository (or any of the parent directories): .git
```

**Cause:**
- Not in a git-initialized directory
- Working in a directory outside any git repository

**Solution:**
```bash
# Verify you're in a git repository
git rev-parse --is-inside-work-tree

# Navigate to your project
cd /path/to/your/project
```

**Prevention:**
- Always run `/stale-branches` from within a git repository

---

### Issue 2: Base branch does not exist

**Symptom:**
```
Error: Branch 'main' does not exist
```

**Cause:**
- The repository uses `master` instead of `main` (or another branch name)
- The base branch was deleted or renamed

**Solution:**
```bash
# Check which branches exist
git branch -a

# Use the correct base branch
/stale-branches --base master
/stale-branches --base develop
```

**Prevention:**
- The skill automatically falls back to `master` if `main` doesn't exist
- For non-standard base branches, always use `--base`

---

### Issue 3: Squash-merged branches appear as "unmerged"

**Symptom:**
```
Branch 'feat/my-feature' appears in INACTIVE UNMERGED section
but was already merged via GitHub squash-and-merge
```

**Cause:**
- `git branch --merged` only detects branches merged with standard merge commits
- Squash merges create a new commit on the base branch that is not an ancestor of the feature branch
- GitHub's "Squash and merge" button triggers this behavior

**Solution:**
This is a fundamental limitation of git's merge detection. To verify if a squash-merged branch's changes are already in base:

```bash
# Check if the branch's diff is empty against base
git diff main...feat/my-feature --stat

# If diff is empty or shows only trivial changes, the work is in main

# Alternative: check if PR was merged on GitHub
gh pr list --state merged --head feat/my-feature
```

**Prevention:**
- Review the "INACTIVE UNMERGED" section carefully — some branches may have been squash-merged
- Use `gh pr list --state merged` to cross-reference with GitHub
- Consider using standard merge commits instead of squash merges if branch cleanup is important

---

### Issue 4: No stale branches found

**Symptom:**
```
No merged branches found.
No inactive unmerged branches found.
All branches are active and up to date.
```

**Cause:**
- All branches are active (commits within the threshold period)
- All merged branches were already cleaned up
- Threshold is too generous (e.g., 12 months)

**Solution:**
```bash
# Try a shorter threshold
/stale-branches --threshold 1

# List all branches to see what exists
git branch -a
```

**Prevention:**
- Start with the default 3-month threshold
- Use `--threshold 1` for stricter cleanup policies

---

### Issue 5: Remote fetch fails

**Symptom:**
```
Warning: Could not reach remote 'origin'
fatal: Could not read from remote repository
```

**Cause:**
- No network connectivity
- Remote URL is invalid or has changed
- SSH key or authentication issue

**Solution:**
```bash
# Check remote configuration
git remote -v

# Test connectivity
git ls-remote origin

# Fix SSH issues
ssh -T git@github.com

# Fix HTTPS authentication
gh auth login
```

**Prevention:**
- Ensure network access before using `--remote`
- The skill gracefully skips remote analysis if fetch fails and reports local results only

---

### Issue 6: Too many branches listed

**Symptom:**
```
Output lists hundreds of branches, making it hard to review
```

**Cause:**
- Large team with many contributors
- Long-running project with accumulated branches
- No branch cleanup policy in place

**Solution:**
```bash
# Use a longer threshold to focus on truly stale branches
/stale-branches --threshold 6

# Focus on local only first (skip --remote)
/stale-branches --threshold 6

# Clean up merged branches first (safest)
git branch --merged main | grep -v main | xargs git branch -d
```

**Prevention:**
- Establish a branch cleanup policy (e.g., delete after merge)
- Configure GitHub to auto-delete branches after PR merge
- Run `/stale-branches` regularly (e.g., monthly)

---

### Issue 7: Current branch appears in results

**Symptom:**
```
The currently checked-out branch appears in the merged or inactive list
```

**Cause:**
- The current branch is merged into base or is inactive
- This is rare but possible if you're on an old branch

**Solution:**
The skill filters out the current branch marker (`*`) from merged branch listings. If you still see it:

```bash
# Check which branch you're on
git branch --show-current

# Switch to base branch before running
git checkout main
/stale-branches
```

**Prevention:**
- The skill excludes branches marked with `*` (current branch indicator)
- Run from the base branch for cleanest results

---

### Issue 8: Date calculation differs between macOS and Linux

**Symptom:**
```
Different results on macOS vs Linux for the same repository
Threshold calculation seems incorrect
```

**Cause:**
- macOS uses BSD `date` command (`date -v-3m`)
- Linux uses GNU `date` command (`date -d "3 months ago"`)
- Slight differences in "3 months ago" calculation between implementations

**Solution:**
The skill handles this automatically with platform detection:

```bash
if [[ "$OSTYPE" == "darwin"* ]]; then
  threshold=$(date -v-${THRESHOLD_MONTHS}m +%s)
else
  threshold=$(date -d "${THRESHOLD_MONTHS} months ago" +%s)
fi
```

If you suspect an issue:

```bash
# Verify the calculated threshold
echo "Threshold: $(date -r $threshold)" # macOS
echo "Threshold: $(date -d @$threshold)" # Linux
```

**Prevention:**
- The skill's cross-platform detection handles this automatically
- Results may differ by a few hours between platforms, which is negligible for month-level thresholds

---

## Quick Diagnostics

### Checklist Before Running

```bash
# 1. Verify git repository
git rev-parse --is-inside-work-tree

# 2. Check current directory
pwd

# 3. Check base branch exists
git rev-parse --verify main 2>/dev/null && echo "main exists" || echo "main NOT found"
git rev-parse --verify master 2>/dev/null && echo "master exists" || echo "master NOT found"

# 4. Count local branches
git branch | wc -l

# 5. Check remote connectivity (if using --remote)
git ls-remote origin 2>/dev/null && echo "Remote OK" || echo "Remote FAIL"
```

### Manual Branch Inspection

```bash
# See all branches with last commit dates
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:relative)' refs/heads/

# Check if a specific branch is merged
git branch --merged main | grep "branch-name"

# Check divergence of a specific branch
git rev-list --left-right --count main...branch-name
```

## Getting Help

### Skill Documentation
- `SKILL.md` — Overview, triggers, and inline workflow
- `WORKFLOW.md` — Detailed 5-phase methodology
- `EXAMPLES.md` — Usage scenarios with sample output

### External Resources
- [Git Branch Management](https://git-scm.com/book/en/v2/Git-Branching-Branch-Management)
- [GitHub Auto-Delete Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches)

## Version

1.0.0
