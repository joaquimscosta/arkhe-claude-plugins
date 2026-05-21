# Prototype — Examples

## Example 1: Basic Component (live preview)

**Command:**
```
/prototype minimalist todo list
```

**Output:**
```
Prototype live preview ready.
  URL:        http://localhost:62477
  Variants:   .prototype/.claude/preview/12345-1779000000/content
  Picks log:  .prototype/.claude/preview/12345-1779000000/state/events.jsonl

  01 — Tactile Risograph Press
  02 — Kinetic Wireframe Suspension
  03 — Obsidian Facet Grid

Click a variant. When you reply I'll read your pick from events.jsonl.
  /prototype --vary N        — generate 3 variations of variant N
  /prototype --continue      — re-read the latest pick
```

The browser opens to a sidebar with 3 variant buttons. Clicking one swaps the iframe canvas to that artifact and logs `{action: 'select-variant', payload: {variant: '02'}, ...}` to `events.jsonl`.

Each artifact HTML file contains a complete, self-contained page with:
- Google Fonts loaded via `<link>`
- Inline `<style>` with all CSS
- Realistic placeholder content (task names, dates, checkboxes)
- Hover effects and entry animations
- Design driven entirely by the style metaphor

---

## Example 2: Custom Output Directory

**Command:**
```
/prototype dashboard with analytics charts --dir ./mockups
```

**Output:**
```
Prototype live preview ready.
  URL:        http://localhost:58432
  Variants:   ./mockups/.claude/preview/12346-1779000050/content
  Picks log:  ./mockups/.claude/preview/12346-1779000050/state/events.jsonl

  01 — Ceramic Contour Map
  02 — Neon Pulse Grid
  03 — Paper Ledger Fold
```

`./mockups/manifest.json` is written at the top of `--dir` so subsequent `/prototype --vary N` and `/prototype --continue --dir ./mockups` resolve correctly.

---

## Example 3: Capture the user's pick

After the user clicks a variant in the browser, the next `/prototype --continue` invocation reads `events.jsonl`:

**Command:**
```
/prototype --continue
```

**Output:**
```
You picked variant 02 — Kinetic Wireframe Suspension
  File: /abs/path/.prototype/.claude/preview/12345-1779000000/content/02-todo-list-wireframe-suspension.html

Next:
  /prototype --vary 2                                     — explore variations of this pick
  /design-intent implement /abs/path/.../02-todo-list-wireframe-suspension.html
```

If the user hasn't clicked yet, `--continue` reports "no pick yet" and reminds them of the URL.

---

## Example 4: Generating Variations

After picking, request variations of the chosen artifact:

**Command:**
```
/prototype --vary 2
```

The skill reads `manifest.json`, opens the artifact, generates 3 radical redesigns using new physical metaphors, writes them as `*-var-1.html`, `-var-2.html`, `-var-3.html` into the live `screen_dir`, and rewrites `99-gallery.html` to surface them. The browser auto-reloads via the file watcher — the user sees the new variations without refreshing.

**Output:**
```
Variations of variant 2 (Kinetic Wireframe Suspension) ready in the live gallery:
  Volcanic Ember Fracture
  Folded Vellum Sheets
  Frost Crystal Lattice

Click one — the gallery has been rebuilt and your browser reloaded.
  /prototype --continue     — read the new pick
```

---

## Example 5: Vague Prompt

The skill handles vague prompts without asking questions:

**Command:**
```
/prototype login form
```

3 complete login forms, each with a radically different visual treatment — one might use frosted glass panels, another raw paper textures, another volcanic dark gradients. All three served live, ready to click.

---

## Example 6: Prototype-to-Implementation Pipeline

Use prototyping as the first step of a full design workflow:

**Step 1 — Explore:**
```
/prototype notification center with activity feed
```

**Step 2 — Click your favorite in the browser.** The pick lands in `events.jsonl`.

**Step 3 — Resolve the pick:**
```
/prototype --continue
```

Output includes the absolute path of the picked artifact.

**Step 4 — Implement:**
```
/design-intent implement the UI from <abs_path-from-continue>
```

The design-intent-specialist skill will:
- Analyze the prototype HTML for visual patterns
- Map to your project's component library and design tokens
- Implement using your actual framework (React, Vue, etc.)
- Flag any conflicts with established design patterns

**Step 5 — Save patterns:**
```
/save-patterns
```

---

## Style Direction Examples by Domain

### E-commerce
- "Embossed Leather Catalog" (Rich textures, gold foil accents, serif typography, warm palette)
- "Neon Marketplace Grid" (Bright accent colors, grid layout, sharp edges, dark background)
- "Watercolor Boutique" (Soft edges, pastel washes, handwritten fonts, organic layout)

### Productivity / SaaS
- "Blueprint Technical Draft" (Precise lines, annotation marks, engineering paper background)
- "Frosted Glass Console" (Blurred panels, translucent layers, minimal chrome, system fonts)
- "Ink Wash Kanban" (Flowing gradients, calligraphic weights, negative space hierarchy)

### Gaming / Entertainment
- "Neon Arcade Cabinet" (Glowing edges, pixel art accents, CRT scan line effects)
- "Holographic Interface" (Translucent panels, sci-fi gradients, angular geometry)
- "Carved Stone Tablet" (Textured surfaces, embossed text, earthy palette, heavy weight)

### Healthcare / Finance
- "Executive Leather Folio" (Rich textures, gold accents, serif typography, conservative palette)
- "Clinical Precision Grid" (High contrast, structured layout, clear data hierarchy, blue/white)
- "Sandstone Data Relief" (Warm neutrals, layered depth, subtle shadows, refined spacing)
