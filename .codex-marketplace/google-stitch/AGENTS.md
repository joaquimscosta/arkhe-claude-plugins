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

Options:
→ All components (recommended)
→ Select specific components
→ Add more components
→ Quick generation (skip all questions, use smart defaults)
```

If user selects "Quick generation": Skip to Step 5 with defaults.
If user selects "Select specific": Present checkboxes for each component.
If user selects "Add more": Accept additional component descriptions.

**Question 2: Style Preferences**

Ask about visual style:

```
What visual style should these prompts target?

Options:
→ Enterprise (professional, data-dense, formal)
→ Consumer (friendly, approachable, vibrant)
→ Minimal (clean, simple, lots of whitespace)
→ Playful (colorful, fun, animated feel)
→ Custom (describe your preference)
→ Use detected: [Project Type + Design System] (if design-intent found)
```

**Question 3: Structure Decision** (only if multiple components)

```
How should I structure the output for [N] components?

Options:
→ Combined (single file with layout + all components)
→ Split (separate prompt per component)
→ Auto-detect (let skill decide based on complexity)
```

### Step 5: Build Structured Input

Compile user selections into structured format:

```
Brief: [original $ARGUMENTS]
Components: [comma-separated list of selected components]
Style: [chosen style option]
Structure: [Combined/Split/Auto]
```

### Step 6: Invoke Skill

Invoke the Skill tool with skill name "google-stitch:authoring-stitch-prompts" with the structured input above.

The skill will:
- Use specified components (skip auto-detection if provided)
- Apply style choice directly (override design context if specified)
- Respect structure preference (skip split detection if specified)

### Step 7: Present Results

Display generated prompt(s) with:
- File path(s) created
- Component breakdown
- Style cues applied
- Next steps for using in Stitch

### Step 8: Offer MCP Generation (Optional)

Check if Stitch MCP tools are available (look for `generate_screen_from_text`).

**If MCP detected AND this is a new prompt (not a revision):**

Offer generation:
```
Stitch MCP is available. Generate screens from this prompt?
  → Yes (generate screens in Stitch now)
  → No (just keep the prompt file)
