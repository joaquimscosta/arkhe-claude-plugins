# Branch Cleanup Workflow

Step-by-step methodology for deleting merged branches and flagging stale unmerged branches.

## Overview

The branch cleanup skill follows a 5-phase workflow:
1. **Environment Validation** — Verify git repository, parse arguments, fetch remote state
2. **Local Merged Branch Cleanup** — Delete local branches merged into base (with confirmation)
3. **Remote Merged Branch Cleanup** — Delete remote merged branches (with confirmation, if `--remote`)
4. **Stale Unmerged Branch Report** — Flag inactive unmerged branches (read-only)
5. **Summary & Audit Trail** — Report all actions taken

## Phase 1: Environment Validation

### Git Repository Check
```bash
git rev-parse --is-inside-work-tree 2>/dev/null
```

If this fails, the user is not in a git repository. Stop and inform them.

### Argument Parsing

Parse the `$ARGUMENTS` string for four optional flags:

| Flag | Variable | Default | Description |
|------|----------|---------|-------------|
| `--base BRANCH` | BASE_BRANCH | main | Base branch for merge check |
| `--threshold N` | THRESHOLD_MONTHS | 3 | Months of inactivity |
| `--remote` | INCLUDE_REMOTE | false | Include remote branch deletion |
| `--dry-run` | DRY_RUN | false | Preview without deleting |

### Base Branch Validation
```bash
git rev-parse --verify "$BASE_BRANCH" 2>/dev/null
# Fallback: try master if main doesn't exist
git rev-parse --verify "master" 2>/dev/null
```

If neither `main` nor `master` exists and no `--base` was specified, stop and ask the user which branch to use.

### Fetch Remote State
```bash
git fetch --prune 2>/dev/null
```

This prunes stale remote-tracking refs and ensures merge status checks are accurate.

### Status Summary
```bash
current_branch=$(git branch --show-current)
total_local=$(git branch | wc -l | tr -d ' ')
merged_local=$(git branch --merged "$BASE_BRANCH" | grep -v "^\*" | grep -v "$BASE_BRANCH" | wc -l | tr -d ' ')
```

Present the overview before proceeding with destructive operations.

**Output**: Validated environment with parsed arguments and branch summary.

## Phase 2: Local Merged Branch Cleanup

### Purpose

Delete local branches that have been merged into the base branch. These branches are safe to delete because their changes are already in the base.

### Discovery

```bash
git branch --merged "$BASE_BRANCH" | grep -v "^\*" | grep -v "$BASE_BRANCH"
```

### Enrichment

For each merged branch, show last commit date:

```bash
git log -1 --format='%ci' "$branch" 2>/dev/null | cut -d' ' -f1
```

### Confirmation

Before deleting, present the full list to the user and ask for explicit confirmation via natural conversation.

**Dry-run mode**: Display the list with "[DRY RUN] Would delete:" prefix and skip deletion.

### Deletion

```bash
# Safe delete — only works on merged branches
git branch -d "$branch"
```

Using `-d` (lowercase) ensures git refuses to delete unmerged branches.

### Output Format

```
=== LOCAL MERGED BRANCHES ===
  feat/001-user-auth  (last commit: 2025-08-15)
  fix/002-login-bug   (last commit: 2025-09-01)
Found 2 local merged branch(es)

Delete these 2 branches? [Confirm/Skip]
→ Deleted: feat/001-user-auth
→ Deleted: fix/002-login-bug
```

**Output**: List of deleted branches or skip confirmation.

## Phase 3: Remote Merged Branch Cleanup

### Trigger

Only executed when `--remote` flag is provided.

### Discovery

```bash
git branch -r --merged "origin/$BASE_BRANCH" | grep -v "origin/$BASE_BRANCH" | grep -v "origin/HEAD"
```

### Confirmation

Present the full list and ask for explicit confirmation. Remote deletions are irreversible (the branch can be recreated from reflog within a limited window, but is effectively gone).

### Deletion

```bash
# Strip origin/ prefix and delete from remote
git push origin --delete "$branch_name"
```

### Output Format

