# Stale Branch Detection Workflow

Step-by-step methodology for identifying git branches that are candidates for cleanup.

## Overview

The stale branch detection skill follows a 5-phase workflow:
1. **Environment Validation** — Verify git repository and parse arguments
2. **Merged Branch Detection** — Find branches already merged into base
3. **Inactive Branch Detection** — Find unmerged branches with no recent activity
4. **Remote Analysis** — Optionally analyze remote branches
5. **Report Generation** — Summarize findings with cleanup suggestions

## Phase 1: Environment Validation

### Git Repository Check
```bash
# Verify working directory is a git repo
git rev-parse --is-inside-work-tree 2>/dev/null
```

If this fails, the user is not in a git repository. Stop and inform them.

### Argument Parsing

Parse the `$ARGUMENTS` string for three optional flags:

| Flag | Variable | Default | Description |
|------|----------|---------|-------------|
| `--threshold N` | THRESHOLD_MONTHS | 3 | Months of inactivity |
| `--base BRANCH` | BASE_BRANCH | main | Base branch for merge check |
| `--remote` | INCLUDE_REMOTE | false | Include remote branches |

### Base Branch Validation
```bash
# Check if base branch exists
git rev-parse --verify "$BASE_BRANCH" 2>/dev/null

# Fallback: try master if main doesn't exist
git rev-parse --verify "master" 2>/dev/null
```

If neither `main` nor `master` exists and no `--base` was specified, stop and ask the user which branch to use.

### Threshold Calculation

Calculate the epoch timestamp for the inactivity cutoff. This must be cross-platform:

```bash
# macOS (BSD date)
if [[ "$OSTYPE" == "darwin"* ]]; then
  threshold=$(date -v-${THRESHOLD_MONTHS}m +%s)
# Linux (GNU date)
else
  threshold=$(date -d "${THRESHOLD_MONTHS} months ago" +%s)
fi
```

**Output**: Validated environment with threshold epoch, base branch name, and remote flag.

## Phase 2: Merged Branch Detection

### Purpose

Find branches that have been merged into the base branch but not deleted. These are always safe to delete.

### Process

```bash
# List branches merged into base (excludes current and base branch)
git branch --merged "$BASE_BRANCH" | grep -v "^\*" | grep -v "$BASE_BRANCH"
```

### Enrichment

For each merged branch, fetch the last commit date for context:

```bash
git log -1 --format='%ci' "$branch" 2>/dev/null | cut -d' ' -f1
```

This shows when the branch was last active, helping the user prioritize cleanup.

### Output Format

```
=== MERGED BRANCHES (safe to delete) ===
  feat/001-user-auth  (last commit: 2025-08-15)
  fix/002-login-bug   (last commit: 2025-09-01)
  chore/003-deps      (last commit: 2025-07-20)
Total merged: 3
```

**Output**: List of merged branches with last commit dates.

## Phase 3: Inactive Branch Detection

### Purpose

Find branches NOT merged into the base branch that have had no commits within the threshold period. These require review before deletion since they may contain unmerged work.

### Process

```bash
# Get all local branches with commit timestamps
git for-each-ref --sort=committerdate \
  --format='%(refname:short) %(committerdate:unix) %(committerdate:relative)' \
  refs/heads/
```

### Filtering Criteria

For each branch:
1. Skip the base branch
2. Skip branches with commits newer than the threshold
3. Skip branches that ARE merged (already reported in Phase 2)

### Divergence Analysis

For inactive unmerged branches, calculate how far they've diverged from base:

```bash
# Get ahead/behind counts
git rev-list --left-right --count "$BASE_BRANCH"..."$branch"
# Output: BEHIND<tab>AHEAD
```

- **Ahead N**: Branch has N commits not in base (potential unmerged work)
- **Behind N**: Base has N commits not in branch (branch is outdated)

### Output Format

```
=== INACTIVE UNMERGED BRANCHES (review before delete) ===
  experiment/old-feature (8 months ago) [ahead 3, behind 42]
  spike/prototype        (5 months ago) [ahead 1, behind 28]
```

