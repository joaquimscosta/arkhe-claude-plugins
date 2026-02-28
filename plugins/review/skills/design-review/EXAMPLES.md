# Design Review Examples

## Invocation

```bash
# Default output path
/review:design-review

# Custom output path
/review:design-review custom/reviews/
```

## Sample Report — Mixed Findings

```markdown
# Design Review Report

**Date**: 2025-08-05T11:00:00Z
**Branch**: feat/settings-page
**Commit**: n4o5p6q
**Reviewer**: Claude Code (design-review)

---

## Summary

The new settings page is well-structured with clean visual hierarchy and intuitive grouping of related options. The form interactions are responsive and the success state feedback is clear. However, there are accessibility issues with keyboard navigation and a responsive layout break on tablet viewports that should be addressed before merge.

## Findings

### Blockers

None.

### High-Priority

- **[High-Priority]** The settings form sections are not keyboard-accessible — Tab key skips from the navigation sidebar directly to the footer, bypassing all form controls. (Confidence: 10/10)
  - **Impact**: Users relying on keyboard navigation cannot access any settings. Violates WCAG 2.1 AA Success Criterion 2.1.1 (Keyboard).
  - **Evidence**: focus-1.png → focus-2.png shows Tab jumping from sidebar to footer

- **[High-Priority]** On tablet portrait viewport (768px), the two-column layout for "Notification Preferences" overlaps with the sidebar, causing form labels to be cut off. (Confidence: 9/10)
  - **Impact**: Users on tablet devices cannot read option labels, making the form unusable at this breakpoint.
  - **Reference**: Layout breakpoint rule at `@media (min-width: 768px)` does not account for sidebar width.
  - **Evidence**: settings-tablet-overlap.png

### Medium-Priority / Suggestions

- **[Medium]** The "Delete Account" button has the same visual weight as the "Save Changes" button. Both are solid blue buttons at the same size. (Confidence: 7/10)
  - **Context**: Destructive actions should be visually differentiated from primary actions to prevent accidental clicks. The design system uses `--color-danger` for destructive actions.

### Praise

- **[Praise]** Clean use of `fieldset`/`legend` for form grouping — correct semantic HTML that makes the form structure clear to assistive technology.

### Nitpicks

- **Nit:** The spacing between the "Profile" and "Security" section headers (32px) is different from the spacing between "Security" and "Notifications" (24px). Design system specifies `--spacing-xl` (32px) for section gaps.

## Responsive Summary

| Viewport | Status | Notes |
|----------|--------|-------|
| Small mobile (375px) | Pass | Single column, good touch targets |
| Standard mobile (390px) | Pass | Consistent with 375px |
| Tablet portrait (768px) | Issues | Two-column overlap with sidebar |
| Tablet landscape (1024px) | Pass | Three-column layout works |
| Laptop (1280px) | Pass | Clean layout, proper spacing |
| Desktop (1440px) | Pass | Clean layout, proper spacing |
| Large monitor (1920px) | Pass | Content centered, max-width applied |
| Zoom reflow (400%) | Pass | Single column, no horizontal scroll |

## Accessibility Summary

### Automated (axe-core)

| Check | Status | Notes |
|-------|--------|-------|
| Color contrast | Pass | All text meets 4.5:1 ratio |
| Image alt text | Pass | No images in settings page |
| Form labels | Pass | All inputs have associated labels |
| ARIA validity | Pass | No ARIA errors detected |
| Heading hierarchy | Pass | h1 → h2 → h3 hierarchy correct |
| Document landmarks | Pass | main, nav, footer present |

### Manual (Keyboard)

| Check | Status | Notes |
|-------|--------|-------|
| Skip link | Pass | Skip-to-content link present |
| Tab order | Issues | Tab skips form controls entirely |
| Focus visibility | Pass | Visible focus rings on all interactive elements |
| Modal focus trap | N/A | No modals on this page |
| Button activation | Pass | Enter and Space work on all buttons |
| Keyboard traps | Pass | No keyboard traps detected |

## Verdict

- **Recommendation**: Request Changes
- **Blockers**: 0
- **High-Priority**: 2
- **Medium-Priority**: 1
- **Nits**: 1
```

## Sample Report — Clean Review

