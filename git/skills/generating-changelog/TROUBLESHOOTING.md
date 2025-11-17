# Changelog Generator Troubleshooting

Common issues and solutions when generating changelogs in your project.

## Common Issues

### Issue 1: "Not a git repository"

**Symptom:**
```
Error: fatal: not a git repository (or any of the parent directories): .git
```

**Cause:**
- Not in a git-initialized directory
- Working in a directory outside the your project monorepo

**Solution:**
```bash
# Verify you're in a git repository
git rev-parse --is-inside-work-tree

# Navigate to your project monorepo root
cd /Users/username/Projects/your-project

# Or navigate to specific service
cd backend/user-service
```

**Prevention:**
- Always run `/changelog` from within a git repository
- Check `pwd` before running the command

---

### Issue 2: "No commits found in range"

**Symptom:**
```
Error: No commits found between v1.1.0 and HEAD
Warning: Cannot generate changelog with empty commit range
```

**Cause:**
- No new commits since last tag
- Incorrect tag name (typo or non-existent tag)
- Working on a branch without new commits

**Solution:**
```bash
# Check existing tags
git tag --list

# Verify commits exist in range
git log v1.1.0..HEAD --oneline

# If no commits, check current branch
git branch --show-current

# Check if on correct branch
git checkout main
```

**Alternative:**
```bash
# Generate changelog for specific commit range
/changelog --since abc123 --until def456

# Or use date range instead
/changelog --since "2025-10-01" --until "2025-10-22"
```

**Prevention:**
- Always verify commits exist before generating changelog
- Use `git log` to check commit range

---

### Issue 3: "Invalid version format"

**Symptom:**
```
Error: Cannot parse version "v1.x.0"
Expected format: MAJOR.MINOR.PATCH (e.g., 1.2.0)
```

**Cause:**
- Non-semantic versioning format
- Typo in version number
- Missing PATCH version (e.g., "1.2" instead of "1.2.0")

**Solution:**
```bash
# Use proper semantic versioning
/changelog --version 1.2.0

# NOT: /changelog --version 1.2
# NOT: /changelog --version v1.x.0
```

**Valid Formats:**
- `1.2.0` ✅
- `1.2.0-rc1` ✅ (pre-release)
- `1.2.0-beta.1` ✅ (pre-release with metadata)
- `v1.2.0` ❌ (remove 'v' prefix)
- `1.2` ❌ (missing PATCH)

**Prevention:**
- Always use `MAJOR.MINOR.PATCH` format
- Omit 'v' prefix (added automatically by skill)

---

### Issue 4: "Duplicate version entry"

**Symptom:**
```
Warning: CHANGELOG.md already contains entry for v1.2.0
Conflicting versions detected
```

**Cause:**
- Version already exists in CHANGELOG.md
- Running command multiple times for same version
- Manual edits conflicting with generated content

**Solution Option A: Overwrite**
```bash
# Overwrite existing entry
/changelog --version 1.2.0 --overwrite
```

**Solution Option B: Skip**
```bash
# Skip generation if version exists
/changelog --version 1.2.0 --skip-if-exists
```

**Solution Option C: Increment Version**
```bash
# Use next version instead
/changelog --version 1.2.1
```

**Prevention:**
- Check CHANGELOG.md before generating
- Use `--append` mode (default) to avoid conflicts
- Delete old entry manually before regenerating

---

### Issue 5: "Malformed commit messages"

**Symptom:**
```
Warning: 12 commits do not follow Conventional Commits format
These commits will be categorized as "Other Changes"
```

**Cause:**
- Commits don't follow `type: subject` format
- Missing colon after type
- Invalid commit type (not feat, fix, docs, etc.)

**Solution:**
```bash
# Review malformed commits
git log --oneline --grep="^[^:]*$"

# Manually categorize in changelog
# Edit CHANGELOG.md after generation
```

**Example Malformed Commits:**
```
❌ Added new feature
❌ Fixing bug in user service
❌ update docs
```

**Correct Format:**
```
✅ feat: add new feature
✅ fix: resolve bug in user service
✅ docs: update documentation
```

**Prevention:**
- Use Conventional Commits for all future commits
- Configure git commit hooks to validate format
- Educate team on commit message standards

---

### Issue 6: "Breaking changes not detected"

**Symptom:**
```
Generated changelog shows MINOR bump but should be MAJOR
Breaking change commits not highlighted in changelog
```

**Cause:**
- Breaking change not properly annotated
- Missing exclamation mark after commit type
- Missing `BREAKING CHANGE:` footer

**Solution:**
Properly annotate breaking changes using one of these methods:

**Method 1: Exclamation Mark**
```bash
git commit -m "feat!: migrate from Redux to TanStack Query

BREAKING CHANGE: Redux store removed, state management refactored"
```

**Method 2: Footer**
```bash
git commit -m "refactor: change API response format

BREAKING CHANGE: API response format changed from array to object"
```

