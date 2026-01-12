# Google Stitch Prompt Authoring Reference

This document summarizes Google Stitch's official prompt authoring best practices for UI generation.  
Use it whenever transforming text or specs into optimized Stitch prompts.

---

## Core Goal
Turn natural language or design specs into **short, directive, atomic prompts** for Stitch that produce clean UI layouts and exportable code.

---

## 1. Stitch Prompt Fundamentals

**Stitch prompt = UI specification in natural language**, not chat instructions.  
It defines:
- App concept and flow
- Layout structure
- Visual style and tone
- Export / handoff details

**Output type:** UI layouts + front-end code (HTML/CSS/JSX) + Figma components.

---

## 2. Structure of a Strong Stitch Prompt

**Always include these sections:**

1. **Purpose / context:** What app or screen you’re designing  
2. **Layout directives:** Key sections, hierarchy, and relationships  
3. **Visual style cues (3–6):** Color, typography, mood, tone  
4. **Constraints:** Responsiveness, export goals, or platform (web, mobile)  
5. *(Optional)* Specific change instructions (for iterative edits)

Example:
> Design a responsive web dashboard for a SaaS analytics app.  
> Include: sidebar navigation, header with search + user menu, KPI cards, revenue chart.  
> Style: minimal, enterprise, cool blue tones, modern sans-serif font.  
> Optimize for desktop first, mobile single-column layout.

---

## 3. Prompting Principles

| Principle | Why it matters | Example |
|------------|----------------|----------|
| **One major intent per prompt** | Stitch struggles with multitask prompts | "Add a new filter bar above the table" |
| **Screen-level focus** | Prevents multi-screen confusion | Split "Dashboard + Settings" into 2 prompts |
| **Intent detection** | Ensures atomic prompts | "Reading pane + comments" = 2 intents → 2 prompts |
| **Concise, directive language** | Prioritizes clarity and token efficiency | "Create", "Add", "Change", "Replace" |
| **Concrete UI nouns** | Stitch is layout-aware | "cards", "sidebar", "CTA button", "modal" |
| **3–6 style cues max** | Defines vibe without overwhelming model | "minimal, editorial, cream background, serif headings" |
| **Explicit spatial relationships** | Stitch maps positional words to coordinates | "Above the chart", "left of sidebar" |
| **Accept varied input detail** | Users can provide minimal or detailed briefs | "fitness app" or full feature list both work |

---

## 4. Layout Prompts: Foundation/Wireframe Approach

When generating prompts for **multi-component pages** (2+ components or full screens), create two types of prompts:

1. **Layout prompt** — Foundation/wireframe showing spatial structure
2. **Component prompts** — Detailed specifications for individual elements

### Purpose of Layout Prompts

Layout prompts create the **high-level page structure** that:
- Shows spatial relationships between major regions
- Defines page-level interactions and user flows
- Uses generic descriptive terms (NOT file/component references)
- Works independently in Stitch as a standalone foundation prompt
- Can be enhanced later with detailed component prompts

### Key Characteristics

| Aspect | Layout Prompt | Component Prompt |
|--------|---------------|------------------|
| **Focus** | Page structure & regions | Individual element details |
| **Scope** | Multiple areas/sections | Single component |
| **Detail level** | High-level purpose | Implementation specifics |
| **Terminology** | Generic ("metrics section") | Specific ("4 KPI cards with sparklines") |
| **Interactions** | Cross-region flows | Internal micro-interactions |
| **Word count** | 150-200 words | 150-250 words |
| **Independence** | Standalone foundation | Standalone specification |

### Generic Terminology Guidelines

**✅ Use generic descriptive terms:**
- "key performance metrics section" (purpose-focused)
- "analytics chart area" (function-focused)
- "activity feed panel" (content-focused)
- "top section", "main content area", "side panel" (position-focused)

**❌ Avoid file/component references:**
- "kpi-cards component" (references specific component)
- "revenue-chart-v1" (references file name)
- "subscription-table component" (references implementation)