```markdown
# Design Review Report

**Date**: 2025-08-08T15:30:00Z
**Branch**: fix/button-states
**Commit**: r7s8t9u
**Reviewer**: Claude Code (design-review)

---

## Summary

Excellent fix for the button hover and disabled states. The visual feedback is now consistent across all button variants (primary, secondary, ghost) and matches the design system specifications. Keyboard focus states are properly implemented and the disabled state correctly prevents interaction while maintaining sufficient color contrast.

## Findings

### Blockers

None.

### High-Priority

None.

### Medium-Priority / Suggestions

None.

### Praise

- **[Praise]** Consistent transition timing across all button variants — 200ms ease-in-out matches the design system's `--transition-fast` token.

### Nitpicks

- **Nit:** The transition duration for the hover state on ghost buttons (300ms) is slightly longer than primary and secondary buttons (200ms). The design system specifies `--transition-fast` (200ms) for all button transitions.

## Responsive Summary

| Viewport | Status | Notes |
|----------|--------|-------|
| Small mobile (375px) | Pass | Full-width buttons display correctly |
| Standard mobile (390px) | Pass | Consistent with 375px |
| Tablet portrait (768px) | Pass | Touch targets meet 44px minimum |
| Tablet landscape (1024px) | Pass | Inline buttons space correctly |
| Laptop (1280px) | Pass | All states work correctly |
| Desktop (1440px) | Pass | All states work correctly |
| Large monitor (1920px) | Pass | No stretch or overflow |
| Zoom reflow (400%) | Pass | Buttons stack vertically at zoom |

## Accessibility Summary

### Automated (axe-core)

| Check | Status | Notes |
|-------|--------|-------|
| Color contrast | Pass | Disabled state maintains 3:1 ratio (decorative) |
| Form labels | N/A | No form inputs in this change |
| ARIA validity | Pass | Button roles correct |

### Manual (Keyboard)

| Check | Status | Notes |
|-------|--------|-------|
| Tab order | Pass | Tab order correct |
| Focus visibility | Pass | Visible focus rings on all button variants |
| Button activation | Pass | Enter and Space work on all variants |
| Keyboard traps | Pass | No keyboard traps |

## Verdict

- **Recommendation**: Approve
- **Blockers**: 0
- **High-Priority**: 0
- **Medium-Priority**: 0
- **Nits**: 1
```

## Sample Report — Accessibility-Focused Review

```markdown
# Design Review Report

**Date**: 2025-09-12T09:45:00Z
**Branch**: feat/search-modal
**Commit**: k3m4n5p
**Reviewer**: Claude Code (design-review)

---

## Summary

The new search modal implements a clean, keyboard-driven interface with a well-structured results list. The visual design is polished and consistent with the design system. However, axe-core detected critical accessibility violations (missing form label, low contrast on placeholder text) and manual keyboard testing revealed a focus trap issue when the modal closes.

## Findings

### Blockers

- **[Blocker]** The search input has no accessible label — axe-core violation `label` (critical). Screen readers announce this as "edit text" with no context. (Confidence: 10/10)
  - **Impact**: Screen reader users cannot identify the purpose of the input field.
  - **Reference**: WCAG 1.3.1 (Info and Relationships), WCAG 4.1.2 (Name, Role, Value)
  - **Evidence**: axe-core output: `{ id: "label", impact: "critical", nodes: 1 }`

- **[Blocker]** When closing the search modal with Escape, focus is sent to `<body>` instead of returning to the trigger button. User loses their place in the page. (Confidence: 10/10)
  - **Impact**: Keyboard users must Tab from the beginning of the page after closing the modal.
  - **Reference**: WCAG 2.4.3 (Focus Order) — focus must return to the triggering element.
  - **Evidence**: after-escape.png shows focus indicator at top of page

### High-Priority

- **[High-Priority]** Placeholder text "Search docs, APIs, guides..." has contrast ratio 2.8:1 against the white background — axe-core violation `color-contrast` (serious). (Confidence: 9/10)
  - **Impact**: Users with low vision cannot read the placeholder text.
  - **Reference**: WCAG 1.4.3 (Contrast Minimum) — 4.5:1 for normal text. Placeholder is not exempt.
  - **Evidence**: axe-core output: `{ id: "color-contrast", impact: "serious", nodes: 1 }`

- **[High-Priority]** Search results list items are not keyboard-navigable. Arrow keys do nothing; Tab skips from input to close button, bypassing all results. (Confidence: 9/10)
  - **Impact**: Keyboard users cannot select a search result.
  - **Reference**: ARIA Authoring Practices — Combobox pattern requires arrow key navigation through results.
  - **Evidence**: focus-3.png shows focus jumping from input to close button

### Medium-Priority / Suggestions

- **[Medium]** No empty state message when search returns zero results. The results area is simply blank. (Confidence: 7/10)
  - **Context**: Users may think the search is still loading. A "No results found" message with suggestion to refine the query improves UX.

### Praise

- **[Praise]** The `aria-live="polite"` region announcing result count ("5 results found") is excellent — screen reader users get immediate feedback as they type.

### Nitpicks

- **Nit:** The modal backdrop uses `opacity: 0.4` while the design system standard is `--overlay-opacity: 0.5`.

## Responsive Summary

| Viewport | Status | Notes |
|----------|--------|-------|
| Small mobile (375px) | Pass | Modal fills viewport, input auto-focused |
| Standard mobile (390px) | Pass | Consistent with 375px |
| Tablet portrait (768px) | Pass | Centered modal, appropriate width |
| Tablet landscape (1024px) | Pass | Consistent with portrait |
| Laptop (1280px) | Pass | Centered, max-width 640px |
| Desktop (1440px) | Pass | Clean centered layout |
| Large monitor (1920px) | Pass | No stretch |
| Zoom reflow (400%) | Pass | Modal adapts to single column |

## Accessibility Summary

### Automated (axe-core)

| Check | Status | Notes |
|-------|--------|-------|
| Color contrast | Issues | Placeholder text 2.8:1 (needs 4.5:1) |
| Image alt text | N/A | No images |
| Form labels | Issues | Search input missing accessible label |
| ARIA validity | Pass | aria-live region correctly implemented |
| Heading hierarchy | Pass | Modal heading is h2 |
| Document landmarks | Pass | dialog role present |

### Manual (Keyboard)

| Check | Status | Notes |
|-------|--------|-------|
| Skip link | N/A | Modal context |
| Tab order | Issues | Results not navigable via keyboard |
| Focus visibility | Pass | Focus ring visible on input and close button |
| Modal focus trap | Pass | Tab cycles within modal |
| Button activation | Pass | Close button responds to Enter/Space |
| Keyboard traps | Pass | Escape closes modal |
| Focus return | Issues | Focus sent to body, not trigger |

## Verdict

- **Recommendation**: Request Changes
- **Blockers**: 2
- **High-Priority**: 2
- **Medium-Priority**: 1
- **Nits**: 1
```

