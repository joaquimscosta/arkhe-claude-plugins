# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Arkhe Claude Plugins** is a collection of Claude Code plugins providing specialized agents, commands, and skills for documentation, AI engineering, code review, git workflows, and educational content extraction.

## Plugin Architecture

This repository uses a **marketplace-based plugin system** where each plugin is independently installable and provides:
- **Agents** - Specialized AI subagents with focused expertise
- **Commands** - Slash commands for specific workflows
- **Skills** - Auto-invoked capabilities triggered by context

### Marketplace Structure

```
arkhe-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog
├── core/                          # Quality control and workflow orchestration
├── skola/                         # Tutorial creation and content extraction
├── ai/                            # AI engineering and LLM development
├── doc/                           # Documentation generation
├── review/                        # Code review and quality
├── ui/                            # UI/UX design and design systems
├── google-stitch/                 # Google Stitch prompting toolkit
├── git/                           # Git workflow automation
└── docs/                          # Developer documentation
```

### Plugin Structure Pattern

Each plugin follows this structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json               # Plugin metadata (name, version, author)
├── agents/                        # Specialized AI subagents (*.md)
│   └── agent-name.md
├── commands/                      # Slash commands (*.md)
│   └── command-name.md
├── skills/                        # Auto-invoke skills
│   └── skill-name/
│       ├── SKILL.md              # Skill metadata and instructions
│       ├── WORKFLOW.md           # Detailed steps
│       ├── EXAMPLES.md           # Usage examples
│       ├── TROUBLESHOOTING.md    # Error handling
│       └── scripts/              # Executable Python scripts
└── README.md                     # Plugin documentation
```

## Available Plugins

### Core Plugin
Quality control and workflow orchestration utilities.
- **Commands**: `/discuss`, `/double-check`, `/ultrathink`, `/workflow`

### AI Plugin
AI engineering toolkit for production-ready LLM applications.
- **Agents**: `ai-engineer`, `prompt-engineer`, `context-manager`
- **Commands**: `/improve-agent`, `/multi-agent-optimize`

### Doc Plugin
Multi-purpose documentation toolkit.
- **Agents**: `docs-architect`
- **Skills**: `mermaid` (auto-invoked diagram generation)
- **Commands**: `/doc-generate`, `/code-explain`, `/diagram`

### Skola Plugin
Tutorial creation and educational content extraction toolkit (Udemy, YouTube, blogs).
- **Agents**: `tutorial-engineer`
- **Skills**: `extracting-udemy` (auto-invoked for Udemy URLs)
- **Commands**: `/extract`, `/teach-code`

### Review Plugin
Code quality review tools for development teams.
- **Agents**: `pragmatic-code-review`, `design-review`
- **Commands**: `/code`, `/security`, `/design`, `/codebase`

### UI Plugin
UI/UX design and design system toolkit.
- **Agents**: `ui-ux-designer`
- **Commands**: None (all capabilities via agent)

### Google Stitch Plugin
Claude + Google Stitch prompting toolkit for prompt authoring and session management.
- **Commands**: `/prompt`
- **Skills**: `authoring-stitch-prompts`, `stitch-session-manager`
- **Use**: Generate Stitch-ready prompts, maintain multi-screen session logs, export summaries

### Git Plugin
Git workflow automation for commits, pull requests, branching, and changelog generation.
- **Commands**: `/commit`, `/create-pr`, `/create-branch`, `/changelog`
- **Skills**: `changelog` (auto-invoke)
- **Scripts**: 4 shell scripts for git workflow automation

### Design Intent Plugin
Design Intent for Spec-Driven Development that combines AI-assisted implementation with persistent pattern memory.
- **Commands**: `/setup`, `/feature`, `/plan`, `/design`, `/implement`, `/document-design-intent`, `/diary`
- **Skills**: `design-intent-specialist` (auto-invoked for visual implementation work)
- **Use**: Build React prototypes from Figma/screenshots, capture proven patterns, and maintain design-intent diaries

## Common Development Commands

### Plugin Management

```bash
# Add marketplace from repository root
/plugin marketplace add ./arkhe-claude-plugins

# Install all plugins
/plugin install core@arkhe-claude-plugins
/plugin install ai@arkhe-claude-plugins
/plugin install doc@arkhe-claude-plugins
/plugin install skola@arkhe-claude-plugins     # Includes Udemy extraction
/plugin install review@arkhe-claude-plugins
/plugin install ui@arkhe-claude-plugins
/plugin install google-stitch@arkhe-claude-plugins
/plugin install git@arkhe-claude-plugins
/plugin install design-intent@arkhe-claude-plugins