### Layout Prompt Structure

```
Design a [platform] [page/screen type] for [purpose].

Include:
- [Region] with [generic description] ([spatial position], [key behavior])
- [Region] with [generic description] ([relative position], [interaction])
- [Region] for [purpose] ([position], [relationship to others])

Interactions:
- [How regions relate/communicate at high level]
- [Primary user flows between sections]

Style: [page-level style cues: layout mood, spacing, visual hierarchy]

Optimize for [page-level concerns: responsiveness, scrolling, transitions]
```

### Example: Multi-Component Dashboard

**Layout Prompt (Foundation):**
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

**Component Prompts (Detailed sections in same file):**
Following the layout prompt, separate component sections provide detailed specifications for:
- KPI Metrics: Detailed spec for metric cards with sparklines, deltas, color coding
- Revenue Chart: Detailed spec for interactive line chart with tooltips, annotations
- Subscription Activity: Detailed spec for activity table with avatars, status badges

All sections combined in single file `dashboard/prompt-v1.md`, separated by `---`.

### When to Generate Layout Prompts

**Generate layout prompt when:**
- 2+ distinct UI components mentioned
- Full page/screen keywords present ("dashboard", "page", "screen", "app")
- Multiple regions described (header + content, sidebar + main, navigation + body)
- Layout structure keywords used ("grid", "sections", "panels", "areas")

**Skip layout prompt when:**
- Single isolated component (button, form field, icon)
- Partial update/modification to existing design
- Component is already part of known larger layout

### Feature-Based Directories with --- Separators

**Organization:**
Each feature gets its own directory containing prompts and design artifacts:

```
design-intent/google-stitch/
├── dashboard/
│   ├── prompt-v1.md           (all prompts in one file with --- separators)
│   ├── prompt-v2.md           (version history in same directory)
│   ├── exports/               (Stitch-generated outputs: PNG, SVG, HTML)
│   └── wireframes/            (pre-work mockups and references)
├── landing/
│   ├── prompt-v1.md
│   ├── exports/
│   └── wireframes/
├── settings/
│   ├── prompt-v1.md
│   ├── exports/
│   └── wireframes/
└── admin-panel/
    ├── prompt-v1-part1.md     (split files for >6 prompts)
    ├── prompt-v1-part2.md
    ├── exports/
    └── wireframes/
```

**File Content Structure:**
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

**Naming Convention:**
- Feature directory: `{feature}/` (semantic name, kebab-case)
- Standard (≤6 prompts): `prompt-v{version}.md`
- Split files (>6 prompts): `prompt-v{version}-part{N}.md`
- Subdirectories: `exports/` and `wireframes/` (pre-created)

**Examples:**
- `dashboard/prompt-v1.md` (layout + 3 components = 4 prompts)
- `landing/prompt-v1.md` (layout + 2 components = 3 prompts)
- `admin-panel/prompt-v1-part1.md` (layout + 5 components = 6 prompts)
- `admin-panel/prompt-v1-part2.md` (2 remaining components = 2 prompts)

**HTML Comment Labels:**
- `<!-- Layout: Analytics Dashboard -->` - For layout/foundation prompts
- `<!-- Component: KPI Metrics -->` - For component detail prompts
- Title case names for readability
- Labels help navigate within large files

**6-Prompt Stitch Limit:**
- Stitch can generate maximum 6 screens/components at once
- Files automatically split if >6 prompts needed
- Part 1 always contains layout + first 5 components
- Subsequent parts contain max 6 components each
- Users must process part files sequentially in Stitch

### Using Single-File Prompts in Stitch

**Workflow option 1: Batch generation (recommended)**
1. Copy entire file content
2. Paste into Stitch prompt interface
3. Stitch processes all prompts separated by `---`
4. Generates complete page with all components

**Workflow option 2: Targeted refinement**
1. Copy specific component section (between `---` separators)
2. Paste into Stitch for individual component generation
3. Use for iterative refinement of specific elements

