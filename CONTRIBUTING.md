# Contributing Guide

Guide for creating new plugins and contributing to Arkhe Claude Plugins.

## Creating a New Plugin

### 1. Create Plugin Directory Structure

```bash
mkdir -p plugins/new-plugin/.claude-plugin
mkdir -p plugins/new-plugin/agents
mkdir -p plugins/new-plugin/commands
mkdir -p plugins/new-plugin/skills
```

### 2. Create Plugin Manifest

Create `plugins/new-plugin/.claude-plugin/plugin.json`:

```json
{
  "name": "new-plugin",
  "description": "Brief description of your plugin's purpose",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

### 3. Add to Marketplace

Edit `.claude-plugin/marketplace.json` and add your plugin:

```json
{
  "name": "new-plugin",
  "source": "./plugins/new-plugin",
  "description": "Brief description of your plugin's purpose"
}
```

### 4. Create README

Create `plugins/new-plugin/README.md` with:
- Overview
- Components (agents, commands, skills)
- Installation instructions
- Usage examples
- Version information

---

## Component Guidelines

### Creating Agents

Create agent files in `agents/` directory with YAML frontmatter:

```markdown
---
name: agent-name
description: When and why to use this agent (include trigger phrases like "Use PROACTIVELY")
tools: Read, Write, Grep, Glob, Bash  # Optional - omit to inherit all
model: sonnet  # Optional - sonnet/opus/haiku or inherit
---

System prompt defining the agent's role, capabilities, and approach.
```

**Naming:** Use lowercase with hyphens (e.g., `docs-architect`, `ai-engineer`)

**Description Guidelines:**
- Keep under 1,024 characters
- Include specific trigger phrases
- Explain when to use the agent

### Creating Commands

Create command files in `commands/` directory:

```markdown
---
description: Brief description of what this command does
argument-hint: [optional: argument description]
---

# Command Name

Full prompt that Claude Code will execute when the command is invoked.
Include specific instructions, context, and expected behavior.
```

**Naming:** Use lowercase with hyphens (e.g., `doc-generate`, `code-explain`)

### Creating Skills

Create skills in `skills/skill-name/` directory with progressive disclosure:

```
skills/skill-name/
├── SKILL.md              # Main instructions (<150 lines)
├── WORKFLOW.md           # Detailed steps (optional)
├── EXAMPLES.md           # Usage examples (recommended)
├── TROUBLESHOOTING.md    # Error handling (recommended)
└── scripts/              # Python scripts (optional)
```

**SKILL.md Template:**

```markdown
---
name: Skill Name
description: What it does. Use when [trigger scenarios].
---

# Quick Start
Essential instructions only (<150 lines)

## Output Structure
What the skill produces

## Common Issues
Quick fixes with references to TROUBLESHOOTING.md

## Examples
Brief examples with reference to EXAMPLES.md
```

**Key Guidelines:**
- SKILL.md: <5,000 tokens (target: <1,000 tokens, ~150 lines)
- Supporting docs: Unlimited size
- Include specific trigger keywords in description
- Python scripts: Standard library only, executable (`chmod +x`)

---

## Python Script Guidelines

### Requirements

- Python 3.8+
- Standard library only (no pip install)
- Must be executable (`chmod +x script.py`)
- Include shebang: `#!/usr/bin/env python3`

### Template

```python
#!/usr/bin/env python3
"""
Script description and usage.
"""

import json
import sys
from pathlib import Path

def main():
    """Main entry point."""
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

### Security Constraints

```python
# ALLOWED
import json, urllib.request, pathlib, re
from pathlib import Path

# FORBIDDEN
import requests  # Third-party package
os.system("pip install package")  # Runtime installation
eval(user_input)  # Code execution risks
```

---

## Testing Your Plugin

### Local Testing

```bash
# Start Claude Code
claude

# Add marketplace
/plugin marketplace add ./arkhe-claude-plugins

# Install your plugin
/plugin install new-plugin@arkhe-claude-plugins

# Verify installation
/plugin
/agents
/help
```

### Iterating on Changes

```bash
# After making changes, reinstall
/plugin uninstall new-plugin@arkhe-claude-plugins
/plugin install new-plugin@arkhe-claude-plugins
```

### Checklist

- [ ] Plugin manifest is valid JSON
- [ ] Plugin added to marketplace.json
- [ ] README.md created with usage examples
- [ ] All agents have valid YAML frontmatter
- [ ] All commands have descriptions
- [ ] Skill SKILL.md is under token limit
- [ ] Python scripts are executable
- [ ] All internal links work

---

## Documentation Standards

### README Structure

1. **Title** - Plugin name
2. **Overview** - What the plugin does
3. **Components** - Agents, commands, skills
4. **Installation** - How to install
5. **Usage** - Examples and workflows
6. **Version** - Current version

### YAML Frontmatter

**Required fields:**
- `name`: 64 characters max
- `description`: 1,024 characters max

**Description template:**
```
[What it does]. Use when [trigger scenario 1], [trigger scenario 2], or [trigger scenario 3].
```

### Trigger Keywords

Include specific keywords in descriptions:
- Good: "Use when user mentions 'diagram', 'flowchart', 'mermaid'"
- Bad: "Use when needed"

---

## Pull Request Process

### Before Submitting

1. Test your changes locally
2. Update README.md if adding new components
3. Update CLAUDE.md if adding new plugins
4. Ensure documentation is complete
5. Run any existing tests

### PR Guidelines

- Use descriptive titles
- Include summary of changes
- Reference any related issues
- Update version numbers if needed

### Commit Messages

Use conventional commits:

```bash
feat(plugin-name): add new agent for X
fix(plugin-name): resolve issue with Y
docs(plugin-name): update README with Z
```

---

## Architecture Reference

### Plugin Structure

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json           # Plugin metadata
├── agents/                    # AI subagents
│   └── agent-name.md
├── commands/                  # Slash commands
│   └── command-name.md
├── skills/                    # Auto-invoke skills
│   └── skill-name/
│       ├── SKILL.md
│       ├── WORKFLOW.md
│       ├── EXAMPLES.md
│       └── scripts/
└── README.md
```

### Marketplace Structure

```
arkhe-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json      # Plugin catalog
├── plugins/                   # All plugins
│   ├── plugin-1/
│   └── plugin-2/
├── docs/                      # Developer documentation
└── README.md
```

---

## Getting Help

- **Documentation:** Check `docs/` directory for guides
- **Examples:** Review existing plugins for patterns
- **Issues:** Open an issue for questions or problems
- **Best Practices:** See `docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md`

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Follow existing patterns and conventions
- Test thoroughly before submitting
- Document your changes
