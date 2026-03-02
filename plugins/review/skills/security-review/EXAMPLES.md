# Security Review Examples

## Invocation

```bash
# Default output path
/review:security-review

# Custom output path
/review:security-review audits/security/
```

## Sample Report — Multiple Vulnerabilities

```markdown
# Security Review Report

**Date**: 2026-02-28T09:45:00Z
**Branch**: feat/user-api
**Commit**: f7g8h9i
**Reviewer**: Claude Code (security-review)
**Framework**: OWASP Top 10 2025 + API Top 10 + LLM Top 10

## Summary
- **Blocker**: 2 findings
- **Improvement**: 1 finding
- **Question**: 1 finding
- **Total**: 4 actionable findings

---

### [Blocker] Vuln 1: INJ-SQL: `src/api/search.ts:28`

* **Severity**: CRITICAL
* **Confidence**: HIGH
* **Category**: OWASP A05:2025 — Injection
* **CWE**: CWE-89
* **Description**: The search query parameter is concatenated directly into a SQL
  string via `db.raw()`, bypassing Knex ORM parameterization. User input flows
  directly from the request query parameter to the SQL execution sink with no
  sanitization.
* **Exploit Scenario**: Attacker sends
  `GET /api/search?q=' UNION SELECT username, password FROM users --`
  to exfiltrate credentials via UNION-based injection.
* **Recommendation**: Use Knex parameterized binding:

Before:
` ``typescript
const results = db.raw(`SELECT * FROM products WHERE name LIKE '%${query}%'`);
` ``

After:
` ``typescript
const results = db('products').where('name', 'like', `%${query}%`);
` ``

---

### [Blocker] Vuln 2: AC-SSRF: `src/services/webhook.ts:45`

* **Severity**: HIGH
* **Confidence**: HIGH
* **Category**: OWASP A01:2025 — Broken Access Control
* **CWE**: CWE-918
* **Description**: The webhook endpoint accepts a user-supplied URL and fetches it
  server-side without validating the target host or protocol. This allows attackers
  to probe internal services and access cloud metadata endpoints.
* **Exploit Scenario**: Attacker sends
  `POST /api/webhooks {"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}`
  to steal AWS IAM credentials.
* **Recommendation**: Validate URLs against an allowlist and block private IP ranges.
  Resolve DNS and re-check IP to prevent DNS rebinding. Only allow HTTPS protocol.

---

### [Improvement] Vuln 3: SC-CICD: `.github/workflows/deploy.yml:12`

* **Severity**: HIGH
* **Confidence**: MEDIUM
* **Category**: OWASP A03:2025 — Software Supply Chain Failures
* **CWE**: CWE-829
* **Description**: GitHub Action `actions/setup-node` is referenced with a mutable
  tag (`@v4`) instead of a pinned SHA hash. A compromised action maintainer could
  inject malicious code into the CI/CD pipeline.
* **Exploit Scenario**: Attacker compromises the action repository and pushes
  malicious code to the `v4` tag. Next pipeline run executes attacker-controlled
  code with access to repository secrets.
* **Recommendation**: Pin actions to full SHA hashes:

Before:
` ``yaml
- uses: actions/setup-node@v4
` ``

After:
` ``yaml
- uses: actions/setup-node@1a4442cacd436585916f9e20e25f6e9e6e5ffd38  # v4.2.0
` ``

---

### [Question] Vuln 4: ERR-FAILOPEN: `src/middleware/auth.ts:67`

* **Severity**: MEDIUM
* **Confidence**: MEDIUM
* **Category**: OWASP A10:2025 — Mishandling of Exceptional Conditions
* **CWE**: CWE-636
* **Description**: The authentication middleware catches all exceptions and calls
  `next()` without the error parameter, effectively granting access when token
  validation fails due to unexpected errors (database timeout, library crash).
* **Exploit Scenario**: If the JWT verification service is temporarily unavailable,
  all requests pass through authentication unchecked.
* **Recommendation**: Fail closed — deny access on unexpected errors by returning
  a 401 response instead of passing through to the next middleware.

---

### [Praise] Good use of parameterized queries in `src/api/users.ts`

The user CRUD endpoints consistently use Knex query builder with parameterized
bindings, preventing SQL injection across all user data operations.

---
```

## Sample Report — Clean Review

```markdown
# Security Review Report

**Date**: 2026-02-28T14:20:00Z
**Branch**: refactor/config-module
**Commit**: j1k2l3m
**Reviewer**: Claude Code (security-review)
**Framework**: OWASP Top 10 2025 + API Top 10 + LLM Top 10

## Summary
- **Blocker**: 0 findings
- **Improvement**: 0 findings
- **Question**: 0 findings
- **Total**: 0 actionable findings

---

No high-confidence security vulnerabilities were identified in this change set.

The refactoring maintains existing security patterns and does not introduce new
attack surfaces. Configuration handling continues to use validated environment
variables through the existing config module.

