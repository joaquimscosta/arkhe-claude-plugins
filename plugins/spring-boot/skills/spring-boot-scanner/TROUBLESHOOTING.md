# Spring Boot Scanner Troubleshooting

Common issues encountered during pattern detection and skill routing.

## Table of Contents

- [No Patterns Detected](#no-patterns-detected)
- [Project Not Recognized](#project-not-recognized)
- [Annotation Detection Issues](#annotation-detection-issues)
- [Script Execution Issues](#script-execution-issues)
- [False Positives and Negatives](#false-positives-and-negatives)

---

## No Patterns Detected

### Issue: "No Spring Boot patterns detected" for a Spring Boot project

**Symptom**: Scanner runs but reports no patterns in files that clearly use Spring annotations.

**Causes**:
- File extensions not recognized (e.g., `.kt` Kotlin files)
- Annotations using full package names instead of imports
- Non-standard directory structure
- Files excluded by scanning scope

**Solution**:

1. **Verify file extensions**: Scanner looks for `*.java` and `*.kt` files:
```bash
# Check if your files have correct extensions
ls -la src/**/*.java src/**/*.kt 2>/dev/null
```

2. **Check annotation format**: Scanner looks for `@AnnotationName`, not fully qualified:
```java
// ✅ Detected
@RestController
public class MyController {}

// ❌ NOT Detected (full package name)
@org.springframework.web.bind.annotation.RestController
public class MyController {}
```

3. **Run script directly for debugging**:
```bash
python3 scripts/detect_patterns.py src/main/java/com/example/MyController.java
```

---

### Issue: Patterns detected in some files but not others

**Symptom**: Scanner detects patterns in some files but misses others.

**Causes**:
- Non-recursive scan mode
- Files in unexpected locations
- Character encoding issues

**Solution**:

1. **Use recursive scanning**:
```bash
python3 scripts/detect_patterns.py . --recursive
```

2. **Check file encoding** (should be UTF-8):
```bash
file -i src/main/java/com/example/MyController.java
```

3. **Verify file permissions**:
```bash
ls -la src/main/java/com/example/MyController.java
```

---

## Project Not Recognized

### Issue: "Not a Spring Boot project" for valid project

**Symptom**: Scanner exits early claiming project isn't Spring Boot.

**Causes**:
- `pom.xml` or `build.gradle` not in expected location
- Non-standard dependency declaration
- Multi-module project structure

**Solution**:

1. **Check build file location**:
```bash
# Find all Maven projects
find . -name "pom.xml" -type f

# Find all Gradle projects
find . -name "build.gradle*" -type f
```

2. **Verify Spring Boot dependency exists**:
```bash
# Maven
grep -l "spring-boot-starter" **/pom.xml

# Gradle
grep -l "spring-boot\|org.springframework.boot" **/build.gradle*
```

3. **For multi-module projects**, run from the correct module:
```bash
python3 scripts/detect_patterns.py ./backend --recursive
```

---

### Issue: Build file detected but version not parsed

**Symptom**: Project recognized but version shows as `null`.

**Causes**:
- Version defined in parent POM
- Version in Gradle version catalog
- Version in gradle.properties

**Solution**:

Check alternative version locations:

**Maven** - parent or properties:
```xml
<parent>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.0.1</version>
</parent>
```

**Gradle** - version catalog (`gradle/libs.versions.toml`):
```toml
[versions]
spring-boot = "4.0.1"
```

---

## Annotation Detection Issues

### Issue: Custom/meta-annotations not detected

**Symptom**: Files with custom annotations (like `@ApiController`) not detected.

**Cause**: Scanner only detects standard Spring annotations.

**Solution**:

This is a known limitation. For custom annotations:

1. **Search for the custom annotation definition** to understand what it composes:
```bash
grep -r "@interface ApiController" src/
```

2. **Use grep directly** for custom patterns:
```bash
grep -l "@ApiController" **/*.java **/*.kt
```

3. **Add patterns to detect_patterns.py** if needed for your project.

---

### Issue: Annotations in comments detected as false positives

**Symptom**: Scanner reports patterns from commented-out code.

**Cause**: Simple regex matching includes comments.

**Solution**:

Review flagged files manually:
```bash
# Check context of detected pattern
grep -n "@RestController" src/main/java/com/example/MyController.java
```

The scanner intentionally errs on the side of detection—better to suggest a skill that may not be needed than miss one that is.

---

## Script Execution Issues

### Issue: "Permission denied" when running script

**Symptom**: `bash: permission denied` error.

**Solution**:
```bash
chmod +x scripts/detect_patterns.py
```

---

### Issue: "python3: command not found"

**Symptom**: Python not available in path.

**Solution**:

1. **Check Python installation**:
```bash
which python3
python3 --version  # Requires 3.8+
```

2. **Try alternative Python commands**:
```bash
python scripts/detect_patterns.py .
# or
/usr/bin/python3 scripts/detect_patterns.py .
```

---

### Issue: UnicodeDecodeError when scanning files

**Symptom**: Script crashes with encoding error.

**Cause**: File contains non-UTF-8 characters.

**Solution**:

1. **Identify problematic file**:
```bash
find . -name "*.java" -exec file {} \; | grep -v UTF-8
```

2. **Convert to UTF-8** if needed:
```bash
iconv -f ISO-8859-1 -t UTF-8 file.java > file_utf8.java
```

---

## False Positives and Negatives

### Issue: Too many skills suggested

**Symptom**: Scanner suggests 5+ skills for a simple file.

**Cause**: File contains patterns from multiple domains.

**Solution**:

This is expected behavior. The scanner detects all applicable patterns. Focus on:
- HIGH RISK skills (security, testing, verify) that require confirmation
- LOW RISK skills are informational only

---

### Issue: Wrong skill suggested

**Symptom**: Scanner suggests `spring-boot-data-ddd` for a service class.

**Cause**: Pattern overlap (e.g., `@Repository` can appear in different contexts).

**Solution**:

Consider the file's directory location:
- `**/domain/**` → `domain-driven-design` skill
- `**/repository/**` → `spring-boot-data-ddd` skill
- `**/controller/**` → `spring-boot-web-api` skill

The scanner provides suggestions; use judgment based on context.

---

### Issue: Missing escalation warnings

**Symptom**: Deprecated patterns not flagged.

**Cause**: Pattern not in escalation list or using different format.

**Solution**:

Escalation patterns are specific. Common variants that may not trigger:

| Detected | NOT Detected |
|----------|--------------|
| `@MockBean` | `@org.springframework.boot.test.mock.mockito.MockBean` |
| `.and()` | `and()` (without dot) |
| `antMatchers` | `ant_matchers` (different style) |

---

## Using Exa MCP for Edge Cases

When encountering issues not covered here, use Exa MCP for latest information:

```
Use Exa MCP to search for: "Spring Boot [specific issue]"
```

Examples:
- "Spring Boot 4 annotation detection patterns"
- "Spring Kotlin annotation processing"
- "Spring Boot custom annotation scanning"
