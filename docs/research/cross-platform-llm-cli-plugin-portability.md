---
title: Cross-platform LLM CLI Plugin Portability
version: "1.0.0"
status: Published
created: 2026-03-04
last_updated: 2026-03-04
slug: cross-platform-llm-cli-plugin-portability
aliases: []
tags: ["gemini-cli", "codex-cli", "mcp", "plugin-portability", "cross-platform", "agent-skills", "SKILL.md"]
promoted_at: 2026-03-04T14:10:39.107263Z
last_refreshed: 2026-03-04T13:33:44.739543+00:00
sources: []
---

<!-- AUTO-GENERATED: Start -->
# Cross-platform LLM CLI Plugin Portability

## Overview

As of March 2026, the three dominant AI coding CLIs — Anthropic's Claude Code, Google's Gemini CLI, and OpenAI's Codex CLI — have converged on a partially shared plugin ecosystem while retaining distinct native extension systems. The most important development is that **Agent Skills (the SKILL.md open standard)** has achieved cross-platform adoption across all three tools and 40+ other platforms, making it the most viable reuse path today.

The landscape divides into two tiers of portability:

1. **High portability (works today)**: Agent Skills (SKILL.md format) and MCP servers are natively supported by all three CLIs. A skill written once runs unchanged on Claude Code, Gemini CLI, and Codex CLI.

2. **Low portability (requires conversion)**: Claude Code's agents (YAML frontmatter .md files), commands (markdown files expanding to prompts), and hooks have no direct equivalents that auto-import. Gemini CLI's extensions (gemini-extension.json) and Codex CLI's AGENTS.md are tool-specific.

Anthropic donated MCP to the Linux Foundation's Agentic AI Foundation in December 2025, with OpenAI, Google, Microsoft, and others as co-founders. MCP now has 97M+ monthly SDK downloads and is the de facto standard for tool connectivity.

## Key Concepts

### The Agent Skills Open Standard (SKILL.md)

Agent Skills is an open specification originally created by Anthropic and now adopted by 40+ tools including Claude Code, Gemini CLI, Codex CLI, Cursor, Windsurf, GitHub Copilot, Goose, Amp, and others. A skill is:

- A directory containing a `SKILL.md` file with YAML frontmatter
- Optional subdirectories: `scripts/`, `references/`, `assets/`
- Zero compiled binaries, zero runtime dependencies, zero vendor lock-in

**Universal SKILL.md format:**
```markdown
---
name: my-skill           # Required: 1-64 chars, lowercase with hyphens
description: |           # Required: 1-1024 chars, describes WHEN to activate
  Expertise in auditing APIs. Use when the user asks to "check",
  "test", or "audit" a URL or API endpoint.
---

# My Skill Instructions

Instructions for the agent in Markdown.

## Workflow
1. Step one
2. Step two

## References
See ./references/guide.md for detailed steps.
```

**Progressive disclosure pattern** works across all platforms:
- Level 1 (always loaded): YAML frontmatter ~100 tokens per skill
- Level 2 (on activation): Full SKILL.md body, target < 500 lines / 5K tokens
- Level 3 (on demand): `scripts/`, `references/`, `assets/` subdirectories

### Platform-Specific Skill Directories

