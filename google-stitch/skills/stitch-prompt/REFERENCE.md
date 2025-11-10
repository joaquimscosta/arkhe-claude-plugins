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
| **One major intent per prompt** | Stitch struggles with multitask prompts | “Add a new filter bar above the table” |
| **Concise, directive language** | Prioritizes clarity and token efficiency | “Create”, “Add”, “Change”, “Replace” |
| **Concrete UI nouns** | Stitch is layout-aware | “cards”, “sidebar”, “CTA button”, “modal” |
| **3–6 style cues max** | Defines vibe without overwhelming model | “minimal, editorial, cream background, serif headings” |
| **Screen-level focus** | Avoids layout resets | “On the dashboard screen, move the KPI cards…” |
| **Explicit spatial relationships** | Stitch maps positional words to coordinates | “Above the chart”, “left of sidebar” |

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
- [ ] ≤ 1,000 words
- [ ] One clear screen or task
- [ ] Uses explicit UI terms
- [ ] Includes 3–6 style cues
- [ ] Includes responsiveness or export detail
- [ ] Avoids overexplaining or repeating context

---

## 7. Tone and Formatting

- Use imperative, professional tone.
- Prefer Markdown-style bulleting.
- Avoid conversational framing.
- Output must be ready to paste directly into Stitch.

---

## References
- [Google Developers Blog – “Introducing Stitch”](https://developers.googleblog.com/en/stitch-a-new-way-to-design-uis/)
- [Google AI Developers Forum – Stitch Prompt Guide](https://discuss.ai.google.dev/t/stitch-prompt-guide/83844)
- [Index.dev – Google Stitch AI Review](https://www.index.dev/blog/google-stitch-ai-review-for-ui-designers)
- [Bitovi – Product Designer’s Review](https://www.bitovi.com/blog/google-stitch-a-product-designers-review)
