---
name: using-arkhe-skills
description: Use when starting any conversation - establishes how arkhe skills bootstrap on Claude Code, Gemini CLI, and Codex CLI, and maps Claude-only tools (AskUserQuestion, TaskCreate, EnterPlanMode, the Skill tool, the Agent tool) to their cross-platform equivalents
---

<SUBAGENT-STOP>
If dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# Using arkhe Skills Across Platforms

arkhe plugins ship the same `SKILL.md` files to three CLI harnesses. This bootstrap establishes how to access skills and how to translate Claude-only tool names into the equivalent operation on Gemini CLI and Codex CLI.

## How to Access Skills

- **Claude Code:** Use the `Skill` tool. When invoked, the skill content is loaded and presented to follow directly.
- **Gemini CLI:** Skill metadata (name + description) is auto-loaded into the system prompt at session start. When triggers fire, use `read_file` to load `skills/<skill-name>/SKILL.md` from the extension directory, then follow its instructions. (Gemini 0.40.x advertises an `activate_skill` tool but the runtime currently rejects calls to it; `read_file` is the reliable mechanism.)
- **Codex CLI:** Skill index and trigger phrases are inlined in `AGENTS.md` at install time. Follow the skill body directly when a trigger phrase fires.

## Platform Tool Mapping

arkhe SKILL.md files reference five Claude-specific primitives. On Gemini and Codex, substitute the equivalent operation from this table.

| Claude tool | Gemini CLI equivalent | Codex CLI equivalent |
|---|---|---|
| `AskUserQuestion` | Ask a plain-text question with numbered choices and await reply. No structured chip UI. | Plain-text question with numbered choices. Same fallback. |
| `TaskCreate` / `TaskUpdate` | Maintain an inline TODO list in the assistant message; re-render the list on each turn to mark progress. | Inline TODO list rendered on each turn. |
| `EnterPlanMode` / `ExitPlanMode` | Announce "entering plan mode", refrain from filesystem writes, and require explicit user approval before executing. | Same — announce plan mode and gate writes on approval. |
| Skill tool (`Skill`) | Use `read_file` on `skills/<name>/SKILL.md` (skill metadata is auto-loaded into the system prompt at session start). | Skill content is already inlined in `AGENTS.md`; follow it directly. |
| Agent tool with `subagent_type` | No native equivalent. Inline the agent's system prompt into the current session and proceed sequentially. Loses parallelism. | Same — agent prompt is pre-inlined in the affected commands; run inline. |

## Command Naming Across Platforms

Commands ship from the same `plugins/<plugin>/commands/<name>.md` source on every platform, but the slash-command syntax differs:

| Platform | Form | Example |
|---|---|---|
| Claude Code | `/<plugin>:<command>` (plugin-namespaced) | `/core:think` |
| Gemini CLI | `/<command>` (no extension prefix) | `/think` |
| Codex CLI | Trigger phrase in chat (no slash) | "think through whether to use Postgres or Redis" |

When this skill or other arkhe docs refer to `core:think`, `core:debug`, etc., resolve them through this table — same command, platform-specific invocation.

## Subagent-Heavy Commands

Six arkhe commands dispatch subagents on Claude Code. On Gemini and Codex they run inline with the agent's prompt collapsed into the command body. Behavior is functionally equivalent for single-pass workflows but loses parallel sub-execution.

The affected commands:

- `core:debug` (with `--deep`)
- `core:think`
- `core:research`
- `core:double-check` (with `--deep`)
- `spring-boot:spring-review`
- `spring-boot:verify-upgrade`

## Instruction Priority

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **arkhe skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If `CLAUDE.md`, `GEMINI.md`, or `AGENTS.md` says "do not use TDD" and a skill says "always use TDD," follow the user's instructions. The user is in control.

## Where Skills Live

- **Canonical source:** `plugins/<plugin>/skills/<skill>/SKILL.md`
- **Claude Code:** loaded via `.claude-plugin/marketplace.json`
- **Gemini CLI:** loaded via `.gemini-extensions/<plugin>/gemini-extension.json` (skills directory is a symlink to the canonical source)
- **Codex CLI:** loaded via `.codex-marketplace/<plugin>/AGENTS.md` (skill index synthesized at build time; full content via symlinked `skills/`)

Skill bodies are not duplicated across platforms. One file, three harnesses.
