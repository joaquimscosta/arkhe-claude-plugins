# Security Review Workflow

Detailed category taxonomy, analysis methodology, false positive filtering, and sub-task orchestration.

---

## Security Categories — OWASP 2025 Taxonomy

### A01: Access Control Vulnerabilities
- **AC-IDOR**: Insecure Direct Object References — horizontal privilege escalation via ID manipulation
- **AC-PRIVESC**: Privilege Escalation — vertical escalation from user to admin
- **AC-SSRF**: Server-Side Request Forgery — internal network access, cloud metadata theft
  - Cloud metadata targets: AWS 169.254.169.254, GCP metadata.google.internal, Azure 169.254.169.254
  - Common vectors: webhook URLs, PDF generators, preview/proxy endpoints, file imports
  - Bypass techniques: IP encoding (decimal, hex, shortened), IPv6 loopback, DNS rebinding
- **AC-CORS**: CORS Misconfiguration — overly permissive cross-origin policies
- **AC-CSRF**: Cross-Site Request Forgery — state-changing actions without token verification
- **AC-PATH**: Path Traversal — accessing files outside intended scope

### A02: Security Misconfiguration
- Default or weak credentials in configuration files
- Debug endpoints or admin interfaces exposed in production
- Error messages exposing stack traces or implementation details
- Missing security headers (CSP, HSTS, X-Frame-Options)
- Cloud misconfiguration (public S3 buckets, over-permissioned IAM roles)
- XML External Entity (XXE) processing enabled
- Open redirects (CWE-601)

### A03: Software Supply Chain Failures (New in 2025)
- **SC-CONFUSION**: Dependency confusion — private package names on public registries
- **SC-TYPOSQUAT**: Typosquatting — lookalike package names
- **SC-CICD**: CI/CD pipeline risks — unpinned GitHub Actions, secrets in logs, GITHUB_TOKEN with write-all
- **SC-DEP**: Vulnerable dependencies — known CVEs in transitive dependencies
- **SC-SBOM**: Missing SBOM or provenance — untracked dependencies, no artifact signing
- **SC-LOCKFILE**: Missing or inconsistent lock files

### A04: Cryptographic Failures
- **CRYPTO-SECRET**: Hardcoded API keys, passwords, tokens in source code
- **CRYPTO-WEAK**: Weak algorithms — MD5/SHA-1 for hashing, RC4/DES/ECB mode
- **CRYPTO-RNG**: Insecure randomness — Math.random() for security-sensitive values
- **CRYPTO-CERT**: Certificate validation disabled (verify=False, InsecureSkipVerify)
- **CRYPTO-KEY**: Insufficient key length — RSA < 2048-bit
- **CRYPTO-TRANSIT**: Missing encryption in transit for sensitive data

### A05: Injection
- **INJ-SQL**: SQL Injection — string concatenation in queries, raw SQL with user input
- **INJ-NOSQL**: NoSQL Injection — MongoDB $where operator, unvalidated query objects
- **INJ-CMD**: OS Command Injection — unsanitized user input in subprocess/exec calls
- **INJ-XSS**: Cross-Site Scripting — stored, reflected, DOM-based variants
- **INJ-SSTI**: Server-Side Template Injection — Jinja2, Twig, Freemarker, EJS unescaped
- **INJ-LDAP**: LDAP Injection — unsanitized input in LDAP queries
- **INJ-LOG**: Log Injection — CRLF injection into log entries (only if PII/secrets exposed)
- **INJ-EXPR**: Expression Language Injection — Spring EL, OGNL

### A07: Authentication & Session Failures
- **AUTH-BYPASS**: Authentication bypass logic flaws
- **AUTH-SESSION**: Session management flaws — tokens not invalidated, excessive validity
- **AUTH-JWT**: JWT vulnerabilities — alg:none, weak secrets, missing expiration
- **AUTH-CRED**: Credential exposure — passwords in URLs, logs, or GET parameters
- **AUTH-MFA**: Missing MFA for privileged operations

### A08: Software & Data Integrity Failures
- **DESER-JAVA**: Java ObjectInputStream, XMLDecoder, Jackson enableDefaultTyping — CRITICAL
- **DESER-PY**: Python unsafe deserialization (yaml.load without SafeLoader) — CRITICAL
- **DESER-PHP**: PHP unserialize on HTTP parameters — CRITICAL
- **DESER-PROTO**: JavaScript Prototype Pollution via __proto__ manipulation
- **INTEGRITY-UPDATE**: Unsigned code updates, missing artifact signing

### A10: Mishandling of Exceptional Conditions (New in 2025)
- **ERR-FAILOPEN**: Fail-open patterns — defaulting to permissive state on error (e.g., auth bypass on timeout)
- **ERR-SWALLOW**: Bare except/catch blocks hiding security errors
- **ERR-VERBOSE**: Error messages revealing system internals to users
- **ERR-OVERFLOW**: Integer overflow/underflow in security-critical calculations

