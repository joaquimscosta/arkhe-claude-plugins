# Workflow: Extract Stitch Mockups

Detailed browser automation steps for extracting mockup images from Google Stitch projects.

---

## Step-by-Step Process

### 1. Validate Input

```python
# Check URL format
if "stitch.withgoogle.com/projects/" not in url:
    error("Invalid Stitch project URL")
    exit(1)
```

**Expected URL format:** `https://stitch.withgoogle.com/projects/{project-id}`

### 2. Locate Chrome Profile

**macOS default location:**
```
~/Library/Application Support/Google/Chrome
```

The script uses Chrome's persistent context to maintain Google authentication.

### 3. Launch Browser

```python
browser = playwright.chromium.launch_persistent_context(
    user_data_dir=chrome_profile_path,
    channel="chrome",
    headless=False,
    args=["--disable-blink-features=AutomationControlled"]
)
```

**Key settings:**
- `headless=False` - Required for auth to work properly
- `channel="chrome"` - Use installed Chrome (not Chromium)
- Disable automation detection to avoid blocks

### 4. Set Up Image Capture

Attach response handler before navigation:

```python
def handle_response(response):
    if response.request.resource_type == "image":
        if "lh3.googleusercontent.com/aida/" in response.url:
            collected_images.append({
                "url": response.url,
                "body": response.body()
            })

page.on("response", handle_response)
```

**Filtering criteria:**
- Resource type: `image`
- URL pattern: `lh3.googleusercontent.com/aida/`

### 5. Navigate and Wait

```python
page.goto(url, wait_until="networkidle")
page.wait_for_timeout(3000)  # Initial load
page.wait_for_timeout(2000)  # Lazy-loaded images
```

**Wait strategy:**
1. `networkidle` - Wait for network activity to stop
2. Additional 3s - Ensure page rendering completes
3. Additional 2s - Catch lazy-loaded content

### 6. Check Generation Status

```python
page_content = page.content()
if "Generating" in page_content and "estimated time" in page_content.lower():
    error("Project is still generating")
    exit(1)
```

**Status indicators:**
- "Generating..." text visible
- "estimated time" mention
- Spinner/loading UI elements

### 7. Extract Project Title

**Priority order:**
1. `h1` element
2. Element with `title` class
3. Element with `project-name` class
4. Fallback: Extract from URL

```python
title_element = page.query_selector('h1, [class*="title"], [class*="project-name"]')
if title_element:
    project_title = title_element.inner_text().strip()
```

### 8. Resolve Feature Directory

**Fallback chain:**
1. User-provided `--feature` argument
2. Auto-detect from existing directories
3. Prompt user to select
4. Create new from project title

**Auto-detection logic:**
```python
normalized = normalize_feature_name(project_title)
# "Eco-Travel Home Screen" -> "eco-travel-home-screen"

# Check for exact match
if normalized in existing_features:
    return normalized

# Check for partial match
for feature in existing_features:
    if feature in normalized or normalized in feature:
        return feature
```

### 9. Save Images

```python
save_dir.mkdir(parents=True, exist_ok=True)

for i, img_data in enumerate(collected_images, 1):
    filename = f"mockup-{i}.png"
    filepath = save_dir / filename

    with open(filepath, "wb") as f:
        f.write(img_data["body"])
```

**Output location:** `design-intent/google-stitch/{feature}/exports/`

### 10. Generate Report

Display extraction summary with:
- Project title and URL
- Number of images extracted
- Output directory path
- List of saved files

---

## Network Traffic Reference

Based on investigation of Stitch's network patterns:

### Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/_/Nemo/data/batchexecute` | Primary RPC endpoint |
| `lh3.googleusercontent.com/aida/...` | Generated mockup images |

### RPC IDs (for reference)

| rpcid | Function |
|-------|----------|
| `o30O0e` | Project initialization/load |
| `uYEY6` | Generation status polling |
| `ErneX` | Design metadata |

### Image Sources

- **Mockups:** `lh3.googleusercontent.com/aida/...` (400px+)
- **Avatars:** `stitch-avatar.png` (excluded)
- **UI assets:** `app-companion-430619.appspot.com` (excluded)

---

## Error Handling

### Authentication Failure

**Symptoms:**
- Redirected to Google sign-in
- Page shows "Sign in" prompt
- No images captured

**Solution:** Open Chrome manually, sign into Google, then retry.

### Generation In Progress

**Symptoms:**
- Page shows "Generating..."
- Status text mentions "estimated time"
- Spinner visible

**Solution:** Wait for generation to complete (~40 seconds), then retry.

### No Images Found

**Symptoms:**
- Script completes but no images saved
- "No mockup images found" message

**Possible causes:**
1. Project is empty (no designs generated)
2. Generation failed on Stitch side
3. Network filtering blocked image responses

### Invalid URL

**Symptoms:**
- "Invalid Stitch project URL" error

**Solution:** Use full URL format:
`https://stitch.withgoogle.com/projects/{project-id}`

---

## Performance Notes

- **Total extraction time:** ~10-15 seconds
- **Network wait:** 5 seconds (configurable)
- **Typical image count:** 1-6 per project
- **Image size:** ~100-500KB each

---

## Security Considerations

- Uses existing Chrome profile (no credentials stored in script)
- Images fetched via authenticated session
- No data transmitted to external services
- All processing done locally
