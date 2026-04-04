# Coding Standards Examples

## Example 1: Full-Stack Bootstrap (JVM + Node.js)

**Scenario**: New project with Kotlin backend and Next.js frontend.

**Detection output** (key fields):
```json
{
  "standards_repo": {"found": true, "template_count": 21},
  "devtools_local": null,
  "ecosystems": [
    {"ecosystem": "jvm", "build_tool": "gradle-kotlin", "root": "apps/api"},
    {"ecosystem": "node", "root": "apps/web"}
  ],
  "compliance": {"total_installed": 0, "total": 21, "score_percent": 0}
}
```

**User interaction**:
```
Q: Which rule categories should we install?
A: [x] Backend (8 rules)  [x] Frontend (4 rules)  [x] Infrastructure (2 rules)

Q: API directory path?
A: apps/api (default)

Q: Web directory path?
A: apps/web (default)
```

**Result**: All 21 files installed. Compliance: 100%.

**Files created**:
```
.claude/rules/backend/architecture.md
.claude/rules/backend/api-patterns.md
.claude/rules/backend/database-patterns.md
.claude/rules/backend/error-handling.md
.claude/rules/backend/kotlin-conventions.md
.claude/rules/backend/logging.md
.claude/rules/backend/security.md
.claude/rules/backend/testing-patterns.md
.claude/rules/frontend/architecture.md
.claude/rules/frontend/component-patterns.md
.claude/rules/frontend/state-management.md
.claude/rules/frontend/styling.md
.claude/rules/infrastructure/cicd.md
.claude/rules/infrastructure/tooling.md
.editorconfig
.prettierrc
eslint.config.mjs
lefthook.yml
Taskfile.yml
.claude/hooks/auto-lint.sh
.claude/hooks/settings.json
.claude/devtools.local.md
```

---

## Example 2: Backend-Only Bootstrap

**Scenario**: Kotlin Spring Boot project with no frontend.

**Detection output** (key fields):
```json
{
  "ecosystems": [
    {"ecosystem": "jvm", "build_tool": "gradle-kotlin", "root": "."}
  ],
  "compliance": {"total_installed": 0, "total": 21, "score_percent": 0}
}
```

**User interaction**:
```
Q: Which rule categories?
A: [x] Backend (8 rules)  [x] Infrastructure (2 rules)

Q: API directory path?
A: . (project root)
```

**Result**: 13 files installed (10 rules + 3 configs, no hooks).

Skipped: `.prettierrc`, `eslint.config.mjs`, `auto-lint.sh`, `settings.json` (Node.js only).
Lefthook.yml: eslint/prettier sections removed, only gitleaks + ktlint + detekt.

---

## Example 3: Update After Standards v1.1.0

**Scenario**: Project bootstrapped at v1.0.0. Standards updated to v1.1.0 adding `error-handling.md` and updating `testing-patterns.md`.

**Detection output** (key fields):
```json
{
  "devtools_local": {
    "coding_standards_path": "/path/to/coding-standards",
    "last_bootstrap": "2026-03-27",
    "ecosystems": ["jvm", "nodejs"]
  },
  "comparison": {
    "rules": [
      {"file": "backend/architecture.md", "status": "match"},
      {"file": "backend/error-handling.md", "status": "missing"},
      {"file": "backend/testing-patterns.md", "status": "modified"}
    ]
  },
  "compliance": {"total_installed": 19, "total": 21, "score_percent": 90}
}
```

**Presented to user**:
```
## Standards Update Available

### New Files
| File | Category |
|------|----------|
| backend/error-handling.md | rules |

### Modified (template changed)
| File | Category |
|------|----------|
| backend/testing-patterns.md | rules |
```

**User interaction**:
```
Q: Which updates to apply?
A: [x] Add backend/error-handling.md  [x] Update backend/testing-patterns.md
```

**Result**: 2 files updated. Compliance: 100%.

---

## Example 4: Audit Report

**Scenario**: Check compliance of existing project.

**Output**:
```
## Coding Standards Audit

Compliance: 12/14 rules, 3/5 configs, 1/2 hooks — 76%

### Rules
| File | Category | Status |
|------|----------|--------|
| architecture.md | backend | Match |
| api-patterns.md | backend | Match |
| database-patterns.md | backend | Match |
| error-handling.md | backend | MISSING |
| kotlin-conventions.md | backend | Match |
| logging.md | backend | Match |
| security.md | backend | Match |
| testing-patterns.md | backend | Modified |
| architecture.md | frontend | Match |
| component-patterns.md | frontend | Match |
| state-management.md | frontend | Match |
| styling.md | frontend | Match |
| cicd.md | infrastructure | Match |
| tooling.md | infrastructure | Match |

### Configs
| File | Status |
|------|--------|
| .editorconfig | Match |
| .prettierrc | MISSING |
| eslint.config.mjs | Match |
| lefthook.yml | Modified (expected: paths customized) |
| Taskfile.yml | Modified (expected: paths customized) |

### Hooks
| File | Status |
|------|--------|
| auto-lint.sh | Installed, executable |
| settings.json | MISSING |
```

**User interaction**:
```
Q: Fix missing/outdated items?
A: Yes, start Update workflow
```
