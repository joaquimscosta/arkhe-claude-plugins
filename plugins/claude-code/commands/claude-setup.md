---
description: Interactively set up Claude Code environment with best practices
argument-hint: [category]
---

# /claude-setup

Interactive setup wizard for Claude Code environment configuration.

Guides you through best-practice setup for Global CLAUDE.md, project scaffolding, MCP servers, hooks, custom agents, keybindings, and settings — based on the latest Claude Code Guide.

## Usage

```
/claude-setup              # Full interactive setup
/claude-setup hooks        # Set up a specific category only
```

## Implementation

Invoke the Skill tool with skill name "claude-code:env-setup" and arguments: `$ARGUMENTS`

The skill will detect your current configuration, fetch the latest guide, and walk you through setup interactively.
