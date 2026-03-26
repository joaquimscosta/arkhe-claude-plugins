# Doc-Freshness Examples

## Example 1: Full Scan on a Web App

**Command**: `scan` (or no arguments)

```
## Documentation Freshness Report

_Scanned 12 docs on 2026-03-21_

| Category | Count | Critical | Warning | Info |
|----------|-------|----------|---------|------|
| Broken Links | 5 | 3 | 2 | — |
| Version Mismatches | 2 | 1 | 1 | — |
| Stale Docs | 3 | — | 2 | 1 |
| Code-Doc Drift | 4 | 2 | 2 | 0 |
| Cross-Doc Conflicts | 1 | — | 1 | 0 |

### Findings

| # | Severity | Type | File:Line | Finding | Evidence |
|---|----------|------|-----------|---------|----------|
| 1 | CRITICAL | broken-link | README.md:45 | Link to deleted file | `docs/api-v1.md` does not exist |
| 2 | CRITICAL | broken-link | docs/setup.md:23 | Link to deleted file | `docs/old-config.md` does not exist |
| 3 | CRITICAL | version | docs/setup.md:7 | Node major version mismatch | Doc says "Node 18", .nvmrc says "20" |
| 4 | CRITICAL | drift | docs/api.md:34 | Function removed | `createUser(name, email)` not found in codebase |
| 5 | CRITICAL | drift | docs/api.md:56 | Endpoint removed | `DELETE /api/v1/sessions` not found in routes |
| 6 | WARNING | version | README.md:3 | Minor version mismatch | Doc says "3.11", pyproject.toml says "3.12" |
| 7 | WARNING | stale | docs/architecture.md | 42 days since last update | Code changed 3 days ago |
| 8 | WARNING | stale | CONTRIBUTING.md | 60 days since last update | CI config changed 5 days ago |
| 9 | WARNING | drift | docs/api.md:12 | Signature changed | `getUsers(page)` is now `getUsers(page, limit)` |
| 10 | WARNING | drift | docs/config.md:8 | Config key renamed | `DB_HOST` is now `DATABASE_URL` |
| 11 | WARNING | cross-doc | README.md:15 vs docs/setup.md:7 | Conflicting Node version | "18" vs "20" |
| 12 | WARNING | broken-link | docs/api.md:78 | Anchor not found | `#authentication` heading removed from docs/auth.md |
```

## Example 2: Links Mode (Fast)

**Command**: `links`

```
## Link Check Results

_Checked 12 docs, found 5 issues_

### Broken Links (3 CRITICAL)

| Doc:Line | Link Text | Target | Reason |
|----------|-----------|--------|--------|
| README.md:45 | "API docs" | docs/api-v1.md | File deleted |
| docs/setup.md:23 | "config reference" | docs/old-config.md | File deleted |
| docs/api.md:78 | "auth section" | docs/auth.md#authentication | Heading removed |

### Stale File References (2 WARNING)

| Doc:Line | Path Referenced | Reason |
|----------|----------------|--------|
| docs/deploy.md:15 | `scripts/deploy.sh` | File not found at project root or doc directory |
| CONTRIBUTING.md:30 | `config/eslint.json` | File not found (renamed to `eslint.config.js`?) |
```

## Example 3: Drift Mode (Deep Code-Doc Analysis)

**Command**: `drift docs/api-reference.md`

```
## Code-Doc Drift Analysis: docs/api-reference.md

### References Checked

| # | Reference Type | Doc Says | Code Shows | Status |
|---|---------------|----------|------------|--------|
| 1 | Function | `createUser(name, email)` | `createUser(data: CreateUserDto)` at src/services/UserService.ts:45 | CHANGED |
| 2 | Endpoint | `POST /api/users` | Found at src/routes/users.ts:12 | OK |
| 3 | Endpoint | `DELETE /api/sessions` | Not found in any route file | REMOVED |
| 4 | Response shape | `{ id, name, email }` | Returns `{ id, name, email, createdAt }` at src/mappers/UserMapper.ts:8 | CHANGED |
| 5 | Config key | `API_PORT` | Found in .env.example:3 | OK |
| 6 | Class | `UserValidator` | Not found (renamed to `UserSchema`?) | REMOVED |

### Summary
- 6 references checked
- 2 OK, 2 changed (WARNING), 2 removed (CRITICAL)
```

## Example 4: Cross-Doc Mode

**Command**: `cross-doc`

```
## Cross-Document Consistency Check

### Topic Overlap Detected

| Topic | Docs |
|-------|------|
| Installation/Setup | README.md, docs/getting-started.md, CONTRIBUTING.md |
| API Authentication | docs/api.md, docs/auth.md |

### Conflicts Found

| # | Topic | Doc A | Doc B | Conflict |
|---|-------|-------|-------|----------|
| 1 | Node version | README.md:3 says "Node 18+" | docs/getting-started.md:5 says "Node 20+" | Version requirement mismatch |
| 2 | Default port | README.md:15 says "port 3000" | docker-compose.yml maps to 8080 | Port number mismatch |
| 3 | Auth method | docs/api.md:20 says "Bearer token" | docs/auth.md:8 says "API key header" | Authentication method conflict |

### Consistent Topics
- Installation steps: README.md and docs/getting-started.md agree on `npm install` workflow
- Database setup: docs/getting-started.md and CONTRIBUTING.md both reference Docker Compose
```

## Example 5: Check Single File

**Command**: `check CONTRIBUTING.md`

```
## Freshness Check: CONTRIBUTING.md

### Staleness
- Last updated: 2026-01-15 (65 days ago)
- Latest code change: 2026-03-19 (2 days ago)
- Drift score: **stale**

### Link Issues (1 found)

| Line | Target | Status |
|------|--------|--------|
| 30 | `config/eslint.json` | WARNING: File not found |

### Code-Doc Drift (2 found)

| Line | Reference | Finding |
|------|-----------|---------|
| 15 | "Run `npm run lint`" | Script exists in package.json — OK |
| 22 | "Tests use Jest" | package.json shows vitest, not jest — **CRITICAL** |
| 45 | "CI runs on GitHub Actions" | .github/workflows/ci.yml exists — OK |

### Version References
- None found
```

## Example 6: Zero-Config vs Config-Driven

### Zero-Config (Auto-Discovery)

The skill works out of the box. It:
1. Discovers docs via default patterns (`README.md`, `docs/**/*.md`, etc.)
2. Maps docs to code via naming conventions
3. Checks versions against auto-detected ground truth files

### Config-Driven (Precise Mappings)

For projects needing explicit control, add to `.arkhe.yaml`:

```yaml
doc-freshness:
  doc_patterns:
    - "docs/**/*.md"
    - "guides/**/*.md"
  exclude:
    - "docs/archive/**"
    - "docs/drafts/**"
  mappings:
    - doc: docs/api-reference.md
      code: src/api/**/*.ts
    - doc: docs/database.md
      code: src/models/**/*.ts
```

This produces more precise drift analysis since the doc-code relationships are explicit rather than guessed.
