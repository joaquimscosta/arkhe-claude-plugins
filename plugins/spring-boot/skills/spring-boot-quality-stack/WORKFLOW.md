# Workflow: Spring Boot Quality Stack

## Phase 1: Recommend

```
USER invokes /spring-boot-quality-stack
    │
    ▼
Run scan_tooling.py on project root
    │
    ▼
Parse JSON output → project profile + detected tools
    │
    ▼
Read research documents (2 files via Read tool)
  ├── docs/research/jvm-quality-tools-evaluation.md
  └── docs/research/kotlin-spring-boot-testing-ecosystem.md
    │
    ▼
Cross-reference: detected tools vs recommended tools
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
Present to user with "Ready to set up?" prompt
```

## Phase 2: Setup

```
USER selects tools to configure
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
| < 3.0 | Suggest OpenRewrite migration, javax→jakarta |
| 3.0 - 3.3 | Standard recommendations apply |
| 3.4+ | MockMvcTester available (NOW) |
| 4.0+ | RestTestClient available (SOON), REST Assured SKIP, Jackson 3 awareness |

## Scanner Output Interpretation

The scanner JSON has four top-level keys:

```json
{
  "project": { ... },      // Build tool, language, versions
  "detected_tools": { ... }, // Tools grouped by category
  "config_files": { ... },   // Config file existence map
  "versions": { ... }        // Detected tool versions
}
```

**Key checks:**
1. `project.language` → determines which language-specific tools to recommend/skip
2. `project.spring_boot_version` → determines version-aware rules
3. `detected_tools.*` → empty arrays indicate gaps to fill
4. `config_files` → missing configs for detected tools suggest incomplete setup
5. `versions` → outdated versions compared to research doc recommendations
