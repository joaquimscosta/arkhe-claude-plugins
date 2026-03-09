# Examples: Spring Boot Tooling Recommender

## Example 1: Kotlin Project with Minimal Tooling

### Scanner Output

```json
{
  "project": {
    "build_tool": "gradle-kotlin",
    "spring_boot_version": "4.0.1",
    "language": "kotlin",
    "java_version": "21",
    "kotlin_version": "2.2.0",
    "has_version_catalog": true,
    "test_file_count": 8,
    "main_file_count": 45
  },
  "detected_tools": {
    "static_analysis": [],
    "testing_libraries": [
      {"name": "assertj", "status": "active", "source": "build-file"},
      {"name": "mockk", "status": "active", "source": "build-file"},
      {"name": "testcontainers", "status": "active", "source": "build-file"}
    ],
    "coverage": [
      {"name": "jacoco", "status": "active", "source": "build-file"}
    ],
    "mutation_testing": [],
    "architecture": [],
    "contract_testing": [],
    "property_testing": [],
    "api_testing": [],
    "benchmarking": [],
    "ci_cd": [
      {"name": "github-actions", "status": "active", "source": "ci-file"}
    ],
    "dependency_management": [],
    "security": [],
    "migrations": [],
    "git_hooks": []
  },
  "config_files": {
    "detekt.yml": false,
    "detekt-config.yml": false,
    ".editorconfig": true,
    ".trivyignore": false,
    "renovate.json": false,
    ".github/dependabot.yml": false,
    "sonar-project.properties": false,
    "lefthook.yml": false,
    ".husky/_/husky.sh": false,
    ".pre-commit-config.yaml": false
  },
  "versions": {
    "spring-boot": "4.0.1",
    "kotlin": "2.2.0",
    "java": "21",
    "jacoco": "0.8.14"
  },
  "tool_config": {
    "jacoco_threshold": "0.05",
    "ktlint_sarif_enabled": false
  }
}
```

### Generated Recommendation Report

## Tooling Audit Report

### Project Profile
- **Build**: Gradle (Kotlin DSL) | **Language**: Kotlin | **Spring Boot**: 4.0.1 | **Java**: 21
- **Test files**: 8 | **Main files**: 45

### Current Stack
| Category | Tools | Status |
|----------|-------|--------|
| Testing | AssertJ, MockK, Testcontainers | active |
| Coverage | JaCoCo | active |
| CI/CD | GitHub Actions | active |

### Tool Configuration
| Setting | Value | Assessment |
|---------|-------|------------|
| JaCoCo threshold | 5% | Too low — recommend 70%+ for meaningful coverage gates |

