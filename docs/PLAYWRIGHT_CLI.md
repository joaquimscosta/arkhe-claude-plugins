# Playwright CLI Guide for Claude Code

> **Source**: [Playwright CLI README](https://github.com/microsoft/playwright-cli) by Microsoft
>
> **Curated**: 2026-02-10 — Practitioner-oriented guide covering essentials for Claude Code users.

Playwright CLI provides browser automation through a command-line interface optimized for coding agents. If you've been using the Playwright MCP server, the CLI offers a lighter, more token-efficient alternative for many workflows.

**Related docs**: [MCP.md](./reference/MCP.md) (Playwright MCP server setup)

---

## Table of Contents

1. [CLI vs MCP: When to Use Which](#cli-vs-mcp-when-to-use-which)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Commands](#core-commands)
5. [Sessions](#sessions)
6. [Headed vs Headless](#headed-vs-headless)
7. [Configuration](#configuration)
8. [Example: Testing a TodoMVC App](#example-testing-a-todomvc-app)

---

## CLI vs MCP: When to Use Which

Both tools use the same Playwright engine under the hood. The difference is how they integrate with your agent.

| | **Playwright CLI** | **Playwright MCP** |
|---|---|---|
| **How it works** | Shell commands via Bash tool | Tool calls via MCP protocol |
| **Token cost** | Low — no tool schemas loaded into context | Higher — full tool schema in every request |
| **Browser state** | Persistent across CLI invocations (sessions) | Persistent within MCP connection |
| **Best for** | Scripted workflows, high-throughput tasks, CI pipelines | Exploratory automation, self-healing tests, rich introspection |
| **Agent integration** | Any agent with shell access | Requires MCP server configuration |

**Rule of thumb**: Use the CLI when you know what you want to do (scripted flows, screenshots, form filling). Use MCP when you need the agent to explore and adapt (discovering page structure, debugging visual issues).

You can use both in the same project — they don't conflict.

---

## Installation

Requires **Node.js 18+**.

```bash
# Install globally
npm install -g @playwright/cli@latest

# Verify installation
playwright-cli --help

# Install skills (optional — agents can also read --help output directly)
playwright-cli install --skills
```

---

## Quick Start

Open a page, interact with it, and take a screenshot — all from the command line:

```bash
# Open a URL (headless by default)
playwright-cli open https://example.com

# Take a screenshot
playwright-cli screenshot

# Get an accessibility snapshot (preferred for agent consumption)
playwright-cli snapshot

# Close the browser
playwright-cli close
```

The accessibility snapshot is particularly useful for agents — it returns structured page content without forcing image data into the context window.

---

## Core Commands

### Navigation

| Command | What it does |
|---------|-------------|
| `open <url>` | Open a URL in a new page |
| `goto <url>` | Navigate current page to URL |
| `go-back` | Browser back button |
| `go-forward` | Browser forward button |
| `reload` | Reload current page |
| `close` | Close the browser |

### Interaction

| Command | What it does |
|---------|-------------|
| `click <ref>` | Click an element |
| `dblclick <ref>` | Double-click an element |
| `type <text>` | Type text into the focused element |
| `fill <ref> <text>` | Fill a form field (clears first) |
| `check <ref>` | Check a checkbox |
| `uncheck <ref>` | Uncheck a checkbox |
| `select <ref> <values>` | Select dropdown option(s) |
| `hover <ref>` | Hover over an element |
| `drag <start> <end>` | Drag from one element to another |
| `upload <ref> <paths>` | Upload file(s) to a file input |

Element references (`<ref>`) come from the `snapshot` command output. Run `snapshot` first to discover what's on the page, then use the references to interact.

### Output

| Command | What it does |
|---------|-------------|
| `screenshot [filename]` | Capture a PNG screenshot |
| `snapshot` | Accessibility tree (structured, token-efficient) |
| `pdf [filename]` | Generate a PDF of the page |

### Keyboard

| Command | What it does |
|---------|-------------|
| `press <key>` | Press a key (e.g., `Enter`, `Tab`, `ArrowDown`) |
| `keydown <key>` | Hold a key down |
| `keyup <key>` | Release a key |

### Tabs

| Command | What it does |
|---------|-------------|
| `tab list` | List all open tabs |
| `tab create [url]` | Open a new tab |
| `tab select <index>` | Switch to a tab |
| `tab close [index]` | Close a tab |

---

## Sessions

Sessions maintain browser state (cookies, localStorage, open tabs) across CLI invocations. This is what makes the CLI practical for multi-step workflows.

### Default session

Every CLI command runs in the default session automatically:

```bash
playwright-cli open https://myapp.com/login
playwright-cli fill "#email" "user@example.com"
playwright-cli fill "#password" "secret"
playwright-cli click "button[type=submit]"
# Session persists — you're now logged in for subsequent commands
```

### Named sessions

Run multiple browser instances for different projects:

```bash
# Session "app" for your main application
playwright-cli -s=app open https://myapp.com

# Session "docs" for reference documentation
playwright-cli -s=docs open https://docs.myapp.com

# List all active sessions
playwright-cli list
```

### Session via environment variable

Pin a session for an entire Claude Code conversation:

```bash
PLAYWRIGHT_CLI_SESSION=my-project claude .
```

### Cleanup

```bash
# Close all sessions gracefully
playwright-cli close-all

# Force-kill all sessions (if something is stuck)
playwright-cli kill-all
```

---

## Headed vs Headless

The CLI runs **headless by default** — no visible browser window. This is ideal for CI pipelines and when you just need data or screenshots.

To see the browser (useful for debugging or demos):

```bash
playwright-cli open https://example.com --headed
```

All subsequent commands in that session will use the visible browser.

---

## Configuration

Create a `.playwright/cli.config.json` file in your project for persistent configuration:

```json
{
  "browser": {
    "browserName": "chromium",
    "launchOptions": {
      "headless": true
    }
  },
  "outputDir": ".playwright-cli",
  "timeouts": {
    "action": 5000,
    "navigation": 60000
  }
}
```

### Key configuration options

| Option | Path in config | Default | Description |
|--------|---------------|---------|-------------|
| Browser engine | `browser.browserName` | `"chromium"` | `chromium`, `firefox`, or `webkit` |
| Headless mode | `browser.launchOptions.headless` | `true` (daemon), `false` (non-Linux) | Run without visible window |
| Action timeout | `timeouts.action` | `5000` | Timeout for click/fill/type actions (ms) |
| Navigation timeout | `timeouts.navigation` | `60000` | Timeout for page navigation (ms) |
| Allowed origins | `network.allowedOrigins` | all | Restrict which origins the browser can visit |
| Blocked origins | `network.blockedOrigins` | none | Block specific origins |
| Save video | `saveVideo` | `false` | Record video of browser sessions |
| Output directory | `outputDir` | `".playwright-cli"` | Directory for screenshots, PDFs, videos |

### Environment variables

All options can also be set via environment variables prefixed with `PLAYWRIGHT_MCP_`:

```bash
PLAYWRIGHT_MCP_BROWSER=firefox playwright-cli open https://example.com
PLAYWRIGHT_MCP_HEADLESS=false playwright-cli open https://example.com
```

---

## Example: Testing a TodoMVC App

A practical walkthrough showing how the CLI commands chain together:

```bash
# 1. Open the app with a visible browser
playwright-cli open https://demo.playwright.dev/todomvc/ --headed

# 2. Add some todos
playwright-cli type "Buy groceries"
playwright-cli press Enter
playwright-cli type "Water flowers"
playwright-cli press Enter

# 3. Take a snapshot to see element references
playwright-cli snapshot

# 4. Check off tasks using refs from the snapshot
playwright-cli check e21
playwright-cli check e35

# 5. Capture the result
playwright-cli screenshot todo-done.png
```

Each command builds on the persistent session state. The `snapshot` in step 3 gives you the element references needed for `check` in step 4.

---

## Further Reading

- [Playwright CLI README](https://github.com/microsoft/playwright-cli) — Full command reference, network mocking, tracing, storage management
- [MCP.md](./reference/MCP.md) — Setting up Playwright as an MCP server in Claude Code
