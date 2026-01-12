# Spring Boot Verification Troubleshooting

Common issues encountered during project verification.

## Table of Contents

- [Build File Detection Issues](#build-file-detection-issues)
- [Version Detection Issues](#version-detection-issues)
- [False Positives](#false-positives)
- [Configuration Parsing Issues](#configuration-parsing-issues)
- [Multi-Module Projects](#multi-module-projects)

---

## Build File Detection Issues

### Issue: Build File Not Found

**Symptom**: Verification fails to detect project type

**Causes**:
- Non-standard project structure
- Build file in subdirectory
- Multi-module project with root pom missing

**Solution**:
Specify the build file location explicitly:
```
Verify Spring Boot project at ./backend/pom.xml
```

Or use Glob to find all build files:
```bash
# Find all Maven projects
find . -name "pom.xml" -type f

# Find all Gradle projects
find . -name "build.gradle*" -type f
```

---

### Issue: Gradle Wrapper vs Direct Gradle

**Symptom**: Different dependency versions reported than expected

**Cause**: Gradle wrapper uses a different Gradle version than system Gradle

**Solution**:
Check Gradle version in `gradle/wrapper/gradle-wrapper.properties`:
```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.14-bin.zip
```

For Boot 4 compatibility, ensure Gradle 8.14+.

---

### Issue: Both Maven and Gradle Present

**Symptom**: Conflicting dependency information

**Cause**: Project has both `pom.xml` and `build.gradle`

**Solution**:
Ask which build system is primary:
- Check CI/CD pipeline for which is used
- Check `.gitignore` for which artifacts are ignored
- Look for wrapper scripts (`mvnw` vs `gradlew`)

---

## Version Detection Issues

### Issue: Spring Boot Version Not Detected

**Symptom**: Unable to determine Spring Boot version

**Causes**:
- Version defined in parent POM
- Version in Gradle version catalog
- Version in properties file

**Maven - Check parent or properties**:
```xml
<!-- In pom.xml -->
<parent>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.0.1</version>
</parent>

<!-- Or in properties -->
<properties>
    <spring-boot.version>4.0.1</spring-boot.version>
</properties>
```

**Gradle - Check version catalog** (`gradle/libs.versions.toml`):
```toml
[versions]
spring-boot = "4.0.1"

[plugins]
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }
```

**Gradle - Check settings.gradle.kts**:
```kotlin
pluginManagement {
    plugins {
        id("org.springframework.boot") version "4.0.1"
    }
}
```

---

### Issue: Dependency Version Conflicts

**Symptom**: Multiple versions of same dependency detected

**Cause**: Transitive dependency conflicts

**Solution - Maven**:
Use dependency management to enforce versions:
```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>4.0.1</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

**Solution - Gradle**:
```kotlin
dependencyManagement {
    imports {
        mavenBom("org.springframework.boot:spring-boot-dependencies:4.0.1")
    }
}
```

---

### Issue: Spring Framework Version Override

**Symptom**: Spring Boot version is 4.x but Spring Framework shows 6.x

**Cause**: Explicit Spring Framework version override in dependencies

**Detection**:
```bash
# Maven
grep -r "spring-framework.version" pom.xml
grep -r "spring.version" pom.xml

# Gradle
grep -r "org.springframework:spring-" build.gradle*
```

**Solution**: Remove explicit Spring Framework versions; let Boot manage them.

---

## False Positives

### Issue: Jackson 2 Detected in Non-Production Code

**Symptom**: Jackson 2 warning for test utilities or legacy code

**Cause**: Test fixtures or deprecated modules still using Jackson 2

**Solution**:
If Jackson 2 is intentionally used (e.g., testing both versions):
- Note this in verification scope
- Exclude specific directories from analysis:
```bash
# Exclude test utilities
grep -r "com\.fasterxml\.jackson" --include="*.java" \
  --exclude-dir="**/testutil" --exclude-dir="**/legacy"
```

---

### Issue: Security `and()` Detected in Comments

**Symptom**: False positive for `and()` method in documentation comments

**Cause**: Pattern matching includes comments and strings

**Solution**:
The verification should check for actual method calls:
```bash
# More precise pattern (excludes common false positives)
grep -r "\.and()" --include="*.java" | grep -v "//" | grep -v "\*"
```

For accurate detection, read the file and analyze the AST or context.

---

### Issue: @MockBean in Commented Code

**Symptom**: @MockBean warning for commented-out test code

**Cause**: Pattern matching doesn't distinguish active vs commented code

**Solution**:
Review flagged lines manually:
```bash
# Check if line is commented
grep -n "@MockBean" src/test/**/*.java | grep -v "^\s*//"
```

---

## Configuration Parsing Issues

### Issue: Multi-Profile Configuration

**Symptom**: Missing configuration issues in profile-specific files

**Cause**: Verification only checking `application.yml`, not `application-{profile}.yml`

**Solution**:
Request verification of all profiles:
```
Verify configuration for all profiles: default, dev, staging, production
```

List all profile files:
```bash
ls -la src/main/resources/application*.yml
ls -la src/main/resources/application*.properties
```

---

### Issue: YAML vs Properties Format Mismatch

**Symptom**: Configuration found in one format but not the other

**Cause**: Property keys differ between YAML and Properties formats

**Reference**: Spring Boot treats these as equivalent:
```yaml
# YAML
spring:
  datasource:
    url: jdbc:postgresql://localhost/db
```
```properties
# Properties
spring.datasource.url=jdbc:postgresql://localhost/db
```

---

### Issue: Externalized Configuration

**Symptom**: Configuration values not found in project files

**Cause**: Configuration loaded from:
- Environment variables
- Command line arguments
- External config server
- Kubernetes ConfigMaps/Secrets

**Solution**:
Check for configuration sources:
```yaml
# application.yml - using environment variable
spring:
  datasource:
    url: ${DATABASE_URL}
    password: ${DB_PASSWORD}
```

Note externalized values in verification report.

---

## Multi-Module Projects

### Issue: Parent POM Version Not Propagated

**Symptom**: Child modules show incorrect version

**Cause**: Child modules override parent version or use independent versioning

**Solution**:
Check each module's pom.xml:
```xml
<!-- Parent POM -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.0.1</version>
</parent>

<!-- Child should inherit, not override -->
<parent>
    <groupId>com.example</groupId>
    <artifactId>parent</artifactId>
    <version>1.0.0</version>
</parent>
<!-- No spring-boot version here - inherited from parent -->
```

---

### Issue: Mixed Spring Boot Versions Across Modules

**Symptom**: Different modules report different Spring Boot versions

**Cause**: Independent module versioning or stale dependencies

**Solution**:
1. Verify all modules use same parent
2. Check for explicit version overrides
3. Run dependency tree analysis:
```bash
# Maven
mvn dependency:tree | grep spring-boot

# Gradle
./gradlew dependencies | grep spring-boot
```

---

### Issue: Shared Test Utilities with @MockBean

**Symptom**: Test utilities module using @MockBean that's shared across modules

**Cause**: Centralized test fixtures haven't been updated

**Solution**:
Update shared test utilities first:
```java
// shared-test-utils/src/main/java/com/example/test/MockConfig.java
// Before
@MockBean private SomeService service;

// After
@MockitoBean private SomeService service;
```

Then update all dependent modules.

---

## Verification Tool Issues

### Issue: Grep Pattern Too Broad

**Symptom**: Too many false positives

**Solution**: Use more specific patterns:
```bash
# Too broad
grep "and()" *.java

# Better - method chain context
grep -E "\.and\(\)" --include="*.java"

# Best - with exclusions
grep -E "\.and\(\)" --include="*.java" \
  --exclude-dir="target" \
  --exclude-dir="build" \
  --exclude-dir=".git"
```

---

### Issue: Large Codebase Performance

**Symptom**: Verification takes too long

**Solution**:
1. Focus on specific directories:
```bash
# Only check src/main and src/test
grep -r "pattern" src/main src/test
```

2. Use parallel execution:
```bash
find . -name "*.java" | xargs -P 4 grep "pattern"
```

3. Exclude generated code:
```bash
grep -r "pattern" --exclude-dir="target" --exclude-dir="build" --exclude-dir="generated"
```

---

## Using Exa MCP for Latest Documentation

When verification encounters edge cases not covered in reference docs, use Exa MCP:

```
Use Exa MCP to search for: "Spring Boot 4 [specific issue]"
```

Examples:
- "Spring Boot 4 Jackson 3 migration guide"
- "Spring Security 7 Lambda DSL examples"
- "Spring Boot 4 Testcontainers @ServiceConnection"
