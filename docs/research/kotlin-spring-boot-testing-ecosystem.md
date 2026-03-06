---
title: "Backend Testing Ecosystem for Kotlin + Spring Boot 4"
version: "1.0.0"
status: Published
created: 2026-03-05
last_updated: 2026-03-05
slug: kotlin-spring-boot-testing-ecosystem
aliases: ["spring-boot-4-testing", "kotlin-testing-libraries", "spring-modulith-testing"]
tags: ["kotlin", "spring-boot", "testing", "junit5", "testcontainers", "spring-modulith", "mockk", "assertj", "kover", "mutation-testing", "contract-testing"]
promoted_at: 2026-03-06T16:26:23.994906Z
last_refreshed: 2026-03-05T14:46:05.063147+00:00
sources: []
---

<!-- AUTO-GENERATED: Start -->
---
slug: kotlin-spring-boot-testing-ecosystem
title: Backend Testing Ecosystem for Kotlin + Spring Boot 4
aliases:
  - spring-boot-4-testing
  - kotlin-testing-libraries
  - spring-modulith-testing
tags:
  - kotlin
  - spring-boot
  - testing
  - junit5
  - testcontainers
  - spring-modulith
  - mockk
  - assertj
  - coverage
  - mutation-testing
  - contract-testing
researched_at: 2026-03-05T00:00:00Z
expires_at: 2026-04-04T00:00:00Z
sources:
  - url: https://spring.io/blog/2025/12/18/next-level-kotlin-support-in-spring-boot-4
    title: Next Level Kotlin Support in Spring Boot 4 (Spring Blog)
  - url: https://docs.spring.io/spring-modulith/reference/testing.html
    title: Integration Testing Application Modules — Spring Modulith Reference
  - url: https://docs.spring.io/spring-modulith/docs/2.0.3/api/org/springframework/modulith/test/ApplicationModuleTest.html
    title: ApplicationModuleTest API — Spring Modulith 2.0.3
  - url: https://instancio.org/getting-started
    title: Instancio Getting Started
  - url: https://github.com/instancio/instancio/releases
    title: Instancio Releases
  - url: https://plugins.gradle.org/plugin/org.jetbrains.kotlinx.kover
    title: Kover Gradle Plugin — version 0.9.7
  - url: https://github.com/Kotlin/kotlinx-kover
    title: kotlinx-kover GitHub Repository
  - url: https://github.com/kotest/kotest/releases
    title: Kotest Releases (v6.1.4 latest)
  - url: https://github.com/assertj/assertj-core/releases
    title: AssertJ Releases (v3.27.7 latest)
  - url: https://central.sonatype.com/artifact/io.strikt/strikt-core
    title: Strikt Core on Maven Central (v0.35.1)
  - url: https://jqwik.net/release-notes.html
    title: jqwik Release Notes (v1.9.3 latest, v1.9.4-SNAPSHOT targets Kotlin 2.2.21)
  - url: https://www.danvega.dev/blog/mock-vs-rest
    title: MockMvcTester vs RestTestClient in Spring Boot 4 (Dan Vega)
  - url: https://github.com/rest-assured/rest-assured/issues/1853
    title: REST Assured MockMvc incompatibility with Spring Boot 4 (GitHub issue)
  - url: https://odrotbohm.de/2025/12/rethinking-spring-application-integration-testing/
    title: Rethinking Spring Application Integration Testing (Oliver Drotbohm)
  - url: https://www.baeldung.com/spring-test-application-events
    title: How to Test Spring Application Events with Modulith Scenario API (Baeldung)
  - url: https://github.com/naver/fixture-monkey/releases
    title: Fixture Monkey Releases (v1.1.15)
  - url: https://central.sonatype.com/artifact/io.github.serpro69/kotlin-faker
    title: kotlin-faker on Maven Central (v2.0.0-rc.10)
  - url: https://ceur-ws.org/Vol-4077/paper3.pdf
    title: Testing Strategy for Multi-Tenant Web Applications Using TestContainers
  - url: https://java.testcontainers.org/features/reuse/
    title: Testcontainers Reusable Containers (Experimental)
---

# Backend Testing Ecosystem for Kotlin + Spring Boot 4

## Overview

