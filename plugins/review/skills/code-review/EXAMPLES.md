# Code Review Examples

## Invocation

```bash
# Default output path
/review:code-review

# Custom output path
/review:code-review custom/reviews/
```

## Sample Report — Mixed Findings

```markdown
# Pragmatic Code Review Report

**Date**: 2025-06-15T14:30:00Z
**Branch**: feat/user-authentication
**Commit**: a1b2c3d
**Reviewer**: Claude Code (pragmatic-code-review)

## PR Assessment

| Attribute | Value |
|-----------|-------|
| **Risk Level** | High |
| **PR Type** | Feature |
| **Atomicity** | Atomic |
| **Breaking Changes** | None |

---

## Summary

This PR adds JWT-based user authentication with login/signup endpoints. The overall approach is sound and follows existing patterns well. However, there is a critical security issue with token validation and a SQL injection vulnerability that must be addressed before merge. Two improvements would strengthen error handling and logging.

## Findings

### Blockers

- **[Blocker]** `src/auth/middleware.ts:45` — JWT secret read from `process.env.JWT_SECRET` without startup validation. If the env var is missing, `jwt.verify()` receives `undefined` and silently accepts any token. (Confidence: 10/10)
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

- **[Blocker]** `src/auth/repository.ts:15` — SQL injection via string interpolation in user lookup query. (Confidence: 10/10)
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

- **[Improvement]** `src/auth/controller.ts:28` — Password logged in error handler at debug level. Even at debug level, this creates risk if debug logging is enabled in production. (Confidence: 9/10)
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

- **[Question]** `src/auth/middleware.ts:62` — The token expiry is set to 7 days. Is this intentional for this app's security requirements, or should it be shorter (e.g., 1 hour with refresh tokens)?

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
**Reviewer**: Claude Code (pragmatic-code-review)

## PR Assessment

| Attribute | Value |
|-----------|-------|
| **Risk Level** | Low |
| **PR Type** | Bugfix |
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
