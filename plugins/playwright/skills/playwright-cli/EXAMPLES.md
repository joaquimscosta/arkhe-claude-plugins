# Playwright CLI Examples

Practical workflow examples progressing from simple to complex.

---

## 1. Basic Screenshot Capture

Capture a screenshot of any public page:

```bash
# Open the page
playwright-cli open https://example.com

# Capture screenshot (--filename must include outputDir path)
playwright-cli screenshot --filename=.playwright-cli/example-homepage.png

# Close the browser
playwright-cli close
```

---

## 2. Login Form Flow

Authenticate into a web application using form fields:

```bash
# Open the login page
playwright-cli open https://myapp.com/login

# Discover form elements
playwright-cli snapshot
# Output includes refs like:
#   textbox "Email" [ref=e12]
#   textbox "Password" [ref=e15]
#   button "Sign in" [ref=e18]

# Fill credentials using refs from snapshot
playwright-cli fill e12 "user@example.com"
playwright-cli fill e15 "my-password"

# Submit the form
playwright-cli click e18

# Verify login succeeded — re-snapshot after navigation
playwright-cli snapshot
# Look for dashboard elements in the output

# Capture evidence (--filename must include outputDir path)
playwright-cli screenshot --filename=.playwright-cli/logged-in-dashboard.png
```

**Key points:**
- Always `snapshot` before interacting to get element refs
- Re-run `snapshot` after navigation (the click triggered a page change)
- Use `fill` (not `type`) for form fields — it clears existing content first

---

## 3. TodoMVC Testing Workflow

Add items, check them off, and verify the result:

```bash
# Open the app with a visible browser for observation
playwright-cli open https://demo.playwright.dev/todomvc/ --headed

# Add todo items by typing into the focused input
playwright-cli type "Buy groceries"
playwright-cli press Enter
playwright-cli type "Water flowers"
playwright-cli press Enter
playwright-cli type "Read a book"
playwright-cli press Enter

# Snapshot to discover checkbox refs
playwright-cli snapshot
# Output includes:
#   checkbox "Toggle Todo" [ref=e21] (for "Buy groceries")
#   checkbox "Toggle Todo" [ref=e28] (for "Water flowers")
#   checkbox "Toggle Todo" [ref=e35] (for "Read a book")

# Check off the first two items
playwright-cli check e21
playwright-cli check e28

# Verify the result (--filename must include outputDir path)
playwright-cli screenshot --filename=.playwright-cli/todo-progress.png

# Clean up
playwright-cli close
```

**Key points:**
- `type` appends text to the focused element (the new-todo input auto-focuses)
- `press Enter` submits each todo item
- `check` toggles checkboxes using refs from the snapshot

---

## 4. Multi-Tab Research with Named Sessions

Work across multiple pages simultaneously using named sessions:

```bash
# Open the main application in session "app"
playwright-cli -s=app open https://myapp.com/dashboard

# Open documentation in session "docs"
playwright-cli -s=docs open https://docs.myapp.com/api

# Work in the docs session — find an API endpoint
playwright-cli -s=docs snapshot

# Switch back to the app session — it's still on the dashboard
playwright-cli -s=app snapshot

# Use tabs within a single session
playwright-cli -s=app tab create https://myapp.com/settings
playwright-cli -s=app tab list
# Output:
#   0: Dashboard - MyApp (active)
#   1: Settings - MyApp

playwright-cli -s=app tab select 1
playwright-cli -s=app snapshot

# List all active sessions
playwright-cli list

# Close specific session
playwright-cli -s=docs close

# Close all sessions when done
playwright-cli close-all
```

**Key points:**
- Named sessions (`-s=<name>`) run independent browser instances
- Each session maintains its own cookies, localStorage, and tabs
- `playwright-cli list` shows all active sessions
- Tabs within a session share the same browser context

---

## 5. Headed Debugging with Configuration

Set up a persistent configuration for visual debugging:

```json
// .playwright/cli.config.json
{
  "browser": {
    "browserName": "chromium",
    "launchOptions": {
      "headless": false
    }
  },
  "outputDir": "./screenshots",
  "timeouts": {
    "action": 10000,
    "navigation": 30000
  }
}
```

```bash
# With config file in place, browser opens visually by default
playwright-cli open https://myapp.com

# Take a full-page snapshot to understand the layout
playwright-cli snapshot

# Interact step by step — watch the browser respond
playwright-cli click e5
playwright-cli fill e10 "search query"
playwright-cli press Enter

# --filename must include outputDir path (./screenshots/ here)
playwright-cli screenshot --filename=./screenshots/debug-result.png

# Override browser engine via environment variable
PLAYWRIGHT_MCP_BROWSER=firefox playwright-cli open https://myapp.com
```

**Key points:**
- `.playwright/cli.config.json` persists configuration across all CLI invocations
- Set `headless: false` for visual debugging sessions
- Increase timeouts for slow-loading pages
- `outputDir` controls where auto-named screenshots and PDFs are saved
- When using `--filename`, prepend the `outputDir` path (e.g., `./screenshots/name.png`)
- Environment variables (`PLAYWRIGHT_MCP_` prefix) override config file settings

---

## Pattern Summary

| Pattern | Commands Used | When to Use |
|---------|--------------|-------------|
| Screenshot | `open` → `screenshot` → `close` | Quick page capture |
| Form fill | `open` → `snapshot` → `fill` → `click` → `snapshot` | Login, search, data entry |
| Testing | `open` → `type`/`press` → `snapshot` → `check`/`click` | E2E test workflows |
| Multi-context | `-s=<name>` for each context | Parallel page research |
| Debugging | Config file + `--headed` | Visual inspection |