### API Security (OWASP API Top 10)
- **API-BOLA**: Broken Object Level Authorization — accessing other users' resources via ID
- **API-MASS**: Mass Assignment — binding user JSON to model without field filtering
- **API-INVENTORY**: Shadow/undocumented API endpoints
- **API-RATE**: Missing rate limiting on sensitive endpoints
- **API-CONSUME**: Trusting third-party API responses without validation

### LLM/AI Security (OWASP LLM Top 10 v2.0)
- **LLM-INJECT**: User input concatenated into LLM prompts without sanitization
- **LLM-OUTPUT**: LLM output used directly in SQL, shell commands, or rendered as unsanitized HTML
- **LLM-AGENCY**: LLM agent with destructive tool access without human-in-the-loop
- **LLM-LEAK**: System prompt leakage via extraction attacks
- **LLM-RAG**: RAG pipeline retrieving and trusting untrusted content

---

## Severity Assignment Quick Reference

| Category Code | Default Severity | Rationale |
|---------------|-----------------|-----------|
| INJ-SQL (confirmed user input) | CRITICAL | Direct data access, potential RCE |
| INJ-CMD (user input in exec calls) | CRITICAL | Direct RCE |
| DESER-JAVA / DESER-PY / DESER-PHP | CRITICAL | RCE via gadget chains |
| AUTH-BYPASS (admin bypass) | CRITICAL | Full system compromise |
| CRYPTO-SECRET (production keys) | HIGH | Credential compromise |
| AC-SSRF (internal network access) | HIGH | Cloud credential theft |
| INJ-XSS (stored, privileged context) | HIGH | Session hijacking |
| AC-IDOR (sensitive data) | HIGH | Data breach |
| AUTH-JWT (alg:none) | HIGH | Authentication bypass |
| LLM-OUTPUT (SQL/shell execution) | HIGH | Indirect code execution |
| SC-CICD (unpinned actions + secrets) | HIGH | Supply chain compromise |
| INJ-XSS (reflected) | MEDIUM | Requires user interaction |
| AC-CSRF (state-changing) | MEDIUM | Requires user interaction |
| CRYPTO-WEAK (MD5 for hashing) | MEDIUM | Depends on data sensitivity |
| ERR-FAILOPEN | MEDIUM | Auth bypass on error |
| CONFIG-HEADER (missing CSP) | LOW | Defense in depth |
| ERR-VERBOSE (stack traces) | LOW | Information disclosure |

### Exploitability Modifiers

**Increase severity by one tier if:**
- Vulnerability is internet-facing (public endpoint)
- No authentication required to reach the vulnerable code path
- Vulnerability is in payment, authentication, or PII-handling code
- Data flow from user input is confirmed

**Decrease severity by one tier if:**
- Code is only reachable by authenticated admins
- Feature is behind a disabled feature flag
- Vulnerability exists in development/test code only
- Mitigating control exists (WAF, network segmentation)

---

## Analysis Methodology — Detailed Steps

### Phase 1: Repository Context Research

Use file search tools to:
- Identify existing security frameworks and libraries in use (e.g., Spring Security, Django CSRF, helmet.js)
- Look for established sanitization and validation patterns
- Examine the project's security model and authentication architecture
- Check for existing security annotations or suppression comments

### Phase 1.5: Automated Security Scan (Optional)

Run the automated scan script to complement manual analysis with tool-based vulnerability and secret detection.

**Prerequisites**: `trivy`, `gitleaks`, `jq` (install via `brew install trivy gitleaks jq`).

**Script Discovery**:
```bash
# Locate the scan script
Glob for **/review/scripts/security-scan.sh
```

**Execution**:
```bash
# Run with --quick (skip git history for faster results) and output to the review directory
bash {script_path} --quick --output-dir {output-directory}
```

**Graceful Skip**: If the script reports tools are not installed (exit code 0 with skip messages), note "Automated Scan: Skipped — tools not installed" in the report summary and continue to Phase 2. Do not block the review.

**Parsing Results**: When scans complete, read the JSON reports from `{output-directory}/`:
- `trivy-*.json` — Dependency vulnerabilities and IaC misconfigurations. Cross-reference with A03 (Supply Chain) and A02 (Security Misconfiguration) findings.
- `gitleaks.json` — Detected secrets in git history. Cross-reference with A04 (Cryptographic Failures) findings.

**Cross-Referencing with Manual Analysis**:
- Trivy findings that overlap with manual supply-chain findings increase confidence to HIGH
- Gitleaks findings that overlap with manual hardcoded secret findings increase confidence to HIGH
- Automated findings that have no manual counterpart should be noted in the report but do not replace manual analysis
- Include automated scan summary (pass/fail/skip counts) in the report Summary section

### Phase 2: Comparative Analysis

- Compare new code changes against existing security patterns
- Identify deviations from established secure practices
- Look for inconsistent security implementations across similar code paths
- Flag code that introduces new attack surfaces (new endpoints, new user input handling)

### Phase 3: Vulnerability Assessment with Data Flow Tracing

For each potential finding, perform data flow analysis:
1. **Identify source** — user input entry point (HTTP params, headers, body, file uploads)
2. **Trace propagation** — assignments, transformations, function calls
3. **Confirm sink reachability** — the dangerous operation (SQL query, command execution, HTML render)
4. **Check for sanitizers** — parameterization, escaping, validation in the path
5. **Assess context** — authenticated? internet-facing? sensitive data involved?

