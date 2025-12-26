# Troubleshooting: Extract Stitch Mockups

Common issues and solutions for mockup extraction.

---

## Installation Issues

### Playwright Not Installed

**Error:**
```
Error: Playwright not installed.
```

**Solution:**
The script uses uv with inline dependencies, so playwright installs automatically. You just need to install the browser:
```bash
uv run playwright install chromium
```

### uv Not Installed

**Error:**
```
uv: command not found
```

**Solution:**
Install uv: https://github.com/astral-sh/uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Chrome Not Found

**Error:**
```
Error: Chrome profile not found.
Expected location: ~/Library/Application Support/Google/Chrome
```

**Solution:**
1. Install Google Chrome if not present
2. Launch Chrome at least once to create profile
3. Verify path exists: `ls ~/Library/Application\ Support/Google/Chrome`

---

## Authentication Issues

### Not Signed Into Google

**Symptoms:**
- Browser opens but redirects to sign-in page
- No images captured
- Script times out

**Solution:**
1. Open Chrome manually
2. Navigate to `https://stitch.withgoogle.com`
3. Sign in with your Google account
4. Close Chrome
5. Re-run extraction script

### Session Expired

**Symptoms:**
- Previously worked but now fails
- Redirects to sign-in

**Solution:**
Same as above - refresh Google session in Chrome.

### Multiple Chrome Profiles

**Symptoms:**
- Signed in on one profile but script uses another

**Solution:**
Script uses default profile. Either:
1. Sign into Google on the default profile
2. Copy session cookies to default profile
3. Modify script to use specific profile path

---

## Extraction Issues

### No Images Found

**Error:**
```
No mockup images found on the page.
Make sure the project has completed generating.
```

**Possible causes:**

1. **Project is empty**
   - The project exists but has no generated designs
   - Solution: Generate designs in Stitch first

2. **Generation failed**
   - Stitch generation failed silently
   - Solution: Check project in Stitch UI, regenerate if needed

3. **Page didn't fully load**
   - Network issues or slow connection
   - Solution: Increase wait time in script (edit `wait_for_timeout` values)

4. **URL pattern changed**
   - Google updated image hosting
   - Solution: Check DevTools Network tab for new URL patterns

### Still Generating

**Error:**
```
Error: Project is still generating.
Please wait for generation to complete and try again.
```

**Solution:**
1. Open project URL in browser
2. Wait for generation to complete (~40 seconds)
3. Verify mockups are visible
4. Re-run extraction

### Wrong Images Extracted

**Symptoms:**
- Script saves UI elements, avatars, or icons instead of mockups

**Cause:**
Image filtering not strict enough.

**Solution:**
The script filters for `lh3.googleusercontent.com/aida/` URLs which should only contain mockups. If wrong images appear:
1. Check the actual URLs of unwanted images
2. Add additional filtering in script's `handle_response` function

---

## URL Issues

### Invalid URL Format

**Error:**
```
Error: Invalid Stitch project URL: <url>
Expected format: https://stitch.withgoogle.com/projects/<id>
```

**Solution:**
Use the full project URL, not:
- Just the project ID
- The landing page URL
- A shortened URL

**Correct format:**
```
https://stitch.withgoogle.com/projects/3236066188909813678
```

### Project Not Found

**Symptoms:**
- Page shows 404 or error
- No images captured

**Possible causes:**
1. Project was deleted
2. Project belongs to different account
3. Typo in URL

**Solution:**
1. Verify URL in browser first
2. Check you're signed into correct Google account
3. Copy URL directly from browser address bar

---

## Directory Issues

### Feature Directory Not Found

**Error:**
```
Could not auto-detect feature directory.
Existing feature directories:
  1. dashboard
  2. eco-travel

Please re-run with --feature <name> to specify target directory.
```

**Solutions:**

1. **Specify manually:**
   ```bash
   python scripts/extract_images.py "<url>" --feature dashboard
   ```

2. **Create feature first:**
   Use authoring-stitch-prompts skill to create the feature directory structure, then extract.

3. **Let script create new:**
   If no features exist, script automatically creates one based on project title.

### Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'design-intent/google-stitch/feature/exports/mockup-1.png'
```

**Solution:**
```bash
chmod -R u+w design-intent/google-stitch/
```

### Directory Already Has Files

**Behavior:**
Script overwrites existing `mockup-*.png` files.

**To preserve existing:**
1. Rename existing files first
2. Or use `--output` to save to different location

---

## Performance Issues

### Slow Extraction

**Symptoms:**
- Script takes >30 seconds
- Browser appears frozen

**Possible causes:**
1. Slow network connection
2. Large number of images
3. Heavy page content

**Solutions:**
1. Check internet connection
2. Close other browser tabs/windows
3. Increase timeout values if needed

### Browser Doesn't Close

**Symptoms:**
- Script completes but Chrome window stays open

**Solution:**
This can happen if script errors before `browser.close()`. Manually close Chrome, then fix the underlying error.

---

## Debugging

### Enable Verbose Output

Set environment variable for JSON output:
```bash
OUTPUT_JSON=1 python scripts/extract_images.py "<url>"
```

### Check Network Traffic

1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Navigate to Stitch project
4. Filter by "Img" type
5. Verify `lh3.googleusercontent.com/aida/` images appear

### Manual Inspection

1. Run script with browser visible (default)
2. Watch what happens in Chrome
3. Note any redirects or errors
4. Check page content after load

---

## Getting Help

If issues persist:

1. **Check investigation notes:** `docs/stitch/stitch-investigation.md`
2. **Verify Stitch is accessible:** Open URL in browser
3. **Test with simple project:** Create new project in Stitch, then extract
4. **Check script output:** Look for specific error messages
