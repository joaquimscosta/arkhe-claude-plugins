# Playwright Plugin

Browser automation via Playwright CLI for testing, screenshots, and interaction workflows.

## Overview

The Playwright plugin provides a skill for browser automation using Playwright CLI. It teaches Claude how to navigate pages, interact with elements, capture screenshots, and test web applications through shell commands — without requiring MCP server configuration.

The CLI approach is token-efficient (no tool schemas loaded into context) and works with any agent that has Bash access.

## Prerequisites

- **Node.js 18+**
- **Playwright CLI**: `npm install -g @playwright/cli@latest`
- Verify: `playwright-cli --help`

## Available Skills

### Playwright CLI (`playwright-cli`)

Auto-invoked when user mentions browser automation, screenshots, browser testing, Playwright, e2e testing, or page interaction.

**Capabilities:**
- Navigate to URLs, go back/forward, reload pages
- Discover page elements via accessibility snapshots
- Click, fill forms, check boxes, select dropdowns, hover, drag
- Capture screenshots and PDFs
- Manage sessions for persistent browser state
- Work with multiple tabs and named sessions
- Configure timeouts, browser engine, headed/headless mode

**Trigger keywords:** `playwright`, `browser automation`, `screenshot`, `browser testing`, `web testing`, `page interaction`, `e2e test`, `playwright-cli`

## Installation

```bash
# Add the marketplace (if not already added)
/plugin marketplace add joaquimscosta/arkhe-claude-plugins

# Install the plugin
/plugin install playwright@arkhe-claude-plugins
```

## Usage

The skill auto-invokes when Claude detects browser automation context. Example prompts:

- "Take a screenshot of https://example.com"
- "Test the login flow on my local app"
- "Use playwright to check if the form submission works"
- "Automate the checkout flow and capture screenshots at each step"

## Skill Structure

```
plugins/playwright/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── playwright-cli/
│       ├── SKILL.md              # Core instructions (~110 lines)
│       ├── EXAMPLES.md           # 5 workflow examples
│       └── TROUBLESHOOTING.md    # 6 problem/solution guides
└── README.md
```

## Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| Invalid element ref | Run `playwright-cli snapshot` before interacting |
| Session stuck | Run `playwright-cli kill-all` |
| Timeout error | Increase timeouts in `playwright-cli.json` |
| CLI not found | Run `npm install -g @playwright/cli@latest` |

See [TROUBLESHOOTING.md](skills/playwright-cli/TROUBLESHOOTING.md) for detailed solutions.

## Version

1.0.0