This research covers the current state of the Kotlin + Spring Boot 4.0.1 testing ecosystem as of March 2026. Spring Boot 4.0 established Kotlin 2.2 as the official baseline, creating a new compatibility tier that not all libraries have fully certified against. Spring Framework 7.0 (which powers Boot 4.0) enforces the jakarta.* namespace throughout, which is a hard breaking change for libraries still using javax.*.

The primary testing stack recommendation for a Spring Boot 4 + Kotlin 2.2 + Java 21 project is:
- **Assertions**: AssertJ 3.27.x (already on classpath) with optional Kotest assertions as a supplement
- **Test data**: Instancio 5.x for JVM objects; kotlin-faker 2.x for locale-specific fakes
- **Coverage**: Kover 0.9.7 (JetBrains, Kotlin-native)
- **Property-based**: jqwik 1.9.3 with its Kotlin module
- **API testing**: MockMvcTester (built in) + RestTestClient for Spring Boot 4
- **Contract testing**: Pact (polyglot; matches OpenAPI-spec workflow)
- **Database testing**: @DataJpaTest + Testcontainers (reuse mode for local dev)
- **Mutation testing**: PIT 1.19.x (with pitest-kotlin awareness)
- **Modulith**: @ApplicationModuleTest + Scenario DSL (already partially used)

---

## Category 1: Assertion Libraries

### AssertJ
- **Latest version**: 3.27.7 (January 2026); Spring Boot 4.0 bundles 3.27.x via spring-boot-starter-test
- **Compatibility**: Full — Spring Boot team tracks and upgrades AssertJ internally
- **Kotlin support**: No dedicated Kotlin DSL, but it works idiomatically from Kotlin via the standard fluent API
- **Spring Boot 4 highlight**: `MockMvcTester` (introduced in Spring Framework 6.2 / Boot 3.4) provides full AssertJ integration for controller tests. Spring Boot 4 introduces `RestTestClient` (from `spring-boot-starter-webmvc-test`) with AssertJ as well
- **Community health**: 2.8k GitHub stars, maintained by the AssertJ core team, active

### Kotest Assertions (standalone)
- **Latest version**: 6.1.4 (February 2026), with 6.0 being the stable major release
- **Compatibility**: Kotest 6.x is designed for Kotlin 2.x. The assertions module (`kotest-assertions-core`) can be used standalone — no Kotest runner required. It registers as a JUnit 5 extension automatically.
- **Kotlin DSL**: First-class — e.g. `name shouldBe "Alice"`, `list shouldContainExactly listOf(...)`, null-safe matchers, soft assertions
- **Community health**: 4.8k GitHub stars, very active (6.1.4 released Feb 2026)
- **Caveat**: IntelliJ plugin for Kotest had IDE integration issues pre-6.0; these are resolved in 6.1.x

### Strikt
- **Latest version**: 0.35.1 (June 2024) — last release was 8 months ago as of writing
- **Compatibility**: Kotlin stdlib dependency pinned to 1.9.20; will work on JVM but not formally certified for Kotlin 2.2 K2 compiler
- **Kotlin DSL**: Excellent type-safe API with assertion blocks
- **Community health**: ~500 stars; largely unmaintained (single maintainer, no commits since mid-2024)
- **Verdict**: SKIP — maintenance concern overrides the API quality advantage

### kotlin-test assertions
- **Already on classpath** via `kotlin-test-junit5`
- **Provides**: `assertEquals`, `assertNotNull`, `assertFails`, `assertIs`, basic matchers
- **Limitation**: No rich fluent DSL, no collection assertions, no soft assertions
- **Verdict**: Use for trivial unit tests; not a replacement for AssertJ or Kotest assertions

### Kluent
- **Status**: Officially DISCONTINUED (per LibHunt data, 2025)
- **Verdict**: SKIP

### Hamcrest
- **Status**: Included transitively but Mockito was explicitly excluded. Hamcrest is still brought in by `spring-boot-starter-test` via JUnit 4 compat
- **Verdict**: EXCLUDE via `exclude(group = "org.hamcrest")` in test dependencies — it adds noise and is superseded by AssertJ

---

## Category 2: Test Data Generation / Fixtures

