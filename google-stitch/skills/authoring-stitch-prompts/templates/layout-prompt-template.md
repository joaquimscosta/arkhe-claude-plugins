# Layout Prompt Template

This template provides the structure for generating foundation/wireframe layout prompts for Google Stitch.

## Purpose

Layout prompts create the **spatial structure and regional organization** of multi-component pages. They are self-contained, use generic descriptive terms, and work independently in Stitch as foundation prompts.

## Key Principles

- **Generic descriptive terms**: "metrics section", "chart area" (NOT "kpi-cards component", file references)
- **Foundation-focused**: High-level purpose and spatial relationships (NOT implementation details)
- **Standalone usable**: Must work in Stitch without other prompts or file context
- **Concise**: Target 150-200 words maximum

## Template Structure

```
Design a [platform] [page/screen type] for [purpose].

Include:
- [Region name] with [generic component description] ([spatial position], [key behavior])
- [Region name] with [generic component description] ([relative position], [interaction pattern])
- [Region name] for [purpose] ([position], [relationship to other regions])

Interactions:
- [How regions relate/communicate at high level]
- [Primary user flows between sections]

Style: [page-level style cues: layout mood, spacing approach, visual hierarchy]

Optimize for [page-level concerns: responsiveness, scrolling, transitions]
```

## Component Guidelines

### Region Names (Generic, Descriptive)
- ✅ "Top section", "Main content area", "Side panel", "Header region"
- ✅ "Left sidebar", "Primary workspace", "Activity feed"
- ❌ "component-1", "kpi-cards section", "revenue-chart area"

### Component Descriptions (Purpose-Focused)
- ✅ "key performance metrics (4 cards with primary KPIs)"
- ✅ "revenue analytics chart (interactive, time-filterable)"
- ✅ "recent subscription activity (scrollable list)"
- ❌ "4 metric cards with sparklines showing delta percentages" (too detailed)
- ❌ "line chart component" (too vague)

### Spatial Positioning
- Use relative positioning: "below metrics", "right of chart", "above fold"
- Include proportions: "60% width", "full width", "spanning height"
- Specify grid patterns: "4-column grid", "3×3 grid", "single column"

### Interactions (High-Level Only)
- ✅ "Metric cards filter chart when clicked"
- ✅ "Chart time range updates all sections"
- ❌ "Click handler triggers Redux action to update chart state" (too technical)

## Example: Analytics Dashboard

```
Design a web dashboard page for SaaS analytics overview.

Include:
- Top section with key performance metrics (4-column grid spanning full width, cards displaying primary KPIs)
- Main content area with revenue analytics chart (below metrics, left side 60% width, interactive time controls)
- Side panel with recent subscription activity (right of chart, 40% width, scrollable list)

Interactions:
- Metric cards filter chart and activity panel when clicked
- Chart time range selector updates entire page data
- Activity panel scrolls independently from main content

Style: clean dashboard aesthetic, ample whitespace, card-based sections, subtle depth

Optimize for desktop-first responsive layout, smooth transitions between filtered states
```

## Example: Landing Page

```
Design a responsive web landing page for SaaS product marketing.

Include:
- Hero section with headline and primary call-to-action (full width, above fold, centered content)
- Feature highlights grid (below hero, 3-column layout, icon-led descriptions)
- Social proof section with testimonial cards (below features, 2-column alternating layout)
- Footer with navigation links (bottom, multi-column layout)

Interactions:
- Hero CTA scrolls to feature section smoothly
- Feature cards expand on hover to show more details
- Testimonials rotate automatically every 5 seconds

Style: modern, bold typography, vibrant gradients, generous spacing, playful yet professional

Optimize for mobile-first responsive design, fast initial render, smooth scroll animations
```

## Validation Checklist

Before finalizing layout prompt:

- [ ] Uses generic descriptive terms (no file references or component names)
- [ ] Includes spatial relationships between all regions
- [ ] Specifies high-level interactions between regions
- [ ] Under 200 words (foundation-focused, not over-detailed)
- [ ] Independently usable in Stitch without other context
- [ ] Includes page-level style cues
- [ ] Addresses page-level optimization concerns

## Usage Notes

**When to generate layout prompts:**
- 2+ distinct UI components mentioned
- Full page/screen keywords (dashboard, page, screen, app)
- Multiple regions (header + content, sidebar + main)
- Layout structure keywords (grid, sections, panels, areas)

**Single-file format with --- separators:**

Each page/feature is saved as **one Markdown file** containing layout + all components:

```markdown
<!-- Layout: {Title Case Name} -->
[layout prompt content]

---

<!-- Component: {Title Case Name} -->
[component prompt content]

---

<!-- Component: {Title Case Name} -->
[component prompt content]
```

**File naming:**
- Standard (≤6 prompts): `.google-stitch/prompts/{page-slug}-v{version}.md`
- Split files (>6 prompts): `.google-stitch/prompts/{page-slug}-part{N}-v{version}.md`

**Examples:**
- `analytics-dashboard-v1.md` (layout + 3 components = 4 prompts)
- `landing-page-v1.md` (layout + 2 components = 3 prompts)
- `admin-panel-part1-v1.md` (layout + 5 components = 6 prompts)
- `admin-panel-part2-v1.md` (2 remaining components = 2 prompts)

**6-Prompt Stitch limit:**
- Stitch can generate maximum 6 screens/components at once
- Files automatically split when >6 prompts needed
- Part 1 always contains layout + first 5 components (6 total)
- Subsequent parts contain max 6 components each
- Users must process part files sequentially in Stitch

**Relationship to component prompts:**
- All prompts for a page/feature combined in one file
- Layout prompt = Foundation/wireframe (first section)
- Component prompts = Detailed specifications (following sections)
- Each section independently usable when separated by `---`
- No cross-references between sections
- File can be copy-pasted directly into Stitch
