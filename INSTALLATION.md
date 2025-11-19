# Installation Guide

Complete guide to installing and using the Arkhe Claude Plugins marketplace.

## Prerequisites

- Claude Code installed and running
- This repository cloned or accessible locally

## Quick Start

### 1. Add the Marketplace

From within Claude Code, navigate to the parent directory of the cloned repository and run:

```bash
/plugin marketplace add ./arkhe-claude-plugins
```

### 2. Install All Plugins

```bash
/plugin install core@arkhe-claude-plugins
/plugin install ai@arkhe-claude-plugins
/plugin install doc@arkhe-claude-plugins
/plugin install skola@arkhe-claude-plugins
/plugin install review@arkhe-claude-plugins
/plugin install ui@arkhe-claude-plugins
/plugin install git@arkhe-claude-plugins
/plugin install design-intent@arkhe-claude-plugins
```

### 3. Restart Claude Code

After installation, restart Claude Code for all plugins to take effect.

---

## Plugin Overview

### Core Plugin
Quality control and workflow orchestration utilities.

**Install**: `/plugin install core@arkhe-claude-plugins`

**Components**:
- 4 commands: `/discuss`, `/double-check`, `/ultrathink`, `/workflow`

---

### AI Plugin
AI engineering toolkit for production-ready LLM applications.

**Install**: `/plugin install ai@arkhe-claude-plugins`

**Components**:
- 3 agents: `ai-engineer`, `prompt-engineer`, `context-manager`
- 2 commands: `/improve-agent`, `/multi-agent-optimize`

---

### Doc Plugin
Multi-purpose documentation toolkit.

**Install**: `/plugin install doc@arkhe-claude-plugins`

**Components**:
- 1 agent: `docs-architect`
- 1 skill: `mermaid` (auto-invoked for diagrams)
- 3 commands: `/doc-generate`, `/code-explain`, `/diagram`

---

### Skola Plugin
Tutorial creation and educational content extraction toolkit (Udemy, YouTube, blogs).

**Install**: `/plugin install skola@arkhe-claude-plugins`

**Components**:
- 1 agent: `tutorial-engineer`
- 1 skill: `extracting-udemy` (auto-invoked for Udemy URLs)
- 2 commands: `/extract`, `/teach-code`

---

### Review Plugin
Code quality review tools for development teams.

**Install**: `/plugin install review@arkhe-claude-plugins`

**Components**:
- 2 agents: `pragmatic-code-review`, `design-review`
- 4 commands: `/code`, `/security`, `/design`, `/codebase`

---

### UI Plugin
UI/UX design and design system toolkit.

**Install**: `/plugin install ui@arkhe-claude-plugins`

**Components**:
- 1 agent: `ui-ux-designer`

---

### Git Plugin
Git workflow automation for commits, pull requests, branching, and changelog generation.

**Install**: `/plugin install git@arkhe-claude-plugins`

**Components**:
- 4 commands: `/commit`, `/create-pr`, `/create-branch`, `/changelog`
- 1 skill: `changelog` (auto-invoked)
- 4 scripts: Shell scripts for git workflow automation

---

### Design Intent Plugin
Design Intent for Spec-Driven Development that combines AI-assisted implementation with documented design patterns.

**Install**: `/plugin install design-intent@arkhe-claude-plugins`

**Components**:
- 7 commands: `/setup`, `/feature`, `/plan`, `/design`, `/implement`, `/document-design-intent`, `/diary`
- 1 skill: `design-intent-specialist` (auto-invoked when implementing from visual references)

**Use for:** Capturing team-specific design intent, translating Figma/screenshots into React implementations, and keeping pattern memory plus diaries synchronized.

---

## Selective Installation

Install only the plugins you need:

### For Documentation Work
```bash
/plugin install core@arkhe-claude-plugins
/plugin install doc@arkhe-claude-plugins
```

### For AI/LLM Development
```bash
/plugin install ai@arkhe-claude-plugins
```

### For Tutorial Creation
```bash
/plugin install skola@arkhe-claude-plugins
/plugin install doc@arkhe-claude-plugins
```

### For Educational Content Extraction
```bash
/plugin install skola@arkhe-claude-plugins    # Includes Udemy, YouTube (coming soon)
```

### For Code Quality & Review
```bash
/plugin install review@arkhe-claude-plugins
```

### For UI/UX Design Work
```bash
/plugin install ui@arkhe-claude-plugins
```

### For Git Workflow Automation
```bash
/plugin install git@arkhe-claude-plugins
```

### For AI-Assisted Frontend Implementation & Design Memory
```bash
/plugin install design-intent@arkhe-claude-plugins
```

---

## Verification

After installation, verify that everything works:

### Check Installed Plugins

```bash
/plugin
```

You should see all 8 plugins listed.

### Check Available Agents

```bash
/agents
```

You should see agents from installed plugins:
- **ai**: `ai-engineer`, `prompt-engineer`, `context-manager`
- **doc**: `docs-architect`
- **skola**: `tutorial-engineer`
- **review**: `pragmatic-code-review`, `design-review`
- **ui**: `ui-ux-designer`

### Check Available Commands

```bash
/help
```