---
```

## Sample Report — With Automated Scan Results

```markdown
# Security Review Report

**Date**: 2026-03-01T10:15:00Z
**Branch**: feat/payment-service
**Commit**: a1b2c3d
**Reviewer**: Claude Code (security-review)
**Framework**: OWASP Top 10 2025 + API Top 10 + LLM Top 10

## Summary
- **Blocker**: 1 finding
- **Improvement**: 1 finding
- **Question**: 0 findings
- **Total**: 2 actionable findings
- **Automated Scan**: 3 issues found (2 Trivy vulnerabilities, 1 Gitleaks secret)

---

### [Blocker] Vuln 1: CRYPTO-SECRET: `src/config/stripe.ts:14`

* **Severity**: HIGH
* **Confidence**: HIGH (corroborated by Gitleaks automated scan)
* **Category**: OWASP A04:2025 — Cryptographic Failures
* **CWE**: CWE-798
* **Description**: Stripe secret key is hardcoded in the configuration file. Gitleaks
  also detected this secret in git history (commit a1b2c3d), confirming the key has
  been committed to the repository.
* **Exploit Scenario**: Any developer or attacker with repository access can extract
  the production Stripe secret key and process fraudulent charges.
* **Recommendation**: Move the key to an environment variable and rotate the
  compromised key immediately. Run `gitleaks detect` to verify no other secrets
  remain in git history.

---

### [Improvement] Vuln 2: SC-DEP: `package.json`

* **Severity**: HIGH
* **Confidence**: MEDIUM (identified by Trivy automated scan)
* **Category**: OWASP A03:2025 — Software Supply Chain Failures
* **CWE**: CWE-1395
* **Description**: Trivy detected 2 HIGH severity vulnerabilities in transitive
  dependencies: CVE-2026-1234 in `lodash@4.17.20` (prototype pollution) and
  CVE-2026-5678 in `express@4.18.1` (path traversal). These are in the dependency
  tree of the payment service.
* **Recommendation**: Update affected dependencies: `pnpm update lodash express`.
  Review Trivy report at `reviews/security/trivy-payment-service.json` for full details.

---
```

## Sample Report — Automated Scan Skipped

```markdown
# Security Review Report

**Date**: 2026-03-01T14:00:00Z
**Branch**: fix/input-validation
**Commit**: e5f6g7h
**Reviewer**: Claude Code (security-review)
**Framework**: OWASP Top 10 2025 + API Top 10 + LLM Top 10

## Summary
- **Blocker**: 0 findings
- **Improvement**: 0 findings
- **Question**: 0 findings
- **Total**: 0 actionable findings
- **Automated Scan**: Skipped — tools not installed

---

No high-confidence security vulnerabilities were identified in this change set.

Note: Automated scanning (Trivy, Gitleaks) was skipped because the tools are not
installed. Install with `brew install trivy gitleaks jq` for dependency vulnerability
and secret detection coverage.

---
```

## Sample Report — LLM/AI Integration Review

```markdown
# Security Review Report

**Date**: 2026-02-28T11:30:00Z
**Branch**: feat/ai-assistant
**Commit**: x4y5z6a
**Reviewer**: Claude Code (security-review)
**Framework**: OWASP Top 10 2025 + API Top 10 + LLM Top 10

## Summary
- **Blocker**: 1 finding
- **Improvement**: 1 finding
- **Question**: 0 findings
- **Total**: 2 actionable findings

---

### [Blocker] Vuln 1: LLM-OUTPUT: `src/ai/assistant.ts:89`

* **Severity**: HIGH
* **Confidence**: HIGH
* **Category**: OWASP LLM Top 10 — LLM05
* **CWE**: CWE-94
* **Description**: The AI assistant's response is rendered directly into the DOM
  without sanitization. LLM output may contain HTML/JavaScript if the model is
  manipulated via prompt injection, enabling stored XSS through the AI chat
  interface.
* **Exploit Scenario**: User sends a crafted message that causes the LLM to output
  malicious HTML/script tags. This executes in the browser of any user viewing
  the chat history.
* **Recommendation**: Sanitize LLM output before rendering. Parse markdown first,
  then apply an HTML sanitizer (e.g., DOMPurify) before inserting into the DOM.

---

### [Improvement] Vuln 2: LLM-AGENCY: `src/ai/tools.ts:34`

* **Severity**: MEDIUM
* **Confidence**: HIGH
* **Category**: OWASP LLM Top 10 — LLM06
* **CWE**: CWE-269
* **Description**: The AI agent is configured with database write and file delete
  tool permissions without requiring human approval for destructive operations.
  A prompt injection attack could cause the agent to delete user data.
* **Recommendation**: Add human-in-the-loop confirmation for destructive operations.
  Require explicit user approval before executing database writes, file deletions,
  or external API calls initiated by the AI agent.

---
```
