# Stale Branch Detection Examples

Real-world scenarios for identifying and cleaning up stale git branches.

## Example 1: Default Usage (Local Branches Only)

### Context
A developer wants to see which branches can be cleaned up in their project.

### Command
```bash
/stale-branches
```

### Execution
```bash
# Defaults: threshold=3 months, base=main, no remote
```

### Output
```
=== MERGED BRANCHES (safe to delete) ===
  feat/001-user-auth    (last commit: 2025-08-15)
  fix/002-login-bug     (last commit: 2025-09-03)
  chore/003-deps-update (last commit: 2025-07-22)
  docs/004-api-guide    (last commit: 2025-08-30)
Total merged: 4

=== INACTIVE UNMERGED BRANCHES (review before delete) ===
  experiment/cache-layer  (6 months ago) [ahead 5, behind 89]
  spike/graphql-prototype (4 months ago) [ahead 12, behind 67]

=== SUMMARY ===
Current branch: feat/010-dashboard
Base branch: main
Inactivity threshold: 3 months
Total local branches: 14
Merged into main: 4

Cleanup commands (run manually):
  Delete merged local:    git branch -d <branch>
  Delete unmerged local:  git branch -D <branch>
  Delete all merged:      git branch --merged main | grep -v main | xargs git branch -d
```

### Key Takeaways
- 4 merged branches are safe to delete immediately
- 2 unmerged branches need review — the `experiment/cache-layer` branch is 5 commits ahead and may have useful work

---

## Example 2: Custom Threshold (1 Month)

### Context
A team with frequent releases wants a stricter cleanup policy — anything inactive for 1+ month should be flagged.

### Command
```bash
/stale-branches --threshold 1
```

### Output
```
=== MERGED BRANCHES (safe to delete) ===
  feat/001-user-auth    (last commit: 2025-08-15)
  fix/002-login-bug     (last commit: 2025-09-03)
  chore/003-deps-update (last commit: 2025-07-22)
  docs/004-api-guide    (last commit: 2025-08-30)
  feat/005-search       (last commit: 2025-10-01)
  fix/006-sidebar       (last commit: 2025-09-28)
Total merged: 6

=== INACTIVE UNMERGED BRANCHES (review before delete) ===
  experiment/cache-layer  (6 months ago) [ahead 5, behind 89]
  spike/graphql-prototype (4 months ago) [ahead 12, behind 67]
  feat/007-notifications  (2 months ago) [ahead 8, behind 15]

=== SUMMARY ===
Current branch: main
Base branch: main
Inactivity threshold: 1 month
Total local branches: 14
Merged into main: 6

Cleanup commands (run manually):
  Delete merged local:    git branch -d <branch>
  Delete unmerged local:  git branch -D <branch>
  Delete all merged:      git branch --merged main | grep -v main | xargs git branch -d
```

### Key Takeaways
- Lower threshold catches more branches (6 merged vs 4 with default)
- `feat/007-notifications` appears as inactive now — it's only 2 months old but exceeds the 1-month threshold
- The team should decide if that branch is still being worked on

---

## Example 3: Including Remote Branches

### Context
A team lead wants to clean up both local and remote branches before a major release.

### Command
```bash
/stale-branches --remote
```

### Output
```
=== MERGED BRANCHES (safe to delete) ===
  feat/001-user-auth    (last commit: 2025-08-15)
  fix/002-login-bug     (last commit: 2025-09-03)
Total merged: 2

=== INACTIVE UNMERGED BRANCHES (review before delete) ===
  experiment/cache-layer (6 months ago) [ahead 5, behind 89]

=== REMOTE MERGED BRANCHES ===
  origin/feat/001-user-auth    (last commit: 2025-08-15)
  origin/fix/002-login-bug     (last commit: 2025-09-03)
  origin/chore/003-deps-update (last commit: 2025-07-22)
  origin/docs/004-api-guide    (last commit: 2025-08-30)
  origin/feat/005-search       (last commit: 2025-10-01)

=== REMOTE INACTIVE UNMERGED BRANCHES ===
  origin/experiment/cache-layer  (6 months ago)
  origin/spike/graphql-prototype (4 months ago)
  origin/feat/old-feature        (8 months ago)

=== SUMMARY ===
Current branch: main
Base branch: main
Inactivity threshold: 3 months
Total local branches: 8
Merged into main: 2

Cleanup commands (run manually):
  Delete merged local:    git branch -d <branch>
  Delete unmerged local:  git branch -D <branch>
  Delete remote:          git push origin --delete <branch>
  Delete all merged:      git branch --merged main | grep -v main | xargs git branch -d
```

