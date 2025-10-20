# Developer Documentation

Welcome to the Arkhe Claude Plugins developer documentation. This directory contains comprehensive guides for understanding and creating Claude Code plugins, agents, commands, and skills.

## Documentation Overview

### 📖 Core Guides

#### [Developer Tools](./DEVELOPER_TOOLS.md)

Reference guide for development and research tools.

**Topics covered:**
- Udemy API Inspector (browser automation for API discovery)
- Request/response analysis workflows
- API endpoint documentation process
- Research tool usage and workflows

**Best for:** Developers extending the plugins or researching new APIs

---

#### [Agent Skills Overview](./AGENT_SKILLS_OVERVIEW.md)

Complete guide to understanding Agent Skills in Claude Code.

**Topics covered:**
- What are Agent Skills and why use them
- How Skills work (progressive disclosure architecture)
- Three-level loading strategy (metadata → instructions → resources)
- Creating custom skills
- Best practices and patterns

**Best for:** Understanding the fundamentals of how skills work in Claude Code

---

#### [Skill Development Best Practices](./SKILL_DEVELOPMENT_BEST_PRACTICES.md)

Lessons learned from real-world skill implementation, specifically from the `extract` skill.

**Topics covered:**
- Progressive disclosure strategy
- YAML frontmatter guidelines
- Token optimization techniques
- File organization patterns
- Security best practices
- Documentation structure
- Common pitfalls and solutions
- Real-world case study (Udemy extractor)

**Best for:** Practical guidance when building your own skills

---

## Plugin Development Resources

### Understanding Plugin Components

The Arkhe Claude Plugins marketplace demonstrates all three types of plugin components:

1. **Agents** (`skola/agents/`, `core/agents/`)
   - Specialized AI assistants with specific expertise
   - Examples: `tutorial-engineer`, `ai-engineer`, `docs-architect`
   - Invoked explicitly via `/agents` menu

2. **Commands** (`skola/commands/`, `core/commands/`)
   - Slash commands for specific tasks
   - Examples: `/discuss`, `/doc-generate`, `/improve-agent`
   - Invoked explicitly via `/command-name`

3. **Skills** (`udemy/skills/`)
   - Model-invoked capabilities (auto-activated by context)
   - Example: `extract` (activates on Udemy URLs)
   - Invoked automatically when Claude detects relevant tasks

### Reference Implementations

Use these plugins as templates for your own development:

#### **core** - Minimal, focused plugin
- 1 agent, 3 commands
- Clean structure for simple utilities
- Good starting point for basic plugins

#### **skola** - Comprehensive plugin
- 5 agents, 4 commands
- Shows how to organize multiple related components
- Demonstrates agent specialization patterns

#### **udemy** - Skill-based plugin
- 1 skill with complete implementation
- Progressive disclosure in action
- Includes Python scripts, documentation, and templates
- Excellent case study for complex skills

---

## Learning Path

### For Beginners

1. **Start here:** Read [Agent Skills Overview](./AGENT_SKILLS_OVERVIEW.md)
2. **Explore examples:** Browse the `core`, `skola`, and `udemy` plugin directories
3. **Understand patterns:** Review the plugin.json files and directory structures
4. **Try it out:** Install the plugins and use them to see how they work

### For Skill Developers

1. **Understand architecture:** Read the progressive disclosure section in [Agent Skills Overview](./AGENT_SKILLS_OVERVIEW.md)
2. **Learn best practices:** Study [Skill Development Best Practices](./SKILL_DEVELOPMENT_BEST_PRACTICES.md)
3. **Examine real code:** Explore `udemy/skills/extract/` in detail
4. **Apply patterns:** Create your own skill following the three-level pattern

### For Plugin Developers

1. **Review structure:** Examine the `arkhe-claude-plugins` marketplace structure
2. **Study components:** Compare `core`, `skola`, and `udemy` organizations
3. **Understand manifests:** Look at `.claude-plugin/plugin.json` files
4. **Create and test:** Build your own plugin using local marketplace for testing

---

## Key Concepts

### Progressive Disclosure

Skills use a three-level architecture to minimize token usage:

- **Level 1 (Metadata)**: ~100 tokens, always loaded, enables discovery
- **Level 2 (Instructions)**: ~1,000 tokens, loaded when triggered, provides quick start
- **Level 3+ (Resources)**: Unlimited, loaded on-demand, offers deep capabilities

This pattern is demonstrated in `udemy/skills/extract/`.

### Plugin Organization

```
your-plugin/
├── .claude-plugin/
│   └── plugin.json          # Required: plugin metadata
├── agents/                   # Optional: agent definitions
│   └── your-agent.md
├── commands/                 # Optional: slash commands
│   └── your-command.md
├── skills/                   # Optional: auto-invoked capabilities
│   └── your-skill/
│       ├── SKILL.md         # Required for skills
│       ├── scripts/         # Optional: executable code
│       └── docs/            # Optional: detailed documentation
└── README.md                # Recommended: usage documentation
```

### Testing Workflow

1. Create a local marketplace directory
2. Add your plugin as a subdirectory
3. Create `.claude-plugin/marketplace.json`
4. Add marketplace to Claude Code: `/plugin marketplace add ./your-marketplace`
5. Install and test: `/plugin install your-plugin@your-marketplace`
6. Iterate: Uninstall, update, reinstall

---

## Additional Resources

### Official Documentation

- [Claude Code Plugins Guide](https://docs.claude.com/en/docs/claude-code/plugins)
- [Agent Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
- [Anthropic Engineering Blog: Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### This Repository

- [Main README](../README.md) - Plugin marketplace overview and quick start
- [Installation Guide](../INSTALLATION.md) - Detailed installation instructions
- Plugin READMEs: [core](../core/README.md), [skola](../skola/README.md), [udemy](../udemy/README.md)

---

## Contributing

Want to contribute to these plugins or create your own?

1. Fork or clone this repository
2. Study the existing plugin structures
3. Follow the patterns and best practices documented here
4. Test thoroughly using a local marketplace
5. Submit contributions or share your own plugins

---

## Questions or Issues?

- Review the [Skill Development Best Practices](./SKILL_DEVELOPMENT_BEST_PRACTICES.md) for common pitfalls
- Examine the `extract` skill as a reference implementation
- Check the official Claude Code documentation
- Open an issue in the repository

Happy plugin development! 🚀
