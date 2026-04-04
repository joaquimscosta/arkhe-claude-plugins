# Doc-Freshness Workflow

Detailed detection algorithms, convention tables, and output templates.

## Context Discovery Protocol

Priority-based context discovery:

1. **Configuration**: Read `.arkhe.yaml` → `doc-freshness:` section
2. **Project Identity**: Read `CLAUDE.md` and `README.md`
3. **Documentation Inventory**: Run `scan_freshness.py` to discover all docs
4. **Code Mapping**: Map docs to code via conventions (below) or config mappings

### Johnny Decimal Detection

If `.jd-config.json` exists or `docs/[0-9][0-9]-*/` directories are found:
- Glob `{jd_root}/[0-9][0-9]-*/**/*.md` to discover all J.D. docs
- Deprioritize `90-*` (archive) — flag but don't report as stale

## Convention-Based Code Mapping

When no explicit `mappings` config exists, map docs to code by convention:

| Doc Pattern | Likely Code Counterpart |
|-------------|------------------------|
| `README.md` | Project root, `src/`, install commands |
| `docs/api-reference.md`, `docs/api/*.md` | `src/api/**`, `src/routes/**`, `src/controllers/**` |
| `docs/architecture.md` | Module structure, `src/*/` directory names |
| `docs/setup.md`, `docs/getting-started.md` | `package.json` scripts, `Makefile`, `docker-compose.yml` |
| `CONTRIBUTING.md` | `.github/`, CI config, linter config |
| `docs/deployment.md` | `Dockerfile`, CI/CD config, `infra/` |
| `CHANGELOG.md` | `package.json` version, git tags |
| `docs/{module-name}.md` | `src/{module-name}/**` |
| `docs/{module-name}/*.md` | `src/{module-name}/**` |

### Tech-Stack-Aware Mapping

| Ecosystem | Additional Code Patterns |
|-----------|-------------------------|
| **Java/Kotlin** | `src/main/java/**`, `src/main/kotlin/**`, `build.gradle.kts` |
| **JavaScript/TypeScript** | `src/**/*.ts`, `src/**/*.tsx`, `app/**`, `pages/**` |
| **Python** | `src/**/*.py`, `app/**/*.py`, `{package}/**/*.py` |
| **Go** | `cmd/**/*.go`, `internal/**/*.go`, `pkg/**/*.go` |
| **Rust** | `src/**/*.rs`, `crates/**/*.rs` |

## Detection Algorithms

### Algorithm 0: Tier Detection (Script-Driven)

Before running checks, classify each doc into a scanning tier:

1. Read first 50 lines for YAML frontmatter (`---` delimiters)
2. If frontmatter contains `last_updated:` or `version:` field → **deep** tier
3. Otherwise → **basic** tier

Basic tier runs: link checking, backtick-path verification, git staleness.
Deep tier runs: all basic checks + version checking, `last_updated` accuracy vs git date, cross-doc consistency.

### Algorithm 1: Stale References (Script-Driven)

The `scan_freshness.py` script handles these deterministic checks:

#### Link Checking
1. Parse all `[text](target)` and `[text]: target` markdown links
2. Skip links inside fenced code blocks
3. For relative links: resolve path from doc's directory, verify target exists
4. For anchor links (`#heading`): verify heading exists in target file using slug matching
5. For backtick-quoted paths (`` `src/foo.ts` ``): check existence from project root and doc directory

#### Version Checking
1. Extract version references from markdown (e.g., "Node.js 18", "Python 3.8+")
2. Collect ground truth from: `package.json`, `.nvmrc`, `.python-version`, `pyproject.toml`, `build.gradle.kts`, `pom.xml`, `go.mod`, `.tool-versions`
3. Compare major versions (CRITICAL mismatch) and minor versions (WARNING)

#### Git Staleness
1. For each doc: get last commit date via `git log -1 --format="%ai"`
2. Get latest code commit date across all source files
3. Compute age gap and classify:
   - **fresh**: doc updated within 7 days of latest code change
   - **aging**: 7-30 day gap
   - **stale**: 30-90 day gap
   - **very_stale**: 90+ day gap

### Algorithm 2: Code-Doc Drift (Claude-Driven)

For docs flagged as stale or when `drift` mode is used:

1. **Extract references** from the doc:
   - Function/method names: grep for `functionName(`, `def function_name`, etc.
   - API endpoints: grep for `GET /api/`, `POST /api/`, etc.
   - File paths: resolve backtick-quoted paths
   - Config keys: grep for referenced config values
   - Class/type names: grep for `class ClassName`, `interface TypeName`, etc.

