# Troubleshooting: Spring Boot Tooling Scanner

## Scanner Reports Empty Results

### No build file found

**Symptom**: `"error": "no_build_file"` in output

**Causes**:
- Running from wrong directory (not project root)
- Monorepo where the Spring Boot app is nested
- Non-standard build file location

**Fix**: Check `nearby_build_files` in the error output for hints, or pass the correct path:
```bash
python3 scan_tooling.py /absolute/path/to/project-root
```

For monorepos, use `--recursive`:
```bash
python3 scan_tooling.py --recursive /path/to/monorepo
```

### Tools configured but not detected

**Symptom**: A tool is configured in the project but doesn't appear in `detected_tools`

**Common causes**:

1. **Convention plugin / buildSrc**: Tool configured in `buildSrc/src/main/kotlin/` or a Gradle convention plugin rather than directly in `build.gradle.kts`. The scanner only reads `build.gradle.kts`, `build.gradle`, and `pom.xml`.

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

## Monorepo Scanning

**Symptom**: Scanner finds tools only in root, misses subproject configurations

**Default behavior**: The scanner reads:
1. Root `build.gradle.kts` / `build.gradle`
2. `settings.gradle.kts` for `include()` declarations
3. Each included module's build file

**For monorepos with deeply nested projects**, use `--recursive`:
```bash
python3 scan_tooling.py --recursive /path/to/monorepo
```

This walks all directories (skipping `build/`, `.gradle/`, `node_modules/`, `.git/`, `target/`, `out/`, `.idea/`) and reports a `modules` section listing each discovered module with its tools.

**Alternative**: Run scanner directly on the subproject:
```bash
python3 scan_tooling.py /path/to/monorepo/services/order-service
```

## Tool Status Interpretation

The scanner reports a `status` field for each detected tool:

| Status | Meaning |
|--------|---------|
| `active` | Found in build file, not commented out |
| `disabled` | Found in build file but inside a comment block |
| `config-only` | Config file exists (e.g., `detekt.yml`) but no build-file plugin reference |
| `version-unknown` | Detected but version could not be extracted |

### Tool Reported as "disabled" Incorrectly

**Symptom**: Scanner reports status `disabled` for a tool that is active

**Causes**:
- Tool reference appears in a comment on a different line than the actual declaration (scanner found the comment first)
- Nested block comments (`/* /* */ */`) — scanner counts open/close markers but doesn't handle nesting

**Resolution**: Check the build file manually and verify the tool's actual status. The scanner picks up the first regex match — if a comment mentions the tool before the actual declaration, it may report `disabled`.

### Tool Reported as "config-only"

**Symptom**: Scanner reports `config-only` for a tool that has a build plugin

**Causes**:
- Plugin configured in `buildSrc/` or a convention plugin (not scanned)
- Plugin name uses a non-standard alias in the version catalog

**Resolution**: See "Tools configured but not detected" above.

## False Positives

**Symptom**: Scanner detects a tool that isn't actually configured

**Causes**:
- Tool name appears in comments or documentation within build files
- Transitive dependency brings in the tool (e.g., Hamcrest via JUnit 4 compat)
- Old configuration that was commented out but not removed

**Resolution**: Check the `status` field — `disabled` indicates the scanner detected it was commented out. For transitive dependencies, verify the build file directly.

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

## Lefthook Issues

### `lefthook: command not found`

**Causes**:
- Lefthook not installed

**Fix**: Install as npm devDep or system binary:
```bash
pnpm add -D lefthook    # npm devDep (recommended for monorepos)
brew install lefthook    # system binary (alternative)
```

### Hooks not running on commit

**Symptom**: Commit succeeds without triggering any hooks

**Causes**:
- `npx lefthook install` was not run after setup or clone
- Another hook manager (Husky) overriding `core.hooksPath`

**Fix**:
```bash
# Install hooks into .git/hooks/
npx lefthook install

# Check if Husky set a custom hooks path
git config core.hooksPath
# If set to .husky, reset it:
git config --unset core.hooksPath
```

### Husky/pre-commit conflict

**Symptom**: Scanner detects Husky or pre-commit alongside lefthook

**Fix**: Remove the old hook manager before installing lefthook:
```bash
# Remove Husky
rm -rf .husky
git config --unset core.hooksPath
npm uninstall husky

# Remove pre-commit
rm .pre-commit-config.yaml
pre-commit uninstall

# Then install lefthook
npx lefthook install
```

### Gitleaks not installed

**Symptom**: `gitleaks: command not found` when hooks run

**Fix**: Gitleaks is a system binary, not an npm package:
```bash
brew install gitleaks
gitleaks version  # verify
```

### Lefthook glob not matching files

**Symptom**: Hook shows "(skip) no files for inspection" even with staged Kotlin files

**Cause**: Globs in `lefthook.yml` are resolved from the **git repo root**, not from the `root:` directive.

**Fix**: Use full paths from repo root:
```yaml
# CORRECT — full path from repo root
ktlint:
  glob: "apps/api/**/*.{kt,kts}"
  root: "apps/api/"
  run: ./gradlew ktlintCheck

# WRONG — relative to root, will match nothing
ktlint:
  glob: "**/*.{kt,kts}"  # matches ALL .kt files, not just api
  root: "apps/api/"
```

## Research Documents Not Fetchable

**Symptom**: WebFetch returns 404 or network error for research docs

**URLs to verify**:
- `https://raw.githubusercontent.com/joaquimscosta/arkhe-claude-plugins/main/docs/research/jvm-quality-tools-evaluation.md`
- `https://raw.githubusercontent.com/joaquimscosta/arkhe-claude-plugins/main/docs/research/kotlin-spring-boot-testing-ecosystem.md`

**Causes**:
- Network connectivity issue
- Files were moved or renamed in the repository
- Repository is private (raw.githubusercontent.com requires public repo or auth token)

**Fallback**: Proceed with scanner results + LLM knowledge. The research docs enrich recommendations with specific versions and sourced rationale but are not required for the audit to work.
