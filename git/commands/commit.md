---
description: Context-aware Git commit assistant with smart pre-commit checks
---

# Commit Command

You are a context-aware Git commit assistant that automatically detects:
- **Root repository**: Main project repository
- **Submodules**: Any git submodules present in the project

## Usage

- `/commit` - Interactive mode (auto-detect changes across repositories)
- `/commit <scope>` - Direct commit to specific repository
- `/commit --no-verify` - Skip pre-commit checks
- `/commit --full-verify` - Run full build before committing
- `/commit <scope> --no-verify` - Combine scope + flag

### Valid Scopes

**Root**: Main project repository
- Automatically detected as the primary git repository

**Submodules**: Any submodules present in the project
- Automatically detected via `.gitmodules` file
- Each submodule can be committed independently

## Examples

```bash
/commit
# Interactive selection from all repositories with changes

/commit root
# Direct commit to root repository

/commit submodule-name
# Direct commit to specific submodule

/commit --no-verify
# Interactive selection, skip all checks

/commit root --full-verify
# Commit to root with full build verification (backend + frontend)
```

## Workflow

The commit command will execute the following steps:

1. **Parse arguments** - Determine scope and flags from `$ARGUMENTS`

2. **Detect/select repository**:
   - If scope provided: Use that repository
   - If no scope: Detect all repositories with changes
   - If only one has changes: Auto-select it
   - If both have changes: Present interactive selection

3. **Validate branch** - Check branch protection (blocks `main` in root, allows `main` in plan)

4. **Run pre-commit checks** - Execute appropriate checks based on scope and flags:
   - **Root**: Smart detection based on changed files
     - Kotlin files (`.kt`) → `./gradlew detekt` (backend linting)
     - TypeScript files (`.ts`/`.tsx`) → `npx tsc --noEmit` (frontend type-check)
     - Both → run both checks
   - **Plan**: Skip all checks (documentation only)
   - **--no-verify**: Skip all checks
   - **--full-verify**: Run full builds (backend: `./gradlew build test`, frontend: `npm run build`)

5. **Stage files** - Stage all changes (or use already staged files)

6. **Suggest commit message** - Generate conventional commit message:
   - Format: `<emoji> <type>(<scope>): <description>`
   - Types: feat, fix, refactor, perf, docs, style, test, build, ci, chore
   - Scope auto-detection for root (backend/frontend/infra/docs/core)
   - Ask for approval: [y/n/edit]

7. **Create commit** - Execute git commit with approved message

8. **Show summary** - Display commit info and next steps

## Implementation

Use the **creating-commit** skill to execute the commit workflow with arguments: `$ARGUMENTS`

The skill handles all workflow logic including:
- Path resolution (works from any directory in the project)
- Repository change detection
- Interactive selection with file counts
- Branch protection enforcement
- Smart pre-commit checks based on file types
- Intelligent commit message generation
- Post-commit summary with submodule reminders

**Skill location**: `git/skills/commit/`
**Script execution**: The skill executes `./scripts/commit.sh` with the provided arguments

## Smart Pre-commit Checks

For the **root** repository, checks are run based on detected file types:

- **Kotlin files detected** (`.kt`):
  ```bash
  cd backend && ./gradlew detekt
  ```
  Runs Kotlin static analysis and linting (~10-30 seconds)

- **TypeScript files detected** (`.ts`/`.tsx`):
  ```bash
  cd frontend && npx tsc --noEmit
  ```
  Runs TypeScript type checking (~5-15 seconds)

- **Both detected**: Runs both checks sequentially

- **Full verification** (`--full-verify`):
  ```bash
  cd backend && ./gradlew build test
  cd frontend && npm run build
  ```
  Full builds with tests (~2-4 minutes)

For **submodules**, checks can be configured or skipped based on content type.

## Repository Structure

### Root Repository
Main project repository automatically detected as the primary git repository.

### Submodules
Any git submodules present in the project, automatically detected via `.gitmodules` file. Each submodule is treated as an independent repository for commit purposes.

## Seamless Submodule Workflow

When you commit to any **submodule**, the command automatically handles the submodule reference update in the **root** repository:

### Clean Case (Only submodule modified in root)
```bash
/commit submodule-name
# ... commits to submodule ...

📤 Commit submodule reference to root? [Y/n]:
# Press Enter to auto-commit (default: Yes)
# Stages only submodule/ and creates: 🔖 chore(submodule): update submodule-name to a898425
```

### Mixed Case (Root has other uncommitted changes)
```bash
/commit submodule-name
# ... commits to submodule ...

⚠️  Root repository has other uncommitted changes.
📤 Commit submodule reference separately? [y/N]:
# Default: No (commit later with other changes)
# If Yes: Stages only submodule/ and commits separately
```

This seamless workflow ensures the submodule reference stays up-to-date without manual intervention.

## Important Notes

1. **Path Resolution** - The command works from any directory in the project
2. **Submodule Independence** - Commits to submodules only affect that specific submodule
3. **Seamless Submodule Updates** - After committing to any submodule, automatically prompts to commit the submodule reference in root with smart defaults
4. **Protected Branches** - Configurable branch protection (default: main branch blocked in root repository)
5. **No Claude Footer** - Commit messages never include Claude Code footer
6. **Absolute Paths** - All git operations use absolute paths
7. **Error Handling** - Clear error messages with actionable suggestions
8. **Smart Detection** - Only runs checks relevant to changed files

## Guidelines

- **ALWAYS resolve paths first** - Never assume current working directory
- **Check branch protection** - Respect branch protection rules (configurable)
- **Encourage atomic commits** - One logical change per commit
- **Follow conventional commits** - Use emoji + type(scope): description format
- **Be helpful** - Guide users through the process
- **Respect flags** - Honor --no-verify and --full-verify choices
- **Context awareness** - Detect all repositories and submodules automatically
- **Graceful errors** - Provide clear error messages and suggestions
