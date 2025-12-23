# Spring Boot 4.x Verification Workflow

Step-by-step guide for verifying Spring Boot projects for compatibility and migration readiness.

## Step 1: Detect Build System and Version

**Goal**: Identify the build system and extract Spring Boot version.

**Actions**:
```bash
# Find build files
Glob: **/pom.xml, **/build.gradle, **/build.gradle.kts
```

**Extract version from**:
- `pom.xml`: `<parent><version>` or `spring-boot.version` property
- `build.gradle`: `plugins { id 'org.springframework.boot' version 'X.X.X' }`

**Decision Point**:
- Version < 3.0 → Major migration required
- Version 3.x → Incremental upgrade path
- Version 4.x → Validate current setup

## Step 2: Analyze Dependencies

**Goal**: Identify deprecated or incompatible dependencies.

**Critical Checks**:

| Pattern to Search | Issue | Resolution |
|-------------------|-------|------------|
| `com.fasterxml.jackson` | Jackson 2.x (removed in Boot 4) | Migrate to `tools.jackson` |
| `spring-boot-starter-undertow` | Undertow removed | Use Tomcat or Jetty |
| `javax.` packages | Java EE namespace | Migrate to `jakarta.` |
| `springfox` or `swagger` | Old Swagger libs | Use `springdoc-openapi` |

**Grep Commands**:
```bash
Grep: com\.fasterxml\.jackson  # Jackson 2.x
Grep: javax\.(servlet|persistence|validation)  # Java EE
Grep: springfox|io\.swagger  # Old Swagger
```

## Step 3: Validate Configuration

**Goal**: Check application configuration for deprecated patterns.

**Files to Analyze**:
- `application.yml` / `application.properties`
- `SecurityConfiguration.java` or similar
- `WebMvcConfigurer` implementations

**Critical Configuration Checks**:

| Pattern | Issue | Resolution |
|---------|-------|------------|
| `management.endpoints.web.exposure.include: *` | All actuator exposed | Limit to `health,info,metrics` |
| `management.tracing.sampling.probability: 1.0` | 100% trace sampling | Use 0.1 (10%) in production |
| `.and()` in Security config | Removed in Security 7 | Use Lambda DSL closures |
| `antMatchers()` | Deprecated | Use `requestMatchers()` |
| `authorizeRequests()` | Deprecated | Use `authorizeHttpRequests()` |

**Grep Commands**:
```bash
Grep: \.and\(\)  # Security chaining
Grep: antMatchers|authorizeRequests  # Deprecated security methods
Grep: @MockBean  # Deprecated test annotation
```

## Step 4: Check Test Configuration

**Goal**: Identify deprecated test patterns.

**Critical Test Checks**:

| Pattern | Issue | Resolution |
|---------|-------|------------|
| `@MockBean` | Deprecated | Use `@MockitoBean` |
| `@SpyBean` | Deprecated | Use `@MockitoSpyBean` |
| `TestRestTemplate` | Legacy | Consider `WebTestClient` |

**Grep Command**:
```bash
Grep: @MockBean|@SpyBean  glob: **/*Test.java
```

## Step 5: Generate Verification Report

**Goal**: Produce actionable report with severity levels.

**Report Structure**:

```markdown
## Spring Boot 4.x Verification Report

### Summary
- **Project**: {name from pom.xml/build.gradle}
- **Current Version**: {detected version}
- **Target Version**: 4.0.x
- **Issues Found**: {n} Critical, {n} Errors, {n} Warnings

### Critical Issues
[Must fix before upgrade]

### Errors
[Should fix for compatibility]

### Warnings
[Recommended improvements]

### Migration Checklist
- [ ] Update Spring Boot version
- [ ] Migrate Jackson dependencies
- [ ] Update Security configuration
- [ ] Replace deprecated test annotations
- [ ] Review actuator exposure
```

## Step 6: Lookup Latest Documentation

**Goal**: Verify recommendations against official docs.

**Use Exa MCP** for latest information:
```
mcp__exa__web_search_exa: "Spring Boot 4.0 migration guide site:spring.io"
mcp__exa__web_search_exa: "Spring Security 7 lambda DSL site:spring.io"
```

**Official Resources**:
- https://docs.spring.io/spring-boot/documentation.html
- https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes

## Quick Reference

### Severity Definitions

| Severity | Meaning | Action |
|----------|---------|--------|
| CRITICAL | Blocks upgrade, runtime failure | Must fix immediately |
| ERROR | Compilation or test failure | Fix before upgrade |
| WARNING | Best practice violation | Recommended fix |
| INFO | Informational finding | Optional improvement |

### Common Migration Paths

**Jackson 2 to Jackson 3**:
```xml
<!-- Before -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>

<!-- After -->
<dependency>
    <groupId>tools.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

**Security Configuration**:
```java
// Before (Security 6)
http.authorizeRequests()
    .antMatchers("/public/**").permitAll()
    .and()
    .formLogin();

// After (Security 7)
http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/public/**").permitAll()
    )
    .formLogin(Customizer.withDefaults());
```

**Test Annotations**:
```java
// Before
@MockBean
private UserService userService;

// After
@MockitoBean
private UserService userService;
```
