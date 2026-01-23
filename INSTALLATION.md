# Installation Guide

Complete guide to installing and using the Arkhe Claude Plugins marketplace.

## Prerequisites

- Claude Code installed and running

## Quick Start

### 1. Add the Marketplace

**Option A: Install directly from GitHub (recommended)**

No cloning required! Run this command in Claude Code:

```bash
/plugin marketplace add joaquimscosta/arkhe-claude-plugins
```

**Option B: Clone and install locally**

If you prefer a local copy or want to contribute:

```bash
git clone https://github.com/joaquimscosta/arkhe-claude-plugins.git
/plugin marketplace add ./arkhe-claude-plugins
```

### 2. Install All Plugins

```bash
/plugin install core@arkhe-claude-plugins
/plugin install ai@arkhe-claude-plugins
/plugin install doc@arkhe-claude-plugins
/plugin install review@arkhe-claude-plugins
/plugin install design-intent@arkhe-claude-plugins
/plugin install git@arkhe-claude-plugins
/plugin install google-stitch@arkhe-claude-plugins
/plugin install lang@arkhe-claude-plugins
/plugin install spring-boot@arkhe-claude-plugins
```

### 3. Restart Claude Code

After installation, restart Claude Code for all plugins to take effect.

---

## Plugin Overview

### Core Plugin
Quality control and workflow orchestration utilities.

**Install**: `/plugin install core@arkhe-claude-plugins`

**Components**:
- 5 agents: `deep-think-partner`, `deep-researcher`, `code-explorer`, `code-architect`, `code-reviewer`
- 6 commands: `/discuss`, `/double-check`, `/develop`, `/debug`, `/think`, `/research`
- 3 skills: `sdlc-develop` (command-invoke), `deep-research` (auto-invoke), `workflow-orchestration` (auto-invoke)

---

### AI Plugin
AI engineering toolkit for production-ready LLM applications.

**Install**: `/plugin install ai@arkhe-claude-plugins`

**Components**:
- 3 agents: `ai-engineer`, `prompt-engineer`, `context-manager`
- 2 commands: `/improve-agent`, `/multi-agent-optimize`
- 1 skill: `lyra` (auto-invoked for AI prompt engineering)

---

### Doc Plugin
Multi-purpose documentation toolkit.

**Install**: `/plugin install doc@arkhe-claude-plugins`

**Components**:
- 1 agent: `docs-architect`
- 4 skills: `diagramming` (auto-invoked for diagrams), `documentation-generation`, `code-explanation`, `managing-adrs`
- 3 commands: `/doc-generate`, `/code-explain`, `/diagram`

---

### Review Plugin
Code quality review tools for development teams.

**Install**: `/plugin install review@arkhe-claude-plugins`

**Components**:
- 2 agents: `pragmatic-code-review`, `design-review`
- 4 commands: `/code`, `/security`, `/design`, `/codebase`

---

### Git Plugin
Git workflow automation for commits, pull requests, branching, and changelog generation.

**Install**: `/plugin install git@arkhe-claude-plugins`

**Requirements**: GitHub CLI (`gh`) for PR commands

**Components**:
- 5 commands: `/commit`, `/create-pr`, `/create-branch`, `/changelog`, `/pr-issue-resolve`
- 4 skills: 1 auto-invoke (`generating-changelog`) + 3 command-invoke
- 4 scripts: Shell scripts for git workflow automation

---

### Design Intent Plugin
Design Intent for Spec-Driven Development that combines AI-assisted implementation with documented design patterns.

**Install**: `/plugin install design-intent@arkhe-claude-plugins`

**Components**:
- 6 commands: `/setup`, `/feature`, `/plan`, `/design-intent`, `/save-patterns`, `/diary`
- 1 skill: `design-intent-specialist` (auto-invoked when implementing from visual references)

**Use for:** Capturing team-specific design intent, translating Figma/screenshots into React implementations, and keeping pattern memory plus diaries synchronized.

---

### Google Stitch Plugin
Claude + Google Stitch prompting toolkit for prompt authoring.

**Install**: `/plugin install google-stitch@arkhe-claude-plugins`

