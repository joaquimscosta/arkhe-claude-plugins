---
description: Comprehensive Spring Boot implementation review with smart skill detection and parallel execution
argument-hint: <scope: "all", module name, or natural language description>
---

# Spring Boot Review

Review a Spring Boot codebase using smart skill detection and parallel execution.

## Scope

$ARGUMENTS

## Instructions

Use the Task tool to invoke the `spring-boot-reviewer` agent with the scope above.

The agent orchestrates a 3-phase review:

**Phase 1: Discovery** (haiku)
- Parse the scope and detect Spring Boot version
- Identify which skills are relevant based on files in scope
- Skip skills with no matching files

**Phase 2: Parallel Review** (sonnet agents)
- Launch skill-specific reviewer agents IN PARALLEL
- Each reviewer reads skill docs and checks assigned files
- Only reports issues with confidence ≥80

**Phase 3: Report & Fix**
- Consolidate findings from all reviewers
- Present unified report grouped by skill area
- Offer interactive fix options

## Example Scopes

- `all` — Review entire project
- `the order module` — Review order-related code
- `security configuration` — Review security setup
- `controllers` — Review all controllers
- `com.example.order` — Review specific package
- `src/main/java/.../OrderController.java` — Review specific file
