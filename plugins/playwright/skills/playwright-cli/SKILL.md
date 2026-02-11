---
name: playwright-cli
description: >-
  Browser automation via Playwright CLI for navigating pages, interacting with
  elements, capturing screenshots, and testing web applications through shell
  commands. Use when user mentions "playwright", "browser automation",
  "take a screenshot", "browser testing", "headless browser", "web testing",
  "fill out a form", "e2e test", or needs to automate browser workflows
  from the command line.
---

# Playwright CLI

Automate browsers through shell commands executed via the Bash tool.
Navigate pages, interact with elements, capture screenshots, and test
web applications — without MCP server configuration.

Both CLI and MCP use the same Playwright engine and do not conflict. See
`docs/PLAYWRIGHT_CLI.md` (project root) for the complete reference.

## Core Workflow

Every browser interaction follows this pattern:

1. **Open** a page: `playwright-cli open <url>`
2. **Snapshot** to discover elements: `playwright-cli snapshot`
3. **Interact** using refs from the snapshot: `playwright-cli click <ref>`
4. **Verify** the result: `playwright-cli screenshot` or `playwright-cli snapshot`

Always run `snapshot` before interacting — element references (`<ref>`) come
exclusively from snapshot output and become stale after navigation.

## Command Reference

### Navigation

| Command | Description |
|---------|-------------|
| `open <url>` | Open URL in new page |
| `goto <url>` | Navigate current page |
| `go-back` | Browser back button |
| `go-forward` | Browser forward button |
| `reload` | Reload current page |
| `close` | Close the browser |

### Interaction

| Command | Description |
|---------|-------------|
| `click <ref>` | Click an element |
| `dblclick <ref>` | Double-click an element |
| `fill <ref> <text>` | Clear field, then type text |
| `type <text>` | Type into focused element (appends) |
| `check <ref>` / `uncheck <ref>` | Toggle checkbox |
| `select <ref> <values>` | Select dropdown option(s) |
| `hover <ref>` | Hover over element |
| `drag <start> <end>` | Drag between elements |
| `press <key>` | Press key (Enter, Tab, ArrowDown) |
| `upload <ref> <paths>` | Upload file(s) to file input |

### Output

| Command | Description |
|---------|-------------|
| `screenshot [filename]` | Capture PNG screenshot |
| `snapshot` | Accessibility tree — structured, token-efficient |
| `pdf [filename]` | Generate PDF of the page |

### Tabs

| Command | Description |
|---------|-------------|
| `tab list` | List open tabs |
| `tab create [url]` | Open new tab |
| `tab select <index>` | Switch to tab |
| `tab close [index]` | Close tab |

## Sessions

Sessions persist browser state (cookies, localStorage, open tabs) across
CLI invocations within the same session.

- **Default session** — all commands share one session automatically
- **Named sessions** — `playwright-cli -s=<name> open <url>` for parallel instances
- **Environment variable** — `PLAYWRIGHT_CLI_SESSION=my-project`
- **List sessions** — `playwright-cli list`
- **Cleanup** — `playwright-cli close-all` or `playwright-cli kill-all` (force)

## Configuration

Create `playwright-cli.json` in the project root:

```json
{
  "browserName": "chromium",
  "headless": true,
  "actionTimeout": 5000,
  "navigationTimeout": 60000
}
```

- Use `--headed` flag for a visible browser window (debugging, demos)
- Environment variables use `PLAYWRIGHT_MCP_` prefix, shared with MCP configuration (e.g., `PLAYWRIGHT_MCP_BROWSER=firefox`)
- Other options: `allowedOrigins`, `blockedOrigins`, `saveVideo`, `outputDir`

## Common Pitfalls

- **Interacting without snapshot** — refs are unknown until `snapshot` runs
- **Stale refs after navigation** — re-run `snapshot` after `goto`, link clicks, or form submissions
- **fill vs type** — `fill` clears the field first; `type` appends to current content
- **Stuck sessions** — run `playwright-cli kill-all` to force-close all browsers

## Resources

- [EXAMPLES.md](EXAMPLES.md) — Multi-step workflow examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Error diagnosis and fixes
- `docs/PLAYWRIGHT_CLI.md` (project root) — Complete reference
