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

- **[High-Priority]** The settings form sections are not keyboard-accessible — Tab key skips from the navigation sidebar directly to the footer, bypassing all form controls.
  - **Impact**: Users relying on keyboard navigation cannot access any settings. Violates WCAG 2.1 AA Success Criterion 2.1.1 (Keyboard).
  - **Screenshot**: settings-keyboard-tab-order.png

- **[High-Priority]** On tablet viewport (768px), the two-column layout for "Notification Preferences" overlaps with the sidebar, causing form labels to be cut off.
  - **Impact**: Users on tablet devices cannot read option labels, making the form unusable at this breakpoint.
  - **Screenshot**: settings-tablet-overlap.png

### Medium-Priority / Suggestions

- **[Medium]** The "Delete Account" button has the same visual weight as the "Save Changes" button. Both are solid blue buttons at the same size.
  - **Context**: Destructive actions should be visually differentiated from primary actions to prevent accidental clicks. Consider using a red outline/ghost button for destructive actions.

### Nitpicks

- **Nit:** The spacing between the "Profile" and "Security" section headers (32px) is different from the spacing between "Security" and "Notifications" (24px). Consistent spacing would improve visual rhythm.

## Responsive Summary

| Viewport | Status | Notes |
|----------|--------|-------|
| Desktop (1440px) | Pass | Clean layout, proper spacing |
| Tablet (768px) | Issues | Two-column overlap with sidebar |
| Mobile (375px) | Pass | Single column, good touch targets |

## Accessibility Summary

| Check | Status | Notes |
|-------|--------|-------|
| Keyboard navigation | Issues | Tab order skips form controls |
| Focus states | Pass | Visible focus rings on all interactive elements |
| Semantic HTML | Pass | Proper use of fieldset/legend for form groups |
| Color contrast | Pass | All text meets 4.5:1 ratio |
| Form labels | Pass | All inputs have associated labels |

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

### Nitpicks

- **Nit:** The transition duration for the hover state on ghost buttons (300ms) is slightly longer than primary and secondary buttons (200ms). Matching these would create a more unified feel across variants.

## Responsive Summary

| Viewport | Status | Notes |
|----------|--------|-------|
| Desktop (1440px) | Pass | All states work correctly |
| Tablet (768px) | Pass | Touch targets meet 44px minimum |
| Mobile (375px) | Pass | Full-width buttons display correctly |

## Accessibility Summary

| Check | Status | Notes |
|-------|--------|-------|
| Keyboard navigation | Pass | Tab order correct |
| Focus states | Pass | Visible focus rings on all button variants |
| Color contrast | Pass | Disabled state maintains 3:1 ratio (decorative) |

## Verdict

- **Recommendation**: Approve
- **Blockers**: 0
- **High-Priority**: 0
- **Medium-Priority**: 0
- **Nits**: 1
```
