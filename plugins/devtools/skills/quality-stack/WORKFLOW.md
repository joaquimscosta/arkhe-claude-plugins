# Workflow: Quality Stack

## Phase 1: Recommend

```
USER invokes quality-stack
    │
    ▼
Run scan_project.py on project root (auto-detects ecosystems)
    │
    ├── "error": "no_ecosystem_detected"?
    │   ├── YES → check nearby_project_files, suggest --recursive or --ecosystem
    │   └── NO → continue
    │
    ▼
For each detected ecosystem in output.ecosystems[]:
    │
    ├── JVM detected? → fetch JVM research docs via WebFetch
    │   ├── jvm-quality-tools-evaluation.md
    │   └── kotlin-spring-boot-testing-ecosystem.md
    │
    ├── Node.js detected? → fetch Node.js research doc
    │   └── node-quality-tools-evaluation.md
    │
    ├── Python detected? → fetch Python research doc
    │   └── python-quality-tools-evaluation.md
    │
    └── Always fetch cross-cutting research doc
        └── cross-cutting-devtools-evaluation.md
    │
    ├── Fetch failed? → warn user, proceed with scanner + LLM knowledge
    │
    ▼
Cross-reference: detected tools vs recommended tools (per ecosystem)
  ├── Check status field: active / disabled / config-only
  ├── Review tool_config (jacoco_threshold, eslint_config_type, mypy_strict, etc.)
  └── Compare versions against research recommendations
    │
    ▼
Apply priority classification rules (per ecosystem)
  ├── JVM: Language-aware (Kotlin/Java/mixed), version-aware (Spring Boot 3.x/4.x)
  │   └── Cross-reference BOTH JVM docs (see JVM Cross-Reference Checklist below)
  ├── Node.js: Framework-aware (Next.js/React/Vue), TypeScript strict audit
  ├── Python: Framework-aware (Django/FastAPI/Flask), dep manager aware
  └── Cross-cutting: Git hooks, CI/CD, dependency automation, security
    │
    ▼
Generate recommendation report (grouped by ecosystem)
    │
    ▼
Present to user with AskUserQuestion (multiSelect: true, top NOW/SOON tools as options)
```

### JVM Cross-Reference Checklist

When JVM ecosystem is detected, cross-reference against BOTH research documents:

1. **jvm-quality-tools-evaluation.md** — static analysis, coverage, build tools, security
2. **kotlin-spring-boot-testing-ecosystem.md** — check the "Priority Actions" section for:
   - [ ] MockMvcTester (Spring Boot 3.4+, built-in)
   - [ ] @DataJpaTest slice tests (has JPA entities but no slice tests)
   - [ ] Testcontainers reuse mode (has Testcontainers but no reuse config)
   - [ ] Assertion library assessment (Kotest assertions vs AssertJ)
   - [ ] Hamcrest exclusion (should be excluded from test classpath)
   - [ ] Scenario DSL (if using Spring Modulith)

Do NOT skip testing-ecosystem items even if the quality-tools doc already covers testing.
The two docs have different scopes — quality-tools covers tool presence, testing-ecosystem
covers testing patterns and practices.

## Phase 2: Setup

```
Present recommendation report to user
    │
    ▼
Multi-round tool selection (see Tool Selection Protocol in Recommendation Report Format below):
  ├── Round 1: NOW tools per ecosystem (AskUserQuestion multiSelect)
  ├── Round 2: Cross-cutting NOW tools (if any remain)
  └── Round 3: SOON tools (if user wants more)
    │
    ▼
Collect all selected tools across rounds
    │
    ▼
For each selected tool:
  ├── 1. Apply Setup Guards (see below) — resolve version, check compatibility
  ├── 2. Add Gradle plugin / Maven plugin / npm package / config file
  ├── 3. Add test dependencies (if applicable)
  ├── 4. Add CI/CD workflow steps (if applicable)
  └── 5. Run Post-Setup Verification (see below) — MUST pass before next tool
    │
    ▼
Re-run scan_project.py to confirm all tools detected
    │
    ▼
Report: "Added {N} tools. Scanner now detects: {list}"
```

## Monorepo Workflow

When the project root contains no build file or is a monorepo:

1. **Auto-detect**: Scanner returns `nearby_build_files` hints when no root build file exists
2. **Recursive scan**: Use `--recursive` to discover all modules:
   ```bash
   python3 scan_tooling.py --recursive /path/to/monorepo
   ```
