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
    "migrations": []
  },
  "config_files": {
    "detekt.yml": false,
    "detekt-config.yml": false,
    ".editorconfig": true,
    ".trivyignore": false,
    "renovate.json": false,
    ".github/dependabot.yml": false,
    "sonar-project.properties": false
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
Tell me which tools you'd like to configure and I'll add the necessary plugins, dependencies, and configuration files.

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
    "migrations": []
  },
  "config_files": {
    "spotbugs-exclude.xml": true,
    "sonar-project.properties": true,
    ".github/dependabot.yml": true
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
Tell me which tools you'd like to configure and I'll add the necessary plugins, dependencies, and configuration files.

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

User selects **Detekt** and **Trivy** from Example 1 recommendations.

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
