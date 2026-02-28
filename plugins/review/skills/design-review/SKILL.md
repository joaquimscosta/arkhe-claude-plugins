---
name: design-review
description: >
  Comprehensive UI/UX design review with live environment testing, responsive validation,
  accessibility compliance (WCAG 2.1 AA), and visual consistency analysis using Playwright.
  Use when user runs /design-review, /review:design-review, requests a "design review",
  "UI review", "UX audit", or mentions "review the design", "check accessibility", "responsive testing".
disable-model-invocation: true
argument-hint: "[output-directory]"
---

# Design Review

World-class design review following standards of top Silicon Valley companies (Stripe, Airbnb, Linear).

## Parse Arguments

**Output Path Configuration**:
- If `$ARGUMENTS` is provided and non-empty: Use `$ARGUMENTS` as the output directory
- Otherwise: Use default `./reviews/design/`

## Git Analysis

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

Review the complete diff above to understand the scope of UI/UX changes.

## Core Methodology

**"Live Environment First"** — Always assess the interactive experience before diving into static analysis or code. Prioritize the actual user experience over theoretical perfection.

## Prerequisites

- A live preview environment (local dev server or staging URL)
- Playwright CLI for automated browser testing (refer to the `playwright:playwright-cli` skill for full command reference)

## Review Phases

Execute each phase systematically. See [WORKFLOW.md](WORKFLOW.md) for detailed checklists.

| Phase | Focus | Key Actions |
|-------|-------|-------------|
| 0 | Preparation | Analyze PR/description, review code diff, set up preview, configure viewport (1440x900) |
| 1 | Interaction | Execute user flows, test interactive states (hover/active/disabled), verify confirmations |
| 2 | Responsiveness | Desktop (1440px), tablet (768px), mobile (375px), no horizontal scroll |
| 3 | Visual Polish | Layout alignment, typography hierarchy, color consistency, image quality |
| 4 | Accessibility | Keyboard nav (Tab order), focus states, Enter/Space activation, semantic HTML, labels, alt text, contrast (4.5:1) |
| 5 | Robustness | Form validation, content overflow, loading/empty/error states, edge cases |
| 6 | Code Health | Component reuse, design tokens (no magic numbers), pattern adherence |
| 7 | Content & Console | Grammar, text clarity, browser console errors/warnings |

## Triage Matrix

Categorize every finding:

- **[Blocker]**: Critical failures requiring immediate fix
- **[High-Priority]**: Significant issues to fix before merge
- **[Medium-Priority]**: Improvements for follow-up
- **[Nitpick]**: Minor aesthetic details (prefix with "Nit:")

## Communication Principles

1. **Problems Over Prescriptions**: Describe problems and their impact, not technical solutions. Example: Instead of "Change margin to 16px", say "The spacing feels inconsistent with adjacent elements."
2. **Evidence-Based**: Provide screenshots for visual issues.
3. **Start Positive**: Begin with acknowledgment of what works well.

## Output Instructions

1. **Create output directory** using Bash: `mkdir -p {output-directory}`
2. **Save the report** to: `{output-directory}/{YYYY-MM-DD}_{HH-MM-SS}_design-review.md`

Include this header:

```markdown
# Design Review Report

**Date**: {ISO 8601 date}
**Branch**: {current branch name}
**Commit**: {short commit hash}
**Reviewer**: Claude Code (design-review)

---
```

3. **Display the full report** to the user in the chat
4. **Confirm the save**: Report saved to: {output-directory}/{filename}

## Resources

- [WORKFLOW.md](WORKFLOW.md) - Detailed phase-by-phase review checklists and report template
- [EXAMPLES.md](EXAMPLES.md) - Sample design review reports
