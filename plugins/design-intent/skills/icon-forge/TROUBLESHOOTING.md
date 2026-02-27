# Troubleshooting

---

## No SVG-to-PNG Converter Found

### Symptoms
```
Error: No SVG-to-PNG converter found.
```

### Cause
The script requires `rsvg-convert` (from librsvg) or `magick`/`convert` (from ImageMagick).

### Solution

**macOS (recommended):**
```bash
brew install librsvg
```

**Alternative (macOS):**
```bash
brew install imagemagick
```

**Ubuntu/Debian:**
```bash
sudo apt-get install librsvg2-bin
```

**Verify:**
```bash
which rsvg-convert  # should print a path
```

---

## uv Not Installed

### Symptoms
```
uv: command not found
```

### Solution
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or via Homebrew:
```bash
brew install uv
```

---

## SVG Unrecognizable at Small Sizes

### Symptoms
- Icon looks like a blob at 16px or 32px
- Details merge together in the favicon

### Cause
The SVG has too much detail, thin strokes, or complex shapes that collapse at small pixel counts.

### Solution
1. Simplify the master SVG: fewer paths, thicker strokes (>= 2 units at 100x100)
2. Remove small decorative elements
3. Use solid fills instead of thin outlines
4. Test by viewing the SVG at actual favicon size:
   ```html
   <img src="master-icon.svg" width="16" height="16">
   <img src="master-icon.svg" width="32" height="32">
   ```

---

## Apple Touch Icon Has Black Background

### Symptoms
- iOS shows black or gray background behind the icon on the home screen

### Cause
The `apple-touch-icon.png` has transparency. iOS fills transparent areas with black.

### Solution
Re-run the script with `--bg-color` set to your brand background color:
```bash
uv run generate_assets.py --svg icon.svg --bg-color "#2563eb"
```

The default is `#ffffff` (white). The script composites the icon onto this solid background.

---

## Maskable Icons Clip Content on Android

### Symptoms
- Icon edges are cut off when displayed as an adaptive icon on Android

### Cause
Content extends outside the safe zone (central 80% of canvas). Different launchers apply different mask shapes (circle, squircle, teardrop).

### Solution
The script already pads the icon to 80% of the canvas for maskable variants. If content still clips:
1. Simplify the master SVG to use less of the canvas edges (keep content within 70% of the viewBox)
2. Preview at [maskable.app](https://maskable.app/) by uploading the generated `icon-maskable-512.png`

---

## Favicon Not Updating in Browser

### Symptoms
- Browser shows the old or generic icon after deploying new favicon

### Cause
Browsers aggressively cache favicons. A hard refresh may not be enough.

### Solution
1. **Hard refresh**: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
2. **Clear favicon cache**: Navigate directly to `/favicon.ico` and hard refresh there
3. **Add cache buster** (temporary): `<link rel="icon" href="/favicon.ico?v=2">`
4. **Verify MIME types** are served correctly:
   - `.ico` → `image/x-icon`
   - `.svg` → `image/svg+xml`
   - `.webmanifest` → `application/manifest+json`

---

## Dark Mode Favicon Not Switching

### Symptoms
- SVG favicon stays in light mode even when OS is set to dark theme

### Cause
- Browser doesn't fully support SVG favicon media queries
- CSS classes not applied correctly in the SVG

### Solution
1. Verify `favicon.svg` contains `@media (prefers-color-scheme: dark)` block
2. Ensure the SVG `<link>` tag uses `type="image/svg+xml"`:
   ```html
   <link rel="icon" href="/favicon.svg" type="image/svg+xml">
   ```
3. Test in Chrome or Firefox (best support). Safari has partial support.
4. The `.ico` fallback will always show the light-mode version — this is expected.

---

## ImageMagick Renders SVG Poorly

### Symptoms
- Generated PNGs look pixelated, misaligned, or have missing elements
- Works fine with `rsvg-convert` but not with `magick`/`convert`

### Cause
ImageMagick delegates SVG rendering to its built-in renderer or to Inkscape/librsvg if available. The built-in renderer has limited SVG support.

### Solution
Install `librsvg` instead — it has superior SVG rendering:
```bash
brew install librsvg
```

The script auto-detects `rsvg-convert` first, falling back to `magick` only if librsvg is not found.

---

## Script Fails with "Invalid SVG"

### Symptoms
```
Error: file.svg does not appear to be a valid SVG file.
```

### Cause
The file doesn't contain an `<svg` tag. It may be:
- A renamed PNG/JPG file
- An SVG wrapped in other XML
- A corrupted download

### Solution
1. Open the file in a text editor and verify it starts with `<svg` or `<?xml`
2. If it's an `<?xml` declaration followed by `<svg>`, it's valid — check for encoding issues
3. If it's a raster image, convert it to SVG first using a vectorization tool

---

## Next.js App Router Icons Not Auto-Detected

### Symptoms
- Next.js doesn't generate `<link>` tags for icons
- Browser shows default/no favicon despite files being present in `app/`

### Cause
Files are not named according to Next.js App Router conventions, or are placed in the wrong directory.

### Solution

1. **Regenerate with framework flag:**
   ```bash
   uv run generate_assets.py --svg icon.svg --framework nextjs
   ```
   This outputs `icon.svg` (not `favicon.svg`) and `apple-icon.png` (not `apple-touch-icon.png`).

2. **Verify file placement:**
   - `favicon.ico`, `icon.svg`, `apple-icon.png`, `manifest.webmanifest` → `app/` directory
   - PWA icons (`icon-192.png`, `icon-512.png`, etc.) → `public/` directory

3. **Check file naming:**

   | Expected (Next.js) | Common mistake |
   |---------------------|---------------|
   | `icon.svg` | `favicon.svg` |
   | `apple-icon.png` | `apple-touch-icon.png` |

4. **Restart dev server** — Next.js needs a restart to detect new file-based metadata.
5. **Clear `.next` cache** — stale cached icons may persist: `rm -rf .next && npm run dev`

### Reference
- [Next.js App Icons docs](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/app-icons)
