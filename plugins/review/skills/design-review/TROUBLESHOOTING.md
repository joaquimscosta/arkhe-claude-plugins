# Design Review Troubleshooting

Common issues when using the design-review skill.

---

## Environment Issues

### No live preview available

**Symptoms**: Cannot execute interaction or responsiveness phases.

**Cause**: No local dev server or staging URL is running.

**Fix**:
- Start the local dev server before running the review
- Provide a staging URL if available
- The skill can still perform code-only review (Phases 6-7) without a live environment, but Phases 1-5 require browser access

### Playwright CLI not installed

**Symptoms**: Browser automation commands fail.

**Fix**:
```bash
npm install -g @playwright/cli@latest
playwright-cli --help
```

Or run `/playwright-setup` to configure interactively.

---

## Viewport Testing Issues

### Responsive issues not detected

**Symptoms**: Report misses layout breakage at certain screen sizes.

**Cause**: Only standard breakpoints were tested, missing between-breakpoint issues.

**Fix**: The skill tests 7 viewport tiers (375-1920px). If you suspect issues at specific sizes, mention the target viewport in your review request.

### Screenshots not captured

**Symptoms**: Report references screenshots but none are attached.

**Cause**: Playwright output directory not configured or not writable.

**Fix**: Run `/playwright-setup` to configure the output directory, or check that `.playwright/cli.config.json` has a valid `outputDir`.

---

## Finding Quality Issues

### Too many aesthetic opinions

**Symptoms**: Report includes subjective design preferences rather than measurable issues.

**Fix**:
- Findings below confidence 7 should be suppressed
- Only measurable failures (contrast ratios, WCAG violations, broken layouts) qualify as Blockers
- Design system violations need a specific token or rule reference

### Accessibility findings seem wrong

**Symptoms**: WCAG violations flagged that the code actually handles.

**Fix**:
- Verify against the actual rendered DOM, not just source code
- Check if ARIA attributes or semantic HTML resolve the flagged issue
- Run axe-core directly for a second opinion: the skill uses automated + manual checks

---

## Output Issues

### Report directory creation fails

**Cause**: Permission denied or invalid path.

**Fix**: Ensure the output directory is writable. Default is `./reviews/design/` relative to the project root.
