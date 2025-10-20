# Installation Guide

Complete guide to installing and using the Arkhe Claude Plugins.

## Prerequisites

- Claude Code installed and running
- This repository cloned or accessible locally

## Step-by-Step Installation

### 1. Add the Marketplace

From within Claude Code, run:

```bash
/plugin marketplace add /Users/jcosta/Projects/skola.dev/arkhe-claude-plugins
```

Or if you're in the project directory:

```bash
/plugin marketplace add ./arkhe-claude-plugins
```

### 2. Browse Available Plugins

```bash
/plugin
```

Select "Browse Plugins" to see all available plugins in the marketplace.

### 3. Install Plugins

You can install plugins individually or all at once:

#### Install All Plugins

```bash
/plugin install core@arkhe-claude-plugins
/plugin install skola@arkhe-claude-plugins
/plugin install udemy@arkhe-claude-plugins
```

#### Install Selectively

**For documentation work only:**
```bash
/plugin install core@arkhe-claude-plugins
```

**For AI/tutorial development:**
```bash
/plugin install skola@arkhe-claude-plugins
```

**For Udemy extraction:**
```bash
/plugin install udemy@arkhe-claude-plugins
```

### 4. Restart Claude Code

After installation, restart Claude Code for the plugins to take effect.

## Verification

After installation, verify that everything works:

### Check Agents

```bash
/agents
```

You should see:
- From **core**: `docs-architect`
- From **skola**: `tutorial-engineer`, `ai-engineer`, `prompt-engineer`, `context-manager`, `mermaid-expert`

### Check Commands

```bash
/help
```

You should see:
- From **core**: `/discuss`, `/double-check`, `/ultrathink`
- From **skola**: `/doc-generate`, `/code-explain`, `/improve-agent`, `/multi-agent-optimize`

### Check Skills

Skills are automatically invoked. The `extract` skill will activate when you:
- Provide a Udemy course URL
- Ask to extract/download Udemy content
- Mention Udemy course analysis

## Usage Examples

### Using Core Plugin

```bash
# Start a technical discussion
/discuss how should I structure the authentication module?

# Validate your work
/double-check

# Deep analysis
/ultrathink optimization strategies for database queries
```

### Using Skola Plugin

```bash
# Generate documentation
/doc-generate for the API endpoints

# Explain complex code
/code-explain src/utils/parser.ts

# Improve an agent
/improve-agent customer-support

# Create a tutorial
/agents
# Select: tutorial-engineer
```

### Using Udemy Plugin

```bash
# The skill auto-activates when you mention Udemy
Extract this course: https://www.udemy.com/course/python-complete/

# Or just ask
I need to extract transcripts from my Udemy course on React
```

## Managing Plugins

### Update a Plugin

```bash
/plugin update plugin-name@arkhe-claude-plugins
```

### Disable a Plugin (without uninstalling)

```bash
/plugin disable plugin-name@arkhe-claude-plugins
```

### Re-enable a Plugin

```bash
/plugin enable plugin-name@arkhe-claude-plugins
```

### Uninstall a Plugin

```bash
/plugin uninstall plugin-name@arkhe-claude-plugins
```

### Remove the Marketplace

```bash
/plugin marketplace remove arkhe-claude-plugins
```

## Troubleshooting

### Plugins not showing up

1. Ensure you restarted Claude Code after installation
2. Check that the marketplace was added correctly: `/plugin marketplace list`
3. Verify the plugin is installed: `/plugin`

### Commands not working

1. Check the command name with `/help`
2. Ensure the plugin is enabled: `/plugin`
3. Try reinstalling the plugin

### Skills not activating

Skills are model-invoked, so they activate automatically based on context. Make sure:
1. The plugin is installed and enabled
2. Your request clearly matches the skill's use case
3. You're providing the necessary information (e.g., Udemy URL for extract)

## Support

For issues or questions:
1. Check the individual plugin README files
2. Review the skill documentation (for udemy)
3. Open an issue in the repository

## Next Steps

- Read individual plugin READMEs for detailed usage
- Explore agent capabilities with `/agents`
- Try different commands to understand their behavior
- Review the Udemy extraction skill documentation if using that feature
