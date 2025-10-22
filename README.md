# Arkhe Claude Plugins

Collection of Claude Code plugins for documentation, AI engineering, and educational content creation.

## Available Plugins

### 1. Core Plugin

Essential documentation and quality control utilities.

**Components:**
- 1 agent: `docs-architect`
- 3 commands: `/discuss`, `/double-check`, `/ultrathink`

**Use for:** Documentation architecture, technical discussions, quality validation

[View Core Plugin Details →](./core/README.md)

---

### 2. Skola Plugin

Complete AI engineering and tutorial creation toolkit.

**Components:**
- 5 agents: `tutorial-engineer`, `ai-engineer`, `prompt-engineer`, `context-manager`, `mermaid-expert`
- 4 commands: `/doc-generate`, `/code-explain`, `/improve-agent`, `/multi-agent-optimize`

**Use for:** Building AI applications, creating tutorials, generating documentation, optimizing agents

[View Skola Plugin Details →](./skola/README.md)

---

### 3. Udemy Plugin

Udemy course content extraction skill.

**Components:**
- 1 skill: `extract` (auto-invoked when working with Udemy URLs)

**Use for:** Extracting course transcripts, articles, quizzes, resources from Udemy

[View Udemy Plugin Details →](./udemy/README.md)

---

### 4. Review Plugin

Code quality review and workflow orchestration tools.

**Components:**
- 2 agents: `pragmatic-code-review`, `ui-ux-designer`
- 5 commands: `/code`, `/security`, `/design`, `/codebase`, `/workflow`

**Use for:** Code review, security assessment, design review, codebase documentation, workflow orchestration

[View Review Plugin Details →](./review/README.md)

---

### 5. Git Plugin

Git workflow automation for commit, PR, and branching.

**Components:**
- 3 commands: `/commit`, `/create-pr`, `/create-branch`
- 4 scripts: Smart pre-commit checks, PR creation/update, branch naming

**Use for:** Git workflows, automated commits, pull requests, feature branching

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
/plugin install skola@arkhe-claude-plugins
/plugin install udemy@arkhe-claude-plugins
/plugin install review@arkhe-claude-plugins
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
→ Install `core` and `skola`

**For AI/LLM development:**
→ Install `skola`

**For educational content creation:**
→ Install `core` and `skola`

**For Udemy course extraction:**
→ Install `udemy`

**For code quality and review:**
→ Install `review`

**For Git workflow automation:**
→ Install `git`

## Developer Documentation

**For plugin developers and contributors:**

### Skills Development

- **[Agent Skills Overview](./docs/AGENT_SKILLS_OVERVIEW.md)** - Complete guide to understanding and using Agent Skills, including architecture, progressive disclosure, and best practices
- **[Skill Development Best Practices](./docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md)** - Lessons learned from real-world skill implementation, token optimization, and common pitfalls

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
├── docs/                          # Developer documentation
│   ├── AGENT_SKILLS_OVERVIEW.md
│   └── SKILL_DEVELOPMENT_BEST_PRACTICES.md
├── core/
│   ├── .claude-plugin/plugin.json
│   ├── agents/
│   │   └── docs-architect.md
│   ├── commands/
│   │   ├── discuss.md
│   │   ├── double-check.md
│   │   └── ultrathink.md
│   └── README.md
├── skola/
│   ├── .claude-plugin/plugin.json
│   ├── agents/
│   │   ├── tutorial-engineer.md
│   │   ├── ai-engineer.md
│   │   ├── prompt-engineer.md
│   │   ├── context-manager.md
│   │   └── mermaid-expert.md
│   ├── commands/
│   │   ├── doc-generate.md
│   │   ├── code-explain.md
│   │   ├── improve-agent.md
│   │   └── multi-agent-optimize.md
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
