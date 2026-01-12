# Spring Boot 4.0 Migration Guide

Comprehensive guide for migrating Spring Boot applications from 3.x to 4.0.

Source: [Official Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)

## Table of Contents

- [Pre-Upgrade Preparation](#pre-upgrade-preparation)
- [System Requirements](#system-requirements)
- [Removed Features](#removed-features)
- [Module Reorganization](#module-reorganization)
- [Breaking Changes](#breaking-changes)
- [Deprecations](#deprecations)
- [New Features and Patterns](#new-features-and-patterns)
- [Migration Checklist](#migration-checklist)

---

## Pre-Upgrade Preparation

Before starting the migration:

1. **Upgrade to latest Spring Boot 3.x** - Ensure you're on the latest 3.x release
2. **Review deprecation warnings** - Address all deprecation warnings in 3.x
3. **Update build tools** - Gradle 8.14+ or Maven 3.9+
4. **Run full test suite** - Establish baseline before changes
5. **Create migration branch** - Isolate changes for review

---

## System Requirements

Spring Boot 4.0 has updated baseline requirements:

| Requirement | Minimum Version | Notes |
|-------------|-----------------|-------|
| **Java** | 17+ | Java 11 no longer supported |
| **Jakarta EE** | 11 | Jakarta namespace required |
| **Servlet API** | 6.1 | Servlet 6.0 insufficient |
| **Kotlin** | 2.2+ | If using Kotlin |
| **GraalVM** | 25+ | For native image builds |
| **Gradle** | 8.14+ | For Gradle builds |
| **Maven** | 3.9+ | For Maven builds |

### Verify Java Version

```xml
<!-- pom.xml -->
<properties>
    <java.version>17</java.version>
</properties>
```

```kotlin
// build.gradle.kts
java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}
```

---

## Removed Features

The following features are removed in Spring Boot 4.0:

### Undertow Support

Undertow is dropped due to Servlet 6.1 incompatibility.

**Migration**:
```xml
<!-- Remove -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-undertow</artifactId>
</dependency>

<!-- Use Tomcat (default) or Jetty -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>
```

### Pulsar Reactive Auto-Configuration

Reactive Pulsar auto-configuration removed.

### Embedded Executable Launch Scripts

Embedded launch scripts for uber jars eliminated.

### Spring Session Support

Direct support removed for:
- Spring Session Hazelcast
- Spring Session MongoDB

Use Spring Session's own auto-configuration instead.

### Spock Integration

Spock removed due to Groovy 5 incompatibility.

**Migration**: Convert Spock tests to JUnit 5 or Kotest.

### Optional Dependencies in Uber Jars

Optional dependencies no longer included automatically. Configure explicitly if needed.

---

## Module Reorganization

Spring Boot 4.0 introduces modular architecture with consistent naming.

### Starter Renaming

| Spring Boot 3.x | Spring Boot 4.0 |
|-----------------|-----------------|
| `spring-boot-starter-web` | `spring-boot-starter-webmvc` |
| `spring-boot-starter-webflux` | `spring-boot-starter-webflux` (unchanged) |

**Gradual Migration**: Classic starter POMs remain available for phased adoption.

```xml
<!-- Option 1: New modular starter -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webmvc</artifactId>
</dependency>

<!-- Option 2: Classic starter (gradual migration) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

### Module Naming Pattern

All Spring Boot modules now follow: `spring-boot-<technology>`

- Dedicated test modules for each technology
- Dedicated starters for each technology
- Consistent packaging across modules

---

## Breaking Changes

### Jackson 3 Migration

Jackson upgraded to version 3 with new group IDs.

**Before**:
```xml
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

```java
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;
```

**After**:
```xml
<dependency>
    <groupId>tools.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

```java
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.core.JacksonException;
```

**Note**: Jackson 2 support provided as deprecated stop-gap measure for gradual migration.

### Package Relocations

Several classes moved to new packages:

| Class | Old Package | New Package |
|-------|-------------|-------------|
| `BootstrapRegistry` | `org.springframework.boot` | `org.springframework.boot.bootstrap` |
| `EnvironmentPostProcessor` | `org.springframework.boot.env` | `org.springframework.boot.context.env` |

**Migration**: Update imports in affected files.

### PropertyMapper Behavior Change

PropertyMapper no longer calls methods when source is null.

**Before** (may have worked):
```java
mapper.from(config.getValue())  // Called even if null
    .to(builder::setValue);
```

**After** (throws on null):
```java
mapper.from(config.getValue())
    .whenNonNull()  // Explicit null handling
    .to(builder::setValue);
```

### Security Filter Chain Updates

Spring Security 7 removes `and()` method chaining.

**Before**:
```java
http
    .authorizeHttpRequests()
        .anyRequest().authenticated()
    .and()
    .oauth2ResourceServer()
        .jwt();
```

**After**:
```java
http
    .authorizeHttpRequests(auth -> auth
        .anyRequest().authenticated()
    )
    .oauth2ResourceServer(oauth2 -> oauth2
        .jwt(Customizer.withDefaults())
    );
```

### HTTP Message Converters

`HttpMessageConverters` deprecated. Spring Framework provides improved defaults.

Use customizers for client/server message converter configuration:
- `HttpMessageConvertersCustomizer` for server
- `RestClientCustomizer` for RestClient
- `WebClientCustomizer` for WebClient

---

## Deprecations

### Testing Annotations

| Deprecated | Replacement |
|------------|-------------|
| `@MockBean` | `@MockitoBean` |
| `@SpyBean` | `@MockitoSpyBean` |

**Migration**:
```java
// Before
@MockBean
private UserService userService;

@SpyBean
private AuditService auditService;

// After
@MockitoBean
private UserService userService;

@MockitoSpyBean
private AuditService auditService;
```

### Test Configuration Annotations

New required annotations for test configuration:

- `@AutoConfigureMockMvc` - Required for MockMvc tests
- `@AutoConfigureTestRestTemplate` - Required for TestRestTemplate
- `@AutoConfigureRestTestClient` - Required for RestTestClient

### MockitoExtension Over TestExecutionListener

Migration from `MockitoTestExecutionListener` to `MockitoExtension`.

---

## New Features and Patterns

### Liveness and Readiness Probes

Probes now **enabled by default**.

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true  # Now default
```

### JSpecify Nullability Annotations

Spring Boot 4 adopts JSpecify for null-safety annotations.

### Virtual Threads Support

Enable virtual threads (Project Loom):

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

### Improved Logback Defaults

UTF-8 charset handling improved by default.

### Modular Architecture Benefits

- Smaller runtime footprint
- Explicit dependencies
- Better native image support
- Clearer component boundaries

---

## Migration Checklist

### Phase 1: Prerequisites

- [ ] Upgrade to latest Spring Boot 3.x
- [ ] Resolve all deprecation warnings
- [ ] Update Java to 17+
- [ ] Update Kotlin to 2.2+ (if applicable)
- [ ] Update Gradle to 8.14+ or Maven to 3.9+
- [ ] Run full test suite and document baseline

### Phase 2: Dependencies

- [ ] Update `spring-boot-starter-parent` to 4.0.x
- [ ] Remove Undertow dependency (if present)
- [ ] Migrate Jackson 2 to Jackson 3:
  - [ ] Update Maven/Gradle group IDs
  - [ ] Update Java imports
- [ ] Update starter names (or use classic starters)

### Phase 3: Security Configuration

- [ ] Remove `and()` method chaining
- [ ] Replace `antMatchers()` with `requestMatchers()`
- [ ] Replace `authorizeRequests()` with `authorizeHttpRequests()`
- [ ] Replace `@EnableGlobalMethodSecurity` with `@EnableMethodSecurity`
- [ ] Convert to Lambda DSL patterns

### Phase 4: Testing

- [ ] Replace `@MockBean` with `@MockitoBean`
- [ ] Replace `@SpyBean` with `@MockitoSpyBean`
- [ ] Add `@AutoConfigureMockMvc` where needed
- [ ] Add `@AutoConfigureTestRestTemplate` where needed
- [ ] Migrate Spock tests to JUnit 5 (if applicable)

### Phase 5: Configuration

- [ ] Fix package relocations (BootstrapRegistry, EnvironmentPostProcessor)
- [ ] Add null guards for PropertyMapper usage
- [ ] Review actuator endpoint exposure
- [ ] Configure HTTP message converters via customizers

### Phase 6: Validation

- [ ] Run full test suite
- [ ] Test in staging environment
- [ ] Verify actuator endpoints work
- [ ] Validate security configuration
- [ ] Check observability (metrics, traces, logs)

### Phase 7: Optional Enhancements

- [ ] Enable virtual threads
- [ ] Switch to modular starters
- [ ] Configure graceful shutdown
- [ ] Add JSpecify nullability annotations

---

## Recommended Migration Order

1. **Low Risk**: Update Java, Kotlin, build tools
2. **Medium Risk**: Replace test annotations (@MockBean → @MockitoBean)
3. **Medium Risk**: Fix package relocations
4. **Medium Risk**: Update Security configuration (Lambda DSL)
5. **High Risk**: Migrate Jackson 2 to Jackson 3
6. **Verification**: Full regression testing after each phase

---

## Resources

- [Official Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- [Spring Boot 4.0 Release Notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes)
- [Spring Security 7 Reference](https://docs.spring.io/spring-security/reference/)
- [Jackson 3 Migration Guide](https://github.com/FasterXML/jackson/wiki/Jackson-3-Migration-Guide)
