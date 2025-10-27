# Git Commit Creation: Detailed Workflow

This document provides a detailed step-by-step breakdown of the commit creation process.

For quick start instructions, see [SKILL.md](SKILL.md).

## Overview

The commit creation process follows 5 main steps:

1. **Repository Detection** - Auto-detect root repository and submodules
2. **Change Analysis** - Identify modified files and determine scope
3. **Pre-commit Checks** - Run language-specific checks
4. **Commit Message Generation** - Create conventional commit messages
5. **Submodule Handling** - Update submodule references in root

---

## Step 1: Repository Detection

Automatically detect the repository structure and identify where changes exist.

### Root Repository Detection

**Process**:
1. Find the root `.git` directory by walking up from current directory
2. Identify repository name from directory or git remote
3. Set root repository path

**Example**:
```
Current directory: /Users/you/projects/myapp/src/
Root repository: /Users/you/projects/myapp/
Repository name: myapp
```

### Submodule Detection

**Process**:
1. Check for `.gitmodules` file in root
2. Parse submodule paths and names
3. For each submodule:
   - Check if directory exists
   - Verify `.git` file/directory
   - Add to submodule list

**Example `.gitmodules`**:
```ini
[submodule "plugins/arkhe-claude-plugins"]
	path = plugins/arkhe-claude-plugins
	url = git@github.com:user/arkhe-claude-plugins.git
```

**Detected Structure**:
```
Root: myapp/
Submodules:
  - arkhe-claude-plugins (plugins/arkhe-claude-plugins/)
```

### Change Detection

**For Root Repository**:
```bash
cd /root/path
git status --porcelain
```

**For Each Submodule**:
```bash
cd /root/path/submodule-path
git status --porcelain
```

**Output Interpretation**:
- `M` = Modified file
- `A` = Added file
- `D` = Deleted file
- `??` = Untracked file
- `R` = Renamed file

**Result**: List of repositories with changes

---

## Step 2: Change Analysis

Analyze the types of changes to determine commit scope and pre-commit checks.

### File Type Detection

**Scan modified files for patterns**:

| File Pattern | Language | Pre-commit Check |
|--------------|----------|------------------|
| `*.kt` | Kotlin | `./gradlew detekt` |
| `*.ts`, `*.tsx` | TypeScript | `npx tsc --noEmit` |
| `*.py` | Python | Configurable linting |
| `*.rs` | Rust | `cargo check` |
| `*.md` | Markdown | None (documentation) |
| `*.json`, `*.yaml` | Config | None |

### Scope Determination

**Interactive Mode** (no arguments):
- If only root has changes → Commit to root
- If only one submodule has changes → Commit to that submodule
- If multiple repositories have changes → Prompt user to select

**Direct Mode** (with scope argument):
- `root` → Commit to root repository
- `<submodule-name>` → Commit to specific submodule
- Skip detection, go directly to specified repository

### Example Change Analysis

**Scenario**: Working on a plugin within a submodule

**Changes Detected**:
```
Root repository (myapp):
  - No changes

Submodule (arkhe-claude-plugins):
  M git/skills/commit/SKILL.md
  M git/skills/commit/scripts/commit.sh
  ?? git/skills/commit/WORKFLOW.md
```

**Analysis**:
- Repository: `arkhe-claude-plugins` (submodule)
- File types: `.md` (3 files), `.sh` (1 file)
- Pre-commit checks: None required (documentation + shell script)
- Commit type suggestion: `docs` or `feat`

---

## Step 3: Pre-commit Checks

Run language-specific checks before allowing commit.

### Check Selection Logic

**Kotlin Files** (`.kt`):
```bash
./gradlew detekt
```
- Runs static analysis
- Checks code style
- Identifies potential bugs

**TypeScript Files** (`.ts`, `.tsx`):
```bash
npx tsc --noEmit
```
- Type checks all TypeScript code
- Reports compilation errors
- No output files generated

**Python Files** (`.py`):
```bash
# Configurable - example:
flake8 --max-line-length=100
pylint --disable=C0111
```
- Linting based on configuration
- PEP 8 compliance

**Rust Files** (`.rs`):
```bash
cargo check
```
- Checks code compiles
- Reports errors
- Fast check without building

### Check Modes

**Standard Mode** (default):
```bash
git/skills/commit/scripts/commit.sh
```
- Runs checks for modified file types only
- Fast feedback loop

