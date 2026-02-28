# Design Review Workflow

Detailed phase-by-phase review checklists and report template.

## Phase 0: Preparation

- Analyze the PR description to understand motivation, changes, and testing notes
- Review the code diff to understand implementation scope
- Set up the live preview environment using Playwright CLI (via Bash)
- Configure initial viewport (1440x900 for desktop)

## Phase 1: Interaction and User Flow

- Execute the primary user flow following testing notes
- Test all interactive states (hover, active, disabled)
- Verify destructive action confirmations
- Assess perceived performance and responsiveness

## Phase 2: Responsiveness Testing

- Test desktop viewport (1440px) — capture screenshot
- Test tablet viewport (768px) — verify layout adaptation
- Test mobile viewport (375px) — ensure touch optimization
- Verify no horizontal scrolling or element overlap

## Phase 3: Visual Polish

- Assess layout alignment and spacing consistency
- Verify typography hierarchy and legibility
- Check color palette consistency and image quality
- Ensure visual hierarchy guides user attention

## Phase 4: Accessibility (WCAG 2.1 AA)

- Test complete keyboard navigation (Tab order)
- Verify visible focus states on all interactive elements
- Confirm keyboard operability (Enter/Space activation)
- Validate semantic HTML usage
- Check form labels and associations
- Verify image alt text
- Test color contrast ratios (4.5:1 minimum)

## Phase 5: Robustness Testing

- Test form validation with invalid inputs
- Stress test with content overflow scenarios
- Verify loading, empty, and error states
- Check edge case handling

## Phase 6: Code Health

- Verify component reuse over duplication
- Check for design token usage (no magic numbers)
- Ensure adherence to established patterns

## Phase 7: Content and Console

- Review grammar and clarity of all text
- Check browser console for errors/warnings

---

## Communication Principles

### Problems Over Prescriptions

Describe problems and their impact, not technical solutions.

**Do**: "The spacing feels inconsistent with adjacent elements, creating visual clutter."
**Don't**: "Change margin to 16px."

### Triage Matrix

Categorize every issue:

- **[Blocker]**: Critical failures requiring immediate fix (broken functionality, inaccessible content, security issue)
- **[High-Priority]**: Significant issues to fix before merge (layout breaks, accessibility violations, major visual inconsistencies)
- **[Medium-Priority]**: Improvements for follow-up (minor visual refinements, performance optimizations)
- **[Nitpick]**: Minor aesthetic details (prefix with "Nit:")

### Evidence-Based Feedback

Provide screenshots for visual issues. Always start with positive acknowledgment of what works well.

### Constructive Tone

Maintain objectivity while being constructive. Always assume good intent from the implementer. Balance perfectionism with practical delivery timelines.

---

## Playwright CLI Integration

Use the Playwright CLI skill (`playwright:playwright-cli`) for all browser automation:

| Action | Command |
|--------|---------|
| Navigate | `playwright-cli open <url>` |
| Click | `playwright-cli click <ref>` |
| Type | `playwright-cli type <text>` |
| Screenshot | `playwright-cli screenshot [filename]` |
| Snapshot | `playwright-cli snapshot` (accessibility tree / DOM) |
| Key press | `playwright-cli press <key>` |
| Resize | `playwright-cli resize <width> <height>` |

**Viewport configurations**:
- Desktop: 1440x900
- Tablet: 768x1024
- Mobile: 375x812

---

## Report Template

```markdown
# Design Review Report

**Date**: {ISO 8601 date}
**Branch**: {current branch name}
**Commit**: {short commit hash}
**Reviewer**: Claude Code (design-review)

---

## Summary

[Positive opening acknowledging what works well, followed by overall assessment]

## Findings

### Blockers

- **[Blocker]** {Problem description}
  - **Impact**: {How this affects users}
  - **Screenshot**: {Attached or inline}

### High-Priority

- **[High-Priority]** {Problem description}
  - **Impact**: {How this affects users}
  - **Screenshot**: {If visual}

### Medium-Priority / Suggestions

- **[Medium]** {Problem description}
  - **Context**: {Why this matters}

### Nitpicks

- **Nit:** {Minor aesthetic detail}

## Responsive Summary

| Viewport | Status | Notes |
|----------|--------|-------|
| Desktop (1440px) | {Pass/Issues} | {Details} |
| Tablet (768px) | {Pass/Issues} | {Details} |
| Mobile (375px) | {Pass/Issues} | {Details} |

## Accessibility Summary

| Check | Status | Notes |
|-------|--------|-------|
| Keyboard navigation | {Pass/Issues} | {Details} |
| Focus states | {Pass/Issues} | {Details} |
| Semantic HTML | {Pass/Issues} | {Details} |
| Color contrast | {Pass/Issues} | {Details} |
| Form labels | {Pass/Issues} | {Details} |

## Verdict

- **Recommendation**: {Approve / Request Changes / Approve with Notes}
- **Blockers**: {count}
- **High-Priority**: {count}
- **Medium-Priority**: {count}
- **Nits**: {count}
```
