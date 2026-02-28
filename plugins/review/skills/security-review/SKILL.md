---
name: security-review
description: >
  Security-focused code review identifying high-confidence exploitable vulnerabilities
  with false positive filtering and parallel sub-task verification.
  Use when user runs /security-review, /review:security-review, requests a "security review",
  "security audit", "vulnerability scan", or mentions "find vulnerabilities", "check for exploits".
disable-model-invocation: true
argument-hint: "[output-directory]"
---

# Security Review

Identify HIGH-CONFIDENCE security vulnerabilities with real exploitation potential. Focus on impact, minimize false positives.

## Parse Arguments

**Output Path Configuration**:
- If `$ARGUMENTS` is provided and non-empty: Use `$ARGUMENTS` as the output directory
- Otherwise: Use default `./reviews/security/`

## Git Analysis

GIT STATUS:

```
!`git status`
```

FILES MODIFIED:

```
!`git diff --name-only origin/HEAD...`
```

COMMITS:

```
!`git log --no-decorate origin/HEAD...`
```

DIFF CONTENT:

```
!`git diff --merge-base origin/HEAD`
```

Review the complete diff above. Focus ONLY on security implications newly added by this PR.

## Objective

- Only flag issues where you're **>80% confident** of actual exploitability
- Skip theoretical issues, style concerns, or low-impact findings
- Prioritize vulnerabilities leading to unauthorized access, data breaches, or system compromise
- Do NOT report: DoS vulnerabilities, secrets stored on disk, rate limiting issues

## Security Categories

| Category | Key Checks |
|----------|------------|
| Input Validation | SQL injection, command injection, XXE, template injection, path traversal |
| Auth & Authorization | Authentication bypass, privilege escalation, session flaws, JWT vulns |
| Crypto & Secrets | Hardcoded keys, weak algorithms, improper key storage, cert validation |
| Injection & RCE | Deserialization, eval, XSS (reflected/stored/DOM), unsafe dynamic code |
| Data Exposure | Sensitive data logging, PII handling, API leakage, debug info exposure |

See [WORKFLOW.md](WORKFLOW.md) for detailed subcategories.

## Analysis Methodology

**Phase 1 — Repository Context Research**: Identify existing security frameworks, patterns, and sanitization in the codebase.

**Phase 2 — Comparative Analysis**: Compare new code against established secure practices. Flag deviations and new attack surfaces.

**Phase 3 — Vulnerability Assessment**: Trace data flow from user inputs to sensitive operations. Identify injection points and unsafe boundaries.

See [WORKFLOW.md](WORKFLOW.md) for detailed methodology and sub-task orchestration pattern.

## Severity Guidelines

| Severity | Criteria |
|----------|----------|
| **HIGH** | Directly exploitable: RCE, data breach, authentication bypass |
| **MEDIUM** | Requires specific conditions but significant impact |
| **LOW** | Defense-in-depth issues or lower-impact vulnerabilities |

## Confidence Scoring

- **0.9-1.0**: Certain exploit path identified
- **0.8-0.9**: Clear vulnerability pattern with known exploitation methods
- **0.7-0.8**: Suspicious pattern requiring specific conditions
- **Below 0.7**: Do not report (too speculative)

## Output Format

For each vulnerability found:

```markdown
# Vuln N: {Category}: `{file}:{line}`

* Severity: {HIGH|MEDIUM}
* Description: {What the vulnerability is and how it can be exploited}
* Exploit Scenario: {Specific attack path demonstrating exploitability}
* Recommendation: {Concrete fix with code reference}
```

## Output Instructions

1. **Create output directory** using Bash: `mkdir -p {output-directory}`
2. **Save the report** to: `{output-directory}/{YYYY-MM-DD}_{HH-MM-SS}_security-review.md`

Include this header:

```markdown
# Security Review Report

**Date**: {ISO 8601 date}
**Branch**: {current branch name}
**Commit**: {short commit hash}
**Reviewer**: Claude Code (security-review)
**Confidence Threshold**: 8/10 minimum

## Summary
- **HIGH Severity**: {count} findings
- **MEDIUM Severity**: {count} findings
- **Total**: {count} actionable vulnerabilities

---
```

3. **Display the full report** to the user in the chat
4. **Confirm the save**: Security report saved to: {output-directory}/{filename}

## False Positive Filtering

Apply the false positive filtering rules from [WORKFLOW.md](WORKFLOW.md) before finalizing. Each finding must pass the signal quality criteria with confidence >= 8/10.

## Resources

- [WORKFLOW.md](WORKFLOW.md) - Detailed analysis methodology, false positive filtering rules, sub-task orchestration
- [EXAMPLES.md](EXAMPLES.md) - Sample security review reports