3. **Module report**: Output includes a `modules` section listing each discovered subproject with its build tool and detected tools
4. **Targeted scan**: Alternatively, point scanner at a specific subproject:
   ```bash
   python3 scan_tooling.py /path/to/monorepo/services/order-service
   ```

## Recommendation Report Format

```markdown
## Tooling Audit Report

### Project Profile
- **Build**: {build_tool} | **Language**: {language} | **Spring Boot**: {version} | **Java**: {version}
- **Test files**: {count} | **Main files**: {count}

### Current Stack
| Category | Tools | Status |
|----------|-------|--------|
| Static Analysis | {tools} | active / disabled / config-only |
| Coverage | {tools} | active |
| ... | ... | ... |

### Tool Configuration
| Setting | Value | Assessment |
|---------|-------|------------|
| JaCoCo threshold | {value} | {e.g., "5% — too low, recommend 70%+"} |
| ktlint SARIF | {enabled/disabled} | {e.g., "Enable for GitHub Security tab"} |
| Lefthook hooks | {list or "none"} | {e.g., "ktlint, gitleaks — add detekt"} |
| Lefthook stage_fixed | {yes/no} | {e.g., "Enable for v2 best practice"} |

### Recommendations
| Priority | Tool | Category | Why |
|----------|------|----------|-----|
| NOW | {tool} | {category} | {reason from research doc} |
| SOON | {tool} | {category} | {reason} |
| LATER | {tool} | {category} | {reason} |
| SKIP | {tool} | {category} | {reason} |

### Tool Selection Protocol

Present tools in priority-ordered rounds. Each round uses AskUserQuestion (multiSelect: true).
Include effort estimates in option descriptions.

**Round 1 — NOW tools** (per ecosystem; if >3 NOW tools across ecosystems, split by ecosystem):

Question: "Which NOW-priority {ecosystem} tools should I configure?"
Options: Up to 3 NOW tools + "Skip {ecosystem} NOW tools"

Example options:
- "Detekt (5 min) — Kotlin static analysis with baseline"
- "MockK (2 min) — add testImplementation dependency"
- "EditorConfig (1 min) — create root .editorconfig"
- "Skip JVM NOW tools"

**Round 2 — Cross-cutting NOW tools** (if any remain after Round 1):

Question: "Which cross-cutting tools should I configure?"
Options: Up to 3 cross-cutting NOW tools + "Skip cross-cutting"

**Round 3 — SOON tools** (if user wants more):

Question: "Any SOON-priority tools to add? (These need minor setup)"
Options: Top 3 SOON tools by impact + "Done — no more tools"

**Collapse rule**: If only 1 ecosystem detected AND <=3 NOW tools total, collapse all
rounds into a single AskUserQuestion with all NOW tools + "Skip setup".
```

## Priority Classification Rules

### Category: Static Analysis

| Tool | Kotlin Project | Java Project | Mixed Project |
|------|---------------|-------------|--------------|
| Detekt | NOW | SKIP | NOW (Kotlin files) |
| ktlint | NOW | SKIP | NOW (Kotlin files) |
| Error Prone | SKIP | NOW | SOON (Java files) |
| SpotBugs | SKIP | NOW | SOON (bytecode) |
| SonarQube | LATER | LATER | LATER |

### Category: Coverage

| Tool | Kotlin Project | Java Project | Mixed Project |
|------|---------------|-------------|--------------|
| Kover | NOW | SKIP | SOON |
| JaCoCo | LATER (if need SonarQube compat) | NOW | NOW |

### Category: Testing Libraries

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| AssertJ | Already in spring-boot-starter-test | KEEP |
| Kotest assertions | When team wants Kotlin DSL | SOON |
| Hamcrest | Should be excluded | NOW (exclude) |
| Instancio | Complex object graphs needed | SOON |
| kotlin-faker | Locale-specific fake data needed | LATER |
| MockK | Kotlin project without it | NOW |
| Mockito | Java project without it | NOW |
| Testcontainers | Not present + uses DB | NOW |
| Spring Modulith test | Has spring-modulith dependency | NOW |

### Category: Architecture

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| ArchUnit | Multi-layer project without it | SOON |

### Category: API Testing

| Tool | Condition | Priority |
|------|-----------|----------|
| MockMvcTester | Spring Boot 3.4+ (built-in) | NOW |
| RestTestClient | Spring Boot 4.0+ (new starter) | SOON |
| REST Assured | Spring Boot 4.0+ | SKIP (javax broken) |

