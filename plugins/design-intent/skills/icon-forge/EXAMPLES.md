# Examples

Real-world examples of the Icon Forge skill.

---

## Example 1: Fintech App (Interactive Discovery)

### User Input

```
/icon-forge Modern fintech app called "Pulse" - blue gradient, minimal
```

### Brand Discovery (extracted from args)

- **Name**: Pulse
- **Industry**: Fintech
- **Colors**: Blue (#2563eb primary)
- **Style**: Modern, minimal

### Concept Options Presented

1. **Pulse Wave** - Abstract heartbeat/pulse line in a circle — represents monitoring and vitality
2. **Signal Dot** - Concentric radiating circles — suggests a pulse/signal expanding outward
3. **P Shield** - Geometric letter P integrated into a shield shape — conveys trust and security

### Selected: Concept 2 (Signal Dot)

### Generated Master SVG

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <style>
    .ring { fill: none; stroke: #2563eb; stroke-width: 3; }
    .dot  { fill: #2563eb; }
    .ring-outer { opacity: 0.3; }
    .ring-mid   { opacity: 0.6; }
  </style>
  <circle class="ring ring-outer" cx="50" cy="50" r="42"/>
  <circle class="ring ring-mid" cx="50" cy="50" r="28"/>
  <circle class="dot" cx="50" cy="50" r="14"/>
</svg>
```

### Dark-Mode Favicon SVG

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root { color-scheme: light dark; }
    .ring { fill: none; stroke: #2563eb; stroke-width: 3; }
    .dot  { fill: #2563eb; }
    .ring-outer { opacity: 0.3; }
    .ring-mid   { opacity: 0.6; }
    @media (prefers-color-scheme: dark) {
      .ring { stroke: #60a5fa; }
      .dot  { fill: #60a5fa; }
    }
  </style>
  <circle class="ring ring-outer" cx="50" cy="50" r="42"/>
  <circle class="ring ring-mid" cx="50" cy="50" r="28"/>
  <circle class="dot" cx="50" cy="50" r="14"/>
</svg>
```

### Script Invocation

```bash
uv run .../generate_assets.py \
  --svg ./master-icon.svg \
  --dark-svg ./favicon.svg \
  --bg-color "#ffffff" \
  --name "Pulse" \
  --theme-color "#2563eb" \
  --output-dir ./brand-assets
```

### Generated Assets

```
brand-assets/
  favicon.ico              (1.3 KB)
  favicon.svg              (0.5 KB)
  apple-touch-icon.png     (2.8 KB)
  icon-192.png             (3.1 KB)
  icon-512.png             (8.7 KB)
  icon-maskable-192.png    (2.5 KB)
  icon-maskable-512.png    (7.2 KB)
  icon-1024.png            (18.4 KB)
  master-icon.svg          (0.4 KB)
  manifest.webmanifest     (0.6 KB)
  _html-snippet.html       (0.3 KB)
```

---

## Example 2: Existing SVG (Skip to Asset Generation)

### User Input

```
/icon-forge --svg ./src/assets/logo.svg
```

### Workflow

Phases 1-3 are skipped entirely. The skill:

1. Validates `./src/assets/logo.svg` exists and contains valid SVG
2. Uses the same SVG as both master and favicon (no dark mode variant)
3. Runs the generation script:

```bash
uv run .../generate_assets.py \
  --svg ./src/assets/logo.svg \
  --output-dir ./brand-assets \
  --name "App"
```

4. Presents generated files and HTML snippet

### Tip

To also provide a dark-mode variant, create it manually first:
```
/icon-forge --svg ./logo.svg --dark-svg ./logo-dark.svg
```

Note: The `--dark-svg` flag is passed through to the script as an argument.

---

## Example 3: Education Platform (Full Interactive)

### User Input

```
/icon-forge
```

### Interactive Discovery

**Claude asks:**
> What's the brand name and industry?

**User:** "Learnify - an online education platform for kids"

**Claude asks:**
> What style are you going for? And do you have brand colors?

**User:** "Playful and friendly. Primary color is coral (#FF6B6B), with a teal accent (#4ECDC4)"

### Concept Options

1. **Open Book** - Stylized open book with a lightbulb rising from the pages
2. **Owl Face** - Friendly geometric owl face (wisdom + approachability)
3. **Star Cap** - Graduation cap with a star accent — achievement meets fun

### Selected: Concept 2 (Owl Face)

### Generated Master SVG

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <style>
    .body { fill: #FF6B6B; }
    .eyes { fill: #ffffff; }
    .pupils { fill: #2d3436; }
    .beak { fill: #4ECDC4; }
  </style>
  <!-- Body: rounded square -->
  <rect class="body" x="15" y="20" width="70" height="65" rx="20"/>
  <!-- Ears -->
  <polygon class="body" points="20,25 35,25 25,8"/>
  <polygon class="body" points="80,25 65,25 75,8"/>
  <!-- Eyes -->
  <circle class="eyes" cx="37" cy="48" r="12"/>
  <circle class="eyes" cx="63" cy="48" r="12"/>
  <circle class="pupils" cx="39" cy="47" r="5"/>
  <circle class="pupils" cx="65" cy="47" r="5"/>
  <!-- Beak -->
  <polygon class="beak" points="50,58 44,68 56,68"/>
</svg>
```

### Framework Detection

Project contains `next.config.ts` and `app/layout.tsx` → detected as **Next.js App Router**. The skill auto-adds `--framework nextjs`.

### Script Invocation

```bash
uv run .../generate_assets.py \
  --svg ./master-icon.svg \
  --dark-svg ./favicon.svg \
  --bg-color "#ffffff" \
  --name "Learnify" \
  --theme-color "#FF6B6B" \
  --framework nextjs \
  --output-dir ./brand-assets
```

### Generated Assets (Next.js-ready)

With `--framework nextjs`, files are named for Next.js App Router conventions:

| File | Notes |
|------|-------|
| `favicon.ico` | Same as default |
| `icon.svg` | Named for Next.js (default: `favicon.svg`) |
| `apple-icon.png` | Named for Next.js (default: `apple-touch-icon.png`) |
| `icon-192.png`, `icon-512.png` | Same as default |
| `icon-maskable-192.png`, `icon-maskable-512.png` | Same as default |
| `icon-1024.png` | Same as default |
| `master-icon.svg` | Same as default |
| `manifest.webmanifest` | Same as default |
| `_nextjs-guide.txt` | Placement guide (default: `_html-snippet.html`) |

### Integration (Next.js App Router)

Copy files to the Next.js project — no renaming needed:

```
app/
├── favicon.ico
├── icon.svg
├── apple-icon.png
├── manifest.webmanifest
└── layout.tsx            (no <link> tags needed)

public/
├── icon-192.png
├── icon-512.png
├── icon-maskable-192.png
└── icon-maskable-512.png
```

Next.js auto-generates `<link>` tags from file-based metadata conventions.
