# Workflows

## A) Generate (Plan → Render)

1) **Brief** — Capture topic, audience, takeaway, and infographic type.  
2) **Choose template** — Concept Map / Process Flow / Algorithm Breakdown / Comparison Matrix / Architecture Snapshot / How-To Ladder.  
3) **Wireframe** — Create a numbered layout (regions, labels, size).  
4) **Content fill** — Insert text/code into regions (≤80 words per region, add alt text).  
5) **Style tokens** — Define type scale, accent color, neutral palette, and stroke weight.  
6) **Checklist** — Run through `08_Checklist.md` for clarity, hierarchy, flow, and accessibility.  
7) **Render** — Use one of the engines below:  
   ```bash
   # Gemini (structured and precise)
   python3 scripts/generate_infograph.py --engine gemini --mode structured --layout-file layout.json

   # Nano Banana (aesthetic and styled)
   python3 scripts/generate_infograph.py --engine nanobanana --mode structured --layout-file layout.json
````

8. **Export** — Outputs are saved to `./output/`.

---

## B) Improve (Audit → Revise → Re-render)

1. **Ingest** — Load existing infographic (plan, JSON, or image description).
2. **Audit** — Follow `08_Checklist.md`: clarity, flow, hierarchy, accessibility.
3. **Revise** — Simplify structure, shorten labels, fix spacing/contrast issues.
4. **Re-render** — Run either Gemini or Nano Banana as needed.

---

## C) Engine Integration Notes

| Engine          | Purpose                                                  | Strengths                             | Best For                                                    |
| --------------- | -------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------- |
| **Gemini**      | Structured, technical rendering from JSON or text prompt | Accurate, reproducible, layout-aware  | Algorithms, architecture diagrams, process flows            |
| **Nano Banana** | Creative visual rendering using SAE-ALD prompt style     | Aesthetic, expressive, brand-friendly | Styled infographics, marketing visuals, educational posters |

**Recommended Workflow**

1. Use **Gemini** first for technical accuracy.
2. Optionally run **Nano Banana** to style the same layout for visual storytelling or publication.
3. Keep both outputs (`*_image.png` and `*_nanobanana_prompt.txt`) for future reuse.

**Note:** Nano Banana is optional; Gemini is the core engine used in automated runs.

---

## D) Tips for Optimal Output

* Keep prompts concise — one clear takeaway.
* Ensure every region has a labeled purpose.
* Validate color contrast (WCAG AA).
* Avoid over-styling unless using Nano Banana for final polish.
* Always store final images and text prompts in version control for reproducibility.

---

> **Reference**: `NANOBANANA_PROMPTING.md` explains SAE-ALD structure and styling best practices.

```
