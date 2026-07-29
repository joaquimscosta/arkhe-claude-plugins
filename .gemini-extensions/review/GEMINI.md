# review

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Gemini equivalents. Install the `core` extension if you have not already.

@../../plugins/core/skills/using-arkhe-skills/SKILL.md

## Skills

- **code-review** — Multi-agent code review using the Pragmatic Quality framework. Orchestrates parallel review agents (CLAUDE.md compliance, bug scanning, git history, security) with independent confidence scoring to produce high-signal findings. Use when user runs /code-review, /review:code-review, requests a "code review", "review my changes", "PR review", or mentions "review diff", "review branch".
- **design-review** — Comprehensive UI/UX design review with live environment testing, responsive validation, accessibility compliance (WCAG 2.1 AA), and visual consistency analysis using Playwright. Use when user runs /design-review, /review:design-review, requests a "design review", "UI review", "UX audit", or mentions "review the design", "check accessibility", "responsive testing".
- **security-review** — Security-focused code review identifying high-confidence exploitable vulnerabilities with two-axis severity/confidence scoring, OWASP 2025 alignment, per-finding Haiku verification, and false positive filtering. Optional GitHub PR posting. Use when user runs /security-review, /review:security-review, requests a "security review", "security audit", "vulnerability scan", or mentions "find vulnerabilities", "check for exploits".
- **verify-findings** — Verify code-review or security-review findings for false positives using deep codebase tracing, framework-aware analysis, and web research. Produces a .verified.md report alongside the original. Use when a review report has been generated and needs independent verification, or when user runs /verify-findings, mentions "verify review", "check false positives", or "validate findings".

## Commands

See `commands/` directory for transpiled Gemini TOML commands.
