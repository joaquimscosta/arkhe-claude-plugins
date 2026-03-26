# Doc-Freshness Troubleshooting

## No Documentation Files Found

**Symptom**: "No documentation files found" or empty results.

**Cause**: Docs are in non-standard locations not covered by default patterns.

**Fix**: Add custom patterns to `.arkhe.yaml`:

```yaml
doc-freshness:
  doc_patterns:
    - "guides/**/*.md"
    - "manual/**/*.md"
    - "wiki/**/*.rst"
```

## Too Many Broken Link False Positives

**Symptom**: Many broken links reported for paths that are intentional (code examples, templates).

**Cause**: Backtick-quoted paths in prose are treated as file references even when they're illustrative.

**Fix**: The checker only flags backtick paths containing `/` (directory separators). If you still get false positives, exclude specific docs:

```yaml
doc-freshness:
  exclude:
    - "docs/templates/**"
    - "docs/examples/**"
```

## Script Permission Denied

**Symptom**: `Permission denied` when running scan_freshness.py.

**Fix**:
```bash
chmod +x plugins/doc/skills/doc-freshness/scripts/*.py
```

## Python Version Error

**Symptom**: Syntax errors or `f-string` failures.

**Cause**: Python < 3.8 being used.

**Fix**: Ensure Python 3.8+ is available:
```bash
python3 --version
```

## Code Mapping Guesses Wrong

**Symptom**: Drift analysis compares doc against unrelated code files.

**Cause**: Convention-based mapping inferred the wrong code counterpart.

**Fix**: Add explicit mappings:

```yaml
doc-freshness:
  mappings:
    - doc: docs/payments.md
      code: src/billing/**/*.ts
```

## Git Staleness Unreliable

**Symptom**: Recently updated docs still flagged as stale.

**Cause**: The doc was touched (e.g., whitespace fix) but not meaningfully updated. Or the doc has no git history (new file not yet committed).

**Mitigation**: Staleness uses commit dates as a heuristic. Combine with `drift` mode for semantic accuracy — a stale date doesn't necessarily mean wrong content.

## Large Repository Slow

**Symptom**: Full scan takes too long on a monorepo.

**Cause**: Too many markdown files or deep directory trees.

**Fix Options**:
1. Use `check <path>` for targeted analysis
2. Use `links` mode for fast mechanical checks only
3. Add exclusions to reduce scope:

```yaml
doc-freshness:
  exclude:
    - "packages/legacy/**"
    - "docs/archive/**"
    - "vendor/**"
```

## Version Checker Finds No Versions

**Symptom**: "0 version mismatches" even though docs reference versions.

**Cause**: The version patterns only match common formats like "Node.js 18", "Python 3.8+", "Java 21". Uncommon formats or tool-specific versions aren't detected.

**Fix**: The checker handles Node.js, Python, Java, Go, Ruby, and Rust version references. For other tools, the code-doc drift analysis (`drift` mode) can catch specific version references via Grep.

## Cross-Doc Mode Finds No Overlaps

**Symptom**: "No overlapping topics detected" even though multiple docs cover the same subject.

**Cause**: The topic clustering uses heading keywords. If docs use very different heading text for the same topic, overlap won't be detected.

**Fix**: Use `check <path>` on specific docs you suspect conflict, or provide more context in the `cross-doc` invocation about which topics to compare.

## No Git Repository

**Symptom**: Staleness section shows "unknown" for all docs.

**Cause**: Not a git repository, or git is not installed.

**Impact**: Link checking and version checking still work normally. Only git-based staleness is unavailable. Use `drift` mode for semantic freshness checking instead.