### Manual Fixtures (TransactionFixtures.kt)
- **Current approach**: Object with factory methods returning domain objects with sensible defaults
- **Strength**: Full domain type safety; parameters self-document intent; fixtures are coupled to your domain model
- **Weakness**: Every new field requires updating all factory methods; brittle under model evolution

### Instancio
- **Latest version**: 5.4.1 (March 2026); `instancio-junit` is the JUnit 5 artifact
- **Compatibility**: Java 8+; supports Java 21 sequenced collections, records, sealed classes; fully compatible with Kotlin data classes via reflection. JUnit 5 integration through `@ExtendWith(InstancioExtension.class)` + `@Seed`
- **Kotlin usage**:
```kotlin
val transaction: Transaction = Instancio.create(Transaction::class.java)
val transactions: List<Transaction> = Instancio.ofList(Transaction::class.java).size(5).create()
// With field overrides:
val completed = Instancio.of(Transaction::class.java)
    .set(field(Transaction::status), TransactionStatus.COMPLETED)
    .create()
```
- **Jakarta Bean Validation support**: Respects `@NotNull`, `@Size`, `@Min`/`@Max` annotations via `InstancioJpaSupport` plugin
- **Community health**: 1k GitHub stars, actively maintained by a single dedicated author, very frequent releases
- **Best use case**: Generating complex object graphs (TransactionItem hierarchies) where you only care about a few specific fields

### kotlin-faker
- **Latest version**: 2.0.0-rc.10 (May 2025) — still release candidate; v1.x stable exists
- **Compatibility**: Kotlin 2.1.21 stdlib in RC, 60+ locales, 213 data generators
- **Use case**: Generating realistic-looking strings — names, addresses, IBANs, phone numbers — for data that appears in UI or audit logs. Not for generating entire object graphs.
- **Community health**: 484 GitHub stars; actively maintained

### Fixture Monkey (Naver)
- **Latest version**: 1.1.15 (September 2025)
- **Compatibility**: Has a `fixture-monkey-starter-kotlin` artifact with `KotlinPlugin()`. Requires Kotest property 5.6.2 and jqwik 1.7.x as underlying arbitraries.
- **Kotlin usage**:
```kotlin
val fixtureMonkey = FixtureMonkey.builder().plugin(KotlinPlugin()).build()
val product: Product = fixtureMonkey.giveMeOne()
val customized = fixtureMonkey.giveMeBuilder<Product>()
    .setExp(Product::id, 1000L)
    .sample()
```
- **Community health**: 683 GitHub stars; maintained by Naver (large Korean tech company)
- **Complexity**: Higher setup cost than Instancio; stronger property-based flavor; requires jqwik or Kotest as underlying engine

### EasyRandom / java-faker
- **EasyRandom**: 1.5k stars but effectively unmaintained (last release 2022). SKIP.
- **java-faker**: ~10k stars but Java-only, no Kotlin DSL; kotlin-faker is the Kotlin port. Use kotlin-faker instead.

---

## Category 3: Code Coverage

### JaCoCo
- **Status**: Included transitively by many Spring Boot plugins; Gradle plugin is `jacoco`
- **Kotlin issues**: Poor handling of Kotlin inline functions (reports uncoverable synthetic bytecode as missing), final classes require `open` instrumentation, coroutines generate continuation classes that inflate line counts
- **Best for**: Mixed Java/Kotlin projects where Java coverage matters; CI gate requirements

### Kover (JetBrains)
- **Latest version**: 0.9.7 (February 2026) — actively developed by JetBrains Kotlin team
- **Compatibility**: Designed specifically for Kotlin JVM and Kotlin Multiplatform; works with Kotlin 2.x; Gradle plugin tested against current Gradle versions
- **Gradle setup**:
```kotlin
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.9.7"
}

kover {
    reports {
        verify {
            rule {
                minBound(80)
            }
        }
    }
}
```
- **Kotlin advantages**:
  - Correctly handles `inline` functions (excludes non-coverable synthetic methods)
  - Handles data class `copy()`, `equals()`, `hashCode()` correctly
  - Coroutines-aware via the JetBrains coverage agent
  - No false "missing" branches on sealed class exhaustive whens
