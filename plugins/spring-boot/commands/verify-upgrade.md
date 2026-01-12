---
description: Verify Spring Boot project upgrade readiness with parallel multi-skill analysis
argument-hint: [project path or scope]
---

# Spring Boot Upgrade Verification

Verify a Spring Boot project's readiness for upgrading to Spring Boot 4 using parallel multi-skill analysis.

## Scope

$ARGUMENTS

## Instructions

Use the Task tool to invoke the `spring-boot-upgrade-verifier` agent with the scope above.

The agent orchestrates a 3-phase verification:

**Phase 1: Discovery** (haiku)
- Detect build system (Maven/Gradle) and current Spring Boot version
- Identify Java version
- Determine which verification areas have files to check
- Skip verifiers with no matching files

**Phase 2: Parallel Verification** (sonnet agents)
- Launch skill-specific verifier agents IN PARALLEL
- Each verifier reads skill docs and checks assigned files
- Categorize findings by severity (Critical/Error/Warning)

**Phase 3: Migration Report**
- Consolidate findings from all verifiers
- Generate unified migration checklist
- Provide actionable remediation steps

## What Gets Verified

| Area | Checks |
|------|--------|
| **Dependencies** | Jackson 3 migration, Undertow removal, javax→jakarta |
| **Security** | Lambda DSL, requestMatchers, authorizeHttpRequests |
| **Testing** | @MockitoBean, Testcontainers 2.x, slice tests |
| **Observability** | Actuator limits, trace sampling, OpenTelemetry |

## Severity Levels

| Severity | Meaning |
|----------|---------|
| Critical | Blocks upgrade, must fix before proceeding |
| Error | Will break functionality after upgrade |
| Warning | Recommended for best practices |

## Example Usage

```bash
# Verify entire project
/verify-upgrade

# Verify specific module
/verify-upgrade the order module

# Verify from specific path
/verify-upgrade src/main/java/com/example/
```
