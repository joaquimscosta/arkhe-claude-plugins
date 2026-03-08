# Prototype — Examples

## Example 1: Basic Component

**Command:**
```
/prototype minimalist todo list
```

**Output:**
```
Prototype generated:
  .prototype/index.html                                (comparison view)
  .prototype/01-todo-list-risograph-press.html         (Tactile Risograph Press)
  .prototype/02-todo-list-wireframe-suspension.html    (Kinetic Wireframe Suspension)
  .prototype/03-todo-list-obsidian-grid.html           (Obsidian Facet Grid)

Open in browser: open .prototype/index.html
Generate variations: /prototype --vary 1
```

Each HTML file contains a complete, self-contained page with:
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
Prototype generated:
  ./mockups/index.html                                (comparison view)
  ./mockups/01-dashboard-ceramic-contour.html         (Ceramic Contour Map)
  ./mockups/02-dashboard-neon-pulse-grid.html         (Neon Pulse Grid)
  ./mockups/03-dashboard-paper-ledger-fold.html       (Paper Ledger Fold)

Open in browser: open ./mockups/index.html
```

---

## Example 3: Generating Variations

After generating the initial prototype, request variations of a specific artifact:

**Command:**
```
/prototype --vary 2
```

This reads `manifest.json` to find artifact 2, then generates 3 radical redesigns:

**Output:**
```
Variations of artifact 2 (Kinetic Wireframe Suspension):
  .prototype/todo-list-wireframe-suspension-var-1.html  (Volcanic Ember Fracture)
  .prototype/todo-list-wireframe-suspension-var-2.html  (Folded Vellum Sheets)
  .prototype/todo-list-wireframe-suspension-var-3.html  (Frost Crystal Lattice)

Open in browser: open .prototype/variations-index.html
```

---

## Example 4: Vague Prompt

The skill handles vague prompts without asking questions:

**Command:**
```
/prototype login form
```

**Output:** 3 complete login forms, each with a radically different visual treatment — one might use frosted glass panels, another raw paper textures, another volcanic dark gradients.

---

## Example 5: Prototype-to-Implementation Pipeline

Use prototyping as the first step of a full design workflow:

**Step 1 — Explore:**
```
/prototype notification center with activity feed
```

**Step 2 — Review the 3 artifacts in the browser and pick a favorite.**

**Step 3 — Implement:**
```
/design-intent implement the UI from .prototype/01-notification-center-risograph-press.html
```

The design-intent-specialist skill will:
- Analyze the prototype HTML for visual patterns
- Map to your project's component library and design tokens
- Implement using your actual framework (React, Vue, etc.)
- Flag any conflicts with established design patterns

**Step 4 — Save patterns:**
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
