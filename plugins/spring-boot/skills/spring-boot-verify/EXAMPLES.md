# Spring Boot Verification Examples

Complete verification examples demonstrating all output patterns.

## Table of Contents

- [Maven Project Verification](#maven-project-verification)
- [Gradle Project Verification](#gradle-project-verification)
- [Configuration Verification](#configuration-verification)
- [Security Configuration Audit](#security-configuration-audit)
- [Migration Readiness Assessment](#migration-readiness-assessment)

---

## Maven Project Verification

### Example: Spring Boot 3.x Project Needing Migration

**Input**: `pom.xml` with Spring Boot 3.x dependencies

**Verification Output**:

```markdown
## Spring Boot 4.x Verification Report

**Generated**: 2025-12-22T10:30:00Z
**Project**: my-application
**Location**: /Users/dev/projects/my-application

---

### Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 2 |
| ERROR | 3 |
| WARNING | 2 |

**Status**: BLOCKED - Critical issues must be resolved before upgrading

---

### Critical Issues

#### [1] Spring Boot Version Outdated
- **Severity**: CRITICAL
- **Category**: Dependencies
- **Current**: 3.2.5
- **Required**: 4.0.0+

**Remediation**:
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.0.1</version>
</parent>
```

#### [2] Jackson 2.x Detected
- **Severity**: CRITICAL
- **Category**: Dependencies
- **Issue**: Using `com.fasterxml.jackson` namespace
- **Impact**: Jackson 3 uses `tools.jackson` namespace

**Files affected**:
- `src/main/java/com/example/config/JacksonConfig.java`
- `src/main/java/com/example/util/JsonUtils.java`

**Remediation**:
Update all imports:
```java
// Before
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;

// After
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.core.JacksonException;
```

---

### Errors

#### [3] @MockBean Usage Detected
- **Severity**: ERROR
- **Category**: Testing
- **Location**: `src/test/java/com/example/UserServiceTest.java:25`

**Before**:
```java
@MockBean
private UserRepository userRepository;
```

**After**:
```java
@MockitoBean
private UserRepository userRepository;
```

#### [4] WebSecurityConfigurerAdapter Detected
- **Severity**: ERROR
- **Category**: Security
- **Location**: `src/main/java/com/example/config/SecurityConfig.java:15`

**Before**:
```java
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        // ...
    }
}
```

**After**:
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        // Lambda DSL configuration
        return http.build();
    }
}
```

#### [5] Java Version Below Minimum
- **Severity**: ERROR
- **Category**: Dependencies
- **Current**: 11
- **Required**: 17 (minimum)

**Remediation**:
```xml
<properties>
    <java.version>17</java.version>
</properties>
```

---

### Warnings

#### [6] Using spring-boot-starter-web
- **Severity**: WARNING
- **Category**: Dependencies
- **Issue**: Modular starters available in Boot 4

**Remediation**:
```xml
<!-- Before -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- After -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webmvc</artifactId>
</dependency>
```

#### [7] All Actuator Endpoints Exposed
- **Severity**: WARNING
- **Category**: Configuration
- **Location**: `src/main/resources/application.yml:12`

**Current**:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"
```

**Recommended**:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics,prometheus"
```

---

### Migration Checklist

- [ ] Upgrade Spring Boot version to 4.0.1
- [ ] Migrate Jackson 2 to Jackson 3 namespace
- [ ] Replace @MockBean with @MockitoBean in tests
- [ ] Convert SecurityConfig to SecurityFilterChain bean
- [ ] Upgrade Java version to 17+
- [ ] Update to modular starters
- [ ] Restrict actuator endpoint exposure
```

---

## Gradle Project Verification

### Example: Kotlin DSL Build File

**Input**: `build.gradle.kts` analysis

**Verification Output**:

```markdown
## Spring Boot 4.x Verification Report

**Generated**: 2025-12-22T11:00:00Z
**Project**: kotlin-service
**Build System**: Gradle (Kotlin DSL)

---

### Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| ERROR | 2 |
| WARNING | 1 |

**Status**: READY WITH ERRORS - Errors must be fixed

---

### Errors

#### [1] Incompatible Kotlin Version
- **Severity**: ERROR
- **Category**: Dependencies
- **Current**: kotlin("jvm") version "1.9.22"
- **Required**: 2.2.0+ for Spring Boot 4

**Remediation**:
```kotlin
plugins {
    kotlin("jvm") version "2.2.0"
    kotlin("plugin.spring") version "2.2.0"
}
```

#### [2] @SpyBean Usage Detected
- **Severity**: ERROR
- **Category**: Testing
- **Location**: `src/test/kotlin/com/example/AuditServiceTest.kt:18`

**Before**:
```kotlin
@SpyBean
private lateinit var auditService: AuditService
```

**After**:
```kotlin
@MockitoSpyBean
private lateinit var auditService: AuditService
```

---

### Warnings

#### [3] 100% Trace Sampling Configured
- **Severity**: WARNING
- **Category**: Configuration
- **Location**: `src/main/resources/application.yml:25`

**Current**:
```yaml
management:
  tracing:
    sampling:
      probability: 1.0
```

**Recommended for production**:
```yaml
management:
  tracing:
    sampling:
      probability: 0.1  # 10% in production
```
```

---

## Configuration Verification

### Example: application.yml Analysis

**Input**:
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    password: secret123
management:
  endpoints:
    web:
      exposure:
        include: "*"
  tracing:
    sampling:
      probability: 1.0
logging:
  level:
    root: DEBUG
```

**Verification Output**:

```markdown
## Spring Boot 4.x Verification Report

**File**: src/main/resources/application.yml

---

### Warnings

#### [1] All Actuator Endpoints Exposed
- **Severity**: WARNING
- **Location**: Line 7
- **Issue**: `include: "*"` exposes all endpoints
- **Risk**: Security vulnerability in production

**Remediation**:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics,prometheus"
    access:
      default: none  # Boot 4 opt-in approach
```

#### [2] 100% Trace Sampling
- **Severity**: WARNING
- **Location**: Line 11
- **Issue**: `probability: 1.0` samples all requests
- **Impact**: Performance overhead and storage costs

**Remediation**:
```yaml
management:
  tracing:
    sampling:
      probability: 0.1  # 10% in production
```

#### [3] Hardcoded Database Password
- **Severity**: WARNING
- **Location**: Line 4
- **Issue**: Secrets should not be in configuration files

**Remediation**:
```yaml
spring:
  datasource:
    password: ${DB_PASSWORD}  # Use environment variable
```

#### [4] DEBUG Logging in Default Profile
- **Severity**: WARNING
- **Location**: Line 14
- **Issue**: DEBUG level inappropriate for production

**Remediation**:
Create profile-specific logging:
```yaml
# application-prod.yml
logging:
  level:
    root: INFO
```
```

---

## Security Configuration Audit

### Example: Legacy Security Configuration

**Input**: SecurityConfig.java with deprecated patterns

**Verification Output**:

```markdown
## Spring Boot 4.x Verification Report

**File**: src/main/java/com/example/config/SecurityConfig.java

---

### Critical Issues

#### [1] Deprecated `and()` Chaining
- **Severity**: CRITICAL
- **Location**: Line 25
- **Issue**: `and()` method removed in Security 7

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

---

### Errors

#### [2] Deprecated antMatchers()
- **Severity**: ERROR
- **Location**: Line 18
- **Issue**: `antMatchers()` replaced with `requestMatchers()`

**Before**:
```java
.antMatchers("/public/**").permitAll()
.antMatchers("/api/admin/**").hasRole("ADMIN")
```

**After**:
```java
.requestMatchers("/public/**").permitAll()
.requestMatchers("/api/admin/**").hasRole("ADMIN")
```

#### [3] Deprecated authorizeRequests()
- **Severity**: ERROR
- **Location**: Line 16
- **Issue**: `authorizeRequests()` replaced with `authorizeHttpRequests()`

**Before**:
```java
http.authorizeRequests()
```

**After**:
```java
http.authorizeHttpRequests(auth -> auth
    // rules
)
```

#### [4] @EnableGlobalMethodSecurity Deprecated
- **Severity**: ERROR
- **Location**: Line 8
- **Issue**: Use `@EnableMethodSecurity` instead

**Before**:
```java
@EnableGlobalMethodSecurity(prePostEnabled = true)
```

**After**:
```java
@EnableMethodSecurity(prePostEnabled = true)
```
```

---

## Migration Readiness Assessment

### Example: Full Project Assessment

**Verification Output**:

```markdown
## Spring Boot 4.x Migration Readiness Assessment

**Project**: enterprise-app
**Current Version**: Spring Boot 3.2.5
**Target Version**: Spring Boot 4.0.1

---

### Overall Score: 45/100

**Status**: BLOCKED - Critical issues prevent migration

---

### Migration Blockers (Must Fix Before Upgrade)

| # | Issue | Files Affected | Effort |
|---|-------|----------------|--------|
| 1 | Upgrade Spring Boot to 4.0.x | pom.xml | 1h |
| 2 | Migrate Jackson 2 to Jackson 3 | 12 files | 4h |
| 3 | Convert Security config to Lambda DSL | 3 files | 4h |
| 4 | Replace @MockBean with @MockitoBean | 45 tests | 2h |
| 5 | Upgrade Java from 11 to 17 | pom.xml, CI | 2h |

---

### Required Changes (Will Cause Failures)

| # | Issue | Files Affected | Effort |
|---|-------|----------------|--------|
| 6 | Replace antMatchers with requestMatchers | 3 files | 1h |
| 7 | Replace authorizeRequests() | 3 files | 1h |
| 8 | Add @AutoConfigureMockMvc to tests | 15 tests | 1h |
| 9 | Update Kotlin to 2.2.0 | build.gradle.kts | 30m |

---

### Recommended Changes (Should Fix)

| # | Issue | Files Affected | Effort |
|---|-------|----------------|--------|
| 10 | Use modular starters | pom.xml | 30m |
| 11 | Enable virtual threads | application.yml | 15m |
| 12 | Configure JSpecify null-safety | 0 | Optional |
| 13 | Restrict actuator endpoints | application.yml | 30m |
| 14 | Add graceful shutdown | application.yml | 15m |

---

### Migration Checklist

**Dependencies**:
- [ ] Upgrade spring-boot-starter-parent to 4.0.1
- [ ] Update Java version to 17
- [ ] Update Kotlin to 2.2.0 (if applicable)
- [ ] Replace Jackson 2 imports with Jackson 3

**Security**:
- [ ] Convert SecurityConfig to use SecurityFilterChain bean
- [ ] Replace and() chaining with Lambda DSL
- [ ] Replace antMatchers() with requestMatchers()
- [ ] Replace authorizeRequests() with authorizeHttpRequests()
- [ ] Replace @EnableGlobalMethodSecurity with @EnableMethodSecurity

**Testing**:
- [ ] Replace @MockBean with @MockitoBean
- [ ] Replace @SpyBean with @MockitoSpyBean
- [ ] Add @AutoConfigureMockMvc to integration tests

**Configuration**:
- [ ] Update to modular starters (webmvc, etc.)
- [ ] Enable virtual threads (optional)
- [ ] Configure graceful shutdown
- [ ] Restrict actuator endpoint exposure

---

### Estimated Total Effort

| Area | Hours |
|------|-------|
| Dependencies | 3 |
| Security Config | 6 |
| Testing | 4 |
| Configuration | 2 |
| **Total** | **15 hours** |

---

### Next Steps

1. Create a feature branch for migration
2. Address CRITICAL issues first (blockers)
3. Run full test suite after each change
4. Use Spring Boot migration guide for edge cases
5. Deploy to staging for validation
```