**Workflow option 3: Split files (>6 prompts)**
1. Use part1 file first → generates layout + first 5 components
2. Use part2 file next → generates remaining components
3. Process sequentially due to Stitch's 6-screen limit

**Independence principle:**
Each prompt within the file works standalone when separated by `---`.

---

## 5. Common Pitfalls

❌ Vague prompts  
> “Make it look modern and cool.”  
✅ Instead  
> “Use a clean layout with flat cards, muted blue-gray palette, sans-serif typography.”

❌ Long multi-topic prompts  
> “Add new features, redesign layout, change colors, and make it responsive.”  
✅ Instead  
> Split into 2–3 smaller, focused prompts.

❌ Excessive narrative or chatty phrasing  
> “Can you please create a screen that maybe has some buttons?”  
✅ Instead  
> “Create a settings screen with toggle switches and save button.”

---

## 6. Advanced Usage

**With Spec Files**  
When input comes from structured specs:
- Read section headers as screens
- Convert bullet points to Stitch layout directives
- Merge style notes into concise visual cues

**With Uploaded Wireframes / Images**  
- Mention their purpose explicitly: “Use uploaded image as layout reference, modernize typography.”

---

## 7. Validation Checklist

Before finalizing an optimized Stitch prompt:
- [ ] ≤ 250 words (absolute max 400)
- [ ] One clear screen or task (atomic focus)
- [ ] Uses explicit UI terms (cards, sidebar, buttons, modal)
- [ ] Includes 3–6 style cues (colors, typography, spacing, mood)
- [ ] Includes responsiveness or export detail
- [ ] Avoids overexplaining or repeating context
- [ ] NO `##` markdown headings in output
- [ ] Bullets average 10-20 words each (max 25)
- [ ] NO performance metrics (`<Nkb`, `Nms`, bundle sizes)
- [ ] NO compliance specs (`WCAG X.X XX` format)
- [ ] NO platform parentheticals (`(iOS/Android)`, `(Chrome/Firefox/Safari)`)
- [ ] NO implementation logic (graceful degradation, fallback when unavailable)
- [ ] Matches structure in EXAMPLES.md (directive → bullets → style → constraints)

---

## 8. Tone and Formatting

- Use imperative, professional tone.
- Prefer Markdown-style bulleting.
- Avoid conversational framing.
- Output must be ready to paste directly into Stitch.

---

## 9. Iteration & Experimentation

Stitch works best with iterative refinement:

1. **Start broad, then refine:** Generate initial version from high-level prompt, review output, identify specific elements to improve.
2. **One change per iteration:** Create focused refinement prompt for one element at a time (color, layout, component).
3. **Build incrementally:** Each refinement prompt produces a new version (v1 → v2 → v3).
4. **Explore alternatives:** Try variations by creating multiple prompt versions with different approaches (different color palettes, alternative layouts, varied typography).
5. **Track iterations:** Use the file versioning system (`{component-slug}-v{version}.md`) to maintain history and compare results.

**Experimentation workflow:**
- Generate baseline design (v1)
- Test variation A: different color scheme (v2)
- Test variation B: alternative layout (v3)
- Refine winning approach (v4)

**Best practices:**
- Review Stitch output before next refinement
- Focus refinements on specific visual/spatial concerns
- Maintain atomic focus (don't bundle multiple changes)
- Use git commits to group related prompt iterations

---

## References
- [Google Developers Blog – “Introducing Stitch”](https://developers.googleblog.com/en/stitch-a-new-way-to-design-uis/)
- [Google AI Developers Forum – Stitch Prompt Guide](https://discuss.ai.google.dev/t/stitch-prompt-guide/83844)
- [Index.dev – Google Stitch AI Review](https://www.index.dev/blog/google-stitch-ai-review-for-ui-designers)
- [Bitovi – Product Designer’s Review](https://www.bitovi.com/blog/google-stitch-a-product-designers-review)
