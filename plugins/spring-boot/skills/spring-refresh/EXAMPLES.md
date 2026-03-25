# Spring Refresh Examples

## Example 1: Basic Freshness Check

**Command:** `/spring-refresh` or `/spring-refresh check`

**Scenario:** You want to see which skills might have stale content.

**Output:**

```
## Spring Boot Skill Freshness Report

### Research Documents
| Document                             | Version | Updated    | Age  | Status   |
|--------------------------------------|---------|------------|------|----------|
| ecosystem-research.md                | 1.0.0   | 2026-03-07 | 17d  | AGING    |
| ddd-implementation.md                | 1.0.0   | 2026-03-07 | 17d  | AGING    |
| security-observability-testing.md    | 1.0.0   | 2026-03-07 | 17d  | AGING    |

### Skills
| Skill                   | Target | Modified   | Research   | Drift | Status       |
|-------------------------|--------|------------|------------|-------|--------------|
| spring-boot-security    | 4.0    | 2026-01-23 | 2026-03-07 | +42d  | NEEDS_UPDATE |
| spring-boot-web-api     | 4.0    | 2026-01-23 | 2026-03-07 | +42d  | NEEDS_UPDATE |
| domain-driven-design    | 4.0    | 2026-02-09 | 2026-03-07 | +25d  | NEEDS_REVIEW |
| spring-boot-scanner     | 4.0    | 2026-03-07 | 2026-03-07 | -1d   | UP_TO_DATE   |
| flyway-consolidate      | 4.0    | 2026-03-09 | -          | -     | NO_RESEARCH  |

### Summary
- 4 up to date, 1 needs review, 4 need update, 1 no research mapping

### Recommendations
- Run `/spring-refresh update spring-boot-security` to update security skill
- Run `/spring-refresh update spring-boot-web-api` to update web-api skill
- Consider running `/spring-refresh refresh` to update research docs first
```

## Example 2: Full Refresh Cycle

**Command:** `/spring-refresh refresh`

**Scenario:** A new Spring Boot 4.1 version was released and you want to update research docs and see what skills are affected.

**What happens:**
1. Deep-research skill refreshes all 3 Spring Boot research docs using EXA web search
2. Research docs in `docs/research/spring-boot/` are updated with latest findings
3. Freshness check runs with updated data
4. Report shows which skills now have drift against the new research

**Output includes:**

```
### Research Refresh Results
| Document                          | Before     | After      | Changed |
|-----------------------------------|------------|------------|---------|
| ecosystem-research.md             | 2026-03-07 | 2026-03-25 | Yes     |
| ddd-implementation.md             | 2026-03-07 | 2026-03-25 | Yes     |
| security-observability-testing.md | 2026-03-07 | 2026-03-25 | Yes     |

### Key Changes Detected
- Spring Boot 4.1 adds native structured concurrency support
- Spring Security 7.1 deprecates Argon2PasswordEncoder default
- Testcontainers 2.0 integration with @ServiceConnection enhanced

### Updated Freshness Report
(full report follows with new drift calculations)
```

## Example 3: Updating a Specific Skill

**Command:** `/spring-refresh update spring-boot-security`

**Scenario:** The freshness check showed spring-boot-security has 42 days of drift.

**What happens:**
1. Reads research doc: `security-observability-testing.md`
2. Reads skill content: SKILL.md, EXAMPLES.md, TROUBLESHOOTING.md, references/
3. Identifies differences between research and skill content
4. Proposes specific changes

**Output:**

```
## Drift Analysis: spring-boot-security

### Research Doc: security-observability-testing.md (updated 2026-03-25)

### Changes Detected
1. **New:** `.csrf(csrf -> csrf.spa())` — SPA-friendly CSRF in Security 7.1
   - Not covered in SKILL.md or references/SECURITY-CONFIG.md
   - Recommendation: Add to SECURITY-CONFIG.md CSRF section

2. **Updated:** Password encoder recommendation
   - Current: Argon2PasswordEncoder as default
   - Research: BCrypt remains recommended; Argon2 for high-security contexts only
   - Recommendation: Update SKILL.md anti-pattern checklist

3. **No change needed:** Lambda DSL migration table (already current)

### Proposed Updates
Shall I apply these changes? (y/n for each)
```

## Status Definitions

| Status | Drift Range | Meaning |
|--------|-------------|---------|
| `UP_TO_DATE` | 0 or negative | Skill was modified after research doc |
| `FRESH` | 1-7 days | Recently updated, likely current |
| `NEEDS_REVIEW` | 8-30 days | May have minor drift, worth checking |
| `NEEDS_UPDATE` | 31+ days | Significant drift, should be updated |
| `NO_RESEARCH` | N/A | No mapped research doc (e.g., flyway-consolidate) |
