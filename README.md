<div align="center">
  <h1>Arkhe Claude Plugins</h1>

  <img src="assets/banner.jpg" alt="Arkhe Claude Plugins Banner" width="100%" />


  <p>
    <b>Supercharge Claude Code with 102 specialized components</b> — from deep reasoning and autonomous dev loops to<br />
    DDD architecture, design system enforcement, and git workflow automation. 22 agents, 32 commands, 48 skills across 13 modular plugins.
  </p>

  <p>
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
    </a>
    <img src="https://img.shields.io/badge/Plugins-13-blue" alt="Plugins" />
    <img src="https://img.shields.io/badge/Agents-22-purple" alt="Agents" />
    <img src="https://img.shields.io/badge/Commands-32-orange" alt="Commands" />
    <img src="https://img.shields.io/badge/Skills-48-green" alt="Skills" />
    <a href="https://github.com/joaquimscosta/arkhe-claude-plugins/stargazers">
      <img src="https://img.shields.io/github/stars/joaquimscosta/arkhe-claude-plugins" alt="Stars" />
    </a>
  </p>

  <h4>
    <a href="#rocket-quick-start">Quick Start</a>
    <span> · </span>
    <a href="#electric_plug-available-plugins">Browse Plugins</a>
    <span> · </span>
    <a href="#books-developer-documentation">Developer Docs</a>
    <span> · </span>
    <a href="https://github.com/joaquimscosta/arkhe-claude-plugins/issues">Report Bug</a>
  </h4>
</div>

<br />

---

## :electric_plug: Available Plugins

| Plugin | Description | Key Components | Docs |
| :--- | :--- | :--- | :---: |
| 🧠 **Core** | 6-phase SDLC pipeline with multi-agent orchestration and deep research. | `deep-think-partner`, `deep-researcher`, `/develop`, `/research` | [View](./plugins/core/README.md) |
| 🤖 **AI** | AI engineering toolkit for production LLM apps, RAG, and prompt optimization. | `ai-engineer`, `prompt-engineer`, `lyra`, `/improve-agent` | [View](./plugins/ai/README.md) |
| 📝 **Doc** | Documentation generation with diagrams, ADRs, RFCs, and Johnny.Decimal management. | `rfc-critic`, `adr-critic`, `doc-coauthoring`, `/diagram`, `/rfc` | [View](./plugins/doc/README.md) |
| 🔍 **Review** | Code quality, security, and design reviews with pragmatic standards. | `pragmatic-code-review`, `design-review`, `false-positive-verifier` | [View](./plugins/review/README.md) |
| 🧵 **Stitch** | Atomic UI prompt authoring and MCP-powered Google Stitch screen generation. | `/prompt`, `/stitch-generate`, `generating-stitch-screens` | [View](./plugins/google-stitch/README.md) |
| 🔀 **Git** | Workflow automation with smart commits, PRs, changelogs, and Dependabot triage. | `/commit`, `/create-pr`, `/changelog`, `dependabot-review` | [View](./plugins/git/README.md) |
| 📐 **Design Intent** | Visual React prototyping from Figma/mockups with persistent pattern memory. | `design-intent-specialist`, `/design-intent`, `/save-patterns` | [View](./plugins/design-intent/README.md) |
| 💻 **Lang** | Production-grade language-specific skills (Bash/Shell). | `scripting-bash`, POSIX compliance, ShellCheck | [View](./plugins/lang/README.md) |
| 🎭 **Playwright** | Browser automation via Playwright CLI for testing and screenshots. | `playwright-cli`, `/playwright-setup` | [View](./plugins/playwright/README.md) |
| 🍃 **Spring Boot** | DDD with Spring Boot 4, Modulith 2.0, Security 7, and OpenTelemetry. | 11 skills: DDD, data, web-api, modulith, security, observability, testing, flyway | [View](./plugins/spring-boot/README.md) |
| 🔄 **Ralph** | Autonomous development loop with fresh context, task sets, and memory system. | `ralph-agent`, `/ralph`, `/create-prd`, Hat-lite system | [View](./plugins/ralph/README.md) |
| 🗺️ **Roadmap** | Product management, roadmap analysis, and solution architecture. | `product-manager`, `system-architect`, `roadmap-analyst` | [View](./plugins/roadmap/README.md) |
| 🛠️ **Claude Code** | Interactive environment setup and configuration wizard. | `env-setup` | [View](./plugins/claude-code/README.md) |

---

## :rocket: Quick Start

### 1. Add the Marketplace

**Option A: Install directly from GitHub (recommended)**

```bash
/plugin marketplace add joaquimscosta/arkhe-claude-plugins
```

