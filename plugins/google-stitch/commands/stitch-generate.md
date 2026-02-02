---
description: Full Stitch pipeline — author prompts, generate screens via MCP, fetch images and code
argument-hint: <brief, description, or @/path/to/prompt-file>
---

# Stitch Generate Command

End-to-end pipeline: author Stitch prompts, generate screens via MCP, and fetch resulting images and code.

## Usage

```bash
/stitch-generate "dashboard for fitness app"
/stitch-generate @design-intent/google-stitch/dashboard/prompt-v1.md
```

## Inputs

- `$ARGUMENTS`: Either a raw text brief or a path to an existing prompt file.

## Execution

### Step 1: Check MCP Availability

Verify Stitch MCP tools are available (look for `generate_screen_from_text`).

- **If not available**: Display clear message and stop:
  ```
  Stitch MCP is not configured. Run /stitch-setup for guided setup.
  ```
- **If available**: Continue to Step 2.

### Step 2: Resolve Input

Determine input type from `$ARGUMENTS`:

- **If path to existing prompt file** (starts with `@` or ends with `.md`):
  - Read the file directly
  - Extract feature name from directory path
- **If raw text brief**:
  - Invoke the `authoring-stitch-prompts` skill to create the prompt file
  - Use the generated file path for subsequent steps

### Step 3: Parse Prompt Sections

Read the prompt file and parse sections separated by `---`:

1. Identify `<!-- Layout: ... -->` and `<!-- Component: ... -->` markers
2. Extract each section's text content
3. Build ordered list of prompts to generate

### Step 4: Create or Select Project

1. Derive project name from feature slug (e.g., "dashboard" -> "Dashboard Design")
2. Call `list_projects` to check for existing project with matching name
3. If found: use existing project
4. If not found: call `create_project` with derived name

### Step 5: Generate Screens

For each parsed prompt section:

1. Call `generate_screen_from_text` with the section's prompt text
2. Use the section label (from HTML comment) as screen name
3. Track generated screen IDs for fetching
4. If generation fails for a section, log the error and continue with remaining sections

### Step 6: Fetch Results

For each successfully generated screen:

1. Call `fetch_screen_image` to get the rendered image
2. Save image to `design-intent/google-stitch/{feature}/exports/{screen-name}.png`
3. Optionally: call `fetch_screen_code` to get generated code
4. Save code to `design-intent/google-stitch/{feature}/code/{screen-name}/`

### Step 7: Report

Present generation summary:

```
Stitch Generation Complete

Project: {project name} ({project URL})
Feature: {feature}/

Screens generated ({N}/{total}):
  1. Layout: {name}      -> exports/{name}.png
  2. Component: {name}   -> exports/{name}.png
  3. Component: {name}   -> exports/{name}.png

Directory structure:
  design-intent/google-stitch/{feature}/
  ├── prompt-v{N}.md          <- Source prompts
  ├── exports/                <- Generated images
  │   ├── {layout-name}.png
  │   ├── {component-1}.png
  │   └── {component-2}.png
  └── code/                   <- Generated code (if fetched)
      ├── {layout-name}/
      └── {component-1}/

Next steps:
  - Review exported images in exports/
  - Iterate: /prompt "adjust the header layout"
  - Re-generate: /stitch-generate @{prompt-file-path}
```

If any screens failed to generate, include a failures section with error details.

### Step 8: Optional Design Context Extraction

After successful generation, offer:
```
Extract design context from generated screens? [Yes / No]
```

If accepted: call `extract_design_context` for the project and save results to `design-intent/google-stitch/{feature}/design-dna.md` for future prompt refinement.