**Full Verification** (`--full-verify`):
```bash
git/skills/commit/scripts/commit.sh --full-verify
```
- Runs complete build process
- Backend + Frontend verification
- Slower but comprehensive

**Skip Verification** (`--no-verify`):
```bash
git/skills/commit/scripts/commit.sh --no-verify
```
- Skips all pre-commit checks
- Faster commit process
- Use for documentation-only changes

### Check Results

**Success**:
```
✅ Pre-commit checks passed
```
→ Proceed to commit message generation

**Failure**:
```
❌ Pre-commit checks failed:
  - Detekt found 3 issues in UserService.kt
  - TypeScript compilation error in auth.ts:42
```
→ Fix issues before committing (or use `--no-verify` to bypass)

### Example: TypeScript Check

**Modified Files**:
```
src/auth/login.ts
src/auth/logout.ts
```

**Check Execution**:
```bash
npx tsc --noEmit
```

**Success Output**:
```
✅ TypeScript compilation successful
```

**Failure Output**:
```
❌ TypeScript errors found:

src/auth/login.ts:42:15 - error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.

42     login(userId);
               ~~~~~~
```

→ Fix error before committing

---

## Step 4: Commit Message Generation

Generate conventional commit messages with appropriate type and scope.

### Conventional Commit Format

```
<type>(<scope>): <description>

[optional body]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit Type Detection

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

**Detection Logic**:
1. Analyze file paths and types
2. Read git diff for context
3. Suggest appropriate type
4. Allow user to confirm or modify

### Scope Detection

**Automatic Scope**:
- From directory structure (e.g., `auth`, `api`, `ui`)
- From file patterns (e.g., `skills/commit` → `commit`)

**Example**:
```
Modified: git/skills/commit/SKILL.md
Scope: commit
Type: docs
Message: docs(commit): update skill documentation
```

### Message Construction

**Step 1: Generate Description**
- Analyze changes from `git diff`
- Summarize in present tense
- Keep under 72 characters

**Step 2: Add Body** (if needed)
- Additional context
- Breaking changes
- Related issues

**Step 3: Add Footer**
```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Interactive Approval

**Script Presents**:
```
Suggested commit message:
────────────────────────────────
docs(commit): add comprehensive workflow documentation

Added detailed 5-step process explanation including
repository detection, change analysis, pre-commit checks,
message generation, and submodule handling.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
────────────────────────────────

Proceed with this commit? (y/n):
```

**User Options**:
- `y` → Commit with this message
- `n` → Abort
- `e` → Edit message (opens editor)

---

## Step 5: Submodule Handling

Handle submodule reference updates in root repository.

### Scenario: Submodule Committed

**After committing changes in a submodule**:

1. Submodule commit successful:
   ```
   [arkhe-claude-plugins abc1234] docs(commit): add workflow doc
   ```

2. Root repository now shows:
   ```bash
   cd /root
   git status
   ```
   ```
   Changes not staged for commit:
     modified:   plugins/arkhe-claude-plugins (new commits)
   ```

### Update Prompt

**Script Asks**:
```
✅ Committed in submodule: arkhe-claude-plugins

The root repository has new commits in this submodule.
Would you like to update the submodule reference in root? (y/n):
```

**Options**:

**Yes** (`y`):
```bash
# Automatic execution:
cd /root
git add plugins/arkhe-claude-plugins
git commit -m "chore: update arkhe-claude-plugins submodule

Updated to include latest changes:
- docs(commit): add workflow documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**No** (`n`):
- Skip root update
- User can manually update later

### Mixed Changes Scenario

**Root has changes AND submodule has changes**:

**Option 1**: Commit to submodule first
```bash
git/skills/commit/scripts/commit.sh arkhe-claude-plugins
```
→ Then prompted to update root

**Option 2**: Commit to root first
```bash
git/skills/commit/scripts/commit.sh root
```
→ Submodule changes remain uncommitted

**Option 3**: Interactive mode
```bash
git/skills/commit/scripts/commit.sh
```
→ Choose which repository to commit first

---

## Complete Example Workflows

### Example 1: Simple Feature Commit

**Context**: Modified authentication logic in root repository

**Step 1: Detection**
```
Root repository: myapp
Changes: src/auth/login.ts (modified)
Submodules: No changes
```

**Step 2: Analysis**
```
File type: TypeScript
Pre-commit check: npx tsc --noEmit
Suggested type: feat
```

**Step 3: Pre-commit**
```bash
Running TypeScript check...
✅ TypeScript compilation successful
```

**Step 4: Message**
```
feat(auth): add OAuth2 login support

