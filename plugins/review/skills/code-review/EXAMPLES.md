# Code Review Examples

## Invocation

```bash
# Default output path
/review:code-review

# Custom output path
/review:code-review custom/reviews/

# With GitHub PR posting
/review:code-review --post-to-pr

# Custom path + PR posting
/review:code-review custom/reviews/ --post-to-pr
```

## Orchestration Flow

What the user sees during a typical multi-agent review:

```
/review:code-review

Phase 1: Gathering context...
  - Agent A: Found 2 CLAUDE.md files (root, src/)
  - Agent B: 8 files changed | Feature | Medium risk

Phase 2: Running 5 parallel reviewers...
  - CLAUDE.md compliance: 1 finding
  - Bug scanner: 2 findings
  - Git history: 0 findings
  - Security: 1 finding
  - Code comments: skipped (no substantive comments)

Phase 3: Scoring 4 findings...
  - Finding 1 (CLAUDE.md): 85/100 — kept
  - Finding 2 (Bug): 92/100 — kept
  - Finding 3 (Bug): 45/100 — filtered
  - Finding 4 (Security): 88/100 — kept

Phase 4: Generating report... 3 findings (1 Blocker, 2 Improvements)
Report saved to: ./reviews/code/2026-03-18_14-30-00_code-review.md

Phase 6: Running verification...
Verified report saved to: ./reviews/code/2026-03-18_14-30-00_code-review.verified.md
```

## Orchestration Flow — Non-PR Branch

When reviewing changes on a branch without a PR:

```
/review:code-review

Phase 1: Gathering context...
  - Agent A: Found 1 CLAUDE.md file (root)
  - Agent B: 3 files changed | Bugfix | Low risk

Phase 2: Running 4 parallel reviewers...
  - CLAUDE.md compliance: 0 findings
  - Bug scanner: 0 findings
  - Git history: 0 findings
  - Security: 0 findings

Phase 3: No findings to score.

Phase 4: Generating clean report...
Report saved to: ./reviews/code/2026-03-18_10-15-00_code-review.md

Phase 6: Running verification...
Verified report saved to: ./reviews/code/2026-03-18_10-15-00_code-review.verified.md
```

## Orchestration Flow — With PR Posting

```
/review:code-review --post-to-pr

Phase 1: Gathering context...
  ...

Phase 2-4: (same as above)
Report saved to: ./reviews/code/2026-03-18_16-00-00_code-review.md

Phase 5: Posting to GitHub PR...
  - PR #42 on feat/auth-refactor — open, eligible
  - Posted review comment with 3 findings

Phase 6: Running verification...
```

## Orchestration Flow — PR Posting Skipped

```
/review:code-review --post-to-pr

Phase 1-4: (same as above)
Report saved to: ./reviews/code/2026-03-18_16-00-00_code-review.md

Phase 5: No open PR found for this branch. Skipping GitHub posting.

Phase 6: Running verification...
```

## Sample Report — Mixed Findings

