# Workflow Orchestration Examples

Real-world scenarios demonstrating when and how to use orchestration tools.

## Example 1: Feature Implementation

**User request:**
> "I need to add user authentication with JWT tokens to my Express app"

**Analysis:**
- Multi-step project with several components
- Can parallelize some work (routes, middleware, tests)
- Needs research for best practices
- Benefits from validation

**Recommendation:**
```bash
/develop implement user authentication with JWT tokens --validate
```

**Why:** This is a multi-agent task with parallel opportunities. The `--validate` flag ensures security is properly reviewed with deep opus-level validation.

**Execution flow:**
1. Gate: Clear request, proceed
2. Context: Find existing auth patterns, routes, middleware
3. Plan: Research JWT patterns, identify parallel tasks
4. Execute:
   - Wave 1: Auth middleware, JWT utilities (parallel)
   - Wave 2: Login/logout routes, token refresh (parallel)
   - Wave 3: Integration, error handling
5. Validate: Security review, test coverage check
6. Report: Summary of implemented auth system

---

## Example 2: Complex Debugging

**User request:**
> "My API is returning intermittent 500 errors and I can't figure out why"

**Analysis:**
- Single problem needing deep investigation
- Requires hypothesis formation and testing
- Benefits from structured debugging approach

**Recommendation:**
```bash
/debug intermittent 500 errors in the API
```

Or for deeper analysis:
```bash
/think investigate the intermittent 500 errors - what could cause sporadic failures?
```

**Why:** This is a single complex problem, not a multi-agent orchestration task. The `/debug` command provides structured troubleshooting, while `/think` engages the deep-think-partner for reasoning through hypotheses.

---

## Example 3: Architecture Decision

**User request:**
> "Should I use a monolith or microservices for my new e-commerce platform?"

**Analysis:**
- Strategic decision with long-term implications
- Needs to weigh multiple trade-offs
- No implementation yet, just reasoning

**Recommendation:**
```bash
/think monolith vs microservices for e-commerce platform
```

Or for more thorough analysis:
```bash
/think evaluate monolith vs microservices architecture for e-commerce, considering team size, scalability needs, and operational complexity
```

**Why:** This is a strategic thinking task, not an implementation task. The deep-think-partner or think (extended) will explore trade-offs, consider constraints, and provide reasoned recommendations.

---

## Example 4: Multi-File Refactoring

**User request:**
> "Refactor the payment service to use the new API client pattern"

**Analysis:**
- Coordinated changes across multiple files
- Clear scope, no research needed
- Standard refactoring task

**Recommendation:**
```bash
/develop refactor payment service to use new API client pattern
```

**Why:** Multi-file coordination benefits from workflow orchestration. No flags needed for a straightforward refactoring task.

**Execution flow:**
1. Gate: Clear request, proceed
2. Context: Find payment service files, new API client pattern
3. Plan: Map current implementation to new pattern
4. Execute: Deploy agent to update service files
5. Report: Summary of refactored service

---

## Example 5: Quick Task (No Orchestration)

**User request:**
> "Add error handling to the getUserById function"

**Analysis:**
- Single function modification
- Clear scope
- No parallelization opportunity

**Recommendation:**
Inline guidance - no command needed.

**Why:** This is a simple, focused task. Orchestration would be overkill. Just provide direct implementation guidance.

---

## Example 6: Code Review Preparation

**User request:**
> "I need to review and improve the quality of my authentication module before the PR"

**Analysis:**
- Quality-focused task
- Benefits from multiple angles of review
- Validation is core requirement

**Recommendation:**
```bash
/develop review authentication module --validate
```

Or use the dedicated review commands:
```bash
/double-check the authentication module implementation
```

**Why:** The `--validate` flag triggers opus-level deep validation. Alternatively, `/double-check` is purpose-built for quality validation.

---

## Example 7: Learning/Understanding

**User request:**
> "How does the event bus work in this codebase?"

**Analysis:**
- Understanding task, not implementation
- Needs code exploration
- No changes required

**Recommendation:**
Direct exploration and explanation - no orchestration command needed.

**Why:** This is a knowledge query, not a task. Read the relevant files and explain the architecture directly.

---

## Example 8: High-Stakes Implementation

**User request:**
> "Implement the payment processing integration with Stripe"

**Analysis:**
- Critical functionality (payments)
- Security-sensitive
- Needs thorough research and validation

**Recommendation:**
```bash
/develop implement Stripe payment integration --validate
```

**Why:** The `--validate` flag is essential for high-stakes, security-sensitive implementations. It triggers opus-level deep validation to ensure security is properly reviewed.

---

## Decision Matrix

| Scenario | Tool | Flags |
|----------|------|-------|
| Multi-component feature | `/develop` | `--validate` if important |
| Single complex problem | `/think` | - |
| Multi-faceted analysis | `/think` | - |
| Strategic decision | `/think` | - |
| Debugging investigation | `/debug` | - |
| Quick code change | Inline | - |
| Security-sensitive work | `/develop` | `--validate` |
| Plan first, implement later | `/develop` | `--plan-only` |
| Quality review | `/double-check` | - |

## Common Patterns

### "How should I approach X?"

Start with `/think` to reason through the approach, then `/develop` if implementation is needed.

### "I need to do A, B, and C"

If independent: `/develop` will parallelize them.
If sequential: `/develop` will sequence them appropriately.

### "This is really complex"

Use `/think` for deep analysis, then `/develop --validate` for implementation.

### "Before I merge this..."

Use `/double-check` for quality validation.
