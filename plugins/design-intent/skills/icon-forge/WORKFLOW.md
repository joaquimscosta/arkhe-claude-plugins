# Detailed Workflow

Complete process for generating brand icons and platform assets.

---

## Phase 1: Brand Discovery

### Questions to Ask

| Category | Questions |
|----------|-----------|
| Identity | Brand name, tagline, industry/domain |
| Concept | Visual metaphor, symbol, abstract vs literal |
| Colors | Primary brand color (hex), secondary, accent |
| Style | Style preset (Geometric, Organic, Illustrative, Symbolic, Constellation) + grid + depth |
| References | Existing logo, competitor icons, inspiration images |
| Constraints | Must work on dark backgrounds? Existing brand guidelines? |

### Style Presets

Present the style menu during discovery. Recommend a preset based on brand description if one fits naturally.

| Preset | Visual Character | Best For |
|--------|-----------------|----------|
| **Geometric** | Clean shapes, mathematical precision, flat fills, perfect symmetry | Corporate, fintech, enterprise SaaS |
| **Organic** | Flowing curves, irregular blobs, natural asymmetry, soft edges | Creative agencies, wellness, community platforms |
| **Illustrative** | Layered scenes, color blocks, story-driven composition, hand-crafted feel | Education, kids brands, creative tools |
| **Symbolic** | Dual-meaning line art, negative space tricks, conceptual merging | Studios, consultancies, language/communication tools |
| **Constellation** | Connected nodes, network graphs, dot clusters, progressive complexity | Dev tools, data platforms, tech networks |

### Grid Size

After style selection, confirm the coordinate grid:

- **100×100** (default): More coordinate space for complex brand icons with organic curves, bezier paths, and layered compositions. Recommended for Organic, Illustrative, and Constellation presets.
- **24×24**: Industry-standard icon grid (Material Design, Feather, Heroicons). Aligns with the 8px spatial grid. Better for simple, UI-style marks where pixel-perfect alignment matters. Recommended for Geometric and Symbolic presets with simple geometry.

If the user doesn't specify, default to 100×100. The `--grid 24` argument selects the 24×24 grid.

### Depth Toggle

After style selection, ask about depth preference:

- **Flat** (default): Solid fills, no gradients. Clean, universal, safest for all renderers.
- **Depth**: Subtle `<linearGradient>`/`<radialGradient>`, opacity layering, soft shadows via `<filter>`. Adds warmth and dimension but increases SVG complexity.

### Parsing $ARGUMENTS

Extract from the user's arguments:
- **Brand name**: First quoted string or capitalized word
- **Color references**: Hex codes (`#2563eb`), named colors (`blue`, `coral`)
- **Style keywords**: geometric, organic, illustrative, symbolic, constellation, flat, depth
- **Grid**: `--grid 24` for 24×24 viewBox (default: 100×100)
- **`--svg <path>`**: Path to existing SVG — skip to Phase 4

### Skip Conditions

- If `--svg <path>` provided: validate SVG exists, skip directly to Phase 4
- If comprehensive description provided: minimize questions, confirm assumptions

---

## Phase 2: SVG Master Design

### Design Process

1. **Brainstorm 2-3 concepts** based on brand info
   - Describe each concept in 1-2 sentences before generating SVG
   - Present text descriptions first for user direction

2. **Generate SVG code** for chosen concept
   - Apply the style preset's SVG technique guidance (see table below)
   - Start with the Glyph tier silhouette (what 2-4 shapes survive at 16px?)
   - Build up to Mark and Master complexity

3. **SVG Structure Requirements**
   ```xml
   <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="icon-title">
     <title id="icon-title">Brand Name</title>
     <style>
       .primary { fill: #2563eb; }
       .accent  { fill: #1e40af; }
     </style>
     <circle class="primary" cx="50" cy="50" r="40"/>
   </svg>
   ```
   - No `width`/`height` attributes — CSS/props control size
   - `<title>` must be the first child element (accessibility)
   - `role="img"` prevents screen readers from traversing internal elements