### Key Takeaways
- Remote has more stale branches than local (common when developers clean locally but forget remote)
- `origin/feat/old-feature` only exists on remote — someone pushed it but never cleaned up
- The `git push origin --delete <branch>` command is provided for remote cleanup

---

## Example 4: Custom Base Branch

### Context
A project uses `develop` as its integration branch instead of `main`. The developer wants to find branches merged into `develop`.

### Command
```bash
/stale-branches --base develop
```

### Output
```
=== MERGED BRANCHES (safe to delete) ===
  feat/sprint-12-auth   (last commit: 2025-09-15)
  feat/sprint-12-search (last commit: 2025-09-20)
  fix/sprint-13-sidebar (last commit: 2025-10-05)
  hotfix/login-crash    (last commit: 2025-10-02)
Total merged: 4

=== INACTIVE UNMERGED BRANCHES (review before delete) ===
  feat/sprint-10-export  (5 months ago) [ahead 23, behind 112]
  experiment/new-ui      (4 months ago) [ahead 45, behind 98]

=== SUMMARY ===
Current branch: feat/sprint-14-dashboard
Base branch: develop
Inactivity threshold: 3 months
Total local branches: 11
Merged into develop: 4

Cleanup commands (run manually):
  Delete merged local:    git branch -d <branch>
  Delete unmerged local:  git branch -D <branch>
  Delete all merged:      git branch --merged develop | grep -v develop | xargs git branch -d
```

### Key Takeaways
- Merge detection correctly uses `develop` as base
- `feat/sprint-10-export` has 23 commits ahead — significant unmerged work that should be reviewed
- Cleanup commands reference `develop` instead of `main`

---

## Example 5: Combined Flags

### Context
A strict cleanup before release: 1-month threshold, `master` base branch, including remotes.

### Command
```bash
/stale-branches --threshold 1 --base master --remote
```

### Output
```
=== MERGED BRANCHES (safe to delete) ===
  feature/user-profiles  (last commit: 2025-09-18)
  bugfix/header-overlap  (last commit: 2025-10-01)
  feature/dark-mode      (last commit: 2025-09-25)
Total merged: 3

=== INACTIVE UNMERGED BRANCHES (review before delete) ===
  feature/abandoned-chat  (3 months ago) [ahead 34, behind 78]
  experimental/wasm-build (2 months ago) [ahead 7, behind 45]

=== REMOTE MERGED BRANCHES ===
  origin/feature/user-profiles  (last commit: 2025-09-18)
  origin/bugfix/header-overlap  (last commit: 2025-10-01)
  origin/feature/dark-mode      (last commit: 2025-09-25)
  origin/release/v2.3.0         (last commit: 2025-08-30)

=== REMOTE INACTIVE UNMERGED BRANCHES ===
  origin/feature/abandoned-chat  (3 months ago)
  origin/experimental/wasm-build (2 months ago)

=== SUMMARY ===
Current branch: master
Base branch: master
Inactivity threshold: 1 month
Total local branches: 9
Merged into master: 3

Cleanup commands (run manually):
  Delete merged local:    git branch -d <branch>
  Delete unmerged local:  git branch -D <branch>
  Delete remote:          git push origin --delete <branch>
  Delete all merged:      git branch --merged master | grep -v master | xargs git branch -d
```

### Key Takeaways
- All three flags work together seamlessly
- `origin/release/v2.3.0` appears as remote-only merged branch — old release branch
- `feature/abandoned-chat` has 34 unmerged commits — worth investigating before deleting

---

## Auto-Invoke Example

### User Message
```
"Which of my branches are stale? I want to clean up before the release."
```

### Skill Behavior
The skill auto-invokes because the user mentioned "stale" and "branches". It runs with default settings (3 months, main, local only) and presents the report. The user can then ask for adjustments like a different threshold or remote analysis.

## Next Steps

- See `TROUBLESHOOTING.md` for common issues and solutions

## Version

1.0.0
