# Stitch Prompt Template

Use this structure when generating optimized Google Stitch prompts.

**CRITICAL:** Output must be a SINGLE BLOCK of text without `##` markdown section headings. Do NOT structure output with headings like "## Layout" or "## Visual Style"—those create PRD-style documents, not Stitch prompts.

---

## Template Structure (for reference only—do NOT use headings in actual output)

**Format:** Directive sentence → bullet list → style cues → constraints (all in one continuous block)

**Example:**

> Design a responsive web dashboard for a project management tool.
> Include: left sidebar (logo, navigation links), top header (search, notifications, user avatar), main section with project cards and progress chart.
> Style: clean, professional, muted blue palette, modern sans-serif, light neutral background.
> Optimize for desktop; maintain consistent 8px spacing and component reuse for export.

---

## Key Requirements

1. **Opening sentence:** Use Stitch verbs (Design/Create/Add/Update) + app/screen description
2. **Layout bullets:** 3-6 items using "Include:", "Add:", or similar prefixes
3. **Style cues:** 3-6 descriptors (colors, typography, spacing, mood)
4. **Constraints:** Responsiveness, platform, accessibility goals

---

## What NOT to Include

❌ **No multi-section headings** like:
```markdown
## Layout & Components
## Visual Style
## Constraints & Behavior
```

❌ **No backend/technical details** like:
- Authentication (JWT, OAuth, Supabase)
- APIs, caching, rate limiting
- Bundle sizes, performance metrics
- Error handling logic
- ARIA implementation details

✅ **Only visual/spatial UI concerns** like:
- Layout structure, components
- Colors, typography, spacing
- Interaction patterns
- Accessibility goals (keyboard nav, screen readers)

---

## Design-Aware Style Cues (When Available)

When design context is discovered from `design-intent/`, enhance style cues with project context.

**Pattern:**
```
Style: [project-type-tone], [design-system-name], [user-provided-cues], [visual-details].
```

**Examples:**

With Enterprise + Fluent UI context:
```
Style: enterprise-grade, professional, Fluent UI styling, deep blue accents, clean sans-serif typography, organized information hierarchy.
```

With Consumer + Material UI context:
```
Style: friendly, engaging, Material Design patterns, vibrant accents, generous whitespace, smooth hover transitions.
```

Without design context (standalone):
```
Style: clean, modern, neutral background, sans-serif typography, subtle shadows.
```

**Key Principle:** Inject high-level descriptors only. Let Stitch infer specific values.

---

## Template Pattern

```
[Imperative verb] a [platform] [app/screen type] for [purpose].

Include:
- [Component 1 with brief description]
- [Component 2 with spatial relationship]
- [Component 3 with interaction pattern]

Style: [3-6 cues: colors, typography, spacing, mood, tone].

Optimize for [responsiveness], [accessibility], [export format].
```

---

## Complete Example

> Design a content engagement toolbar for cultural heritage educational pages optimized for mobile-first responsive design.
>
> Include:
> - Share button with native dialog (mobile) and Facebook/copy link options (desktop)
> - Four emoji reactions (Love, Helpful, Interesting, Thank you) with counts
> - Copy link button with one-click copy and confirmation toast
> - Suggest improvement button opening contact form
> - Print button for browser print dialog
> - Related content grid (3-5 tag-matched items) below toolbar
>
> Style: Clean, inviting, culturally respectful, Ocean Blue (#005A8D), Valley Green (#3E7D5A), Bougainvillea Pink (#D90368), Sunny Yellow (#F7B801), Merriweather headings, Lato body text, 44px touch targets, subtle shadows.
>
> Optimize for mobile-first (320px minimum), full keyboard navigation, screen reader support, dark mode.

---

## Final Checklist

- [ ] <250 words total
- [ ] NO `##` headings in output
- [ ] Starts with imperative verb (Design/Create/Add/Update)
- [ ] 3-6 layout bullets
- [ ] 3-6 style cues
- [ ] NO backend/auth/API/performance details
- [ ] Matches structure in EXAMPLES.md

**Remember:** Output should be paste-ready for Google Stitch—not a planning document.
