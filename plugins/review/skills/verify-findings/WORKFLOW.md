# Verification Workflow

Detailed procedures for independently verifying code review and security review findings.

## Code Review Verification Procedures

### Architecture & Integrity Findings

1. Read the flagged code and its module/package context
2. Check if the architectural pattern is used consistently elsewhere in the codebase
3. Verify if the concern is about an actual SRP violation or just a large file
4. Assess modularity — are the responsibilities actually coupled or just co-located?

### Functionality & Correctness Findings

1. Read the complete function/method containing the flagged line
2. Trace the logic path — does the claimed edge case actually occur?
3. Check if guard clauses or validation exist upstream
4. Verify race condition claims by checking concurrency primitives (locks, atomics, channels)
5. Test idempotency claims by checking if the operation has side effects

### Security Findings (in code reviews)

Defer to the security verification procedure below.

### Maintainability & Readability Findings

1. Grep for the naming convention in question — is it established in the codebase?
2. Check if the "complexity" concern is inherent to the domain or artificial
3. Verify that cited DRY violations are actually duplicated logic, not similar but distinct code
4. Assess YAGNI claims — is the flagged abstraction actually used in one place?

### Testing Strategy Findings

1. Check if tests exist for the flagged code (grep for test files, describe/it blocks)
2. Verify if the claimed missing edge case is realistic in production
3. Check if integration tests cover what unit tests supposedly miss
4. Assess test isolation — does the test actually depend on external state?

### Performance & Scalability Findings

1. Check if the N+1 query claim is valid — is the ORM doing eager loading?
2. Verify bundle size concerns with actual dependency analysis
3. Check if caching is already applied at a different layer
4. Assess memory leak claims — is the reference actually retained?

### Dependencies & Documentation Findings

