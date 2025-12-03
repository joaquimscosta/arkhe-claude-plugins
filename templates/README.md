# Plugin Templates

Templates for creating new Claude Code plugins.

## Quick Start

1. Copy the `plugin-template/` directory to the repository root
2. Rename the directory to your plugin name
3. Update `plugin.json` with your plugin details
4. Add your plugin to `marketplace.json`
5. Customize agents, commands, and skills as needed

```bash
# Copy template
cp -r templates/plugin-template ./my-new-plugin

# Update plugin name in files
# Edit: my-new-plugin/.claude-plugin/plugin.json
# Edit: my-new-plugin/README.md
```

## Template Structure

```
plugin-template/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest (REQUIRED)
├── agents/
│   └── agent-template.md     # Example agent
├── commands/
│   └── command-template.md   # Example command
├── skills/
│   └── skill-template/
│       ├── SKILL.md          # Skill instructions
│       └── EXAMPLES.md       # Usage examples
└── README.md                 # Plugin documentation
```

## What to Customize

### plugin.json
- `name`: Your plugin name (lowercase, hyphens)
- `description`: Brief description
- `version`: Semantic version
- `author.name`: Your name

### Agents
- Replace `agent-name` with your agent name
- Update description with trigger phrases
- Define role, capabilities, and approach

### Commands
- Replace `command-name` with your command name
- Update description for `/help` display
- Define process and expected output

### Skills
- Replace `skill-template` directory name
- Update SKILL.md with trigger keywords
- Add supporting docs (WORKFLOW.md, TROUBLESHOOTING.md)

### README.md
- Update all sections with your plugin details
- Add real usage examples

## Guidelines

- **Names**: Use lowercase with hyphens
- **Descriptions**: Include trigger keywords
- **SKILL.md**: Keep under 150 lines
- **Python scripts**: Standard library only

## Reference

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Full contribution guide
- [docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md](../docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md) - Skill guidelines
- [docs/PLUGINS.md](../docs/PLUGINS.md) - Plugin system documentation
