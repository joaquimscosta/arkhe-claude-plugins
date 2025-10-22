# Developer Documentation

Welcome to the Arkhe Claude Plugins developer documentation. This comprehensive guide helps plugin developers understand Claude Code's plugin architecture, create custom components, and build sophisticated plugins for their workflows.

## Who This Documentation Is For

This documentation is designed primarily for **plugin developers** who want to:

- Understand Claude Code's plugin architecture and component system
- Create custom commands, agents, skills, and hooks
- Build and distribute plugins for their teams or the community
- Learn from real-world reference implementations

Whether you're building your first plugin or architecting complex multi-component systems, this documentation provides the foundation and advanced patterns you need.

---

## Foundational Concepts

Master the core architecture of Claude Code's plugin system. These guides provide essential understanding for all plugin development.

### 📖 [Plugins Guide](./PLUGINS.md)

Complete introduction to Claude Code's plugin system.

**Topics covered:**
- What plugins are and why use them
- Plugin components (commands, agents, skills, hooks)
- Creating and testing plugins locally
- Installing and managing plugins
- Marketplace structure and distribution

**Best for:** Understanding plugin fundamentals and getting started with plugin development

---

### 🤖 [Subagents (Agents) Guide](./SUBAGENTS.md)

Comprehensive guide to creating and using specialized AI subagents.

**Topics covered:**
- What subagents are and their benefits
- Creating agents with custom system prompts
- Configuring tool access and permissions
- Managing agents (project vs user level)
- Plugin agents and integration patterns

**Best for:** Creating specialized AI assistants for task-specific workflows

---

### ⚡ [Hooks Guide](./HOOKS.md)

Learn to customize and extend Claude Code's behavior with event-driven automation.

**Topics covered:**
- Hook events overview (PreToolUse, PostToolUse, Notification, etc.)
- Creating and configuring hooks
- Security considerations
- Practical examples (formatting, logging, notifications)
- Debugging and troubleshooting

**Best for:** Automating workflows and enforcing project-specific conventions

---

## Specialized Topics

Deep-dive into advanced plugin features and patterns for sophisticated use cases.

### 🎯 [Agent Skills Overview](./AGENT_SKILLS_OVERVIEW.md)

Complete guide to understanding Agent Skills in Claude Code.

**Topics covered:**
- What are Agent Skills and why use them
- How Skills work (progressive disclosure architecture)
- Three-level loading strategy (metadata → instructions → resources)
- Creating custom skills
- Best practices and patterns

**Best for:** Understanding the fundamentals of how skills work in Claude Code

---

### 🛠️ [Skill Development Best Practices](./SKILL_DEVELOPMENT_BEST_PRACTICES.md)

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

### 🔍 [Developer Tools](./DEVELOPER_TOOLS.md)

Reference guide for development and research tools.

**Topics covered:**
- Udemy API Inspector (browser automation for API discovery)
- Request/response analysis workflows
- API endpoint documentation process
- Research tool usage and workflows

**Best for:** Developers extending the plugins or researching new APIs

---

## Plugin Development Resources

Now that you understand the foundational concepts and specialized features, explore the five reference implementations that demonstrate these patterns in practice.

### Understanding All Five Plugins

The Arkhe Claude Plugins marketplace demonstrates all plugin component types across five reference implementations. Study these to understand different architectural patterns and use cases.

#### Component Distribution

**Commands** (workflow automation via slash commands):
- **core**: 3 commands - `/discuss`, `/double-check`, `/ultrathink`
- **skola**: 4 commands - `/doc-generate`, `/code-explain`, `/improve-agent`, `/multi-agent-optimize`
- **git**: 3 commands + 4 scripts - `/commit`, `/create-pr`, `/create-branch`
- **review**: 5 commands - `/code`, `/security`, `/design`, `/codebase`, `/workflow`

**Agents** (specialized AI assistants):
- **core**: 1 agent - `docs-architect`
- **skola**: 5 agents - `tutorial-engineer`, `ai-engineer`, `prompt-engineer`, `context-manager`, `mermaid-expert`
- **review**: 2 agents - `pragmatic-code-review`, `ui-ux-designer`

**Skills** (model-invoked capabilities):
- **udemy**: 1 skill - `extract` (auto-activates on Udemy URLs)

**Scripts** (executable automation):
- **git**: 4 scripts - commit.sh, pr.sh, branch.sh, common.sh

### Reference Implementations

Use these plugins as templates for your own development. Each demonstrates different architectural patterns and complexity levels.