**Method 3: Rewrite Commit Message**
```bash
# Amend last commit
git commit --amend

# Or interactive rebase for older commits
git rebase -i HEAD~5
```

**Prevention:**
- Always use `feat!:` or `fix!:` for breaking changes
- Include `BREAKING CHANGE:` footer with detailed description
- Review commits before tagging release

---

### Issue 7: "Missing PR numbers"

**Symptom:**
```
Changelog entries missing GitHub PR links
Expected: "Add feature (#123)"
Actual: "Add feature"
```

**Cause:**
- Commits don't reference PR numbers
- PR numbers not in standard format (#123)
- Manual commits instead of GitHub merge commits

**Solution:**
```bash
# Manually add PR numbers in commit messages
git commit -m "feat: add feature (#123)"

# Or use GitHub's merge commit message (automatic)
# "Merge pull request #123 from branch-name"

# Rewrite commit messages to add PR numbers
git rebase -i HEAD~5
```

**Alternative:**
```bash
# Generate changelog and manually add PR links
/changelog --version 1.2.0

# Edit CHANGELOG.md to add missing PR numbers
vim CHANGELOG.md
```

**Prevention:**
- Always merge PRs using GitHub's "Merge pull request" button
- Include PR number in commit message: `(#123)`
- Configure branch protection to require PR workflow

---

### Issue 8: "Monorepo commits grouped incorrectly"

**Symptom:**
```
All commits appear in root changelog
Service-specific changelogs are empty
```

**Cause:**
- Running command from wrong directory
- Not filtering commits by service path
- Monorepo structure not recognized

**Solution:**
```bash
# Generate service-specific changelog
cd backend/user-service
/changelog --version 1.2.0

# Filter commits by path (manual)
git log v1.1.0..HEAD --oneline -- backend/user-service/

# Or specify path filter
/changelog --path backend/user-service
```

**Monorepo Best Practices:**
- **Root changelog**: Project-wide changes affecting multiple services
- **Service changelogs**: Service-specific changes only
- Run command from service directory for service-specific changelogs

**Prevention:**
- Always `cd` to correct directory before generating
- Use `--path` filter for monorepo commits

---

### Issue 9: "Changelog format incorrect"

**Symptom:**
```
Generated changelog doesn't match expected format
Sections out of order or missing
```

**Cause:**
- Incorrect format specified
- Custom format expectations not met
- Missing category mapping

**Solution:**
```bash
# Specify format explicitly
/changelog --format keepachangelog  # Industry standard
/changelog --format conventional    # Conventional Commits
/changelog --format github          # GitHub release notes
```

**Format Comparison:**
| Format | Use Case | Example |
|--------|----------|---------|
| `keepachangelog` | Default, human-friendly | `### Added`, `### Fixed` |
| `conventional` | Developer-focused | `#### Features`, `#### Bug Fixes` |
| `github` | GitHub releases | `**New Features:**`, `**Bug Fixes:**` |

**Prevention:**
- Choose format before generating
- Review format examples in `EXAMPLES.md`
- Use consistent format across project

---

### Issue 10: "Performance issues with large repositories"

**Symptom:**
```
Command hangs or takes >30 seconds
Memory errors with large commit history
```

**Cause:**
- Analyzing thousands of commits
- Large monorepo with multiple services
- Inefficient git operations

**Solution:**
```bash
# Limit commit range
/changelog --since v1.9.0 --until HEAD  # Last version only

# Use date range instead of full history
/changelog --since "2025-10-01"

# Generate incrementally (per service)
cd backend/user-service && /changelog
cd backend/search-service && /changelog
```

**Optimization:**
```bash
# Use shallow clone for faster operations
git log --since="2025-10-01" --pretty=format:"%s" | head -100
```

**Prevention:**
- Always specify commit range with `--since`
- Avoid generating changelogs for entire repository history
- Use service-specific changelogs in monorepo

---

## Quick Diagnostics

### Checklist Before Running Command

```bash
# 1. Verify git repository
git rev-parse --is-inside-work-tree

# 2. Check current directory
pwd

# 3. Verify commits exist
git log --oneline | head -10

# 4. Check existing tags
git tag --list | tail -5

# 5. Verify commit range
git log v1.1.0..HEAD --oneline

# 6. Check for existing changelog
test -f CHANGELOG.md && echo "Exists" || echo "Will create new"
```

### Debug Mode

```bash
# Enable verbose output
/changelog --verbose --version 1.2.0

# Dry run (preview without writing)
/changelog --dry-run --version 1.2.0

# Show detected commits
git log v1.1.0..HEAD --pretty=format:"%h %s" | head -20
```

## Getting Help

### Skill Documentation
- `SKILL.md` - Overview and triggers
- `WORKFLOW.md` - Step-by-step methodology
- `EXAMPLES.md` - Real-world your project scenarios

### your project Resources
- `CLAUDE.md` - Main project guidance
- `ARCHITECTURE.md` - System architecture
- Service-specific `CLAUDE.md` files

### External Resources
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)

## Version

1.0.0
