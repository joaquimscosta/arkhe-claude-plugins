# Generating Stitch Screens — Troubleshooting

## MCP Tools Not Detected

**Symptom:** Skill reports "Stitch MCP is not configured" even though you believe it should be set up.

**Causes:**
- MCP server not configured in `.mcp.json`
- Stitch API access not approved (403 errors)
- Node.js/npx not available in PATH

**Fix:**
1. Run `/stitch-setup` for guided verification
2. Check that Node.js is installed: `node --version`
3. Verify MCP is configured: `claude mcp list`
4. If not configured, add to your project's `.mcp.json` (see plugin README)
5. Restart Claude Code to reload MCP servers

**Note:** Stitch API requires preview/allowlist access from Google. If you get 403 errors, you need to request access before MCP will work.

---

## Authentication Failed

**Symptom:** `list_projects` or `generate_screen_from_text` returns authentication error.

**Causes:**
- Google Cloud ADC credentials expired
- No credentials configured
- Wrong Google account authenticated

**Fix:**
1. Refresh credentials:
   ```bash
   gcloud auth application-default login
   ```
2. Verify the correct account:
   ```bash
   gcloud auth list
   ```
3. Ensure your account has access to Google Stitch / AI Studio

---

## Generation Timeout

**Symptom:** `generate_screen_from_text` hangs or returns timeout error.

**Causes:**
- Complex prompt requiring longer processing
- Stitch service under heavy load
- Network connectivity issues

**Fix:**
1. Wait and retry — generation can take 30-60 seconds for complex prompts
2. Simplify the prompt (fewer components, shorter description)
3. Check Stitch service status at [stitch.withgoogle.com](https://stitch.withgoogle.com)
4. Try generating directly in the Stitch web UI to isolate the issue

---

## No Screens Created

**Symptom:** `generate_screen_from_text` succeeds but returns no screen ID or empty result.

**Causes:**
- Prompt text too short or vague for Stitch to process
- Invalid prompt format (non-UI content)
- Project quota exceeded

**Fix:**
1. Validate prompt format — ensure it follows Stitch conventions (directive sentence + bullets + style cues)
2. Check prompt length — minimum ~20 words for meaningful generation
3. Try the prompt text directly in the Stitch web UI
4. Check project quotas in Google Cloud console

---

## fetch_screen_image Returned Empty

**Symptom:** Image fetch returns empty or null after successful generation.

**Causes:**
- Generation still in progress (image not yet rendered)
- Screen generation failed silently
- Temporary Stitch backend issue

**Fix:**
1. Wait 5-10 seconds and retry the fetch
2. Check screen status via `get_project` to see if generation completed
3. Try fetching from the Stitch web UI directly
4. If persistent, regenerate the screen

---

## STITCH_PROJECT_ID Not Set

**Symptom:** Skill creates a new project every time instead of reusing an existing one.

**Causes:**
- `STITCH_PROJECT_ID` environment variable not configured
- Variable set in wrong shell profile

**Fix:**
1. Set the variable:
   ```bash
   export STITCH_PROJECT_ID="your-project-id"
   ```
2. Add to shell profile (`~/.zshrc`, `~/.bashrc`) for persistence
3. Find your project ID via `list_projects` or from the Stitch web UI URL
4. Run `/stitch-setup` to verify the configuration

---

## Prompt File Parsing Errors

**Symptom:** Skill can't find sections in prompt file or generates wrong number of screens.

**Causes:**
- Missing `---` separators between sections
- Missing or malformed HTML comment labels
- Extra content outside of labeled sections

**Fix:**
1. Verify prompt file format:
   ```markdown
   <!-- Layout: Name -->
   [prompt text]

   ---

   <!-- Component: Name -->
   [prompt text]
   ```
2. Ensure `---` is on its own line (no leading/trailing spaces)
3. Ensure HTML comments use exact format: `<!-- Layout: Name -->` or `<!-- Component: Name -->`
4. Re-author the prompt using `/prompt` to ensure correct formatting

---

## Code Fetch Returns Unexpected Format

**Symptom:** `fetch_screen_code` returns code in unexpected structure or language.

**Causes:**
- Stitch generates code based on its own interpretation
- Multiple framework options available

**Fix:**
1. Code fetching is best-effort — Stitch determines the output format
2. Review generated code and adapt as needed
3. Use `extract_design_context` instead for design tokens and patterns
4. The primary value is in the generated images, not the code

---

## Rate Limiting

**Symptom:** MCP calls return rate limit errors after multiple rapid generations.

**Causes:**
- Too many API calls in short succession
- Project-level generation limits

**Fix:**
1. Wait the indicated cooldown period before retrying
2. For large batches (>6 screens), expect natural delays between part files
3. Check Google Cloud quotas for your project
4. Consider generating in smaller batches if consistently hitting limits
