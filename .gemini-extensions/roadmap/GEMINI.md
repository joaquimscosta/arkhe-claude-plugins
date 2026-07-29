# roadmap

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Gemini equivalents. Install the `core` extension if you have not already.

@../../plugins/core/skills/using-arkhe-skills/SKILL.md

## Skills

- **architect** — Analyze system architecture, module structure, API contracts, data models, and code patterns. Use when designing systems, reviewing module boundaries, evaluating API designs, analyzing data models, checking pattern conformance, tracing decisions, or reviewing frontend architecture. Triggers: "architecture", "module design", "API design", "data model", "boundaries", "patterns", "decisions", "frontend architecture".
- **pm** — Analyze features from user perspective and write user stories with acceptance criteria. Use when defining requirements, writing user stories, validating scope against project state, prioritizing features by impact, comparing approaches, analyzing user needs, or planning next work. Triggers: "user story", "acceptance criteria", "scope", "prioritize", "compare requirements", "user needs", "what to build next".
- **refresh** — Detect drift in .arkhe/roadmap/ context files and regenerate them from the current codebase state. Scaffolds context directory if missing. Use when user runs /roadmap:refresh, mentions "refresh context", "update context", "init roadmap", "stale context", or "scaffold roadmap".
- **roadmap** — Synthesize project documentation and codebase into comprehensive roadmap status, gaps analysis, and blockers. Use when assessing project health, identifying blockers, tracking progress, comparing plan vs reality, documenting risks, or planning next milestones. Triggers: "roadmap", "project status", "blockers", "risks", "progress", "next milestone", "gaps", "what's done".

## Commands

See `commands/` directory for transpiled Gemini TOML commands.