**Note**: Even if something is only exploitable from the local network, it can still be a HIGH severity issue if it handles sensitive data.

---

## Sub-Task Orchestration Pattern

Execute the analysis in 3 steps:

1. **Identify vulnerabilities** using a sub-task. Use repository exploration tools to understand codebase context, then analyze PR changes for security implications across all OWASP 2025 categories.

2. **Filter false positives** for each vulnerability identified. Launch these as parallel sub-tasks. Apply all false positive filtering rules below.

3. **Apply signal quality matrix**: Filter out any findings that don't pass the severity/confidence matrix defined in SKILL.md.

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
9. Vulnerabilities related to outdated third-party libraries (managed separately by SCA tools)
10. Memory safety issues in memory-safe languages (Rust, Go, Java, etc.)
11. Files that are only unit tests or only used as part of running tests
12. Log spoofing concerns — outputting un-sanitized user input to logs is not a vulnerability
13. SSRF vulnerabilities that only control the path (only concern if controlling host or protocol)
14. Including user-controlled content in AI system prompts is not a vulnerability by itself
15. Regex injection — injecting untrusted content into a regex is not a vulnerability
16. Regex DoS concerns
17. Insecure documentation — do not report findings in documentation/markdown files
18. Lack of audit logs is not a vulnerability

### Framework-Aware Suppression Rules

Apply these when the corresponding framework is detected in the codebase:

| Framework | Safe Pattern | Unsafe Pattern (flag only this) |
|-----------|-------------|-------------------------------|
| Django templates | Auto-escaped by default | `safe` filter or `mark_safe()` |
| React JSX | Renders are safe by default | Unsafe innerHTML prop |
| Angular | Auto-escaped by default | `bypassSecurityTrust*()` methods |
| Spring/JPA | `@Query` with named parameters | String concatenation in queries |
| Rails ActiveRecord | `.where` with hash syntax | `.where` with string interpolation |
| Express + helmet | Headers set by middleware | Missing `helmet()` call |
| subprocess (Python) | Argument list form | shell=True with user input |

### Sanitizer Recognition

Before flagging injection vulnerabilities, check if any recognized sanitizers exist in the data flow path:

**Python**: `html.escape()`, `bleach.clean()`, parameterized queries, `shlex.quote()`
**Java**: `ESAPI.encoder()`, `HtmlUtils.htmlEscape()`, PreparedStatement, Spring `@Param`
**JavaScript**: `DOMPurify.sanitize()`, `validator.escape()`, parameterized queries
**Go**: `html.EscapeString()`, parameterized `database/sql` queries
**Custom**: Look for wrapper functions with names like `sanitize`, `escape`, `clean`, `safe`

### Entropy-Based Secret Detection

When evaluating hardcoded secrets (CRYPTO-SECRET):
- Real secrets have high entropy (> 3.5 bits/char for hex, > 4.5 for base64)
- Exclude known placeholder patterns: `example.com`, `localhost`, `test`, `dummy`, `placeholder`, `YOUR_API_KEY`, `XXXXXXXX`, `changeme`
- Exclude template variables: `${VAR}`, `{{var}}`, `<API_KEY>`
- Environment variables and CLI flags are trusted values — attacks relying on controlling env vars are invalid

### Precedents

1. Logging high-value secrets in plaintext IS a vulnerability. Logging URLs is assumed safe.
2. UUIDs can be assumed unguessable and do not need validation.
3. Environment variables and CLI flags are trusted values.
4. Resource management issues (memory/file descriptor leaks) are not valid.
5. Subtle/low-impact web vulnerabilities (tabnabbing, XS-Leaks, open redirects) should not be reported unless extremely high confidence.
6. React and Angular are generally secure against XSS. Do not report XSS unless using explicitly unsafe HTML injection methods.
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

If any answer is "no", suppress the finding.

---

## Report Template

```markdown
# Security Review Report

**Date**: {ISO 8601 date}
**Branch**: {current branch name}
**Commit**: {short commit hash}
**Reviewer**: Claude Code (security-review)
**Framework**: OWASP Top 10 2025 + API Top 10 + LLM Top 10

## Summary
- **Blocker**: {count} findings
- **Improvement**: {count} findings
- **Question**: {count} findings
- **Total**: {count} actionable findings
- **Automated Scan**: {Passed | X issues found | Skipped — tools not installed}

---

### [Blocker] Vuln 1: {Category Code}: `{file}:{line}`

* **Severity**: {CRITICAL|HIGH}
* **Confidence**: HIGH
* **Category**: {OWASP A0X:2025}
* **CWE**: CWE-XXX
* **Description**: {Detailed description of the vulnerability}
* **Exploit Scenario**: {Specific attack path with example payload}
* **Recommendation**: {Concrete fix with code example}

---

## Final Note

Focus on Blocker and Improvement findings. Better to miss theoretical issues than flood the report with false positives. Each finding should be something a security engineer would confidently raise in a PR review.
```
