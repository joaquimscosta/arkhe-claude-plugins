# Spring Boot 4.x Configuration Validation Rules

Complete configuration validation rules for Spring Boot 4.x projects.

## Table of Contents

- [Security Configuration Rules](#security-configuration-rules)
  - [CRITICAL - Must Fix Immediately](#critical---must-fix-immediately)
  - [ERROR - Will Cause Failures](#error---will-cause-failures)
- [Actuator Configuration Rules](#actuator-configuration-rules)
  - [WARNING - Security Risk](#warning---security-risk)
  - [WARNING - Performance](#warning---performance)
  - [Boot 4 Specific - New Access Control Model](#boot-4-specific---new-access-control-model)
- [Application Properties Rules](#application-properties-rules)
  - [Virtual Threads Configuration](#virtual-threads-configuration)
  - [Graceful Shutdown (Required for Kubernetes)](#graceful-shutdown-required-for-kubernetes)
  - [Health Probes for Kubernetes](#health-probes-for-kubernetes)
  - [Jackson 3 Configuration](#jackson-3-configuration)
- [Testing Configuration Rules](#testing-configuration-rules)
  - [Rule: @AutoConfigureMockMvc Required](#rule-autoconfiguremockmvc-required)
  - [Rule: @MockitoBean Required (Not @MockBean)](#rule-mockitobean-required-not-mockbean)
- [Profile Configuration Rules](#profile-configuration-rules)
  - [Rule: Check All Profile Files](#rule-check-all-profile-files)
  - [WARNING: Secrets in Default Profile](#warning-secrets-in-default-profile)
  - [WARNING: Debug Settings in Production](#warning-debug-settings-in-production)
- [Grep Patterns for Configuration Detection](#grep-patterns-for-configuration-detection)

## Security Configuration Rules

### CRITICAL - Must Fix Immediately

#### Rule: Lambda DSL Required (No `and()` Chaining)

**Pattern to detect** (Grep):
```bash
grep -r "\.and()" --include="*.java" --include="*.kt"
```

**Deprecated**:
```java
http
    .authorizeRequests()
        .anyRequest().authenticated()
    .and()  // REMOVED IN SECURITY 7
    .oauth2ResourceServer()
        .jwt();
```

**Required**:
```java
http
    .authorizeHttpRequests(auth -> auth
        .anyRequest().authenticated()
    )
    .oauth2ResourceServer(oauth2 -> oauth2
        .jwt(Customizer.withDefaults())
    );
```

#### Rule: authorizeHttpRequests Required

**Pattern to detect**:
```bash
grep -r "authorizeRequests()" --include="*.java" --include="*.kt"
```

**Deprecated**: `.authorizeRequests()`
**Required**: `.authorizeHttpRequests()`

#### Rule: requestMatchers Required

**Patterns to detect**:
```bash
grep -r "antMatchers(" --include="*.java" --include="*.kt"
grep -r "mvcMatchers(" --include="*.java" --include="*.kt"
grep -r "regexMatchers(" --include="*.java" --include="*.kt"
```

**Deprecated**:
```java
.antMatchers("/api/**").permitAll()
.mvcMatchers("/api/**").authenticated()
.regexMatchers("/api/.*").hasRole("USER")
```

**Required**:
```java
.requestMatchers("/api/**").permitAll()
.requestMatchers(new AntPathRequestMatcher("/api/**")).authenticated()
.requestMatchers(new MvcRequestMatcher(introspector, "/api/{id}")).hasRole("USER")
```

### ERROR - Will Cause Failures

#### Rule: WebSecurityConfigurerAdapter Removed

**Pattern to detect**:
```bash
grep -r "WebSecurityConfigurerAdapter" --include="*.java" --include="*.kt"
```

**Deprecated**:
```java
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) { }
}
```

**Required**:
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        // configuration
        return http.build();
    }
}
```

#### Rule: Method Security Annotation Changed

**Pattern to detect**:
```bash
grep -r "@EnableGlobalMethodSecurity" --include="*.java" --include="*.kt"
```

**Deprecated**: `@EnableGlobalMethodSecurity(prePostEnabled = true)`
**Required**: `@EnableMethodSecurity(prePostEnabled = true)`

## Actuator Configuration Rules

### WARNING - Security Risk

#### Rule: Avoid Exposing All Endpoints

**Pattern to detect** in `application.yml`:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"  # WARNING: Security vulnerability
```

**Recommended**:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics,prometheus"
    access:
      default: none  # Opt-in approach (Boot 4)
  endpoint:
    health:
      show-details: when-authorized
```

#### Rule: Use Separate Management Port

**Recommended for production**:
```yaml
management:
  server:
    port: 8081  # Separate from application port
```

### WARNING - Performance

#### Rule: Avoid 100% Trace Sampling in Production

**Pattern to detect**:
```yaml
management:
  tracing:
    sampling:
      probability: 1.0  # WARNING: Performance overhead
```

**Recommended for production**:
```yaml
management:
  tracing:
    sampling:
      probability: 0.1  # 10% sampling
```

### Boot 4 Specific - New Access Control Model

**New in Boot 4**:
```yaml
management:
  endpoints:
    access:
      default: none  # Opt-in approach
  endpoint:
    health:
      access: unrestricted
    info:
      access: read-only
    metrics:
      access: read-only
    loggers:
      access: read-only
```

## Application Properties Rules

### Virtual Threads Configuration

**Recommended for Boot 4 (I/O-bound workloads)**:
```yaml
spring:
  threads:
    virtual:
      enabled: true  # Enable Project Loom virtual threads
```

### Graceful Shutdown (Required for Kubernetes)

**Required for production**:
```yaml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

### Health Probes for Kubernetes

**Recommended**:
```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
        add-additional-paths: true  # Exposes /livez and /readyz
      group:
        liveness:
          include: "livenessState,ping"
        readiness:
          include: "readinessState,db,redis"
```

### Jackson 3 Configuration

**New in Boot 4** (immutable configuration via JsonMapper):
```yaml
spring:
  jackson:
    default-property-inclusion: non-null
    date-format: "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
    serialization:
      write-dates-as-timestamps: false
```

## Testing Configuration Rules

### Rule: @AutoConfigureMockMvc Required

**Boot 4 change**: MockMvc no longer auto-configured in `@SpringBootTest`

**Pattern to detect** (missing annotation):
```java
@SpringBootTest
class MyTest {
    @Autowired MockMvc mockMvc;  // Will be null without @AutoConfigureMockMvc
}
```

**Required**:
```java
@SpringBootTest
@AutoConfigureMockMvc  // Required in Boot 4!
class MyTest {
    @Autowired MockMvc mockMvc;
}
```

### Rule: @MockitoBean Required (Not @MockBean)

**Pattern to detect**:
```bash
grep -r "@MockBean" --include="*.java" --include="*.kt"
grep -r "@SpyBean" --include="*.java" --include="*.kt"
```

**Deprecated**:
```java
@MockBean
private UserService userService;

@SpyBean
private AuditService auditService;
```

**Required**:
```java
@MockitoBean
private UserService userService;

@MockitoSpyBean
private AuditService auditService;
```

## Profile Configuration Rules

### Rule: Check All Profile Files

Verify these profile-specific files:
- `application.yml` (default)
- `application-dev.yml`
- `application-test.yml`
- `application-staging.yml`
- `application-prod.yml` / `application-production.yml`

### WARNING: Secrets in Default Profile

**Pattern to detect**:
```yaml
# application.yml - default profile
spring:
  datasource:
    password: prod-password  # WARNING: Hardcoded secret
```

**Recommended**:
```yaml
# application-prod.yml
spring:
  datasource:
    password: ${DB_PASSWORD}  # Environment variable
```

### WARNING: Debug Settings in Production

**Pattern to detect** (in prod profile):
```yaml
logging:
  level:
    root: DEBUG  # WARNING in production
    org.hibernate.SQL: DEBUG
    org.springframework.security: DEBUG
```

**Recommended for production**:
```yaml
logging:
  level:
    root: INFO
    org.hibernate.SQL: WARN
    org.springframework.security: WARN
```

## Grep Patterns for Configuration Detection

```bash
# Security patterns (CRITICAL/ERROR)
grep -r "\.and()" --include="*.java" --include="*.kt"
grep -r "authorizeRequests()" --include="*.java" --include="*.kt"
grep -r "antMatchers(" --include="*.java" --include="*.kt"
grep -r "WebSecurityConfigurerAdapter" --include="*.java" --include="*.kt"
grep -r "@EnableGlobalMethodSecurity" --include="*.java" --include="*.kt"

# Testing patterns (ERROR)
grep -r "@MockBean" --include="*.java" --include="*.kt"
grep -r "@SpyBean" --include="*.java" --include="*.kt"

# Configuration patterns (WARNING)
grep -r 'include:.*"\*"' --include="*.yml" --include="*.yaml"
grep -r "probability: 1.0" --include="*.yml" --include="*.yaml"
grep -r "level:.*DEBUG" --include="*-prod*.yml" --include="*-production*.yml"
```
