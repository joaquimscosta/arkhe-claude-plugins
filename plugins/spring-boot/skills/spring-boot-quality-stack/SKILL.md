---
name: spring-boot-quality-stack
description: >
  Scan a JVM project to detect configured quality and testing tools,
  cross-reference against research-backed recommendations, and assist with setup.
  Use when user asks to "audit tooling", "recommend tools", "quality stack",
  "what tools am I missing", "setup detekt", "add coverage", "configure CI quality pipeline".
disable-model-invocation: true
---

# Spring Boot Quality Stack

Scan a project's build configuration, cross-reference against curated research documents, and assist with tool setup.

## Two-Phase Workflow

### Phase 1: Recommend

1. **Run the scanner** on the project root:

```bash
python3 <skill-path>/scripts/scan_tooling.py <project-root>
```

2. **Read the research documents** to get current recommendations:

```
docs/research/jvm-quality-tools-evaluation.md
docs/research/kotlin-spring-boot-testing-ecosystem.md
```

Use the Read tool to load these files. They contain versioned, sourced recommendations that are updated independently of this skill.

3. **Cross-reference** scanner JSON output against research recommendations:
   - Identify tools recommended by research but missing from the project
   - Flag tools that are present but outdated or superseded
   - Note tools to SKIP based on project profile (language, Spring Boot version)

4. **Generate the recommendation report** using the format below.

### Phase 2: Setup

After the user selects tools to configure:

1. Read the relevant section from the research document for setup instructions
2. For each selected tool, apply changes:
   - Add Gradle plugin or Maven plugin declaration
   - Add test dependencies
   - Create config files (detekt.yml, .trivyignore, etc.)
   - Add CI/CD workflow steps if applicable
3. Re-run the scanner to confirm detection

## Priority Classification

Classify each recommendation based on project context:

| Priority | Criteria |
|----------|----------|
| **NOW** | Essential missing tools, zero-dependency additions, items marked NOW in research |
| **SOON** | High-value additions requiring minor setup, items marked SOON in research |
| **LATER** | Nice-to-have tools with prerequisites, items marked LATER in research |
| **SKIP** | Not applicable for this project (wrong language, incompatible version, deprecated) |

**Language-aware rules:**
- Pure Kotlin → SKIP Error Prone, SpotBugs (Java-only or bytecode-only value)
- Pure Java → SKIP Detekt, ktlint, Kover, MockK, kotlin-faker
- Spring Boot 4+ → SKIP REST Assured spring-mock-mvc (broken with jakarta)
- Spring Boot 4+ → NOW MockMvcTester (built-in replacement)

## Recommendation Report Format

```markdown
## Tooling Audit Report

### Project Profile
- **Build**: {build_tool} | **Language**: {language} | **Spring Boot**: {version} | **Java**: {version}
- **Test files**: {count} | **Main files**: {count}

### Current Stack
| Category | Tools | Status |
|----------|-------|--------|
| Static Analysis | {tools} | Configured |
| Coverage | {tools} | Configured |
| ... | ... | ... |

### Recommendations
| Priority | Tool | Category | Why |
|----------|------|----------|-----|
| NOW | {tool} | {category} | {reason from research doc} |
| SOON | {tool} | {category} | {reason} |
| LATER | {tool} | {category} | {reason} |
| SKIP | {tool} | {category} | {reason} |

### Ready to set up?
Tell me which tools you'd like to configure and I'll add the necessary
plugins, dependencies, and configuration files.
```

## Research Document Paths

These files are the source of truth. Read them at runtime — do not cache or embed their content:

- **Quality Tools**: `docs/research/jvm-quality-tools-evaluation.md`
  - Covers: Error Prone, SpotBugs, Detekt, ktlint, SonarQube, JaCoCo, PIT, ArchUnit, Testcontainers, Spring Cloud Contract, Pact, Gradle Cache, GitHub Actions, OpenRewrite, Renovate, JMH, OWASP DC, Trivy, Snyk
- **Testing Ecosystem**: `docs/research/kotlin-spring-boot-testing-ecosystem.md`
  - Covers: Assertions (AssertJ, Kotest, Strikt), Test Data (Instancio, kotlin-faker, Fixture Monkey), Coverage (Kover), Property Testing (jqwik), API Testing (MockMvcTester, RestTestClient), Contract Testing (Pact), DB Testing (@DataJpaTest, Testcontainers reuse), Mutation Testing (PIT), Spring Modulith Testing

## References

- **Workflow**: See [WORKFLOW.md](WORKFLOW.md) for detailed phase descriptions and classification logic
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for realistic audit scenarios
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for scanner issues
- **Scanner Script**: See [scripts/scan_tooling.py](scripts/scan_tooling.py) for detection patterns
