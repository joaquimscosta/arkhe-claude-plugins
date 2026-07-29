# google-stitch — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

Claude + Google Stitch workflow toolkit with MCP integration (prompt authoring, screen generation, design extraction)

## Skills

- **authoring-stitch-prompts** — Converts natural-language descriptions or UI spec files into optimized Google Stitch prompts. Use when creating, refining, or validating design directives for Google Stitch. Use when user says "creat…
- **generating-stitch-screens** — Generates Stitch screens from authored prompt files using MCP tools. Reads prompt sections, sends each to Stitch for generation, and fetches resulting images and code. Use when user mentions "generat…

## Commands as Trigger Phrases

### When the user says "/google-stitch:prompt" (args: <brief or @/path/to/spec>)

Generate Google Stitch-ready prompts from briefs or spec files using the authoring skill

# Prompt Command

Convert natural-language descriptions, revision notes, or spec files into Stitch-optimized prompts. This command gathers your preferences before generating to ensure the output matches your vision.

## Usage

```bash
/prompt "Design a fintech dashboard with KPI cards and charts"
/prompt @specs/mobile-app.md
/prompt "Move the KPI cards above the chart and add a region filter"
```

Attach files or reference repository paths as needed; the Skill will read them before rewriting the prompt.

## Inputs

- `$ARGUMENTS`: user-provided brief, iteration note, or file path(s) to parse.
- Attached files (optional): wireframes, specs, or references to include during analysis.

## Interactive Flow

For new prompt generation (not revisions), this command asks about your preferences:

1. **Component Selection** - Which UI components to include
2. **Style Preferences** - Visual style (Enterprise, Consumer, Minimal, etc.)
3. **Structure Decision** - Combined file or split by component

Select "Quick generation" at the first question to skip all questions and use smart defaults.

**Questions are skipped when:**
- Input is a revision request (starts with "change", "update", "move", "adjust")
- User selects "Quick generation"
- Single component detected (structure question only)

---

## Execution

### Step 1: Detect Request Type

Check if `$ARGUMENTS` is a revision request:
- If starts with: "change", "update", "move", "adjust", "resize", "reposition", "modify"
- → Skip all questions, invoke skill directly with `$ARGUMENTS`

### Step 2: Check for Design Context

Look for `design-intent/memory/constitution.md`:
- If found: Extract Project Type and Design System for style defaults
- If not found: Proceed without context

### Step 3: Analyze Brief for Components

Parse `$ARGUMENTS` to identify UI components mentioned:
- Navigation elements (sidebar, header, menu, tabs)
- Content areas (cards, grids, tables, lists)
- Data visualization (charts, graphs, metrics, KPIs)
- Interactive elements (forms, buttons, modals, dialogs)
- Media (images, video, galleries)

### Step 4: Ask Questions (Interactive)

**Question 1: Component Selection**

Present detected components and ask user which to include:

```
I detected these components from your brief:

• [Component 1]: [brief description]
• [Component 2]: [brief description]
• [Component 3]: [brief description]

Which components should I include in the Stitch prompt?

_…full command body at `plugins/google-stitch/commands/prompt.md`._

### When the user says "/google-stitch:stitch-generate" (args: <brief, description, or @/path/to/prompt-file>)

Full Stitch pipeline — author prompts, generate screens via MCP, fetch images and code

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

_…full command body at `plugins/google-stitch/commands/stitch-generate.md`._

### When the user says "/google-stitch:stitch-setup"

Guided setup and verification of Stitch MCP server connection

# Stitch Setup Command

Set up and verify the Stitch MCP server connection for automated screen generation.

## Execution

### Step 1: Check MCP Availability

Check if Stitch MCP tools are available by looking for the `generate_screen_from_text` tool.

- **If available**: Proceed to Step 2 (verification)
- **If not available**: Proceed to Step 3 (setup guidance)

### Step 2: Verify Connection

If MCP tools are detected:

1. Call `list_projects` to verify the connection works

2. **Handle errors:**
   - **If 403 Forbidden**: The Stitch API requires preview/allowlist access from Google. Report:

     ```text
     Stitch MCP: Connection Failed (403 Forbidden)

     The Google Stitch API requires preview access. This API is not yet
     generally available and requires allowlist approval from Google.

     To stop the failing MCP server from retrying:
       claude mcp remove stitch

     To check MCP status:
       claude mcp list

     Once you have Stitch API access, run /stitch-setup again.
     ```

   - **If authentication error** (message contains "invalid authentication credentials",
     "OAuth 2 access token", or "Token fetch failed"):

     The MCP server connected but the isolated credentials at `~/.stitch-mcp/config`
     have expired. This commonly happens when doctor passes but API calls fail.

     Proceed directly to Step 2b (Credential Refresh) - no diagnostic needed since
     the error message already identifies the issue.

   - **If MCP tools unavailable but stitch is configured**: The MCP server may be failing to connect. Proceed to Step 2a (Proxy Diagnostic).

   - **If other error**: Report the error and suggest checking ADC credentials

3. **On success**, run the doctor command to validate the full setup:

   ```bash
   npx @_davideast/stitch-mcp doctor
   ```

   This validates: CLI installation, user login, credentials, project config, API reachability.

4. **Report status**:

   ```text
   Stitch MCP: Connected
   Projects found: {count}
   Project ID: {STITCH_PROJECT_ID or "not set"}

   Ready to use:
     /prompt       - Author Stitch prompts (with auto-generate offer)
     /stitch-generate - Full pipeline: author -> generate -> fetch
   ```

5. If `STITCH_PROJECT_ID` is not set, suggest setting it for default project targeting

### Step 2a: Proxy Diagnostic (when MCP connection fails without clear error)

_…full command body at `plugins/google-stitch/commands/stitch-setup.md`._