```markdown
# Pragmatic Code Review Report

**Date**: 2025-06-15T14:30:00Z
**Branch**: feat/user-authentication
**Commit**: a1b2c3d
**Reviewer**: Claude Code (multi-agent code review)
**Review Mode**: Multi-Agent Orchestration (4 reviewers, confidence threshold: 80)

## PR Assessment

| Attribute | Value |
|-----------|-------|
| **Risk Level** | High |
| **Change Type** | Feature |
| **Atomicity** | Atomic |
| **Breaking Changes** | None |

---

## Summary

This PR adds JWT-based user authentication with login/signup endpoints. The overall approach is sound and follows existing patterns well. However, there is a critical security issue with token validation and a SQL injection vulnerability that must be addressed before merge. Two improvements would strengthen error handling and logging.

## Findings

### Blockers

- **[Blocker]** `src/auth/middleware.ts:45` — JWT secret read from `process.env.JWT_SECRET` without startup validation. If the env var is missing, `jwt.verify()` receives `undefined` and silently accepts any token. (Confidence: 95/100, Source: Security)
  - **Principle**: Defense in depth — fail securely when configuration is missing
  - **Current**:
    ```ts
    const secret = process.env.JWT_SECRET;
    const decoded = jwt.verify(token, secret);
    ```
  - **Suggested**:
    ```ts
    const secret = process.env.JWT_SECRET;
    if (!secret) throw new Error('JWT_SECRET is required');
    const decoded = jwt.verify(token, secret);
    ```

- **[Blocker]** `src/auth/repository.ts:15` — SQL injection via string interpolation in user lookup query. (Confidence: 98/100, Source: Security)
  - **Principle**: OWASP A03 Injection — never construct queries from user input
  - **Current**:
    ```ts
    const result = await db.query(`SELECT * FROM users WHERE email = '${email}'`);
    ```
  - **Suggested**:
    ```ts
    const result = await db.query('SELECT * FROM users WHERE email = $1', [email]);
    ```

### Improvements

- **[Improvement]** `src/auth/controller.ts:28` — Password logged in error handler at debug level. Even at debug level, this creates risk if debug logging is enabled in production. (Confidence: 88/100, Source: Bug Scan)
  - **Principle**: Data minimization — never log credentials regardless of log level
  - **Current**:
    ```ts
    logger.debug('Login attempt', { email, password });
    ```
  - **Suggested**:
    ```ts
    logger.debug('Login attempt', { email, timestamp: Date.now() });
    ```

### Questions

- **[Question]** `src/auth/middleware.ts:62` — The token expiry is set to 7 days. Is this intentional for this app's security requirements, or should it be shorter (e.g., 1 hour with refresh tokens)? (Source: Security)

### Praise

- **[Praise]** `src/auth/service.ts:10-35` — Clean separation of auth logic into a dedicated service layer with proper dependency injection. This makes the auth flow testable and follows the existing service pattern well.

### Nitpicks

- **[Nit]** `src/auth/types.ts:8` — `TokenPayload` interface uses `any` for the `metadata` field. Consider `Record<string, unknown>` for type safety.

## Verdict

- **Recommendation**: Request Changes
- **Risk Level**: High
- **Blockers**: 2
- **Improvements**: 1
- **Questions**: 1
- **Nits**: 1
```

## Sample Report — Clean Review

```markdown
# Pragmatic Code Review Report

**Date**: 2025-06-20T10:15:00Z
**Branch**: fix/pagination-offset
**Commit**: d4e5f6g
**Reviewer**: Claude Code (multi-agent code review)
**Review Mode**: Multi-Agent Orchestration (4 reviewers, confidence threshold: 80)

## PR Assessment

| Attribute | Value |
|-----------|-------|
| **Risk Level** | Low |
| **Change Type** | Bugfix |
| **Atomicity** | Atomic |
| **Breaking Changes** | None |

---

## Summary

This PR fixes an off-by-one error in the pagination logic that caused the last item on each page to be duplicated on the next page. The fix is minimal, correct, and includes a regression test. Clean implementation.

## Findings

### Blockers

None.

### Improvements

None.

### Questions

None.

### Praise

- **[Praise]** `tests/pagination.test.ts:38-55` — Excellent regression test that specifically targets the page boundary duplication bug with clear assertion messages. This prevents future regressions on the exact scenario.

### Nitpicks

- **[Nit]** `tests/pagination.test.ts:42` — Test name "should work correctly" could be more descriptive. Consider "should not duplicate items across page boundaries".

## Verdict

- **Recommendation**: Approve
- **Risk Level**: Low
- **Blockers**: 0
- **Improvements**: 0
- **Questions**: 0
- **Nits**: 1
```

## Sample GitHub PR Comment

When using `--post-to-pr`, the posted comment looks like:

```markdown
### Code review

Found 3 issues:

1. JWT secret read without validation — if env var is missing, jwt.verify() silently accepts any token (Security: defense-in-depth violation)

https://github.com/owner/repo/blob/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0/src/auth/middleware.ts#L44-L48

2. SQL injection via string interpolation in user lookup query (Security: OWASP A03 Injection)

https://github.com/owner/repo/blob/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0/src/auth/repository.ts#L14-L16

3. Password logged in debug error handler (Bug Scan: data minimization violation)

https://github.com/owner/repo/blob/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0/src/auth/controller.ts#L27-L29

---

Generated with [Claude Code](https://claude.ai/code)

<sub>If this review was useful, react with :+1:. Otherwise, react with :-1:.</sub>
```