**Output**: List of inactive unmerged branches with age and divergence counts.

## Phase 4: Remote Analysis

### Trigger

Only executed when `--remote` flag is provided.

### Preparation

```bash
# Fetch latest remote state and prune deleted remote branches
git fetch --prune
```

This ensures the local remote-tracking references are up to date and removes tracking refs for branches that no longer exist on the remote.

### Remote Merged Branches

```bash
# List remote branches merged into base
git branch -r --merged "$BASE_BRANCH" | grep -v "HEAD" | grep -v "$BASE_BRANCH"
```

Enriched with last commit dates, same as Phase 2.

### Remote Inactive Unmerged Branches

```bash
# Get all remote branches with timestamps
git for-each-ref --sort=committerdate \
  --format='%(refname:short) %(committerdate:unix) %(committerdate:relative)' \
  refs/remotes/origin/
```

Same filtering criteria as Phase 3 but applied to remote-tracking refs.

### Output Format

```
=== REMOTE MERGED BRANCHES ===
  origin/feat/001-user-auth  (last commit: 2025-08-15)
  origin/fix/002-login-bug   (last commit: 2025-09-01)

=== REMOTE INACTIVE UNMERGED BRANCHES ===
  origin/experiment/old-feature (8 months ago)
  origin/spike/prototype        (5 months ago)
```

**Output**: Remote branch analysis results.

## Phase 5: Report Generation

### Summary Block

```bash
current_branch=$(git branch --show-current)
total_local=$(git branch | wc -l | tr -d ' ')
merged_into_base=$(git branch --merged "$BASE_BRANCH" | grep -v "$BASE_BRANCH" | wc -l | tr -d ' ')
```

### Report Structure

```
=== SUMMARY ===
Current branch: feat/004-new-feature
Base branch: main
Inactivity threshold: 3 months
Total local branches: 12
Merged into main: 4

Cleanup commands (run manually):
  Delete merged local:    git branch -d <branch>
  Delete unmerged local:  git branch -D <branch>
  Delete remote:          git push origin --delete <branch>
  Delete all merged:      git branch --merged main | grep -v main | xargs git branch -d
```

### Safety Rules

1. **Never execute deletion commands** — only suggest them
2. **Always show current branch** — so the user knows where they are
3. **Distinguish merged vs unmerged** — merged branches are safe; unmerged require review
4. **Warn about squash merges** — branches merged via squash won't appear as "merged"

**Output**: Complete summary with cleanup suggestions.

## Workflow Diagram

```
+---------------------------+
| 1. Environment Validation |
|  - Git repo check         |
|  - Parse arguments        |
|  - Validate base branch   |
|  - Calculate threshold    |
+-----------+---------------+
            |
            v
+---------------------------+
| 2. Merged Branch Detection|
|  - git branch --merged    |
|  - Enrich: last commit    |
|  - Count total merged     |
+-----------+---------------+
            |
            v
+---------------------------+
| 3. Inactive Branch Detect |
|  - for-each-ref scan      |
|  - Filter by threshold    |
|  - Exclude merged         |
|  - Ahead/behind counts    |
+-----------+---------------+
            |
            v (if --remote)
+---------------------------+
| 4. Remote Analysis        |
|  - git fetch --prune      |
|  - Remote merged branches |
|  - Remote inactive branches|
+-----------+---------------+
            |
            v
+---------------------------+
| 5. Report Generation      |
|  - Summary stats          |
|  - Cleanup suggestions    |
|  - Squash merge warning   |
+---------------------------+
```

## Error Handling

### No Base Branch
```
Error: Branch 'main' does not exist
-> Try 'master' fallback
-> If neither exists, ask user for --base <branch>
```

### No Stale Branches Found
```
All branches are active and up to date.
No cleanup needed.
```

### Network Errors (--remote)
```
Warning: Could not reach remote 'origin'
-> Skip remote analysis
-> Report local results only
```

## Next Steps

- See `EXAMPLES.md` for real-world usage scenarios
- See `TROUBLESHOOTING.md` for common issues and solutions

## Version

1.0.0