| Platform | Project-level path | Global/personal path |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` |
| OpenAI Codex | `.agents/skills/` | `~/.codex/skills/` |
| Cursor | `.cursor/skills/` | — |
| VS Code / Copilot | `.github/skills/` | — |
| **Universal (all)** | `.agents/skills/` | varies |

The `.agents/skills/` directory is the emerging universal location supported by all tools. Using it maximizes compatibility when you do not know which tool a developer uses.

### MCP (Model Context Protocol)

MCP is the standard for exposing tools, resources, and prompts to AI agents. All three CLIs support MCP as a first-class citizen:

| CLI | MCP Support | Transport | Config location |
|---|---|---|---|
| Claude Code | Full | STDIO + HTTP | `.claude/mcp.json` or `claude mcp add` |
| Gemini CLI | Full (STDIO + HTTP) | Both | `~/.gemini/settings.json` `mcpServers` key, or via extensions |
| Codex CLI | STDIO only (as of March 2026) | STDIO only | `~/.codex/config.toml` `[mcp_servers.*]` |

**Codex limitation**: As of March 2026, Codex CLI only supports STDIO MCP servers. Remote MCP over SSE or Streamable HTTP is not supported yet.

---

## Gemini CLI Extensibility (Deep Dive)

### Native Extension System: gemini-extension.json

Launched October 2025, extensions are the primary packaging unit for Gemini CLI customizations. An extension is a self-contained directory installable from GitHub or local paths.

**Extension directory structure:**
```
my-extension/
├── gemini-extension.json        # Required: manifest
├── GEMINI.md                    # Optional: persistent context
├── commands/                    # Optional: slash commands
│   └── group/
│       └── command.toml
├── skills/                      # Optional: Agent Skills (SKILL.md)
│   └── skill-name/
│       └── SKILL.md
└── package.json                 # If using Node.js MCP server
```

**gemini-extension.json manifest:**
```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "contextFileName": "GEMINI.md",
  "settings": [{
    "name": "API Key",
    "envVar": "MY_API_KEY",
    "sensitive": true
  }],
  "mcpServers": {
    "serverName": {
      "command": "node",
      "args": ["${extensionPath}${/}server.js"],
      "cwd": "${extensionPath}"
    }
  },
  "excludeTools": ["run_shell_command"]
}
```

**Extension install command:**
```bash
gemini extensions install https://github.com/org/my-extension
gemini extensions install ./local-extension-folder
```

Extensions auto-configure their settings upon installation via a prompted setup flow (Feb 2026 feature).

### GEMINI.md Context Files

Equivalent of Claude Code's CLAUDE.md. Loaded hierarchically:
1. `~/.gemini/GEMINI.md` — global scope
2. Ancestor directories up to `.git` root — project scope
3. Subdirectory files (respects `.gitignore`) — component scope

All discovered files are concatenated and sent with every prompt.

**Key difference from CLAUDE.md**: Gemini CLI can be configured to accept alternative filenames:
```json
{
  "context": {
    "fileName": ["AGENTS.md", "CONTEXT.md", "GEMINI.md"]
  }
}
```
This means if you name your file `AGENTS.md`, Gemini CLI will read it (if configured). **Important: this is not the default.** By default only `GEMINI.md` is loaded.

**Import syntax** (`@file.md`) allows breaking large files into modules.

**Slash command:** `/memory show`, `/memory refresh`, `/memory add <text>`

### Custom Commands (TOML format)

Gemini CLI commands are defined in TOML files, not Markdown:

**File locations:**
- Project: `.gemini/commands/group/command.toml`
- Global: `~/.gemini/commands/group/command.toml`
- Extension-bundled: inside extension directory `commands/`

**Command format:**
```toml
description = "Generates a Git commit message based on staged changes."
prompt = """Please generate a commit message for the following changes:
!{git diff --staged}

Use conventional commits format."""
```

**Supported interpolations:**
- `{{args}}` — user-provided arguments
- `!{shell command}` — execute shell command and inject output
- `@{path/to/file.md}` — include file contents

Commands are invoked as `/group:command` or `/command` (no namespace needed for ungrouped).

### Hooks System (Jan 2026)

Hooks are scripts executed at specific lifecycle events within the Gemini CLI agent loop:

**Hook events (10 total):**

| Event | Trigger | Key Use |
|---|---|---|
| `SessionStart` | Session begins | Inject context, init resources |
| `SessionEnd` | Session ends | Clean up, save state |
| `BeforeAgent` | Before planning | Add context, validate prompts |
| `AfterAgent` | Agent loop completes | Review output, force retry |
| `BeforeModel` | Before LLM request | Modify prompts |
| `AfterModel` | After LLM response | Filter/redact |
| `BeforeToolSelection` | Before tool selection | Filter available tools |
| `BeforeTool` | Before tool execution | Validate, block dangerous ops |
| `AfterTool` | After tool execution | Process results, run tests |
| `PreCompress` | Context compression | Advisory only |

**Hook configuration in settings.json:**
```json
{
  "hooks": {
    "BeforeTool": [{
      "matcher": "write_.*",
      "hooks": [{
        "name": "security-check",
        "type": "command",
        "command": "/path/to/check.sh",
        "timeout": 5000
      }]
    }]
  }
}
```

**Hook exit code semantics:**
- `0` → Success, parse stdout as JSON response
- `2` → Block operation, stderr becomes rejection reason
- Other → Non-fatal warning, proceed with defaults

**No direct equivalent in Claude Code or Codex CLI** as of March 2026. Claude Code has hooks (PostToolUse, etc.) but with different configuration format.

### Gemini CLI Settings Hierarchy

```
/etc/gemini-cli/system-defaults.json  (system-wide defaults)
~/.gemini/settings.json               (user-level)
.gemini/settings.json                 (project-level)
environment variables (.env)
command-line flags
```

---

## OpenAI Codex CLI Extensibility (Deep Dive)

### AGENTS.md System

The primary customization mechanism. Codex reads AGENTS.md files before any work starts.

**Discovery precedence (lowest to highest):**
1. `~/.codex/AGENTS.md` — global scope
2. Project root AGENTS.md (walking up to `.git`)
3. Subdirectory AGENTS.md files (walking down to cwd)
4. `AGENTS.override.md` takes priority over `AGENTS.md` at same level

**Key behaviors:**
- Files are concatenated in order (root → current dir), later files override earlier
- Skips empty files, stops at 32 KiB combined (configurable via `project_doc_max_bytes`)
- No YAML frontmatter — pure prose Markdown only
- Global: `~/.codex/AGENTS.md`

**Alternative filenames** can be configured in `config.toml`:
```toml
project_doc_fallback_filenames = ["CLAUDE.md", "README.md"]
```

This means Codex can be configured to read `CLAUDE.md`! This is the most direct compatibility bridge with Claude Code.

### config.toml (Codex Configuration)

Shared between CLI and VS Code extension. Located at `~/.codex/config.toml` (global) and `.codex/config.toml` (project-level).

**Key configuration sections:**
```toml
model = "gpt-5-codex"
approval_policy = "on-request"   # never | on-request | trusted

