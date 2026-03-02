# Verification Examples

## Example 1: Code Review Verification

### Input: Original Code Review Report

```markdown
# Pragmatic Code Review Report

**Date**: 2026-02-28T14:30:00Z
**Branch**: feature/user-profile
**Commit**: a1b2c3d
**Reviewer**: Claude Code (pragmatic-code-review)

## PR Assessment

| Attribute | Value |
|-----------|-------|
| **Risk Level** | Medium |
| **PR Type** | Feature |
| **Atomicity** | Atomic |
| **Breaking Changes** | None |

## Findings

### Blockers

- **[Blocker]** `src/services/userService.ts:45` — SQL injection vulnerability in user search (Confidence: 9/10)
  - **Principle**: Security — Input Validation
  - **Current**: `db.query(\`SELECT * FROM users WHERE name LIKE '%${query}%'\`)`
  - **Suggested**: `db.query('SELECT * FROM users WHERE name LIKE $1', [\`%${query}%\`])`

### Improvements

- **[Improvement]** `src/components/UserProfile.tsx:112` — XSS risk: user-supplied content rendered without sanitization (Confidence: 8/10)
  - **Principle**: Security — Output Encoding
  - **Current**: `<div>{user.bio}</div>`
  - **Suggested**: Use a sanitization library before rendering

- **[Improvement]** `src/utils/cache.ts:23` — Cache invalidation missing for user updates (Confidence: 7/10)
  - **Principle**: DRY — Single Source of Truth
  - **Current**: Cache is set on read but never invalidated
  - **Suggested**: Add cache invalidation in `updateUser()` and `deleteUser()`

- **[Improvement]** `src/services/userService.ts:78` — N+1 query in user list with roles (Confidence: 7/10)
  - **Principle**: Performance — Efficient Data Access
  - **Current**: `users.forEach(u => db.query('SELECT * FROM roles WHERE user_id = ?', [u.id]))`
  - **Suggested**: `db.query('SELECT * FROM roles WHERE user_id IN (?)', [userIds])`

## Verdict
- **Recommendation**: Request Changes
- **Blockers**: 1
- **Improvements**: 3
```

### Output: Verified Report

```markdown
# Pragmatic Code Review Report (Verified)

**Date**: 2026-02-28T14:30:00Z
**Branch**: feature/user-profile
**Commit**: a1b2c3d
**Reviewer**: Claude Code (pragmatic-code-review)
**Verified by**: Claude Code (false-positive-verifier)
**Verification Date**: 2026-02-28T14:45:00Z

## Verification Summary

| Metric | Count |
|--------|-------|
| **Findings Reviewed** | 4 |
| **Confirmed** | 2 |
| **Downgraded** | 1 |
| **Dismissed** | 1 |
| **Signal Ratio** | 50% |

---

## PR Assessment

| Attribute | Value |
|-----------|-------|
| **Risk Level** | Medium |
| **PR Type** | Feature |
| **Atomicity** | Atomic |
| **Breaking Changes** | None |

---

## Verified Findings

### Blockers

- **[Blocker]** `src/services/userService.ts:45` — SQL injection vulnerability in user search (Confidence: 9/10)
  - **Principle**: Security — Input Validation
  - **Current**: `db.query(\`SELECT * FROM users WHERE name LIKE '%${query}%'\`)`
  - **Suggested**: `db.query('SELECT * FROM users WHERE name LIKE $1', [\`%${query}%\`])`
  - > **Verification**: CONFIRMED — Data flow traced: `query` parameter originates from `req.query.search` in `userController.ts:12`, passed directly to `userService.searchUsers()` at line 43, then interpolated into SQL string at line 45. No parameterization, no input sanitization found between controller and query. The `pg` driver is used (confirmed in package.json) which supports parameterized queries.

### Improvements

- **[Improvement]** `src/utils/cache.ts:23` — Cache invalidation missing for user updates (Confidence: 7/10)
  - **Principle**: DRY — Single Source of Truth
  - **Current**: Cache is set on read but never invalidated
  - **Suggested**: Add cache invalidation in `updateUser()` and `deleteUser()`
  - > **Verification**: CONFIRMED — Grepped for `cache.del`, `cache.invalidate`, `cache.clear` across the codebase: 0 results in `userService.ts`. The `updateUser()` function at line 67 and `deleteUser()` at line 89 both modify the database without touching the cache set at line 23. Stale data will be served until TTL expires.

- **[Improvement]** `src/services/userService.ts:78` — N+1 query in user list with roles (Confidence: 5/10, was 7/10)
  - **Principle**: Performance — Efficient Data Access
  - > **Verification**: DOWNGRADED — The N+1 pattern exists but the `getUsersWithRoles()` function is only called from the admin dashboard (`adminController.ts:34`), which has a `limit: 20` parameter. With max 20 users, the performance impact is negligible. Additionally, the roles table has an index on `user_id` (confirmed in `migrations/003_add_roles.sql`). Downgraded from 7/10 to 5/10.

---

## Dismissed Findings

### Dismissed 1: `src/components/UserProfile.tsx:112` — XSS risk: user-supplied content rendered without sanitization

- **Original Triage**: Improvement
- **Original Confidence**: 8/10
- **Reason**: React auto-escapes JSX expressions by default. The `{user.bio}` expression renders as text content, not as HTML. XSS via JSX text interpolation is not possible unless unsafe HTML rendering APIs are used.
- **Evidence**: Grepped for unsafe HTML rendering APIs in `UserProfile.tsx` and all imported components: 0 results. React 18.3.1 confirmed in `package.json`. The `user.bio` field is rendered inside a `<div>` as a text node — React's virtual DOM escapes the content automatically.

---

## Verdict (Revised)

- **Recommendation**: Request Changes
- **Risk Level**: Medium
- **Blockers**: 1
- **Improvements**: 2 (1 downgraded)
- **Questions**: 0
- **Nits**: 0
- **False Positives Removed**: 1
```

---

## Example 2: Security Review Verification

### Input: Original Security Review Report

```markdown
# Security Review Report

**Date**: 2026-02-28T15:00:00Z
**Branch**: feature/api-v2
**Commit**: d4e5f6g
**Reviewer**: Claude Code (security-review)
**Framework**: OWASP Top 10 2025 + API Top 10 + LLM Top 10

## Summary
- **Blocker**: 2 findings
- **Improvement**: 1 finding
- **Total**: 3 actionable findings

## Findings

### [Blocker] Vuln 1: A05 Injection: `src/api/search.ts:34`

* **Severity**: HIGH
* **Confidence**: HIGH
* **Category**: A05:2025 Injection
* **CWE**: CWE-89
* **Description**: User input from query parameter interpolated directly into MongoDB query
* **Exploit Scenario**: Attacker sends `{"$gt": ""}` as search parameter to extract all records
* **Recommendation**: Use MongoDB's built-in query sanitization or `mongo-sanitize` package

### [Blocker] Vuln 2: A01 Access Control: `src/api/users.ts:67`

* **Severity**: HIGH
* **Confidence**: HIGH
* **Category**: A01:2025 Broken Access Control
* **CWE**: CWE-639
* **Description**: IDOR vulnerability — user can access other users' profiles by changing the ID parameter
* **Exploit Scenario**: Authenticated user changes `/api/users/123` to `/api/users/456` to access another user's data
* **Recommendation**: Add authorization check comparing `req.user.id` with the requested resource owner

### [Improvement] Vuln 3: A04 Cryptographic Failures: `src/utils/token.ts:12`

* **Severity**: MEDIUM
* **Confidence**: MEDIUM
* **Category**: A04:2025 Cryptographic Failures
* **CWE**: CWE-326
* **Description**: JWT signed with HS256 which is vulnerable to brute-force attacks on weak secrets
* **Exploit Scenario**: Attacker brute-forces the JWT secret and forges authentication tokens
* **Recommendation**: Switch to RS256 or use a strong secret (256+ bits of entropy)
```

### Output: Verified Report

```markdown
# Security Review Report (Verified)

**Date**: 2026-02-28T15:00:00Z
**Branch**: feature/api-v2
**Commit**: d4e5f6g
**Reviewer**: Claude Code (security-review)
**Framework**: OWASP Top 10 2025 + API Top 10 + LLM Top 10
**Verified by**: Claude Code (false-positive-verifier)
**Verification Date**: 2026-02-28T15:20:00Z

## Verification Summary

| Metric | Count |
|--------|-------|
| **Findings Reviewed** | 3 |
| **Confirmed** | 1 |
| **Downgraded** | 1 |
| **Dismissed** | 1 |
| **Signal Ratio** | 33% |

---

## Summary (Revised)
- **Blocker**: 1 finding (was 2)
- **Improvement**: 1 finding (downgraded from Blocker)
- **Total**: 2 actionable findings
- **False Positives Removed**: 1

---

## Verified Findings

### [Blocker] Vuln 1: A01 Access Control: `src/api/users.ts:67`

* **Severity**: HIGH
* **Confidence**: HIGH
* **Category**: A01:2025 Broken Access Control
* **CWE**: CWE-639
* **Description**: IDOR vulnerability — user can access other users' profiles by changing the ID parameter
* **Exploit Scenario**: Authenticated user changes `/api/users/123` to `/api/users/456` to access another user's data
* **Recommendation**: Add authorization check comparing `req.user.id` with the requested resource owner
* > **Verification**: CONFIRMED — Traced the request handler at `users.ts:67`. The `getUserById` endpoint extracts `req.params.id` at line 68 and queries `User.findById(id)` at line 70. No authorization middleware applied to this route (checked `routes/users.ts:15` — only `authMiddleware` which verifies authentication but not authorization). The `req.user.id` is available but never compared to the requested ID. Any authenticated user can access any profile.

### [Improvement] Vuln 2: A05 Injection: `src/api/search.ts:34` (Downgraded from Blocker)

* **Severity**: MEDIUM (was HIGH)
* **Confidence**: MEDIUM (was HIGH)
* **Category**: A05:2025 Injection
* **CWE**: CWE-89
* **Description**: User input from query parameter used in MongoDB query
* **Recommendation**: Add explicit type checking or use `mongo-sanitize`
* > **Verification**: DOWNGRADED — The NoSQL injection concern is valid but overstated. The `mongoose` ODM (v8.1.0, confirmed in package.json) is used with a schema-validated model. The `search` parameter is passed to `Model.find({ name: { $regex: query } })` at line 36. While `$regex` injection is possible, Mongoose's query casting rejects object-type inputs for string fields by default (verified via Mongoose 8.x docs: "Query casting prevents most NoSQL injection when schemas have typed fields"). The field `name` is typed as `String` in the schema at `models/item.ts:8`. Severity downgraded to MEDIUM because exploitation requires bypassing Mongoose's type casting, which is non-trivial. Confidence downgraded to MEDIUM.

---

## Dismissed Findings

### Dismissed 1: `src/utils/token.ts:12` — JWT signed with HS256

- **Original Triage**: Improvement
- **Original Confidence**: MEDIUM
- **Reason**: HS256 is not inherently weak — it depends on the secret's entropy. The JWT secret is loaded from `process.env.JWT_SECRET` at `config.ts:5`. The `.env.example` specifies `JWT_SECRET=<generate-with-openssl-rand-base64-64>` with a comment requiring 512-bit minimum. The actual secret length cannot be verified (environment variable), but the project's security documentation (`docs/SECURITY.md:23`) mandates 64-byte secrets generated via `openssl rand -base64 64`.
- **Evidence**: Searched OWASP JWT cheat sheet: "HS256 is acceptable when combined with a sufficiently strong secret (256+ bits)." The project enforces this via documentation and `.env.example` template. No evidence of a weak secret. CWE-326 (Inadequate Encryption Strength) does not apply when the key has sufficient entropy.

---

## Verdict (Revised)

- **Recommendation**: Request Changes
- **Risk Level**: Medium (was High)
- **Blockers**: 1 (was 2)
- **Improvements**: 1
- **Questions**: 0
- **Nits**: 0
- **False Positives Removed**: 1
```
