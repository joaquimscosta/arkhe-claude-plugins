# core

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Gemini equivalents. Install the `core` extension if you have not already.

@../../plugins/core/skills/using-arkhe-skills/SKILL.md

## Skills

- **deep-research** — Deep research on technical topics using EXA tools with intelligent two-tier caching. Use when user asks to research a topic, investigate best practices, look up information, find patterns, or explore architectures. Also invoked by /research command. Triggers: "research", "look up", "investigate", "deep dive", "find information about", "what are best practices for", "how do others implement".
- **sdlc-develop** — Orchestrates 6-phase SDLC pipeline (discovery, requirements, architecture, workstreams, implementation, summary) for guided feature development. Use when user runs /core:develop command, requests spec-driven development, wants to create implementation plans with architecture decisions, or mentions "SDLC", "spec-driven", "plan feature", "development pipeline". Supports plan persistence, wave-based resume, autonomous mode, and architecture/implementation verification.
- **using-arkhe-skills** — Use when starting any conversation - establishes how arkhe skills bootstrap on Claude Code, Gemini CLI, and Codex CLI, and maps Claude-only tools (AskUserQuestion, TaskCreate, EnterPlanMode, the Skill tool, the Agent tool) to their cross-platform equivalents
- **workflow-orchestration** — Coordinate structured thinking and multi-agent parallel execution for complex tasks. Use when tackling multi-step projects, planning parallel work, breaking down complex problems, coordinating specialist tasks, facing architectural decisions, or when user mentions "workflow", "orchestration", "multi-step", "coordinate", "parallel execution", "structured thinking", "break this down", "plan this out", "how should I approach", or needs help planning complex implementations.

## Commands

See `commands/` directory for transpiled Gemini TOML commands.