1. Verify claimed license issues with the actual package license
2. Check if the dependency is a well-maintained package (not abandoned)
3. Assess if missing docs are actually needed (simple, self-documenting code doesn't need docs)

## Security Review Verification Procedures

### Data Flow Tracing

For each security finding, trace the complete data flow:

1. **Identify the source**: Where does user input enter? (request params, headers, body, file uploads, environment variables)
2. **Trace propagation**: Follow the data through variable assignments, function calls, and transformations
3. **Identify the sink**: Where does the data reach a sensitive operation? (SQL query, shell command, HTML output, file system, network request)
4. **Check for sanitizers**: Between source and sink, look for:
   - Input validation (regex, schema validation, type checking)
   - Output encoding (HTML encoding, URL encoding, SQL parameterization)
   - Framework auto-protection (ORM parameterization, template auto-escaping)
   - Security middleware (CSRF tokens, auth checks, rate limiting)

### Framework Protection Detection

Check for these common framework-level protections:

| Framework | Protection | What it handles |
|-----------|-----------|-----------------|
| React/JSX | Auto-escaping in JSX expressions | XSS in rendered output |
| Angular | Template sanitization | XSS in templates |
| Django ORM | Parameterized queries | SQL injection |
| Spring Data JPA | Named parameters, repository methods | SQL injection |
| Express + helmet | Security headers middleware | Various header-based attacks |
| Rails | CSRF tokens, parameter filtering | CSRF, mass assignment |
| Next.js | Server Components, API routes | Various depending on version |

**How to detect**: Grep for framework imports, check `package.json`/`requirements.txt`/`pom.xml` for framework versions, read configuration files.

### CWE/CVE Web Research Protocol

For each security finding with a CWE reference:

1. **Search**: `"{CWE-XXX}" false positive {framework}` and `"{CWE-XXX}" {language} mitigation`
2. **Check CWE entry**: Confirm the weakness actually applies to the code pattern
3. **Trusted sources** (prioritize in order):
   - CWE/MITRE (cwe.mitre.org)
   - OWASP documentation (owasp.org)
   - Official framework security documentation
   - NVD/CVE databases (nvd.nist.gov)
   - Framework-specific security advisories
4. **Avoid relying solely on**: Blog posts, StackOverflow answers, or AI-generated content (unless corroborated by official sources)

### Exploit Feasibility Assessment

For each claimed exploit scenario:

1. **Is the entry point accessible?** — Is the endpoint public, authenticated, or admin-only?
2. **Is the payload deliverable?** — Can the attacker actually craft the required input?
3. **Does the exploit path exist?** — Are all intermediate steps in the chain present?
4. **What's the actual impact?** — Does exploitation lead to the claimed consequence?
5. **Are there compensating controls?** — WAF, rate limiting, monitoring, authentication

## Verdict Decision Matrix

| Evidence Found | Verdict | Explanation |
|----------------|---------|-------------|
| Exploit path confirmed, no sanitizer found | **CONFIRMED** | Finding is a real vulnerability |
| Data flow reaches sink with no protection | **CONFIRMED** | Risk is genuine |
| Framework handles the concern automatically | **DISMISSED** | Framework protection mitigates the risk |
| Sanitizer/validator exists in the data path | **DISMISSED** | Input is cleaned before reaching sink |
| Pattern is established elsewhere in codebase | **DISMISSED** | Intentional design choice (code findings) |
| Code is test-only or mock data | **DISMISSED** | No production impact |
| Code is behind authentication/authorization | **DISMISSED** | Requires auth, reducing attack surface |
| Behind a feature flag or disabled by default | **DISMISSED** | Not reachable in current configuration |
| Finding valid but impact lower than claimed | **DOWNGRADED** | Adjust severity/confidence accordingly |
| Severity is HIGH but exploit requires admin access | **DOWNGRADED** | Reduce severity to MEDIUM |
| Uncertain after thorough investigation | **CONFIRMED** | Conservative: keep the finding with "verification inconclusive" note |

## Verified Report Template

```markdown
# {Original Title} (Verified)

**Date**: {original date}
**Branch**: {original branch}
**Commit**: {original commit}
**Reviewer**: {original reviewer}
**Verified by**: Claude Code (false-positive-verifier)
**Verification Date**: {ISO 8601 date}

## Verification Summary

| Metric | Count |
|--------|-------|
| **Findings Reviewed** | {N} |
| **Confirmed** | {N} |
| **Downgraded** | {N} |
| **Dismissed** | {N} |
| **Signal Ratio** | {confirmed / total reviewed}% |

---

{Original PR Assessment / Summary section — preserved as-is}

---

## Verified Findings

### Blockers

- **[Blocker]** `{file}:{line}` — {Description} (Confidence: {N}/10)
  - **Principle**: {principle}
  - **Current**: `{code snippet}`
  - **Suggested**: `{fix snippet}`
  - > **Verification**: CONFIRMED — {evidence summary, e.g., "Data flow traced from request.body.email at line 12 through to db.query() at line 45 with no parameterization or sanitization in the path."}

### Improvements

- **[Improvement]** `{file}:{line}` — {Description} (Confidence: {N}/10)
  - **Principle**: {principle}
  - **Current**: `{code snippet}`
  - **Suggested**: `{fix snippet}`
  - > **Verification**: CONFIRMED — {evidence summary}

{For DOWNGRADED findings, show the adjusted confidence/severity with note}

- **[Improvement]** `{file}:{line}` — {Description} (Confidence: {adjusted}/10, was {original}/10)
  - > **Verification**: DOWNGRADED — {reason for adjustment}

### Questions

{Preserved as-is from original — questions don't need verification}

### Praise

{Preserved as-is from original}

### Nitpicks

{Preserved as-is from original}

---

## Dismissed Findings

Findings removed during verification. Each includes the reason for dismissal.

### Dismissed 1: `{file}:{line}` — {Original description}

- **Original Triage**: {Blocker/Improvement/Question}
- **Original Confidence**: {N}/10
- **Reason**: {Detailed explanation}
- **Evidence**: {What was checked — grep results, framework docs, web research findings}

### Dismissed 2: `{file}:{line}` — {Original description}

- **Original Triage**: {Blocker/Improvement/Question}
- **Original Confidence**: {N}/10
- **Reason**: {Detailed explanation}
- **Evidence**: {What was checked}

---

## Verdict (Revised)

- **Recommendation**: {Approve / Request Changes / Approve with Nits}
- **Risk Level**: {may change from original}
- **Blockers**: {revised count}
- **Improvements**: {revised count}
- **Questions**: {count}
- **Nits**: {count}
- **False Positives Removed**: {count}
```

### Security Review Verified Report Template

For security reviews, the Verified Findings section uses the security format:

```markdown
### [Blocker] Vuln N: {Category Code}: `{file}:{line}`

* **Severity**: {CRITICAL|HIGH|MEDIUM}
* **Confidence**: {HIGH|MEDIUM}
* **Category**: {OWASP category}
* **CWE**: CWE-XXX
* **Description**: {vulnerability description}
* **Exploit Scenario**: {attack path}
* **Recommendation**: {fix}
* > **Verification**: CONFIRMED — {evidence: data flow trace, sink reachability confirmed, no sanitizer found between lines X-Y}
```
