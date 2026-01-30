---
description: Guided setup and verification of Stitch MCP server connection
---

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
2. Report status:
   ```
   Stitch MCP: Connected
   Projects found: {count}
   Project ID: {STITCH_PROJECT_ID or "not set"}

   Ready to use:
     /prompt       - Author Stitch prompts (with auto-generate offer)
     /stitch-generate - Full pipeline: author -> generate -> fetch
   ```
3. If `STITCH_PROJECT_ID` is not set, suggest setting it for default project targeting

### Step 3: Setup Guidance

If MCP tools are NOT detected, present setup options:

```
Stitch MCP is not configured. Choose a setup method:

Option A: Interactive Setup (Recommended)
  Run: npx @_davideast/stitch-mcp init
  This walks through authentication and project configuration.

Option B: Manual gcloud Setup (for existing gcloud users)
  1. gcloud auth application-default login
  2. Set STITCH_PROJECT_ID environment variable
  3. The plugin's .mcp.json auto-configures the MCP server

Option C: Alternative MCP Servers
  - @anthropic/stitch-mcp - Anthropic's variant
  - @anthropic/stitch-mcp-auto - Auto-configuration variant
  Check npm for latest available packages.
```

### Step 4: Verify Environment

After setup, check:
1. `STITCH_PROJECT_ID` environment variable is set
2. Google Cloud Application Default Credentials (ADC) are configured
3. Test connection by calling `list_projects`

### Step 5: Post-Setup Suggestions

On successful verification:
```
Setup complete. Try these next:

  /prompt "dashboard for analytics app"
    → Author a Stitch prompt with optional auto-generation

  /stitch-generate "landing page for SaaS product"
    → Full pipeline: author prompt, generate screens, fetch images
```