## Sample Report — Responsive Edge Case

```markdown
# Design Review Report

**Date**: 2025-10-01T14:20:00Z
**Branch**: feat/pricing-cards
**Commit**: w8x9y0z
**Reviewer**: Claude Code (design-review)

---

## Summary

The pricing cards component is visually polished at standard breakpoints with good typography hierarchy and clear CTA placement. However, between-breakpoint testing revealed a layout failure at widths between 768px and 1024px where the three-column card grid doesn't gracefully transition to two columns, causing cards to overflow. The 400% zoom reflow also has issues.

## Findings

### Blockers

- **[Blocker]** At viewport widths 769px–1023px, the three-column pricing grid overflows its container. Cards are clipped on the right edge, and the "Enterprise" card's CTA button is partially hidden. (Confidence: 10/10)
  - **Impact**: Users on small tablets or resized browser windows cannot see or interact with the rightmost pricing option.
  - **Reference**: CSS grid uses `grid-template-columns: repeat(3, 1fr)` at `≥768px` but the combined card min-widths (280px × 3 = 840px) exceed available width at 769px–1023px.
  - **Evidence**: pricing-900px.png shows right card clipped

### High-Priority

- **[High-Priority]** At 400% browser zoom, pricing cards stack vertically but the "Most Popular" badge on the middle card overflows its container and overlaps the adjacent card's title. (Confidence: 8/10)
  - **Impact**: Zoomed-in users see overlapping content that obscures pricing information.
  - **Reference**: WCAG 1.4.4 (Resize Text) — content must reflow without loss of information at 400% zoom.
  - **Evidence**: zoom-400-pricing.png shows badge overlap

### Medium-Priority / Suggestions

- **[Medium]** On landscape mobile (812×375), the pricing toggle (Monthly/Annual) wraps to two lines, pushing the cards below the fold. (Confidence: 7/10)
  - **Context**: Toggle text "Billed Monthly" / "Billed Annually" could be shortened to "Monthly" / "Annual" at narrow viewports using a responsive variant.

### Praise

- **[Praise]** The card hover state with subtle elevation change and border color transition creates a polished interactive feel. The `--shadow-md` to `--shadow-lg` progression matches the design system perfectly.

### Nitpicks

- **Nit:** The "per month" text under pricing uses `font-size: 13px` — the design system's smallest text token is `--text-xs` (12px). Consider aligning to the token.

## Responsive Summary

| Viewport | Status | Notes |
|----------|--------|-------|
| Small mobile (375px) | Pass | Single column, cards stack well |
| Standard mobile (390px) | Pass | Consistent with 375px |
| Tablet portrait (768px) | Issues | 3-col grid too tight at exactly 768px |
| Between (769–1023px) | Issues | Cards overflow container |
| Tablet landscape (1024px) | Pass | 3-col grid has enough space |
| Laptop (1280px) | Pass | Clean 3-col layout |
| Desktop (1440px) | Pass | Generous spacing |
| Large monitor (1920px) | Pass | Max-width constrains cards |
| Zoom reflow (400%) | Issues | Badge overflow on stacked cards |

## Accessibility Summary

### Automated (axe-core)

| Check | Status | Notes |
|-------|--------|-------|
| Color contrast | Pass | All text meets 4.5:1 |
| Image alt text | N/A | Decorative icons use aria-hidden |
| Form labels | N/A | Toggle uses proper radio group |
| ARIA validity | Pass | No errors |
| Heading hierarchy | Pass | Card titles are h3 under page h2 |
| Document landmarks | Pass | Section role with aria-label |

### Manual (Keyboard)

| Check | Status | Notes |
|-------|--------|-------|
| Tab order | Pass | Toggle → Card 1 CTA → Card 2 CTA → Card 3 CTA |
| Focus visibility | Pass | Focus ring on toggle and CTA buttons |
| Button activation | Pass | Enter/Space work on toggle and CTAs |
| Keyboard traps | Pass | No traps |

## Verdict

- **Recommendation**: Request Changes
- **Blockers**: 1
- **High-Priority**: 1
- **Medium-Priority**: 1
- **Nits**: 1
```
