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
| Style | Minimal, playful, corporate, bold, elegant, techy |
| References | Existing logo, competitor icons, inspiration images |
| Constraints | Must work on dark backgrounds? Existing brand guidelines? |

### Parsing $ARGUMENTS

Extract from the user's arguments:
- **Brand name**: First quoted string or capitalized word
- **Color references**: Hex codes (`#2563eb`), named colors (`blue`, `coral`)
- **Style keywords**: minimal, modern, bold, playful, corporate, techy, elegant
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
   - Start with simple geometric shapes
   - Build up complexity only as needed
   - Test mental model: "Would this be recognizable as a 16x16 favicon?"

3. **SVG Structure Requirements**
   ```xml
   <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
     <!-- No width/height attributes — CSS/props control size -->
     <!-- Colors as CSS classes for dark mode adaptability -->
     <style>
       .primary { fill: #2563eb; }
       .accent  { fill: #1e40af; }
     </style>
     <!-- All paths use coordinates within 0-100 space -->
     <circle class="primary" cx="50" cy="50" r="40"/>
   </svg>
   ```

4. **Validation Checklist**
   - [ ] `viewBox` is `0 0 100 100` (square)
   - [ ] No `width`/`height` attributes on root `<svg>`
   - [ ] No `<text>` elements (text doesn't survive 16px rendering)
   - [ ] No strokes thinner than 2 units
   - [ ] Maximum 3 distinct colors
   - [ ] All paths are closed (end with `Z`)
   - [ ] `xmlns="http://www.w3.org/2000/svg"` attribute present
   - [ ] No embedded raster images (`<image>`)
   - [ ] No external references (`xlink:href` to URLs)

5. **Present to user**
   - Save SVG to a temporary file and suggest opening in browser to preview
   - Describe the design in words alongside the code

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
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
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
Assets directory: [path]
Files generated:  11

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
