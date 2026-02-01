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

### Step 2a: Proxy Diagnostic (when MCP fails but doctor passes)

When `claude mcp list` shows stitch as "Failed to connect" but `npx @_davideast/stitch-mcp doctor` passes all checks, the actual error is hidden. Use this diagnostic step:

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

Then restart Claude Code or run `/mcp` to reconnect.

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
