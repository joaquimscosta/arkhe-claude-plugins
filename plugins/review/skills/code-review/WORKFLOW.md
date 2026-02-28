# Code Review Workflow

Detailed checklists for each category in the Hierarchical Review Framework.

## 1. Architectural Design & Integrity (Critical)

- Evaluate if the design aligns with existing architectural patterns and system boundaries
- Assess modularity and adherence to Single Responsibility Principle
- Identify unnecessary complexity — could a simpler solution achieve the same goal?
- Verify the change is atomic (single, cohesive purpose) not bundling unrelated changes
- Check for appropriate abstraction levels and separation of concerns

## 2. Functionality & Correctness (Critical)

- Verify the code correctly implements the intended business logic
- Identify handling of edge cases, error conditions, and unexpected inputs
- Detect potential logical flaws, race conditions, or concurrency issues
- Validate state management and data flow correctness
- Ensure idempotency where appropriate

## 3. Security (Non-Negotiable)

- Verify all user input is validated, sanitized, and escaped (XSS, SQLi, command injection prevention)
- Confirm authentication and authorization checks on all protected resources
- Check for hardcoded secrets, API keys, or credentials
- Assess data exposure in logs, error messages, or API responses
- Validate CORS, CSP, and other security headers where applicable
- Review cryptographic implementations for standard library usage

## 4. Maintainability & Readability (High Priority)

- Assess code clarity for future developers
- Evaluate naming conventions for descriptiveness and consistency
- Analyze control flow complexity and nesting depth
- Verify comments explain 'why' (intent/trade-offs) not 'what' (mechanics)
- Check for appropriate error messages that aid debugging
- Identify code duplication that should be refactored

## 5. Testing Strategy & Robustness (High Priority)

- Evaluate test coverage relative to code complexity and criticality
- Verify tests cover failure modes, security edge cases, and error paths
- Assess test maintainability and clarity
- Check for appropriate test isolation and mock usage
- Identify missing integration or end-to-end tests for critical paths

## 6. Performance & Scalability (Important)

- **Backend**: Identify N+1 queries, missing indexes, inefficient algorithms
- **Frontend**: Assess bundle size impact, rendering performance, Core Web Vitals
- **API Design**: Evaluate consistency, backwards compatibility, pagination strategy
- Review caching strategies and cache invalidation logic
- Identify potential memory leaks or resource exhaustion

## 7. Dependencies & Documentation (Important)

- Question necessity of new third-party dependencies
- Assess dependency security, maintenance status, and license compatibility
- Verify API documentation updates for contract changes
- Check for updated configuration or deployment documentation

---

## Communication Principles

### Actionable Feedback
Provide specific, actionable suggestions. Include file path and line number for every finding.

### Explain the "Why"
When suggesting changes, explain the underlying engineering principle that motivates the suggestion.

### Triage Matrix
Categorize every significant issue to help the author prioritize:

- **[Critical/Blocker]**: Must be fixed before merge (e.g., security vulnerability, architectural regression)
- **[Improvement]**: Strong recommendation for improving the implementation
- **[Nit]**: Minor polish, optional

### Constructive Tone
Maintain objectivity and assume good intent. The goal is net improvement, not perfection.

---

## Report Template

```markdown
# Pragmatic Code Review Report

**Date**: {ISO 8601 date}
**Branch**: {current branch name}
**Commit**: {short commit hash}
**Reviewer**: Claude Code (pragmatic-code-review)

---

## Summary

[Overall assessment: Is this change a net positive? High-level observations about the approach, architecture, and quality.]

## Findings

### Critical Issues

- **[Critical]** `{file}:{line}` — {Description of the issue and why it's critical, grounded in engineering principles}
  - **Principle**: {e.g., SRP violation, security vulnerability}
  - **Suggestion**: {Specific fix recommendation}

### Suggested Improvements

- **[Improvement]** `{file}:{line}` — {Suggestion and rationale}
  - **Principle**: {Engineering principle}
  - **Suggestion**: {What to change}

### Nitpicks

- **Nit:** `{file}:{line}` — {Minor detail}

## Verdict

- **Recommendation**: {Approve / Request Changes / Approve with Nits}
- **Critical Issues**: {count}
- **Improvements**: {count}
- **Nits**: {count}
```
