# ralph

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Gemini equivalents. Install the `core` extension if you have not already.

@../../plugins/core/skills/using-arkhe-skills/SKILL.md

## Skills

- **ralph-loop** — Execute an autonomous development loop that picks one task per iteration, implements it, verifies it, and commits the result — each iteration in a fresh context window. Use when user runs /ralph, mentions "ralph loop", "autonomous loop", "builder verifier", "run tasks automatically", "iterate on tasks", "develop autonomously", or wants an automated build-verify-commit cycle with task tracking.
- **ralph-prd** — Create Product Requirements Document (PRD) and setup for Ralph autonomous loop. Use when user runs /create-prd command, wants to set up a project for Ralph, mentions "ralph setup", "create prd", "product requirements", or needs to generate tasks for autonomous development.

## Commands

See `commands/` directory for transpiled Gemini TOML commands.
