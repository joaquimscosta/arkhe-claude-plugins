# Design Review Workflow

Detailed phase-by-phase review checklists, false positive filtering, and confidence scoring guide.

---

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

### Viewport Tiers

Test across 7 viewport tiers, capturing screenshots at each:

| Tier | Width x Height | Rationale |
|------|---------------|-----------|
| Small mobile | 375 x 812 | iPhone SE — worst-case small mobile |
| Standard mobile | 390 x 844 | iPhone 14/15 — most common mobile |
| Tablet portrait | 768 x 1024 | iPad mini |
| Tablet landscape | 1024 x 768 | iPad / small laptop |
| Laptop | 1280 x 800 | Common laptop |
| Desktop | 1440 x 900 | Standard desktop |
| Large monitor | 1920 x 1080 | Wide desktop |

**Priority**: Always test 375px, 768px, and 1440px. Test additional tiers when the diff touches layout, grid, or responsive code.

### Between-Breakpoint Testing

Testing only at standard breakpoints misses failures between them. After fixed-viewport tests:

1. Identify the app's CSS breakpoints from the codebase (e.g., `@media (min-width: 768px)`)
2. Test at widths just below each breakpoint (e.g., 767px, 1023px, 1279px)
3. Look for: overlapping elements, text truncation, missing layout transitions

### Modern CSS Checks

- **Container queries** (`@container`): Verify components adapt to container width, not just viewport
- **Fluid typography** (`clamp()`): Verify body text stays ≥16px at minimum viewport and doesn't become excessively large
- **Viewport units**: Check for `vh` vs `dvh`/`svh`/`lvh` — mobile browser chrome collapse creates layout issues with full-height components

### Zoom Reflow (WCAG 1.4.4)

Content must reflow at 400% browser zoom without horizontal scrolling:

```bash
playwright-cli eval "document.documentElement.style.zoom = '4'"
playwright-cli screenshot --filename=.playwright-cli/zoom-400.png
```

Verify: single-column reflow, no horizontal scroll, all content visible.

### Orientation Testing

Test landscape mode on mobile viewports — modals and fixed-position elements often break:

```bash
playwright-cli resize 812 375
playwright-cli screenshot --filename=.playwright-cli/mobile-landscape.png
```

## Phase 3: Visual Polish

- Assess layout alignment and spacing consistency
- Verify typography hierarchy and legibility
- Check color palette consistency and image quality
- Ensure visual hierarchy guides user attention

## Phase 4: Accessibility (WCAG 2.1 AA)

Split into automated checks (axe-core) and manual checks (keyboard testing). Both are required — axe-core catches ~30% of WCAG issues; the rest require human verification.

### Automated: axe-core Scan

Run axe-core via Playwright to detect machine-verifiable violations:

```bash
playwright-cli eval "
  const script = document.createElement('script');
  script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js';
  document.head.appendChild(script);
  await new Promise(r => script.onload = r);
  const results = await axe.run();
  return JSON.stringify({
    violations: results.violations.map(v => ({
      id: v.id,
      impact: v.impact,
      description: v.description,
      nodes: v.nodes.length
    })),
    passes: results.passes.length,
    incomplete: results.incomplete.length
  }, null, 2);
"
```

**What axe-core reliably catches**:
- Color contrast ratios below 4.5:1 (normal text) / 3:1 (large text / UI components)
- Images missing `alt` attributes (presence only — not quality)
- Form inputs without associated labels
- Missing `<html lang>` attribute
- Duplicate element IDs
- Empty/nameless buttons and links
- Invalid ARIA roles, attributes, and values
- Skipped heading levels
- Missing document landmarks (`<main>`, `<nav>`)

**Severity-to-triage mapping**:

| axe Impact | Triage Level |
|------------|-------------|
| critical | [Blocker] |
| serious | [High-Priority] |
| moderate | [Medium-Priority] |
| minor | [Nit] |

### Manual: Keyboard Navigation Sequence

axe-core cannot verify these — execute manually using Playwright CLI:

