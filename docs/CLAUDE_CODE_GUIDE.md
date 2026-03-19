# The Complete Guide to Claude Code V4

> **Source**: [The Complete Guide to Claude Code V4](https://thedecipherist.com/articles/claude-code-guide-v4/) by Tim Carter Clausen (published 2026-01-25)
>
> **Curated**: 2026-03-19 — This is a custom document (not auto-synced). Content has been organized and cross-referenced with existing project documentation.
>
> This guide has been substantially updated beyond the original article to reflect Claude Code V4.6 features and current official documentation.

This guide covers Claude Code configuration, extensibility, and V4-specific features across 13 topics. It serves as a practitioner-oriented companion to the official reference docs already synced in this repository.

**Existing reference docs** (for deep dives into specific topics):
[SETTINGS.md](./reference/SETTINGS.md) | [MCP.md](./reference/MCP.md) | [SKILLS.md](./reference/SKILLS.md) | [HOOKS.md](./reference/HOOKS.md) | [SUBAGENTS.md](./reference/SUBAGENTS.md) | [BEST_PRACTICES.md](./reference/BEST_PRACTICES.md)

---

## Table of Contents

**Foundation**

1. [Global CLAUDE.md as Security Gatekeeper](#1-global-claudemd-as-security-gatekeeper)
2. [Global Rules for New Project Scaffolding](#2-global-rules-for-new-project-scaffolding)
3. [MCP Servers](#3-mcp-servers)
4. [Commands](#4-commands)
5. [Skills](#5-skills)
6. [Single-Purpose Chats](#6-single-purpose-chats)
7. [Hooks](#7-hooks)
8. [LSP](#8-lsp)

**V4 Features**

9. [MCP Tool Search](#9-mcp-tool-search)
10. [Custom Agents](#10-custom-agents)
11. [Session Teleportation](#11-session-teleportation)
12. [Background Tasks](#12-background-tasks)
13. [New Commands & Shortcuts](#13-new-commands--shortcuts)

**Reference**

- [Quick Reference](#quick-reference)
- [Related Documentation](#related-documentation)

---

## Foundation

### 1. Global CLAUDE.md as Security Gatekeeper

The global `~/.claude/CLAUDE.md` file sits at the top of a three-level memory hierarchy and serves as the primary security gatekeeper across all projects.

#### Memory Hierarchy

| Level | Location | Purpose |
|-------|----------|---------|
| Enterprise | `/etc/claude-code/CLAUDE.md` | Org-wide policies |
| Global User | `~/.claude/CLAUDE.md` | Standards for ALL projects |
| Project | `./CLAUDE.md` | Team-shared instructions |

> **Official Reference**: For the complete settings specification, see [SETTINGS.md](./reference/SETTINGS.md).

#### Security Rules

Every global CLAUDE.md should include explicit "never" rules:

```markdown
## NEVER EVER DO

### NEVER Publish Sensitive Data
- NEVER publish passwords, API keys, tokens to git/npm/docker
- Before ANY commit: verify no secrets included

### NEVER Commit .env Files
- NEVER commit .env to git
- ALWAYS verify .env is in .gitignore
```

#### Why This Matters

Security researchers discovered that Claude Code automatically reads `.env` files without explicit permission. Backslash Security warns:

> "If not restricted, Claude can read .env, AWS credentials, or secrets.json and leak them through helpful suggestions."

#### Defense in Depth

| Layer | What | How |
|-------|------|-----|
| 1 | Behavioral rules | Global CLAUDE.md "NEVER" rules |
| 2 | Access control | Deny list in `settings.json` |
| 3 | Git safety | `.gitignore` |

#### Team Workflow

When a team member makes a mistake, add it as a rule to CLAUDE.md. Over time, this file becomes an evolving set of guardrails that prevent repeated issues.

#### Cross-Machine Sync with GNU Stow

```bash
# Using GNU Stow to sync across machines
cd ~/dotfiles
stow claude  # Symlinks ~/.claude to dotfiles/claude/.claude
```

#### Account Configuration

Include account identifiers to avoid misconfiguration:

```markdown
## GitHub Account
ALWAYS use YourUsername for all projects:
- SSH: git@github.com:YourUsername/<repo>.git

## Docker Hub
Already authenticated. Username in ~/.env as DOCKER_HUB_USER
```

---

### 2. Global Rules for New Project Scaffolding

Use the global CLAUDE.md to define scaffolding rules that every new project must follow.

#### Required Files

```
.env            - Environment variables (NEVER commit)
.env.example    - Template with placeholders
.gitignore      - Must include: .env, node_modules/, dist/
CLAUDE.md       - Project overview
```

#### Required Directory Structure

```
project/
├── src/
├── tests/
├── docs/
├── .claude/
│   ├── skills/
│   ├── agents/
│   └── commands/
└── scripts/
```

#### Node.js Requirement

Always include unhandled rejection handling:

```javascript
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
  process.exit(1);
});
```

---

### 3. MCP Servers

MCP (Model Context Protocol) servers give Claude access to external tools and services.

#### Basic Commands

```bash
claude mcp add <server-name> -- <command>
claude mcp list
claude mcp remove <server-name>
```

> **Official Reference**: For the complete MCP specification, see [MCP.md](./reference/MCP.md).

#### When NOT to Use MCP

| Use Case | MCP Overhead | Alternative |
|----------|-------------|-------------|
| Trello tasks | High | CLI tool (`trello-cli`) |
| Simple HTTP calls | Overkill | `curl` via Bash |
| One-off queries | Wasteful | Direct command |

#### Recommended Servers

**Core Development**

| Server | Purpose | Install |
|--------|---------|---------|
| Context7 | Live docs for any library | `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` |
| GitHub | PRs, issues, CI/CD | `claude mcp add github -- npx -y @modelcontextprotocol/server-github` |
| Filesystem | Advanced file operations | `claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem` |
| Sequential Thinking | Structured problem-solving | `claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking` |

**Databases**

| Server | Purpose | Install |
|--------|---------|---------|
| MongoDB | Atlas/Community, Performance Advisor | `claude mcp add mongodb -- npx -y mongodb-mcp-server` |
| PostgreSQL | Query Postgres naturally | `claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres` |
| DBHub | Universal (MySQL, SQLite, etc.) | `claude mcp add db -- npx -y @bytebase/dbhub` |

**Documents & RAG**

| Server | Purpose | Install |
|--------|---------|---------|
| Docling | PDF/DOCX parsing, 97.9% table accuracy | `claude mcp add docling -- uvx docling-mcp-server` |
| Qdrant | Vector search, semantic memory | `claude mcp add qdrant -- npx -y @qdrant/mcp-server` |
| Chroma | Embeddings, vector DB | `claude mcp add chroma -- npx -y @chroma/mcp-server` |

**Browser & Testing**

| Server | Purpose | Install |
|--------|---------|---------|
| Playwright | E2E testing, scraping | `claude mcp add playwright -- npx -y @anthropic-ai/playwright-mcp` |
| Browser MCP | Use your logged-in Chrome | browsermcp.io |

**Cloud & DevOps**

| Server | Purpose | Install |
|--------|---------|---------|
| AWS | S3, Lambda, CloudWatch | `claude mcp add aws -- npx -y @anthropic-ai/aws-mcp` |
| Docker | Container management | `claude mcp add docker -- npx -y @anthropic-ai/docker-mcp` |
| Kubernetes | Cluster operations | `claude mcp add k8s -- npx -y @anthropic-ai/kubernetes-mcp` |

---

### 4. Commands

Commands are personal shortcuts — slash commands that expand to full prompts.

> **Note**: Custom commands have been merged into skills. Files in `.claude/commands/` still work, but skills (`.claude/skills/`) are now recommended as they support additional features like supporting files and invocation control. See [Section 5: Skills](#5-skills).

> **Official Reference**: For the complete commands specification, see [PLUGINS_REFERENCE.md](./reference/PLUGINS_REFERENCE.md).

#### Basic Command

`~/.claude/commands/review.md`:

```markdown
---
description: Review code for issues
---

Review this code for:
1. Security vulnerabilities
2. Performance issues
3. Error handling gaps
4. Code style violations
```

#### Command with Arguments

`~/.claude/commands/ticket.md`:

```markdown
---
description: Create a ticket from description
argument-hint: <ticket-description>
---

Create a detailed ticket for: $ARGUMENTS

Include:
- User story
- Acceptance criteria
- Technical notes
```

#### Advanced: Bash Execution with `!` Backtick Syntax

`~/.claude/commands/smart-commit.md`:

```markdown
---
description: Smart commit with context
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [message]
---

## Context
- Current git status: !`git status`
- Current git diff: !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`

## Task
Create a commit with message: $ARGUMENTS
```

The `!` backtick syntax executes shell commands inline when the command loads, injecting their output as context.

#### Additional Frontmatter Fields

Commands support the same frontmatter as skills: `allowed-tools`, `model`, `disable-model-invocation`. See [Skills Frontmatter Reference](#frontmatter-reference) for details.

---

### 5. Skills

Skills extend what Claude can do. Create a `SKILL.md` file with instructions, and Claude adds it to its toolkit. Claude uses skills when relevant, or you can invoke one directly with `/skill-name`.

> **Official Reference**: For the complete skills specification, see [SKILLS.md](./reference/SKILLS.md) and [SKILL_DEVELOPMENT_BEST_PRACTICES.md](./SKILL_DEVELOPMENT_BEST_PRACTICES.md).

#### Bundled Skills

Bundled skills ship with Claude Code and are available in every session. They are prompt-based: they give Claude a detailed playbook and let it orchestrate the work using its tools.

| Skill | Purpose |
|-------|---------|
| `/batch <instruction>` | Orchestrate large-scale changes in parallel. Decomposes into 5-30 units, spawns one agent per unit in isolated git worktrees, each opens a PR |
| `/claude-api` | Load Claude API reference material. Auto-activates when code imports `anthropic` or `@anthropic-ai/sdk` |
| `/debug [description]` | Troubleshoot current session by reading debug logs with optional issue focus |
| `/loop [interval] <prompt>` | Run a prompt repeatedly on an interval. Example: `/loop 5m check if the deploy finished` |
| `/simplify [focus]` | Review recently changed files for code reuse, quality, and efficiency. Spawns three parallel review agents |

#### Skill Creation Example

`.claude/skills/code-review/SKILL.md`:

```markdown
---
name: code-review
description: Comprehensive code review with security focus. Use when reviewing code, auditing for vulnerabilities, or checking code quality.
---

When reviewing code:
1. Check for security vulnerabilities (OWASP Top 10)
2. Look for performance issues (N+1 queries, memory leaks)
3. Verify error handling (edge cases, null checks)
4. Assess test coverage
5. Review naming and documentation
```

#### Frontmatter Reference

All fields are optional. Only `description` is recommended so Claude knows when to use the skill.

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name (max 64 chars). Defaults to directory name |
| `description` | Recommended | What the skill does and when to use it. Claude uses this for auto-invocation |
| `argument-hint` | No | Hint shown during autocomplete (e.g., `[issue-number]`) |
| `disable-model-invocation` | No | `true` to prevent Claude from auto-loading. Use for manual-only workflows |
| `user-invocable` | No | `false` to hide from `/` menu. Use for background knowledge |
| `allowed-tools` | No | Tools Claude can use without asking permission when skill is active |
| `model` | No | Model override for this skill |
| `context` | No | `fork` to run in an isolated subagent context |
| `agent` | No | Which subagent type to use when `context: fork` is set |
| `hooks` | No | Lifecycle hooks scoped to this skill |

#### String Substitutions

Skills support dynamic values in their content:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Access argument by 0-based index (e.g., `$ARGUMENTS[0]`) |
| `$N` | Shorthand for `$ARGUMENTS[N]` (e.g., `$0`, `$1`) |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing the skill's SKILL.md file |

#### Where Skills Live

| Location | Path | Applies To |
|----------|------|------------|
| Enterprise | See [managed settings](./reference/SETTINGS.md) | All users in organization |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where plugin is enabled |

When skills share the same name, higher-priority locations win: enterprise > personal > project.

#### Progressive Disclosure (3 Stages)

| Stage | When | Token Cost |
|-------|------|------------|
| Startup | Always | ~50 tokens (name + description only) |
| Triggered | Skill matches context | Full SKILL.md content |
| As needed | Deep dive required | Additional resources (WORKFLOW.md, etc.) |

#### Automatic Discovery

Skills are automatically discovered from nested `.claude/skills/` directories — no registration step needed. This includes subdirectories: if you're editing files in `packages/frontend/`, Claude Code also discovers skills in `packages/frontend/.claude/skills/`. This supports monorepo setups where packages have their own skills.

#### Rule of Thumb

If less than ~20% of conversations need a particular capability, make it a skill rather than embedding it in CLAUDE.md. This keeps the base context lean.

---

### 6. Single-Purpose Chats

Research shows that context management directly impacts Claude's performance.

> **Official Reference**: For context engineering best practices, see [BEST_PRACTICES.md](./reference/BEST_PRACTICES.md).

#### Research Findings

- **39% performance drop** when instructions are delivered across multiple turns (multi-turn conversation study)
- **Chroma Research**: "As tokens in context window increase, model's ability to accurately recall information decreases"

#### The Golden Rule

```
One Task, One Chat
```

#### When to Use `/clear`

| Scenario | Action |
|----------|--------|
| New feature | New chat |
| Bug fix (unrelated) | `/clear` then new task |
| Research vs implementation | Separate chats |
| 20+ turns elapsed | Start fresh |

#### V4: `/context` Command

Inspect exactly where your tokens are going:

```bash
/context
```

Shows `context_window.used_percentage` and `context_window.remaining_percentage` — lets you make informed decisions about when to start fresh.

---

### 7. Hooks

Hooks are user-defined shell commands, HTTP endpoints, or LLM prompts that execute automatically at specific points in Claude Code's lifecycle.

> **Official Reference**: For the complete hooks specification, see [HOOKS.md](./reference/HOOKS.md).

#### CLAUDE.md vs Hooks

| Mechanism | Type | Reliability |
|-----------|------|-------------|
| CLAUDE.md rules | Suggestion | Can be overridden |
| Hooks | Enforcement | Always executes |

#### Hook Types

| Type | Description |
|------|-------------|
| **Command** | Shell commands that receive JSON on stdin |
| **HTTP** | POST to a URL endpoint (alternative to command hooks) |
| **Prompt** | LLM-based hooks that use Claude to evaluate conditions |

#### Hook Events (21 Events)

| Category | Event | When It Fires |
|----------|-------|---------------|
| Session | `SessionStart` | Session begins or resumes |
| Session | `SessionEnd` | Session terminates |
| User Input | `UserPromptSubmit` | User submits a prompt, before processing |
| Tool Execution | `PreToolUse` | Before tool call executes (can block it) |
| Tool Execution | `PostToolUse` | After tool call succeeds |
| Tool Execution | `PostToolUseFailure` | After tool call fails |
| Tool Execution | `PermissionRequest` | When permission dialog appears |
| Subagents | `SubagentStart` | Subagent is spawned |
| Subagents | `SubagentStop` | Subagent finishes |
| Agent Teams | `TeammateIdle` | Agent team teammate about to go idle |
| Tasks | `Stop` | Claude finishes responding |
| Tasks | `TaskCompleted` | Task marked as completed |
| Context | `InstructionsLoaded` | CLAUDE.md or `.claude/rules/*.md` loaded into context |
| Context | `ConfigChange` | Configuration file changes during session |
| Context | `PreCompact` | Before context compaction |
| Context | `PostCompact` | After context compaction completes |
| Worktrees | `WorktreeCreate` | Worktree created via `--worktree` or `isolation: "worktree"` |
| Worktrees | `WorktreeRemove` | Worktree removed at session exit or subagent finish |
| MCP | `Elicitation` | MCP server requests user input during tool call |
| MCP | `ElicitationResult` | User responds to MCP elicitation |
| Notifications | `Notification` | Claude Code sends a notification |

#### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (JSON output is processed if present) |
| 2 | Blocking error (stderr fed back to Claude) |
| Any other | Non-blocking error (shown to user) |

Command hooks can return structured JSON output with `hookSpecificOutput` for richer control (e.g., `permissionDecision: "deny"` in PreToolUse). See [HOOKS.md](./reference/HOOKS.md) for the full JSON schema.

#### Example: Block Secrets Hook

**`settings.json` configuration:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "python3 ~/.claude/hooks/block-secrets.py"
        }]
      }
    ]
  }
}
```

**`~/.claude/hooks/block-secrets.py`:**

```python
#!/usr/bin/env python3
import json, sys
from pathlib import Path

SENSITIVE = {'.env', '.env.local', 'secrets.json', 'id_rsa'}

data = json.load(sys.stdin)
file_path = data.get('tool_input', {}).get('file_path', '')

if Path(file_path).name in SENSITIVE:
    print(f"BLOCKED: Access to {file_path} denied.", file=sys.stderr)
    sys.exit(2)  # Exit 2 = block and feed stderr to Claude

sys.exit(0)
```

#### Setup Hook Event

The Setup hook runs during session initialization with `--init`, `--init-only`, or `--maintenance` flags:

```json
{
  "hooks": {
    "Setup": [{
      "type": "command",
      "command": "npm install && npm run prepare"
    }]
  }
}
```

```bash
claude --init          # Triggers Setup hook
claude --init-only     # Triggers Setup hook, then exits
claude --maintenance   # Triggers Setup hook for maintenance
```

#### Managing Hooks

The `/hooks` command opens a read-only browser of all configured hooks. To create or edit hooks, modify `settings.json` directly or use the settings UI.

---

### 8. LSP

Language Server Protocol integration gives Claude IDE-level code intelligence.

#### Capabilities

| Capability | What It Does |
|------------|-------------|
| Go to Definition | Jump to where a symbol is defined |
| Find References | See everywhere a function is used |
| Hover | Get type signatures and docs |
| Diagnostics | Real-time error detection |
| Document Symbols | List all symbols in a file |

#### Performance

**900x faster** — 50ms vs 45 seconds for cross-codebase navigation.

#### Supported Languages

Python, TypeScript, Go, Rust, Java, C/C++, C#, PHP, Kotlin, Ruby, HTML/CSS

#### Availability

Built-in since **v2.0.74** (December 2025). For older versions:

```bash
export ENABLE_LSP_TOOL=1
```

---

## V4 Features

### 9. MCP Tool Search

MCP Tool Search is the headline V4 feature — an 85% reduction in initial context consumption through lazy tool loading.

> **Official Reference**: For the complete MCP specification, see [MCP.md](./reference/MCP.md).

#### The Problem

Before Tool Search, all MCP tool descriptions were loaded at startup:

```
Loading 73 MCP tools... [39.8k tokens]
Loading 56 agents... [9.7k tokens]
Loading system tools... [22.6k tokens]
Ready with 92k tokens remaining.  <- 54% context GONE before typing
```

#### The Solution

With Tool Search, Claude loads a lightweight registry and fetches tools on demand:

```
Loading tool registry... [5k tokens]
Ready with 195k tokens available.  <- 95% context preserved

User: "I need to query the database"
> Auto-loading: postgres-mcp [+1.2k tokens]
> 193.8k tokens remaining
```

#### How It Works

1. **Detection**: Checks if tool descriptions would use >10% of context
2. **Registry Creation**: Builds lightweight index of tool names and descriptions
3. **On-Demand Loading**: Tools load when Claude determines they're needed
4. **Intelligent Caching**: Loaded tools remain available for session duration

#### Performance Statistics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Initial context usage | ~77K tokens | ~8.7K tokens | **85% reduction** |
| Opus 4 accuracy | 49% | 74% | **+25 percentage points** |
| Opus 4.5 accuracy | 79.5% | 88.1% | **+8.6 percentage points** |

#### Configuration

Disable Tool Search for servers that must always be available:

```json
{
  "mcpServers": {
    "always-needed": {
      "command": "...",
      "enable_tool_search": false
    }
  }
}
```

Adjust the activation threshold (default: 10% of context):

```json
{
  "mcp": {
    "tool_search": "auto:15"
  }
}
```

Use `/context` to check current token usage. If you enable or disable a plugin during a session, run `/reload-plugins` to pick up changes without restarting.

---

### 10. Custom Agents

Custom agents (subagents) provide context isolation, focused system prompts, and automatic delegation.

> **Official Reference**: For the complete agents specification, see [SUBAGENTS.md](./reference/SUBAGENTS.md).

#### Why Agents?

| Problem | Solution |
|---------|----------|
| Context pollution from diverse tasks | Each agent has an isolated context window |
| Generic advice for specialized work | Agents have focused system prompts |
| Manual orchestration overhead | Automatic delegation based on task |

#### Method 1: Interactive Creation

```bash
/agents
```

Select "Create new agent" -> Choose location -> Choose model -> Pick a color -> Configure memory -> Save.

#### Method 2: Manual Agent File

`.claude/agents/code-reviewer.md`:

```markdown
---
name: code-reviewer
description: Reviews code for security, performance, and best practices
tools: Read, Grep, Glob
model: sonnet
---

You are a senior code reviewer specializing in:
- Security vulnerabilities (OWASP Top 10)
- Performance antipatterns
- Error handling gaps
- Code maintainability

When reviewing:
1. Start with security concerns
2. Then performance issues
3. Then style/maintainability
4. Provide specific line references
5. Suggest concrete fixes

Be critical but constructive. Explain WHY something is a problem.
```

#### Subagent Scopes

Store subagents in different locations depending on scope. Higher-priority locations win when names conflict.

| Location | Scope | Priority |
|----------|-------|----------|
| `--agents` CLI flag | Current session only | 1 (highest) |
| `.claude/agents/` | Current project | 2 |
| `~/.claude/agents/` | All your projects | 3 |
| Plugin's `agents/` directory | Where plugin is enabled | 4 (lowest) |

CLI-defined subagents are passed as JSON and exist only for that session:

```bash
claude --agents '{"code-reviewer": {"description": "Expert code reviewer", "prompt": "You are a senior code reviewer.", "tools": ["Read", "Grep"], "model": "sonnet"}}'
```

#### Configuration Options

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase letters and hyphens) |
| `description` | Yes | When Claude should delegate to this subagent |
| `tools` | No | Tool allowlist. Inherits all tools if omitted |
| `disallowedTools` | No | Tool denylist, removed from inherited or specified list |
| `model` | No | `sonnet`, `opus`, `haiku`, full model ID (e.g., `claude-opus-4-6`), or `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, or `plan` |
| `maxTurns` | No | Maximum agentic turns before the subagent stops |
| `skills` | No | Skills to preload into context at startup (full content injected) |
| `mcpServers` | No | MCP servers scoped to this subagent (inline definition or name reference) |
| `hooks` | No | Lifecycle hooks scoped to this subagent |
| `memory` | No | Persistent memory scope: `user`, `project`, or `local` |
| `background` | No | `true` to always run as a background task |
| `isolation` | No | `worktree` to run in an isolated git worktree copy |

#### Persistent Memory

The `memory` field gives a subagent a persistent directory that survives across conversations, allowing it to accumulate insights over time (codebase patterns, recurring issues, architectural decisions).

```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. Update your agent memory with patterns and conventions you discover.
```

| Scope | Location | Use When |
|-------|----------|----------|
| `user` | `~/.claude/agent-memory/` | Insights apply across all projects |
| `project` | `.claude/agent-memory/` | Insights are project-specific |
| `local` | `.claude/agent-memory.local/` | Personal project insights (gitignored) |

#### MCP Server Scoping

Use the `mcpServers` field to give a subagent access to MCP servers not available in the main conversation. Inline servers connect when the subagent starts and disconnect when it finishes.

```yaml
---
name: browser-tester
description: Tests features in a real browser using Playwright
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  - github   # references an already-configured server
---
```

#### Automatic Delegation Flow

```
You: "Review the authentication module for security issues"

Claude thinks: "This is a code review task focusing on security"
-> Delegates to code-reviewer agent
-> Agent runs with isolated context
-> Returns findings to main conversation
```

#### Built-in Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| Explore | Haiku | Fast, read-only codebase search and analysis |
| Plan | Inherits | Research agent for plan mode context gathering |
| General-purpose | Inherits | Complex multi-step tasks requiring exploration + modification |
| Bash | Inherits | Running terminal commands in a separate context |
| statusline-setup | Sonnet | Configure custom status line via `/statusline` |
| Claude Code Guide | Haiku | Answer questions about Claude Code features |

#### Agent Teams

For multi-session coordination where multiple agents work in parallel and communicate with each other, see [agent teams](./reference/SUBAGENTS.md). Agent teams coordinate across separate sessions (unlike subagents which work within a single session). Use `@agent-name` syntax to mention and interact with teammates.

#### Best Practices

1. **Keep agents focused** — one specialty per agent
2. **Write clear descriptions** — Claude uses these for routing decisions
3. **Limit tools** — read-only agents shouldn't have Write
4. **Test delegation** — verify Claude routes tasks correctly
5. **Start with 3-4 agents maximum**

---

### 11. Session Teleportation

Move sessions between terminal, web, and other devices seamlessly.

#### Teleport to Web

```bash
/teleport
```

Opens the current session at claude.ai/code. Use cases:
- Switching from terminal to a visual interface
- Sharing a session with collaborators
- Continuing on a different device

#### Configure Remote Environment

```bash
/remote-env
```

Set up environment variables and configuration for remote sessions.

#### Resume Sessions

```bash
# Continue most recent session
claude --continue    # or: claude -c

# Resume specific session by ID
claude --resume abc123    # or: claude -r abc123

# Resume with a new prompt
claude --resume abc123 "Continue with the tests"
```

#### VSCode Remote Session Browsing

OAuth users can browse and resume remote Claude sessions from the Sessions dialog in the VSCode extension.

---

### 12. Background Tasks

Run tasks in the background and continue working in the foreground.

#### Backgrounding

```
Press Ctrl+B to background:
- Currently running agents
- Shell commands
- Both simultaneously (unified in V4)
```

#### Managing Tasks

```bash
/tasks
```

Shows all background tasks with:
- Status indicators
- Inline display of the agent's final response
- Clickable links to full transcripts

#### Notification Behavior

- Capped at 3 lines per notification
- Overflow summary for multiple completions
- Final response visible without opening the full transcript

#### Disable Background Tasks

Via environment variable:

```bash
export CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=true
```

Or in `settings.json`:

```json
{
  "enableBackgroundTasks": false
}
```

---

### 13. New Commands & Shortcuts

V4 introduces several quality-of-life improvements for daily workflows.

#### New Commands

| Command | What It Does |
|---------|-------------|
| `/config` | Search functionality — type to filter settings |
| `/stats` | Press **r** to cycle: Last 7 days, Last 30 days, All time |
| `/doctor` | Shows auto-update channel and available npm versions |
| `/keybindings` | Configure custom keyboard shortcuts |
| `/context` | See exactly where tokens are going |
| `/compact [focus]` | Compact conversation history with optional focus area |
| `/btw` | Side questions that don't enter conversation history |
| `/effort` | Set effort level (low/medium/high) for Opus/Sonnet 4.6+ |
| `/reload-plugins` | Reload plugins without restarting the session |
| `/statusline` | Configure a custom status line display |

#### Custom Keybindings

`~/.claude/keybindings.json`:

```json
{
  "ctrl+shift+r": "/review",
  "ctrl+shift+d": "/deploy",
  "ctrl+shift+t": "/test",
  "ctrl+shift+c": "/commit"
}
```

#### Essential Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel current operation |
| `Ctrl+D` | Exit Claude Code |
| `Ctrl+B` | Background current task |
| `Ctrl+G` | Open plan in text editor for direct editing |
| `Shift+Tab` | In plan mode: auto-accept edits |
| `Esc Esc` | Rewind to previous state (double-tap) |
| `Tab` | Autocomplete commands, files, agents |
| `Shift+Enter` | Insert newline without submitting |
| `Up/Down` | Navigate command history |
| `Ctrl+R` | Reverse search history |

#### Plan Mode Improvements

- **Shift+Tab**: Quickly select "auto-accept edits"
- **Ctrl+G**: Open the plan in your text editor for direct editing before Claude proceeds
- **Reject with feedback**: Tell Claude what to change before rerunning

#### PR Review Indicator

Shows the branch's PR state directly in the prompt:
- Colored dot indicating status (approved, changes requested, pending, draft)
- Clickable link to the PR

#### Language Setting

In `settings.json`:

```json
{
  "language": "ja"
}
```

Or in `CLAUDE.md`:

```markdown
## Language
Always respond in Spanish.
```

#### External CLAUDE.md Imports

Load CLAUDE.md files from additional directories:

```bash
export CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
claude --add-dir ../shared-configs ../team-standards
```

#### VSCode Improvements

- Clickable destination selector for permission requests
- Choose where settings are saved: this project, all projects, shared with team, session only
- Secondary sidebar support (VS Code 1.97+) — Claude in right sidebar, file explorer in left
- Streaming message support — see responses in real-time

#### Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | Disable background task functionality |
| `CLAUDE_CODE_TMPDIR` | Override temp directory location |
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | Enable `--add-dir` CLAUDE.md loading |
| `FORCE_AUTOUPDATE_PLUGINS` | Allow plugin autoupdate when main auto-updater is disabled |
| `IS_DEMO` | Hide email and organization from UI (for streaming/demos) |

---

## Quick Reference

| Tool | Purpose | Location |
|------|---------|----------|
| Global CLAUDE.md | Security + scaffolding | `~/.claude/CLAUDE.md` |
| Project CLAUDE.md | Architecture + team rules | `./CLAUDE.md` |
| MCP Servers | External integrations | `claude mcp add` |
| **MCP Tool Search** | **Lazy loading (85% savings)** | **Automatic when >10% context** |
| Skills | Reusable expertise (10 frontmatter fields) | `.claude/skills/*/SKILL.md` |
| **Bundled Skills** | **`/batch`, `/loop`, `/simplify`, `/debug`, `/claude-api`** | **Built-in** |
| **Custom Agents** | **Automatic delegation (13 config fields)** | `~/.claude/agents/*.md` |
| **Persistent Memory** | **Cross-session agent learning** | `memory:` field in agent frontmatter |
| **Agent Teams** | **Multi-session coordination** | See [SUBAGENTS.md](./reference/SUBAGENTS.md) |
| Commands | Personal shortcuts (merged into skills) | `~/.claude/commands/*.md` |
| Hooks | Deterministic enforcement (20+ events) | `~/.claude/settings.json` |
| LSP | Semantic code intelligence | Built-in (v2.0.74+) |
| **Keybindings** | **Custom shortcuts** | `~/.claude/keybindings.json` |
| `/clear` | Reset context | Type in chat |
| `/context` | View token usage | Type in chat |
| `/teleport` | Move to claude.ai/code | Type in chat |
| `/tasks` | Manage background tasks | Type in chat |
| `/reload-plugins` | Reload plugins without restart | Type in chat |

---

## Related Documentation

### Synced Official Docs (in this repository)

- [SETTINGS.md](./reference/SETTINGS.md) — Claude Code settings and configuration
- [MCP.md](./reference/MCP.md) — Model Context Protocol reference
- [SKILLS.md](./reference/SKILLS.md) — Using Skills in Claude Code
- [HOOKS.md](./reference/HOOKS.md) — Event handling and hooks
- [SUBAGENTS.md](./reference/SUBAGENTS.md) — Agent configuration and usage
- [BEST_PRACTICES.md](./reference/BEST_PRACTICES.md) — Context engineering best practices
- [PLUGINS_REFERENCE.md](./reference/PLUGINS_REFERENCE.md) — Plugins reference

### Custom Docs (in this repository)

- [SKILL_DEVELOPMENT_BEST_PRACTICES.md](./SKILL_DEVELOPMENT_BEST_PRACTICES.md) — Practical skill authoring guide
- [README.md](./README.md) — Developer documentation index

### External Resources

- [The Complete Guide to Claude Code V4](https://thedecipherist.com/articles/claude-code-guide-v4/) — Original source article
- [claude-code-mastery (GitHub)](https://github.com/TheDecipherist/claude-code-mastery) — Templates, hooks, agents, and keybindings from the article author

> **Note**: The external article and repository reflect V4 features. This guide has been updated to cover V4.6 and later.
