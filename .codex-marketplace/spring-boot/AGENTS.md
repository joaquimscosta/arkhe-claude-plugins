# spring-boot — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

Domain-Driven Design with Spring Boot 4 (DDD patterns, Spring Data, REST APIs, Spring Modulith)

## Skills

- **domain-driven-design** — Expert guidance for Domain-Driven Design architecture and implementation. Use when designing complex business systems, defining bounded contexts, structuring domain models, choosing between modular m…
- **flyway-consolidate** — Analyze and consolidate Flyway SQL migrations into clean, domain-grouped CREATE TABLE migrations for pre-production projects. Use when consolidating database migrations, refactoring Flyway schemas, s…
- **spring-boot-data-ddd** — Spring Boot 4 data layer implementation for Domain-Driven Design. Use when implementing JPA or JDBC aggregates, Spring Data repositories, transactional services, projections, or entity auditing. Cove…
- **spring-boot-modulith** — Spring Modulith 2.0 implementation for bounded contexts in Spring Boot 4. Use when structuring application modules, implementing @ApplicationModuleListener for event-driven communication, testing wit…
- **spring-boot-observability** — Spring Boot 4 observability with Actuator, Micrometer, and OpenTelemetry. Use when configuring health indicators, health checks, custom metrics, distributed tracing, production endpoint exposure, Kub…
- **spring-boot-scanner** — Smart code scanner that detects Spring Boot patterns and routes to appropriate skills. Use when editing Java or Kotlin files in Spring Boot projects, working with pom.xml/build.gradle containing spri…
- **spring-boot-security** — Spring Security 7 implementation for Spring Boot 4. Use when configuring authentication, authorization, OAuth2/JWT resource servers, method security, or CORS/CSRF. Covers the mandatory Lambda DSL mig…
- **spring-boot-testing** — Spring Boot 4 testing strategies and patterns. Use when writing unit tests, slice tests (@WebMvcTest, @DataJpaTest), integration tests, Testcontainers with @ServiceConnection, security testing (@With…
- **spring-boot-verify** — Verify Spring Boot 4.x projects for correct dependencies, configuration, and migration readiness. Use when analyzing pom.xml, build.gradle, application.yml, discussing Spring Boot project setup, depe…
- **spring-boot-web-api** — Spring Boot 4 REST API implementation patterns. Use when creating REST controllers, REST endpoints, request validation, exception handlers with ProblemDetail (RFC 9457), API versioning, content negot…
- **spring-refresh** — Check Spring Boot skill content freshness against latest research and flag skills needing updates. Use when running /spring-refresh, or when user mentions "refresh spring skills", "spring boot update…

## Commands as Trigger Phrases

### When the user says "/spring-boot:spring-refresh" (args: "[check | refresh | update <skill-name>]")

Refresh Spring Boot research docs and check which skills need updating for the latest Spring Boot version

# Spring Boot Skill Refresh

Check Spring Boot skill freshness and update content when needed.

## Mode

$ARGUMENTS

## Instructions

Invoke the Skill tool with `spring-boot:spring-refresh` and the mode above.

The skill supports three modes:

**`check`** (default when no arguments)
- Runs the freshness scanner script
- Produces a report showing which research docs and skills are stale
- Recommends which skills need updating

**`refresh`**
- Updates all 3 Spring Boot research docs via deep-research skill
- Then runs `check` to show the updated freshness status
- Use when a new Spring Boot version has been released

**`update <skill-name>`**
- Reads relevant research docs and current skill content
- Identifies specific content that needs updating
- Proposes changes for your confirmation before editing

## Examples

```
/spring-refresh                              # Quick freshness check
/spring-refresh check                        # Same as above
/spring-refresh refresh                      # Update research docs + check
/spring-refresh update spring-boot-security  # Update a specific skill
```

### When the user says "/spring-boot:spring-review" (args: <scope: "all", module name, or natural language description>)

Comprehensive Spring Boot implementation review with smart skill detection and parallel execution

> **Note:** On Codex, this command runs inline; the agent it would invoke on Claude has been collapsed into the prompt body. Behavior is degraded — no parallel sub-execution.

# Spring Boot Review

Review a Spring Boot codebase using smart skill detection and parallel execution.

## Scope

$ARGUMENTS

## Instructions

Use the Agent tool to invoke the `spring-boot-reviewer` agent with the scope above.

The agent orchestrates a 3-phase review:

**Phase 1: Discovery** (haiku)
- Parse the scope and detect Spring Boot version
- Identify which skills are relevant based on files in scope
- Skip skills with no matching files

**Phase 2: Parallel Review** (sonnet agents)
- Launch skill-specific reviewer agents IN PARALLEL
- Each reviewer reads skill docs and checks assigned files
- Only reports issues with confidence ≥80

**Phase 3: Report**
- Consolidate findings from all reviewers
- Present unified report grouped by skill area
- Include fix suggestions for each finding

## Example Scopes

- `all` — Review entire project
- `the order module` — Review order-related code
- `security configuration` — Review security setup
- `controllers` — Review all controllers
- `com.example.order` — Review specific package
- `src/main/java/.../OrderController.java` — Review specific file

#### Inlined agent: `spring-boot:spring-boot-reviewer`

You are an **orchestrator** for Spring Boot code reviews. You delegate discovery and review work to specialized sub-agents, then consolidate findings into a unified report.

## Core Principles

- **Orchestrate, don't implement** — Delegate all analysis to sub-agents
- **Maximize parallelism** — Launch review agents simultaneously via the Agent tool
- **Use model tiers** — haiku for discovery, sonnet for review
- **Backpressure over prescription** — Define quality gates, let workers decide how to review
- **Report only** — Produce findings with fix suggestions; never apply fixes directly

---

## Phase 1: Discovery (haiku sub-agent)

Launch a **haiku** sub-agent to parse scope, detect the Spring Boot version, and identify which skills have matching files.

**Worker gets:** The user's scope (e.g., "all", a module name, a file path, or natural language like "security configuration").

**Quality gate — discovery output must include:**
- `spring_boot_version` — extracted from pom.xml or build.gradle
- `scope_interpreted` — what the user asked to review
- `relevant_skills` — list of skill names that have matching files in scope
- `files_by_skill` — map of skill name to file paths

**Stop condition:** If no Spring Boot project is detected (missing pom.xml/build.gradle), report and stop.

After discovery, report: "Found X relevant skills: [list]. Skipping Y skills (no matching files)."

---

## Phase 2: Parallel Review (sonnet sub-agents)

_…full agent body at `plugins/spring-boot/agents/spring-boot-reviewer.md` (symlinked into `skills/` for Codex)._

### When the user says "/spring-boot:verify-upgrade" (args: [project path or scope])

Verify Spring Boot project upgrade readiness with parallel multi-skill analysis

> **Note:** On Codex, this command runs inline; the agent it would invoke on Claude has been collapsed into the prompt body. Behavior is degraded — no parallel sub-execution.

# Spring Boot Upgrade Verification

Verify a Spring Boot project's readiness for upgrading to Spring Boot 4 using parallel multi-skill analysis.

## Scope

$ARGUMENTS

## Instructions

Use the Agent tool to invoke the `spring-boot-upgrade-verifier` agent with the scope above.

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

#### Inlined agent: `spring-boot:spring-boot-upgrade-verifier`

You are an **orchestrator** for Spring Boot upgrade verification. You delegate discovery and verification work to specialized sub-agents, then consolidate findings into an actionable migration report.

## Core Principles

- **Orchestrate, don't implement** — Delegate all analysis to sub-agents
- **Maximize parallelism** — Launch verifier agents simultaneously via the Agent tool
- **Use model tiers** — haiku for discovery, sonnet for verification
- **Backpressure over prescription** — Define quality gates, let workers decide how to verify
- **Actionable output** — Every finding must include a concrete migration action

---

## Phase 1: Discovery (haiku sub-agent)

Launch a **haiku** sub-agent to detect project info and determine which verification areas are relevant.

**Quality gate — discovery output must include:**
- `current_version` — from pom.xml or build.gradle
- `target_version` — 4.0.x (Spring Boot 4)
- `java_version` — from build config
- `build_system` — maven or gradle
- `relevant_verifiers` — list of verifier areas with matching files (spring-boot-verify always runs)
- `files_by_verifier` — map of verifier to file paths

**Stop condition:** If no build file found (missing pom.xml/build.gradle), report and stop.

After discovery, report: "Detected Spring Boot {version}. Running {X} verifiers: [list]. Skipping {Y} (no matching files)."

---

## Phase 2: Parallel Verification (sonnet sub-agents)

_…full agent body at `plugins/spring-boot/agents/spring-boot-upgrade-verifier.md` (symlinked into `skills/` for Codex)._
