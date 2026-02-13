# Java/Kotlin Quality Tools Evaluation

## A Practitioner's Guide for Modern JVM Projects

> **Last updated**: February 2026 | **Java baseline**: 21+ | **Build tools**: Gradle 9.x / Maven 3.9+
>
> This guide evaluates 18 tools across four categories for Java and Kotlin teams building
> production systems with Spring Boot. Every tool listed is free or has a meaningful free tier.
> Configurations are shown in both Gradle (Kotlin DSL) and Maven where applicable.

---

## Executive Summary

### Tool Landscape at a Glance

| Tool | Category | Version | Java 21 | Kotlin | Spring Boot 3/4 | Gradle | Maven | Cost | Stars |
|------|----------|---------|---------|--------|-----------------|--------|-------|------|-------|
| **Error Prone** | Static Analysis | 2.47.0 | Required | No | Yes | Yes | Yes | Free | 7.1k |
| **SpotBugs** | Static Analysis | 4.9.8 | Yes | Via bytecode | Yes | Yes | Yes | Free | 3.8k |
| **Detekt** | Static Analysis | 1.23.8 / 2.0.0-alpha.2 | N/A | Native | Yes | Yes | Yes | Free | 6.8k |
| **ktlint** | Static Analysis | 1.8.0 | N/A | Native | Yes | Yes | Yes | Free | 5.9k |
| **SonarQube** | Static Analysis | 26.1.0 | Yes | Yes | Yes | Yes | Yes | Freemium | N/A |
| **JaCoCo** | Testing & Quality | 0.8.14 | Yes | Yes | Yes | Yes | Yes | Free | 4.5k |
| **PIT** | Testing & Quality | 1.22.0 | Yes | Yes (plugin) | Yes | Yes | Yes | Freemium | 1.8k |
| **ArchUnit** | Testing & Quality | 1.4.1 | Yes | Yes | Yes | Yes | Yes | Free | 3.6k |
| **Testcontainers** | Testing & Quality | 2.0.3 | Yes | Yes | Native | Yes | Yes | Free | 8.6k |
| **Spring Cloud Contract** | Testing & Quality | 4.1.x | Yes | Yes | Native | Yes | Yes | Free | N/A |
| **Pact** | Testing & Quality | 4.6.x | Yes | Yes | Yes | Yes | Yes | Freemium | N/A |
| **Gradle Cache** | Build & CI/CD | 9.3.1 | Yes | Yes | Yes | Native | N/A | Free | N/A |
| **GitHub Actions** | Build & CI/CD | N/A | Yes | Yes | Yes | Yes | Yes | Freemium | N/A |
| **OpenRewrite** | Build & CI/CD | 8.71.0 | Yes | Partial | Yes | Yes | Yes | Free | N/A |
| **Renovate** | Build & CI/CD | 43.x | N/A | N/A | N/A | Yes | Yes | Free | 20.7k |
| **JMH** | Performance & Security | 1.37 | Yes | N/A | Yes | Yes | Yes | Free | 2.6k |
| **OWASP DC** | Performance & Security | 12.2.0 | Yes | N/A | Yes | Yes | Yes | Free | 7.4k |
| **Trivy** | Performance & Security | 0.69.x | Yes | N/A | Yes | Via CLI | Via CLI | Free | 31.9k |

### Recommended Starting Sets

#### Lean Java Team (< 5 developers, Java-only)

| Layer | Tool | Why |
|-------|------|-----|
| Compile-time | Error Prone | Catches bugs during `javac` with auto-fix |
| Post-build | SpotBugs + Find Security Bugs | Bytecode analysis + OWASP security checks |
| Coverage | JaCoCo | The standard, zero alternatives |
| Architecture | ArchUnit | Enforce layered architecture in tests |
| Integration | Testcontainers | Real dependencies, production parity |
| Security | Trivy | Free, comprehensive, fast |
| CI/CD | GitHub Actions + Gradle Cache | Optimal for GitHub-hosted projects |

#### Kotlin-First Spring Boot Team (5-20 developers)

| Layer | Tool | Why |
|-------|------|-----|
| Formatting | ktlint | Zero-config, auto-fix, pre-commit hooks |
| Linting | Detekt | Native Kotlin AST, coroutine/flow awareness |
| Compile-time (Java) | Error Prone | For any Java code in mixed projects |
| Post-build | SpotBugs | Analyzes Kotlin bytecode too |
| Coverage | JaCoCo | Kotlin bytecode filtering built-in |
| Mutation | PIT + pitest-kotlin | Filters Kotlin-generated junk mutations |
| Integration | Testcontainers | Spring Boot `@ServiceConnection` |
| Contracts | Spring Cloud Contract | JVM-only: auto-generated tests + stubs |
| Security | Trivy + OWASP DC | Defense in depth |
| Dependencies | Renovate | Multi-module Gradle, version catalogs |
| Migrations | OpenRewrite | Spring Boot 3 to 4 automated |
| Quality Platform | SonarQube Community | Centralized dashboards, quality gates |

#### Enterprise Java/Kotlin (20+ developers, polyglot services)

| Layer | Tool | Why |
|-------|------|-----|
| All static analysis | Error Prone + Detekt + SpotBugs + ktlint | Full coverage across languages |
| Quality platform | SonarQube Developer+ | Branch analysis, PR decoration |
| Coverage | JaCoCo | Integrated with SonarQube |
| Mutation | PIT + ArcMutate | Commercial acceleration for large codebases |
| Architecture | ArchUnit + Spring Modulith | Low-level rules + module boundaries |
| Integration | Testcontainers | Singleton pattern for performance |
| Contracts | Pact + PactFlow | Cross-language, can-i-deploy |
| Benchmarking | JMH | Performance regression detection |
| Security | Snyk (paid) + Trivy | Reachability analysis + container scanning |
| Dependencies | Renovate | Advanced auto-merge, stability days |
| Migrations | OpenRewrite + Moderne | Multi-repo at scale |
| CI/CD | GitHub Actions + remote build cache | Configuration cache enabled |

---

## 1. Static Analysis

### 1.1 Error Prone

