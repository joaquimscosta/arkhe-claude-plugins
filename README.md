# Arkhe Claude Plugins

Collection of Claude Code plugins for documentation, AI engineering, and educational content creation.

## Available Plugins

### 1. Core Plugin

Quality control and workflow orchestration utilities.

**Components:**
- 4 commands: `/discuss`, `/double-check`, `/ultrathink`, `/workflow`

**Use for:** Technical discussions, quality validation, workflow orchestration

[View Core Plugin Details →](./core/README.md)

---

### 2. AI Plugin

AI engineering toolkit for building production-ready LLM applications.

**Components:**
- 3 agents: `ai-engineer`, `prompt-engineer`, `context-manager`
- 2 commands: `/improve-agent`, `/multi-agent-optimize`

**Use for:** Building AI-powered features, optimizing prompts, managing context in multi-agent workflows

[View AI Plugin Details →](./ai/README.md)

---

### 3. Doc Plugin

Multi-purpose documentation toolkit.

**Components:**
- 2 agents: `docs-architect`, `mermaid-expert`
- 2 commands: `/doc-generate`, `/code-explain`

**Use for:** Generating technical documentation, creating architecture diagrams, explaining complex code

[View Doc Plugin Details →](./doc/README.md)

---

### 4. Skola Plugin

Tutorial and educational content toolkit.

**Components:**
- 1 agent: `tutorial-engineer`
- 1 command: `/teach-code`

**Use for:** Creating step-by-step tutorials, educational code explanations, progressive learning experiences

[View Skola Plugin Details →](./skola/README.md)

---

### 5. Udemy Plugin

Udemy course content extraction skill.

**Components:**
- 1 skill: `extract` (auto-invoked when working with Udemy URLs)

**Use for:** Extracting course transcripts, articles, quizzes, resources from Udemy

[View Udemy Plugin Details →](./udemy/README.md)

---

### 6. Review Plugin

Code quality review tools for development teams.

**Components:**
- 2 agents: `pragmatic-code-review`, `design-review`
- 4 commands: `/code`, `/security`, `/design`, `/codebase`

**Use for:** Code review, security assessment, design review with Playwright MCP, codebase documentation

[View Review Plugin Details →](./review/README.md)

---

### 7. UI Plugin

UI/UX design and design system toolkit.

**Components:**
- 1 agent: `ui-ux-designer`

**Use for:** Design systems, accessibility compliance, user research, component library design, design-to-development handoff

[View UI Plugin Details →](./ui/README.md)

---

### 8. Git Plugin

Git workflow automation for commit, PR, branching, and changelog generation.

**Components:**
- 4 commands: `/commit`, `/create-pr`, `/create-branch`, `/changelog`
- 1 skill: `changelog` (auto-invoked)
- 4 scripts: Smart pre-commit checks, PR creation/update, branch naming

**Use for:** Git workflows, automated commits, pull requests, feature branching, changelog generation

[View Git Plugin Details →](./git/README.md)

---

## Quick Start

### 1. Add the Marketplace

```bash
/plugin marketplace add ./arkhe-claude-plugins
```

### 2. Install Plugins

Install all plugins:
```bash
/plugin install core@arkhe-claude-plugins
/plugin install ai@arkhe-claude-plugins
/plugin install doc@arkhe-claude-plugins
/plugin install skola@arkhe-claude-plugins
/plugin install udemy@arkhe-claude-plugins
/plugin install review@arkhe-claude-plugins
/plugin install ui@arkhe-claude-plugins
/plugin install git@arkhe-claude-plugins
```

Or install selectively based on your needs.

### 3. Use the Plugins

After installation, restart Claude Code and use:

- **Agents**: Type `/agents` to see and select available agents
- **Commands**: Type `/help` to see all available commands
- **Skills**: Skills are automatically invoked when Claude detects relevant tasks

## Plugin Recommendations

**For documentation work:**
→ Install `core` and `doc`

**For AI/LLM development:**
→ Install `ai`

**For educational content creation:**
→ Install `skola` and `doc`

**For tutorial creation:**
→ Install `skola`

**For Udemy course extraction:**
→ Install `udemy`

**For code quality and review:**
→ Install `review`

**For UI/UX design and design systems:**
→ Install `ui`

**For Git workflow automation:**
→ Install `git`

## Developer Documentation

**For plugin developers and contributors:**

### Skills Development

- **[Agent Skills Overview](./docs/AGENT_SKILLS_OVERVIEW.md)** - Complete guide to understanding and using Agent Skills, including architecture, progressive disclosure, and best practices
- **[Skill Development Best Practices](./docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md)** - Lessons learned from real-world skill implementation, token optimization, and common pitfalls

### Prompt Engineering & Best Practices

- **[Claude 4 Best Practices](./docs/CLAUDE_4_BEST_PRACTICES.md)** - Official prompt engineering techniques for Claude 4 models (Sonnet 4.5, Opus 4.1, Haiku 4.5) including instruction following, context optimization, and migration guidance

### Creating Your Own Plugins

Want to extend these plugins or create your own?

1. Review the existing plugin structure in this repository
2. Read the [Skills Development Best Practices](./docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md) for technical guidance
3. Follow the patterns established in `core`, `skola`, and `udemy`
4. Test locally using the marketplace structure

## Directory Structure

```
arkhe-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json
├── docs/                                      # Developer documentation
│   ├── AGENT_SKILLS_OVERVIEW.md              # ← Synced from Claude docs
│   ├── CLAUDE_4_BEST_PRACTICES.md            # ← Synced from Claude docs
│   ├── COMMANDS.md                           # ← Synced from Claude docs
│   ├── DEVELOPER_TOOLS.md                    # Custom development guide
│   ├── HOOKS.md                              # ← Synced from Claude docs
│   ├── PLUGINS.md                            # ← Synced from Claude docs
│   ├── SKILL_DEVELOPMENT_BEST_PRACTICES.md   # Custom lessons learned
│   ├── SUBAGENTS.md                          # ← Synced from Claude docs
│   ├── README.md                             # Documentation index
│   └── update-claude-docs.sh                 # Automated doc sync script
├── core/
│   ├── .claude-plugin/plugin.json
│   ├── agents/
│   ├── commands/
│   │   ├── discuss.md
│   │   ├── double-check.md
│   │   └── ultrathink.md
│   └── README.md
├── skola/
│   ├── .claude-plugin/plugin.json
│   ├── agents/
│   │   └── tutorial-engineer.md
│   ├── commands/
│   │   └── teach-code.md
│   └── README.md
├── udemy/
│   ├── .claude-plugin/plugin.json
│   ├── skills/
│   │   └── extract/
│   └── README.md
├── README.md
└── INSTALLATION.md
```

## Version

All plugins are currently at version 1.0.0

## License

See individual plugin directories for licensing information.