### Category: Property-Based Testing

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| jqwik + jqwik-kotlin | Domain logic with invariants | SOON |
| Kotest property | If already using Kotest runner | LATER |

### Category: Contract Testing

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Pact | Polyglot consumers (mobile, web) | LATER |
| Spring Cloud Contract | JVM-only consumers | LATER |

### Category: Mutation Testing

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| PIT + pitest-kotlin | Test coverage >70% exists | LATER |

### Category: Security

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Trivy | No security scanner present | SOON |
| OWASP DC | No security scanner present | SOON |

### Category: Git Hooks

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Lefthook | No git hook manager + has linters (ktlint/detekt) | SOON |
| Lefthook | Husky or pre-commit already present | SKIP (note: migration possible) |

### Category: CI/CD & Build

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| GitHub Actions | No CI detected | NOW |
| Gradle build cache | Gradle project without it | NOW |
| Renovate | No dependency automation | SOON |
| OpenRewrite | Spring Boot version < 4.0 | SOON |

### Category: Database Testing

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| @DataJpaTest | Has JPA entities, no slice tests | NOW |
| Testcontainers reuse | Has Testcontainers, no reuse config | NOW |

## Version-Aware Rules

| Spring Boot Version | Implications |
|-------------------|-------------|
| < 3.0 | Suggest OpenRewrite migration, javax->jakarta |
| 3.0 - 3.3 | Standard recommendations apply |
| 3.4+ | MockMvcTester available (NOW) |
| 4.0+ | RestTestClient available (SOON), REST Assured SKIP, Jackson 3 awareness |

## Scanner Output Interpretation

The scanner JSON has five top-level keys:

```json
{
  "project": { ... },       // Build tool, language, versions
  "detected_tools": { ... }, // Tools grouped by category (with status)
  "config_files": { ... },   // Config file existence map
  "versions": { ... },       // Detected tool versions
  "tool_config": { ... }     // Tool settings (thresholds, reporters)
}
```

With `--recursive`, a sixth key is added:
```json
{
  "modules": [               // Each discovered module
    {"path": "services/order-service", "build_tool": "gradle-kotlin", "tools": ["detekt", "jacoco"]}
  ]
}
```

**Key checks:**
1. `project.language` -> determines which language-specific tools to recommend/skip
2. `project.spring_boot_version` -> determines version-aware rules
3. `detected_tools.*` -> check both presence and `status` field
4. `status: "disabled"` -> tool is commented out, needs re-enabling or removal
5. `status: "config-only"` -> config file exists but plugin not declared in build
6. `tool_config.jacoco_threshold` -> check if threshold is meaningful (>= 0.70)
7. `tool_config.ktlint_sarif_enabled` -> recommend enabling for GitHub Security integration
8. `config_files` -> missing configs for detected tools suggest incomplete setup
9. `versions` -> outdated versions compared to research doc recommendations
10. `git_hooks` -> check for lefthook/husky/pre-commit; empty means no local enforcement
11. `tool_config.lefthook_hooks` -> list of configured hook commands (if lefthook detected)
12. `tool_config.lefthook_has_stage_fixed` -> whether v2 best practice is used
13. `frontend_tools` -> frontend tools detected in package.json files (for Lefthook wiring only)
    - Each entry has a `path` (relative to project root) and `tools` map
    - Only present when frontend tools are actually detected
    - Not used in recommendation phase — only consumed during Lefthook setup (Phase 2)
14. `editor_config.subdirectory_configs` -> list of subdirectory `.editorconfig` files with `is_root` flag
    - If any entry has `is_root: true`, warn: "Subdirectory {path}/.editorconfig has `root = true` — this blocks inheritance from the project root .editorconfig"
    - Must be resolved before creating or modifying root `.editorconfig`

## Lefthook Setup Flow (Phase 2)

When user selects Lefthook from recommendations:

### 1. Determine Installation Method

- **Has `package.json`**: Install as npm devDep (`pnpm add -D lefthook` or `npm i -D lefthook`)
- **No `package.json`**: Install as system binary (`brew install lefthook`)

### 2. Generate `lefthook.yml`

Tailor the config based on detected tools in `detected_tools.static_analysis`:

