# Branch Cleanup Examples

Usage scenarios for the `cleaning-up-branches` skill.

## Example 1: Default Usage (Local Merged Only)

**Input:**
```bash
/cleanup-branches
```

**Output:**
```
=== BRANCH STATUS ===
Current branch: main
Base branch: main
Local branches: 8 (3 merged into main)
Remote branches: 12 (5 merged into main)

=== LOCAL MERGED BRANCHES ===
  feat/001-user-auth    (last commit: 2025-08-15)
  fix/002-login-bug     (last commit: 2025-09-01)
  chore/003-deps        (last commit: 2025-07-20)
Found 3 local merged branch(es)
```

Claude asks: _"These 3 branches are merged into main. Delete them?"_

User confirms → branches deleted:
```
→ Deleted: feat/001-user-auth
→ Deleted: fix/002-login-bug
→ Deleted: chore/003-deps

=== STALE UNMERGED BRANCHES (manual review required) ===
  experiment/old-feature (8 months ago) [ahead 3, behind 42]

To delete these branches manually:
  Local:   git branch -D <branch>
  Remote:  git push origin --delete <branch>

=== CLEANUP SUMMARY ===
Local merged branches deleted: 3
Remote merged branches deleted: skipped — use --remote
Stale unmerged branches flagged: 1 (manual review)
```

## Example 2: Including Remote Branches

**Input:**
```bash
/cleanup-branches --remote
```

**Output (after local cleanup):**
```
=== REMOTE MERGED BRANCHES ===
  feat/001-user-auth    (last commit: 2025-08-15)
  fix/002-login-bug     (last commit: 2025-09-01)
  chore/003-deps        (last commit: 2025-07-20)
  docs/004-readme       (last commit: 2025-06-10)
  refactor/005-api      (last commit: 2025-08-22)
Found 5 remote merged branch(es)
```

Claude asks: _"These 5 remote branches are merged. Delete them from origin?"_

User confirms:
```
→ Deleted remote: feat/001-user-auth
→ Deleted remote: fix/002-login-bug
→ Deleted remote: chore/003-deps
→ Deleted remote: docs/004-readme
→ Deleted remote: refactor/005-api

=== CLEANUP SUMMARY ===
Local merged branches deleted: 3
Remote merged branches deleted: 5
Stale unmerged branches flagged: 1 (manual review)
```

## Example 3: Custom Base Branch and Threshold

**Input:**
```bash
/cleanup-branches --base develop --threshold 1
```

**Output:**
```
=== BRANCH STATUS ===
Current branch: feat/006-new-feature
Base branch: develop
Local branches: 10 (4 merged into develop)
Remote branches: 15 (6 merged into develop)

=== LOCAL MERGED BRANCHES ===
  feat/001-user-auth    (last commit: 2025-08-15)
  fix/002-login-bug     (last commit: 2025-09-01)
  chore/003-deps        (last commit: 2025-07-20)
  hotfix/007-crash      (last commit: 2025-09-10)
Found 4 local merged branch(es)
```

With `--threshold 1`, more branches appear as stale (1 month inactivity vs default 3).

## Example 4: Dry-Run Mode

**Input:**
```bash
/cleanup-branches --remote --dry-run
```

**Output:**
```
=== BRANCH STATUS ===
Current branch: main
Base branch: main
Local branches: 8 (3 merged into main)
Remote branches: 12 (5 merged into main)

[DRY RUN] Would delete 3 local merged branches:
  feat/001-user-auth    (last commit: 2025-08-15)
  fix/002-login-bug     (last commit: 2025-09-01)
  chore/003-deps        (last commit: 2025-07-20)

[DRY RUN] Would delete 5 remote merged branches:
  feat/001-user-auth    (last commit: 2025-08-15)
  fix/002-login-bug     (last commit: 2025-09-01)
  chore/003-deps        (last commit: 2025-07-20)
  docs/004-readme       (last commit: 2025-06-10)
  refactor/005-api      (last commit: 2025-08-22)

=== STALE UNMERGED BRANCHES (manual review required) ===
  experiment/old-feature (8 months ago) [ahead 3, behind 42]

=== CLEANUP SUMMARY ===
[DRY RUN] No branches were deleted.
Local merged branches that would be deleted: 3
Remote merged branches that would be deleted: 5
Stale unmerged branches flagged: 1 (manual review)
```

## Example 5: Natural Language Trigger

**User says:** "Can you clean up the old merged branches in this repo?"

The skill auto-invokes because of the trigger phrase "clean up ... merged branches". Claude runs the cleanup workflow with default settings (local only, 3-month threshold, main as base).

**User says:** "Delete all the stale branches including remote ones"

The skill auto-invokes with `--remote` inferred from "including remote ones".

## Example 6: No Cleanup Needed

**Input:**
```bash
/cleanup-branches
```

**Output:**
```
=== BRANCH STATUS ===
Current branch: main
Base branch: main
Local branches: 2 (0 merged into main)
Remote branches: 3 (0 merged into main)

No local merged branches to delete.
No stale unmerged branches found.

=== CLEANUP SUMMARY ===
Local merged branches deleted: 0
Remote merged branches deleted: skipped — use --remote
Stale unmerged branches flagged: 0
All branches are active and up to date.
```

## Version

1.0.0