2. **Verify each reference** against the codebase:
   - Does the function/class still exist? → Grep for it
   - Has its signature changed? → Read the definition, compare with doc
   - Does the file path still exist? → Check filesystem
   - Does the API endpoint still exist? → Grep routes/controllers

3. **Report mismatches** with:
   - Doc file and line number
   - What the doc says
   - What the code actually shows (with file:line reference)
   - Severity (CRITICAL if removed, WARNING if changed)

### Algorithm 3: Cross-Doc Drift (Claude-Driven)

For `cross-doc` mode or as part of full `scan`:

1. **Topic clustering**: Group docs by shared heading keywords
   - Extract headings from each doc (script provides this)
   - Find docs with overlapping topics (e.g., both have "Installation" sections)

2. **Claim comparison**: For overlapping topics:
   - Read the relevant sections from each doc
   - Extract factual claims (version requirements, setup steps, configuration values)
   - Compare claims across docs

3. **Conflict detection**: Flag contradictions like:
   - Different version requirements (e.g., "Node 18" vs "Node 20")
   - Different setup steps for the same thing
   - Conflicting configuration instructions
   - Inconsistent terminology for the same concept

## Mode Workflows

### `scan` Mode (Full Analysis)

```
Step 1: Run scan_freshness.py <project-root>
Step 2: Parse JSON output
Step 3: Present summary table (docs, broken links, version mismatches, stale docs)
Step 4: Present broken links grouped by severity
Step 5: Present version mismatches
Step 6: For each stale/very_stale doc, run Algorithm 2 (code-doc drift)
Step 7: Run Algorithm 3 (cross-doc drift) on docs with overlapping topics
Step 8: Present final report with all findings
```

### `links` Mode (Fast)

```
Step 1: Run scan_freshness.py --links-only <project-root>
Step 2: Parse JSON output
Step 3: Present broken links table (CRITICAL broken links, then WARNING file refs)
Step 4: Present summary counts
```

### `check <path>` Mode (Focused)

```
Step 1: If path is directory, discover .md files within it
Step 2: Run link checker on targeted files
Step 3: Run version checker on targeted files
Step 4: For each targeted doc, run Algorithm 2 (code-doc drift)
Step 5: Present findings for targeted scope only
```

### `drift <path>` Mode (Deep Code-Doc)

```
Step 1: Read the specified doc
Step 2: Run Algorithm 2 (code-doc drift) thoroughly
Step 3: For each reference extracted, verify against codebase
Step 4: Present detailed mismatch report with evidence
```

### `cross-doc` Mode

```
Step 1: Run scan_freshness.py to get doc inventory
Step 2: Cluster docs by topic
Step 3: Run Algorithm 3 on overlapping pairs
Step 4: Present conflicts with doc references
```

### `report` Mode (Persist)

```
Step 1: Run full scan (same as scan mode)
Step 2: Format as markdown report
Step 3: Write to {output_dir}/{YYYY-MM-DD}-freshness.md
Step 4: Confirm file written
```

### `setup`

Scaffold a GitHub Actions workflow for automated documentation health checks using `joaquimscosta/docs-health-action`.

#### Step 1: Check existing setup

```bash
ls .github/workflows/docs-health.yml 2>/dev/null
```

- If file exists: "A docs-health workflow already exists at `.github/workflows/docs-health.yml`. Overwrite / skip?"
- If `.github/workflows/` doesn't exist: create it with `mkdir -p`

#### Step 2: Gather preferences

Use `AskUserQuestion` with two questions:

**Question 1** (multiSelect): "Which documentation health checks should run on every PR?"
- `links` — Broken internal links and missing anchors (Recommended)
- `versions` — Version references vs ground truth (.nvmrc, package.json, etc.)
- `staleness` — Git-based documentation age scoring
- `claude-md` — CLAUDE.md structural drift (Claude Code projects only)
- `cross-doc` — Cross-document version conflicts
- `frontmatter` — Missing tracking frontmatter

Default selection: links, versions, staleness.

**Question 2** (single): "When should the workflow fail?"
- `errors` — Fail on broken links and critical mismatches (Recommended)
- `warnings` — Also fail on staleness and minor version drift
- `none` — Advisory only, never fail

#### Step 3: Generate workflow file

Use the template below, substituting `{checks}` and `{fail_on}` from user selections:

```yaml
name: Documentation Health

on:
  pull_request:
    paths:
      - '**/*.md'
      - 'package.json'
      - '.nvmrc'
      - '.python-version'
      - 'pyproject.toml'
      - 'go.mod'
      - 'Cargo.toml'

permissions:
  contents: read
  pull-requests: write

jobs:
  docs-health:
    name: Documentation Health
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run documentation health checks
        uses: joaquimscosta/docs-health-action@v1
        with:
          checks: '{checks}'
          fail-on: '{fail_on}'
```

