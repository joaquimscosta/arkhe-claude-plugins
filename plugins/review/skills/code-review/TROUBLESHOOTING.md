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

## Multi-Agent Pipeline Issues

### A reviewer agent fails or times out

**Symptoms**: Report notes "Note: {reviewer-name} did not complete. Partial review."

**Fix**: This is expected behavior — the pipeline continues with results from successful agents. If a specific reviewer consistently fails:
- Check if the diff is too large for that reviewer's scope
- The Git History reviewer (Reviewer 3) may time out on files with extensive blame history
- Rerun the review to retry

### All reviewer agents fail

**Symptoms**: Report uses single-agent fallback mode instead of multi-agent.

**Fix**: This typically indicates a systemic issue:
- Check network connectivity (agents need to spawn)
- Verify the diff content is valid and non-empty
- The fallback produces a valid review using the same methodology

### Reviewer 5 (Code Comments) never runs

**Symptoms**: Only 4 reviewers launch instead of 5.

**Fix**: This is intentional. Reviewer 5 only launches when modified files contain substantive code comments (`// NOTE:`, `// IMPORTANT:`, `// INVARIANT:`, `// SAFETY:`, `// TODO:`). If no such comments exist, it's skipped to save resources.

---

## Confidence Scoring Issues

### All findings filtered out (score < 80)

**Symptoms**: Clean report on a branch with significant changes.

**Fix**: This means all reviewer findings were scored below the confidence threshold. This is expected for:
- Clean, well-written code
- Changes that follow established patterns
- Minor refactors with no behavioral changes

If you believe issues were missed, check the reviewer outputs before scoring was applied.

### Scoring seems inconsistent

**Symptoms**: Similar issues scored very differently.

**Fix**: Each finding is scored by an independent Haiku agent. Slight variation is expected. The 80 threshold is calibrated to filter speculative findings while keeping real issues. If a finding was incorrectly filtered, run the review again — scoring agents may produce slightly different results.

### Too many findings survive filtering

**Symptoms**: Report has 8+ findings after scoring.

**Fix**: If many findings score 80+, it indicates genuine issues in the code. The pipeline does not impose an arbitrary cap — all high-confidence findings are reported. Address the highest-confidence ones first. If the report feels overwhelming, focus on Blockers before Improvements.

### Scoring agent fails for a finding

**Symptoms**: A finding appears in the report without a confidence score justification, or the report notes a scoring agent failure.

**Fix**: When a scoring agent fails, the finding defaults to a score of 80 (at threshold) and stays in the report. This is the expected safe behavior — it prevents real issues from being silently dropped. If the finding is a false positive, run `/review:verify-findings` on the report for additional verification.

---

## GitHub PR Posting Issues

### "No open PR found" when PR exists

**Cause**: `gh pr view` can't find the PR for the current branch.

**Fix**:
```bash
# Verify gh CLI is authenticated
gh auth status

# Check if PR exists for this branch
gh pr list --head $(git branch --show-current)

# If branch isn't pushed, push first
git push -u origin $(git branch --show-current)
```

### PR comment fails to post

**Cause**: Permission denied or PR state changed during review.

**Fix**:
- Verify `gh auth status` shows correct permissions
- Check if the PR was closed/merged during the review
- Ensure you have write access to the repository

### PR posting skipped — "already reviewed"

**Cause**: The eligibility check detected a previous Claude Code review comment on the PR.

**Fix**: This prevents duplicate reviews. If you want to re-review:
- Delete the previous review comment on the PR
- Run `/review:code-review --post-to-pr` again

---

## Finding Quality Issues

### Too many findings (noisy report)

**Symptoms**: Report has many low-signal or speculative findings.

**Fix**:
- The pipeline enforces a confidence threshold of 80/100 — findings below this are filtered
- If noise persists, run `/review:verify-findings` on the report for additional false positive verification
- Check that the diff doesn't include generated files or lock files

### Too few findings (suspiciously clean)

**Symptoms**: Clean report on a branch with significant new functionality.

**Fix**:
- Verify the diff output contains all changed files
- Check that `origin/HEAD` points to the correct base branch
- Review manually for missed categories (security, performance, testing)

### False positives in report

**Symptoms**: Findings flag patterns that are established conventions or framework-handled concerns.

**Fix**:
- Run `/review:verify-findings {report-path}` for automatic false positive verification
- The verifier traces code paths and checks framework protections
- Phase 3 scoring should catch most false positives — if it didn't, the finding may warrant closer inspection

---

## Output Issues

### Report directory creation fails

**Cause**: Permission denied or invalid path.

**Fix**: Ensure the output directory path is writable. Default is `./reviews/code/` relative to the project root.

### Report file already exists

The skill uses timestamped filenames (`{YYYY-MM-DD}_{HH-MM-SS}_code-review.md`), so collisions are rare. If running multiple reviews in the same second, the second review overwrites the first.
