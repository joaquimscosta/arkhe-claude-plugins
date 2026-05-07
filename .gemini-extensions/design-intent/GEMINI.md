# design-intent

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Gemini equivalents. Install the `core` extension if you have not already.

@../../plugins/core/skills/using-arkhe-skills/SKILL.md

## Skills

- **design-intent-specialist** — Creates accurate frontend implementations from visual references while maintaining design consistency. Use when user provides Figma URLs, screenshots, design images, requests visual implementation from reference, or asks to build UI matching a design. Automatically checks existing design intent patterns before implementation.
- **icon-forge** — Generate brand icons as SVG and produce all platform assets including favicon package (ICO, SVG with dark mode, apple-touch-icon), PWA manifest icons, and mobile app icons. Use when user runs /icon-forge, requests "brand icon", "favicon generation", "app icon", or "svg logo" for a project.
- **prototype** — Rapid UI prototyping — generates 3 visually distinct HTML/CSS components from a text prompt, each driven by a unique physical/material metaphor. Use when user runs /prototype, asks to "prototype a UI", "mock up a component", "generate HTML mockups", "create UI variations", "design exploration", "quick UI concept", or wants to see multiple visual approaches to a component. Also trigger when user says "show me different ways to build...", "explore different designs for...", or wants rapid visual exploration of a UI idea — even without saying "prototype" explicitly.
- **stitch-to-react** — Converts Google Stitch exports into React components with design DNA integration. Use when user references design-intent/google-stitch exports, mentions "convert Stitch output", "Stitch to React", or processes Stitch code directories containing HTML + PNG pairs.

## Commands

See `commands/` directory for transpiled Gemini TOML commands.
