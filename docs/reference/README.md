# Reference Documentation

This directory contains **auto-synced copies** of official Claude Code documentation. These files are managed by `update-claude-docs.sh` and should not be edited manually — any changes will be overwritten on the next sync.

## Synced Files

| File | Source |
|------|--------|
| SUBAGENTS.md | Agent configuration and usage |
| PLUGINS.md | Plugin system documentation |
| HOOKS.md | Event handling documentation |
| SKILLS.md | Using Skills in Claude Code |
| SETTINGS.md | Settings scopes, precedence, and how-to |
| SETTINGS_REFERENCE.md | Full settings keys, permissions, sandbox, env vars |
| MCP.md | MCP server integration guide |
| PLUGINS_REFERENCE.md | Plugin manifest reference |
| BEST_PRACTICES.md | Official Claude Code best practices |
| PLUGINS_CREATE.md | Creating plugins: quickstart, layout, local testing |
| PLUGINS_COMPONENTS.md | Plugin components: skills, agents, hooks, MCP, LSP, monitors |
| PLUGINS_MARKETPLACE_REFERENCE.md | marketplace.json schema |
| PLUGINS_TROUBLESHOOTING.md | Plugin debugging and common errors |

## Updating

To sync the latest official documentation:

```bash
cd docs/reference
./update-claude-docs.sh
```

## Adding New Documentation

1. Edit `update-claude-docs.sh` and add to the `URL_MAPPINGS` array
2. Run `./update-claude-docs.sh` to download
3. Update references in `CLAUDE.md`, `docs/README.md`, and `README.md`