#### **core** - Minimal Focused Plugin

**Structure**: 1 agent + 3 commands
**Complexity**: Low
**Key Features**:
- Clean structure for simple utilities
- Essential documentation and quality tools
- Good starting point for basic plugins

**Best for learning**:
- Plugin basics and structure
- Simple command development
- Agent configuration fundamentals

[View Core Plugin Details →](../core/README.md)

---

#### **skola** - Comprehensive Multi-Agent Plugin

**Structure**: 5 agents + 4 commands
**Complexity**: High
**Key Features**:
- Multiple related agents with specializations
- Command coordination across agents
- AI engineering and educational content tools

**Best for learning**:
- Organizing multiple related components
- Agent specialization patterns
- Complex plugin architecture

[View Skola Plugin Details →](../skola/README.md)

---

#### **udemy** - Skills-Based Plugin

**Structure**: 1 skill with complete implementation
**Complexity**: Advanced
**Key Features**:
- Progressive disclosure in action
- Python scripts, documentation, and templates
- Auto-invoked capability based on context
- Comprehensive resource loading strategy

**Best for learning**:
- Skill development and architecture
- Progressive disclosure patterns
- Resource management strategies
- Complex skill implementations

[View Udemy Plugin Details →](../udemy/README.md)

---

#### **git** - Command + Script Integration Pattern

**Structure**: 3 commands + 4 shell scripts
**Complexity**: Medium
**Key Features**:
- Smart pre-commit checks based on file types
- Context-aware repository detection (root + submodules)
- Seamless Git workflow automation
- Conventional commit message generation

**Best for learning**:
- Command development with executable scripts
- Multi-repository handling patterns
- Conditional execution based on file changes
- Shell script integration with Claude Code

[View Git Plugin Details →](../git/README.md)

---

#### **review** - Multi-Component Integration Pattern

**Structure**: 2 agents + 5 commands
**Complexity**: High
**Key Features**:
- Code quality review with Pragmatic Quality framework
- Security assessment with vulnerability analysis
- Design review with Playwright MCP integration
- Workflow orchestration with task tracking

**Best for learning**:
- Coordinating agents and commands
- MCP server integration (Playwright)
- Customizable output paths
- Complex review workflows

[View Review Plugin Details →](../review/README.md)

---

## Learning Paths

Choose your learning path based on your goals and experience level.

### For Beginners

**Goal**: Understand plugin fundamentals and create your first plugin

1. **Start here:** Read [Plugins Guide](./PLUGINS.md) - Understand plugin architecture and components
2. **Understand agents:** Review [Subagents Guide](./SUBAGENTS.md) - Learn about specialized AI assistants
3. **Learn automation:** Explore [Hooks Guide](./HOOKS.md) - Understand event-driven automation
4. **Explore examples:** Browse `core`, `git`, and `review` plugin directories
5. **Create your first plugin:** Follow the quickstart in Plugins Guide
6. **Test locally:** Use the marketplace structure to test your plugin

### For Plugin Developers

**Goal**: Build production-ready plugins with multiple components

1. **Master architecture:** Study all three foundational guides (Plugins, Subagents, Hooks)
2. **Examine reference implementations:**
   - **Simple commands**: Study `git` plugin (commands + scripts)
   - **Agent patterns**: Study `review` plugin (agents + commands)
   - **Comprehensive plugins**: Study `skola` plugin (multi-agent architecture)
3. **Understand component coordination:** Learn how `review` plugin coordinates agents and commands
4. **Apply patterns:** Create your own plugin following established patterns
5. **Test and iterate:** Use local marketplace for development and testing
6. **Distribution:** Package and share via marketplace

### For Skill Developers

**Goal**: Create sophisticated model-invoked capabilities

1. **Understand architecture:** Read progressive disclosure section in [Agent Skills Overview](./AGENT_SKILLS_OVERVIEW.md)
2. **Learn best practices:** Study [Skill Development Best Practices](./SKILL_DEVELOPMENT_BEST_PRACTICES.md)
3. **Examine real implementation:** Explore `udemy/skills/extract/` in detail
4. **Master token optimization:** Apply three-level loading strategy
5. **Build your skill:** Create following progressive disclosure pattern
6. **Test thoroughly:** Verify metadata, instructions, and resource loading

### For Advanced Developers

**Goal**: Build complex integrations and multi-plugin workflows