1. **Skip link**: Press Tab once → verify skip-to-content link appears as first focusable element
2. **Tab order**: Press Tab through all interactive elements → verify logical order matches visual layout
3. **Modal focus trap**: Open a modal → Tab → verify focus stays inside modal; cannot Tab to elements behind it
4. **Modal dismiss**: Press Escape → verify modal closes and focus returns to the trigger element
5. **Button activation**: Press Enter and Space on all buttons → verify both activate the button
6. **Dropdown/menu navigation**: Press Arrow keys in dropdowns → verify items are navigable
7. **No keyboard traps**: Verify you can always Tab away from any element (no element captures focus permanently)

```bash
# Example keyboard testing sequence
playwright-cli press Tab
playwright-cli screenshot --filename=.playwright-cli/focus-1.png
playwright-cli press Tab
playwright-cli screenshot --filename=.playwright-cli/focus-2.png
playwright-cli press Enter
playwright-cli screenshot --filename=.playwright-cli/after-enter.png
playwright-cli press Escape
playwright-cli screenshot --filename=.playwright-cli/after-escape.png
```

### Additional Checks

- Verify all images have `alt` text (axe checks presence; manually verify quality for key images)
- Test color contrast on dynamic elements (hover states, active states, disabled states)
- Verify focus indicators are visible on all interactive elements (minimum 2px outline or equivalent)
- Check that touch targets meet 44x44px minimum on mobile viewports

### What NOT to Flag (Requires Specialized Tools)

Do not flag these as findings — they require screen reader testing or subjective judgment beyond automated review scope:

- Alt text *quality* (axe verifies presence; quality requires human context)
- Screen reader announcement phrasing
- Reading order preferences that differ from DOM order without clear usability impact

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

## Signal Quality & False Positive Filtering

Apply these rules before finalizing findings. Discard any finding that matches a hard exclusion.

### Hard Exclusions

1. **Aesthetic preferences** — do not flag without referencing a specific design token, WCAG criterion, or system rule
2. **Code-level issues invisible in the live environment** — defer to code review
3. **Third-party widget styling** — maps, embeds, social buttons, ad units are out of scope
4. **Cross-browser font rendering** — antialiasing differences between macOS/Windows/Linux are expected
5. **Dynamic content variability** — timestamps, user avatars, live data change between screenshots
6. **Animation mid-transition** — always wait for animations to settle before capturing evidence
7. **Pixel rounding differences** — sub-pixel variations between viewports are not findings
8. **Vague suggestions** — discard any finding that says "could look better" without citing a design token or WCAG rule
9. **Consistent patterns** — do not flag code or design patterns used elsewhere in the codebase
10. **Changes outside the diff** — do not report on unchanged UI unless directly impacted by the change

### Signal Quality Criteria

For each remaining finding, verify all four:
1. Is there a concrete, demonstrable impact (broken layout, inaccessible content, visual inconsistency)?
2. Can you reference a specific design token, WCAG criterion, or system rule being violated?
3. Is the finding backed by evidence (screenshot, axe output, contrast ratio measurement)?
4. Would a senior designer confidently raise this in a design review?

If any answer is "no," suppress the finding.

### Confidence Scoring Guide

| Score | Meaning | Examples |
|-------|---------|----------|
| 9-10 | Measurable failure — concrete evidence of broken experience | Contrast ratio 2.1:1 (needs 4.5:1); element overflows viewport at 768px; keyboard trap in modal; form submittable without required field |
| 7-8 | System violation — documented rule broken | Using `#333` instead of `--text-primary` token; 12px spacing where system uses 16px grid; missing landmark per WCAG 1.3.1 |
| 5-6 | Plausible concern — suppress | "This spacing feels off" without token reference; subjective alignment preference |
| 1-4 | Opinion — discard | Animation timing preference; pixel rounding; font weight opinion |

### Self-Reflection Pass

After generating all candidate findings:

1. Review all findings together as a set — are there redundant or overlapping items?
2. Re-score each finding with full context of the others
3. Apply hard exclusion rules — remove any matches
4. Enforce caps: keep top 8 meaningful findings + top 2 Nits by confidence
5. If exceeding caps, drop the lowest-confidence items and note: "Additional observations available on request"

---

## Playwright CLI Integration