```yaml
# Lefthook — Git hooks for {project_name}
# Install: pnpm add -D lefthook && npx lefthook install

pre-commit:
  parallel: true
  commands:
    gitleaks:
      run: gitleaks protect --staged --verbose
      skip:
        - merge
        - rebase

    # Include if ktlint detected in static_analysis
    ktlint:
      glob: "**/*.{kt,kts}"
      run: ./gradlew ktlintCheck

    # Include if detekt detected in static_analysis
    detekt:
      glob: "**/*.{kt,kts}"
      run: ./gradlew detekt

    # --- Frontend hooks (include if frontend_tools detected) ---

    # Include if eslint detected in frontend_tools
    eslint:
      glob: "**/*.{ts,tsx,js,jsx}"
      run: npx eslint --fix {staged_files}
      stage_fixed: true

    # Include if prettier detected in frontend_tools
    prettier-code:
      glob: "**/*.{ts,tsx,js,jsx}"
      run: npx prettier --write {staged_files}
      stage_fixed: true

    # Include if prettier detected in frontend_tools
    prettier-assets:
      glob: "**/*.{json,css,md,yml,yaml}"
      run: npx prettier --write {staged_files}
      stage_fixed: true
```

**Monorepo adjustment**: If `--recursive` was used or project has modules, narrow `glob:` patterns to specific module paths (e.g., `apps/api/**/*.{kt,kts}`) and set `root:` accordingly. Remember: **globs are always resolved from the git repo root**, regardless of `root:`.

**Frontend tools in monorepo**: When `frontend_tools[].path` is NOT `(root)`, scope globs and set `root:` to the frontend directory:

```yaml
    eslint:
      glob: "apps/web/**/*.{ts,tsx,js,jsx}"
      root: "apps/web/"
      run: npx eslint --fix {staged_files}
      stage_fixed: true

    prettier-code:
      glob: "apps/web/**/*.{ts,tsx,js,jsx}"
      root: "apps/web/"
      run: npx prettier --write {staged_files}
      stage_fixed: true

    prettier-assets:
      glob: "apps/web/**/*.{json,css,md,yml,yaml}"
      root: "apps/web/"
      run: npx prettier --write {staged_files}
      stage_fixed: true
```

Remember: **globs are always resolved from the git repo root**, regardless of `root:`. The `root:` directive only changes the working directory for `run:`.

**Multiple frontend directories**: When multiple frontend apps exist (e.g., `apps/web/` + `apps/admin/`), suffix hook names to avoid conflicts: `eslint-web`, `eslint-admin`, `prettier-code-web`, `prettier-code-admin`, etc.

**Tailwind CSS + Prettier**: When both `prettier-plugin-tailwindcss` and `tailwindcss` are detected, Prettier automatically applies Tailwind class sorting. No additional hook is needed. However, if using Tailwind CSS v4, ensure the Prettier config includes `tailwindStylesheet` pointing to the CSS entry file containing `@theme` — otherwise class sorting silently becomes a no-op.

### 3. Install and Verify

```bash
# Install hooks into .git/hooks/
npx lefthook install
# Output: sync hooks: ✔️ (pre-commit)

# Dry run — verify hooks skip cleanly with no staged files
npx lefthook run pre-commit
```

### 4. Recommend gitleaks

If `which gitleaks` fails, recommend installation:
```bash
brew install gitleaks
gitleaks version  # verify
```

### 5. Re-run Scanner

Re-run `scan_project.py` to confirm `git_hooks` category now shows lefthook as `active`.

---

## Post-Setup Verification (Phase 2)

After configuring EACH tool, perform these verification steps before moving to the next tool.

### 1. Run the tool's check command

| Tool | Verification Command |
|------|---------------------|
| Detekt | `./gradlew detekt` |
| Kover | `./gradlew koverHtmlReport` (then check report exists) |
| ktlint | `./gradlew ktlintCheck` |
| ESLint | `npx eslint .` |
| Prettier | `npx prettier --check .` |
| Ruff | `ruff check .` |
| mypy | `mypy .` |
| Lefthook | `npx lefthook run pre-commit` |

### 2. Verify patterns against codebase

For tools with filter/exclusion patterns (Kover, Detekt, .gitignore additions):
- List actual file/class paths that should match the pattern
- Verify each path matches by testing the pattern logic
- For Kover: check that `*` only matches within one package segment

### 3. Check for config inheritance conflicts

- EditorConfig: check `editor_config.subdirectory_configs` for `is_root: true` entries that block inheritance
- Gradle: verify no `buildSrc` or convention plugin overrides the new plugin declaration
- tsconfig: verify no `extends` chain overrides new strict settings