# MCP servers (STDIO only as of March 2026)
[mcp_servers.my-server]
command = "npx"
args = ["-y", "@org/my-mcp-server"]
env = { API_KEY = "..." }

# Multi-agent roles
[agents]
max_threads = 4

[agents.planner]
model = "gpt-5.2"
reasoning_effort = "high"

[agents.implementer]
model = "gpt-5.3-codex"
reasoning_effort = "low"

# Feature flags
[features]
child_agents_md = true   # hierarchical AGENTS.md scope
multi_agents = true      # parallel sub-agent threads
```

**Note on sub-agent configuration:** As of March 2026, the `[agents]` section and `agents_config.toml` for per-sub-agent configuration are experimental/in development. An open GitHub issue (#11701) shows active community demand for SKILL.md-style sub-agent definitions.

### Codex CLI Skills (Experimental, Dec 2025)

Codex added experimental SKILL.md support in December 2025. Skills live in:
- `~/.codex/skills/` — global
- `.agents/skills/` — project-level (universal location)

**To enable:**
```bash
codex --enable skills
```

The format is identical to Claude Code SKILL.md. Once enabled, Codex automatically discovers skills at session start.

### Codex Slash Commands (Built-in only)

As of March 2026, Codex does **not** support user-defined slash commands in the way Claude Code or Gemini CLI do. Built-in commands include:

| Command | Purpose |
|---|---|
| `/agent` | Switch active agent thread |
| `/init` | Generate AGENTS.md scaffold |
| `/mcp` | List configured MCP tools |
| `/review` | Analyze working tree diffs |
| `/model` | Switch model mid-session |
| `/copy` | Copy latest output |
| `/clear` | Clear and start fresh |

**There is an open GitHub issue (#5419) requesting custom slash commands.** User-defined commands are not yet implemented.

### Codex Multi-Agent Support (Experimental)

Codex supports parallel sub-agent threads (experimental feature flag `multi_agents`). Sub-agents can be configured in `config.toml` under `[agents]`. An `agents_config.toml` format is being developed to support per-agent role definitions similar to how Claude Code uses sub-agent markdown files.

---

## Component Mapping: Claude Code → Gemini CLI → Codex CLI

### Agents (Subagents)

| Component | Claude Code | Gemini CLI | Codex CLI |
|---|---|---|---|
| **Format** | `.md` file with YAML frontmatter (name, description, model, tools) | Not a first-class concept; extensions bundle skills+MCP | Experimental via `agents_config.toml` + `[agents]` in config.toml |
| **Discovery** | Auto-discovered from `agents/` dirs in plugins | No equivalent auto-spawn | `/agent` command, `--spawn-agent` flag (experimental) |
| **System prompt** | Markdown body of the .md file | GEMINI.md context file or extension-bundled GEMINI.md | AGENTS.md body |
| **Model selection** | `model:` frontmatter field | Model selected per session/prompt | `model` key in `[agents.name]` block |
| **Tool restriction** | `tools:` frontmatter field | `excludeTools` in extension manifest | No fine-grained tool restriction per-agent yet |
| **Portability today** | Source format | Must convert to GEMINI.md + extension | Must convert to AGENTS.md + `agents_config.toml` |

**Practical mapping:** A Claude Code agent file maps most cleanly to:
- Gemini CLI: A GEMINI.md context file bundled in an extension (always-on context, not on-demand)
- Codex CLI: An AGENTS.md file or a dedicated AGENTS.override.md in a subdirectory

### Commands (Slash Commands)

| Component | Claude Code | Gemini CLI | Codex CLI |
|---|---|---|---|
| **Format** | `.md` file in `commands/` dir, YAML frontmatter + prompt body | `.toml` file in `commands/` dir or extension | Not user-definable yet (open feature request) |
| **Parameter syntax** | `$ARGUMENTS` or `{{param}}` in body | `{{args}}` (catch-all) + `!{shell}` for dynamic content | N/A |
| **Invocation** | `/command-name` | `/group:command` or `/command` | N/A (built-ins only) |
| **Shell execution** | Limited (via bash tool in body) | Yes: `!{shell command}` in prompt field | N/A |
| **File inclusion** | Via prompt body | `@{path/to/file.md}` | N/A |
| **Portability today** | Must convert format | Direct source (if Claude commands converted) | Cannot port (feature missing) |

**Key difference:** Claude Code commands use Markdown with prose body; Gemini CLI uses TOML with a `prompt` key. The `ai-command-converter` tool (github.com/Commands-com/ai-command-converter) handles bidirectional conversion.

**Conversion rules:**
- Claude `{{param}}` → Gemini `{{args}}` with natural language description in prompt
- Claude YAML frontmatter → TOML `description` + `prompt` fields
- Claude file body → Gemini TOML `prompt = """..."""` block

### Skills (Auto-invoked Capabilities)

This is where the most portability exists today.

| Component | Claude Code | Gemini CLI | Codex CLI |
|---|---|---|---|
| **Format** | SKILL.md with YAML frontmatter | SKILL.md with YAML frontmatter (identical) | SKILL.md with YAML frontmatter (identical) |
| **Project directory** | `.claude/skills/` | `.gemini/skills/` | `.agents/skills/` |
| **Global directory** | `~/.claude/skills/` | `~/.gemini/skills/` | `~/.codex/skills/` |
| **Universal directory** | `.agents/skills/` | `.agents/skills/` | `.agents/skills/` |
| **Discovery** | Automatic at session start | Automatic at session start | Automatic (when `--enable skills` flag set) |
| **Activation** | Model decides based on description + context | Model decides, asks permission | Model decides based on description |
| **Supporting files** | `scripts/`, `references/`, `assets/` | `scripts/`, `references/`, `assets/` | `scripts/`, `references/`, `assets/` |
| **`allowed-tools` field** | Fully supported | Partially supported | Not supported (ignored) |
| **Portability today** | Source format | 100% compatible (same SKILL.md) | Experimental, same format |

**Skills are the highest-portability component.** The SKILL.md format works unchanged across all three tools. The only consideration is using `.agents/skills/` as the directory to maximize tool compatibility.

### Scripts (Python/Shell scripts executed by skills)

| Component | Claude Code | Gemini CLI | Codex CLI |
|---|---|---|---|
| **Execution** | Via Bash tool calls from within skill instructions | Via shell execution (Node.js shown in examples, any interpreter works) | Via shell execution within skill or AGENTS.md |
| **Language** | Any (Python 3.8+ stdlib preferred per Arkhe conventions) | Any (Node.js commonly used in examples) | Any |
| **Portability** | High — scripts are tool-agnostic, executed via shell | High | High |
| **Discovery** | `scripts/` subdirectory in skill | `scripts/` subdirectory in skill | `scripts/` subdirectory in skill |

Scripts are portable. The execution mechanism is always "the CLI runs it via shell." Python scripts work on all platforms.

---

## Standards Landscape

### MCP (Model Context Protocol)

- Created by Anthropic November 2024; donated to Linux Foundation Agentic AI Foundation (AAIF) in December 2025
- Co-founded with OpenAI, Block, Google, Microsoft, AWS, Bloomberg, Cloudflare as platinum members
- 97M+ monthly downloads of Python and TypeScript SDKs
- 10,000+ active MCP servers
- Supported by: Claude Code, Gemini CLI, Codex CLI, VS Code, Cursor, Windsurf, Xcode 26.3, and many more
- **This is the de facto standard for tool connectivity.** MCP servers written once work everywhere.

**Key limitation**: Codex CLI only supports STDIO transport (not HTTP/SSE). Gemini CLI supports both. Claude Code supports both.

### Google Agent-to-Agent Protocol (A2A)

- Google's protocol for agent-to-agent communication (not tool connectivity)
- 100+ enterprise adopters as of Feb 2026
- Distinct from MCP: MCP = agent to tools, A2A = agent to agent
- Less relevant for CLI plugin portability; more relevant for multi-agent orchestration architectures

### OSSA (Open Standard for Software Agents)

- Version 0.4.0 (Feb 2026), maintained by Bluefly.io / openstandardagents.org
- Declarative YAML/JSON spec: "the OpenAPI for AI agents"
- Defines agent identity, capabilities, trust boundaries, governance
- Platform extensions for: Cursor, OpenAI, CrewAI, LangChain, Anthropic, Langflow, AutoGen
- Validated via `npm install -g @bluefly/openstandardagents` CLI

**Example OSSA manifest:**
```yaml
apiVersion: ossa/v0.4.0
kind: Agent
metadata:
  name: security-audit-agent
  description: "Analyzes pull requests for CVEs and logic flaws"