If `staleness` is NOT in the selected checks, remove `fetch-depth: 0` (shallow clone is faster).

If `claude-md` is in the selected checks and a `CLAUDE.md` exists, add `'CLAUDE.md'` to the paths filter.

#### Step 4: Present and confirm

Show the generated file content and ask: "Write to `.github/workflows/docs-health.yml`? (y/N)"

On confirmation, write the file.

#### Step 5: Post-setup guidance

After writing, print:

```
Workflow created at .github/workflows/docs-health.yml

Next steps:
1. Commit the workflow file: git add .github/workflows/docs-health.yml
2. Push to trigger on your next PR
3. The action will post a comment on PRs with documentation issues

To customize further, see: https://github.com/joaquimscosta/docs-health-action
```

---

## Output Templates

### Summary Table

```markdown
## Documentation Freshness Report

_Scanned {N} docs on {date}_

| Category | Count | Critical | Warning | Info |
|----------|-------|----------|---------|------|
| Broken Links | {n} | {n} | {n} | — |
| Version Mismatches | {n} | {n} | {n} | — |
| Stale Docs | {n} | — | {n} | {n} |
| Code-Doc Drift | {n} | {n} | {n} | {n} |
| Cross-Doc Conflicts | {n} | — | {n} | {n} |
```

### Findings Table

```markdown
### Findings

| # | Severity | Type | File:Line | Finding | Evidence |
|---|----------|------|-----------|---------|----------|
| 1 | CRITICAL | broken-link | README.md:45 | Link to deleted file | `docs/api.md` does not exist |
| 2 | WARNING | version | docs/setup.md:7 | Node version mismatch | Doc says 18, .nvmrc says 20 |
| 3 | WARNING | stale | docs/architecture.md | 45 days since last update | Code changed 2 days ago |
| 4 | CRITICAL | drift | docs/api.md:23 | Function removed | `createUser()` not found in codebase |
| 5 | WARNING | cross-doc | README.md:15 vs docs/setup.md:7 | Conflicting Node version | 18 vs 20 |
```

## Config File Reference

Optional configuration in `.arkhe.yaml`:

```yaml
doc-freshness:
  # Custom doc patterns (overrides defaults)
  doc_patterns:
    - "docs/**/*.md"
    - "wiki/**/*.md"
    - "README.md"

  # Files/patterns to exclude from scanning
  exclude:
    - "docs/archive/**"
    - "CHANGELOG.md"

  # Explicit doc-to-code mappings (supplements convention-based discovery)
  mappings:
    - doc: docs/api-reference.md
      code: src/api/**/*.ts
    - doc: docs/auth.md
      code: src/auth/**/*.ts

  # Version references to track against ground truth
  versions:
    - name: "Node.js"
      pattern: "node.*?(\\d+\\.\\d+)"
      source: ".nvmrc"
```

## Hook Integration

The doc-freshness skill integrates with Claude Code hooks for proactive freshness monitoring.

### SessionStart Hook (Critical-Doc Fast Scan)

**Trigger**: Session start (synchronous, 5-second timeout)

**Configuration** (in `.claude/settings.local.json`):
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check critical documentation freshness: README.md, CLAUDE.md. Use: /doc:health --critical-only\n\nSurface only if issues found (broken links or stale docs).",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**Behavior**: Scans critical root-level docs only (README.md, CLAUDE.md) to keep execution < 1 second. Surfaces alerts only if issues found.

### PostToolUse Hook (Post-Commit Doc-Impact Checks)

**Trigger**: After `/commit` command completes (async, non-blocking, 30-second timeout)

**Configuration** (in `.claude/settings.local.json`):
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Skill",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "After commit completed, check if modified code files lack corresponding documentation: /doc:health drift\n\nReport findings only if doc-code misalignment detected.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Behavior**: Runs asynchronously after commit succeeds. Checks if modified source files have corresponding documentation updates. Non-blocking — doesn't interrupt workflow.

### User-Driven Periodic Monitoring (`/loop`)

**Pattern**: `/loop <interval> /doc:health <mode>`

**Examples**:
```bash
/loop 1h /doc:health links        # Hourly broken-link checks
/loop 4h /doc:health scan         # Full scans every 4 hours
/loop 30m /doc:health drift       # Rapid post-commit checks
```

**Configuration**: No setup needed — user initiates based on session needs.

When no config is present, the skill uses convention-based discovery and default patterns.
