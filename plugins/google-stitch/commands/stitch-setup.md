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
2. **Handle errors:**
   - **If 403 Forbidden**: The Stitch API requires preview/allowlist access from Google. Report:
     ```
     Stitch MCP: Connection Failed (403 Forbidden)

     The Google Stitch API requires preview access. This API is not yet
     generally available and requires allowlist approval from Google.

     To stop the failing MCP server from retrying:
       claude mcp remove stitch

     To check MCP status:
       claude mcp list

     Once you have Stitch API access, run /stitch-setup again.
     ```
   - **If other error**: Report the error and suggest checking ADC credentials
3. **On success**, report status:
   ```
   Stitch MCP: Connected
   Projects found: {count}
   Project ID: {STITCH_PROJECT_ID or "not set"}

   Ready to use:
     /prompt       - Author Stitch prompts (with auto-generate offer)
     /stitch-generate - Full pipeline: author -> generate -> fetch
   ```
4. If `STITCH_PROJECT_ID` is not set, suggest setting it for default project targeting

### Step 3: Setup Guidance

If MCP tools are NOT detected, present setup instructions:

```
Stitch MCP is not configured.

IMPORTANT: The Stitch API requires preview/allowlist access from Google.
Setup will fail with 403 errors until you have API access approved.

Step 1: Authenticate with Google Cloud
  gcloud auth application-default login

Step 2: Add MCP configuration to your project's .mcp.json:

  {
    "stitch": {
      "command": "npx",
      "args": ["-y", "@_davideast/stitch-mcp", "proxy"],
      "env": {
        "STITCH_PROJECT_ID": "your-project-id"
      }
    }
  }

  Replace "your-project-id" with your Google Cloud project ID.

Step 3: Restart Claude Code to load the MCP configuration.

Step 4: Run /stitch-setup again to verify the connection.

Alternative: Interactive Setup
  npx @_davideast/stitch-mcp init
  This walks through authentication and configuration interactively.
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

### Step 6: Troubleshooting

Common issues and solutions:

#### 403 Forbidden Error

Cause: Stitch API requires preview/allowlist access from Google.

Solution:
1. Request access from Google for the Stitch API preview
2. Remove the failing MCP server (see commands below)
3. Wait for API access approval, then run `/stitch-setup` again

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
```
