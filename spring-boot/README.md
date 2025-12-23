# Spring Boot Plugin

Domain-Driven Design patterns with Spring Boot 4 implementation for complex business systems.

## Components

### Skills

| Skill | Purpose | Auto-Invoked When |
|-------|---------|-------------------|
| **domain-driven-design** | Strategic and tactical DDD guidance | "DDD", "bounded context", "aggregate", "domain model", "ubiquitous language" |
| **spring-boot-data-ddd** | JPA/JDBC implementation patterns | JPA aggregates, Spring Data repositories, entity auditing, projections |
| **spring-boot-web-api** | REST API patterns | REST controllers, validation, ProblemDetail (RFC 9457), WebFlux |
| **spring-boot-modulith** | Modular monolith with Spring Modulith 2.0 | Module structure, @ApplicationModuleListener, event externalization |
| **spring-boot-security** | Spring Security 7, Lambda DSL, JWT/OAuth2 | Authentication, authorization, CORS/CSRF, method security |
| **spring-boot-observability** | Actuator, Micrometer, OpenTelemetry | Health checks, metrics, distributed tracing, Kubernetes probes |
| **spring-boot-testing** | Slice tests, Testcontainers, @MockitoBean | Unit/integration tests, security testing, Modulith Scenario API |
| **spring-boot-verify** | Dependency and configuration verification | pom.xml, build.gradle, application.yml, "verify dependencies", "check configuration" |

## Tech Stack

- **Spring Boot 4** / Spring Framework 7
- **Spring Modulith 2.0**
- **Spring Security 7**
- **Java 21+** (virtual threads support)
- **Jakarta EE 11**
- **JSpecify** (null-safety annotations)
- **OpenTelemetry** (default tracing)
- **Jackson 3**

## Skill Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                    domain-driven-design                         │
│              (Concepts, Patterns, Architecture)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ spring-boot-  │   │  spring-boot-   │   │  spring-boot-   │
│   data-ddd    │   │    web-api      │   │    modulith     │
│  (Data Layer) │   │  (REST Layer)   │   │ (Module Events) │
└───────────────┘   └─────────────────┘   └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ spring-boot-  │   │  spring-boot-   │   │  spring-boot-   │
│   security    │   │  observability  │   │    testing      │
│    (AuthN/Z)  │   │ (Metrics/Trace) │   │  (All Layers)   │
└───────────────┘   └─────────────────┘   └─────────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │     spring-boot-verify    │
              │  (Deps & Config Checker)  │
              └───────────────────────────┘
```

## Use Cases

- Designing complex business systems with DDD
- Implementing aggregates with Spring Data JPA/JDBC
- Building REST APIs with validation and error handling
- Structuring modular monoliths with Spring Modulith
- Securing APIs with Spring Security 7 Lambda DSL
- Production observability with Actuator and OpenTelemetry
- Comprehensive testing with Testcontainers and slice tests
- Verifying project dependencies and configuration for Spring Boot 4 compatibility

## Installation

### Add the Marketplace

```bash
/plugin marketplace add ./arkhe-claude-plugins
```

### Install the Plugin

```bash
/plugin install spring-boot@arkhe-claude-plugins
```

## Usage

Skills auto-invoke based on context:

```bash
# DDD architecture guidance
"How should I structure bounded contexts for this e-commerce system?"

# Spring Data implementation
"How do I implement an aggregate root with JPA?"

# REST API patterns
"How do I handle validation errors with ProblemDetail?"

# Modular monolith
"How do I set up Spring Modulith for my bounded contexts?"

# Security
"How do I configure JWT authentication with Spring Security 7?"

# Observability
"How do I add custom metrics and health checks?"

# Testing
"How do I test my controllers with @WebMvcTest and @MockitoBean?"

