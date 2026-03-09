# Workflow: Spring Boot Quality Stack

## Phase 1: Recommend

```
USER invokes spring-boot-quality-stack
    │
    ▼
Run scan_tooling.py on project root
    │
    ├── "error": "no_build_file"?
    │   ├── YES → check nearby_build_files, suggest --recursive or subproject path
    │   └── NO → continue
    │
    ▼
Fetch research docs via WebFetch
  ├── https://raw.githubusercontent.com/joaquimscosta/arkhe-claude-plugins/main/docs/research/jvm-quality-tools-evaluation.md
  └── https://raw.githubusercontent.com/joaquimscosta/arkhe-claude-plugins/main/docs/research/kotlin-spring-boot-testing-ecosystem.md
    │
    ├── Fetch failed?
    │   ├── YES → warn user, proceed with scanner + LLM knowledge
    │   └── NO → continue
    │
    ▼
Cross-reference: detected tools vs recommended tools
  ├── Check status field: active / disabled / config-only
  ├── Review tool_config (jacoco_threshold, ktlint_sarif_enabled)
  └── Compare versions against research recommendations
    │
    ▼
Apply priority classification rules
  ├── Language-aware filtering (Kotlin-only, Java-only, mixed)
  ├── Version-aware filtering (Spring Boot 3.x vs 4.x)
  └── Research priority mapping (NOW/SOON/LATER from research docs)
    │
    ▼
Generate recommendation report
    │
    ▼
Present to user with AskUserQuestion (multiSelect: true, top NOW/SOON tools as options)
```

## Phase 2: Setup

```
USER selects tools via AskUserQuestion response (or types custom selection)
    │
    ▼
Read relevant research doc section for selected tool
    │
    ▼
For each selected tool:
  ├── 1. Add Gradle plugin / Maven plugin declaration
  ├── 2. Add test dependencies (if applicable)
  ├── 3. Create config files (detekt.yml, .trivyignore, etc.)
  └── 4. Add CI/CD workflow steps (if applicable)
    │
    ▼
Re-run scan_tooling.py to confirm detection
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

### Ready to set up?

[AskUserQuestion — multiSelect: true]
Question: "Which tools would you like me to configure?"
Options (dynamically built from NOW + SOON recommendations):
1. "{tool1} — {short reason}" (NOW items first)
2. "{tool2} — {short reason}"
3. "{tool3} — {short reason}"
4. "Skip setup — I'll configure manually"

Include up to 4 highest-priority tools as options. User can select multiple or type custom choices via "Other".
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

Re-run `scan_tooling.py` to confirm `git_hooks` category now shows lefthook as `active`.
