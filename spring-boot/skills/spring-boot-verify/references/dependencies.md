# Spring Boot 4.x Dependency Verification Rules

Complete dependency compatibility matrix and verification rules for Spring Boot 4.x projects.

## Core Dependency Matrix

### Spring Boot 4.x Required Versions

| Component | Minimum Version | Recommended | Notes |
|-----------|-----------------|-------------|-------|
| **Java** | 17 | 25 | Virtual threads require 21+ |
| **Kotlin** | 2.2.0 | 2.2.0+ | K2 compiler, strict null-safety |
| **Spring Framework** | 7.0.0 | 7.0.x | Strict requirement |
| **Spring Security** | 7.0.0 | 7.0.x | Lambda DSL mandatory |
| **Hibernate** | 7.0.0 | 7.x | JPA 3.2, StatelessSession |
| **Jackson** | 3.0.0 | 3.x | New namespace: `tools.jackson` |
| **Gradle** | 8.14 | 8.14+ | Required for Kotlin 2.2 |
| **Maven** | 3.6.3 | 3.9+ | - |
| **Tomcat** | 11.0.0 | 11.x | Servlet 6.1 |
| **Jetty** | 12.1.0 | 12.1.x | Alternative to Tomcat |
| **JUnit** | 5.11+ | 6.x planned | Latest testing framework |
| **Mockito** | 5.x | 5.x+ | Required for @MockitoBean |
| **Testcontainers** | 1.20+ | Latest | @ServiceConnection support |
| **Spring Modulith** | 2.0.x | 2.0.x | Bounded context modeling |

### Jakarta EE 11 Requirements

| Component | Version | Package |
|-----------|---------|---------|
| Servlet API | 6.1 | `jakarta.servlet.*` |
| JPA | 3.2 | `jakarta.persistence.*` |
| Validation | 3.1 | `jakarta.validation.*` |
| Security Enterprise | 4.0 | `jakarta.security.enterprise.*` |
| Concurrency | 3.1 | `jakarta.enterprise.concurrent.*` |

## Deprecated Dependencies

### CRITICAL - Must Replace Immediately

| Deprecated | Replacement | Detection Pattern |
|------------|-------------|-------------------|
| `com.fasterxml.jackson.*` | `tools.jackson.*` | Grep imports and Maven/Gradle deps |
| Undertow server | Tomcat or Jetty | `spring-boot-starter-undertow` dependency |
| `ObjectMapper` | `JsonMapper` | Jackson 3 uses immutable mapper |

**Jackson 3 Migration Example**:

```java
// Before (Jackson 2)
import com.fasterxml.jackson.databind.ObjectMapper;
ObjectMapper mapper = new ObjectMapper();

// After (Jackson 3)
import tools.jackson.databind.json.JsonMapper;
JsonMapper mapper = JsonMapper.builder().build();
```

### ERROR - Will Cause Failures

| Deprecated | Replacement | Location |
|------------|-------------|----------|
| `@MockBean` | `@MockitoBean` | Test files |
| `@SpyBean` | `@MockitoSpyBean` | Test files |
| `@EnableGlobalMethodSecurity` | `@EnableMethodSecurity` | Security config |
| `WebSecurityConfigurerAdapter` | `SecurityFilterChain` bean | Security config |
| `RestTemplate` | `RestClient` or `@HttpExchange` | HTTP clients |

**Testing Migration Example**:

```java
// Before (Boot 3.x)
@MockBean
private UserService userService;

// After (Boot 4.x)
@MockitoBean
private UserService userService;
```

### WARNING - Should Update

| Deprecated | Replacement | Notes |
|------------|-------------|-------|
| `spring-boot-starter-web` | `spring-boot-starter-webmvc` | Modular starters in Boot 4 |
| `spring-boot-starter-aop` | `spring-boot-starter-aspectj` | Renamed |
| Brave tracing | OpenTelemetry | Default in Boot 4 |

## Required Dependencies

### Minimum Maven pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.0.1</version>
    </parent>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webmvc</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

### Minimum Gradle (Kotlin DSL)

```kotlin
plugins {
    java
    id("org.springframework.boot") version "4.0.1"
    id("io.spring.dependency-management") version "1.1.7"
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-webmvc")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

## Starter Migration Map

### Web Starters

| Boot 3.x | Boot 4.x | Notes |
|----------|----------|-------|
| `spring-boot-starter-web` | `spring-boot-starter-webmvc` | MVC applications |
| `spring-boot-starter-webflux` | `spring-boot-starter-webflux` | Unchanged |

### Security Starters

| Boot 3.x | Boot 4.x |
|----------|----------|
| `spring-boot-starter-security` | `spring-boot-starter-security` |
| `spring-boot-starter-oauth2-client` | `spring-boot-starter-security-oauth2-client` |
| `spring-boot-starter-oauth2-resource-server` | `spring-boot-starter-security-oauth2-resource-server` |

### Testing Starters

| Boot 3.x | Boot 4.x | Notes |
|----------|----------|-------|
| `spring-boot-starter-test` | Technology-specific test starters | Modular |
| - | `spring-boot-starter-webmvc-test` | Web layer tests |
| - | `spring-boot-starter-data-jpa-test` | Repository tests |
| - | `spring-boot-starter-json-test` | JSON tests |

### Compatibility Starters (Migration Aid)

For gradual migration, use classic starters:

```xml
<!-- Temporary migration aid -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-classic</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test-classic</artifactId>
    <scope>test</scope>
</dependency>
```

## Version Compatibility Rules

### Rule 1: Spring Boot and Spring Framework Must Match

| Spring Boot | Spring Framework |
|-------------|------------------|
| 4.0.x | 7.0.x |
| 3.5.x | 6.2.x |
| 3.4.x | 6.2.x |

**Verification**: Flag if Spring Framework version is explicitly overridden.

### Rule 2: Hibernate Must Match JPA Version

| Spring Boot | Hibernate | JPA |
|-------------|-----------|-----|
| 4.0.x | 7.x | 3.2 |
| 3.x | 6.x | 3.1 |

### Rule 3: Testing Dependencies Must Be Aligned

| Component | Boot 4 Version |
|-----------|----------------|
| JUnit | 5.11+ (JUnit 6 planned) |
| Mockito | 5.x |
| Testcontainers | 1.20+ |
| Spring Modulith | 2.0.x |

## Grep Patterns for Detection

```bash
# Jackson 2 imports (CRITICAL)
grep -r "com\.fasterxml\.jackson" --include="*.java" --include="*.kt"

# @MockBean usage (ERROR)
grep -r "@MockBean" --include="*.java" --include="*.kt"

# @SpyBean usage (ERROR)
grep -r "@SpyBean" --include="*.java" --include="*.kt"

# Undertow dependency (ERROR)
grep -r "spring-boot-starter-undertow" pom.xml build.gradle*

# Old security annotations (ERROR)
grep -r "@EnableGlobalMethodSecurity" --include="*.java" --include="*.kt"

# WebSecurityConfigurerAdapter (ERROR)
grep -r "WebSecurityConfigurerAdapter" --include="*.java" --include="*.kt"
```
