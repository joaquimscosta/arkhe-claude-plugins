# Changelog Generator Workflow

Step-by-step methodology for generating professional changelogs from git history.

## Overview

The changelog skill follows a 6-phase workflow:
1. **Context Analysis** - Understand repository and versioning scheme
2. **Git History Analysis** - Extract and parse commit history
3. **Commit Categorization** - Group commits by conventional commit types
4. **Version Detection** - Determine semantic version bump
5. **Changelog Generation** - Format output in requested style
6. **Update & Validation** - Write to file and validate markdown

## Phase 1: Context Analysis

### Repository Detection
```bash
# Check if in git repository
git rev-parse --is-inside-work-tree

# Detect if monorepo (multiple services)
ls backend/*/CLAUDE.md frontend/*/CLAUDE.md

# Identify current service (if in subdirectory)
pwd | grep -E "(backend|frontend)/([^/]+)"
```

### Versioning Scheme Detection
```bash
# Check for existing tags
git tag --list

# Identify versioning pattern
git tag --list | head -5
# Examples:
#   v1.0.0, v1.1.0 → Semantic versioning with 'v' prefix
#   1.0.0, 1.1.0 → Semantic versioning without prefix
#   2025.10.22 → CalVer (calendar versioning)
```

### Changelog Location
```bash
# Check for existing changelog
test -f CHANGELOG.md && echo "Exists" || echo "Create new"

# Monorepo: Check service-specific changelog
test -f backend/user-service/CHANGELOG.md
```

**Output**: Repository context (monorepo vs single, versioning scheme, changelog location)

## Phase 2: Git History Analysis

### Commit Range Determination
```bash
# Option A: Since last tag (default)
SINCE=$(git describe --tags --abbrev=0)
UNTIL="HEAD"

# Option B: User-specified range
SINCE="v1.1.0"
UNTIL="v1.2.0"

# Option C: Date range
SINCE="2025-01-01"
UNTIL="2025-10-22"
```

### Commit Extraction
```bash
# Get commits with metadata
git log $SINCE..$UNTIL \
  --pretty=format:"%H|%an|%ae|%ad|%s|%b" \
  --date=short

# Example output:
# abc123|John Doe|john@example.com|2025-10-22|feat: add keyword scoring|PR #123
# def456|Jane Smith|jane@example.com|2025-10-21|fix: resolve JWT issue|Fixes #124
```

### Commit Parsing
For each commit, extract:
- **Hash**: First 7 chars (abc123)
- **Author**: Name and email
- **Date**: ISO 8601 format
- **Type**: feat, fix, docs, etc. (from conventional commit prefix)
- **Scope**: Optional scope in parentheses (e.g., `feat(api):`)
- **Subject**: Commit message subject line
- **Body**: Full commit message body
- **Footer**: Metadata (PR numbers, issue refs, breaking changes)

**Output**: Structured commit data (JSON or array)

## Phase 3: Commit Categorization

### Conventional Commit Type Detection
```python
# Regex pattern for conventional commits
pattern = r'^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s+(?P<subject>.+)$'

# Categorize commits
categories = {
    'feat': [],      # Features
    'fix': [],       # Bug Fixes
    'docs': [],      # Documentation
    'style': [],     # Code Style
    'refactor': [],  # Refactoring
    'perf': [],      # Performance
    'test': [],      # Testing
    'build': [],     # Build System
    'ci': [],        # CI/CD
    'chore': [],     # Other
}
```

### Breaking Changes Detection
```python
# Method 1: Exclamation mark after type
if commit.breaking:  # feat!: or fix!:
    breaking_changes.append(commit)

# Method 2: BREAKING CHANGE footer
if 'BREAKING CHANGE:' in commit.footer:
    breaking_changes.append(commit)

# Method 3: Manual annotation in body
if re.search(r'\[breaking\]', commit.body, re.IGNORECASE):
    breaking_changes.append(commit)
```

### GitHub Metadata Extraction
```python
# Extract PR numbers
pr_numbers = re.findall(r'#(\d+)', commit.subject + commit.body)

# Extract issue references
issues = re.findall(r'(?:fixes|closes|resolves)\s+#(\d+)', commit.body, re.IGNORECASE)

# Extract co-authors
co_authors = re.findall(r'Co-authored-by:\s+([^<]+)\s+<([^>]+)>', commit.body)
```

**Output**: Categorized commits with metadata (breaking changes, PRs, issues, authors)

## Phase 4: Version Detection

### Semantic Version Bump Calculation
```python
def calculate_version_bump(commits, breaking_changes):
    """
    MAJOR: Breaking changes exist
    MINOR: Features exist (no breaking changes)
    PATCH: Only fixes exist
    """
    if breaking_changes:
        return 'MAJOR'  # x.0.0

    has_features = any(c.type == 'feat' for c in commits)
    if has_features:
        return 'MINOR'  # 0.x.0

    return 'PATCH'  # 0.0.x

# Example: v1.1.0 → v1.2.0 (MINOR bump)
```

### Version String Construction
```python
def build_version(last_version, bump_type):
    """
    Parse last version, apply bump, return new version
    """
    major, minor, patch = parse_semver(last_version)

    if bump_type == 'MAJOR':
        return f"{major + 1}.0.0"
    elif bump_type == 'MINOR':
        return f"{major}.{minor + 1}.0"
    else:  # PATCH
        return f"{major}.{minor}.{patch + 1}"

# Example: 1.1.0 + MINOR → 1.2.0
```

