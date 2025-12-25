---
description: Comprehensive Spring Boot implementation review against DDD, security, testing, and other best practices
argument-hint: <scope: "all", module name, or natural language description>
---

# Spring Boot Review

Review a Spring Boot codebase for correct implementation against all spring-boot skills.

## Scope

$ARGUMENTS

## Instructions

Use the Task tool to invoke the `spring-boot-reviewer` agent with the scope above.

The agent will:
1. Parse the scope (or ask if not provided)
2. Detect Spring Boot version from build files
3. Review against all 8 spring-boot skills:
   - domain-driven-design
   - spring-boot-data-ddd
   - spring-boot-web-api
   - spring-boot-modulith
   - spring-boot-security
   - spring-boot-observability
   - spring-boot-testing
   - spring-boot-verify
4. Report findings with confidence scores (only ≥80 reported)
5. Offer to fix issues interactively

## Example Scopes

- `all` — Review entire project
- `the order module` — Review order-related code
- `security configuration` — Review security setup
- `controllers` — Review all controllers
- `com.example.order` — Review specific package
- `src/main/java/.../OrderController.java` — Review specific file
