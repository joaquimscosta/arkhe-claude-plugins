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

---

## Summary

This PR adds JWT-based user authentication with login/signup endpoints. The overall approach is sound and follows existing patterns well. However, there is a critical security issue with token validation that must be addressed before merge, along with two improvements that would strengthen the implementation.

## Findings

### Critical Issues

- **[Critical]** `src/auth/middleware.ts:45` — JWT secret is read from `process.env.JWT_SECRET` without a fallback check. If the env var is missing, `jwt.verify()` receives `undefined` as the secret and will silently accept any token.
  - **Principle**: Defense in depth — fail securely when configuration is missing
  - **Suggestion**: Add startup validation that throws if `JWT_SECRET` is not set. Consider using a config module that validates all required env vars at boot.

### Suggested Improvements

- **[Improvement]** `src/auth/controller.ts:28` — Password is logged in the error handler at debug level: `logger.debug('Login attempt', { email, password })`. Even at debug level, this creates a risk if debug logging is ever enabled in production.
  - **Principle**: Data minimization — never log credentials regardless of log level
  - **Suggestion**: Remove `password` from the log payload. Log only the email and attempt timestamp.

- **[Improvement]** `src/auth/repository.ts:15-32` — The `findByEmail` query uses string interpolation instead of parameterized queries: `` `SELECT * FROM users WHERE email = '${email}'` ``
  - **Principle**: Input validation — always use parameterized queries to prevent SQL injection
  - **Suggestion**: Use `db.query('SELECT * FROM users WHERE email = $1', [email])`

### Nitpicks

- **Nit:** `src/auth/types.ts:8` — `TokenPayload` interface uses `any` for the `metadata` field. Consider using `Record<string, unknown>` for type safety.

## Verdict

- **Recommendation**: Request Changes
- **Critical Issues**: 1
- **Improvements**: 2
- **Nits**: 1
```

## Sample Report — Clean Review

```markdown
# Pragmatic Code Review Report

**Date**: 2025-06-20T10:15:00Z
**Branch**: fix/pagination-offset
**Commit**: d4e5f6g
**Reviewer**: Claude Code (pragmatic-code-review)

---

## Summary

This PR fixes an off-by-one error in the pagination logic that caused the last item on each page to be duplicated on the next page. The fix is minimal, correct, and includes a regression test. Clean implementation.

## Findings

### Critical Issues

None.

### Suggested Improvements

None.

### Nitpicks

- **Nit:** `tests/pagination.test.ts:42` — Test name "should work correctly" could be more descriptive. Consider "should not duplicate items across page boundaries".

## Verdict

- **Recommendation**: Approve
- **Critical Issues**: 0
- **Improvements**: 0
- **Nits**: 1
```