### 4. If verification fails

- Fix the issue immediately
- Re-run the verification command
- Do NOT move to the next tool until verification passes

---

## Setup Guards

Before configuring any tool in Phase 2, apply these guards.

### Version Resolution

NEVER guess a tool version. Use this resolution order:

1. Check the research doc's version compatibility table (if present)
2. If research doc lacks the version, fetch the tool's releases page or Gradle Plugin Portal via WebFetch
3. For JVM tools: verify Kotlin version compatibility before applying
4. For Gradle plugins: verify the correct plugin ID (names change across major versions)

### Tool-Specific Guards

**Detekt**:
- Kotlin 2.0.x → Detekt 1.23.x (plugin ID: `io.gitlab.arturbosch.detekt`)
- Kotlin 2.1.x+ → Detekt 2.x (plugin ID: `dev.detekt`); may need Kotlin version pin in detekt config
- Detekt 2.x config properties differ from 1.x (e.g., `threshold` → `allowedLines`, `thresholdInFiles` → `allowedFunctionsPerFile`)
- When in doubt: run `./gradlew detektGenerateConfig` and modify the generated file

**Kover**:
- Filter pattern `*` matches characters within one package segment only (NOT across dots like Unix globs)
- Use `annotatedBy("fully.qualified.Annotation")` for annotation-based exclusion
- Recommended for Spring `@Configuration` classes: `annotatedBy("org.springframework.context.annotation.Configuration")`
- Always test exclusion patterns against actual class paths: list matching classes and verify the pattern covers them

**EditorConfig**:
- Before creating root `.editorconfig`, check scanner output for `editor_config.subdirectory_configs`
- If any subdirectory has `is_root: true`, it blocks inheritance — warn the user and offer to remove `root = true` from the subdirectory file

---

## Node.js/TypeScript Classification Rules

### Category: Static Analysis

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| ESLint (flat config) | No linter present | NOW |
| Biome | No linter + wants all-in-one (replaces ESLint + Prettier) | SOON |
| ESLint flat config migration | Has legacy `.eslintrc.*` config | SOON |

### Category: Formatting

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Prettier | No formatter + not using Biome | NOW |
| Biome (formatter) | Already using Biome for linting | NOW (enable) |

### Category: Type Checking

| Setting | When to Recommend | Priority |
|---------|------------------|----------|
| TypeScript `strict: true` | TS project + strict not enabled | NOW |
| `noUncheckedIndexedAccess` | TS strict enabled but this flag missing | SOON |
| `exactOptionalPropertyTypes` | TS strict enabled but this flag missing | LATER |

### Category: Testing

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Vitest | No test runner + Vite/Next.js/React project | NOW |
| Jest | No test runner + non-Vite project | NOW |
| Playwright Test | No E2E test runner | SOON |
| @testing-library/react | React project without it | SOON |

### Category: Coverage

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| @vitest/coverage-v8 | Has Vitest but no coverage | SOON |
| c8 | Has Node.js tests but no coverage | SOON |
| istanbul/nyc | Legacy; prefer c8 or vitest coverage | SKIP |

### Category: Bundle Analysis

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| size-limit | Library project without bundle checks | LATER |
| @next/bundle-analyzer | Next.js project without bundle analysis | LATER |

### Category: Framework-Specific

| Framework | Tools to Check | Priority |
|-----------|---------------|----------|
| Next.js | `next lint` in scripts, @next/bundle-analyzer | SOON |
| React | @testing-library/react, vitest | NOW |

### Node.js Phase 2: Setup Patterns

| Tool | Setup Command |
|------|--------------|
| ESLint (flat config) | `pnpm add -D eslint @eslint/js typescript-eslint` |
| Prettier | `pnpm add -D prettier` + create `.prettierrc` |
| Vitest | `pnpm add -D vitest @vitest/coverage-v8` |
| Playwright | `pnpm add -D @playwright/test && npx playwright install` |
| TypeScript strict | Edit `tsconfig.json`: set `"strict": true` |

---

## Python Classification Rules

### Category: Linting

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Ruff (linter) | No linter present | NOW |
| Flake8 | Has Flake8, suggest migrating to Ruff | LATER (migrate) |
| Pylint | Has Pylint, suggest migrating to Ruff | LATER (migrate) |