- **Report formats**: HTML, XML (for SonarQube/Codecov integration)
- **Community health**: 1.4k stars; JetBrains-owned, active

### Recommendation
Use **Kover** for a pure Kotlin project. JaCoCo can be used for CI artifact compatibility (Codecov, SonarQube) since Kover can emit JaCoCo-compatible XML.

---

## Category 4: Property-Based Testing

### jqwik
- **Latest version**: 1.9.3 (June 2025); 1.9.4-SNAPSHOT already upgrades to Kotlin 2.2.21 and JUnit Platform 1.14.0 — meaning full Kotlin 2.2 support is imminent (should be released before mid-2026)
- **Compatibility**: JUnit 5 native (runs as a JUnit 5 test engine, no separate runner needed). Has a dedicated `net.jqwik:jqwik-kotlin` module.
- **Spring integration**: `jqwik-spring` extension (24 stars, maintained by same author) allows `@SpringBootTest` + `@Property` in the same class
- **Kotlin DSL**:
```kotlin
@Property
fun `transaction number always matches format`(
    @ForAll @LongRange(min = 1, max = 99999) seqNum: Long
) {
    val number = TransactionNumberFormatter.format(seqNum)
    assertThat(number).matches("TXN-\\d{8}-\\d{5}")
}
```
- **Key features**: Input shrinkage (finds minimal failing case), `@Provide` custom arbitraries, stateful testing via `Action` chains
- **Community health**: 621 GitHub stars, 64 forks; maintained by Johannes Link (jlink)

### Kotest Property Testing
- **Availability**: `kotest-property` module, standalone without Kotest runner via JUnit 5 compat
- **Latest**: 6.1.4
- **Consideration**: If Kotest assertions are already added, this is a natural extension. However, it requires the Kotest JUnit5 runner (`kotest-runner-junit5`) to work well with property tests.

### kotlin-quickcheck
- **Status**: Unmaintained (last activity 2018). SKIP.

### Recommendation
Use **jqwik** — it's pure JUnit 5 native (no new runner required), has excellent Kotlin support via `jqwik-kotlin`, and jqwik 1.9.4 will fully support Kotlin 2.2. Kotest property testing is a viable alternative if the team adopts Kotest runner wholesale.

---

## Category 5: API / Controller Testing

### MockMvcTester (Spring Boot 4 built-in)
- **Status**: Included in `spring-boot-starter-test` (via Spring Framework 6.2+). Spring Boot 4.0 bundles this.
- **AssertJ integration**: Full — `perform(get("/api/transactions")).andExpect()` replaced by fluent AssertJ chains
- **Usage**:
```kotlin
@WebMvcTest(TransactionController::class)
class TransactionControllerTest {
    @Autowired lateinit var mvc: MockMvcTester

    @Test
    fun `create transaction returns 201`() {
        mvc.post().uri("/api/transactions")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""{"items": [...]}""")
            .assertThat()
            .hasStatus(HttpStatus.CREATED)
    }
}
```
- **Best for**: Server-side inspection, multipart uploads, handler mapping verification

