# PR Issue Resolver: Troubleshooting

Solutions to common issues when using the `resolving-pr-issues` skill.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).
For examples, see [EXAMPLES.md](EXAMPLES.md).

---

## gh CLI Issues

### Issue: Authentication Failure

**Symptom**: All `gh` commands fail with "authentication required" or "401 Unauthorized".

**Solution**:

```bash
gh auth status    # Check current auth
gh auth login     # Re-authenticate
```

Ensure the token has `repo` scope for private repositories and `read:discussion` for PR comments.

### Issue: Rate Limiting

**Symptom**: `gh api` calls fail with "403 rate limit exceeded".

**Solution**: Wait for the rate limit to reset (shown in the error message). For large PRs with many comments, the skill batches API calls to stay within limits. If the issue persists, use a personal access token with higher rate limits.

### Issue: Missing Repository Permissions

**Symptom**: Can view PR but cannot post comments or push commits.

**Solution**: Ensure your token has `repo` scope (not just `public_repo`). For organization repos, check that your account has write access to the repository.

---

## Comment API Issues

### Issue: Inline vs General Comment Confusion

**Symptom**: Reply posted as a new general comment instead of in the review thread.

**Cause**: GitHub has two separate comment APIs:
- Inline review comments: `pulls/{pr}/comments` — supports thread replies
- General issue comments: `issues/{pr}/comments` — does NOT support threading

**Solution**: The skill detects comment type in Phase 1. Inline comments are replied to via the thread API. General comments get a single consolidated response with anchor links. If misclassified, check the comment ID format — inline comments have `pull_request_review_id` and `diff_hunk` fields.

### Issue: 404 on Comment Reply

**Symptom**: `gh api` returns 404 when replying to a comment.

**Causes**:
- Comment was deleted by the reviewer after extraction
- Comment ID is from the wrong API endpoint (inline ID used with general endpoint or vice versa)
- PR was closed or merged between Phase 1 and Phase 5

**Solution**: Re-fetch the comment to verify it still exists. If deleted, skip the reply. If the PR was closed, inform the user and skip Phase 5.

### Issue: Reply Creates Duplicate Thread

**Symptom**: Multiple reply threads appear on the same review comment.

**Cause**: Retrying a failed reply that actually succeeded (network timeout with server-side success).

**Solution**: Before retrying a reply, check if your response already appears in the thread via `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`.

---

## Multi-Agent Pipeline Issues

### Issue: Verification Agent Timeout

**Symptom**: One or more Phase 2 agents don't return results.

**Solution**: The skill continues with results from successful agents and notes the gap in the triage report. If most agents fail, it falls back to sequential verification (reading the code directly instead of using agents).

### Issue: Zero Actionable Comments Found

**Symptom**: Phase 1 returns no unresolved comments.

**Causes**:
- All review threads are already resolved
- PR has only bot comments (CI, coverage) or approval comments
- Comments are from the PR author (self-review, filtered out)

**Solution**: The skill reports "Nothing to resolve" and stops. If you believe comments exist, check the PR directly with `gh pr view {number}` and verify review threads are unresolved.

### Issue: All Findings Filtered (Below Threshold)

**Symptom**: Phase 2 returns findings but all score below 80.

**Solution**: This means the verification agents determined all suggestions are low-confidence (false positives or nitpicks). The skill presents the filtered results for transparency and asks if you want to lower the threshold or address specific items anyway.

---

## Resolution Issues

### Issue: Merge Conflict After Applying Changes

**Symptom**: `git push` fails with merge conflict after committing fixes.

**Solution**: Rebase the branch against the base:

```bash
git fetch origin
git rebase origin/{base-branch}
# Resolve conflicts
git push --force-with-lease
```

The skill attempts rebase automatically. If conflicts are complex, it stops and asks for help.

### Issue: Tests Fail After Fix

**Symptom**: A fix addresses the review comment but breaks existing tests.

**Solution**: The skill stops immediately when tests fail — it does not push broken code. Investigate the root cause: the fix may need adjustment, or the test may need updating. The skill presents the failure and asks for guidance before continuing.

### Issue: Pre-Commit Hook Blocks Commit

**Symptom**: Commit fails due to linting, formatting, or other pre-commit hooks.

**Solution**: Fix the hook violations (usually formatting). The skill runs the fix through formatters if detected. If the hook is unrelated to the change, investigate rather than bypassing with `--no-verify`.

---

## File Mode Issues

### Issue: Unrecognized Report Format

**Symptom**: File mode agent cannot parse the review report.

**Cause**: The report doesn't match expected formats (code-review skill template, generic markdown with file:line references).

**Solution**: The skill supports these formats:
- Code-review skill reports: `## Findings` with `**[Blocker]**`, `**[Improvement]**` markers
- Generic markdown: numbered lists with `file:line` references
- Plain text: lines containing file paths and line numbers

If the format isn't recognized, the agent extracts whatever actionable items it can find and presents them for confirmation.

### Issue: File Path Not Found

**Symptom**: Findings reference files that don't exist in the current working directory.

**Cause**: The review was generated from a different branch or the files have since been moved/deleted.

**Solution**: The skill checks each referenced file before verification. Missing files are flagged as "cannot verify" in the triage report. If many files are missing, it suggests checking out the correct branch.

---

## Edge Cases

### Issue: PR Closed During Resolution

**Symptom**: PR is closed or merged between Phase 1 and Phase 5.

**Solution**: The skill re-checks PR status before pushing (Phase 5). If closed, it informs the user and offers to keep the local commits for manual application.

### Issue: Reviewer Deletes Comment

**Symptom**: A comment extracted in Phase 1 no longer exists in Phase 5.

**Solution**: Skip the reply for that comment. The fix is still valid — it was verified against the code, not just the comment.

### Issue: Branch Protection Prevents Push

**Symptom**: `git push` fails due to branch protection rules (required reviews, status checks).

**Solution**: The skill cannot bypass branch protection. It informs the user and suggests:
1. Push to a separate branch and create a follow-up PR
2. Ask a repository admin to temporarily adjust protection rules
3. Push with `--force-with-lease` if the protection only requires linear history

---

## Getting Help

- [GitHub CLI docs](https://cli.github.com/manual/)
- [GitHub REST API — Pull Request Comments](https://docs.github.com/en/rest/pulls/comments)
- [GitHub REST API — Issue Comments](https://docs.github.com/en/rest/issues/comments)
- File issues at the plugin repository