**Components**:
- 1 command: `/prompt`
- 2 skills: `authoring-stitch-prompts`, `extracting-stitch-mockups`

**Use for:** Generating Stitch-ready prompts and extracting mockups.

---

### Lang Plugin
Language-specific programming skills for various languages.

**Install**: `/plugin install lang@arkhe-claude-plugins`

**Components**:
- 1 skill: `scripting-bash` (auto-invoked for Bash scripting)

**Use for:** Production-ready Bash scripting, defensive programming patterns, CI/CD scripts, POSIX compliance.

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

### For Code Quality & Review
```bash
/plugin install review@arkhe-claude-plugins
```

### For Git Workflow Automation
```bash
/plugin install git@arkhe-claude-plugins
```

### For UI/UX Design & Frontend Implementation
```bash
/plugin install design-intent@arkhe-claude-plugins
```

### For Google Stitch Prompting
```bash
/plugin install google-stitch@arkhe-claude-plugins
```

### For Language-Specific Programming Guidance
```bash
/plugin install lang@arkhe-claude-plugins
```

---

## Verification

After installation, verify that everything works:

### Check Installed Plugins

```bash
/plugin
```

You should see all 9 plugins listed.

### Check Available Agents

```bash
/agents
```

You should see agents from installed plugins:
- **core**: `deep-think-partner`, `deep-researcher`, `code-explorer`, `code-architect`, `code-reviewer`
- **ai**: `ai-engineer`, `prompt-engineer`, `context-manager`
- **doc**: `docs-architect`
- **review**: `pragmatic-code-review`, `design-review`
- **design-intent**: `ui-explorer`, `ui-architect`, `design-reviewer`

### Check Available Commands

```bash
/help
```

You should see commands from installed plugins:
- **core**: `/discuss`, `/double-check`, `/develop`, `/debug`, `/think`, `/research`
- **ai**: `/improve-agent`, `/multi-agent-optimize`
- **doc**: `/doc-generate`, `/code-explain`, `/diagram`
- **review**: `/code`, `/security`, `/design`, `/codebase`
- **git**: `/commit`, `/create-pr`, `/create-branch`, `/changelog`, `/pr-issue-resolve`
- **design-intent**: `/setup`, `/feature`, `/plan`, `/design-intent`, `/save-patterns`, `/diary`
- **google-stitch**: `/prompt`

### Check Skills

Skills are automatically invoked when relevant context is detected:
- **core**: `workflow-orchestration` activates for complex multi-step tasks; `deep-research` activates for research queries
- **doc**: `diagramming` skill activates when you mention diagrams, flowcharts, or visualization keywords
- **git**: `generating-changelog` skill activates when you edit CHANGELOG.md or request changelog generation
- **design-intent**: `design-intent-specialist` activates when you're implementing UI from visual references or running `/design-intent`
- **google-stitch**: `authoring-stitch-prompts`, `extracting-stitch-mockups` activate for Stitch prompt work
- **lang**: `scripting-bash` skill activates for Bash scripting guidance

---

## Usage Examples

### Core Plugin

```bash
# Start a technical discussion
/discuss how should I structure the authentication module?

# Validate your work
/double-check

# Deep analysis with collaborative thinking
/think optimization strategies for database queries

# Orchestrate complex development workflows
/develop Create a new feature for user authentication
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

### Design Intent Plugin

```bash
# Initialize the design-intent folder structure with memory + templates
/setup

# Create a feature spec + implementation plan scaffolding
/feature onboarding dashboard layout

# Turn Figma or screenshot references into React code
/design https://www.figma.com/file/EXAMPLE

# Capture successful patterns for reuse
/save-patterns

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

### Google Stitch Plugin

```bash
# Generate Stitch-ready prompts
/prompt create a multi-screen onboarding flow

# Skills auto-invoke when working with Stitch
"Help me author a prompt for Stitch"
```

### Lang Plugin

```bash
# Skills auto-invoke for language-specific guidance
"Help me write a robust bash script for deployment"
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
3. You're providing the necessary information (e.g., diagram type for diagramming skill)

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