# Verify installation
/plugin                    # View installed plugins
/agents                    # View available agents
/help                      # View available commands
```

### Testing Plugin Changes

```bash
# After modifying a plugin, reinstall to test
/plugin uninstall plugin-name@arkhe-claude-plugins
/plugin install plugin-name@arkhe-claude-plugins
```

## Plugin Component Guidelines

### Agent Files (agents/*.md)

Agents are specialized AI subagents with focused expertise. Each agent file uses YAML frontmatter:

```markdown
---
name: agent-name
description: When and why to use this agent
tools: Read, Write, Grep, Glob, Bash  # Optional - omit to inherit all
model: sonnet  # Optional - sonnet/opus/haiku or 'inherit'
---

System prompt defining the agent's role, capabilities, and approach.
```

**Agent Naming Convention**: Use lowercase with hyphens (e.g., `docs-architect`, `ai-engineer`)

**Description Guidelines**:
- Clearly state when to use the agent
- Include trigger phrases like "Use PROACTIVELY" or "MUST BE USED" for automatic invocation
- Keep under 1,024 characters

### Command Files (commands/*.md)

Commands are slash commands that expand to full prompts:

```markdown
---
description: Brief description of what this command does
---

# Command Name

Full prompt that Claude Code will execute when the command is invoked.
Include specific instructions, context, and expected behavior.
```

**Command Naming Convention**: Use lowercase with hyphens (e.g., `/doc-generate`, `/code-explain`)

### Skill Files (skills/skill-name/SKILL.md)

Skills are auto-invoked capabilities triggered by context. Use progressive disclosure:

```markdown
---
name: Skill Name
description: What it does. Use when [triggers].
---

# Quick Start
Essential instructions only (<150 lines target)

## Output Structure
What the skill produces

## Common Issues
Quick fixes with references to TROUBLESHOOTING.md

## Examples
Brief examples with reference to EXAMPLES.md
```

**Critical Skill Guidelines**:
- **SKILL.md**: <5,000 tokens (target: <1,000 tokens, ~150 lines)
- **Supporting docs**: Unlimited size (WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md)
- **Scripts**: Python 3.8+ with standard library only, executable (`chmod +x`)
- **Description**: Include specific trigger keywords and use cases

**Skill Execution Pattern**:
1. User action/mention triggers skill (e.g., Udemy URL, "changelog", editing CHANGELOG.md)
2. SKILL.md loads with instructions
3. Supporting docs load on-demand as needed
4. Python scripts execute deterministic operations

## Python Script Guidelines

### Requirements
- **Python Version**: 3.8+
- **Libraries**: Standard library only (no pip install)
- **Execution**: Must be executable (`chmod +x script.py`)
- **Shebang**: Include `#!/usr/bin/env python3`

### Security Constraints
```python
# ✅ ALLOWED
import json, urllib.request, pathlib, re
from pathlib import Path
# Standard library operations

# ❌ FORBIDDEN
import requests  # Third-party package
os.system("pip install package")  # Runtime installation
eval(user_input)  # Code execution risks
```

### Example Script Structure

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

## Token Optimization Strategy

### Progressive Disclosure Architecture

```
Level 1: Metadata (Always Loaded)
├── YAML frontmatter
├── ~100 tokens
└── Purpose: Skill discovery

Level 2: Instructions (Loaded When Triggered)
├── SKILL.md body
├── <1,000 tokens target (<5,000 max)
└── Purpose: Quick start

Level 3+: Resources (Loaded As Needed)
├── WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md
├── Effectively unlimited
└── Purpose: Deep dives
```

### Optimization Techniques

**Extract detailed content**:
```markdown
<!-- ❌ Don't embed everything in SKILL.md -->
## Detailed Workflow
(200 lines of step-by-step instructions)

<!-- ✅ Reference supporting docs -->
## Workflow
See [WORKFLOW.md](WORKFLOW.md) for detailed steps.
```

**Use references over embedding**:
```markdown
<!-- ❌ Don't embed all examples -->
## Examples
(150 lines of code and output)

<!-- ✅ Reference examples file -->
## Examples
See [EXAMPLES.md](EXAMPLES.md) for complete examples.
```

## File Naming Conventions