### RestTestClient (Spring Boot 4 new)
- **Module**: `spring-boot-starter-webmvc-test` (separate starter in Boot 4's new modular architecture)
- **Usage**: Annotation `@AutoConfigureRestTestClient` on `@WebMvcTest` class
- **Best for**: Typed response body deserialization, non-JSON (XML, Protobuf), unified API for mock and real HTTP

### WebTestClient
- **Status**: Still available for WebFlux; `@AutoConfigureWebTestClient` annotation was moved to `org.springframework.boot.webtestclient.autoconfigure` package in Boot 4.0 (breaking change from Boot 3.x — StackOverflow confirmed). Requires `spring-boot-starter-webclient` dependency.
- **For WebMvc projects** (this codebase uses webmvc, not webflux): Use MockMvcTester or RestTestClient instead.

### REST Assured
- **Critical issue**: REST Assured's `spring-mock-mvc` module still uses `javax.servlet.*` which was replaced by `jakarta.servlet.*` in Spring Framework 6+. This causes `NoClassDefFoundError: javax/servlet/http/HttpServlet` with Spring Boot 4. The issue is open on GitHub (issue #1853, December 2025) with no fix timeline.
- **Verdict**: SKIP for MockMvc integration. REST Assured's standalone HTTP mode (hitting a running server) still works but adds test complexity.

### Spring REST Docs vs SpringDoc/OpenAPI
- **Spring REST Docs**: Generates documentation from tests — ties documentation accuracy to test coverage. Works with MockMvc. Valuable for API-first projects.
- **SpringDoc/OpenAPI (springdoc-openapi)**: Runtime annotation scanning; generates OpenAPI spec at `/v3/api-docs`. Not test-driven but auto-syncs with code.
- **For this project**: Since `libs/api-contracts/openapi.yaml` is the source of truth and shared with mobile clients, SpringDoc as a documentation-from-tests tool is less critical. Consider Spring REST Docs only if you want test-verified documentation.

---

## Category 6: Contract Testing

### Context
This project has `libs/api-contracts/openapi.yaml` shared between the Spring Boot backend and Kotlin Multiplatform mobile clients. This is a producer-driven OpenAPI spec workflow.

### Spring Cloud Contract
- **Approach**: Provider-driven — the producer writes contracts (Groovy DSL, YAML, or Java) that generate WireMock stubs for consumers
- **Spring Boot 4 compatibility**: Spring Cloud Contract is part of the Spring ecosystem and tracks Spring Boot versions. Version 4.x is expected to align with Boot 4.0.
- **Strengths**: Native Spring integration, stub generation for consumer testing, good CI/CD story
- **Weaknesses**: JVM-centric (mobile Kotlin client support is limited), consumer has to use generated stubs (not standard WireMock)
- **Fit for this project**: Moderate — useful for backend-to-backend contracts but the mobile client workflow is awkward

### Pact
- **Approach**: Consumer-driven — each consumer (mobile app, web dashboard) defines the interactions they expect. Providers verify against all registered consumer pacts.
- **Language support**: Java (pact-jvm), Kotlin, TypeScript/JS, Swift/Obj-C — perfect for the polyglot consumer set here
- **OpenAPI integration**: Pact 4.x can validate a provider's OpenAPI spec against consumer pacts. This directly addresses the shared `openapi.yaml` use case.
- **Pact Broker**: Centralized contract repository (self-hosted or PactFlow SaaS) enabling "can I deploy?" checks in CI
- **Spring Boot 4 compatibility**: `pact-jvm-provider-junit5` works with JUnit 5; the provider verification side does not use servlet APIs directly so jakarta migration is not an issue

### Recommendation
**Pact** is the better fit because:
1. Mobile clients (KMP) can write consumer pacts in Kotlin
2. The TypeScript web client can write consumer pacts in JS
3. Pact can validate provider compliance against the existing `openapi.yaml`
4. Consumer-driven naturally catches breaking API changes before they reach mobile

---

## Category 7: Database Testing Enhancements

### Current Setup
`@SpringBootTest` + Testcontainers (PostgreSQL) + Flyway — high fidelity but slow (context startup + container startup per test class that doesn't share a context).

### @DataJpaTest Slice Testing
- **Status**: Available in `spring-boot-starter-test` — no additional dependency
- **What it does**: Loads only JPA-related beans (repositories, entities, Flyway/Liquibase, DataSource) — no web layer, no services. ~3-5x faster than full `@SpringBootTest`.
- **With Testcontainers**:
```kotlin
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class TransactionRepositoryTest {
    @Container
    companion object {
        @JvmStatic
        val postgres = PostgreSQLContainer<Nothing>("postgres:18")
    }
    // ...
}
```
- **Multi-tenancy consideration**: `@TenantId` on entities and `TenantContext` need to be populated before repository calls. Wrap each test in `TenantContext.withTenant(tenantId) { }`.

### Testcontainers Reusable Mode
- **Status**: "Experimental" in official docs but widely used in production projects
- **How it works**: Containers that have `.withReuse(true)` set are not stopped after test suite completion. A container hash is stored in `~/.testcontainers.properties`. Second run reuses the existing container.
- **Setup**:
```kotlin
companion object {
    @JvmStatic
    val postgres = PostgreSQLContainer<Nothing>("postgres:18-alpine")
        .withReuse(true) // Keep container alive between runs
}
```
- **Local dev benefit**: First run: ~30s to pull and start. Subsequent runs: ~100ms. Dramatically faster feedback loop.
- **CI**: Do not enable reuse in CI — containers are ephemeral per build agent.
- **Warning**: Database state persists between runs in reuse mode. Use `@Transactional` on tests or `@Sql` to truncate between tests.

### Database Rider (DBUnit wrapper)
- **Status**: Active but with integration issues in 2025 — GitHub reports show insert failures with Testcontainers + Spring Boot. Root cause is connection lifecycle conflicts between DBUnit's `@DBRider` transaction model and Spring's transaction management.
- **Verdict**: SKIP — the dataset-driven testing pattern adds XML/YAML fixture complexity that Instancio handles better without the integration headaches.

### Multi-Tenant Testing Patterns
- **Recommended pattern**: Create a `TenantContextExtension` JUnit 5 extension that wraps each test in `TenantContext.withTenant("test-tenant")`:
```kotlin
@ExtendWith(TenantContextExtension::class)
class TransactionRepositoryTest { ... }
```
- Or use `@BeforeEach` / `@AfterEach` in a base class to set/clear tenant context
- Test data isolation: Use separate tenant IDs per test class (e.g., UUID per test run) to avoid row-level leakage

---

## Category 8: Mutation Testing

### PIT (pitest)
- **Latest version**: 1.19.1 (April 2025)
- **Gradle plugin**: `info.solidsoft.gradle.pitest` — use version 1.15.0+
- **JUnit 5 integration**: Requires `pitest-junit5-plugin` as a separate dependency
- **Kotlin support status**:
  - Standard Kotlin classes: Works well, bytecode mutation is language-agnostic at JVM level
  - `inline` functions: Cannot be mutated (bytecode is inlined at call sites). Expected behavior.
  - `suspend` functions: Known issue (GitHub #1391, March 2025) — Pitest reports no coverage on `@Component` suspend methods. Non-reactive suspend in services is affected.
  - Data classes: `copy()`, `equals()`, `hashCode()` generate many surviving mutants. Exclude them via `excludedClasses`.
- **Gradle setup**:
```kotlin
plugins {
    id("info.solidsoft.pitest") version "1.15.0"
}

pitest {
    pitestVersion.set("1.19.1")
    junit5PluginVersion.set("1.2.1")
    targetClasses.set(setOf("cv.deznode.pos.*"))
    excludedClasses.set(setOf("cv.deznode.pos.**.domain.*Kt")) // exclude data class generated methods
    mutationThreshold.set(70)
    threads.set(4)
    outputFormats.set(setOf("HTML", "XML"))
}
```
- **Community health**: 2k GitHub stars; actively maintained by Henry Coles

### Is it worth introducing now?
- **Pre-conditions for value**: PIT requires existing test coverage of 70%+ to produce actionable results. Running it on sparse coverage produces noise. Current test count (8 classes) suggests deferral.
- **Recommendation**: Introduce LATER when the domain layer has stable, comprehensive unit tests.

---

## Category 9: Spring Modulith-Specific Testing

### Already in Use
The project already has `spring-modulith-starter-test` on the classpath and presumably uses `@ApplicationModuleTest` for architecture verification (`ModulithTests`).

### What @ApplicationModuleTest Offers

**Bootstrap Modes** — controls how many modules are loaded:
```kotlin
@ApplicationModuleTest // default: STANDALONE
@ApplicationModuleTest(mode = BootstrapMode.DIRECT_DEPENDENCIES)
@ApplicationModuleTest(mode = BootstrapMode.ALL_DEPENDENCIES)
```
- `STANDALONE`: Only the module under test. Fast. All dependencies must be mocked.
- `DIRECT_DEPENDENCIES`: The module + its direct module dependencies. Good for integration tests that cross one boundary.
- `ALL_DEPENDENCIES`: Full transitive graph. Equivalent to `@SpringBootTest` scoped to the module cluster.

**Published Events API**:
```kotlin
@ApplicationModuleTest
class TransactionModuleTest {
    @Test
    fun `completing a transaction publishes TransactionCompletedEvent`(
        events: PublishedEvents
    ) {
        // ... call service method that fires event
        val completed = events.ofType(TransactionCompletedEvent::class.java)
        assertThat(completed).hasSize(1)
    }
}
```

### Scenario DSL (Spring Modulith 2.0)
The `Scenario` API provides a declarative DSL for event-driven integration tests. It was introduced in earlier versions but significantly improved in 2.0.

```kotlin
@ApplicationModuleTest
class TransactionScenarioTest {
    @Test
    fun `completing a transaction triggers compliance submission`(
        scenario: Scenario
    ) {
        scenario
            .stimulate { transactionService.complete(transactionId) }
            .andWaitForEventOfType(TransactionCompletedEvent::class.java)
            .toArrive()
            .andVerify { event ->
                assertThat(event.transactionId).isEqualTo(transactionId)
            }
    }
}
```

Key `Scenario` operations:
- `.stimulate { }` — triggers the SUT action
- `.andWaitForEventOfType(...)` — asserts event publication
- `.andExpect(SomeEvent::class.java)` — asserts event receipt by a listener
- `.toArrive()` / `.toArriveAndVerify { }` — finalizes the assertion

**Module Documentation Generation**:
```kotlin
@Test
fun `writeDocumentationSnippets`() {
    ApplicationModules.of(Application::class.java)
        .forEach { it.verify() }
}
```
Modulith can generate PlantUML/C4 diagrams from module structure. Call from a test to regenerate docs in CI.

**`@EnableScenarios`**: Class-level annotation to enable Scenario injection without inheriting from any base class.

### Practical Recommendations for This Project
1. Move from `@SpringBootTest` in `ModulithTests` to `@ApplicationModuleTest` per-module tests
2. Use `STANDALONE` mode for pure business logic tests (mock external module APIs)
3. Use `DIRECT_DEPENDENCIES` mode for event-flow tests between `transaction` and `compliance` modules
4. Add `Scenario` DSL tests for e-Fatura submission flow when compliance module is built

---

## Summary Recommendation Table

| Category | Recommended Choice | Version | Adoption Priority | Notes |
|---|---|---|---|---|
| **Assertions** | AssertJ (keep) | 3.27.7 | KEEP — already in use | Supplement with Kotest assertions if team wants Kotlin DSL |
| **Assertions (Kotlin DSL)** | Kotest assertions (standalone) | 6.1.4 | SOON | Add `kotest-assertions-core` only — no runner needed |
| **Test Data Fixtures** | Instancio | 5.4.1 | NOW | Replace ad-hoc builders; complement TransactionFixtures.kt |
| **Fake Data (strings/locale)** | kotlin-faker | 2.0.0-rc.10 | LATER | Only needed when realistic string data matters (names, IBANs) |
| **Code Coverage** | Kover | 0.9.7 | NOW | JetBrains-native Kotlin coverage; replaces JaCoCo for Kotlin |
| **Property-Based Testing** | jqwik + jqwik-kotlin | 1.9.3 | SOON | No new test runner; pure JUnit 5; Kotlin 2.2 support in 1.9.4 |
| **API Testing (controllers)** | MockMvcTester | Boot 4.0 built-in | NOW | Switch existing MockMvc tests; already on classpath |
| **API Testing (typed responses)** | RestTestClient | Boot 4.0 new starter | SOON | Add `spring-boot-starter-webmvc-test` when needed |
| **REST Assured** | SKIP | — | SKIP | `spring-mock-mvc` broken with jakarta (issue #1853, unresolved) |
| **Contract Testing** | Pact (pact-jvm) | 4.6.x | LATER | Valuable when mobile KMP client is consuming the API |
| **DB Slice Tests** | @DataJpaTest | Boot 4.0 built-in | NOW | Add to repository tests; 3-5x faster than @SpringBootTest |
| **Testcontainers Reuse** | withReuse(true) | TC 1.20.x | NOW | Enable locally only; saves 30s+ per subsequent local run |
| **Database Rider** | SKIP | — | SKIP | Integration issues with Spring Boot; Instancio is better |
| **Mutation Testing** | PIT + pitest-kotlin | 1.19.1 | LATER | Wait until domain unit test coverage is substantial |
| **Modulith @AppModuleTest** | @ApplicationModuleTest | SM 2.0.1 | NOW | Already partially used; expand to all modules |
| **Modulith Scenario DSL** | Scenario API | SM 2.0.1 | SOON | Use for event-driven tests (transaction → compliance flow) |
| **Hamcrest** | EXCLUDE | — | NOW | Exclude from spring-boot-starter-test; adds noise |

---

## Immediate Action Items (NOW)

These are zero-new-dependency additions or minimal-risk additions:

1. **Switch to MockMvcTester** — already in `spring-boot-starter-test`. Replace `MockMvc` in controller tests with `MockMvcTester` for AssertJ fluency.

2. **Add Kover** — single Gradle plugin addition:
   ```kotlin
   // build.gradle.kts
   plugins {
       id("org.jetbrains.kotlinx.kover") version "0.9.7"
   }
   ```

3. **Add @DataJpaTest** — use for repository-layer tests instead of `@SpringBootTest`. Add `@AutoConfigureTestDatabase(replace = Replace.NONE)` to use the real PostgreSQL container.

4. **Enable Testcontainers reuse locally** — add `.withReuse(true)` to the PostgreSQL container in integration test base class.

5. **Expand @ApplicationModuleTest** — move module verification tests to per-module `@ApplicationModuleTest(mode = STANDALONE)` tests.

6. **Exclude Hamcrest**:
   ```kotlin
   testImplementation("org.springframework.boot:spring-boot-starter-test") {
       exclude(group = "org.mockito")
       exclude(group = "org.hamcrest")
   }
   ```

## Near-Term Additions (SOON)

7. **Add Instancio** for complex object graph generation:
   ```kotlin
   testImplementation("org.instancio:instancio-junit:5.4.1")
   ```

8. **Add Kotest assertions** (no runner, pure assertions):
   ```kotlin
   testImplementation("io.kotest:kotest-assertions-core:6.1.4")
   ```

9. **Add jqwik** for property-based testing of domain invariants (Money, TransactionNumber, tax calculations):
   ```kotlin
   testImplementation("net.jqwik:jqwik:1.9.3")
   testImplementation("net.jqwik:jqwik-kotlin:1.9.3")
   ```

10. **Add Scenario DSL tests** for event-driven flows (no new dependency — part of `spring-modulith-starter-test`).

---

## Compatibility Matrix

| Library | Kotlin 2.2 | Java 21 | Spring Boot 4.0.1 | Spring Framework 7 | Jakarta NS |
|---|---|---|---|---|---|
| AssertJ 3.27.x | Yes | Yes | Yes (bundled) | Yes | N/A |
| Kotest 6.1.4 | Yes | Yes | Compatible | Yes | N/A |
| Instancio 5.4.x | Yes (reflection) | Yes | Compatible | N/A | Yes (JPA annotations) |
| kotlin-faker 2.0.0-rc | Yes (2.1.21 stdlib) | Yes | Compatible | N/A | N/A |
| Kover 0.9.7 | Yes (JetBrains native) | Yes | Yes (Gradle plugin) | N/A | N/A |
| jqwik 1.9.3 | Yes (Kotlin 2.1.21 in 1.9.3, 2.2 in 1.9.4) | Yes | JUnit 5 native | N/A | N/A |
| MockMvcTester | Yes | Yes | Yes (built-in) | Yes | Yes |
| RestTestClient | Yes | Yes | Yes (new starter) | Yes | Yes |
| REST Assured (spring-mock-mvc) | N/A | N/A | BROKEN | BROKEN (javax issue) | No |
| Pact (pact-jvm) | Yes | Yes | JUnit 5 native | N/A | N/A |
| PIT 1.19.x | Partial (no suspend) | Yes | Yes (build plugin) | N/A | N/A |
| Spring Modulith 2.0.1 | Yes | Yes | Yes (BOM managed) | Yes | Yes |
| Strikt 0.35.1 | Uncertain (1.9.20 stdlib) | Yes | Compatible | N/A | N/A |
<!-- AUTO-GENERATED: End -->

<!-- TEAM-NOTES: Start -->
## Team Context

_Add project-specific notes, implementation references, and team knowledge here._

<!-- TEAM-NOTES: End -->
