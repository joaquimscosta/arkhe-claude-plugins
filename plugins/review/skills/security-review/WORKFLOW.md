# Security Review Workflow

Detailed analysis methodology, false positive filtering, and sub-task orchestration.

## Security Categories — Detailed Subcategories

### Input Validation Vulnerabilities
- SQL injection via unsanitized user input
- Command injection in system calls or subprocesses
- XXE injection in XML parsing
- Template injection in templating engines
- NoSQL injection in database queries
- Path traversal in file operations

### Authentication & Authorization Issues
- Authentication bypass logic
- Privilege escalation paths
- Session management flaws
- JWT token vulnerabilities
- Authorization logic bypasses

### Crypto & Secrets Management
- Hardcoded API keys, passwords, or tokens
- Weak cryptographic algorithms or implementations
- Improper key storage or management
- Cryptographic randomness issues
- Certificate validation bypasses

### Injection & Code Execution
- Remote code execution via deserialization
- YAML deserialization vulnerabilities
- Eval injection in dynamic code execution
- XSS vulnerabilities in web applications (reflected, stored, DOM-based)

### Data Exposure
- Sensitive data logging or storage
- PII handling violations
- API endpoint data leakage
- Debug information exposure

---

## Analysis Methodology — Detailed Steps

### Phase 1: Repository Context Research

Use file search tools to:
- Identify existing security frameworks and libraries in use
- Look for established secure coding patterns in the codebase
- Examine existing sanitization and validation patterns
- Understand the project's security model and threat model

### Phase 2: Comparative Analysis

- Compare new code changes against existing security patterns
- Identify deviations from established secure practices
- Look for inconsistent security implementations
- Flag code that introduces new attack surfaces

### Phase 3: Vulnerability Assessment

- Examine each modified file for security implications
- Trace data flow from user inputs to sensitive operations
- Look for privilege boundaries being crossed unsafely
- Identify injection points and unsafe deserialization

**Note**: Even if something is only exploitable from the local network, it can still be a HIGH severity issue.

---

## Sub-Task Orchestration Pattern

Execute the analysis in 3 steps:

1. **Identify vulnerabilities** using a sub-task. Use repository exploration tools to understand codebase context, then analyze PR changes for security implications.

2. **Filter false positives** for each vulnerability identified. Launch these as parallel sub-tasks. Apply all false positive filtering rules below.

3. **Apply confidence threshold**: Filter out any vulnerabilities where the sub-task reported a confidence less than 8.

---

## False Positive Filtering Rules

### Hard Exclusions

Automatically exclude findings matching these patterns:

1. Denial of Service (DoS) vulnerabilities or resource exhaustion attacks
2. Secrets or credentials stored on disk if they are otherwise secured
3. Rate limiting concerns or service overload scenarios
4. Memory consumption or CPU exhaustion issues
5. Lack of input validation on non-security-critical fields without proven security impact
6. Input sanitization concerns for GitHub Action workflows unless clearly triggerable via untrusted input
7. Lack of hardening measures — only flag concrete vulnerabilities, not missing best practices
8. Race conditions or timing attacks that are theoretical rather than practical
9. Vulnerabilities related to outdated third-party libraries (managed separately)
10. Memory safety issues in memory-safe languages (Rust, Go, Java, etc.)
11. Files that are only unit tests or only used as part of running tests
12. Log spoofing concerns — outputting un-sanitized user input to logs is not a vulnerability
13. SSRF vulnerabilities that only control the path (only concern if controlling host or protocol)
14. Including user-controlled content in AI system prompts is not a vulnerability
15. Regex injection — injecting untrusted content into a regex is not a vulnerability
16. Regex DoS concerns
17. Insecure documentation — do not report findings in documentation/markdown files
18. Lack of audit logs is not a vulnerability

### Precedents

1. Logging high-value secrets in plaintext IS a vulnerability. Logging URLs is assumed safe.
2. UUIDs can be assumed unguessable and do not need validation.
3. Environment variables and CLI flags are trusted values. Attacks relying on controlling env vars are invalid.
4. Resource management issues (memory/file descriptor leaks) are not valid.
5. Subtle/low-impact web vulnerabilities (tabnabbing, XS-Leaks, prototype pollution, open redirects) should not be reported unless extremely high confidence.
6. React and Angular are generally secure against XSS. Do not report XSS unless using unsafe HTML injection methods explicitly.
7. Most GitHub Action workflow vulnerabilities are not exploitable in practice. Ensure a very specific attack path exists.
8. Lack of permission checking in client-side JS/TS is not a vulnerability (backend handles validation).
9. Only include MEDIUM findings if they are obvious and concrete issues.
10. Most notebook (*.ipynb) vulnerabilities are not exploitable in practice.
11. Logging non-PII data is not a vulnerability. Only report if exposing secrets, passwords, or PII.
12. Command injection in shell scripts is generally not exploitable (scripts don't run with untrusted input). Only report with a very specific untrusted-input attack path.

### Signal Quality Criteria

For each remaining finding, assess:
1. Is there a concrete, exploitable vulnerability with a clear attack path?
2. Does this represent a real security risk vs theoretical best practice?
3. Are there specific code locations and reproduction steps?
4. Would this finding be actionable for a security team?

Assign confidence score 1-10:
- **1-3**: Low confidence, likely false positive — discard
- **4-6**: Medium confidence, needs investigation — discard
- **7-10**: High confidence, likely true vulnerability — keep only if >= 8

---

## Report Template

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

# Vuln 1: {Category}: `{file}:{line}`

* Severity: {HIGH|MEDIUM}
* Confidence: {8-10}/10
* Description: {Detailed description of the vulnerability}
* Exploit Scenario: {Specific attack path with example payload}
* Recommendation: {Concrete fix with code example}

---

## Final Note

Focus on HIGH and MEDIUM findings only. Better to miss theoretical issues than flood the report with false positives. Each finding should be something a security engineer would confidently raise in a PR review.
```