**Output**: Recommended version number and bump type

## Phase 5: Changelog Generation

### Format Selection

#### Keep a Changelog Format (default)
```markdown
## [1.2.0] - 2025-10-22

### Added
- Feature A description (#123)
- Feature B description (#124)

### Fixed
- Bug A description (#125)

### Changed
- Refactoring A description (#126)

### Security
- Security update A (#127)

### Performance
- Performance improvement A (#128)

### Deprecated
- Deprecated feature A (#129)

### Removed
- Removed feature A (#130)
```

#### Conventional Format
```markdown
## 1.2.0 (2025-10-22)

#### Features
* feat: add feature A (abc123)
* feat: add feature B (def456)

#### Bug Fixes
* fix: resolve bug A (ghi789)

#### Breaking Changes
* feat!: breaking change description (jkl012)
```

#### GitHub Format
```markdown
## What's Changed

**New Features:**
- Add feature A by @johndoe in #123
- Add feature B by @janesmith in #124

**Bug Fixes:**
- Resolve bug A by @johndoe in #125

**Full Changelog**: v1.1.0...v1.2.0
```

### Section Ordering
```python
# Standard order for Keep a Changelog
section_order = [
    'Added',       # New features
    'Changed',     # Changes to existing functionality
    'Deprecated',  # Soon-to-be removed features
    'Removed',     # Removed features
    'Fixed',       # Bug fixes
    'Security',    # Security updates
    'Performance', # Performance improvements
]
```

### Content Generation
```python
def generate_section(category_name, commits):
    """
    Generate markdown list for a category
    """
    if not commits:
        return ""

    lines = [f"### {category_name}\n"]

    for commit in commits:
        # Format: - Subject (#PR) [by @author]
        pr_link = f"(#{commit.pr})" if commit.pr else ""
        author = f"by @{commit.author}" if commit.author else ""

        line = f"- {commit.subject} {pr_link} {author}".strip()
        lines.append(line)

    return "\n".join(lines) + "\n"
```

**Output**: Formatted changelog sections (markdown)

## Phase 6: Update & Validation

### Changelog File Update

#### Append Mode (default)
```python
def append_to_changelog(new_version_section, changelog_path='CHANGELOG.md'):
    """
    Insert new version section at top (after header)
    """
    with open(changelog_path, 'r') as f:
        content = f.read()

    # Find insertion point (after header, before first version)
    header_end = content.find('## [')
    if header_end == -1:
        header_end = content.find('# Changelog') + len('# Changelog\n\n')

    # Insert new section
    updated = content[:header_end] + new_version_section + '\n' + content[header_end:]

    with open(changelog_path, 'w') as f:
        f.write(updated)
```

#### Overwrite Mode
```python
def overwrite_changelog(full_changelog, changelog_path='CHANGELOG.md'):
    """
    Replace entire changelog file
    """
    with open(changelog_path, 'w') as f:
        f.write(full_changelog)
```

### Markdown Validation
```python
def validate_markdown(changelog_content):
    """
    Validate markdown syntax
    """
    # Check for proper header hierarchy
    assert re.match(r'^# Changelog', changelog_content), "Missing main header"

    # Check for version sections
    versions = re.findall(r'^## \[?(\d+\.\d+\.\d+)\]?', changelog_content, re.MULTILINE)
    assert len(versions) > 0, "No version sections found"

    # Check for proper list formatting
    assert not re.search(r'^\*[^ ]', changelog_content, re.MULTILINE), "Invalid list formatting"

    return True
```

### Git Operations (optional)
```bash
# Stage changelog
git add CHANGELOG.md

# Commit changelog
git commit -m "docs: update CHANGELOG for v1.2.0"

# Create git tag
git tag -a v1.2.0 -m "Release v1.2.0"
```

**Output**: Updated CHANGELOG.md file, validation report

## Workflow Summary

```
┌─────────────────────┐
│ 1. Context Analysis │
│  - Repository type  │
│  - Versioning scheme│
│  - Changelog location│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Git History      │
│  - Extract commits  │
│  - Parse metadata   │
│  - Identify range   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Categorization   │
│  - Conventional type│
│  - Breaking changes │
│  - GitHub metadata  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Version Detection│
│  - Calculate bump   │
│  - Build version    │
│  - Validate semver  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. Generation       │
│  - Format selection │
│  - Section ordering │
│  - Content creation │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 6. Update & Validate│
│  - Write to file    │
│  - Validate markdown│
│  - Optional git ops │
└─────────────────────┘
```

## Error Handling

### No Git Repository
```
Error: Not a git repository
→ Prompt user to initialize git or navigate to repository
```

### No Commits in Range
```
Error: No commits found between v1.1.0 and HEAD
→ Suggest checking tag names or commit range
```

### Invalid Version Format
```
Error: Cannot parse version "1.x.0"
→ Prompt user to provide valid semver format
```

### Conflicting Changelog
```
Warning: CHANGELOG.md already contains entry for v1.2.0
→ Ask user: Overwrite, skip, or merge?
```

## Next Steps

- **Level 3**: See `EXAMPLES.md` for real-world your project scenarios
- **Level 4**: See `TROUBLESHOOTING.md` for common issues and solutions

## Version

1.0.0
