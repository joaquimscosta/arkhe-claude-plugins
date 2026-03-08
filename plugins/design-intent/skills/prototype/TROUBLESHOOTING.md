# Prototype — Troubleshooting

## Common Issues

### HTML Output Contains Markdown Fences

**Symptom**: Generated HTML starts with `` ```html `` or ends with `` ``` ``

**Solution**: Strip markdown fences before writing files:
- Remove leading `` ```html `` or `` ``` `` and any whitespace after
- Remove trailing `` ``` `` and any whitespace before
- Verify the result starts with `<!DOCTYPE html>` or `<html>`

---

### All 3 Artifacts Look Too Similar

**Symptom**: The design variations feel like color swaps rather than distinct approaches

**Causes**:
- Style direction names are too generic (e.g., "Modern Clean", "Elegant Simple")
- The metaphors don't translate to concrete CSS techniques

**Solutions**:
1. Ensure style names follow the pattern: `[Adjective] + [Material/Process] + [Form/Action]`
2. Each metaphor should imply different CSS techniques (see materiality-to-CSS mapping in WORKFLOW.md)
3. Regenerate with more specific creative examples in the style direction prompt
4. The examples should span different visual dimensions: texture vs structure vs motion vs color

---

### Google Fonts Not Loading

**Symptom**: Artifacts display in system fonts instead of the specified Google Fonts

**Causes**:
- Missing `<link>` tag in HTML `<head>`
- Incorrect font family name in CSS
- No internet connection when viewing the file

**Solutions**:
1. Verify each artifact has a Google Fonts `<link>` tag:
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
   ```
2. Ensure `font-family` in CSS matches the imported font name exactly
3. For offline use, consider adding a system font fallback stack

---

### Output Directory Already Exists

**Symptom**: Error or overwrite concerns when `.prototype/` already has files

**Solution**: The skill should create the directory if it doesn't exist and overwrite existing files with the same names. Previous prototype files with different names are preserved. If the user wants a clean start, they can delete the directory or use `--dir` to specify a new one.

---

### Large Token Usage

**Symptom**: Generation takes a long time or hits token limits

**Causes**: Each HTML artifact can be 200-500 lines. Generating 3 in one response is token-heavy.

**Solutions**:
1. Keep the component description focused and specific
2. For complex components, prototype a single section rather than a full page
3. Use simpler prompts: "login form" generates faster than "full e-commerce checkout flow with cart summary, payment, and confirmation"

---

### iframes Not Loading in Index Page

**Symptom**: The `index.html` comparison view shows blank panels

**Causes**:
- File paths in `src` attributes don't match actual filenames
- Browser security restrictions on local file access

**Solutions**:
1. Verify `src` attributes use relative paths (just filenames, not absolute paths)
2. Some browsers restrict `<iframe src="file://...">`. Use a local server:
   ```bash
   cd .prototype && python3 -m http.server 8080
   # Then open http://localhost:8080
   ```
3. Or open the individual HTML files directly in the browser

---

### Artifacts Reference Artist Names or Brands

**Symptom**: Generated HTML contains references to specific artists, brands, or copyrighted works

**Solution**: The IP safeguard in the prompt should prevent this. If it occurs:
1. Remove the offending references manually
2. Regenerate with a stronger safeguard instruction
3. The prompt explicitly states "No artist names, brand names, or trademarks" — if this is being ignored, add a more emphatic instruction

---

### --vary Fails to Find the Artifact

**Symptom**: `/prototype --vary 2` doesn't know which file is artifact 2

**Causes**:
- `manifest.json` is missing from the output directory
- The manifest was manually edited or corrupted

**Solutions**:
1. Check that `.prototype/manifest.json` exists and contains the `artifacts` array
2. If missing, the skill will fall back to globbing for files starting with `02-`
3. Regenerate with `/prototype <original prompt>` to create a fresh manifest

---

## When to Ask for Help

- If the skill fails to generate valid HTML after multiple attempts
- If the index page template produces layout issues on your display
- If you need to customize the generation for a specific design system or framework
