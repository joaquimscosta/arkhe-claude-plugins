# Claude Code Plugin

Claude Code environment setup and configuration wizard.

## Overview

This plugin provides an interactive setup wizard that guides users through configuring their Claude Code environment following best practices from the [Claude Code Guide](../../docs/CLAUDE_CODE_GUIDE.md). It detects existing configuration and only suggests what's missing.

## Commands

| Command | Description |
|---------|-------------|
| `/claude-setup` | Interactive environment setup wizard |
| `/claude-setup [category]` | Set up a specific category (e.g., `hooks`, `mcp`) |

## Setup Categories

| Category | What It Configures |
|----------|--------------------|
| Global CLAUDE.md | Security rules, account configuration |
| Project Scaffolding | Directory structure, .env.example, .gitignore |
| MCP Servers | Install recommended MCP servers |
| Hooks | Security hooks (block-secrets), setup hooks |
| Custom Agents | Starter agent templates |
| Keybindings | Keyboard shortcuts |
| Settings | Language, background tasks |

## How It Works

1. **Detects** existing configuration (what's already set up)
2. **Fetches** the latest Claude Code Guide from GitHub for up-to-date recommendations
3. **Presents** setup categories with status indicators
4. **Guides** through each selected category with interactive questions
5. **Confirms** all changes before executing
6. **Summarizes** what was configured and next steps

## Installation

```
/plugin marketplace add ./arkhe-claude-plugins
/plugin install claude-code@arkhe-claude-plugins
```

## Skill Structure

```
skills/claude-setup/
├── SKILL.md              # Main instructions
├── WORKFLOW.md           # Per-category setup flows
├── EXAMPLES.md           # Example setup sessions
├── TROUBLESHOOTING.md    # Common issues
└── scripts/
    └── detect_setup.py   # Environment detection (Python 3.8+)
```
