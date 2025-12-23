---
description: Verify Spring Boot project upgrade readiness including dependencies, configuration, and migration compatibility
---

# Spring Boot Project Verification

Analyze the current Spring Boot project and generate a comprehensive verification report.

## Verification Steps

1. **Detect Build System** - Find pom.xml or build.gradle and extract Spring Boot version
2. **Analyze Dependencies** - Check for deprecated libraries (Jackson 2.x, Undertow, javax.* packages)
3. **Validate Configuration** - Review application.yml/properties and security configuration
4. **Check Test Setup** - Identify deprecated test annotations (@MockBean, @SpyBean)
5. **Generate Report** - Produce structured report with severity levels and remediation steps

## Report Format

Generate a verification report with:
- Project summary (name, version, target version)
- Critical issues (must fix before upgrade)
- Errors (should fix for compatibility)
- Warnings (recommended improvements)
- Migration checklist with actionable steps

## Key Checks

| Category | What to Check |
|----------|---------------|
| Dependencies | Jackson namespace, Undertow removal, javax to jakarta |
| Security | Lambda DSL migration, requestMatchers, authorizeHttpRequests |
| Testing | @MockitoBean instead of @MockBean |
| Actuator | Endpoint exposure limits, sampling rates |

## Implementation

Invoke the Skill tool with skill name "spring-boot:spring-boot-verify" and arguments: `$ARGUMENTS`

The skill will handle build system detection, dependency analysis, configuration validation, and report generation.

For detailed documentation, see `spring-boot/skills/spring-boot-verify/SKILL.md`.