### Documentation Files
- **UPPERCASE.md** - Documentation and instructions
- **SKILL.md** - Required for skills
- **WORKFLOW.md** - Detailed step-by-step (optional)
- **EXAMPLES.md** - Usage examples (recommended)
- **TROUBLESHOOTING.md** - Error handling (recommended)
- **README.md** - Plugin overview

### Script Files
- **lowercase_with_underscores.py** - Python scripts
- **main.py** or **extract.py** - Entry points
- **module_name.py** - Modules and utilities

### Plugin Metadata
- **plugin.json** - Plugin manifest (in `.claude-plugin/`)
- **marketplace.json** - Marketplace catalog (in root `.claude-plugin/`)

## Plugin Development Workflow

### Creating a New Plugin

```bash
# 1. Create plugin directory structure
mkdir new-plugin
cd new-plugin
mkdir -p .claude-plugin agents commands skills

# 2. Create plugin manifest
cat > .claude-plugin/plugin.json << 'EOF'
{
  "name": "new-plugin",
  "description": "Plugin description",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
EOF

# 3. Add agents, commands, or skills
# See component guidelines above

# 4. Register in marketplace
# Edit ../arkhe-claude-plugins/.claude-plugin/marketplace.json
```

### Testing a New Plugin Locally

```bash
# From parent directory of arkhe-claude-plugins
cd ..
claude  # Start Claude Code

# In Claude Code:
/plugin marketplace add ./arkhe-claude-plugins
/plugin install new-plugin@arkhe-claude-plugins

# Test your components
/agents     # Check if agents appear
/help       # Check if commands appear
# Test skill triggers
```

### Iterating on Plugin Changes

```bash
# After making changes:
/plugin uninstall new-plugin@arkhe-claude-plugins
/plugin install new-plugin@arkhe-claude-plugins

# Test again
```

## Skill Development Best Practices

### YAML Frontmatter

**Required fields**:
```yaml
---
name: Skill Name              # 64 chars max (20-40 recommended)
description: What it does...  # 1,024 chars max (200-400 recommended)
---
```

**Description template**:
```
[What it does]. Use when [trigger scenario 1], [trigger scenario 2], or [trigger scenario 3].
```

**Good description example**:
> Extract complete Udemy course content including video transcripts, articles, quizzes, downloadable resources (PDFs, code files), and external links. Use when user provides a Udemy course URL, mentions extracting/downloading/scraping/archiving Udemy content, analyzing course structure, or wants offline access to course materials.

**Why it works**:
- Lists specific capabilities
- Defines clear triggers
- Includes use cases
- Under 300 characters

### Skill File Organization

```
skills/my-skill/
├── SKILL.md                  # Main instructions (<150 lines)
├── WORKFLOW.md              # Detailed steps (optional)
├── EXAMPLES.md              # Usage examples (recommended)
├── TROUBLESHOOTING.md       # Error handling (recommended)
├── scripts/
│   ├── main.py              # Entry point
│   ├── module1.py
│   ├── module2.py
│   └── tools/               # Testing/analysis utilities
└── templates/               # Output templates (optional)
```

### Pre-Publication Checklist

**Structure**:
- [ ] SKILL.md with YAML frontmatter
- [ ] Name ≤ 64 characters
- [ ] Description ≤ 1,024 characters
- [ ] Description includes "what" and "when"
- [ ] SKILL.md <5,000 tokens (target: <1,000)
- [ ] Supporting docs created (EXAMPLES.md, TROUBLESHOOTING.md)

**Code Quality**:
- [ ] Scripts executable (`chmod +x`)
- [ ] Shebang added (`#!/usr/bin/env python3`)
- [ ] Standard library only
- [ ] No runtime package installation
- [ ] Secure authentication (if needed)

**Documentation**:
- [ ] Quick start examples
- [ ] Output structure documented
- [ ] Common issues listed
- [ ] All file references valid

## Common Pitfalls

### ❌ Embedding Everything in SKILL.md

**Problem**: SKILL.md becomes 500+ lines, consuming excessive tokens

**Solution**: Split into multiple files with references
```markdown
# Quick Start
(Essential steps only)

## Workflow
See [WORKFLOW.md](WORKFLOW.md) for detailed steps.

## Examples
See [EXAMPLES.md](EXAMPLES.md) for complete examples.

## Troubleshooting
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for error handling.
```

### ❌ Broken Documentation References

**Problem**: Moving/renaming files without updating references

