# 🧩 Google Stitch Plugin

> Claude + Google Stitch prompting toolkit for optimized prompt authoring.

---

## 🚀 Overview

The Google Stitch plugin provides an **Agent Skill** plus a shortcut slash command so Claude Code can ideate and author Stitch design prompts.

| Component | Type | Purpose |
| --- | --- | --- |
| `/prompt` | Command | One-step invocation of the Stitch prompt skill from any conversation. |
| 🧠 `authoring-stitch-prompts` | Skill | Converts freeform descriptions or spec files into optimized Stitch prompts that follow Google's recommended structure. |

Install the plugin to enforce atomic prompting and generate high-quality Stitch prompts.

---

## 🧠 Skill: `authoring-stitch-prompts`

**Purpose**  
Transforms plain text or structured specs into Stitch-ready prompts with directive language, UI nouns, and 3–6 visual cues.

**Highlights**
- Enforces atomic prompting (one major intent per output)
- Injects Stitch-friendly phrasing (“Design… Include…”)
- Supports markdown specs, pasted briefs, or referenced files
- Provides evaluation suite (`evaluation.json`) for regression testing

**Capabilities**
- Converts natural text or structured specs into Stitch-ready prompts
- Embeds visual style cues (3–6) and responsive constraints
- Handles iteration briefs (“move KPI cards above chart”) without re-authoring entire screens
- Applies Stitch’s preferred structure automatically (screen summary → bullets → style cues)
- Includes reference docs, templates, and regression tests for consistent output

**Typical usage**
```
Optimize this description into a Google Stitch prompt:
"A web dashboard with analytics cards, filters, and a dark theme."
```

**Example output**
> Design a responsive web dashboard for a wellness app.  
> Include: sidebar navigation (Home, Reports, Settings), header with user profile, KPI cards (Calories, Sleep, Steps), and a trend chart.  
> Style: calm, pastel tones, rounded cards, sans-serif font, minimal shadows.  
> Optimize for desktop first, single-column on mobile.

---

## ⚡ Command: `/prompt`

Run this command when you want Claude to rewrite any brief into a Stitch-ready prompt without manually referencing the skill.

```bash
/prompt "Design a fintech dashboard with KPI cards and charts"
/prompt @specs/mobile-app.md
```

The command automatically invokes **authoring-stitch-prompts**, passes along attached files, and returns a templated Stitch prompt.

---

## 📁 Directory Structure

```
google-stitch/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── prompt.md
├── README.md
└── skills/
    └── authoring-stitch-prompts/
        ├── SKILL.md
        ├── REFERENCE.md
        ├── EXAMPLES.md
        ├── evaluation.json
        └── templates/
            └── authoring-stitch-prompts-template.md
```

---

## ⚙️ Installation

1. **Add the marketplace (from repo root):**
   ```bash
   /plugin marketplace add ./arkhe-claude-plugins
   ```
2. **Install the plugin:**
   ```bash
   /plugin install google-stitch@arkhe-claude-plugins
   ```
3. **Restart Claude Code** to load the new Skills.

## 🧩 Typical Workflow

1. `Optimize this description into a Google Stitch prompt: "A web dashboard with analytics cards and dark theme"`
   → `authoring-stitch-prompts` transforms the brief into a structured Stitch prompt.

2. `/prompt create a mobile onboarding flow with 3 screens`
   → The `/prompt` command invokes the skill directly for quick prompt generation.

3. `Iterate on the dashboard: move the KPI cards above the chart`
   → The skill handles iteration briefs without re-authoring the entire screen.

---

## 🧪 Evaluation

Run the included regression tests from Claude Code:
```
Evaluate the authoring-stitch-prompts Skill using evaluation.json
```
The harness checks prompt structure, UI noun usage, style cue count, and atomicity. Extend `skills/authoring-stitch-prompts/evaluation.json` with new cases as you expand coverage.

---

## 📚 References

- [Google Developers Blog – Introducing Stitch](https://developers.googleblog.com/en/stitch-a-new-way-to-design-uis/)
- [Google AI Developers Forum – Stitch Prompt Guide](https://discuss.ai.google.dev/t/stitch-prompt-guide/83844)
- [Index.dev – Google Stitch Review](https://www.index.dev/blog/google-stitch-ai-review-for-ui-designers)
- [Bitovi – Product Designer’s Review](https://www.bitovi.com/blog/google-stitch-a-product-designers-review)
- [Anthropic Docs – Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Anthropic Docs – Skill Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

---

## 🧾 Version History

| Version | Date       | Notes |
| --- | --- | --- |
| 1.0.0 | 2025-02-10 | Initial release — combined authoring + session management toolkit. |
