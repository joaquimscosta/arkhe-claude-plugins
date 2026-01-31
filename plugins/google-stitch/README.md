# Google Stitch Plugin

> Claude + Google Stitch workflow toolkit with MCP integration for prompt authoring, screen generation, and design extraction.

---

## Overview

The Google Stitch plugin provides prompt authoring skills, slash commands, and optional MCP-powered automation for generating UI designs in Google Stitch.

**Architecture: Progressive Enhancement** — MCP-aware but works fully without MCP. The same prompt authoring quality is available regardless of MCP configuration.

| Component | Type | Purpose |
| --- | --- | --- |
| `/prompt` | Command | Interactive prompt authoring with optional MCP generation |
| `/stitch-generate` | Command | Full pipeline: author -> generate -> fetch via MCP |
| `/stitch-setup` | Command | Guided MCP setup and connection verification |
| `authoring-stitch-prompts` | Skill | Converts descriptions into optimized Stitch prompts |
| `generating-stitch-screens` | Skill | Orchestrates MCP-based screen generation |

---

## Prerequisites

- **Claude Code** with plugin support
- **Node.js** (for npx — required for MCP server)
- **Google Cloud account** (for MCP authentication)

MCP is optional. Without it, prompts are authored and saved for manual use in Stitch.

---

## Quick Start

1. **Install the plugin:**
   ```bash
   /plugin marketplace add ./arkhe-claude-plugins
   /plugin install google-stitch@arkhe-claude-plugins
   ```

2. **Author a prompt (works without MCP):**
   ```bash
   /prompt "Design a fintech dashboard with KPI cards and charts"
   ```

3. **Set up MCP for automation (optional):**
   ```bash
   /stitch-setup
   ```

4. **Generate screens via MCP:**
   ```bash
   /stitch-generate "landing page for SaaS product"
   ```

---

## Capability Comparison

| Capability | Without MCP | With MCP |
|------------|-------------|----------|
| Prompt authoring | Full support | Full support |
| Interactive /prompt | Full support | + auto-generate offer |
| Screen generation | Manual copy-paste | Automated via MCP |
| Image extraction | Not available | `fetch_screen_image` |
| Code extraction | Not available | `fetch_screen_code` |
| Design context | `constitution.md` only | + `extract_design_context` |
| Project management | Not available | `create`/`list`/`get` projects |

---

## Skill: `authoring-stitch-prompts`

Transforms plain text or structured specs into Stitch-ready prompts with directive language, UI nouns, and 3-6 visual cues.

**Capabilities:**
- Converts natural text or structured specs into Stitch-ready prompts
- Enforces atomic prompting (one major intent per output)
- Supports markdown specs, pasted briefs, or referenced files
- Handles iteration briefs without re-authoring entire screens
- Feature-based directory organization with version auto-increment
- 6-prompt Stitch limit with automatic file splitting
- Optional MCP generation after authoring (when configured)

**Usage:**
```
Optimize this description into a Google Stitch prompt:
"A web dashboard with analytics cards, filters, and a dark theme."
```

---

## Skill: `generating-stitch-screens`

Orchestrates screen generation using the Stitch MCP server. Reads authored prompt files, sends each section to Stitch, and fetches resulting images and code.

**Requires:** Stitch MCP server configured (see MCP Setup below).

**Capabilities:**
- Parses prompt files with layout and component sections
- Creates or selects Stitch projects via MCP
- Generates screens from each prompt section
- Fetches rendered images and generated code
- Handles partial failures with retry logic

---

## Commands

### `/prompt`

Interactive prompt authoring with user preference gathering.

```bash
/prompt "Design a fintech dashboard with KPI cards and charts"
/prompt @specs/mobile-app.md
/prompt "Move the KPI cards above the chart"
```

Asks about components, style, and structure before generating. Revision requests skip questions. When MCP is configured, offers automated screen generation after authoring.

### `/stitch-generate`

Full end-to-end pipeline via MCP.

```bash
/stitch-generate "dashboard for fitness app"
/stitch-generate @design-intent/google-stitch/dashboard/prompt-v1.md
```

Accepts raw text (authors prompt first) or existing prompt files. Generates screens, fetches images, and saves everything to the feature directory.

### `/stitch-setup`

Guided MCP setup and verification.

```bash
/stitch-setup
```

Checks MCP availability, verifies connection, or guides through setup options.

---