**Option B: Clone and install locally**

```bash
git clone https://github.com/joaquimscosta/arkhe-claude-plugins.git
/plugin marketplace add ./arkhe-claude-plugins
```

### 2. Install Plugins

You can install all plugins at once:

```bash
/plugin install core@arkhe-claude-plugins
/plugin install ai@arkhe-claude-plugins
/plugin install doc@arkhe-claude-plugins
/plugin install review@arkhe-claude-plugins
/plugin install design-intent@arkhe-claude-plugins
/plugin install git@arkhe-claude-plugins
/plugin install google-stitch@arkhe-claude-plugins
/plugin install lang@arkhe-claude-plugins
/plugin install playwright@arkhe-claude-plugins
/plugin install spring-boot@arkhe-claude-plugins
/plugin install ralph@arkhe-claude-plugins
/plugin install roadmap@arkhe-claude-plugins
/plugin install claude-code@arkhe-claude-plugins
```

*Or install selectively based on your needs.*

### 3. Usage

After installation, run `/reload-plugins` and use:

- **Agents:** Type `/agents` to see and select available agents.
- **Commands:** Type `/help` to see all available commands.
- **Skills:** Skills are automatically invoked when Claude detects relevant tasks.

---

## :compass: Recommendations & Namespacing

### Recommended Plugin Stacks

Start with **`core`** + **`git`** — they provide the SDLC pipeline, deep reasoning, commit/PR automation, and changelog generation that benefit every workflow.

Then add plugins for your focus area:

| Focus | Add These | You Get |
| :--- | :--- | :--- |
| **Frontend/UI** | `design-intent`, `playwright` | Figma-to-React prototyping, pattern memory, browser testing |
| **Backend (Java)** | `spring-boot` | DDD, Spring Modulith, Security 7, observability, Flyway |
| **AI/LLM Apps** | `ai` | RAG systems, prompt optimization, multi-agent coordination |
| **Code Quality** | `review` | Pragmatic code review, security audits, design review |
| **Documentation** | `doc` | Diagrams, ADRs, Johnny.Decimal, co-authored docs |
| **Product/Planning** | `roadmap` | User stories, scope assessment, architecture design |
| **Shell/DevOps** | `lang` | Production Bash scripting, POSIX compliance |
| **Google Stitch** | `google-stitch` | Atomic UI prompts, MCP-powered screen generation |

### Namespacing

If multiple plugins provide commands with similar names, use namespaced invocation:

```bash
# Direct invocation
/commit

# Namespaced invocation (to avoid conflicts)
/git:commit
/design-intent:design-intent
```

---

## :books: Developer Documentation

<details>
<summary><b>Click to expand Developer Resources</b></summary>

### Skills Development

- **[Skills Guide](./docs/reference/SKILLS.md)** — Creating and managing Agent Skills
- **[Skill Development Best Practices](./docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md)** — Real-world lessons and token optimization
- **[Anthropic Skills Repository](https://github.com/anthropics/skills)** — Reference implementations

### Plugin & Agent Development

- **[Plugins Guide](./docs/reference/PLUGINS.md)** — Plugin system documentation
- **[Subagents Guide](./docs/reference/SUBAGENTS.md)** — Agent configuration and usage
- **[Best Practices](./docs/reference/BEST_PRACTICES.md)** — Official Claude Code best practices

### Reference

- **[Claude Code Guide](./docs/CLAUDE_CODE_GUIDE.md)** — Curated practitioner's guide

</details>

<details>
<summary><b>Directory Structure</b></summary>

```
arkhe-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json              # Marketplace catalog
├── plugins/                          # All 13 plugins
│   ├── core/                         # 1. Quality control & orchestration
│   ├── ai/                           # 2. AI engineering toolkit
│   ├── doc/                          # 3. Documentation toolkit
│   ├── review/                       # 4. Code review tools
│   ├── google-stitch/                # 5. Google Stitch prompting
│   ├── git/                          # 6. Git workflow automation
│   ├── design-intent/                # 7. Design Intent for UI development
│   ├── lang/                         # 8. Language-specific skills
│   ├── playwright/                   # 9. Browser automation via Playwright CLI
│   ├── spring-boot/                  # 10. Domain-Driven Design with Spring Boot 4
│   ├── ralph/                        # 11. Autonomous development loop
│   ├── roadmap/                      # 12. Product management & architecture
│   └── claude-code/                  # 13. Claude Code environment setup
├── docs/                             # Developer documentation
├── templates/                        # Plugin templates
├── assets/                           # Project assets
├── README.md
├── INSTALLATION.md
└── CLAUDE.md
```

</details>

---

## :warning: License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
