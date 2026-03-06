# Troubleshooting: Spring Boot Tooling Scanner

## Scanner Reports Empty Results

### No build file found

**Symptom**: `"build_tool": "unknown"` in output

**Causes**:
- Running from wrong directory (not project root)
- Multi-module project where build file is in a parent directory
- Non-standard build file location

**Fix**: Pass the correct project root path:
```bash
python3 scan_tooling.py /absolute/path/to/project-root
```

### Tools configured but not detected

**Symptom**: A tool is configured in the project but doesn't appear in `detected_tools`

**Common causes**:

1. **Convention plugin / buildSrc**: Tool configured in `buildSrc/src/main/kotlin/` or a Gradle convention plugin rather than directly in `build.gradle.kts`. The scanner only reads `build.gradle.kts`, `build.gradle`, and `pom.xml` at the root and direct submodule level.

   **Workaround**: Check `buildSrc/` manually:
   ```bash
   grep -r "detekt\|ktlint\|jacoco\|kover" buildSrc/
   ```

2. **Included build**: Tool configured in a composite build (`includeBuild("tools")` in `settings.gradle.kts`).

   **Workaround**: Run scanner on the included build directory separately.

3. **Profile-based Maven activation**: Tool in a Maven profile that isn't active by default.

   **Workaround**: Search the full POM:
   ```bash
   grep -A5 "pitest\|jacoco\|spotbugs" pom.xml
   ```

## Version Not Detected

**Symptom**: `"versions": { "tool": null }` for a tool that is present

**Causes**:
- Version managed by Spring Boot BOM (no explicit version in build file)
- Version defined in `gradle.properties` (not scanned)
- Version in parent POM (multi-module Maven)
- Version catalog key doesn't match expected name

**Workaround**: Check these locations manually:
```bash
# gradle.properties
grep -i "version" gradle.properties

# Version catalog
cat gradle/libs.versions.toml | head -30

# Parent POM
grep -A2 "<version>" pom.xml | head -20
```

## Multi-Module Projects

**Symptom**: Scanner only finds tools from root build file, missing submodule-specific tools

**How it works**: The scanner reads:
1. Root `build.gradle.kts` / `build.gradle`
2. `settings.gradle.kts` for `include()` declarations
3. Each included module's build file

**Limitation**: It does not recursively walk all directories. Only modules declared in `settings.gradle.kts` are checked.

**Workaround for deep nesting**: Run scanner on specific submodule:
```bash
python3 scan_tooling.py /path/to/project/apps/backend
```

## False Positives

**Symptom**: Scanner detects a tool that isn't actually configured

**Causes**:
- Tool name appears in comments or documentation within build files
- Transitive dependency brings in the tool (e.g., Hamcrest via JUnit 4 compat)
- Old configuration that was commented out but not removed

**Resolution**: The recommendation report will note these. During Phase 2 setup, verify the tool's actual status before making changes.

## Python Execution Issues

### Permission denied

```bash
chmod +x scripts/scan_tooling.py
```

### Python version too old

The scanner requires Python 3.8+. Check version:
```bash
python3 --version
```

### UnicodeDecodeError

Build file contains non-UTF-8 characters. The scanner uses `encoding="utf-8"`. If the project uses a different encoding, convert the file or report the issue.

## Research Documents Not Found

**Symptom**: Claude reports it cannot read the research documents

**Causes**:
- Research documents haven't been promoted to `docs/research/` yet
- File was renamed or moved

**Check**:
```bash
ls docs/research/jvm-quality-tools-evaluation.md
ls docs/research/kotlin-spring-boot-testing-ecosystem.md
```

If missing, use `/research promote <slug>` to promote from cache, or `/research <topic>` to generate fresh research.
