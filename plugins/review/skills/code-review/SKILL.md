---
name: code-review
description: >
  Conduct comprehensive code reviews using the Pragmatic Quality framework with
  hierarchical analysis (architecture, security, maintainability, testing, performance).
  Use when user runs /code-review, /review:code-review, requests a "code review",
  "review my changes", "PR review", or mentions "review diff", "review branch".
disable-model-invocation: true
argument-hint: "[output-directory]"
---

# Code Review

Pragmatic Quality framework — balance rigorous engineering standards with development speed.

## Parse Arguments

**Output Path Configuration**:
- If `$ARGUMENTS` is provided and non-empty: Use `$ARGUMENTS` as the output directory
- Otherwise: Use default `./reviews/code/`

Example usage:
- `/review:code-review` → saves to `./reviews/code/`
- `/review:code-review custom/reviews` → saves to `custom/reviews/`

## Git Analysis

Analyze the following outputs to understand the scope and content of the changes.

GIT STATUS:

```
!`git status`
```

FILES MODIFIED:

```
!`git diff --name-only origin/HEAD...`
```

COMMITS:

```
!`git log --no-decorate origin/HEAD...`
```

DIFF CONTENT:

```
!`git diff --merge-base origin/HEAD`
```

Review the complete diff above. This contains all code changes to review.

## Review Philosophy

1. **Net Positive > Perfection**: Determine if the change improves overall code health. Do not block on imperfections if the change is a net improvement.
2. **Focus on Substance**: Prioritize architecture, design, business logic, security, and complex interactions.
3. **Grounded in Principles**: Base feedback on SOLID, DRY, KISS, YAGNI — not opinions.
4. **Signal Intent**: Prefix minor polish suggestions with '**Nit:**'.

## Hierarchical Review Framework

Analyze code using this prioritized checklist. See [WORKFLOW.md](WORKFLOW.md) for detailed checklists per category.

| Priority | Category | Focus Areas |
|----------|----------|-------------|
| 1 (Critical) | Architecture & Integrity | Patterns, modularity, SRP, complexity, atomicity |
| 2 (Critical) | Functionality & Correctness | Logic, edge cases, race conditions, state, idempotency |
| 3 (Non-Negotiable) | Security | Input validation, auth, secrets, data exposure, crypto |
| 4 (High) | Maintainability & Readability | Clarity, naming, complexity, comments, duplication |
| 5 (High) | Testing Strategy | Coverage, failure modes, isolation, integration tests |
| 6 (Important) | Performance & Scalability | N+1 queries, bundle size, caching, memory leaks |
| 7 (Important) | Dependencies & Documentation | Third-party risk, license, API docs, config changes |

## Triage Matrix

Categorize every significant finding:

- **[Critical/Blocker]**: Must be fixed before merge (security vulnerability, architectural regression)
- **[Improvement]**: Strong recommendation for improving the implementation
- **[Nit]**: Minor polish, optional

## Output Instructions

1. **Create output directory** using Bash: `mkdir -p {output-directory}`
2. **Save the report** to: `{output-directory}/{YYYY-MM-DD}_{HH-MM-SS}_code-review.md`

Include this header in the saved file:

```markdown
# Pragmatic Code Review Report

**Date**: {ISO 8601 date}
**Branch**: {current branch name}
**Commit**: {short commit hash}
**Reviewer**: Claude Code (pragmatic-code-review)

---
```

3. **Display the full report** to the user in the chat
4. **Confirm the save**: Report saved to: {output-directory}/{filename}

## Content Guidelines

- Provide specific, actionable feedback with file paths and line numbers
- Explain the underlying engineering principle for each suggestion
- Be constructive — assume good intent from the author
- See [WORKFLOW.md](WORKFLOW.md) for detailed review checklists per category

## Resources

- [WORKFLOW.md](WORKFLOW.md) - Detailed hierarchical review checklists and report template
- [EXAMPLES.md](EXAMPLES.md) - Sample code review reports
