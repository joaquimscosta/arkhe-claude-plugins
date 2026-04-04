# Examples

Real-world examples demonstrating different style presets.

---

## Example 1: "Deznode" — Constellation Preset with Depth

### User Input

```
/icon-forge Dev tools platform called "Deznode" - network/constellation feel, warm accents on dark, depth enabled
```

### Brand Discovery (extracted from args)

- **Name**: Deznode
- **Industry**: Developer tools
- **Colors**: Navy dark (#0f1729), Yellow (#f5a623), Coral red (#e74c5e), Slate gray (#6b7d99)
- **Style preset**: Constellation
- **Depth**: Enabled

### Concept Options

1. **Neural Network** — Central chevron hub with organic blob-nodes radiating outward via curved connections. Nodes pulse outward at varied sizes. Progressive complexity: glyph shows just the chevron + 2 accent dots.
2. **Protocol Graph** — Interconnected nodes forming a loose graph structure. Each node is an irregular blob, not a perfect circle. Connections curve naturally between them.
3. **Code Constellation** — Stars/dots of varied sizes arranged in a constellation pattern, with a bold chevron cutting through the center.

### Selected: Concept 1 (Neural Network)

### Generated Master SVG

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="deznode-title">
  <title id="deznode-title">Deznode</title>
  <defs>
    <radialGradient id="glow-red" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ff6b7a"/>
      <stop offset="100%" stop-color="#e74c5e"/>
    </radialGradient>
    <radialGradient id="glow-yellow" cx="50%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#ffd06b"/>
      <stop offset="100%" stop-color="#f5a623"/>
    </radialGradient>
  </defs>
  <style>
    .node-slate { fill: #6b7d99; }
    .node-dark  { fill: #3a4a63; }
    .conn       { fill: none; stroke: #3a4a63; stroke-width: 1.8; opacity: 0.6; }
    .conn-warm  { fill: none; stroke: #e74c5e; stroke-width: 1.5; opacity: 0.4; }
    .chevron    { fill: url(#glow-yellow); }
    .dot-red    { fill: url(#glow-red); }
  </style>

  <!-- Connections — curved bezier paths, NOT straight lines -->
  <path class="conn" d="M 38,42 C 30,30 22,28 18,32"/>
  <path class="conn" d="M 38,48 C 28,55 20,62 18,68"/>
  <path class="conn" d="M 62,42 C 68,30 78,22 82,25"/>
  <path class="conn-warm" d="M 62,52 C 70,58 76,62 80,65"/>
  <path class="conn" d="M 50,38 C 48,28 42,18 38,14"/>

  <!-- Blob nodes — irregular shapes, NOT perfect circles -->
  <path class="node-slate" d="M 14,28 C 12,24 16,20 20,22 C 24,24 24,30 22,34 C 20,38 14,36 12,32 Z"/>
  <path class="node-dark" d="M 12,64 C 10,60 14,56 18,58 C 22,60 24,66 22,70 C 20,74 14,72 12,68 Z"/>
  <path class="node-slate" d="M 78,20 C 76,16 80,12 84,14 C 88,16 90,22 88,26 C 86,30 80,28 78,24 Z"/>
  <path class="node-dark" d="M 34,8 C 32,4 36,2 40,4 C 44,6 44,12 42,16 C 40,18 34,16 34,12 Z"/>

  <!-- Accent nodes with radial gradient glow -->
  <circle class="dot-red" cx="82" cy="65" r="7"/>
  <circle class="dot-red" cx="22" cy="78" r="5" opacity="0.7"/>

  <!-- Central chevron — the glyph-tier anchor -->
  <path class="chevron" d="M 38,35 L 55,50 L 38,65 L 44,65 L 62,50 L 44,35 Z"/>

  <!-- Particle trail behind chevron -->
  <circle fill="#f5a623" cx="30" cy="46" r="1.5" opacity="0.8"/>
  <circle fill="#f5a623" cx="26" cy="48" r="1.2" opacity="0.6"/>
  <circle fill="#f5a623" cx="22" cy="50" r="1" opacity="0.4"/>
  <circle fill="#f5a623" cx="32" cy="52" r="1.3" opacity="0.7"/>
  <circle fill="#f5a623" cx="28" cy="54" r="1" opacity="0.5"/>
</svg>
```

### Glyph-Tier Favicon Variant

At 16-32px, the nodes and connections disappear. Only the chevron and accent dots survive:

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="deznode-fav">
  <title id="deznode-fav">Deznode</title>
  <style>
    :root { color-scheme: light dark; }
    .chevron { fill: #f5a623; }
    .dot     { fill: #e74c5e; }
    @media (prefers-color-scheme: dark) {
      .chevron { fill: #ffd06b; }
      .dot     { fill: #ff6b7a; }
    }
  </style>
  <path class="chevron" d="M 28,28 L 58,50 L 28,72 L 38,72 L 68,50 L 38,28 Z"/>
  <circle class="dot" cx="76" cy="38" r="7"/>
  <circle class="dot" cx="76" cy="62" r="5"/>
</svg>
```

### Monochrome Variant (Phase 3b)

All colors replaced with `currentColor` — inherits color from CSS context:

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="deznode-mono">
  <title id="deznode-mono">Deznode</title>
  <!-- Connections -->
  <path fill="none" stroke="currentColor" stroke-width="1.8" opacity="0.4" d="M 38,42 C 30,30 22,28 18,32"/>
  <path fill="none" stroke="currentColor" stroke-width="1.8" opacity="0.4" d="M 62,42 C 68,30 78,22 82,25"/>
  <!-- Blob nodes as filled currentColor -->
  <path fill="currentColor" opacity="0.3" d="M 14,28 C 12,24 16,20 20,22 C 24,24 24,30 22,34 C 20,38 14,36 12,32 Z"/>
  <path fill="currentColor" opacity="0.3" d="M 78,20 C 76,16 80,12 84,14 C 88,16 90,22 88,26 C 86,30 80,28 78,24 Z"/>
  <!-- Central chevron -->
  <path fill="currentColor" d="M 38,35 L 55,50 L 38,65 L 44,65 L 62,50 L 44,35 Z"/>
  <!-- Accent dots -->
  <circle fill="currentColor" cx="82" cy="65" r="7" opacity="0.6"/>
</svg>
```

### Script Invocation

```bash
uv run .../generate_assets.py \
  --svg ./master-icon.svg \
  --dark-svg ./favicon.svg \
  --bg-color "#0f1729" \
  --name "Deznode" \
  --theme-color "#f5a623" \
  --output-dir ./brand-assets
```

---

## Example 2: "Skola.dev" — Illustrative Preset with Depth

### User Input

```
/icon-forge Educational platform "Skola.dev" - learning, warm colors, illustrative, depth
```

### Brand Discovery (extracted from args)

- **Name**: Skola.dev
- **Industry**: Education / Developer learning
- **Colors**: Coral (#ff6b6b), Teal (#4ecdc4), Gold (#f7b731), Deep navy (#1a1a2e)
- **Style preset**: Illustrative
- **Depth**: Enabled

### Concept Options

1. **Code Sailboat** — A warm-toned sailboat with layered color-block sails. The hull is a gentle curve. Represents a journey of learning — setting sail into code. Layered `<g>` groups build the scene.
2. **Wave of Knowledge** — A flowing organic wave with embedded code brackets `< >`. Warm gradient from coral to teal.
3. **Compass Rose** — A stylized compass with code symbols at cardinal points. Warm color palette.

### Selected: Concept 1 (Code Sailboat)

### Generated Master SVG

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="skola-title">
  <title id="skola-title">Skola.dev</title>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffe8cc"/>
      <stop offset="100%" stop-color="#ffd4a8"/>
    </linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#4ecdc4"/>
      <stop offset="100%" stop-color="#3ab5ad"/>
    </linearGradient>
  </defs>
  <style>
    .sail-coral { fill: #ff6b6b; }
    .sail-gold  { fill: #f7b731; }
    .hull       { fill: #1a1a2e; }
    .mast       { fill: #1a1a2e; }
    .flag       { fill: #4ecdc4; }
  </style>

  <!-- Background: warm sky gradient -->
  <rect fill="url(#sky)" width="100" height="100" rx="8"/>

  <!-- Water layer — organic wave, not a straight line -->
  <g class="water-layer">
    <path fill="url(#water)" d="M 0,62 C 15,58 30,64 50,60 C 70,56 85,63 100,59 L 100,100 L 0,100 Z"/>
    <!-- Secondary wave for depth -->
    <path fill="#3ab5ad" opacity="0.5" d="M 0,68 C 20,64 40,70 60,66 C 80,62 90,67 100,65 L 100,100 L 0,100 Z"/>
  </g>

  <!-- Sailboat -->
  <g class="boat" transform="translate(2, 0)">
    <!-- Mast -->
    <rect class="mast" x="47" y="18" width="3" height="45" rx="1"/>

    <!-- Main sail — coral color block -->
    <path class="sail-coral" d="M 50,20 C 65,28 72,42 68,58 L 50,58 Z"/>

    <!-- Jib sail — gold color block, overlapping -->
    <path class="sail-gold" d="M 47,22 C 32,30 28,45 30,56 L 47,56 Z"/>

    <!-- Hull — smooth organic curve -->
    <path class="hull" d="M 28,60 C 30,56 38,54 50,54 C 62,54 70,56 72,60 C 68,66 32,66 28,60 Z"/>

    <!-- Small flag at mast top -->
    <path class="flag" d="M 50,18 L 58,14 L 50,11 Z"/>
  </g>

  <!-- Subtle wave foam dots -->
  <circle fill="#ffffff" cx="20" cy="62" r="1" opacity="0.6"/>
  <circle fill="#ffffff" cx="75" cy="60" r="1.2" opacity="0.5"/>
  <circle fill="#ffffff" cx="90" cy="63" r="0.8" opacity="0.4"/>
</svg>
```

### Dark-Mode Favicon SVG

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="skola-fav">
  <title id="skola-fav">Skola.dev</title>
  <style>
    :root { color-scheme: light dark; }
    .bg   { fill: #faf5ef; }
    .sail1 { fill: #ff6b6b; }
    .sail2 { fill: #f7b731; }
    .hull  { fill: #1a1a2e; }
    .wave  { fill: #4ecdc4; }
    @media (prefers-color-scheme: dark) {
      .bg    { fill: #1a1a2e; }
      .sail1 { fill: #ff8a8a; }
      .sail2 { fill: #ffd06b; }
      .hull  { fill: #e0e0ff; }
      .wave  { fill: #5ee6dc; }
    }
  </style>
  <rect class="bg" width="100" height="100" rx="12"/>
  <!-- Simplified sailboat for favicon -->
  <rect class="hull" x="47" y="20" width="3" height="42" rx="1"/>
  <path class="sail1" d="M 50,22 C 64,30 68,45 66,58 L 50,58 Z"/>
  <path class="sail2" d="M 47,24 C 34,32 30,46 32,56 L 47,56 Z"/>
  <path class="hull" d="M 30,60 C 32,56 40,54 50,54 C 60,54 68,56 70,60 C 66,66 34,66 30,60 Z"/>
  <path class="wave" d="M 0,68 C 20,63 50,70 80,64 C 90,62 100,66 100,66 L 100,100 L 0,100 Z"/>
</svg>
```

### Script Invocation (Next.js detected)

```bash
uv run .../generate_assets.py \
  --svg ./master-icon.svg \
  --dark-svg ./favicon.svg \
  --bg-color "#faf5ef" \
  --name "Skola.dev" \
  --theme-color "#ff6b6b" \
  --framework nextjs \
  --output-dir ./brand-assets
```

---

## Example 3: "Papia Studio" — Symbolic Preset, Flat

### User Input

```
/icon-forge "Papia Studio" - language preservation tools for Cape Verdean Kriolu, symbolic, flat
```

### Brand Discovery (extracted from args)

- **Name**: Papia Studio
- **Industry**: Language tools / Cultural preservation
- **Colors**: Indigo (#4355db), Soft white (#f5f5f7)
- **Style preset**: Symbolic
- **Depth**: Flat

### Concept Options

1. **Speech Pen** — A pen nib merged with a speech bubble. The pen represents writing/creation; the bubble represents spoken language. A small star inside symbolizes the spark of preservation. Uses `fill-rule="evenodd"` for the star cutout.
2. **Sound Wave Script** — Audio waveform flowing out of a stylized document. Represents the bridge between spoken and written Kriolu.
3. **Bridge Letters** — Two letter forms from Kriolu connected by an arch, symbolizing the bridge between tradition and digital tools.

### Selected: Concept 1 (Speech Pen)

### Generated Master SVG

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="papia-title">
  <title id="papia-title">Papia Studio</title>
  <style>
    .primary { fill: #4355db; }
    .accent  { fill: none; stroke: #4355db; stroke-width: 2.5; stroke-linecap: round; }
  </style>

  <!-- Speech bubble — organic rounded shape, not a perfect rectangle -->
  <path class="primary" fill-rule="evenodd" d="
    M 25,18 C 25,12 75,12 75,18
    L 75,55 C 75,61 58,61 52,61
    L 45,72 L 42,61
    C 36,61 25,61 25,55 Z
    M 50,30 L 52.5,37.5 L 60,37.5 L 54,42 L 56.5,50 L 50,45 L 43.5,50 L 46,42 L 40,37.5 L 47.5,37.5 Z
  " />

  <!-- Pen nib extending from top-right of bubble -->
  <line class="accent" x1="68" y1="18" x2="80" y2="6"/>
  <line class="accent" x1="78" y1="8" x2="82" y2="4"/>

  <!-- Sparkle lines radiating from pen tip -->
  <line class="accent" stroke-width="1.5" x1="84" y1="4" x2="88" y2="2" opacity="0.7"/>
  <line class="accent" stroke-width="1.5" x1="82" y1="2" x2="84" y2="-2" opacity="0.5"/>
  <line class="accent" stroke-width="1.5" x1="86" y1="6" x2="90" y2="6" opacity="0.6"/>
</svg>
```

**How the symbolism works**: The speech bubble represents Kriolu as a spoken language. The star cutout (via `fill-rule="evenodd"`) represents cultural value and preservation. The pen nib extending from the bubble bridges spoken word to written/digital form. The sparkle lines convey active creation.

### Dark-Mode Favicon SVG

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="papia-fav">
  <title id="papia-fav">Papia Studio</title>
  <style>
    :root { color-scheme: light dark; }
    .bg { fill: #f5f5f7; }
    .fg { fill: #4355db; }
    @media (prefers-color-scheme: dark) {
      .bg { fill: #1a1a2e; }
      .fg { fill: #8b9cf7; }
    }
  </style>
  <rect class="bg" width="100" height="100" rx="12"/>
  <path class="fg" fill-rule="evenodd" d="
    M 25,20 C 25,14 75,14 75,20
    L 75,58 C 75,64 58,64 52,64
    L 45,75 L 42,64
    C 36,64 25,64 25,58 Z
    M 50,32 L 52.5,39.5 L 60,39.5 L 54,44 L 56.5,52 L 50,47 L 43.5,52 L 46,44 L 40,39.5 L 47.5,39.5 Z
  " />
</svg>
```

### Script Invocation

```bash
uv run .../generate_assets.py \
  --svg ./master-icon.svg \
  --dark-svg ./favicon.svg \
  --bg-color "#f5f5f7" \
  --name "Papia Studio" \
  --theme-color "#4355db" \
  --output-dir ./brand-assets
```

---

## Example 4: Existing SVG (Skip to Asset Generation)

### User Input

```
/icon-forge --svg ./src/assets/logo.svg
```

### Workflow

Phases 1-3 are skipped. The skill validates the SVG exists, uses it as both master and favicon (no dark mode variant), and runs the generation script:

```bash
uv run .../generate_assets.py \
  --svg ./src/assets/logo.svg \
  --output-dir ./brand-assets \
  --name "App"
```

To provide a dark-mode variant: `/icon-forge --svg ./logo.svg --dark-svg ./logo-dark.svg`

---

## Example 5: Design Seed (`--base`)

### User Input

```
/icon-forge --base ./old-logo.svg organic, depth
```

### Workflow

The skill reads `old-logo.svg`, analyzes its structure, and presents:

```
Base SVG Analysis:
  Shapes:  2 circles, 1 rect, 1 polygon
  Colors:  #333333, #0066cc
  Style:   Geometric — flat, symmetric, sharp edges
  Issues:  No <title>, no role="img", viewBox is 0 0 512 512
```

Brand Discovery is abbreviated — colors and concept are already known from the base SVG. The user selected **Organic** preset with **depth** enabled. The skill presents:

1. **Cleaned original** — same design with a11y, normalized to 100x100 viewBox, pixel-aligned
2. **Organic reinterpretation** — same concept but with flowing bezier curves, irregular blobs replacing the circles, radial gradients on key shapes

User picks the organic variant, iterates, then the normal pipeline continues (dark mode, monochrome, asset generation).

---

## Example 6: Geometric Preset (Corporate)

### User Input

```
/icon-forge "Vaultix" - fintech security platform, geometric, flat
```

### Style Selection

User chose **Geometric** preset with **flat** depth. The skill applies the geometric technique set: `<circle>`, `<rect>`, `<polygon>`, straight path segments, mathematical symmetry.

### Concept

**Shield Lock** — A geometric shield constructed from clean rectangles with a centered keyhole. Two-tone blue palette. Perfect symmetry, sharp edges, `rx` rounding only on the outer shield.

This preset produces the clean, corporate, mathematical icons that are appropriate for enterprise and fintech brands.