Use the Playwright CLI skill (`playwright:playwright-cli`) for all browser automation:

### Core Commands

| Action | Command |
|--------|---------|
| Navigate | `playwright-cli open <url>` |
| Click | `playwright-cli click <ref>` |
| Type | `playwright-cli fill <ref> <text>` |
| Screenshot | `playwright-cli screenshot [--filename=path]` |
| Snapshot | `playwright-cli snapshot` (accessibility tree) |
| Key press | `playwright-cli press <key>` |
| Resize | `playwright-cli resize <width> <height>` |
| Evaluate JS | `playwright-cli eval "<js>"` |

### Viewport Configurations

| Device | Command |
|--------|---------|
| Small mobile | `playwright-cli resize 375 812` |
| Standard mobile | `playwright-cli resize 390 844` |
| Tablet portrait | `playwright-cli resize 768 1024` |
| Tablet landscape | `playwright-cli resize 1024 768` |
| Laptop | `playwright-cli resize 1280 800` |
| Desktop | `playwright-cli resize 1440 900` |
| Large monitor | `playwright-cli resize 1920 1080` |

### Accessibility Testing Commands

```bash
# Accessibility tree inspection
playwright-cli snapshot

# Keyboard navigation testing
playwright-cli press Tab
playwright-cli press Enter
playwright-cli press Space
playwright-cli press Escape

# Focus state verification (screenshot after each Tab)
playwright-cli press Tab
playwright-cli screenshot --filename=.playwright-cli/focus-state.png

# axe-core scan (see Phase 4 for full script)
playwright-cli eval "<axe-core injection script>"
```

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

- **[Blocker]** {Problem description} (Confidence: {N}/10)
  - **Impact**: {How this affects users}
  - **Evidence**: {Screenshot or axe output}

### High-Priority

- **[High-Priority]** {Problem description} (Confidence: {N}/10)
  - **Impact**: {How this affects users}
  - **Reference**: {Design token, WCAG criterion, or system rule violated}
  - **Evidence**: {Screenshot or measurement}

### Medium-Priority / Suggestions

- **[Medium]** {Problem description} (Confidence: {N}/10)
  - **Context**: {Why this matters, with evidence}

### Praise

- **[Praise]** {What was done well and why it matters}

### Nitpicks

- **Nit:** {Minor aesthetic detail}

## Responsive Summary

| Viewport | Status | Notes |
|----------|--------|-------|
| Small mobile (375px) | {Pass/Issues} | {Details} |
| Standard mobile (390px) | {Pass/Issues} | {Details} |
| Tablet portrait (768px) | {Pass/Issues} | {Details} |
| Tablet landscape (1024px) | {Pass/Issues} | {Details} |
| Laptop (1280px) | {Pass/Issues} | {Details} |
| Desktop (1440px) | {Pass/Issues} | {Details} |
| Large monitor (1920px) | {Pass/Issues} | {Details} |
| Zoom reflow (400%) | {Pass/Issues} | {Details} |

## Accessibility Summary

### Automated (axe-core)

| Check | Status | Notes |
|-------|--------|-------|
| Color contrast | {Pass/Issues} | {Details} |
| Image alt text | {Pass/Issues} | {Details} |
| Form labels | {Pass/Issues} | {Details} |
| ARIA validity | {Pass/Issues} | {Details} |
| Heading hierarchy | {Pass/Issues} | {Details} |
| Document landmarks | {Pass/Issues} | {Details} |

### Manual (Keyboard)

| Check | Status | Notes |
|-------|--------|-------|
| Skip link | {Pass/Issues/N/A} | {Details} |
| Tab order | {Pass/Issues} | {Details} |
| Focus visibility | {Pass/Issues} | {Details} |
| Modal focus trap | {Pass/Issues/N/A} | {Details} |
| Button activation | {Pass/Issues} | {Details} |
| Keyboard traps | {Pass/Issues} | {Details} |

## Verdict

- **Recommendation**: {Approve / Request Changes / Approve with Notes}
- **Blockers**: {count}
- **High-Priority**: {count}
- **Medium-Priority**: {count}
- **Nits**: {count}
```