1. **Multi-component integration:** Study `review` plugin architecture
2. **MCP server integration:** Examine Playwright MCP usage in `/design` command
3. **Hook automation:** Implement sophisticated automation with hooks
4. **Workflow orchestration:** Understand `/workflow` command patterns
5. **Multi-plugin workflows:** Combine `git` + `review` for complete development workflow
6. **Security patterns:** Study security review implementation and best practices
7. **Performance optimization:** Apply progressive disclosure and tool scoping patterns

---

## Key Concepts

The following concepts are essential for understanding how Claude Code plugins work and how to build effective components.

### Plugin Component Types

Claude Code plugins can include four types of components:

1. **Commands** (`commands/`)
   - Slash commands invoked explicitly by users
   - Markdown files with frontmatter configuration
   - Can execute scripts or provide instructions to Claude
   - Examples: `/commit`, `/code`, `/doc-generate`

2. **Agents** (`agents/`)
   - Specialized AI assistants with custom system prompts
   - Can be invoked explicitly or automatically by Claude
   - Use separate context windows from main conversation
   - Examples: `pragmatic-code-review`, `tutorial-engineer`

3. **Skills** (`skills/`)
   - Model-invoked capabilities that activate automatically
   - Progressive disclosure architecture (metadata → instructions → resources)
   - Context-aware activation based on task detection
   - Examples: `extract` skill for Udemy content

4. **Hooks** (`hooks/`)
   - Event-driven automation for Claude Code lifecycle events
   - Run deterministically at specific points (PreToolUse, PostToolUse, etc.)
   - Can block operations or provide feedback to Claude
   - Examples: Auto-formatting, logging, custom permissions

### Progressive Disclosure

Skills use a three-level architecture to minimize token usage while maximizing capability:

- **Level 1 (Metadata)**: ~100 tokens, always loaded, enables discovery
  - Defined in SKILL.md frontmatter
  - Provides name, description, invocation patterns

- **Level 2 (Instructions)**: ~1,000 tokens, loaded when triggered, provides quick start
  - Main SKILL.md content
  - Detailed instructions and workflow guidance

- **Level 3+ (Resources)**: Unlimited tokens, loaded on-demand, offers deep capabilities
  - Additional documentation, templates, scripts
  - Loaded as needed during skill execution

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
├── hooks/                    # Optional: event handlers
│   └── hooks.json
├── scripts/                  # Optional: executable automation
│   └── your-script.sh
└── README.md                # Recommended: usage documentation
```

### Testing Workflow

Develop and test plugins locally before distribution:

1. Create a local marketplace directory
2. Add your plugin as a subdirectory
3. Create `.claude-plugin/marketplace.json`
4. Add marketplace to Claude Code: `/plugin marketplace add ./your-marketplace`
5. Install and test: `/plugin install your-plugin@your-marketplace`
6. Iterate: Uninstall, update, reinstall
7. Verify all components work as expected

### Multi-Plugin Workflows

Combine plugins for comprehensive development workflows:

**Example: Complete Development Cycle**
```bash
# 1. Create feature branch
/create-branch add user authentication

# 2. Make changes and commit
# ... write code ...
/commit

# 3. Review code quality
/code

# 4. Security assessment
/security

# 5. Create pull request
/create-pr
```

This workflow uses both `git` and `review` plugins together, demonstrating how multiple plugins can coordinate for complete development workflows.

---

## Additional Resources

### Official Documentation

- [Claude Code Plugins Guide](https://docs.claude.com/en/docs/claude-code/plugins)
- [Agent Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
- [Anthropic Engineering Blog: Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### This Repository

- [Main README](../README.md) - Plugin marketplace overview and quick start
- [Installation Guide](../INSTALLATION.md) - Detailed installation instructions
- Plugin READMEs: [core](../core/README.md), [skola](../skola/README.md), [udemy](../udemy/README.md), [git](../git/README.md), [review](../review/README.md)

---

## Contributing

Want to contribute to these plugins or create your own?

1. Fork or clone this repository
2. Study the existing plugin structures (all five reference implementations)
3. Follow the patterns and best practices documented here
4. Test thoroughly using a local marketplace
5. Submit contributions or share your own plugins

---

## Questions or Issues?

- Review the [Skill Development Best Practices](./SKILL_DEVELOPMENT_BEST_PRACTICES.md) for common pitfalls
- Examine the reference implementations (`git`, `review`, `core`, `skola`, `udemy`)
- Check the foundational guides (Plugins, Subagents, Hooks)
- Check the official Claude Code documentation
- Open an issue in the repository

Happy plugin development! 🚀
