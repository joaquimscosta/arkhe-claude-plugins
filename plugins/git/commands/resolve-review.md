---
description: Analyze, verify, and resolve review suggestions from a GitHub PR or local code-review report
argument-hint: [PR-number | URL | file-path]
---

# PR Issue Resolver

Multi-agent review resolution with trust-but-verify methodology and confidence-based filtering.

## Usage

```bash
/resolve-review 123                              # Resolve PR review comments by number
/resolve-review https://github.com/org/repo/42   # Resolve PR review comments by URL
/resolve-review reviews/code/2026-03-18_review.md # Resolve findings from a local review file
```

## What It Does

1. Extracts review comments (PR) or findings (file)
2. Verifies each with parallel agents using confidence scoring (0-100)
3. Filters false positives (below 80)
4. Presents a triage report for your approval
5. Applies approved fixes and replies to comments

## Implementation

Invoke the Skill tool with skill name "git:resolving-pr-issues" and arguments: `$ARGUMENTS`

For detailed documentation, see `git/skills/resolving-pr-issues/SKILL.md`.
