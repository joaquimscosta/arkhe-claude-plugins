# Security Review Troubleshooting

Common issues and calibration guidance for the security-review skill.

---

## Git Diff Issues

### "No diff output" or empty diff

**Cause**: No remote tracking branch, or `origin/HEAD` is not set.

**Fix**:
```bash
# Set origin/HEAD to the default branch
git remote set-head origin --auto

# Or specify the base branch explicitly in your review workflow
git diff --merge-base origin/main
```

### "Diff is too large" — review times out or context is truncated

**Cause**: PR contains too many changed files (e.g., generated code, lock files, large migrations).

**Fix**:
- Split large PRs into smaller, focused changes
- Exclude generated files from the diff: `git diff --merge-base origin/HEAD -- ':!package-lock.json' ':!*.generated.ts'`
- Review high-risk files individually rather than the full diff

---

## Finding Quality Issues

### Too many findings (noisy report)

**Symptoms**: Report has 10+ findings, most are LOW severity or speculative.

**Causes**:
1. Confidence threshold not being applied correctly
2. Framework-aware suppression rules not triggered
3. Hard exclusions not filtering theoretical issues

**Fixes**:
- Verify the signal quality matrix is applied: only report findings in the "Report" cells
- Check if the codebase uses a framework with built-in protections (React, Django, Spring Security) — these should suppress many XSS and CSRF findings
- Re-read the Hard Exclusions list in WORKFLOW.md — common over-reports include DoS concerns, missing rate limiting, and theoretical race conditions
- Apply the finding cap: max 8 meaningful findings + 2 nits

### Too few findings (suspiciously clean)

**Symptoms**: Clean report on a PR that introduces significant new functionality with user input handling.

**Causes**:
1. Diff not captured correctly (see Git Diff Issues above)
2. Phase 1 context research didn't identify security-sensitive code paths
3. Analysis focused only on traditional OWASP categories, missing supply chain or API security issues

**Fixes**:
- Verify the diff output contains all changed files
- Manually check for new endpoints, user input handling, and external service calls
- Review against all 10 security categories in SKILL.md, including A03 (Supply Chain), A10 (Error Handling), API, and LLM categories

### False positive in report

**Symptoms**: A finding describes a theoretical vulnerability that the framework or existing code already handles.

**Common false positive patterns**:
- XSS flagged in React JSX (React auto-escapes by default)
- SQL injection flagged on ORM parameterized queries
- CSRF flagged when the framework has built-in CSRF middleware
- Command injection flagged on subprocess with argument list (not shell mode)
- Hardcoded secrets that are actually placeholder/example values

**Fixes**:
- Apply framework-aware suppression rules from WORKFLOW.md
- Check for sanitizers in the data flow path
- Verify entropy for secret detection (placeholders have low entropy)

---

## Severity Calibration

### When to use CRITICAL vs HIGH

| Use CRITICAL when... | Use HIGH when... |
|---------------------|-----------------|
| RCE is achievable (command injection, deserialization) | Data read access (SQLi read-only, SSRF info leak) |
| Full authentication bypass (admin access) | Stored XSS in privileged context |
| Mass data exfiltration (SQLi with write) | Single-user data breach (IDOR) |
| No authentication required | Authentication required but bypassable |

### When to suppress MEDIUM findings

Suppress MEDIUM findings unless they are:
- Obvious and concrete (not theoretical)
- Backed by HIGH confidence (data flow confirmed)
- Actionable without additional investigation

### Exploitability modifier confusion

**Problem**: Unsure whether to increase or decrease severity.

**Rule of thumb**:
- If an average attacker with public knowledge could exploit it: increase
- If exploitation requires insider access, disabled features, or chained bugs: decrease
- When in doubt, keep the default severity from the quick reference table

---

## Category Selection

### Finding doesn't fit any category

If a vulnerability doesn't map cleanly to the taxonomy codes:
1. Use the closest OWASP category (A01-A10)
2. Add the CWE identifier for specificity
3. Describe the actual vulnerability clearly — the category is secondary to the finding quality

### Overlapping categories

Some vulnerabilities span multiple categories (e.g., an SSRF that also exposes secrets):
- Use the **primary** category that describes the root cause
- Mention the secondary impact in the description
- Example: SSRF (AC-SSRF) that leads to credential theft — primary is AC-SSRF, mention CRYPTO-SECRET impact in description

---

## Output Issues

### Report directory creation fails

**Cause**: Permission denied or invalid path.

**Fix**: Ensure the output directory path is writable. Default is `./reviews/security/` relative to the project root.

### Report file already exists

The skill uses timestamped filenames (`{YYYY-MM-DD}_{HH-MM-SS}_security-review.md`), so collisions are unlikely. If running multiple reviews in the same second, the second review will overwrite the first — wait a moment between runs.