### Category: Formatting

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Ruff (formatter) | Has Ruff linter but no formatter | NOW |
| Black | No formatter + not using Ruff formatter | SOON |
| isort | Using Black without isort (Ruff handles both) | SKIP if using Ruff |

### Category: Type Checking

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| mypy (strict) | No type checker + has type annotations | NOW |
| Pyright | Alternative to mypy for VS Code users | SOON |
| mypy `strict = true` | Has mypy but not in strict mode | SOON |

### Category: Testing

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| pytest | No test runner (or only unittest) | NOW |
| hypothesis | Domain logic with invariants (property testing) | LATER |

### Category: Coverage

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| pytest-cov | Has pytest but no coverage | SOON |
| coverage.py | No coverage tool | SOON |

### Category: Security

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| bandit | No security scanner | SOON |
| pip-audit | No dependency scanning | SOON |
| safety | Alternative to pip-audit | LATER |

### Category: Task Runner

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Nox | No task automation + complex test matrix | LATER |
| tox | No task automation + CI matrix needed | LATER |

### Category: Dependency Manager

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| uv | Using pip without lockfile | SOON |

### Python Phase 2: Setup Patterns

| Tool | Setup Command |
|------|--------------|
| Ruff | `uv add --dev ruff` + add `[tool.ruff]` to pyproject.toml |
| mypy | `uv add --dev mypy` + add `[tool.mypy]` with `strict = true` |
| pytest | `uv add --dev pytest pytest-cov` |
| bandit | `uv add --dev bandit` |
| pip-audit | `uv add --dev pip-audit` |

---

## Cross-Cutting Classification Rules

### Category: Git Hooks

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Lefthook | No hook manager + has linters (any ecosystem) | SOON |
| Lefthook | Husky or pre-commit already present | SKIP (migration possible) |

### Category: Commit Conventions

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| commitlint | No commit conventions + team project | LATER |
| commitizen | No commit conventions + wants interactive | LATER |

### Category: Editor Config

| Setting | When to Recommend | Priority |
|---------|------------------|----------|
| `.editorconfig` | Missing entirely | NOW |
| `root = true` | EditorConfig exists but missing `root = true` | NOW |
| `trim_trailing_whitespace` | EditorConfig exists but not set | SOON |

### Category: Dependency Automation

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Renovate | No dependency automation (preferred over Dependabot) | SOON |
| Dependabot | No dep automation + simpler setup needed | SOON |

### Category: Security Scanning

| Tool | When to Recommend | Priority |
|------|------------------|----------|
| Trivy | No security scanner in CI | SOON |
| gitleaks | No secret scanning | SOON |

---

## Multi-Ecosystem Report Format

For projects with multiple ecosystems, the report groups by ecosystem:

```markdown
## Tooling Audit Report

### Detected Ecosystems
- JVM (Gradle Kotlin DSL) — root: `.`
- Node.js (pnpm + Turbo) — root: `apps/web`

---

### JVM Ecosystem (root: `.`)

#### Project Profile
- **Build**: Gradle (Kotlin DSL) | **Language**: Kotlin | **Spring Boot**: 4.0.1

#### Current Stack
| Category | Tools | Status |
|----------|-------|--------|
| ... | ... | ... |

#### Recommendations
| Priority | Tool | Category | Why |
|----------|------|----------|-----|
| ... | ... | ... | ... |

---

### Node.js Ecosystem (root: `apps/web`)

#### Project Profile
- **Package Manager**: pnpm | **Framework**: Next.js | **TypeScript**: strict

#### Current Stack
| Category | Tools | Status |
|----------|-------|--------|
| ... | ... | ... |

#### Recommendations
| Priority | Tool | Category | Why |
|----------|------|----------|-----|
| ... | ... | ... | ... |

---

### Cross-Cutting Tools

#### Current Stack
| Category | Tools | Status |
|----------|-------|--------|
| CI/CD | GitHub Actions | active |
| Git Hooks | (none) | — |
| ... | ... | ... |

#### Recommendations
| Priority | Tool | Category | Why |
|----------|------|----------|-----|
| NOW | EditorConfig | Editor | Missing entirely |
| SOON | Lefthook | Git Hooks | Enforce linters on commit |
| SOON | Renovate | Dependencies | Auto-update across all ecosystems |
| SOON | Trivy | Security | Vulnerability + secret scanning in CI |

---

### Tool Selection

Use the multi-round Tool Selection Protocol (see Recommendation Report Format above).
```
