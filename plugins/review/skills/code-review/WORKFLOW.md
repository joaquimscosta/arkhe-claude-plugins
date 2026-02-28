# Code Review Workflow

Detailed checklists, false positive filtering, diff-context probes, and confidence scoring guide.

---

## Phase 0: PR Assessment

Perform this assessment before any line-by-line analysis.

### Risk Stratification

| Change Type | Risk | Primary Focus |
|-------------|------|---------------|
| New files (feature code) | Medium | Architecture, error handling, test coverage |
| Modified core logic | High | Correctness, regressions, breaking changes |
| Deleted code | Medium-High | Orphaned callers, unused imports, broken references |
| Config / dependencies | High | Security, compatibility, environment impact |
| Database migrations | Critical | Rollback strategy, data integrity, performance |
| Test-only changes | Low | Coverage adequacy, test isolation |
| Docs / comments only | Low | Accuracy, completeness |

### Atomicity Check

- Does this PR serve a single, cohesive purpose?
- Are there unrelated changes bundled together (e.g., feature + refactor + config)?
- If mixed, note in the PR Assessment: "Mixed — consider splitting"

### Breaking Change Detection

Check for these signals in the diff:

1. **Public function/method signature changed** — search for callers outside the diff
2. **Database migration added** — verify rollback strategy exists
3. **API response structure changed** — check for downstream consumers
4. **Environment variable added/renamed/removed** — check deployment docs and config
5. **Exports removed or renamed** — search for all importers across the codebase

---

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

## Diff-Context Awareness

Go beyond the diff to detect cross-file impacts:

### Context Probes

| Trigger in Diff | Context Action |
|-----------------|----------------|
| Function/method signature changed | Search for callers outside the diff using Grep |
| Export removed or renamed | Check all importers across the codebase |
| Database schema changed | Verify migration has rollback; check ORM models |
| API response structure changed | Search for downstream consumers |
| Shared type/interface modified | Find all files using that type |
| Config key added/renamed | Check deployment configs, CI/CD, and docs |

### When to Ask Questions vs. Assert

- If context outside the diff could justify the change, use **[Question]** not **[Blocker]**
- Example: "Is this timeout intentionally set to 0, or should it use the default?"
- Only assert a finding as Blocker when you can verify the issue from the diff + context probes

---

## False Positive Filtering

Apply these rules before finalizing findings. Discard any finding that matches a hard exclusion.

### Hard Exclusions

1. **Style-only issues** — defer to linters (formatting, import order, trailing whitespace)
2. **Theoretical performance** — do not flag without measurable impact or Big-O degradation
3. **Subjective preferences** — discard if you cannot cite a named engineering principle
4. **Test-only file issues** — do not flag patterns in test files that don't affect production code
5. **Framework-handled concerns** — do not flag XSS in React/Angular unless using unsafe HTML injection APIs
6. **Missing features not in scope** — do not flag features the PR didn't intend to add
7. **Consistent naming** — do not nitpick naming that matches the existing codebase convention
8. **Established patterns** — do not flag code patterns used elsewhere in the codebase as issues
9. **Code outside the diff** — do not report on unchanged code unless directly impacted by the change
10. **Vague suggestions** — discard any finding that says "could be improved" without specific impact

### Signal Quality Criteria

For each remaining finding, verify:
1. Is there a concrete, demonstrable impact (bug, security risk, performance degradation, maintenance burden)?
2. Can you name the engineering principle being violated?
3. Is the suggestion actionable with a specific fix (not just "consider improving")?
4. Would a senior engineer confidently raise this in a PR review?

If any answer is "no," suppress the finding.

---

## Confidence Scoring Guide

### Scoring Rubric

| Score | Meaning | Examples |
|-------|---------|----------|
| 9-10 | Certain — clear bug, vulnerability, or architectural violation | SQL injection via string interpolation; missing null check causing crash; SRP violation creating circular dependency |
| 7-8 | Strong evidence — likely issue, may depend on context | Missing error handling on API call; potential race condition in concurrent path; N+1 query pattern |
| 5-6 | Moderate — plausible concern but speculative | "This could be slow at scale" without metrics; naming that's unclear but functional |
| 1-4 | Weak — personal preference or theoretical | Style preference not in style guide; micro-optimization; "I would have done it differently" |

### Decision Matrix

| Confidence | Allowed Triage Levels |
|------------|----------------------|
| 9-10 | Blocker, Improvement |
| 7-8 | Improvement, Question |
| 5-6 | Suppress (do not report) |
| Below 5 | Discard |

### Self-Reflection Pass

After generating all candidate findings:

1. Review all findings together as a set — are there redundant or overlapping items?
2. Re-score each finding with full context of the others
3. Remove any finding that dropped below threshold after re-evaluation
4. Enforce caps: keep top 8 meaningful findings + top 2 Nits by confidence
5. If exceeding caps, drop the lowest-confidence items and note: "Additional observations available on request"

---

## Communication Principles

### Actionable Feedback
Provide specific, actionable suggestions. Include file path and line number for every finding.

### Before/After Code Blocks
Blocker and Improvement findings must include code showing current state and suggested fix:

```
Current (`file:line`):
  code here

Suggested:
  improved code here
```

### Explain the "Why"
When suggesting changes, explain the underlying engineering principle:
- **Security**: OWASP Top 10, defense-in-depth, least privilege
- **Design**: Specific SOLID principle, DRY, KISS, YAGNI
- **Performance**: Big-O impact, specific metric or query pattern
- **Testing**: Test pyramid, test isolation, coverage strategy

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

## PR Assessment

| Attribute | Value |
|-----------|-------|
| **Risk Level** | {Low / Medium / High / Critical} |
| **PR Type** | {Feature / Bugfix / Refactor / Config / Test-only / Docs} |
| **Atomicity** | {Atomic / Mixed — consider splitting} |
| **Breaking Changes** | {None / Yes — description} |

---

## Summary

[Overall assessment: Is this change a net positive? High-level observations about the approach, architecture, and quality.]

## Findings

### Blockers

- **[Blocker]** `{file}:{line}` — {Description} (Confidence: {N}/10)
  - **Principle**: {Named engineering principle}
  - **Current**: `{code snippet}`
  - **Suggested**: `{fix snippet}`

### Improvements

- **[Improvement]** `{file}:{line}` — {Suggestion and rationale} (Confidence: {N}/10)
  - **Principle**: {Named engineering principle}
  - **Current**: `{code snippet}`
  - **Suggested**: `{fix snippet}`

### Questions

- **[Question]** `{file}:{line}` — {Clarification needed}

### Praise

- **[Praise]** `{file}:{line}` — {What was done well and why it matters}

### Nitpicks

- **[Nit]** `{file}:{line}` — {Minor detail}

## Verdict

- **Recommendation**: {Approve / Request Changes / Approve with Nits}
- **Risk Level**: {Low / Medium / High / Critical}
- **Blockers**: {count}
- **Improvements**: {count}
- **Questions**: {count}
- **Nits**: {count}
```
