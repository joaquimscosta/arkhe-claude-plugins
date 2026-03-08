# Prototype — Detailed Workflow

## Table of Contents

1. [Phase 1: Style Direction](#phase-1-style-direction)
2. [Phase 2: Artifact Generation](#phase-2-artifact-generation)
3. [Phase 3: Output](#phase-3-output)
4. [Variation Workflow](#variation-workflow)
5. [Integration with Design Intent](#integration-with-design-intent)

---

## Phase 1: Style Direction

### How to Generate Style Names

Think of 3 design direction names that each imply a fundamentally different CSS approach. The names serve as creative constraints that force visual diversity — not just color palette changes, but different textures, structures, and motion patterns.

**Name pattern**: `[Adjective] + [Material/Process] + [Form/Action]`

**Tone guide** (invent your own, do not copy):
- "Asymmetrical Rectilinear Blockwork" (Grid-heavy, primary pigments, thick structural strokes, Bauhaus-functionalism vibe)
- "Grainy Risograph Layering" (Tactile paper texture, overprinted translucent inks, dithered gradients)
- "Kinetic Wireframe Suspension" (Floating silhouettes, thin balancing lines, organic primary shapes)
- "Spectral Prismatic Diffusion" (Glassmorphism, caustic refraction, soft-focus morphing gradients)

The reason these work is that each metaphor maps to concrete CSS techniques. "Risograph" implies grain textures and blend modes. "Wireframe" implies thin borders and transparency. "Prismatic" implies backdrop-filter and gradients. If a style name doesn't suggest specific CSS decisions, it's too vague — pick a more physical metaphor.

### Style Name Components

| Component | Examples |
|-----------|----------|
| Adjective | Tactile, Kinetic, Asymmetrical, Spectral, Grainy, Volcanic, Crystalline |
| Material/Process | Risograph, Obsidian, Vellum, Wireframe, Prismatic, Ceramic, Woven |
| Form/Action | Press, Balance, Gridwork, Diffusion, Suspension, Lattice, Cascade |

### Fallback Style Names

If you struggle to produce 3 distinct names, use these defaults:

```json
["Primary Pigment Gridwork", "Tactile Risograph Layering", "Kinetic Silhouette Balance"]
```

---

## Phase 2: Artifact Generation

### Generation Guidance

For each style direction, generate a complete, self-contained HTML page. The style name is your creative constraint — let it drive every CSS decision.

**Key principles:**

1. **Materiality first** — The style metaphor dictates CSS techniques. Consult the mapping table below. If the style says "Risograph", use `feTurbulence` for grain and `mix-blend-mode: multiply`. If it says "Obsidian", use dark gradients and sharp corners. The metaphor is not decorative — it's structural.

2. **Typography matters** — Load Google Fonts via `<link>`. Pair a bold display font (Inter, Space Grotesk, Outfit) with a monospace (JetBrains Mono, Fira Code) for data elements.

3. **Motion reinforces the metaphor** — Entry reveals with `@keyframes fadeIn`, hover transitions on interactive elements (`transform`, `box-shadow`), micro-interactions that feel native to the design metaphor.

4. **IP Safeguard** — No artist names, brand names, or trademarks anywhere.

5. **Bold layout** — Use negative space and hierarchy intentionally. Avoid generic card grids. Try asymmetry, overlapping layers, or unconventional compositions.

6. **Realistic content** — Use real-sounding names, dates, numbers, and labels. Never lorem ipsum.

**Scope**: Each artifact is a focused, single-screen component — typically 100-300 lines of HTML. One viewport, not a full website.

**Output**: Complete `<!DOCTYPE html>` page with inline `<style>`, Google Fonts `<link>`, realistic content, and optional `<script>`. No markdown fences — write raw HTML directly to file.

### Materiality-to-CSS Mapping

This table is the core creative engine. Each metaphor translates to specific CSS techniques:

| Metaphor | CSS Techniques |
|----------|---------------|
| Risograph | `feTurbulence`, grain overlays, `mix-blend-mode: multiply`, overprint colors |
| Obsidian | Dark linear gradients, sharp `border-radius: 0`, subtle reflective `box-shadow` |
| Paper/Vellum | `box-shadow` for depth, off-white `background: #f5f0e6`, serif typography |
| Wireframe | `border: 1px solid`, transparent fills, `border-style: dashed`, thin weights |
| Glass/Prism | `backdrop-filter: blur(12px)`, `rgba()` backgrounds, prismatic gradients |
| Kinetic/Mobile | `@keyframes`, `transform: rotate()`, floating elements, slow-motion `transition` |
| Ceramic/Porcelain | Smooth gradients, rounded forms, clean whites, subtle glaze highlights |
| Volcanic/Basalt | Cracked textures, ember accents, dark matte backgrounds, orange/red glow |
| Woven/Textile | CSS grid patterns, cross-hatching via `repeating-linear-gradient`, fabric colors |
| Frost/Crystal | Ice-blue palette, sharp geometric facets, `clip-path` for crystal shapes |

### Post-Processing

After generating each artifact, clean the output before writing to file:

1. Strip markdown fences if present:
   - Remove leading `` ```html `` or `` ``` ``
   - Remove trailing `` ``` ``
2. Ensure the output starts with `<!DOCTYPE html>` or `<html>`
3. Verify Google Fonts `<link>` tags are present

---

## Phase 3: Output

### Directory Structure

```
.prototype/                              # Default output directory
├── index.html                           # Side-by-side comparison page
├── manifest.json                        # Artifact position mapping
├── 01-{slug}-{style-1}.html            # Artifact 1
├── 02-{slug}-{style-2}.html            # Artifact 2
└── 03-{slug}-{style-3}.html            # Artifact 3
```

### File Naming

Generate slugs from the prompt and style names:
- Prompt slug: `"minimalist todo list"` → `todo-list`
- Style slug: `"Tactile Risograph Press"` → `risograph-press`
- Full filename: `01-todo-list-risograph-press.html`

Rules:
- Position prefix: `01-`, `02-`, `03-`
- Lowercase, hyphens only
- Remove common words (a, the, an, with, for)
- Max 40 characters per slug
- Keep the most descriptive words

### Manifest File

Write `manifest.json` to track artifact positions (needed for `--vary`):

```json
{
  "prompt": "minimalist todo list",
  "created": "2026-03-08",
  "artifacts": [
    {
      "position": 1,
      "style": "Tactile Risograph Press",
      "file": "01-todo-list-risograph-press.html"
    },
    {
      "position": 2,
      "style": "Kinetic Wireframe Suspension",
      "file": "02-todo-list-wireframe-suspension.html"
    },
    {
      "position": 3,
      "style": "Obsidian Facet Grid",
      "file": "03-todo-list-obsidian-grid.html"
    }
  ]
}
```

### Index Page Template

Generate this `index.html` to display all 3 artifacts:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Prototype: {{prompt}}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0a0a0a;
      color: #e0e0e0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .header {
      padding: 16px 24px;
      border-bottom: 1px solid #1a1a1a;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }
    .header h1 {
      font-size: 16px;
      font-weight: 500;
      color: #fff;
    }
    .header .meta {
      font-size: 12px;
      color: #666;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      flex: 1;
      gap: 1px;
      background: #1a1a1a;
      min-height: 0;
    }
    .panel {
      display: flex;
      flex-direction: column;
      background: #0a0a0a;
      min-height: 0;
    }
    .panel-label {
      padding: 10px 16px;
      font-size: 12px;
      font-weight: 500;
      color: #888;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      border-bottom: 1px solid #1a1a1a;
      flex-shrink: 0;
    }
    iframe {
      flex: 1;
      border: none;
      background: #fff;
      min-height: 0;
    }
    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>{{prompt}}</h1>
    <span class="meta">3 variations &middot; prototype</span>
  </div>
  <div class="grid">
    <div class="panel">
      <div class="panel-label">{{style1}}</div>
      <iframe src="{{file1}}" title="{{style1}}"></iframe>
    </div>
    <div class="panel">
      <div class="panel-label">{{style2}}</div>
      <iframe src="{{file2}}" title="{{style2}}"></iframe>
    </div>
    <div class="panel">
      <div class="panel-label">{{style3}}</div>
      <iframe src="{{file3}}" title="{{style3}}"></iframe>
    </div>
  </div>
</body>
</html>
```

Replace `{{prompt}}`, `{{style1-3}}`, and `{{file1-3}}` with actual values.

### Output Summary

After writing all files, print:

```
Prototype generated:
  .prototype/index.html                          (comparison view)
  .prototype/01-{file1}.html                     ({style1})
  .prototype/02-{file2}.html                     ({style2})
  .prototype/03-{file3}.html                     ({style3})

Open in browser: open .prototype/index.html
Generate variations: /prototype --vary 1
```

---

## Variation Workflow

When user passes `--vary N`:

### Step 1: Read Manifest

Read `manifest.json` from the output directory to find the Nth artifact's filename and style name. If `manifest.json` doesn't exist, glob the directory for files starting with `0N-` and infer the original prompt from the filenames.

### Step 2: Read Existing Artifact

Read the HTML file to understand the current design — its layout, color palette, typography, and structural approach. This context helps generate variations that are genuinely different rather than adjacent.

### Step 3: Generate 3 Variations

For each variation:
- Invent a unique design persona name based on a NEW physical metaphor (different from the original and from each other)
- Let the metaphor's visual language drive every CSS decision
- Generate a complete, self-contained HTML page
- Each variation should be dramatically different — different textures, structures, and motion patterns

The goal is radical divergence. If the original was dark and angular, one variation might be light and organic. If it used heavy borders, a variation might use no borders at all.

### Step 4: Write Variation Files

- Name: `{original-slug}-var-1.html`, `{original-slug}-var-2.html`, `{original-slug}-var-3.html`
- Update or create a `variations-index.html` showing the 3 variations side-by-side
- Update `manifest.json` with a `variations` array for the varied artifact

---

## Integration with Design Intent

After prototyping, users can feed their preferred artifact into the full design-intent workflow:

1. **Pick a favorite**: User identifies which of the 3 artifacts they prefer
2. **Run `/design-intent`**: Reference the prototype HTML as the visual reference
   ```
   /design-intent implement the UI from .prototype/01-todo-list-risograph-press.html
   ```
3. **The design-intent-specialist skill** will:
   - Analyze the HTML for layout, colors, typography, spacing
   - Check existing design intent patterns for conflicts
   - Implement using the project's actual component library and design system
4. **Save patterns**: Run `/save-patterns` to capture any new design decisions

This creates a pipeline: **rapid exploration** (prototype) → **production implementation** (design-intent).
