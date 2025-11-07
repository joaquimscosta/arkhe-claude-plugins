# Nano Banana Prompting Guide

## Purpose
Nano Banana excels at *creative, styled visual renderings* — especially for educational diagrams, infographics, and minimalist concept visuals. Use it when you need **aesthetic richness** or **visual storytelling** that goes beyond functional structure.

---

## Prompt Structure — SAE-ALD Format
Use the **SAE-ALD** formula for best results:

| Element | Meaning | Example |
|----------|----------|----------|
| **S** – Subject | What you want | "Educational infographic about distributed systems" |
| **A** – Action | What to do | "Illustrate with modular blocks, arrows, and concise labels" |
| **E** – Emotion | Tone or feel | "Balanced, calm, and confident visual hierarchy" |
| **A** – Aesthetic | Style keywords | "Minimalist, flat design, blue-grey palette, clean typography" |
| **L** – Layout | Composition cues | "Centered title, evenly spaced panels, labeled connectors" |
| **D** – Details | Specific visual elements | "Include data flow arrows, code boxes, and annotated callouts" |

Combine these into a compact, natural-language paragraph.

---

## Example Prompt
```

Educational infographic on "Kotlin Coroutines: Structured Concurrency".
Use modular panels with balanced spacing.
Tone: calm and clear.
Style: minimalist tech-diagram, subtle gradients, blue accent lines, no drop shadows.
Show parent/child coroutine scopes with arrows and labels.

````

---

## Best Practices
✅ **Keep visual scope small** — one clear takeaway  
✅ **Use concise, declarative sentences**  
✅ **Avoid “and” chaining**; prefer line-by-line instructions  
✅ **Emphasize layout + tone** over color micro-details  
✅ **Limit palette to 3–5 colors**  
✅ **Mention export intent** (“1K image, web optimized”)  

---

## Checklist
- [ ] SAE-ALD fields filled  
- [ ] 3–7 core elements  
- [ ] Consistent tone (educational, clean)  
- [ ] Explicit layout and spacing directions  
- [ ] Mention contrast or palette constraints  
- [ ] No conflicting instructions  

---

## Integration Tip
When using `scripts/generate_infograph.py`:
```bash
python3 scripts/generate_infograph.py --engine nanobanana --mode structured --layout-file layout.json
````
```