# Verification
"Check my pom.xml for Spring Boot 4 compatibility"
"Verify this project's dependencies and configuration"
```

## Skill Coverage

| Skill | Topics |
|-------|--------|
| **domain-driven-design** | Subdomains, bounded contexts, aggregates, domain services, anti-patterns |
| **spring-boot-data-ddd** | Strongly-typed IDs, value objects, repositories, transactions, projections |
| **spring-boot-web-api** | Validation groups, exception handlers, content negotiation, WebFlux |
| **spring-boot-modulith** | Package conventions, event publishing, module testing, event externalization |
| **spring-boot-security** | Lambda DSL, SecurityFilterChain, OAuth2/JWT, @PreAuthorize, password encoding |
| **spring-boot-observability** | Actuator endpoints, Micrometer Timer/Counter/Gauge, OpenTelemetry spans |
| **spring-boot-testing** | @WebMvcTest, @DataJpaTest, Testcontainers, @WithMockUser, Scenario API |
| **spring-boot-verify** | Version matrix, deprecated dependencies, configuration validation, migration readiness |

## Skill Reference Files

| Skill | References |
|-------|------------|
| **domain-driven-design** | `tactical-patterns.md`, `strategic-design.md`, `architecture-decisions.md` |
| **spring-boot-data-ddd** | `aggregates.md`, `repositories.md`, `transactions.md` |
| **spring-boot-web-api** | `controllers.md`, `error-handling.md`, `webflux.md` |
| **spring-boot-modulith** | `module-structure.md`, `events.md` |
| **spring-boot-security** | `security-config.md`, `authentication.md`, `jwt-oauth2.md` |
| **spring-boot-observability** | `actuator.md`, `metrics.md`, `tracing.md` |
| **spring-boot-testing** | `slice-tests.md`, `testcontainers.md`, `security-testing.md`, `modulith-testing.md` |
| **spring-boot-verify** | `dependencies.md`, `configuration.md` |

## Skill Supporting Documentation

Each skill (except `domain-driven-design`) includes:
- **EXAMPLES.md** - Complete working code examples
- **TROUBLESHOOTING.md** - Common issues and Spring Boot 4 migration

## Deep Dive Resources

For comprehensive background and architectural context, see the research materials:

| Document | Description |
|----------|-------------|
| [DDD Fundamentals](../docs/research/domain-driven-design.md) | Strategic DDD, subdomains, bounded contexts, Event Storming |
| [Spring Boot 4 Ecosystem](../docs/research/spring-boot/ecosystem-research.md) | Framework 7 architecture, Java 25 alignment, Jackson 3, build tools |
| [DDD Implementation](../docs/research/spring-boot/ddd-implementation.md) | Aggregates, repositories, value objects with Spring Boot 4 |
| [Security & Observability](../docs/research/spring-boot/security-observability-testing.md) | Security 7 Lambda DSL, OpenTelemetry, testing strategies |

## Spring Boot 4 Breaking Changes

### Security (Lambda DSL Mandatory)

```java
// ❌ Old (removed in Security 7)
http.authorizeRequests()
    .antMatchers("/api/**").authenticated()
    .and()
    .oauth2ResourceServer().jwt();

// ✅ New (required)
http
    .authorizeHttpRequests(auth -> auth
        .requestMatchers("/api/**").authenticated()
    )
    .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
```

### Testing (@MockitoBean)

```java
// ❌ Old (removed in Boot 4)
@MockBean
private OrderService orderService;

// ✅ New (required)
@MockitoBean
private OrderService orderService;
```

### Migration Checklist

- [ ] Replace `@MockBean` → `@MockitoBean`
- [ ] Replace `authorizeRequests()` → `authorizeHttpRequests()`
- [ ] Replace `antMatchers()` → `requestMatchers()`
- [ ] Remove all `and()` calls in Security config
- [ ] Replace `@EnableGlobalMethodSecurity` → `@EnableMethodSecurity`
- [ ] Add `@AutoConfigureMockMvc` explicitly to `@SpringBootTest`
- [ ] Replace `@DynamicPropertySource` → `@ServiceConnection` for Testcontainers
- [ ] Update health indicator imports to `org.springframework.boot.health.contributor`

## Version

1.0.0