## MCP Setup

> **Note:** The Stitch API requires preview/allowlist access from Google. MCP setup will fail with 403 errors until you have API access approved.

MCP is **not auto-configured** — you must manually add the server after confirming you have Stitch API access.

### Step 1: Authenticate with Google Cloud

```bash
gcloud auth application-default login
```

### Step 2: Add MCP Configuration

Add to your project's `.mcp.json` or user-level MCP config:

```json
{
  "stitch": {
    "command": "npx",
    "args": ["-y", "@_davideast/stitch-mcp", "proxy"],
    "env": {
      "STITCH_PROJECT_ID": "your-project-id"
    }
  }
}
```

Replace `your-project-id` with your Google Cloud project ID.

### Step 3: Restart Claude Code

Restart Claude Code to load the MCP configuration, then verify with `/stitch-setup`.

### Alternative: Interactive Setup

```bash
npx @_davideast/stitch-mcp init
```

Walks through authentication and configuration interactively.

---

## Directory Structure

```
google-stitch/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── prompt.md
│   ├── stitch-setup.md
│   └── stitch-generate.md
├── skills/
│   ├── authoring-stitch-prompts/
│   │   ├── SKILL.md
│   │   ├── WORKFLOW.md
│   │   ├── REFERENCE.md
│   │   ├── EXAMPLES.md
│   │   ├── TROUBLESHOOTING.md
│   │   ├── evaluation.json
│   │   └── templates/
│   │       └── authoring-stitch-prompts-template.md
│   └── generating-stitch-screens/
│       ├── SKILL.md
│       ├── WORKFLOW.md
│       ├── EXAMPLES.md
│       └── TROUBLESHOOTING.md
└── README.md
```

---

## Typical Workflow

### Without MCP

1. `/prompt "dashboard for analytics app"` — Author optimized Stitch prompt
2. Copy `design-intent/google-stitch/dashboard/prompt-v1.md` into Stitch UI
3. Generate screens in Stitch
4. Save exports to `design-intent/google-stitch/dashboard/exports/`
5. Iterate: `/prompt "move KPI cards above the chart"`

### With MCP

1. `/stitch-generate "dashboard for analytics app"` — Author + generate + fetch
2. Review images in `design-intent/google-stitch/dashboard/exports/`
3. Iterate: `/prompt "move KPI cards above the chart"` — re-author with generation offer
4. Accept generation to update screens automatically

---

## Relationship to Google Labs stitch-skills

This plugin is complementary to Google's own [stitch-skills](https://github.com/anthropics/skills) packages. Our strengths:

- **Prompt authoring** — atomic prompting, layout+component decomposition, 6-limit splitting
- **Interactive UX** — 3-question preference gathering via `/prompt`
- **Feature organization** — directory-based artifact management with version history

Google's stitch-skills focus on DESIGN.md-based workflows and React code transforms. Both can coexist in the same project.

---

## Evaluation

Run the included regression tests:
```
Evaluate the authoring-stitch-prompts Skill using evaluation.json
```

The harness checks prompt structure, UI noun usage, style cue count, atomicity, and MCP pipeline behavior.

---

## Installation

1. **Add the marketplace:**
   ```bash
   /plugin marketplace add ./arkhe-claude-plugins
   ```
2. **Install the plugin:**
   ```bash
   /plugin install google-stitch@arkhe-claude-plugins
   ```
3. **Restart Claude Code** to load skills.
4. **Optional:** Run `/stitch-setup` to configure MCP for automated generation (requires Stitch API access).

---

## References

- [Google Developers Blog - Introducing Stitch](https://developers.googleblog.com/en/stitch-a-new-way-to-design-uis/)
- [Google AI Developers Forum - Stitch Prompt Guide](https://discuss.ai.google.dev/t/stitch-prompt-guide/83844)
- [@_davideast/stitch-mcp](https://www.npmjs.com/package/@_davideast/stitch-mcp) — MCP server for Stitch
- [Anthropic Docs - Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)

---

## Version History

| Version | Date | Notes |
| --- | --- | --- |
| 1.0.0 | 2025-02-10 | Initial release — authoring + session management toolkit. |
| 2.0.0 | 2026-01-30 | MCP integration — screen generation, image/code fetching, design extraction. Removed extracting-stitch-mockups (replaced by MCP). Added /stitch-setup, /stitch-generate commands and generating-stitch-screens skill. |
