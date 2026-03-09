---
description: Verify Playwright CLI installation and create a .playwright/cli.config.json configuration file. Use when setting up browser automation, configuring Playwright, or user mentions "setup playwright", "configure browser testing", "install playwright".
---

# /playwright-setup

Verify Playwright CLI installation and interactively create a `.playwright/cli.config.json` configuration file.

## Step 1 — Verify CLI Installation

Run `playwright-cli --version` via Bash.

**If installed**: Report the version and proceed to Step 2.

**If NOT installed**: Display install instructions:

```
Playwright CLI is not installed.

Install it with:
  npm install -g @playwright/cli@latest

Verify with:
  playwright-cli --help
```

Then ask via `AskUserQuestion`:
- **"Continue without CLI?"** — Options: "Continue with config creation" (create the config file anyway), "Cancel setup" (stop here)

If the user cancels, stop and summarize what happened.

## Step 2 — Check for Existing Config

Check if `.playwright/cli.config.json` exists in the project (current working directory).

**If exists and valid JSON**: Display current settings in a table, then ask via `AskUserQuestion`:
- **"Config exists"** — Options: "Reconfigure all settings" (proceed to Step 3), "Keep current config" (stop here)

**If exists but malformed JSON**: Warn the user about invalid JSON, then ask via `AskUserQuestion`:
- **"Malformed config"** — Options: "Overwrite with new config" (proceed to Step 3), "Cancel setup" (stop here)

**If does not exist**: Proceed to Step 3.

## Step 3 — Ask Configuration Questions

Use `AskUserQuestion` to gather settings. Ask these essential questions together in a single call:

| # | Question | Header | Options | Default |
|---|----------|--------|---------|---------|
| Q1 | Which browser engine? | Browser | chromium, firefox, webkit | chromium |
| Q2 | Run in headless mode? | Headless | Yes (headless), No (headed) | Yes |
| Q3 | Output directory for screenshots/videos? | Output dir | `.playwright-cli`, `./test-results`, `./playwright-output` | `.playwright-cli` |

Then ask whether to configure advanced settings:

| # | Question | Header | Options | Default |
|---|----------|--------|---------|---------|
| Q4 | Configure advanced settings? | Advanced | No (use defaults), Yes | No |

**If Q4 = Yes**, ask the following via `AskUserQuestion` (use up to 4 questions per call, split across multiple calls if needed):

| # | Question | Header | Options/Input | Default |
|---|----------|--------|---------------|---------|
| Q4a | Action timeout in milliseconds? | Timeout | 3000, 5000, 10000 | 5000 |
| Q4b | Navigation timeout in milliseconds? | Nav timeout | 30000, 60000, 120000 | 60000 |
| Q4c | Save video recordings of sessions? | Video | Yes, No | No |
| Q4d | Allowed origins (comma-separated, blank for all)? | Origins | Text input via "Other" | (empty) |

## Step 4 — Create `.playwright/cli.config.json`

Create the `.playwright/` directory if it doesn't exist, then build the configuration object and write it with `Write` tool using 2-space indentation.

**Basic config** (when advanced settings are skipped):

```json
{
  "browser": {
    "browserName": "chromium",
    "launchOptions": {
      "headless": true
    }
  },
  "outputDir": ".playwright-cli"
}
```

**Full config** (when advanced settings are configured):

```json
{
  "browser": {
    "browserName": "chromium",
    "launchOptions": {
      "headless": true
    }
  },
  "outputDir": ".playwright-cli",
  "network": {
    "allowedOrigins": []
  },
  "saveVideo": false,
  "timeouts": {
    "action": 5000,
    "navigation": 60000
  }
}
```

Only include advanced fields that differ from defaults or were explicitly set by the user.

## Step 5 — Post-Setup Summary

Display a summary with:

### Configured Settings

Show a table of all settings written to the config file.

### Trigger Keywords

Remind the user that the `playwright-cli` skill auto-invokes when mentioning:
`playwright`, `browser automation`, `screenshot`, `browser testing`, `web testing`, `page interaction`, `e2e test`, `playwright-cli`

### Example Prompts to Try

- "Take a screenshot of https://example.com"
- "Test the login flow on my local app at localhost:3000"
- "Navigate to the homepage and click the sign-up button"

### Override Priority

Mention that CLI flags override environment variables, which override `.playwright/cli.config.json` settings:

```
CLI flags > Environment variables > .playwright/cli.config.json
```