spec:
  role: "Expert Security Engineer"
  capabilities:
    - type: tool-use
      protocol: mcp
      tools:
        - name: read_git_diff
          description: "Fetch changes from the current branch"
  efficiency:
    tier: standard
    promptCaching: true
  orchestration:
    completionSignals: [...]
```

OSSA is early-stage but represents the most ambitious interoperability layer. It sits above MCP and A2A as a contract layer.

### Agent Skills Open Standard

- Emerged from Anthropic's Claude Code SKILL.md format
- Adopted by 40+ tools as of March 2026
- Package registry: skills.sh (Vercel Labs, Jan 2026) with 84,000+ skills indexed
- `npx skills` CLI auto-detects installed agents and installs to all correct directories
- 399K+ installs of the `find-skills` skill alone

**Installation:**
```bash
npx skills add anthropics/skills           # Official Anthropic collection
npx skills add vercel-labs/agent-skills    # Vercel React/Next.js skills
npx skills add microsoft/github-copilot-for-azure  # Azure skills
npx skills add ./my-local-skill-dir       # Local path
```

---

## Practical Portability Architectures

### Architecture 1: Agent Skills as the Universal Layer (RECOMMENDED TODAY)

**Best for:** Porting Claude Code Skills to other tools

Skills are already cross-platform. The only work needed is ensuring the SKILL.md is in the right directory for each tool.

**Strategy:**
1. Keep skills in `.agents/skills/` (universal path, supported by all three CLIs)
2. Use `npx skills add` for installation automation
3. Avoid `allowed-tools` frontmatter field (only Claude Code honors it fully)
4. Keep skill descriptions platform-neutral (no Claude-specific terminology)

**What you get:** Skills work identically on Claude Code, Gemini CLI (natively), Codex CLI (with `--enable skills` flag).

### Architecture 2: MCP Bridge for Agents and Commands

**Best for:** Exposing Claude Code agents/commands as tool calls to other CLIs

Convert Claude Code agents into MCP servers that expose the agent's capabilities as MCP tools. Any CLI with MCP support (Gemini CLI, Codex CLI, VS Code, etc.) can then call the agent's functionality via tool calls.

**Implementation:**
1. Wrap each agent's capability as an MCP tool using `@modelcontextprotocol/sdk`
2. Host as STDIO MCP server (works on all three CLIs)
3. Bundle the system prompt as a tool description or as GEMINI.md/AGENTS.md context
4. Register in each tool's MCP config

**Limitation:** Loses the "sub-agent spawning" behavior; exposes as tools instead. Works best for deterministic skill-like capabilities rather than open-ended agents.

### Architecture 3: Context File Injection (System Prompt Mapping)

**Best for:** Porting CLAUDE.md and agent system prompts to other tools

Map instruction files:

| Source | Target Gemini CLI | Target Codex CLI |
|---|---|---|
| `.claude/CLAUDE.md` | `.gemini/GEMINI.md` or set `fileName: ["CLAUDE.md"]` in settings.json | `.codex/AGENTS.md` or set `project_doc_fallback_filenames = ["CLAUDE.md"]` in config.toml |
| Agent system prompt body | Extension-bundled GEMINI.md | AGENTS.override.md in relevant subdirectory |
| Plugin README | Append to GEMINI.md/AGENTS.md | Append to AGENTS.md |

**Codex trick:** `project_doc_fallback_filenames = ["CLAUDE.md"]` makes Codex read your existing CLAUDE.md files. Similarly, Gemini CLI's `context.fileName` can include `["CLAUDE.md", "GEMINI.md"]`. This is the lowest-effort compatibility bridge.

### Architecture 4: Command Format Transpiler

**Best for:** Sharing slash commands between Claude Code and Gemini CLI

A transpiler converts between Claude Code `.md` commands and Gemini CLI `.toml` commands. The `ai-command-converter` project (github.com/Commands-com/ai-command-converter) implements this bidirectionally.

**Conversion logic:**
```
Claude .md:                    Gemini .toml:
---                            description = "..."
description: "..."      →
---                            prompt = """
{{ARGUMENTS}}                  {{args}}
!{git diff}              →     !{git diff}
@include file.md         →     @{file.md}
```

**Limitations:**
- `{{param_name}}` → `{{args}}` loses parameter typing (Gemini only has one catch-all arg)
- Complex multi-param commands require restructuring prompt text
- Codex CLI cannot receive custom commands (feature not implemented yet)

### Architecture 5: Universal Plugin Manifest (Intermediate Format)

**Best for:** Long-term multi-tool plugin distribution

Define a universal manifest that a build tool compiles into each target format:

```yaml
# plugin-manifest.yaml (proposed intermediate format)
name: my-plugin
version: 1.0.0

context:
  - path: CLAUDE.md           # Will be copied to GEMINI.md and AGENTS.md

skills:
  - path: skills/my-skill/   # Copied to .agents/skills/ (universal)

commands:
  - name: my-command
    description: "..."
    prompt: "..."
    args: [{ name: "target", type: "string" }]
    # Compiled to: .md (Claude Code), .toml (Gemini CLI), skipped (Codex)

agents:
  - path: agents/my-agent.md
    # Compiled to: Claude Code agent, Gemini extension GEMINI.md, Codex AGENTS.override.md

mcp_servers:
  - name: my-tools
    command: "node"
    args: ["./server.js"]
    # Injected into: mcp.json (Claude), settings.json (Gemini), config.toml (Codex)
```

**No production tool implements this today.** The `cc-switch-cli` project comes closest (Rust CLI managing Claude Code, Codex, Gemini configs + MCP sync + skill extensions), but it manages configs rather than compiling from a universal format.

### Architecture 6: Hybrid Approach (Recommended for Arkhe Plugins)

Combine the above strategies based on component type:

| Component | Strategy | Effort |
|---|---|---|
| Skills (SKILL.md) | Use `.agents/skills/` universal path | Minimal — just move files |
| Context/Instructions | Configure fallback filenames in each tool, or maintain parallel files | Low |
| MCP Servers | Single server definition, inject config per tool format | Low |
| Agents | Convert system prompt to GEMINI.md/AGENTS.md per tool | Medium |
| Commands | Maintain two formats (.md + .toml), use ai-command-converter | Medium |
| Hooks | No equivalent in Codex/Claude Code (different hook systems) | N/A |

---

## Trade-offs and Limitations

### What Works Today (March 2026)

1. **SKILL.md**: True cross-platform portability. Write once, run on 40+ tools. The `allowed-tools` field is the only compatibility gap (Claude Code honors it; others mostly ignore it).

2. **MCP Servers**: Universal tool connectivity. Codex CLI's STDIO-only constraint is the main friction point. Remote MCP servers (HTTP/SSE) only work on Claude Code and Gemini CLI.

3. **Context files (GEMINI.md / AGENTS.md / CLAUDE.md)**: Partially portable via filename aliasing config. Gemini CLI and Codex CLI both support configuring alternative context filenames, enabling them to read CLAUDE.md without renaming.

### What Requires Conversion

1. **Commands**: Claude Code `.md` ↔ Gemini CLI `.toml` conversion exists (ai-command-converter). Codex CLI has no custom command support yet.

2. **Agents**: No universal format. Must manually adapt system prompt to each tool's context mechanism (GEMINI.md for Gemini, AGENTS.md for Codex).

3. **Hook systems**: Claude Code (PostToolUse, PreToolUse), Gemini CLI (10-event hook system), and Codex CLI (no hook system) are incompatible. Cannot share hooks.

### Key Gaps (March 2026)

| Feature | Claude Code | Gemini CLI | Codex CLI |
|---|---|---|---|
| Custom slash commands | Yes | Yes (TOML) | No (built-ins only) |
| Sub-agent spawning | Yes (full) | Via extensions (limited) | Experimental |
| Hook/lifecycle events | Yes | Yes (10 events) | No |
| Remote MCP (HTTP/SSE) | Yes | Yes | No |
| Skills | Yes (native) | Yes (native) | Experimental (opt-in) |
| Context file aliasing | No (only CLAUDE.md) | Yes (configurable) | Yes (configurable) |
| Extension system | Plugins (marketplace) | Extensions (gemini-extension.json) | No equivalent |

### Codex CLI Trajectory

The Codex GitHub repository shows active development toward greater compatibility:
- Open issue #11701 requests SKILL.md-style sub-agent definitions in `agents_config.toml`
- Open issue #5419 requests custom slash commands
- Open issue #9550 requests per-session MCP server scoping
- Codex adopted SKILL.md support in December 2025 (experimental)

### Gemini CLI Agent Skills Adoption

Gemini CLI officially adopted the Agent Skills (SKILL.md) open standard in its extension system (documented in `writing-extensions.md`). The standard's documentation is on Gemini CLI's official docs site. Skills bundled in Gemini extensions use the same `SKILL.md` format as Claude Code skills.

---

## References

- **Skills standard**: skills.sh (Vercel Labs, 8K stars, 80+ contributors, Jan 2026)
- **Gemini CLI extensions**: google.dev/blog (Oct 2025), geminicli.com/docs
- **Gemini CLI hooks**: geminicli.com/docs/hooks (Jan 2026)
- **Codex CLI AGENTS.md**: developers.openai.com/codex/guides/agents-md
- **Codex CLI config**: developers.openai.com/codex/config-advanced
- **MCP donation to Linux Foundation**: December 2025, Agentic AI Foundation
- **OSSA spec**: openstandardagents.org/specification (v0.4.0, Feb 2026)
- **AI Command Converter**: github.com/Commands-com/ai-command-converter
- **CC-Switch CLI**: github.com/thomas-jack/cc-switch-cli (unified Gemini/Claude/Codex manager)
- **Protocol wars analysis**: hungyichen.com (MCP vs A2A vs WebMCP, Feb 2026)
<!-- AUTO-GENERATED: End -->

<!-- TEAM-NOTES: Start -->
## Team Context

_Add project-specific notes, implementation references, and team knowledge here._

<!-- TEAM-NOTES: End -->