### Recommendations
| Priority | Tool | Category | Why |
|----------|------|----------|-----|
| NOW | Detekt 1.23.8 | Static Analysis | Native Kotlin AST analysis; catches coroutine misuse, complexity, code smells |
| NOW | ktlint 1.8.0 | Static Analysis | Zero-config Kotlin formatter with auto-fix; pre-commit hooks |
| NOW | Kover 0.9.7 | Coverage | Kotlin-native coverage; handles inline functions, data classes correctly (JaCoCo doesn't) |
| NOW | Hamcrest | Testing | EXCLUDE from spring-boot-starter-test — superseded by AssertJ |
| NOW | JaCoCo threshold | Coverage | Raise threshold from 5% to at least 70% |
| SOON | Instancio 5.4.1 | Test Data | Auto-generate complex object graphs; complement manual fixtures |
| SOON | Kotest assertions 6.1.4 | Testing | Kotlin DSL assertions (`shouldBe`, `shouldContain`); no runner needed |
| SOON | Trivy | Security | Free, comprehensive vulnerability + secret scanning |
| SOON | Renovate | Dependencies | Auto-update dependencies; supports Gradle version catalogs |
| SOON | jqwik 1.9.3 | Property Testing | JUnit 5 native; test domain invariants (Money, TransactionNumber) |
| LATER | PIT 1.19.1 | Mutation Testing | Wait until test coverage >70%; currently only 8 test files |
| LATER | Pact 4.6.x | Contract Testing | Valuable when mobile KMP client consumes the API |
| LATER | JMH 1.37 | Benchmarking | Add when performance-sensitive code paths exist |
| SKIP | Error Prone | Static Analysis | Java-only; not applicable for pure Kotlin project |
| SKIP | SpotBugs | Static Analysis | Bytecode analysis; low value for pure Kotlin with Detekt |
| SKIP | REST Assured | API Testing | spring-mock-mvc broken with jakarta (Spring Boot 4) |

### Ready to set up?

[AskUserQuestion — multiSelect: true]
Question: "Which tools would you like me to configure?"
Options:
1. "Detekt 1.23.8 — native Kotlin static analysis"
2. "ktlint 1.8.0 — zero-config Kotlin formatter"
3. "Kover 0.9.7 — Kotlin-native coverage (replaces JaCoCo)"
4. "Skip setup — I'll configure manually"

---

## Example 2: Well-Equipped Java Project

### Scanner Output

```json
{
  "project": {
    "build_tool": "maven",
    "spring_boot_version": "3.4.2",
    "language": "java",
    "java_version": "21",
    "kotlin_version": null,
    "has_version_catalog": false,
    "test_file_count": 120,
    "main_file_count": 200
  },
  "detected_tools": {
    "static_analysis": [
      {"name": "error-prone", "status": "active", "source": "build-file"},
      {"name": "spotbugs", "status": "active", "source": "build-file"},
      {"name": "sonarqube", "status": "active", "source": "build-file"}
    ],
    "testing_libraries": [
      {"name": "assertj", "status": "active", "source": "build-file"},
      {"name": "mockito", "status": "active", "source": "build-file"},
      {"name": "testcontainers", "status": "active", "source": "build-file"}
    ],
    "coverage": [
      {"name": "jacoco", "status": "active", "source": "build-file"}
    ],
    "mutation_testing": [
      {"name": "pitest", "status": "active", "source": "build-file"}
    ],
    "architecture": [
      {"name": "archunit", "status": "active", "source": "build-file"}
    ],
    "contract_testing": [
      {"name": "spring-cloud-contract", "status": "active", "source": "build-file"}
    ],
    "property_testing": [],
    "api_testing": [],
    "benchmarking": [],
    "ci_cd": [
      {"name": "github-actions", "status": "active", "source": "ci-file"}
    ],
    "dependency_management": [
      {"name": "dependabot", "status": "active", "source": "config-file"}
    ],
    "security": [
      {"name": "owasp-dependency-check", "status": "active", "source": "build-file"}
    ],
    "migrations": [],
    "git_hooks": []
  },
  "config_files": {
    "spotbugs-exclude.xml": true,
    "sonar-project.properties": true,
    ".github/dependabot.yml": true,
    "lefthook.yml": false,
    ".husky/_/husky.sh": false,
    ".pre-commit-config.yaml": false
  },
  "versions": {
    "spring-boot": "3.4.2",
    "java": "21"
  },
  "tool_config": {
    "jacoco_threshold": "0.80"
  }
}
```

### Generated Recommendation Report

## Tooling Audit Report

### Project Profile
- **Build**: Maven | **Language**: Java | **Spring Boot**: 3.4.2 | **Java**: 21
- **Test files**: 120 | **Main files**: 200

### Current Stack
| Category | Tools | Status |
|----------|-------|--------|
| Static Analysis | Error Prone, SpotBugs, SonarQube | active |
| Testing | AssertJ, Mockito, Testcontainers | active |
| Coverage | JaCoCo (threshold: 80%) | active |
| Mutation Testing | PIT | active |
| Architecture | ArchUnit | active |
| Contract Testing | Spring Cloud Contract | active |
| CI/CD | GitHub Actions | active |
| Dependencies | Dependabot | active |
| Security | OWASP Dependency-Check | active |

### Recommendations
| Priority | Tool | Category | Why |
|----------|------|----------|-----|
| NOW | MockMvcTester | API Testing | Built into Spring Boot 3.4+; full AssertJ integration for controller tests |
| SOON | Trivy | Security | Complement OWASP DC with container + secret scanning; lower false positives |
| SOON | OpenRewrite | Migrations | Prepare for Spring Boot 4.0 migration (javax->jakarta automated) |
| SOON | Renovate | Dependencies | More capable than Dependabot for Maven (auto-merge, stability days) |
| LATER | JMH 1.37 | Benchmarking | Performance regression detection for critical paths |
| SKIP | Detekt, ktlint, Kover, MockK | Various | Java-only project; Kotlin tools not applicable |

### Ready to set up?

[AskUserQuestion — multiSelect: true]
Question: "Which tools would you like me to configure?"
Options:
1. "MockMvcTester — built-in AssertJ API testing for Spring Boot 3.4+"
2. "Trivy — comprehensive vulnerability + secret scanning"
3. "OpenRewrite — automated Spring Boot 4.0 migration"
4. "Skip setup — I'll configure manually"

---

## Example 3: Disabled Tools Detected

### Scanner Output (partial)

```json
{
  "detected_tools": {
    "static_analysis": [
      {"name": "detekt", "status": "disabled", "source": "build-file"},
      {"name": "ktlint", "status": "active", "source": "build-file"}
    ],
    "coverage": [
      {"name": "jacoco", "status": "config-only", "source": "config-file"}
    ]
  },
  "tool_config": {
    "ktlint_sarif_enabled": false
  }
}
```

### Interpretation

- **Detekt**: `disabled` — plugin is commented out in the build file. Recommendation: re-enable or remove the commented-out block.
- **JaCoCo**: `config-only` — a JaCoCo config exists but the plugin isn't declared in the build file. Likely configured via `buildSrc/` or a convention plugin. Verify manually.
- **ktlint SARIF**: not enabled. Recommendation: enable SARIF output for GitHub Security tab integration.

---

## Example 4: Phase 2 Setup Walkthrough

User selects **Detekt** and **Trivy** via AskUserQuestion from Example 1 recommendations.

### Detekt Setup

**1. Add Gradle plugin:**
```kotlin
// build.gradle.kts
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.8"
}

detekt {
    config.setFrom(file("config/detekt.yml"))
    buildUponDefaultConfig = true
}

dependencies {
    detektPlugins("io.gitlab.arturbosch.detekt:detekt-formatting:1.23.8")
}
```

**2. Generate default config:**
```bash
./gradlew detektGenerateConfig
```

This creates `config/detekt.yml` with all default rules that you can customize.

**3. Add CI step** (if GitHub Actions detected):
```yaml
# In .github/workflows/build.yml, add step:
- name: Detekt
  run: ./gradlew detekt
```

### Trivy Setup

**1. Create `.trivyignore`** (empty initially):
```
# Add CVE IDs to suppress false positives
# Example: CVE-2023-12345
# Example with expiry: CVE-2024-56789 exp:2026-06-01
```

**2. Add CI step:**
```yaml
# In .github/workflows/build.yml, add job:
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Run Trivy
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'HIGH,CRITICAL'

    - name: Upload to GitHub Security
      uses: github/codeql-action/upload-sarif@v3
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
```

**3. Local usage:**
```bash
brew install trivy  # macOS
trivy fs --severity HIGH,CRITICAL .
```

### Verification

Re-run the scanner to confirm:
```bash
python3 scan_tooling.py /path/to/project
```

Expected changes in output:
- `detected_tools.static_analysis` includes `{"name": "detekt", "status": "active", "source": "build-file"}`
- `config_files[".trivyignore"]` is `true`
- `detected_tools.security` includes `{"name": "trivy", "status": "active", "source": "config-file"}`

---

## Example 5: Kotlin Project with Linters but No Git Hooks

### Scanner Output (partial)

```json
{
  "project": {
    "build_tool": "gradle-kotlin",
    "spring_boot_version": "4.0.1",
    "language": "kotlin",
    "java_version": "21",
    "kotlin_version": "2.2.0"
  },
  "detected_tools": {
    "static_analysis": [
      {"name": "detekt", "status": "active", "source": "build-file"},
      {"name": "ktlint", "status": "active", "source": "build-file"}
    ],
    "git_hooks": [],
    "ci_cd": [
      {"name": "github-actions", "status": "active", "source": "ci-file"}
    ]
  },
  "config_files": {
    "lefthook.yml": false,
    ".husky/_/husky.sh": false,
    ".pre-commit-config.yaml": false
  }
}
```

### Interpretation

The project has Detekt and ktlint configured in the build, but no git hook manager enforces them locally. Developers can commit without running linters — CI catches violations late.

### Recommendation

| Priority | Tool | Category | Why |
|----------|------|----------|-----|
| SOON | Lefthook | Git Hooks | Enforce ktlint + Detekt on every commit; catch violations before CI |

### Phase 2: Lefthook Setup

**1. Install lefthook:**
```bash
pnpm add -D lefthook    # if package.json exists
# OR
brew install lefthook    # system binary
```

**2. Generate `lefthook.yml`:**
```yaml
# Lefthook — Git hooks for the project
# Install: pnpm add -D lefthook && npx lefthook install

pre-commit:
  parallel: true
  commands:
    gitleaks:
      run: gitleaks protect --staged --verbose
      skip:
        - merge
        - rebase

    ktlint:
      glob: "**/*.{kt,kts}"
      run: ./gradlew ktlintCheck

    detekt:
      glob: "**/*.{kt,kts}"
      run: ./gradlew detekt
```

**3. Install and verify:**
```bash
npx lefthook install
npx lefthook run pre-commit
# All hooks should show "(skip) no files for inspection"
```

**4. Re-run scanner:**
```bash
python3 scan_tooling.py /path/to/project
```

Expected: `detected_tools.git_hooks` now includes `{"name": "lefthook", "status": "active", "source": "config-file"}`

---

## Example 6: Project with Existing Husky (Conflict)

### Scanner Output (partial)

```json
{
  "detected_tools": {
    "static_analysis": [
      {"name": "ktlint", "status": "active", "source": "build-file"}
    ],
    "git_hooks": [
      {"name": "husky", "status": "active", "source": "config-file"}
    ]
  },
  "config_files": {
    "lefthook.yml": false,
    ".husky/_/husky.sh": true
  }
}
```

### Interpretation

Husky is already managing git hooks. Adding lefthook would conflict. Recommendation: SKIP lefthook or migrate from Husky first.

### Recommendation

| Priority | Tool | Category | Why |
|----------|------|----------|-----|
| SKIP | Lefthook | Git Hooks | Husky already present — migration needed first (remove `.husky/`, reset `git config core.hooksPath`) |

---

## Example 7: Monorepo with Frontend + Backend (Lefthook Wiring)

### Scanner Output (partial — showing frontend_tools)

```json
{
  "project": {
    "build_tool": "gradle-kotlin",
    "spring_boot_version": "4.0.1",
    "language": "kotlin"
  },
  "detected_tools": {
    "static_analysis": [
      {"name": "detekt", "status": "active", "source": "build-file"},
      {"name": "ktlint", "status": "active", "source": "build-file"}
    ],
    "git_hooks": []
  },
  "frontend_tools": [
    {
      "path": "apps/web",
      "tools": {
        "eslint": {"detected": true, "version": "^9.17.0", "source": "package-json", "config_file": "eslint.config.mjs"},
        "prettier": {"detected": true, "version": "^3.4.2", "source": "package-json", "config_file": ".prettierrc"},
        "tailwindcss": {"detected": true, "version": "^4.0.0", "source": "package-json", "config_file": null},
        "prettier-plugin-tailwindcss": {"detected": true, "version": "^0.6.11", "source": "package-json", "config_file": null}
      }
    }
  ]
}
```

### Interpretation

The monorepo has a Kotlin Spring Boot backend (`apps/api/`) with Detekt and ktlint, plus a frontend app (`apps/web/`) with ESLint, Prettier, and Tailwind CSS. No git hook manager is configured.

### Phase 2: Lefthook Setup with Frontend Hooks

**Generated `lefthook.yml`:**
```yaml
# Lefthook — Git hooks for the monorepo
# Install: pnpm add -D lefthook && npx lefthook install

pre-commit:
  parallel: true
  commands:
    gitleaks:
      run: gitleaks protect --staged --verbose
      skip:
        - merge
        - rebase

    # JVM hooks (from detected_tools.static_analysis)
    ktlint:
      glob: "apps/api/**/*.{kt,kts}"
      root: "apps/api/"
      run: ./gradlew ktlintCheck

    detekt:
      glob: "apps/api/**/*.{kt,kts}"
      root: "apps/api/"
      run: ./gradlew detekt

    # Frontend hooks (from frontend_tools, path: apps/web)
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

**Key decisions:**
- Globs use full paths from repo root (`apps/web/**/*`) even though `root:` is set
- Frontend hooks use `stage_fixed: true` (lefthook v2 best practice) so formatted files are auto-restaged
- Tailwind CSS class sorting happens automatically through `prettier-plugin-tailwindcss` — no separate hook needed
- Since Tailwind CSS v4 is detected, remind user to verify `tailwindStylesheet` in `.prettierrc` points to the correct CSS entry file