```
=== REMOTE MERGED BRANCHES ===
  feat/001-user-auth  (last commit: 2025-08-15)
  fix/002-login-bug   (last commit: 2025-09-01)
Found 2 remote merged branch(es)

Delete these 2 remote branches from origin? [Confirm/Skip]
→ Deleted remote: feat/001-user-auth
→ Deleted remote: fix/002-login-bug
```

**Output**: List of deleted remote branches or skip confirmation.

## Phase 4: Stale Unmerged Branch Report

### Purpose

Identify branches NOT merged into base with no commits within the threshold period. These are flagged for manual review only — **never auto-deleted**.

### Threshold Calculation

Cross-platform epoch timestamp:

```bash
# macOS (BSD date)
if [[ "$OSTYPE" == "darwin"* ]]; then
  threshold=$(date -v-${THRESHOLD_MONTHS}m +%s)
# Linux (GNU date)
else
  threshold=$(date -d "${THRESHOLD_MONTHS} months ago" +%s)
fi
```

### Scanning

```bash
git for-each-ref --sort=committerdate \
  --format='%(refname:short) %(committerdate:unix) %(committerdate:relative)' \
  refs/heads/
```

### Filtering

For each branch:
1. Skip the base branch and current branch
2. Check timestamp against threshold (must be older)
3. Verify branch is NOT merged into base
4. Calculate ahead/behind divergence counts

### Output Format

```
=== STALE UNMERGED BRANCHES (manual review required) ===
  experiment/old-feature (8 months ago) [ahead 3, behind 42]
  spike/prototype        (5 months ago) [ahead 1, behind 28]

To delete these branches manually:
  Local:   git branch -D <branch>
  Remote:  git push origin --delete <branch>
```

**Output**: Read-only report with manual deletion suggestions.

## Phase 5: Summary & Audit Trail

### Summary Report

```
=== CLEANUP SUMMARY ===
Local merged branches deleted: 2
Remote merged branches deleted: 2 (or "skipped — use --remote")
Stale unmerged branches flagged: 3 (manual review)
```

### Audit Context

Include the parameters used for the cleanup:
- Base branch checked against
- Inactivity threshold applied
- Whether remote was included
- Whether dry-run mode was active

**Output**: Complete cleanup summary.

## Workflow Diagram

```
+---------------------------+
| 1. Environment Validation |
|  - Git repo check         |
|  - Parse arguments        |
|  - Validate base branch   |
|  - Fetch & prune remote   |
|  - Branch status summary  |
+-----------+---------------+
            |
            v
+---------------------------+
| 2. Local Merged Cleanup   |
|  - List merged branches   |
|  - Show last commit dates |
|  - ASK USER CONFIRMATION  |
|  - Delete with git -d     |
+-----------+---------------+
            |
            v (if --remote)
+---------------------------+
| 3. Remote Merged Cleanup  |
|  - List remote merged     |
|  - Show last commit dates |
|  - ASK USER CONFIRMATION  |
|  - Delete from origin     |
+-----------+---------------+
            |
            v
+---------------------------+
| 4. Stale Unmerged Report  |
|  - Calculate threshold    |
|  - Scan for inactive      |
|  - Show ahead/behind      |
|  - Suggest manual cmds    |
|  - NEVER AUTO-DELETE      |
+-----------+---------------+
            |
            v
+---------------------------+
| 5. Summary & Audit Trail  |
|  - Deleted counts         |
|  - Flagged counts         |
|  - Parameters used        |
+---------------------------+
```

## Error Handling

### Cannot Delete Current Branch
```
Error: Cannot delete branch 'feat/xxx' checked out at '/path'
→ Skip this branch and continue with others
→ Inform user to switch branches first if needed
```

### Remote Permission Denied
```
Error: permission denied to push to 'origin'
→ Stop remote deletion
→ Report which branches were not deleted
→ Suggest checking remote access permissions
```

### No Merged Branches Found
```
No local merged branches to delete.
→ Skip Phase 2
→ Continue to Phase 3 (remote) or Phase 4 (stale)
```

## Next Steps

- See `EXAMPLES.md` for real-world usage scenarios
- See `TROUBLESHOOTING.md` for common issues and solutions

## Version

1.0.0
