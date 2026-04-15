---
name: spring-boot-scanner
description: "Smart code scanner that detects Spring Boot patterns and routes to appropriate skills. Use when editing Java or Kotlin files in Spring Boot projects, working with pom.xml/build.gradle containing spring-boot-starter, or when context suggests Spring Boot development. Detects annotations (@RestController, @Entity, @EnableWebSecurity, @SpringBootTest) to determine relevant skills and provides contextual guidance. Uses progressive automation - auto-invokes for low-risk patterns (web-api, data, DDD), confirms before loading high-risk skills (security, testing, verify)."
spring-boot-version: "4.0"
---

# Spring Boot Scanner

Smart pattern detection and skill routing for Spring Boot projects.

## Core Behavior

**Trigger Conditions**:
- Editing `*.java` or `*.kt` files in a project with `spring-boot-starter` dependencies
- Working with `pom.xml` or `build.gradle*` containing Spring Boot
- User mentions "Spring Boot", "Spring Security", "Spring Data", etc.

**Action**: Scan code → Detect patterns → Route to appropriate skill

## Detection Workflow

1. **Detect project**: Glob for `pom.xml`/`build.gradle*`, grep for `spring-boot-starter` or `org.springframework.boot` → exit if not Spring Boot
2. **Scan annotations**: Match current file against the annotation map below → collect `{skill, risk_level}` pairs
3. **Classify risk**: Separate LOW (auto-invoke guidance) from HIGH (confirm with user first)
4. **Route**: LOW-only → auto-invoke; HIGH-only → ask user; mixed → auto-invoke LOW, ask about HIGH; escalation patterns → show warning first

**Validation checkpoints**: Confirm project type before scanning. Never auto-invoke HIGH risk skills. Batch multiple LOW risk suggestions into a single response.

See [WORKFLOW.md](WORKFLOW.md) for the complete detection flow with response templates.

## Annotation → Skill Map

| Annotation Pattern | Detected Skill | Risk Level |
|-------------------|----------------|------------|
| `@RestController`, `@GetMapping`, `@PostMapping`, `@RequestMapping` | spring-boot-web-api | LOW |
| `@Entity`, `@Repository`, `@Aggregate`, `@MappedSuperclass` | spring-boot-data-ddd | LOW |
| `@Service` in `**/domain/**` or `**/service/**` | domain-driven-design | LOW |
| `@ApplicationModule`, `@ApplicationModuleListener` | spring-boot-modulith | LOW |
| `@Timed`, `@Counted`, `HealthIndicator`, `MeterRegistry` | spring-boot-observability | LOW |
| `@EnableWebSecurity`, `@PreAuthorize`, `@Secured`, `SecurityFilterChain` | spring-boot-security | HIGH |
| `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest`, `@MockitoBean` | spring-boot-testing | HIGH |
| `@MockBean` (deprecated) | spring-boot-testing | HIGH + WARNING |
| Build file with version < 4.0 | spring-boot-verify | HIGH |

Run `python3 scripts/detect_patterns.py /path/to/file.java` from the project root for programmatic detection.

## Escalation Triggers

Always confirm before proceeding when detecting:

| Pattern | Reason | Action |
|---------|--------|--------|
| `@EnableGlobalMethodSecurity` | Deprecated in Security 6+ | Confirm + Migration guidance |
| `@MockBean` | Deprecated in Boot 3.4+ | Confirm + Show @MockitoBean |
| `spring-boot-starter-parent` < 3.0 | Major migration needed | Confirm + Suggest verify-upgrade |
| `.and()` in security config | Removed in Security 7 | Confirm + Lambda DSL guidance |
| `com.fasterxml.jackson` | Jackson 3 migration | Confirm + Namespace change |

## Delegation

**To skills** (pattern-specific guidance): `spring-boot-web-api`, `spring-boot-data-ddd`, `spring-boot-security`, `spring-boot-testing`, `spring-boot-modulith`, `spring-boot-observability`, `spring-boot-verify`, `domain-driven-design`

**To agents** (comprehensive review): Delegate to `spring-boot-reviewer` or `spring-boot-upgrade-verifier` when the user asks for full project review, multiple HIGH RISK patterns span many files, or an explicit `/spring-review` or `/verify-upgrade` command is given.

## Response Examples

**LOW risk auto-invoke** (web-api detected):
> I noticed `@RestController` and `@GetMapping` in this file. Loading Spring Boot Web API guidance for endpoint best practices.

**HIGH risk confirmation** (security detected):
> I detected `@EnableWebSecurity` and `SecurityFilterChain` — this involves security configuration. Load Spring Boot Security skill for Spring Security 7 guidance? [Yes/No]

## Escape Hatch

This scanner is advisory — skip LOW suggestions by ignoring them, skip HIGH confirmations by selecting "No." For full project review, use `/spring-review`.

## References

- [WORKFLOW.md](WORKFLOW.md) — Detection flow with response templates
- [EXAMPLES.md](EXAMPLES.md) — Trigger scenarios and scanner responses
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common detection issues
- [scripts/detect_patterns.py](scripts/detect_patterns.py) — Programmatic detection script