**Solution**: Search for references after any file operation
```bash
grep -r "old-filename.md" .
# Update all references to new location
```

### ❌ Vague Descriptions

**Problem**: `description: Processes data. Use when needed.`

**Solution**: Include specific capabilities, triggers, and use cases
```yaml
description: Extract structured data from PDFs including tables, images, and form fields. Use when user provides PDF files, mentions extracting tables/forms from PDFs, or needs to convert PDF data to JSON/CSV.
```

### ❌ Non-Executable Scripts

**Problem**: `bash: permission denied` when running scripts

**Solution**:
```bash
chmod +x scripts/*.py
# Add shebang to all scripts
#!/usr/bin/env python3
```

## Key Documentation Files

### Developer Resources

**Skills Development** (most important for skill creation):
- `docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md` - **PRIMARY GUIDE**: Integrated best practices from official docs and real implementations (custom)
- `docs/SKILLS.md` - Practical guide to creating and managing Agent Skills in Claude Code (synced)
- `docs/AGENT_SKILLS_OVERVIEW.md` - Comprehensive guide to Agent Skills architecture (synced)
- [Official Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md) - Anthropic's official skill authoring guide (online)

**Plugin System**:
- `docs/PLUGINS.md` - Plugin system documentation (synced)
- `docs/SUBAGENTS.md` - Agent configuration and usage guide (synced)
- `docs/COMMANDS.md` - Slash commands reference and development guide (synced)
- `docs/HOOKS.md` - Event handling documentation (synced)

**Development Tools**:
- `docs/CLAUDE_4_BEST_PRACTICES.md` - Official prompt engineering techniques for Claude 4 models (synced)

### Automated Documentation Sync

The `docs/` directory includes both **custom documentation** (written for this project) and **synced documentation** (automated copies of official Claude Code documentation).

**To update synced documentation**:
```bash
cd docs && ./update-claude-docs.sh
```

**Synced files** (7 total):
- SUBAGENTS.md, PLUGINS.md, HOOKS.md, COMMANDS.md, SKILLS.md
- AGENT_SKILLS_OVERVIEW.md, CLAUDE_4_BEST_PRACTICES.md

**Custom files** (never overwritten):
- SKILL_DEVELOPMENT_BEST_PRACTICES.md, README.md

**To add new documentation URLs**:
1. Edit `docs/update-claude-docs.sh` and add to `URL_MAPPINGS` array
2. Run `./update-claude-docs.sh` to download
3. Update README.md, CLAUDE.md, and docs/README.md to reference new file

See [docs/README.md](docs/README.md) "Maintaining This Documentation" section for complete details.

### Plugin Documentation
- `*/README.md` - Plugin overview and usage examples
- `skills/*/SKILL.md` - Skill instructions and quick start
- `skills/*/WORKFLOW.md` - Detailed step-by-step procedures
- `skills/*/EXAMPLES.md` - Comprehensive usage examples
- `skills/*/TROUBLESHOOTING.md` - Error handling and solutions

## Plugin Versions

All plugins are currently at **version 1.0.0**. When making breaking changes, increment the major version and update `plugin.json`.

## Related Documentation

For complete technical specifications:
- **Plugin System**: `docs/PLUGINS.md`
- **Agent Configuration**: `docs/SUBAGENTS.md`
- **Commands Development**: `docs/COMMANDS.md`
- **Skill Development**: `docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md`
- **Prompt Engineering**: `docs/CLAUDE_4_BEST_PRACTICES.md`
- **Installation Guide**: `INSTALLATION.md`
- **Main README**: `README.md`

## External Resources

**Official Documentation**:
- **[Agent Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md)** - Comprehensive authoring guide covering core principles, YAML frontmatter, degrees of freedom, content guidelines, workflows, and evaluation
- [Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) - Introduction to Agent Skills across Claude products
- [Using Skills in Claude Code](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/using-skills) - Practical guide for creating and managing skills

**Official Skill Examples**:
- **[Anthropic Skills Repository](https://github.com/anthropics/skills)** - Official reference implementations of Agent Skills with real-world examples, architecture patterns, and best practices from Anthropic's engineering team
- **[skill-creator Reference](https://github.com/anthropics/skills/tree/main/skill-creator)** - Exemplary official skill demonstrating best practices for YAML frontmatter, writing style (imperative/infinitive form), resource organization (scripts/references/assets), and progressive disclosure architecture. See detailed analysis in `docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md`