Implemented OAuth2 authentication flow with token refresh
and secure session management.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Step 5: Commit**
```
✅ Committed: [myapp 7f3a8b9] feat(auth): add OAuth2 login support
```

---

### Example 2: Submodule Commit with Root Update

**Context**: Modified plugin skill in submodule

**Step 1: Detection**
```
Root repository: myapp
  - No direct changes
  - Submodule has changes

Submodule: arkhe-claude-plugins
  - Modified: git/skills/commit/SKILL.md
```

**Step 2: Interactive Selection**
```
Multiple repositories detected:
1. arkhe-claude-plugins (submodule)

Commit to: arkhe-claude-plugins
```

**Step 3: Pre-commit**
```
No checks required (documentation)
✅ Skipping pre-commit checks
```

**Step 4: Commit to Submodule**
```
docs(commit): update skill documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

✅ Committed: [arkhe-claude-plugins def5678]
```

**Step 5: Root Update Prompt**
```
Submodule reference updated in root repository.
Update root? (y/n): y

Committing to root:
chore: update arkhe-claude-plugins submodule

✅ Committed: [myapp 8g4b9c0]
```

---

### Example 3: Skip Verification

**Context**: Documentation-only change, want to skip checks

**Command**:
```bash
git/skills/commit/scripts/commit.sh --no-verify
```

**Workflow**:
```
Step 1: Detection ✅
Step 2: Analysis ✅
Step 3: Pre-commit → SKIPPED
Step 4: Message generation ✅
Step 5: Commit ✅
```

**Result**: Fast commit without waiting for checks

---

## Advanced Features

### Absolute Path Resolution

**The script works from any directory**:

```bash
# From root
cd /Users/you/projects/myapp
git/skills/commit/scripts/commit.sh

# From subdirectory
cd /Users/you/projects/myapp/src/auth
../../git/skills/commit/scripts/commit.sh

# From submodule
cd /Users/you/projects/myapp/plugins/arkhe-claude-plugins
../../git/skills/commit/scripts/commit.sh
```

All paths are resolved absolutely, ensuring consistent behavior.

### Branch Protection Awareness

**Protected Branches** (main, master, production):
- Script warns before committing
- Suggests creating feature branch
- Prevents accidental commits to protected branches

### Emoji Convention

**Commit message prefixes** (optional):
- 🎨 `:art:` - Improve structure/format
- ⚡️ `:zap:` - Improve performance
- 🔥 `:fire:` - Remove code/files
- 🐛 `:bug:` - Fix a bug
- ✨ `:sparkles:` - Introduce new features
- 📝 `:memo:` - Add/update documentation
- ♻️ `:recycle:` - Refactor code

**Usage**: Automatically added based on commit type (configurable)

---

## Configuration

### Environment Variables

**GIT_COMMIT_NO_VERIFY** (optional):
```bash
export GIT_COMMIT_NO_VERIFY=1
```
Always skip pre-commit checks

**GIT_COMMIT_FULL_VERIFY** (optional):
```bash
export GIT_COMMIT_FULL_VERIFY=1
```
Always run full verification

### Custom Pre-commit Commands

Edit `git/skills/commit/scripts/commit.sh` to customize checks:

```bash
# Add custom Python linting
if [[ $HAS_PYTHON_FILES == true ]]; then
    flake8 --max-line-length=100 || exit 1
fi
```

---

## Best Practices

1. **Run checks before committing**: Let the script detect and run appropriate checks
2. **Use meaningful commit messages**: The script generates good defaults, but customize if needed
3. **Commit frequently**: Small, focused commits are easier to review
4. **Keep submodules in sync**: Always update root when submodule changes
5. **Review staged changes**: Check `git status` before running commit script
6. **Use scoped commits**: Commit to specific repository when working on mixed changes

---

## Summary

The commit creation workflow automates:
1. ✅ Repository and submodule detection
2. ✅ Language-specific pre-commit checks
3. ✅ Conventional commit message generation
4. ✅ Submodule reference management
5. ✅ Interactive approval process

**Result**: Consistent, high-quality commits with minimal manual effort.

For examples, see [EXAMPLES.md](EXAMPLES.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

*Last Updated: 2025-10-27*
