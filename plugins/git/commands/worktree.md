---
description: Create a git worktree in the .worktrees/ directory for isolated parallel development
argument-hint: <name>
---

# Worktree Command

Creates an isolated git worktree in `.worktrees/<name>` for parallel development.

## Workflow

### 1. Parse Arguments

Extract the worktree name from `$ARGUMENTS`. If no name is provided, ask the user for one.

### 2. Validate

- Check that the name is not empty
- Check that `.worktrees/<name>` doesn't already exist (run `ls .worktrees/<name> 2>/dev/null`)

If it already exists, report the conflict and stop.

### 3. Safety Check

Verify `.worktrees/` is git-ignored to prevent accidentally committing worktree contents:

```bash
git check-ignore -q .worktrees 2>/dev/null
```

If NOT ignored, add `.worktrees/` to `.gitignore` before proceeding:

```bash
echo '\n# Worktrees\n.worktrees/' >> .gitignore
git add .gitignore && git commit -m "chore: add .worktrees/ to .gitignore"
```

### 4. Ask Base Branch

Use AskUserQuestion to ask which branch to base the worktree on:

- **main (Recommended)** — Create from the main branch
- **Current branch** — Create from the currently checked out branch
- **Other** — User specifies a different branch name

### 5. Create Worktree

```bash
mkdir -p .worktrees
git worktree add .worktrees/<name> -b <name> <base-branch>
```

Where `<base-branch>` is `main`, `HEAD`, or the user-specified branch.

### 6. Confirm Success

Report:
- Path: `.worktrees/<name>`
- Branch: `<name>` (based on `<base-branch>`)
- List worktrees: `git worktree list`
- Remove when done: `git worktree remove .worktrees/<name>`
