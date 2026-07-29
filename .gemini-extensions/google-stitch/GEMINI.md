# google-stitch

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Gemini equivalents. Install the `core` extension if you have not already.

@../../plugins/core/skills/using-arkhe-skills/SKILL.md

## Skills

- **authoring-stitch-prompts** — Converts natural-language descriptions or UI spec files into optimized Google Stitch prompts. Use when creating, refining, or validating design directives for Google Stitch. Use when user says "create a Stitch prompt", "optimize this for Stitch", "convert this spec to a Stitch prompt", "write a UI prompt", or mentions Google Stitch prompt authoring. Follows Stitch best practices with short, directive prompts focused on screens, structure, and visual hierarchy.
- **generating-stitch-screens** — Generates Stitch screens from authored prompt files using MCP tools. Reads prompt sections, sends each to Stitch for generation, and fetches resulting images and code. Use when user mentions "generate in stitch", "create stitch screens", "run prompts in stitch", "send prompts to stitch", "generate screens from prompts", "fetch stitch images", or has prompt-v*.md files ready for generation. Requires Stitch MCP server.

## Commands

See `commands/` directory for transpiled Gemini TOML commands.
