# playwright — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

Browser automation via Playwright CLI for testing, screenshots, and interaction workflows

## Skills

- **playwright-cli** — Browser automation via Playwright CLI for navigating pages, interacting with elements, capturing screenshots, and testing web applications through shell commands. Use when user mentions "playwright",…

## Commands as Trigger Phrases

### When the user says "/playwright:playwright-setup"

Verify Playwright CLI installation and create a .playwright/cli.config.json configuration file. Use when setting up browser automation, configuring Playwright, or user mentions "setup playwright", "c…

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

_…full command body at `plugins/playwright/commands/playwright-setup.md`._