You should see commands from installed plugins:
- **core**: `/discuss`, `/double-check`, `/ultrathink`, `/workflow`
- **ai**: `/improve-agent`, `/multi-agent-optimize`
- **doc**: `/doc-generate`, `/code-explain`, `/diagram`
- **skola**: `/teach-code`
- **review**: `/code`, `/security`, `/design`, `/codebase`
- **git**: `/commit`, `/create-pr`, `/create-branch`, `/changelog`
- **design-intent**: `/setup`, `/feature`, `/plan`, `/design`, `/implement`, `/document-design-intent`, `/diary`

### Check Skills

Skills are automatically invoked when relevant context is detected:
- **doc**: `mermaid` skill activates when you mention diagrams, flowcharts, or visualization keywords
- **skola**: `extracting-udemy` skill activates when you provide Udemy URLs or mention Udemy content extraction
- **git**: `changelog` skill activates when you edit CHANGELOG.md or request changelog generation
- **design-intent**: `design-intent-specialist` activates when you're implementing UI from visual references or running `/design` or `/implement`

---

## Usage Examples

### Core Plugin

```bash
# Start a technical discussion
/discuss how should I structure the authentication module?

# Validate your work
/double-check

# Deep analysis with multi-step thinking
/ultrathink optimization strategies for database queries

# Orchestrate complex workflows
/workflow Create a new feature for user authentication
```

### AI Plugin

```bash
# Use AI engineering agent
/agents
# Select: ai-engineer
"Help me build an intelligent search feature with semantic similarity"

# Improve an existing agent
/improve-agent frontend-engineer

# Optimize multi-agent workflows
/multi-agent-optimize
```

### Doc Plugin

```bash
# Generate documentation
/doc-generate for the API endpoints

# Explain complex code
/code-explain src/utils/parser.ts

# Create diagrams (manual control)
/diagram create a sequence diagram for the authentication flow

# Or use auto-invoke
"I need an ERD for the database schema"
```

### Skola Plugin

```bash
# Create a tutorial
/agents
# Select: tutorial-engineer
"Create a step-by-step tutorial for setting up JWT authentication"

# Generate documentation with educational focus
/doc-generate tutorial for building a REST API
```

### Skola Udemy Extraction Skill

```bash
# The skill auto-activates when you mention Udemy
Extract this course: https://www.udemy.com/course/python-complete/

# Or just ask
I need to extract transcripts from my Udemy course on React
```

### Review Plugin

```bash
# Code review workflow
/code

# Security assessment
/security

# Design review (requires Playwright MCP)
/design

# Complete codebase documentation
/codebase

# Use specialized review agents
/agents
# Select: pragmatic-code-review or design-review
```

### UI Plugin

```bash
# Access UI/UX design expert
/agents
# Select: ui-ux-designer
"Help me create a design token system for our product"
"Review our interface for WCAG 2.1 AA compliance"
"Design accessible form validation patterns"
```

### Design Intent Plugin

```bash
# Initialize the design-intent folder structure with memory + templates
/setup

# Create a feature spec + implementation plan scaffolding
/feature onboarding dashboard layout

# Turn Figma or screenshot references into React code
/design https://www.figma.com/file/EXAMPLE

# Capture successful patterns for reuse
/document-design-intent

# Create a handoff summary before ending the session
/diary
```

### Git Plugin

```bash
# Create context-aware commit
/commit

# Create pull request
/create-pr

# Create feature branch with smart naming
/create-branch

# Generate changelog from commits
/changelog
```

---

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

---

## Troubleshooting

### Plugins Not Showing Up

1. Ensure you restarted Claude Code after installation
2. Check that the marketplace was added correctly: `/plugin marketplace list`
3. Verify the plugin is installed: `/plugin`

### Commands Not Working

1. Check the command name with `/help`
2. Ensure the plugin is enabled: `/plugin`
3. Try reinstalling the plugin

### Agents Not Appearing

1. Check installed plugins with `/plugin`
2. Verify agents with `/agents`
3. Ensure the plugin is enabled (not disabled)

### Skills Not Activating

Skills are model-invoked, so they activate automatically based on context. Make sure:
1. The plugin is installed and enabled
2. Your request clearly matches the skill's use case
3. You're providing the necessary information (e.g., Udemy URL for extract skill)

### Playwright MCP Issues (for design-review)

If the `/design` command or `design-review` agent fails:
1. Verify Playwright MCP server is installed and running
2. Check `.mcp.json` configuration in your project
3. Ensure preview environment is accessible
4. Review MCP server logs for errors

---

## Next Steps

- **Read plugin documentation**: Each plugin has a detailed README with usage examples
- **Explore agents**: Use `/agents` to discover specialized AI assistants
- **Try commands**: Use `/help` to see all available commands and experiment
- **Review skills**: Check individual plugin documentation for skill capabilities
- **Developer documentation**: See `docs/` directory for plugin development guides

---

## Support

For issues or questions:
1. Check individual plugin README files for detailed documentation
2. Review the developer documentation in `docs/`
3. Open an issue in the repository

---

## Additional Resources

- [Main README](./README.md) - Project overview and plugin summaries
- [Developer Documentation](./docs/README.md) - Complete guide for plugin developers
- [Plugin Development Best Practices](./docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md) - Lessons learned from real implementations
- [Claude 4 Best Practices](./docs/CLAUDE_4_BEST_PRACTICES.md) - Official prompt engineering guide
