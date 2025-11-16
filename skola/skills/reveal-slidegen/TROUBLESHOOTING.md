# Reveal SlideGen — Troubleshooting Guide

Complete error handling reference for the `reveal-slidegen` skill.

## Table of Contents

- [Input Issues](#input-issues)
- [Output Issues](#output-issues)
- [CDN and Library Loading](#cdn-and-library-loading)
- [Rendering Problems](#rendering-problems)
- [Script Execution Errors](#script-execution-errors)
- [Integration Issues](#integration-issues)

---

## Input Issues

### Error: "Input file not found"

**Symptoms:**
```
[Error] Input file not found: tutorial.md
```

**Causes:**
- File path is incorrect
- File doesn't exist in current directory
- Relative vs absolute path confusion

**Solutions:**
1. Verify file exists:
   ```bash
   ls -la tutorial.md
   ```
2. Use absolute path:
   ```bash
   python skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py \
     --input /full/path/to/tutorial.md \
     --output slides.html
   ```
3. Check current working directory:
   ```bash
   pwd
   ```

---

### Error: "Empty input"

**Symptoms:**
- Script runs but generates empty or minimal HTML
- No slides appear in output

**Causes:**
- Input file is empty
- Input is not valid markdown
- No headings found in input

**Solutions:**
1. Verify input file has content:
   ```bash
   cat tutorial.md
   ```
2. Ensure input has markdown structure:
   ```markdown
   # Title

   ## Section 1
   Content here...

   ## Section 2
   More content...
   ```
3. Check stdin is not empty when piping:
   ```bash
   # Bad - empty input
   echo "" | skill reveal-slidegen

   # Good - valid content
   cat tutorial.md | skill reveal-slidegen
   ```

---

### Warning: "No time-coded outline found"

**Symptoms:**
- Presentation generates successfully but appendix is missing
- No timeline slide in output

**Causes:**
- Input doesn't contain a time-coded outline table
- Table format is not recognized

**Solutions:**
This is a warning, not an error. To add a time-coded outline, include a table in your input:

```markdown
## Time-coded Outline

| Timestamp | Section | Description |
|-----------|---------|-------------|
| 00:00–00:20 | Intro | Welcome |
| 00:20–02:00 | Concepts | Core ideas |
```

---

## Output Issues

### Error: "Invalid HTML output"

**Symptoms:**
```
<!doctype html> tag missing
<div class="reveal"> container not found
```

**Causes:**
- Skill failed to generate proper HTML structure
- Markdown parsing error
- Incomplete template rendering

**Solutions:**
1. Verify output HTML structure:
   ```bash
   head -20 slides.html
   ```
   Should start with:
   ```html
   <!doctype html>
   <html lang="en">
   <head>
   ...
   ```

2. Check for `<div class="reveal">`:
   ```bash
   grep -c "div class=\"reveal\"" slides.html
   ```

3. Re-run generation with valid input:
   ```bash
   python skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py \
     --input tutorial.md \
     --output slides.html
   ```

---

### Error: "Slides not rendering properly"

**Symptoms:**
- HTML file opens but shows blank page
- Slides don't appear or are garbled

**Causes:**
- Missing Reveal.js container
- CDN scripts blocked or failed to load
- Browser JavaScript disabled

**Solutions:**
1. Open browser console (F12) and check for errors
2. Verify CDN scripts are loading:
   ```bash
   grep -E "(reveal\.js|highlight\.js|mermaid)" slides.html
   ```
3. Test in different browser (Chrome, Firefox, Safari)
4. Check internet connection (CDN requires network access)
5. Try opening HTML file via `file://` or local web server

---

## CDN and Library Loading

### Error: "highlight.js not working"

**Symptoms:**
- Code blocks appear but are not syntax-highlighted
- All code is monochrome

**Causes:**
- highlight.js CDN script failed to load
- Incorrect language class on `<code>` blocks
- highlight.js initialization failed

**Solutions:**
1. Verify highlight.js script in HTML:
   ```bash
   grep "highlight.js" slides.html
   ```
   Should include:
   ```html
   <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
   ```

2. Check code block syntax:
   ```html
   <pre><code class="language-javascript">
   // code here
   </code></pre>
   ```

3. Ensure initialization script is present:
   ```html
   <script>
   hljs.highlightAll();
   </script>
   ```

---

### Error: "Mermaid diagrams not rendering"

**Symptoms:**
- Mermaid code blocks show as plain text
- Diagrams don't appear

**Causes:**
- Mermaid CDN script failed to load
- Mermaid initialization missing
- Invalid Mermaid syntax in input

**Solutions:**
1. Verify Mermaid script:
   ```bash
   grep "mermaid" slides.html
   ```
   Should include:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs" type="module"></script>
   ```

2. Check Mermaid initialization:
   ```html
   <script type="module">
   import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
   mermaid.initialize({ startOnLoad: true, theme: 'dark' });
   </script>
   ```

3. Validate Mermaid syntax in input:
   ```markdown
   ```mermaid
   graph TD
       A[Start] --> B[End]
   ` ` `
   ```

---

### Error: "Reveal.js transitions not working"

**Symptoms:**
- Slides jump instead of smooth transitions
- No fade or slide animations

**Causes:**
- Reveal.js initialization config missing
- CDN script failed to load
- Browser doesn't support transitions

**Solutions:**
1. Verify Reveal.js initialization:
   ```html
   <script>
   Reveal.initialize({
       transition: 'fade',
       hash: true,
       plugins: [ RevealNotes ]
   });
   </script>
   ```

2. Check CDN loading:
   ```bash
   grep "reveal.js" slides.html
   ```

3. Test in modern browser with JavaScript enabled

---

## Rendering Problems

### Error: "Speaker notes not appearing"

**Symptoms:**
- Pressing `S` key doesn't open speaker view
- No speaker notes panel

**Causes:**
- RevealNotes plugin not loaded
- No `<aside class="notes">` blocks in HTML
- Browser popup blocked

**Solutions:**
1. Verify RevealNotes plugin loaded:
   ```bash
   grep "RevealNotes" slides.html
   ```

2. Check for notes blocks:
   ```bash
   grep -c "aside class=\"notes\"" slides.html
   ```

3. Allow popup windows in browser settings
4. Ensure narration was provided in input markdown

---

### Error: "Slides overflow or cut off"

**Symptoms:**
- Content extends beyond slide boundaries
- Text is truncated or hidden

**Causes:**
- Too much content on a single slide
- Long code blocks without scrolling
- Images too large

**Solutions:**
1. Split content across multiple slides
2. Reduce font size in custom CSS:
   ```html
   <style>
   .reveal pre code { font-size: 0.8em; }
   </style>
   ```
3. Enable scrolling for code blocks:
   ```html
   <pre style="max-height: 400px; overflow-y: auto;"><code>
   ...
   </code></pre>
   ```

---

## Script Execution Errors

### Error: "Permission denied" when running script

**Symptoms:**
```bash
bash: ./generate_reveal_slidegen.py: Permission denied
```

**Causes:**
- Script doesn't have execute permissions

**Solutions:**
```bash
chmod +x skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py
```

Then run:
```bash
./skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py --input tutorial.md --output slides.html
```

---

### Error: "Python module not found"

**Symptoms:**
```
ModuleNotFoundError: No module named 'argparse'
```

**Causes:**
- Python environment issue (highly unlikely for argparse)
- Using Python 2 instead of Python 3

**Solutions:**
1. Verify Python version:
   ```bash
   python3 --version
   ```
   Should be Python 3.8 or higher

2. Run with explicit python3:
   ```bash
   python3 skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py --input tutorial.md
   ```

---

### Error: "Skill command not found"

**Symptoms:**
```bash
skill: command not found
```

**Causes:**
- Claude Code CLI not installed or not in PATH
- Wrong execution context

**Solutions:**
1. Use Python script directly instead:
   ```bash
   python3 skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py --input tutorial.md --output slides.html
   ```

2. Or ensure Claude Code is installed and active

---

## Integration Issues

### Error: "Chaining with microlearn fails"

**Symptoms:**
- Pipeline fails when chaining skills
- Empty output or errors

**Causes:**
- microlearn output format incompatible
- Pipe broken or interrupted
- Encoding issues

**Solutions:**
1. Test each skill separately:
   ```bash
   skill microlearn topic.md > temp.md
   skill reveal-slidegen temp.md > slides.html
   ```

2. Verify microlearn output:
   ```bash
   skill microlearn topic.md | head -20
   ```

3. Use explicit files instead of pipes:
   ```bash
   skill microlearn topic.md > microlearn-output.md
   python skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py \
     --input microlearn-output.md \
     --output slides.html
   ```

---

### Error: "UTF-8 encoding issues"

**Symptoms:**
- Special characters display as `�` or garbled
- Accents, emojis broken

**Causes:**
- File not saved as UTF-8
- Encoding declaration missing

**Solutions:**
1. Ensure input file is UTF-8:
   ```bash
   file -I tutorial.md
   ```

2. Convert to UTF-8 if needed:
   ```bash
   iconv -f ISO-8859-1 -t UTF-8 tutorial.md > tutorial-utf8.md
   ```

3. Verify HTML includes charset declaration:
   ```html
   <meta charset="utf-8">
   ```

---

## General Tips

1. **Always validate HTML:** Open generated files in browser before sharing
2. **Check browser console:** Press F12 to see JavaScript errors
3. **Test CDN connectivity:** Ensure internet connection for script loading
4. **Use modern browsers:** Chrome, Firefox, Safari, Edge (latest versions)
5. **Provide structured input:** Clear headings and sections improve output
6. **Include narration:** Speaker notes enhance presentation quality
7. **Test locally first:** Preview before deploying to production

---

## Getting Help

If you encounter issues not covered here:

1. Check [EXAMPLES.md](EXAMPLES.md) for working patterns
2. Review [WORKFLOW.md](WORKFLOW.md) for detailed processing logic
3. Verify input follows expected markdown structure
4. Test with minimal example to isolate the issue
5. Check Reveal.js, highlight.js, and Mermaid documentation for library-specific issues
