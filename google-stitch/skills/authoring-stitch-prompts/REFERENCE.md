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

## 4. Common Pitfalls

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

## 5. Advanced Usage

**With Spec Files**  
When input comes from structured specs:
- Read section headers as screens
- Convert bullet points to Stitch layout directives
- Merge style notes into concise visual cues

**With Uploaded Wireframes / Images**  
- Mention their purpose explicitly: “Use uploaded image as layout reference, modernize typography.”

---

## 6. Validation Checklist

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

## 7. Tone and Formatting

- Use imperative, professional tone.
- Prefer Markdown-style bulleting.
- Avoid conversational framing.
- Output must be ready to paste directly into Stitch.

---

## 8. Iteration & Experimentation

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