```

If accepted: Orchestrate via `generating-stitch-screens` skill using the authored prompt file.

**If MCP not present:** Skip this step entirely. No error or warning — the command works fully without MCP.

**If revision request:** Skip this step. Revisions are targeted edits, not full generation candidates.

---

## Style Mapping

| Style Choice | Stitch Style Cues |
|--------------|-------------------|
| Enterprise | enterprise-grade, professional, data-dense, clean sans-serif typography |
| Consumer | friendly, approachable, vibrant accents, generous whitespace |
| Minimal | clean, minimal, ample whitespace, subtle shadows, restrained palette |
| Playful | playful, colorful, fun, animated feel, rounded corners, bold typography |

---

## Examples

**Interactive generation:**
```
User: /prompt "dashboard for fitness app"
Claude: [Asks 3 questions about components, style, structure]
User: [Selects: All components, Consumer style, Combined]
Claude: [Generates prompt with friendly, approachable style cues]
```

**Quick generation:**
```
User: /prompt "e-commerce product page"
Claude: [Asks first question]
User: Quick generation (skip all questions)
Claude: [Generates with smart defaults]
```

**Revision (questions skipped):**
```
User: /prompt "change the header to sticky and add a search bar"
Claude: [Skips questions, generates revision prompt directly]
```

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

Use this step when `claude mcp list` shows "Failed to connect" but the error is not clear.
For authentication errors with clear messages (e.g., "invalid authentication credentials"),
skip directly to Step 2b.

When `npx @_davideast/stitch-mcp doctor` passes all checks but the MCP server fails,
the actual error may be hidden. Use this diagnostic step:

1. **Ask user for permission** to run the proxy diagnostic:

   ```text
   The doctor shows all checks passing, but the MCP server is failing to connect.
   This often indicates expired credentials or a runtime issue not caught by doctor.

   Would you like me to run a diagnostic? This will attempt to start the proxy
   and capture the actual error message.
   ```

2. **If user confirms**, run the proxy with timeout to capture the error:

   ```bash
   timeout 10 npx @_davideast/stitch-mcp proxy 2>&1
   ```

3. **Parse output for known error patterns:**

   - **Expired isolated credentials** - Look for: `Token fetch failed` or `Failed to retrieve initial access token`
     → Proceed to Step 2b (Credential Refresh)

   - **Other errors** - Report the error and suggest checking the Troubleshooting section

### Step 2b: Credential Refresh (expired isolated credentials)

When the proxy diagnostic shows expired credentials in `~/.stitch-mcp/config`:

1. **Report the issue and offer to fix:**

   ```text
   Issue Detected: Expired Isolated Credentials

   Your Stitch credentials in ~/.stitch-mcp/config have expired.

   Would you like me to refresh them now? This will open a browser for Google authentication.

   [Yes, refresh credentials] [No, I'll do it manually]
   ```

2. **If user confirms**, run the credential refresh:

   ```bash
   CLOUDSDK_CONFIG="$HOME/.stitch-mcp/config" gcloud auth application-default login
   ```

3. **After successful refresh**, instruct user:

   ```text
   Credentials refreshed successfully.

   Restart Claude Code (or run /mcp) to reconnect the Stitch MCP server,
   then run /stitch-setup again to verify the connection.
   ```

### Step 3: Setup Guidance

If MCP tools are NOT detected, present setup instructions:

```text
Stitch MCP is not configured.

IMPORTANT: The Stitch API requires preview/allowlist access from Google.
Setup will fail with 403 errors until you have API access approved.

## Recommended: Interactive Setup

Run the setup wizard targeting Claude Code:

  npx @_davideast/stitch-mcp init -c claude-code

This automates:
  - Google Cloud CLI installation (isolated to ~/.stitch-mcp/)
  - User authentication (gcloud auth login)
  - Application credentials (gcloud auth application-default login)
  - Project selection and IAM configuration
  - Stitch API enablement
  - MCP configuration generation

Options:
  --local          Install gcloud locally to project directory
  -y, --yes        Auto-approve verification prompts
  -c, --client     Pre-select client (claude-code)
  -t, --transport  Choose transport (http or stdio)

## Alternative: Manual Setup

For existing gcloud users who prefer manual configuration:

Step 1: Authenticate with Google Cloud

  Option A: New users / Isolated config
    CLOUDSDK_CONFIG="~/.stitch-mcp/config" gcloud auth login
    CLOUDSDK_CONFIG="~/.stitch-mcp/config" gcloud auth application-default login

  Option B: Existing gcloud users
    gcloud auth application-default login
    Then add STITCH_USE_SYSTEM_GCLOUD=1 to your MCP env config.

Step 2: Set up IAM permissions

  gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:your-email@gmail.com" \
    --role="roles/serviceusage.serviceUsageConsumer"

Step 3: Enable the Stitch API

  gcloud components install beta
  gcloud beta services mcp enable stitch.googleapis.com --project=YOUR_PROJECT_ID

  Or via Console: https://console.cloud.google.com/apis/library/stitch.googleapis.com

Step 4: Add MCP configuration to .mcp.json:

  Standard config (for Option A authentication):
  {
    "stitch": {
      "command": "npx",
      "args": ["-y", "@_davideast/stitch-mcp", "proxy"],
      "env": {
        "STITCH_PROJECT_ID": "your-project-id"
      }
    }
  }

  For existing gcloud users (Option B):
  {
    "stitch": {
      "command": "npx",
      "args": ["-y", "@_davideast/stitch-mcp", "proxy"],
      "env": {
        "STITCH_USE_SYSTEM_GCLOUD": "1"
      }
    }
  }

Step 5: Restart Claude Code to load the MCP configuration.

Step 6: Run /stitch-setup again to verify the connection.
```

### Step 4: Verify Environment

After setup, check:

1. `STITCH_PROJECT_ID` environment variable is set (or `STITCH_USE_SYSTEM_GCLOUD` for existing gcloud users)

2. Google Cloud Application Default Credentials (ADC) are configured

3. Run the doctor command to validate the full setup:

   ```bash
   npx @_davideast/stitch-mcp doctor
   ```

4. Test connection by calling `list_projects`

### Step 5: Post-Setup Suggestions

On successful verification:

```text
Setup complete. Try these next:

  /prompt "dashboard for analytics app"
    → Author a Stitch prompt with optional auto-generation

  /stitch-generate "landing page for SaaS product"
    → Full pipeline: author prompt, generate screens, fetch images
```

### Step 6: Troubleshooting

Common issues and solutions:

#### 403 Forbidden Error

Cause: Stitch API requires preview/allowlist access from Google.

Solution:

1. Request access from Google for the Stitch API preview
2. Remove the failing MCP server (see commands below)
3. Wait for API access approval, then run `/stitch-setup` again

#### Permission Denied (403 - Not Owner/Editor)

Cause: Missing required IAM role for Stitch API usage.

Solution:

1. Grant the Service Usage Consumer role:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="user:your-email@gmail.com" \
     --role="roles/serviceusage.serviceUsageConsumer"
   ```

2. Verify billing is enabled on your project

3. Re-run `/stitch-setup` to test connection

#### MCP Server Stuck "connecting..."

Cause: MCP server continuously retrying failed connection.

Solution:

1. Check status: `claude mcp list`
2. Remove failing server: `claude mcp remove stitch` (or your server name)
3. Fix the underlying issue (usually 403 or credentials)
4. Run `/stitch-setup` to reconfigure

#### ADC (Application Default Credentials) Issues

Cause: Google Cloud credentials not configured or expired.

Solution:

1. Run: `gcloud auth application-default login`
2. Ensure correct project: `gcloud config set project YOUR_PROJECT_ID`
3. Verify: `gcloud auth application-default print-access-token`
4. Enable debug logging to see detailed errors:

   ```bash
   npx @_davideast/stitch-mcp proxy --debug
   # Check logs at /tmp/stitch-proxy-debug.log
   ```

#### Expired Isolated Credentials

Cause: The credentials stored in `~/.stitch-mcp/config` have expired. This commonly
happens when the doctor passes but the MCP proxy fails to start.

Symptoms:
- Doctor shows "All checks passed!"
- `claude mcp list` shows stitch as "Failed to connect"
- Proxy error: `Token fetch failed... Failed to retrieve initial access token`

Solution:

```bash
CLOUDSDK_CONFIG="$HOME/.stitch-mcp/config" gcloud auth application-default login
```

Then run `/reload-plugins` or `/mcp` to reconnect.

Note: The `CLOUDSDK_CONFIG` variable only applies to that single command. It stores
the refreshed credentials in the isolated config directory, which the stitch-mcp
proxy reads automatically on startup.

#### Authentication Reset

Use when: authentication is stuck, using wrong account, or need a fresh start.

Solution:

```bash
npx @_davideast/stitch-mcp logout --force --clear-config
```

Then re-run Step 1 authentication from Setup Guidance.

#### STITCH_PROJECT_ID Not Set

Cause: Environment variable missing from MCP configuration.

Solution: Update your `.mcp.json` with the correct project ID in the `env` section.

#### MCP Status Commands

```bash
# List all MCP servers and their status
claude mcp list

# Remove a specific MCP server
claude mcp remove stitch

# View MCP configuration
claude mcp list --json

# Validate full Stitch setup
npx @_davideast/stitch-mcp doctor

# Debug mode for verbose logging
npx @_davideast/stitch-mcp proxy --debug
```
