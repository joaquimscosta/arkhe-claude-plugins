# Code Review Troubleshooting

Common issues when using the code-review skill.

---

## Git Diff Issues

### "No diff output" or empty diff

**Cause**: No remote tracking branch, or `origin/HEAD` is not set.

**Fix**:
```bash
# Set origin/HEAD to the default branch
git remote set-head origin --auto

# Or specify the base branch explicitly
git diff --merge-base origin/main
```

### Diff is too large — review times out or context is truncated

**Cause**: PR contains too many changed files (generated code, lock files, large migrations).

**Fix**:
- Split large PRs into smaller, focused changes
- Exclude generated files: `git diff --merge-base origin/HEAD -- ':!package-lock.json' ':!*.generated.ts'`
- Review high-risk files individually rather than the full diff

---

## Finding Quality Issues

### Too many findings (noisy report)

**Symptoms**: Report has 10+ findings, most are low-signal or speculative.

**Fix**:
- The skill enforces a cap of 8 meaningful findings + 2 nits — if exceeded, the self-reflection step may not have run
- Check that confidence thresholds are applied: only >=7 confidence findings should appear
- Run `/review:verify-findings` on the report to filter false positives

### Too few findings (suspiciously clean)

**Symptoms**: Clean report on a PR with significant new functionality.

**Fix**:
- Verify the diff output contains all changed files
- Check that `origin/HEAD` points to the correct base branch
- Review manually for missed categories (security, performance, testing)

### False positives in report

**Symptoms**: Findings flag patterns that are established conventions or framework-handled concerns.

**Fix**:
- Run `/review:verify-findings {report-path}` for automatic false positive verification
- The verifier traces code paths and checks framework protections

---

## Output Issues

### Report directory creation fails

**Cause**: Permission denied or invalid path.

**Fix**: Ensure the output directory path is writable. Default is `./reviews/code/` relative to the project root.

### Report file already exists

The skill uses timestamped filenames (`{YYYY-MM-DD}_{HH-MM-SS}_code-review.md`), so collisions are rare. If running multiple reviews in the same second, the second review overwrites the first.