**What**: Compile-time static analysis tool that augments the Java compiler with 500+ bug pattern checks
**Site**: [errorprone.info](https://errorprone.info/) | **Version**: 2.47.0 (Feb 2025) | **License**: Apache 2.0
**Compat**: Java 21 **Required**, Kotlin No, Spring Boot 3/4 Yes, Gradle Yes, Maven Yes

#### Why It Matters

Error Prone catches bugs during compilation, before code review or CI even runs. It provides auto-fix suggestions for many issues, making it both a detection and remediation tool. Google uses it internally across billions of lines of code.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - Requires JDK 21+ (even for Java 8 targets) |
| Kotlin Support | **N/A** - Java only |
| Spring Boot Integration | **Strong** - Works with debug/reload, all Spring versions |
| Setup Effort | **Low** - Single Gradle plugin + dependency |
| Ongoing Maintenance | **Low** - Minimal config, auto-fix reduces burden |
| Quality Impact | **High** - 500+ checks, compile-time feedback loop |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 7.1k stars, 200+ contributors, Google-backed |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
plugins {
    id("net.ltgt.errorprone") version "4.0.1"
    java
}

dependencies {
    errorprone("com.google.errorprone:error_prone_core:2.47.0")
}

tasks.withType<JavaCompile>().configureEach {
    options.errorprone.disableWarningsInGeneratedCode.set(true)
    options.errorprone.isEnabled.set(true)
}
```

#### Quick Start - Maven

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <source>21</source>
        <target>21</target>
        <compilerArgs>
            <arg>-XDcompilePolicy=simple</arg>
            <arg>-Xplugin:ErrorProne</arg>
        </compilerArgs>
        <annotationProcessorPaths>
            <path>
                <groupId>com.google.errorprone</groupId>
                <artifactId>error_prone_core</artifactId>
                <version>2.47.0</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `disableWarningsInGeneratedCode` | Skip generated code (Lombok, etc.) | `false` |
| `check("NullAway", ERROR)` | Promote specific check to error | Varies |
| `disable("UnusedVariable")` | Suppress noisy checks | All enabled |
| `option("NullAway:AnnotatedPackages", "com.example")` | NullAway configuration | None |

#### Known Limitations

- **Requires JDK 21+** to run, even when targeting Java 8 (`--release 8`)
- Java 23 support still in progress (tracked in issue #4415)
- Cannot analyze Kotlin source code directly
- Adds 10-30% to compile time
- JDK 16+ requires `--add-exports` flags for some checks

#### Alternatives

- SpotBugs: Post-compilation, works on all JVM languages ([Section 1.2](#12-spotbugs))
- SonarQube: Platform-level analysis with broader language support ([Section 1.5](#15-sonarqube))

---

### 1.2 SpotBugs

**What**: Successor to FindBugs; analyzes compiled Java bytecode to detect 400+ bug patterns
**Site**: [spotbugs.readthedocs.io](https://spotbugs.readthedocs.io/) | **Version**: 4.9.8 (Oct 2025) | **License**: LGPL 2.1
**Compat**: Java 21 Yes, Kotlin Via bytecode, Spring Boot 3/4 Yes, Gradle Yes, Maven Yes

#### Why It Matters

SpotBugs works on compiled `.class` files, meaning it can analyze any JVM language including Kotlin, Groovy, and Scala without language-specific support. The Find Security Bugs plugin adds 144 security vulnerability patterns covering the OWASP Top 10.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All versions including 21 and 23 |
| Kotlin Support | **Strong** - Analyzes compiled Kotlin bytecode natively |
| Spring Boot Integration | **Strong** - Detects Spring-specific issues with security plugin |
| Setup Effort | **Low** - Single Gradle plugin |
| Ongoing Maintenance | **Medium** - Suppress false positives via exclude filters |
| Quality Impact | **High** - 400+ bug patterns + 144 security patterns |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 3.8k stars, 200+ contributors, FindBugs successor |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
plugins {
    id("com.github.spotbugs") version "6.4.8"
    java
}

spotbugs {
    toolVersion.set("4.9.8")
    effort.set(Effort.MAX)
    reportLevel.set(Confidence.LOW)
}

dependencies {
    spotbugsPlugins("com.h3xstream.findsecbugs:findsecbugs-plugin:1.14.0")
}
```

#### Quick Start - Maven

```xml
<plugin>
    <groupId>com.github.spotbugs</groupId>
    <artifactId>spotbugs-maven-plugin</artifactId>
    <version>4.7.3.0</version>
    <configuration>
        <effort>Max</effort>
        <threshold>Low</threshold>
        <failOnError>true</failOnError>
        <plugins>
            <plugin>
                <groupId>com.h3xstream.findsecbugs</groupId>
                <artifactId>findsecbugs-plugin</artifactId>
                <version>1.14.0</version>
            </plugin>
        </plugins>
    </configuration>
</plugin>
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `effort` | Analysis depth (MIN / DEFAULT / MAX) | `DEFAULT` |
| `reportLevel` | Minimum confidence (LOW / MEDIUM / HIGH) | `MEDIUM` |
| `excludeFilter` | XML file listing exclusions | None |
| `onlyAnalyze` | Restrict to specific packages | All |

#### Known Limitations

- No auto-fix capability (detection only)
- Feedback arrives after compilation, not during
- Some false positives with modern Java patterns (streams, lambdas)
- Version 5.0 planned but not yet released

#### Error Prone vs SpotBugs

| Aspect | Error Prone | SpotBugs |
|--------|-------------|----------|
| Runs at | Compile-time (javac) | Post-compilation (.class) |
| Auto-fix | Yes | No |
| JVM languages | Java only | All (Kotlin, Groovy, Scala) |
| Security plugin | No | Yes (Find Security Bugs) |
| Requires source | Yes | No (bytecode only) |

**Recommendation**: Use both. Error Prone for immediate compile-time feedback, SpotBugs for comprehensive post-build verification and security scanning.

---

### 1.3 Detekt

**What**: Native Kotlin static analysis tool parsing Kotlin AST directly; understands coroutines, flows, and sealed interfaces
**Site**: [detekt.dev](https://detekt.dev/) | **Version**: 1.23.8 stable / 2.0.0-alpha.2 (Jan 2026) | **License**: Apache 2.0
**Compat**: Java N/A (Kotlin-only), Kotlin Native, Spring Boot 3/4 Yes, Gradle Yes, Maven Yes

#### Why It Matters

Detekt is the only static analysis tool that natively understands Kotlin constructs like coroutines, flows, suspend functions, and sealed interfaces. Java-based analyzers like SpotBugs can process Kotlin bytecode but miss Kotlin-specific anti-patterns and idiom violations.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **N/A** - Kotlin only |
| Kotlin Support | **Strong** - Native AST analysis, 300+ rules |
| Spring Boot Integration | **Strong** - Detects anti-patterns in Spring components |
| Setup Effort | **Low** - Single plugin, generate default config |
| Ongoing Maintenance | **Medium** - Baseline management, rule tuning |
| Quality Impact | **High** - Catches coroutine misuse, complexity, code smells |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 6.8k stars, 300+ contributors |

#### Quick Start - Gradle

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

#### Quick Start - Maven

```xml
<plugin>
    <groupId>com.github.ozsie</groupId>
    <artifactId>detekt-maven-plugin</artifactId>
    <version>1.23.8</version>
    <configuration>
        <config>config/detekt.yml</config>
        <buildUponDefaultConfig>true</buildUponDefaultConfig>
    </configuration>
</plugin>
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `buildUponDefaultConfig` | Extend defaults rather than replace | `false` |
| `baseline` | XML file with known issues to suppress | None |
| `allRules` | Enable all available rules | `false` |
| `detekt-formatting` plugin | Integrates ktlint rules into Detekt | Not included |

#### Known Limitations

- 2.0.0 is still alpha (stable at 1.23.8)
- Cannot analyze Java code
- Slower than ktlint (deep analysis vs syntax-level)
- Custom rule authoring requires Detekt API knowledge

#### Alternatives

- ktlint: Faster, formatting-focused, zero-config ([Section 1.4](#14-ktlint))
- SonarQube: Platform-level Kotlin analysis ([Section 1.5](#15-sonarqube))

---

### 1.4 ktlint

**What**: Kotlin linter and code formatter with built-in auto-fix; enforces official Kotlin coding conventions
**Site**: [github.com/pinterest/ktlint](https://github.com/pinterest/ktlint) | **Version**: 1.8.0 (2025) | **License**: MIT
**Compat**: Java N/A, Kotlin Native, Spring Boot 3/4 Yes, Gradle Yes, Maven Yes

#### Why It Matters

ktlint provides deterministic, fast code formatting for Kotlin with zero configuration required. It auto-fixes most style violations and integrates with pre-commit hooks to prevent style issues from reaching code review.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **N/A** - Kotlin only |
| Kotlin Support | **Strong** - Native, all modern versions |
| Spring Boot Integration | **Adequate** - Formats Spring Kotlin code correctly |
| Setup Effort | **Low** - Zero configuration, convention over config |
| Ongoing Maintenance | **Low** - Minimal config, auto-fix handles most issues |
| Quality Impact | **Medium** - Style consistency, not bug detection |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 5.9k stars, Pinterest-maintained |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
plugins {
    id("org.jlleitschuh.gradle.ktlint") version "12.1.0"
}

ktlint {
    version.set("1.8.0")
}
```

#### Quick Start - Maven

```xml
<plugin>
    <groupId>com.github.gantsign.maven</groupId>
    <artifactId>ktlint-maven-plugin</artifactId>
    <version>3.2.0</version>
</plugin>
```

#### Detekt vs ktlint

| Aspect | Detekt | ktlint |
|--------|--------|--------|
| Purpose | Code quality / smells | Code formatting / style |
| Auto-fix | Limited | Comprehensive |
| Speed | Slower (deep analysis) | Fast (syntax-level) |
| Configuration | Highly configurable | Minimal |

**Recommendation**: Use both. ktlint for formatting, Detekt for linting. Many teams use the `detekt-formatting` plugin to embed ktlint rules inside Detekt.

---

### 1.5 SonarQube

**What**: Comprehensive code quality and security platform supporting 35+ languages with centralized dashboards and quality gates
**Site**: [sonarsource.com](https://www.sonarsource.com/) | **Version**: 26.1.0 (Jan 2026) | **License**: LGPL 3.0 (Community)
**Compat**: Java 21 Yes, Kotlin Yes, Spring Boot 3/4 Yes, Gradle Yes, Maven Yes

#### Why It Matters

SonarQube provides historical code quality tracking, quality gates for CI/CD, and unified dashboards across all languages in a project. The Community Build is free and covers 19 languages. SonarLint provides real-time IDE feedback that syncs with server rules.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All versions |
| Kotlin Support | **Strong** - Native analysis |
| Spring Boot Integration | **Strong** - Quality gates, JaCoCo coverage integration |
| Setup Effort | **Medium** - Requires server instance or cloud account |
| Ongoing Maintenance | **Medium** - Quality gate tuning, profile management |
| Quality Impact | **High** - Historical tracking, technical debt management |
| Cost | **Free** (Community) / Paid (Developer+) |
| Ecosystem Maturity | **Strong** - Industry standard for enterprise code quality |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
plugins {
    id("org.sonarqube") version "5.0.0.4638"
    jacoco
}

sonarqube {
    properties {
        property("sonar.projectKey", "my-project")
        property("sonar.host.url", "https://sonarcloud.io")
        property("sonar.token", System.getenv("SONAR_TOKEN"))
    }
}
```

#### Quick Start - Maven

```xml
<properties>
    <sonar.projectKey>my-project</sonar.projectKey>
    <sonar.host.url>https://sonarcloud.io</sonar.host.url>
</properties>

<plugin>
    <groupId>org.sonarsource.scanner.maven</groupId>
    <artifactId>sonar-maven-plugin</artifactId>
    <version>4.0.0.4121</version>
</plugin>
```

Run: `mvn clean verify sonar:sonar -Dsonar.token=$SONAR_TOKEN`

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `sonar.qualitygate.wait` | Block CI until gate passes | `false` |
| `sonar.coverage.jacoco.xmlReportPaths` | JaCoCo report location | Auto-detected |
| `sonar.exclusions` | Files to exclude from analysis | None |
| `sonar.cpd.minimumTokens` | Duplication detection threshold | `100` |

#### Editions Comparison

| Feature | Community (Free) | Developer (Paid) |
|---------|-----------------|------------------|
| Branch analysis | Main only | All branches |
| PR decoration | No | Yes |
| Languages | 19 | 26 |
| Security reports | Basic | Advanced (OWASP) |

#### Known Limitations

- Community Build: main branch analysis only (no PR decoration)
- Requires server infrastructure (self-hosted) or SonarCloud account
- SonarScanner Gradle plugin had configuration cache issues (resolved in recent versions)
- Quality profiles require initial tuning to avoid noise

### Static Analysis Decision Guide

```
Is your project Java-only?
├── Yes → Error Prone + SpotBugs (+ SonarQube for dashboards)
├── Kotlin-only → Detekt + ktlint (+ SonarQube for dashboards)
└── Java + Kotlin → Error Prone (Java) + Detekt + ktlint (Kotlin) + SpotBugs (both)

Need security scanning?
├── Yes → Add Find Security Bugs plugin to SpotBugs
└── No → SpotBugs alone is sufficient

Need centralized quality tracking?
├── Yes → Add SonarQube + SonarLint IDE plugin
└── No → Tool-level reports are sufficient
```

---

## 2. Testing & Quality

### 2.1 JaCoCo

**What**: Java code coverage library using bytecode instrumentation via Java agent
**Site**: [jacoco.org](https://www.jacoco.org/) | **Version**: 0.8.14 (Oct 2025) | **License**: EPL 2.0
**Compat**: Java 21 Yes (up to Java 25), Kotlin Yes (excellent filtering), Spring Boot 3/4 Yes, Gradle Yes, Maven Yes

#### Why It Matters

JaCoCo is the uncontested standard for JVM code coverage. It provides line, branch, and instruction coverage metrics with minimal performance overhead (~5-10%). No serious alternatives exist in 2026.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - Java 25 official, Java 26 experimental |
| Kotlin Support | **Strong** - Advanced filtering for coroutines, inline functions |
| Spring Boot Integration | **Strong** - Works with all Spring Boot versions |
| Setup Effort | **Low** - Built-in Gradle plugin |
| Ongoing Maintenance | **Low** - Minimal configuration needed |
| Quality Impact | **High** - Essential coverage metrics |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 4.5k stars, de facto standard |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
plugins {
    jacoco
}

jacoco {
    toolVersion = "0.8.14"
}

tasks.test {
    finalizedBy(tasks.jacocoTestReport)
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)
    reports {
        xml.required.set(true)  // Required for SonarQube
        html.required.set(true)
    }
}
```

#### Quick Start - Maven

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.14</version>
    <executions>
        <execution>
            <goals><goal>prepare-agent</goal></goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals><goal>report</goal></goals>
        </execution>
    </executions>
</plugin>
```

#### Known Limitations

- Line coverage can be misleading without branch coverage
- Kotlin coroutine bytecode inflates uncovered branches (mitigated in recent versions)
- Cannot measure coverage of native methods

---

### 2.2 PIT Mutation Testing

**What**: Mutation testing tool that verifies test quality by introducing faults into code and checking if tests detect them
**Site**: [pitest.org](https://pitest.org/) | **Version**: 1.22.0 | **License**: Apache 2.0 (open source) / Commercial (ArcMutate)
**Compat**: Java 21 Yes, Kotlin Yes (with plugin), Spring Boot 3/4 Yes, Gradle Yes, Maven Yes

#### Why It Matters

Code coverage tells you which lines execute during tests; mutation testing tells you if those tests actually verify behavior. PIT modifies your code (mutations) and checks if tests fail. Surviving mutations reveal weak test assertions.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All modern versions |
| Kotlin Support | **Adequate** - Requires `pitest-kotlin` plugin to filter junk mutations |
| Spring Boot Integration | **Adequate** - Works but context startup amplifies runtime |
| Setup Effort | **Medium** - Requires target class/test configuration |
| Ongoing Maintenance | **Medium** - Incremental runs essential for large projects |
| Quality Impact | **High** - Exposes weak test assertions that coverage misses |
| Cost | **Free** (PIT) / Paid (ArcMutate for 50-80% faster runs) |
| Ecosystem Maturity | **Strong** - 1.8k stars, industry standard for JVM mutation testing |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
plugins {
    id("info.solidsoft.pitest") version "1.19.0-rc.3"
}

pitest {
    junit5PluginVersion.set("1.2.1")
    targetClasses.set(listOf("com.example.myapp.*"))
    targetTests.set(listOf("com.example.myapp.*"))
    threads.set(4)
    outputFormats.set(listOf("HTML", "XML"))
    timestampedReports.set(false)

    // For Kotlin projects - REQUIRED to avoid junk mutations
    pitestVersion.set("1.22.0")
    plugins.set(listOf("pitest-kotlin:1.2.0"))
}
```

#### Quick Start - Maven

```xml
<plugin>
    <groupId>org.pitest</groupId>
    <artifactId>pitest-maven</artifactId>
    <version>1.22.0</version>
    <dependencies>
        <dependency>
            <groupId>org.pitest</groupId>
            <artifactId>pitest-junit5-plugin</artifactId>
            <version>1.2.1</version>
        </dependency>
    </dependencies>
    <configuration>
        <targetClasses>
            <param>com.example.myapp.*</param>
        </targetClasses>
        <threads>4</threads>
    </configuration>
</plugin>
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `threads` | Parallel mutation execution | `1` |
| `mutationThreshold` | Minimum mutation score to pass | `0` |
| `timestampedReports` | Unique report dirs per run | `true` |
| `historyInputLocation` / `historyOutputLocation` | Incremental testing | None |

#### Build Time Impact

- **Overhead**: 3x to 30x test execution time
- **Optimization**: Use incremental mode (Git integration), parallel threads, and scoped execution
- **Kotlin**: MUST use `pitest-kotlin` plugin to filter junk mutations from compiler artifacts

#### Known Limitations

- Full mutation runs on large Spring Boot apps can take hours
- Spring context startup overhead amplified per mutation
- Without `pitest-kotlin`, Kotlin projects generate many false surviving mutations
- ArcMutate (commercial) reduces runtime by 50-80% for large codebases

---

### 2.3 ArchUnit

**What**: Library for checking architecture rules as unit tests; verifies package dependencies, layer boundaries, and naming conventions
**Site**: [archunit.org](https://www.archunit.org/) | **Version**: 1.4.1 (Mar 2025) | **License**: Apache 2.0
**Compat**: Java 21 Yes, Kotlin Yes, Spring Boot 3/4 Yes, Gradle Yes, Maven Yes

#### Why It Matters

ArchUnit encodes architecture decisions as executable tests. When someone violates a layer boundary or naming convention, the build fails instead of relying on code review to catch it. This is essential for maintaining architecture over time.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All versions |
| Kotlin Support | **Strong** - Works seamlessly with Kotlin bytecode |
| Spring Boot Integration | **Strong** - Validates Spring annotations, layer rules |
| Setup Effort | **Low** - Single test dependency |
| Ongoing Maintenance | **Low** - Rules rarely change after initial setup |
| Quality Impact | **High** - Prevents architecture drift |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 3.6k stars, TNG Technology Consulting |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("com.tngtech.archunit:archunit-junit5:1.4.1")
}
```

#### Quick Start - Maven

```xml
<dependency>
    <groupId>com.tngtech.archunit</groupId>
    <artifactId>archunit-junit5</artifactId>
    <version>1.4.1</version>
    <scope>test</scope>
</dependency>
```

#### Example Test (Kotlin)

```kotlin
@AnalyzeClasses(packages = ["com.example.myapp"])
class ArchitectureTest {

    @ArchTest
    val layerDependencies = layeredArchitecture()
        .consideringAllDependencies()
        .layer("Controller").definedBy("..controller..")
        .layer("Service").definedBy("..service..")
        .layer("Repository").definedBy("..repository..")
        .whereLayer("Controller").mayNotBeAccessedByAnyLayer()
        .whereLayer("Service").mayOnlyBeAccessedByLayers("Controller")
        .whereLayer("Repository").mayOnlyBeAccessedByLayers("Service")
}
```

#### ArchUnit vs Spring Modulith

| Aspect | ArchUnit | Spring Modulith |
|--------|----------|-----------------|
| Scope | Generic (any Java/Kotlin) | Spring Boot only |
| Granularity | Class/package level rules | Module boundary enforcement |
| Runtime features | Test-time only | Event verification, module API validation |
| Framework dependency | None | Spring Boot required |

**Recommendation**: Use both. ArchUnit for fine-grained architecture rules, Spring Modulith for high-level module boundaries and event-driven architecture.

---

### 2.4 Testcontainers

**What**: Library that provides lightweight, throwaway Docker containers for integration testing
**Site**: [testcontainers.org](https://java.testcontainers.org/) | **Version**: 2.0.3 | **License**: MIT
**Compat**: Java 21 Yes, Kotlin Yes, Spring Boot 3.1+ Native, Gradle Yes, Maven Yes

#### Why It Matters

Testcontainers replaced embedded databases and mock services with real infrastructure running in Docker containers. Spring Boot 3.1+ provides native `@ServiceConnection` integration that auto-configures beans from container properties. It is THE integration testing standard in 2026.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All versions |
| Kotlin Support | **Strong** - Kotlin-friendly APIs and DSL |
| Spring Boot Integration | **Strong** - Native support since 3.1, `@ServiceConnection` |
| Setup Effort | **Low** - Requires Docker, single dependency |
| Ongoing Maintenance | **Low** - Container images auto-pull |
| Quality Impact | **High** - Production parity, real dependencies |
| Cost | **Free** (open source) / Testcontainers Desktop (free tier available) |
| Ecosystem Maturity | **Strong** - 8.6k stars, 100+ modules, no serious competitors |

#### Quick Start - Gradle (Spring Boot 3.4+)

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("org.springframework.boot:spring-boot-testcontainers")
    testImplementation("org.testcontainers:junit-jupiter")
    testImplementation("org.testcontainers:postgresql")
}
```

#### Quick Start - Maven (Spring Boot 3.4+)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <scope>test</scope>
</dependency>
```

#### Example Test (Kotlin)

```kotlin
@SpringBootTest
@Testcontainers
class OrderRepositoryTest {

    @Container
    @ServiceConnection
    val postgres = PostgreSQLContainer("postgres:16-alpine")

    @Test
    fun `should persist and retrieve order`() {
        // Spring Boot auto-configures DataSource from @ServiceConnection
    }
}
```

#### Key Configuration Options

| Setting | Purpose | Impact |
|---------|---------|--------|
| Singleton pattern | Share container across test classes | 70% faster |
| Reusable containers | Keep containers running between runs | Even faster |
| Alpine images | Smaller container images | Faster startup |
| `@DynamicPropertySource` | Manual property injection (pre-3.1) | Legacy approach |

#### Known Limitations

- Requires Docker runtime on CI/CD agents
- Container startup adds 5-30 seconds per service
- Resource-intensive for many concurrent containers
- Not suitable for unit tests (too slow)

---

### 2.5 Contract Testing: Spring Cloud Contract vs Pact

**What**: Tools for verifying API contracts between service consumers and providers
**Versions**: Spring Cloud Contract 4.1.x | Pact JVM 4.6.x | **License**: Apache 2.0 / MIT

#### When to Choose Which

| Factor | Spring Cloud Contract | Pact |
|--------|----------------------|------|
| **Best for** | JVM-only teams | Polyglot teams |
| **Contract approach** | Provider-driven or CDC | Consumer-driven (CDC) |
| **Auto-generated tests** | Yes | No |
| **Broker** | Uses artifact repos | Pact Broker (centralized) |
| **Can-I-Deploy** | No | Yes |
| **Messaging support** | Excellent (Kafka, RabbitMQ) | Good |
| **Learning curve** | Medium (Spring knowledge helps) | Steeper (CDC mindset) |
| **Commercial option** | None | PactFlow (SaaS) |

#### Quick Start - Spring Cloud Contract (Gradle)

```kotlin
plugins {
    id("org.springframework.cloud.contract") version "4.1.0"
}

contracts {
    baseClassForTests.set("com.example.BaseContractTest")
    contractsDslDir.set(file("src/test/resources/contracts"))
}
```

#### Quick Start - Pact (Gradle)

```kotlin
dependencies {
    testImplementation("au.com.dius.pact.consumer:junit5:4.6.7")
    testImplementation("au.com.dius.pact.provider:junit5:4.6.7")
}
```

#### Recommendation

- **JVM-only teams** with Spring Boot: Spring Cloud Contract (simpler, native integration)
- **Polyglot teams** or large organizations: Pact (cross-language, can-i-deploy, Pact Broker)
- **Hybrid**: Use Spring Cloud Contract for JVM-to-JVM, Pact for JVM-to-non-JVM

### Testing & Quality Decision Guide

```
What do you need?
├── Code coverage → JaCoCo (the only real option)
├── Test quality verification → PIT (add pitest-kotlin for Kotlin)
├── Architecture enforcement → ArchUnit (+ Spring Modulith for module boundaries)
├── Integration testing → Testcontainers (with @ServiceConnection for Spring Boot)
└── Contract testing
    ├── JVM-only → Spring Cloud Contract
    └── Polyglot → Pact
```

---

## 3. Build & CI/CD

### 3.1 Gradle Build Cache & Configuration Cache

**What**: Gradle's build acceleration features that cache task outputs and configuration phase results
**Site**: [gradle.org](https://gradle.org/) | **Version**: 9.3.1 (Jan 2026) | **License**: Apache 2.0
**Compat**: Java 21 Yes, Kotlin Yes, Spring Boot 3/4 Yes, Gradle Native, Maven N/A

#### Why It Matters

Gradle 9.0 made configuration cache the **preferred execution mode**. Combined with build cache, it can reduce CI build times by 90-97% on cache hits. For multi-module Spring Boot projects, this translates from minutes to seconds.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All versions |
| Kotlin Support | **Strong** - Kotlin DSL fully supported |
| Spring Boot Integration | **Strong** - Spring Boot Gradle plugin supports config cache |
| Setup Effort | **Low** - Properties file change |
| Ongoing Maintenance | **Low** - Mostly automatic |
| Quality Impact | **Medium** - Developer productivity, not code quality |
| Cost | **Free** (local) / Paid (Gradle Enterprise remote cache) |
| Ecosystem Maturity | **Strong** - ~85% plugin compatibility in Gradle 9 |

#### Quick Start - Gradle

```properties
# gradle.properties
org.gradle.configuration-cache=true
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=1g
```

#### Performance Impact

| Scenario | Without Cache | With Cache |
|----------|--------------|------------|
| Configuration phase | 5-30 seconds | Cached (instant) |
| Full build (cache miss) | 5 minutes | 5 minutes |
| Incremental build (cache hit) | 5 minutes | 10-20 seconds |
| Multi-module CI pipeline | 15 minutes | 1-2 minutes |

#### Known Limitations

- ~15-20% of plugins still incompatible with configuration cache
- Remote build cache requires infrastructure (Gradle Enterprise or HTTP server)
- CI requires encryption key for configuration cache (`GRADLE_ENCRYPTION_KEY` secret)
- Cache debugging can be complex (use Build Scans)

---

### 3.2 GitHub Actions

**What**: CI/CD platform integrated with GitHub for automated build, test, and deployment workflows
**Site**: [github.com/features/actions](https://github.com/features/actions) | **License**: Freemium

#### Why It Matters

GitHub Actions is the natural CI/CD choice for GitHub-hosted projects. Public repositories get unlimited free minutes. The `gradle/actions/setup-gradle@v5` action provides optimized caching, dependency graph generation, and configuration cache support.

#### Free Tier Limits (2026)

| Account Type | Free Minutes/Month | Cache Storage |
|-------------|-------------------|---------------|
| Public repos | Unlimited | 10 GB |
| Private - Free | 2,000 min | 10 GB |
| Private - Pro | 3,000 min | 10 GB |
| Private - Team | 3,000 min | 10 GB |
| Private - Enterprise | 50,000 min | 10 GB |

**2026 Update**: Hosted runner pricing reduced 20-39% effective January 2026. Self-hosted runner fee postponed indefinitely.

#### Quick Start - GitHub Actions (Gradle)

```yaml
name: Build

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '21'

      - uses: gradle/actions/setup-gradle@v5
        with:
          cache-encryption-key: ${{ secrets.GRADLE_ENCRYPTION_KEY }}

      - run: ./gradlew build --configuration-cache --build-cache
```

---

### 3.3 OpenRewrite

**What**: Automated source code refactoring and migration framework with 5,095+ recipes
**Site**: [docs.openrewrite.org](https://docs.openrewrite.org/) | **Version**: 8.71.0 (Jan 2026) | **License**: Apache 2.0
**Compat**: Java 21 Yes, Kotlin Partial, Spring Boot 3/4 Yes, Gradle Yes, Maven Yes

#### Why It Matters

OpenRewrite automates large-scale code migrations that would take teams weeks or months. The Spring Boot migration recipes handle dependency updates, deprecated API replacements, property name changes, and annotation migrations. The `javax.*` to `jakarta.*` migration alone saved teams thousands of hours.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All versions |
| Kotlin Support | **Adequate** - Some recipes work, Java-focused |
| Spring Boot Integration | **Strong** - 800+ Spring-specific recipes |
| Setup Effort | **Low** - Add plugin + activate recipe |
| Ongoing Maintenance | **Low** - Run on-demand for migrations |
| Quality Impact | **High** - Eliminates manual migration errors |
| Cost | **Free** (open source) / Paid (Moderne platform for multi-repo) |
| Ecosystem Maturity | **Strong** - 5,095 recipes, rapid growth |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
plugins {
    id("org.openrewrite.rewrite") version "latest.release"
}

rewrite {
    activeRecipe("org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_5")
}

dependencies {
    rewrite("org.openrewrite.recipe:rewrite-spring:6.23.1")
}
```

Run: `./gradlew rewriteDryRun` (preview) then `./gradlew rewriteRun` (apply)

#### Quick Start - Maven

```xml
<plugin>
    <groupId>org.openrewrite.maven</groupId>
    <artifactId>rewrite-maven-plugin</artifactId>
    <version>5.21.0</version>
    <configuration>
        <activeRecipes>
            <recipe>org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_5</recipe>
        </activeRecipes>
    </configuration>
    <dependencies>
        <dependency>
            <groupId>org.openrewrite.recipe</groupId>
            <artifactId>rewrite-spring</artifactId>
            <version>6.23.1</version>
        </dependency>
    </dependencies>
</plugin>
```

Run: `mvn rewrite:dryRun` (preview) then `mvn rewrite:run` (apply)

#### Key Migration Recipes

| Recipe | Purpose |
|--------|---------|
| `UpgradeSpringBoot_3_5` | Migrate to Spring Boot 3.5 |
| `UpgradeSpringBoot_4_0` | Migrate to Spring Boot 4.0 |
| `UpgradeSpringSecurity_6_5` | Spring Security 6.5 migration |
| `SpringCloudProperties_2025` | Spring Cloud 2025 property updates |

#### Known Limitations

- Not all migrations are fully automated (some require manual intervention)
- Gradle plugin slightly less mature than Maven plugin
- Recipe quality varies (community contributions)
- Large codebases (5,000+ files) can take 10-30 minutes

---

### 3.4 Dependency Automation: Renovate vs Dependabot

**What**: Automated dependency update tools that create pull requests when new versions are available

#### Head-to-Head Comparison

| Feature | Dependabot | Renovate |
|---------|-----------|----------|
| **Platform** | GitHub only | GitHub, GitLab, Bitbucket, Azure DevOps |
| **Package managers** | 13 | 90+ |
| **Gradle version catalogs** | No | Yes |
| **Dependency dashboard** | No | Yes |
| **Auto-merge** | Limited | Advanced (stability days, status checks) |
| **Multi-module Gradle** | Basic | Excellent (auto-grouping) |
| **Setup** | Zero-config | Requires `renovate.json` |
| **GitHub Stars** | N/A (built-in) | 20.7k |

#### Quick Start - Renovate

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "packageRules": [
    {
      "groupName": "Spring Boot",
      "matchPackagePrefixes": ["org.springframework.boot"],
      "automerge": true,
      "minimumReleaseAge": "3 days"
    },
    {
      "matchUpdateTypes": ["patch"],
      "automerge": true
    }
  ]
}
```

#### Quick Start - Dependabot

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      spring:
        patterns: ["org.springframework*"]
```

#### Recommendation

- **Simple single-module projects on GitHub**: Dependabot (zero config)
- **Everything else** (multi-module, version catalogs, advanced auto-merge): **Renovate**

### Build & CI/CD Decision Guide

```
Build acceleration:
└── Gradle → Enable configuration cache + build cache in gradle.properties

CI/CD platform:
├── GitHub repos → GitHub Actions + gradle/actions/setup-gradle@v5
└── GitLab/other → Equivalent CI with Gradle cache

Framework migrations:
└── OpenRewrite (Spring Boot 2→3→4, javax→jakarta, etc.)

Dependency updates:
├── Simple project, GitHub-only → Dependabot
└── Multi-module Gradle, need auto-merge → Renovate
```

---

## 4. Performance & Security

### 4.1 JMH

**What**: Industry-standard Java microbenchmark harness developed by the OpenJDK team
**Site**: [openjdk.org/projects/code-tools/jmh](https://openjdk.org/projects/code-tools/jmh/) | **Version**: 1.37 (Jan 2026) | **License**: GPL 2.0 (with Classpath Exception)
**Compat**: Java 21 Yes, Kotlin N/A (Java benchmarks), Spring Boot Yes, Gradle Yes, Maven Yes

#### Why It Matters

JMH handles the fundamental challenges of accurate JVM performance measurement: JIT compilation warmup, dead code elimination, garbage collection interference, and false sharing. Without JMH, microbenchmarks are unreliable.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All versions including 21 and 23 |
| Kotlin Support | **Adequate** - Java annotation processor, works in Kotlin projects |
| Spring Boot Integration | **Adequate** - Manual context bootstrap required |
| Setup Effort | **Low** - Single Gradle plugin |
| Ongoing Maintenance | **Low** - Run on-demand |
| Quality Impact | **Medium** - Performance regression detection |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 2.6k stars, OpenJDK team, no alternatives |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
plugins {
    id("me.champeau.jmh") version "0.7.3"
}

jmh {
    includes.set(listOf(".*Benchmark.*"))
    iterations.set(10)
    warmupIterations.set(5)
    fork.set(2)
}
```

#### Quick Start - Maven

```xml
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-generator-annprocess</artifactId>
    <version>1.37</version>
    <scope>provided</scope>
</dependency>
```

#### Example Benchmark (Java)

```java
@State(Scope.Benchmark)
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 10, time = 1)
@Fork(2)
public class CollectionBenchmark {

    @Param({"10", "100", "1000"})
    private int size;

    @Benchmark
    public void arrayList(Blackhole bh) {
        List<Integer> list = new ArrayList<>();
        for (int i = 0; i < size; i++) list.add(i);
        bh.consume(list);
    }

    @Benchmark
    public void linkedList(Blackhole bh) {
        List<Integer> list = new LinkedList<>();
        for (int i = 0; i < size; i++) list.add(i);
        bh.consume(list);
    }
}
```

#### Known Limitations

- Results vary across JVM versions and hardware
- Spring Boot context bootstrap adds significant overhead
- Not a substitute for profiling (JMH measures, profilers diagnose)

---

### 4.2 OWASP Dependency-Check

**What**: Free SCA tool that identifies known vulnerabilities in project dependencies using the NVD
**Site**: [owasp.org/www-project-dependency-check](https://owasp.org/www-project-dependency-check/) | **Version**: 12.2.0 (Jan 2026) | **License**: Apache 2.0
**Compat**: Java 21 Yes, Kotlin N/A (dependency scanning), Spring Boot Yes, Gradle Yes, Maven Yes

#### Why It Matters

OWASP Dependency-Check scans all project dependencies against the National Vulnerability Database (NVD) at zero cost. After the 2023-2024 NVD API transition, an **NVD API key is now essential** for reasonable scan times (10 minutes with key vs 4+ hours without).

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All versions |
| Kotlin Support | **N/A** - Scans dependencies, not source |
| Spring Boot Integration | **Strong** - Scans all transitive dependencies |
| Setup Effort | **Medium** - Requires NVD API key registration |
| Ongoing Maintenance | **Medium** - False positive suppression management |
| Quality Impact | **High** - Identifies known CVEs in dependencies |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 7.4k stars, OWASP project |

#### Quick Start - Gradle

```kotlin
// build.gradle.kts
plugins {
    id("org.owasp.dependencycheck") version "12.2.0"
}

dependencyCheck {
    nvd {
        apiKey = System.getenv("NVD_API_KEY")
    }
    failBuildOnCVSS = 7.0f
    suppressionFile = "config/dependency-suppression.xml"
    format = "ALL"
}
```

#### Quick Start - Maven

```xml
<plugin>
    <groupId>org.owasp</groupId>
    <artifactId>dependency-check-maven</artifactId>
    <version>12.2.0</version>
    <configuration>
        <nvdApiKey>${env.NVD_API_KEY}</nvdApiKey>
        <failBuildOnCVSS>7</failBuildOnCVSS>
        <suppressionFile>dependency-suppression.xml</suppressionFile>
    </configuration>
</plugin>
```

#### NVD API Key Setup

1. Visit [nvd.nist.gov/developers/request-an-api-key](https://nvd.nist.gov/developers/request-an-api-key)
2. Request free API key (instant approval)
3. Add as CI secret: `NVD_API_KEY`
4. Rate limit: 50 requests/30 seconds (vs 5 without key)

#### Known Limitations

- **Requires NVD API key** for reasonable performance (4+ hours without)
- ~500MB database download on first run
- No reachability analysis (reports all vulnerabilities even if code path unused)
- False positives with shaded/relocated dependencies

---

### 4.3 Trivy

**What**: Comprehensive security scanner for vulnerabilities, misconfigurations, secrets, licenses, and SBOMs
**Site**: [trivy.dev](https://trivy.dev) | **Version**: 0.69.x (Jan 2026) | **License**: Apache 2.0
**Compat**: Java 21 Yes, Kotlin N/A, Spring Boot Yes, Gradle Via CLI, Maven Via CLI

#### Why It Matters

Trivy has emerged as the best free alternative to commercial tools like Snyk. It scans containers, filesystems, Git repos, and SBOMs for vulnerabilities with lower false positive rates than OWASP DC. It also generates CycloneDX and SPDX SBOMs and detects exposed secrets.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - Scans Maven, Gradle, JAR files |
| Kotlin Support | **N/A** - Scans dependencies, not source |
| Spring Boot Integration | **Strong** - Scans JARs, images, and Spring Boot SBOMs |
| Setup Effort | **Low** - Single binary, 2-minute setup |
| Ongoing Maintenance | **Low** - Auto-updating vulnerability database |
| Quality Impact | **High** - Vulnerabilities, secrets, IaC, licenses |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 31.9k stars, Aqua Security backed |

#### Quick Start - CLI

```bash
# Install
brew install trivy  # macOS
# or: apt-get install trivy  # Debian/Ubuntu

# Scan filesystem
trivy fs --severity HIGH,CRITICAL .

# Scan container image
trivy image mycompany/spring-app:latest

# Generate SBOM
trivy fs --format cyclonedx --output sbom.cdx.json .
```

#### Quick Start - GitHub Actions

```yaml
- name: Run Trivy
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'HIGH,CRITICAL'

- name: Upload to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: 'trivy-results.sarif'
```

#### False Positive Suppression

```
# .trivyignore
CVE-2023-12345
CVE-2024-56789 exp:2026-06-01
```

#### Known Limitations

- No native Gradle/Maven plugin (CLI integration only)
- No reachability analysis (unlike Snyk paid)
- No auto-fix PRs (unlike Snyk/Dependabot)
- No IDE integration

---

### 4.4 Snyk

**What**: Developer-first security platform with SCA, SAST, container scanning, and reachability analysis
**Site**: [snyk.io](https://snyk.io) | **Version**: SaaS (continuous) | **License**: Proprietary (free tier available)
**Compat**: Java 21 Yes, Kotlin N/A, Spring Boot Yes, Gradle Yes, Maven Yes

#### Why It Matters

Snyk's key differentiator is **reachability analysis**: it determines if vulnerable code paths are actually called in your application, reducing alert fatigue by ~60-70%. The free tier was significantly reduced in 2025-2026 and is now primarily useful for open-source projects or solo developers.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Java Compatibility | **Strong** - All versions |
| Kotlin Support | **N/A** - Scans dependencies |
| Spring Boot Integration | **Strong** - Deep framework awareness |
| Setup Effort | **Low** - CLI or GitHub integration |
| Ongoing Maintenance | **Low** - Automated monitoring |
| Quality Impact | **High** - Reachability analysis, fix PRs |
| Cost | **Free** (severely limited) / $1,260+/year (paid) |
| Ecosystem Maturity | **Strong** - Market leader in developer security |

#### Free Tier Limits (2026)

| Feature | Free Tier |
|---------|-----------|
| Private project developers | 1 |
| Open Source tests | 400/month |
| Code tests | 100/month |
| Container tests | 100/month |
| SBOM generation | No |
| Reachability | Limited |

#### Quick Start - CLI

```bash
npm install -g snyk
snyk auth
snyk test --severity-threshold=high
snyk monitor  # Continuous monitoring
```

#### OWASP DC vs Trivy vs Snyk

| Factor | OWASP DC | Trivy | Snyk Free | Snyk Paid |
|--------|----------|-------|-----------|-----------|
| Cost | Free | Free | Free (limited) | $1,260+/yr |
| Setup time | 10 min (+API key) | 2 min | 5 min | 10 min |
| Reachability | No | No | Limited | Yes |
| SBOM generation | CycloneDX | CycloneDX + SPDX | No | Yes |
| Container scanning | Limited | Unlimited | 100/month | Unlimited |
| Secret detection | No | Yes | No | Yes |
| Fix PRs | No | No | Yes | Yes |
| IDE plugin | No | No | Yes | Yes |
| False positives | Medium | Low-Medium | Low | Very Low |
| Offline mode | Yes | Yes | No | No |

### Performance & Security Decision Guide

```
Performance benchmarking:
└── JMH (the only serious option)

Vulnerability scanning:
├── Budget: $0, need comprehensive scanning → Trivy
├── Budget: $0, need Gradle/Maven native plugin → OWASP DC (+ NVD API key)
├── Budget: $0, open source project → Trivy + Snyk Free (fix PRs)
└── Budget: $1,200+/dev/year, need reachability → Snyk Paid (+ Trivy for containers)

SBOM generation:
├── Spring Boot 3.3+ → Built-in CycloneDX (via Actuator)
├── Gradle → CycloneDX Gradle Plugin 3.1.0
├── Maven → CycloneDX Maven Plugin 2.8.1
└── Container images → Trivy
```

---

## Appendix A: Quick-Start Configurations

### Complete Gradle Build (Java + Kotlin)

```kotlin
// build.gradle.kts - Full quality tool stack
plugins {
    java
    kotlin("jvm") version "2.1.0"
    id("org.springframework.boot") version "3.4.0"
    id("io.spring.dependency-management") version "1.1.7"
    jacoco
    id("net.ltgt.errorprone") version "4.0.1"
    id("com.github.spotbugs") version "6.4.8"
    id("io.gitlab.arturbosch.detekt") version "1.23.8"
    id("org.jlleitschuh.gradle.ktlint") version "12.1.0"
    id("info.solidsoft.pitest") version "1.19.0-rc.3"
    id("org.owasp.dependencycheck") version "12.2.0"
    id("org.sonarqube") version "5.0.0.4638"
}

java {
    sourceCompatibility = JavaVersion.VERSION_21
}

// Error Prone (Java compile-time)
dependencies {
    errorprone("com.google.errorprone:error_prone_core:2.47.0")
}

tasks.withType<JavaCompile>().configureEach {
    options.errorprone.disableWarningsInGeneratedCode.set(true)
}

// SpotBugs (bytecode analysis)
spotbugs {
    toolVersion.set("4.9.8")
    effort.set(Effort.MAX)
}

dependencies {
    spotbugsPlugins("com.h3xstream.findsecbugs:findsecbugs-plugin:1.14.0")
}

// Detekt (Kotlin linting)
detekt {
    config.setFrom(file("config/detekt.yml"))
    buildUponDefaultConfig = true
}

dependencies {
    detektPlugins("io.gitlab.arturbosch.detekt:detekt-formatting:1.23.8")
}

// ktlint (Kotlin formatting)
ktlint {
    version.set("1.8.0")
}

// JaCoCo (coverage)
jacoco {
    toolVersion = "0.8.14"
}

tasks.test {
    finalizedBy(tasks.jacocoTestReport)
}

tasks.jacocoTestReport {
    reports {
        xml.required.set(true)
        html.required.set(true)
    }
}

// PIT (mutation testing) - run separately: ./gradlew pitest
pitest {
    junit5PluginVersion.set("1.2.1")
    targetClasses.set(listOf("com.example.*"))
    threads.set(4)
    plugins.set(listOf("pitest-kotlin:1.2.0"))
}

// OWASP Dependency-Check
dependencyCheck {
    nvd {
        apiKey = System.getenv("NVD_API_KEY")
    }
    failBuildOnCVSS = 7.0f
}

// SonarQube
sonarqube {
    properties {
        property("sonar.projectKey", "my-project")
        property("sonar.host.url", System.getenv("SONAR_HOST_URL") ?: "https://sonarcloud.io")
        property("sonar.token", System.getenv("SONAR_TOKEN") ?: "")
    }
}

// Test dependencies
dependencies {
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.boot:spring-boot-testcontainers")
    testImplementation("org.testcontainers:junit-jupiter")
    testImplementation("org.testcontainers:postgresql")
    testImplementation("com.tngtech.archunit:archunit-junit5:1.4.1")
}
```

### Complete Maven POM (Java)

```xml
<project>
    <properties>
        <java.version>21</java.version>
        <jacoco.version>0.8.14</jacoco.version>
        <spotbugs.version>4.7.3.0</spotbugs.version>
        <owasp.dc.version>12.2.0</owasp.dc.version>
        <archunit.version>1.4.1</archunit.version>
        <testcontainers.version>2.0.3</testcontainers.version>
    </properties>

    <dependencies>
        <!-- ArchUnit -->
        <dependency>
            <groupId>com.tngtech.archunit</groupId>
            <artifactId>archunit-junit5</artifactId>
            <version>${archunit.version}</version>
            <scope>test</scope>
        </dependency>

        <!-- Testcontainers -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-testcontainers</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <!-- Error Prone -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <compilerArgs>
                        <arg>-XDcompilePolicy=simple</arg>
                        <arg>-Xplugin:ErrorProne</arg>
                    </compilerArgs>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>com.google.errorprone</groupId>
                            <artifactId>error_prone_core</artifactId>
                            <version>2.47.0</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>

            <!-- JaCoCo -->
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>${jacoco.version}</version>
                <executions>
                    <execution>
                        <goals><goal>prepare-agent</goal></goals>
                    </execution>
                    <execution>
                        <id>report</id>
                        <phase>test</phase>
                        <goals><goal>report</goal></goals>
                    </execution>
                </executions>
            </plugin>

            <!-- SpotBugs -->
            <plugin>
                <groupId>com.github.spotbugs</groupId>
                <artifactId>spotbugs-maven-plugin</artifactId>
                <version>${spotbugs.version}</version>
                <configuration>
                    <effort>Max</effort>
                    <threshold>Low</threshold>
                    <plugins>
                        <plugin>
                            <groupId>com.h3xstream.findsecbugs</groupId>
                            <artifactId>findsecbugs-plugin</artifactId>
                            <version>1.14.0</version>
                        </plugin>
                    </plugins>
                </configuration>
            </plugin>

            <!-- OWASP Dependency-Check -->
            <plugin>
                <groupId>org.owasp</groupId>
                <artifactId>dependency-check-maven</artifactId>
                <version>${owasp.dc.version}</version>
                <configuration>
                    <nvdApiKey>${env.NVD_API_KEY}</nvdApiKey>
                    <failBuildOnCVSS>7</failBuildOnCVSS>
                </configuration>
            </plugin>

            <!-- PIT Mutation Testing -->
            <plugin>
                <groupId>org.pitest</groupId>
                <artifactId>pitest-maven</artifactId>
                <version>1.22.0</version>
                <dependencies>
                    <dependency>
                        <groupId>org.pitest</groupId>
                        <artifactId>pitest-junit5-plugin</artifactId>
                        <version>1.2.1</version>
                    </dependency>
                </dependencies>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## Appendix B: CI/CD Pipeline Template

### GitHub Actions - Full Quality Pipeline

```yaml
name: Quality Pipeline

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read
  security-events: write

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '21'

      - uses: gradle/actions/setup-gradle@v5
        with:
          cache-encryption-key: ${{ secrets.GRADLE_ENCRYPTION_KEY }}
          cache-read-only: ${{ github.ref != 'refs/heads/main' }}

      # Step 1: Compile with Error Prone
      - name: Compile
        run: ./gradlew compileJava compileKotlin --configuration-cache

      # Step 2: Format check (Kotlin)
      - name: ktlint check
        run: ./gradlew ktlintCheck

      # Step 3: Detekt analysis (Kotlin)
      - name: Detekt
        run: ./gradlew detekt

      # Step 4: Tests with JaCoCo coverage
      - name: Test
        run: ./gradlew test jacocoTestReport

      # Step 5: SpotBugs analysis
      - name: SpotBugs
        run: ./gradlew spotbugsMain

      # Step 6: Architecture tests (ArchUnit runs as part of test)
      # Already covered by ./gradlew test above

  security-scan:
    runs-on: ubuntu-latest
    needs: build-and-test
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

  sonar:
    runs-on: ubuntu-latest
    needs: build-and-test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '21'

      - uses: gradle/actions/setup-gradle@v5

      - name: SonarQube Analysis
        run: ./gradlew sonar
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

---

## Appendix C: Evaluation Methodology

### Criteria Definitions

| Criterion | Scale | Description |
|-----------|-------|-------------|
| **Java Compatibility** | Strong / Adequate / Weak | Support for Java 21+, upcoming Java versions |
| **Kotlin Support** | Strong / Adequate / Weak / N/A | Native Kotlin analysis or Kotlin-aware features |
| **Spring Boot Integration** | Strong / Adequate / Weak | Integration with Spring Boot 3.x/4.x ecosystem |
| **Setup Effort** | Low / Medium / High | Time from zero to working configuration |
| **Ongoing Maintenance** | Low / Medium / High | Regular effort to keep tool effective |
| **Quality Impact** | High / Medium / Low | Measurable improvement to code/product quality |
| **Cost** | Free / Freemium / Paid | Licensing model and typical annual cost |
| **Ecosystem Maturity** | Strong / Adequate / Emerging | GitHub activity, community size, release cadence |

### Research Sources

All tool evaluations are based on:
- Official documentation and release notes (as of February 2026)
- GitHub repository activity and issue trackers
- Community benchmarks and comparison articles
- Direct configuration testing

### Cross-Tool Synergies

| Combination | Benefit |
|-------------|---------|
| Error Prone + SpotBugs | Compile-time + post-build coverage |
| Detekt + ktlint | Deep analysis + fast formatting |
| JaCoCo + PIT | Coverage metrics + test quality verification |
| ArchUnit + Spring Modulith | Fine-grained rules + module boundaries |
| Trivy + OWASP DC | Defense in depth for vulnerability scanning |
| Renovate + OpenRewrite | Dependency updates + major migration automation |
| SonarQube + JaCoCo | Coverage tracking in quality dashboards |

### Potential Conflicts

| Combination | Issue | Resolution |
|-------------|-------|------------|
| Error Prone + Lombok | Annotation processor ordering | Configure processor order in compiler plugin |
| Detekt + ktlint (standalone) | Overlapping style rules | Use `detekt-formatting` to embed ktlint in Detekt |
| ArchUnit + Spring Modulith | Overlapping package dependency checks | Use ArchUnit for class-level, Modulith for module-level |
| OWASP DC + Trivy | Redundant scanning | Pick primary (Trivy recommended), keep other for weekly deep scan |

---

## References

### Official Documentation

| Tool | URL |
|------|-----|
| Error Prone | [errorprone.info](https://errorprone.info/) |
| SpotBugs | [spotbugs.readthedocs.io](https://spotbugs.readthedocs.io/) |
| Detekt | [detekt.dev](https://detekt.dev/) |
| ktlint | [github.com/pinterest/ktlint](https://github.com/pinterest/ktlint) |
| SonarQube | [docs.sonarsource.com](https://docs.sonarsource.com/) |
| JaCoCo | [jacoco.org](https://www.jacoco.org/) |
| PIT | [pitest.org](https://pitest.org/) |
| ArchUnit | [archunit.org](https://www.archunit.org/) |
| Testcontainers | [testcontainers.org](https://java.testcontainers.org/) |
| Spring Cloud Contract | [spring.io/projects/spring-cloud-contract](https://spring.io/projects/spring-cloud-contract) |
| Pact | [docs.pact.io](https://docs.pact.io/) |
| Gradle | [gradle.org](https://gradle.org/) |
| GitHub Actions | [docs.github.com/actions](https://docs.github.com/actions) |
| OpenRewrite | [docs.openrewrite.org](https://docs.openrewrite.org/) |
| Renovate | [docs.renovatebot.com](https://docs.renovatebot.com/) |
| JMH | [openjdk.org/projects/code-tools/jmh](https://openjdk.org/projects/code-tools/jmh/) |
| OWASP DC | [owasp.org/www-project-dependency-check](https://owasp.org/www-project-dependency-check/) |
| Trivy | [trivy.dev](https://trivy.dev) |
| Snyk | [snyk.io](https://snyk.io) |

### Key GitHub Repositories

| Repository | Stars | Last Active |
|-----------|-------|-------------|
| [google/error-prone](https://github.com/google/error-prone) | 7.1k | Active |
| [spotbugs/spotbugs](https://github.com/spotbugs/spotbugs) | 3.8k | Active |
| [detekt/detekt](https://github.com/detekt/detekt) | 6.8k | Active |
| [pinterest/ktlint](https://github.com/pinterest/ktlint) | 5.9k | Active |
| [jacoco/jacoco](https://github.com/jacoco/jacoco) | 4.5k | Active |
| [hcoles/pitest](https://github.com/hcoles/pitest) | 1.8k | Active |
| [TNG/ArchUnit](https://github.com/TNG/ArchUnit) | 3.6k | Active |
| [testcontainers/testcontainers-java](https://github.com/testcontainers/testcontainers-java) | 8.6k | Active |
| [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | 31.9k | Active |
| [dependency-check/DependencyCheck](https://github.com/dependency-check/DependencyCheck) | 7.4k | Active |
| [renovatebot/renovate](https://github.com/renovatebot/renovate) | 20.7k | Active |
| [openrewrite/rewrite](https://github.com/openrewrite/rewrite) | N/A | Active |

### Research Cache

This evaluation is backed by four deep research entries cached at `~/.claude/plugins/research/entries/`:

| Slug | Topic | Size |
|------|-------|------|
| `java-kotlin-static-analysis-tools-2026` | Static Analysis Tools | 26K chars |
| `java-testing-quality-tools-2026` | Testing & Quality Tools | 24K chars |
| `java-build-ci-cd-tools-2026` | Build & CI/CD Tools | 35K chars |
| `java-performance-security-tools-2026` | Performance & Security Tools | 34K chars |

Run `/research list` to view cache status, or `/research promote <slug>` to add to project docs.
