# Playwright CLI Troubleshooting

Common issues and solutions when using Playwright CLI.

---

## 1. Element Not Found / Invalid Reference

**Symptoms:**
- `Error: element not found for ref "e12"`
- Click or fill does nothing
- `Invalid ref` error message

**Causes:**
- No `snapshot` was run before interacting
- Refs are stale — the page changed since the last snapshot
- Using a ref from a different tab or session

**Solutions:**

```bash
# Always snapshot first to get current refs
playwright-cli snapshot

# After any navigation, re-snapshot to refresh refs
playwright-cli goto https://myapp.com/page2
playwright-cli snapshot

# After clicking a link that navigates, re-snapshot
playwright-cli click e5
playwright-cli snapshot
```

**Rule of thumb:** Run `snapshot` before every interaction sequence, and again after any action that changes the page.

---

## 2. Session Stuck / Browser Not Responding

**Symptoms:**
- Commands hang indefinitely
- Browser window frozen (headed mode)
- `Error: session not found` after a crash

**Causes:**
- Previous session crashed without cleanup
- Browser process orphaned
- Network timeout during page load

**Solutions:**

```bash
# List active sessions to diagnose
playwright-cli list

# Gracefully close all sessions
playwright-cli close-all

# Force-kill all sessions if close-all hangs
playwright-cli kill-all

# Start fresh
playwright-cli open https://myapp.com
```

---

## 3. Timeout Errors

**Symptoms:**
- `Error: timeout 5000ms exceeded`
- `Navigation timeout of 60000ms exceeded`
- Actions fail on slow-loading pages

**Causes:**
- Default `actionTimeout` (5s) too short for complex interactions
- Default `navigationTimeout` (60s) too short for heavy pages
- Page waiting for resources that never load

**Solutions:**

Create or update `.playwright/cli.config.json` in the project:

```json
{
  "timeouts": {
    "action": 15000,
    "navigation": 120000
  }
}
```

For one-off overrides, use environment variables:

```bash
PLAYWRIGHT_MCP_ACTION_TIMEOUT=15000 playwright-cli click e5
```

If the page loads partially, try interacting with what is available rather than waiting for full load.

---

## 4. Browser Not Installed

**Symptoms:**
- `Error: browser not found`
- `playwright-cli: command not found`
- `Cannot find module @playwright/cli`

**Causes:**
- Playwright CLI not installed
- Browser binaries not downloaded
- Node.js version too old (requires 18+)

**Solutions:**

```bash
# Install the CLI globally
npm install -g @playwright/cli@latest

# Verify installation
playwright-cli --help

# Check Node.js version (must be 18+)
node --version
```

---

## 5. Headless vs Headed Confusion

**Symptoms:**
- Browser window appears unexpectedly (or fails to appear)
- Config file settings seem ignored
- Different behavior in CI vs local development

**Causes:**
- `.playwright/cli.config.json` has `"browser.launchOptions.headless": false` but `--headed` flag is expected
- Environment variable overrides config file
- CI environment forces headless regardless

**Resolution order** (highest priority first):
1. Command-line flag: `--headed`
2. Environment variable: `PLAYWRIGHT_MCP_HEADLESS=false`
3. Config file: `.playwright/cli.config.json` → `"browser.launchOptions.headless": false`
4. Default: headless (no visible window)

```bash
# Force headed mode regardless of config
playwright-cli open https://myapp.com --headed

# Force headless via environment variable
PLAYWRIGHT_MCP_HEADLESS=true playwright-cli open https://myapp.com
```

---

## 6. Commands Fail Silently or Return Empty Output

**Symptoms:**
- `snapshot` returns minimal or empty content
- `screenshot` produces a blank image
- `click` succeeds but nothing happens visually

**Causes:**
- Page JavaScript has not finished executing
- Page redirected and content is on a different URL
- Element is present in DOM but not visible or interactive

**Solutions:**

```bash
# After opening a page, snapshot to confirm content loaded
playwright-cli open https://myapp.com
playwright-cli snapshot
# If snapshot shows minimal content, the page may still be loading

# Take a screenshot to visually inspect what the browser sees
playwright-cli screenshot --filename=.playwright-cli/debug-check.png

# For single-page apps, wait briefly then re-snapshot
# (the app may need time to hydrate)
playwright-cli snapshot
```

If an element appears in the snapshot but interactions fail, it may be obscured by an overlay, modal, or loading spinner. Snapshot again to check for overlapping elements.

---

## Quick Reference

| Problem | First Step |
|---------|-----------|
| Invalid ref | Run `playwright-cli snapshot` |
| Stale ref after navigation | Run `playwright-cli snapshot` again |
| Session stuck | Run `playwright-cli kill-all` |
| Timeout error | Increase timeouts in `.playwright/cli.config.json` |
| CLI not found | Run `npm install -g @playwright/cli@latest` |
| No visible browser | Add `--headed` flag |
| Empty snapshot | Wait, then `snapshot` again |
