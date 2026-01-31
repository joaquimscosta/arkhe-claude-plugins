# Generating Stitch Screens — Workflow

## Step 1: Verify MCP Availability

Before any generation, confirm Stitch MCP tools are accessible.

### Check for Required Tools

Look for these MCP tools:
- `generate_screen_from_text` (required)
- `fetch_screen_image` (required)
- `create_project` (required)
- `list_projects` (required)
- `fetch_screen_code` (optional — code fetching)
- `extract_design_context` (optional — design DNA extraction)

### If Tools Not Found

Display setup message and stop:
```
Stitch MCP is not configured.

To set up:
  1. Run /stitch-setup for guided setup
  2. Or manually configure MCP (see plugin README)

Note: Stitch API requires preview/allowlist access from Google.
```

Do not proceed with generation. Do not attempt workarounds.

---

## Step 2: Locate and Read Prompt File

### Input Sources

1. **Direct file path**: Read from provided path
2. **Feature name**: Look in `design-intent/google-stitch/{feature}/` for latest version
3. **From authoring skill**: Use newly created prompt file path

### Version Resolution

If only feature name provided:
1. Scan `design-intent/google-stitch/{feature}/prompt-v*.md`
2. Select highest version number
3. If part files exist, process all parts sequentially

---

## Step 3: Parse Prompt Sections

### Parsing Algorithm

1. Split file content by `---` separator lines
2. For each section:
   a. Look for HTML comment label: `<!-- Layout: {name} -->` or `<!-- Component: {name} -->`
   b. Extract label type (Layout or Component) and name
   c. Extract prompt text (everything after the label, trimmed)
3. Build ordered list of `{type, name, prompt_text}` entries

### Edge Cases

- **No labels found**: Treat entire file as single prompt, use filename as screen name
- **Empty sections**: Skip sections with no prompt text after the label
- **Part files**: Process part1 first, then part2, etc. in order

---

## Step 4: Create or Select Stitch Project

### Project Naming

Derive project name from feature:
- Feature slug `dashboard` -> Project name `Dashboard Design`
- Feature slug `admin-panel` -> Project name `Admin Panel Design`
- Convert kebab-case to Title Case, append "Design"

### Project Selection

1. Call `list_projects`
2. Search for project matching derived name (case-insensitive)
3. If match found: use existing project ID
4. If no match: call `create_project` with derived name

### STITCH_PROJECT_ID Override

If `STITCH_PROJECT_ID` environment variable is set, use it directly instead of creating/searching.

---

## Step 5: Generate Screens

### Generation Loop

For each parsed section (in order):

1. Call `generate_screen_from_text` with:
   - `project_id`: from Step 4
   - `prompt`: section's prompt text
   - `name`: section's label name (e.g., "Analytics Dashboard", "KPI Metrics")
2. Store returned screen ID
3. Log progress: `Generating: {type}: {name}...`

### Error Handling per Section

- **API error**: Log error, skip section, continue with next
- **Rate limit**: Wait indicated duration, retry once
- **Timeout**: Mark as pending, continue with next, retry at end

### Progress Reporting

After each successful generation:
```
[{N}/{total}] Generated: {type}: {name}
```

---

## Step 6: Fetch Screen Images

### Fetch Loop

For each successfully generated screen:

1. Call `fetch_screen_image` with screen ID
2. If image returned:
   - Save to `design-intent/google-stitch/{feature}/exports/{slugified-name}.png`
   - Log: `Saved: exports/{slugified-name}.png`
3. If image empty/not ready:
   - Wait 3 seconds
   - Retry fetch once
   - If still empty: log warning, continue

### File Naming

Convert screen names to file-safe slugs:
- "Analytics Dashboard" -> `analytics-dashboard.png`
- "KPI Metrics" -> `kpi-metrics.png`
- Lowercase, hyphens for spaces, strip special characters

---

## Step 7: Fetch Screen Code (Optional)

Only if user requested code extraction or `/stitch-generate` was used.

### Code Fetch Loop

For each generated screen:

1. Call `fetch_screen_code` with screen ID
2. Save to `design-intent/google-stitch/{feature}/code/{slugified-name}/`
3. Organize by file type if multiple files returned

---

## Step 8: Extract Design Context (Optional)

If user accepts design context extraction:

1. Call `extract_design_context` with project ID
2. Save result to `design-intent/google-stitch/{feature}/design-dna.md`
3. This captured context can be used to improve future prompt generation

---

## Step 9: Report Results

### Success Report

```
Stitch Generation Complete

Project: {name} ({URL})
Feature: {feature}/

Screens ({success}/{total}):
  1. Layout: {name}      -> exports/{slug}.png
  2. Component: {name}   -> exports/{slug}.png
  3. Component: {name}   -> exports/{slug}.png

Directory:
  design-intent/google-stitch/{feature}/
  ├── prompt-v{N}.md
  ├── exports/
  │   ├── {slug-1}.png
  │   └── {slug-2}.png
  └── code/ (if fetched)
```

### Partial Failure Report

If some screens failed:

```
Stitch Generation: {success}/{total} screens

Succeeded:
  1. Layout: {name}      -> exports/{slug}.png
  2. Component: {name}   -> exports/{slug}.png

Failed:
  3. Component: {name}   -> Error: {message}
  4. Component: {name}   -> Error: {message}

Retry failed screens:
  /stitch-generate @{prompt-file-path}
```

### Complete Failure Report

If no screens generated:

```
Stitch Generation Failed

No screens were generated. Common causes:
  - Authentication expired: run `gcloud auth application-default login`
  - Project quota exceeded: check Google Cloud console
  - Invalid prompts: review prompt file format

Run /stitch-setup to verify your configuration.
```