4. **Validation Checklist**
   - [ ] `viewBox` is square (`0 0 100 100` for brand icons, or `0 0 24 24` for UI-style marks)
   - [ ] No `width`/`height` attributes on root `<svg>`
   - [ ] No `<text>` elements (text doesn't survive 16px rendering)
   - [ ] No strokes thinner than 2 units in Glyph/Mark tiers (Master may use 1.5+)
   - [ ] Color count within preset limit (1-3 most presets; up to 5 for Illustrative/Constellation)
   - [ ] All paths are closed (end with `Z`)
   - [ ] `xmlns="http://www.w3.org/2000/svg"` attribute present
   - [ ] No embedded raster images (`<image>`)
   - [ ] No external references (`xlink:href` to URLs)
   - [ ] `<title>` element as first child of `<svg>` with brand name
   - [ ] `role="img"` on root `<svg>` element
   - [ ] Filled shapes use integer coordinates (no sub-pixel blur)
   - [ ] Decimal precision limited to 1-2 places

### Style-to-SVG Technique Table

This table is the core creative engine. Each preset maps to specific SVG elements and path strategies:

| Preset | SVG Techniques |
|--------|---------------|
| Geometric | **Filled**. `<circle>`, `<rect>`, `<polygon>`, straight `<path>` L/H/V segments, `rx`/`ry` rounding, mathematical symmetry |
| Organic | **Filled**. Cubic bezier `C`/`S` commands with off-axis control points, `<ellipse>` with unequal rx/ry, irregular blob `<path>` shapes, smooth joins, asymmetric composition |
| Illustrative | **Filled**. Layered `<g>` groups for scene composition, flat color blocks as distinct `<path>` regions, overlapping shapes with opacity, warm multi-color palettes (up to 4-5 colors) |
| Symbolic | **Stroked**. `clip-path` and `fill-rule="evenodd"` for negative space, `stroke="currentColor"` line art, stroke-width variation, boolean path operations |
| Constellation | **Hybrid**. Filled `<circle>` nodes at varied sizes/positions, stroked cubic bezier `<path>` connections (`fill="none"`), `opacity` variation for depth layers, dot clusters |

**Depth add-ons** (when depth toggle is enabled):
- `<linearGradient>`/`<radialGradient>` defined in `<defs>`
- `<filter>` with `feGaussianBlur` for soft glow or shadow effects
- `opacity` layering on overlapping elements
- Color stops that shift from brand primary to a lighter/darker variant

### SVG Path Techniques by Style

**Organic blob** — Use cubic bezier curves with control points pulled away from the straight path to create irregular, amoeba-like shapes:
```xml
<!-- Irregular blob shape — NOT a circle -->
<path d="M 30,50 C 25,30 40,15 55,20 C 70,25 80,40 75,55 C 70,70 55,80 40,75 C 25,70 35,70 30,50 Z" class="primary"/>
```

**Constellation connection** — Curved paths between node circles, not straight lines:
```xml
<!-- Nodes at irregular positions -->
<circle cx="25" cy="60" r="6" class="node"/>
<circle cx="70" cy="35" r="9" class="node-lg"/>
<!-- Curved connection — control points create a natural arc -->
<path d="M 25,60 C 35,40 55,30 70,35" fill="none" stroke-width="2" class="connection"/>
```

**Illustrative layering** — Overlapping groups build a scene:
```xml
<g class="background">
  <path d="M 0,60 C 20,50 40,55 60,50 C 80,45 100,55 100,100 L 0,100 Z" class="water"/>
</g>
<g class="midground">
  <path d="M 45,25 L 50,60 L 40,60 Z" class="mast"/>
  <path d="M 47,25 C 60,30 65,45 55,58 L 50,58 L 50,28 Z" class="sail"/>
</g>
```

**Symbolic negative space** — `fill-rule="evenodd"` cuts inner shapes from outer shapes:
```xml
<!-- Outer speech bubble with inner cutout forming a star -->
<path fill-rule="evenodd" d="
  M 20,15 C 20,10 80,10 80,15 L 80,65 C 80,70 55,70 50,75 L 45,70 C 40,70 20,70 20,65 Z
  M 50,30 L 53,40 L 63,40 L 55,46 L 58,56 L 50,50 L 42,56 L 45,46 L 37,40 L 47,40 Z
" class="primary"/>
```

### Progressive Detail Tiers

Design with three consumption tiers in mind:

| Tier | Size Range | Complexity | Purpose |
|------|-----------|------------|---------|
| **Glyph** | 16-32px | 2-4 shapes, silhouette-grade | Favicon, browser tab |
| **Mark** | 48-192px | Full logomark, moderate detail | App icons, PWA, nav bars |
| **Master** | 512-1024px | Rich detail, gradients, fine curves | App store, hero images, splash |

**Design approach**: Start at the Glyph tier — what 2-4 shapes capture the brand's essence when everything else is stripped away? This is the icon's skeleton. Then build up through Mark (add secondary shapes, color variation) to Master (add depth, decorative elements, fine bezier detail).

For complex designs (e.g., Constellation with many nodes), optionally produce a separate `favicon-glyph.svg` with only the core shapes for the smallest sizes.

### Pixel Alignment Rules

Sub-pixel misalignment causes blur when SVGs are rasterized. Follow these rules, especially at the Glyph tier:

- **Filled shapes**: Keep all edges on integer coordinates (`x="20"`, not `x="20.3"`)
- **Even stroke widths** (2, 4): Align coordinates to whole numbers
- **Odd stroke widths** (1, 3): Offset by 0.5 so the stroke straddles the pixel center (`cx="50.5"`)
- **Decimal precision**: Limit to 1-2 decimal places. `d="M 30.12 50.65"` is visually identical to `d="M 30.123456 50.654321"` at icon scale, and reduces file size

At the Master tier (512-1024px), sub-pixel alignment is less critical because each coordinate maps to multiple rendered pixels. Focus alignment effort on the Glyph tier shapes.

### Fill vs Stroke Strategy

Choose the right rendering approach per style preset:

| Preset | Strategy | Rationale |
|--------|----------|-----------|
| **Geometric** | Filled paths | Mathematical shapes render crisply as filled regions; stroke scaling at small sizes is unpredictable |
| **Organic** | Filled paths | Blob shapes are inherently filled regions; strokes would outline them awkwardly |
| **Illustrative** | Filled paths | Color-block scenes use filled regions by definition |
| **Symbolic** | **Stroked** paths | Line art and negative-space designs rely on stroke weight for visual character |
| **Constellation** | Hybrid | Nodes are filled; connections are stroked with `fill="none"` |

**Why filled paths are the default**: Filled paths bake line thickness into geometry, so they scale predictably from 16px to 1024px. Stroked paths scale proportionally — a 2-unit stroke at 100×100 becomes visually different at 16×16 vs 512×512. For Symbolic presets where stroke character matters, use `vector-effect: non-scaling-stroke` in the CSS if constant stroke width is desired at all sizes.

5. **Present to user**
   - Save SVG to a temporary file and suggest opening in browser to preview
   - Describe the design in words alongside the code
   - Show how the design simplifies across the three tiers

6. **Iterate** based on user feedback until satisfied

### Output
- Save as `master-icon.svg` in the project directory

---

## Phase 3: Dark-Mode Favicon Variant

### When to Create

Always create a dark-mode variant for the favicon SVG. Modern browsers (Chrome, Firefox, Edge) respect `@media (prefers-color-scheme: dark)` inside SVG favicons.

### Color Adaptation Rules

| Light Mode | Dark Mode Adaptation |
|------------|---------------------|
| Dark foreground (#1a1a2e) | Light equivalent (#e0e0ff) |
| Light background (#ffffff) | Dark equivalent (#1a1a2e) |
| Brand primary | Lighter/more saturated version |
| Subtle grays | Inverted or adjusted for dark bg |

### Contrast Requirements

All foreground-to-background color pairs must meet **WCAG 2.1 AA contrast ratio >= 4.5:1**.

### Template

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="fav-title">
  <title id="fav-title">Brand Name</title>
  <style>
    :root { color-scheme: light dark; }
    .bg { fill: #ffffff; }
    .fg { fill: #1a1a2e; }
    .brand { fill: #2563eb; }
    @media (prefers-color-scheme: dark) {
      .bg { fill: #1a1a2e; }
      .fg { fill: #e0e0ff; }
      .brand { fill: #60a5fa; }
    }
  </style>
  <rect class="bg" width="100" height="100" rx="12"/>
  <path class="fg" d="..."/>
  <circle class="brand" cx="50" cy="50" r="20"/>
</svg>
```

### Output
- Save as `favicon.svg` in the project directory

---

## Phase 3b: Monochrome Variant

### Purpose

Generate a `currentColor` monochrome variant of the master SVG. This enables CSS-based theming — the icon inherits color from its parent element, making it usable in navbars, footers, documentation, and any context where brand colors aren't appropriate.

### Process

1. Duplicate the master SVG
2. Replace all `fill` and `stroke` color values with `currentColor`
3. Remove `<style>` blocks, gradients, and filters — the icon should be a single-color silhouette
4. Keep the `<title>` and `role="img"` accessibility attributes

### Template

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="mono-title">
  <title id="mono-title">Brand Name</title>
  <path fill="currentColor" d="..."/>
</svg>
```

### Output
- Save as `monochrome.svg` in the project directory
- Pass to generate_assets.py via `--mono-svg` if the script supports it, otherwise include in the output directory manually

---

## Phase 4: Asset Generation

### Prerequisites

1. Master SVG file exists (from Phase 2 or `--svg` argument)
2. One of these system tools is installed:
   - `rsvg-convert` (recommended): `brew install librsvg`
   - `magick`/`convert`: `brew install imagemagick`
3. `uv` is available for PEP 723 script execution

### Framework Detection

Before running the script, detect the target project's framework:

1. If `next.config.(js|mjs|ts)` exists AND `app/layout.(tsx|jsx|js)` exists → **Next.js App Router**. Add `--framework nextjs` to the script command.
2. Otherwise → omit `--framework` (generic output with `favicon.svg`, `apple-touch-icon.png`).

### Script Invocation

```bash
uv run <absolute-path-to>/skills/icon-forge/scripts/generate_assets.py \
  --svg ./master-icon.svg \
  --dark-svg ./favicon.svg \
  --bg-color "#ffffff" \
  --name "App Name" \
  --short-name "App" \
  --theme-color "#2563eb" \
  --framework nextjs \
  --output-dir ./brand-assets
```

### CLI Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--svg` | Yes | — | Path to master SVG icon |
| `--dark-svg` | No | Same as --svg | Dark-mode SVG for favicon.svg |
| `--output-dir` | No | `./brand-assets` | Output directory |
| `--bg-color` | No | `#ffffff` | Background for apple-touch-icon and maskable icons |
| `--name` | No | `App` | App name in manifest |
| `--short-name` | No | Same as --name | Short name in manifest |
| `--theme-color` | No | Same as --bg-color | Theme color in manifest |
| `--framework` | No | `None` | Target framework for file naming (auto-detected by skill) |

### Generated Files

| File | Size | Format | Purpose |
|------|------|--------|---------|
| `favicon.ico` | 16x16 + 32x32 | ICO | Legacy browsers, Windows taskbar |
| `favicon.svg` | Vector | SVG | Modern browsers with dark mode support |
| `apple-touch-icon.png` | 180x180 | PNG (RGB, solid bg) | iOS/iPadOS Add to Home Screen |
| `icon-192.png` | 192x192 | PNG (RGBA) | Android Chrome home screen |
| `icon-512.png` | 512x512 | PNG (RGBA) | PWA splash screen |
| `icon-maskable-192.png` | 192x192 | PNG (RGB, 80% safe zone) | Android adaptive icon |
| `icon-maskable-512.png` | 512x512 | PNG (RGB, 80% safe zone) | Android adaptive icon |
| `icon-1024.png` | 1024x1024 | PNG (RGB, solid bg) | iOS App Store source |
| `master-icon.svg` | Vector | SVG | Preserved copy of original |
| `manifest.webmanifest` | — | JSON | PWA icon manifest |
| `_html-snippet.html` | — | HTML | Ready-to-paste `<link>` tags |

> **With `--framework nextjs`:** `favicon.svg` → `icon.svg`, `apple-touch-icon.png` → `apple-icon.png`, `_html-snippet.html` → `_nextjs-guide.txt` (App Router placement instructions).

### Optional: SVG Optimization

Before asset generation, optimize the master SVG to reduce file size (typically 50-80% reduction). This is optional but recommended for production use.

**SVGO** (Node.js, recommended):
```bash
npx svgo --multipass master-icon.svg -o master-icon.svg \
  --config='{"plugins":[{"name":"preset-default","params":{"overrides":{"removeViewBox":false,"removeTitle":false}}},"sortAttrs"]}'
```

**scour** (Python):
```bash
pip install scour && scour -i master-icon.svg -o master-icon.svg \
  --set-precision=2 --enable-viewboxing --enable-comment-stripping \
  --shorten-ids --remove-metadata
```

Key optimization rules:
- **Never remove `viewBox`** — it is what makes SVGs scalable
- **Never remove `<title>`** — it provides accessibility
- **Reduce decimal precision** to 2 places for 100×100 viewBox, 1 place for 24×24
- **Strip editor metadata**, empty `<defs>`, identity transforms, and namespace attributes

### Verifying Output

After generation, verify:
- [ ] All 11 files exist in output directory
- [ ] `apple-touch-icon.png` (or `apple-icon.png` with `--framework nextjs`) has NO transparency (RGB mode, not RGBA)
- [ ] `icon-maskable-*.png` have content centered within the inner 80%
- [ ] `favicon.ico` file size > 300 bytes (confirms multiple resolutions)
- [ ] `manifest.webmanifest` is valid JSON with correct icon entries

---

## Phase 5: Integration Output

### HTML Snippet

Present the content of `_html-snippet.html`:

```html
<!-- Favicon Package -- paste into <head> -->
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
```

### Framework-Specific Placement

| Framework | Icon files location | Manifest location | Notes |
|-----------|-------------------|-------------------|-------|
| Next.js (App Router) | `favicon.ico`, `icon.svg`, `apple-icon.png` → `app/`; PWA icons → `public/` | `app/manifest.webmanifest` | Auto-detected: `--framework nextjs` |
| Next.js (Pages) | `public/` directory | `public/manifest.webmanifest` | Default naming works |
| Vite / Vue / React | `public/` directory | `public/manifest.webmanifest` | Default naming works |
| CRA | `public/` directory | `public/manifest.json` (rename) | Default naming works |
| Astro | `public/` directory | `public/manifest.webmanifest` | Default naming works |
| Static HTML | Site root | Site root | Default naming works |

### Next.js App Router Integration

When generated with `--framework nextjs`, place files as follows:

```
your-nextjs-app/
├── app/
│   ├── favicon.ico              ← from brand-assets/
│   ├── icon.svg                 ← from brand-assets/ (auto-detected by Next.js)
│   ├── apple-icon.png           ← from brand-assets/ (auto-detected by Next.js)
│   ├── manifest.webmanifest     ← from brand-assets/
│   └── layout.tsx               (no <link> tags needed)
├── public/
│   ├── icon-192.png             ← from brand-assets/ (referenced by manifest)
│   ├── icon-512.png             ← from brand-assets/
│   ├── icon-maskable-192.png    ← from brand-assets/
│   └── icon-maskable-512.png    ← from brand-assets/
```

Next.js auto-generates `<link>` tags from the file-based metadata — no manual tags or metadata export needed in `layout.tsx`.

### Summary Report

Present a summary like:

```
Brand Icon Generation Complete
================================
Brand:            [name]
Master SVG:       [path]
Favicon SVG:      [path] (with dark mode)
Monochrome SVG:   [path] (currentColor variant)
Assets directory: [path]
Files generated:  11 + monochrome.svg

Favicon package:
  - favicon.ico (16x16 + 32x32)
  - favicon.svg / icon.svg (with dark mode CSS)
  - apple-touch-icon.png / apple-icon.png (180x180)

PWA icons:
  - icon-192.png, icon-512.png
  - icon-maskable-192.png, icon-maskable-512.png

Mobile:
  - icon-1024.png (iOS App Store source)

Integration:
  - manifest.webmanifest
  - _html-snippet.html or _nextjs-guide.txt
```
