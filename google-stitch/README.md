# 🧩 Google Stitch Plugin

> Claude + Google Stitch prompting toolkit that pairs optimized prompt authoring with session management for multi-screen design work.

---

## 🚀 Overview

The Google Stitch plugin bundles two complementary **Agent Skills** plus a shortcut slash command so Claude Code can ideate, author, and track Stitch design sessions end to end.

| Component | Type | Purpose |
| --- | --- | --- |
| `/prompt` | Command | One-step invocation of the Stitch prompt skill from any conversation. |
| 🧠 `authoring-stitch-prompts` | Skill | Converts freeform descriptions or spec files into optimized Stitch prompts that follow Google's recommended structure. |
| 📂 `stitch-session-manager` | Skill | Logs every Stitch prompt in a project, preserves style cues, and exports summaries for reviews or handoff. |

Install the plugin to keep Claude aware of your Stitch projects, enforce atomic prompting, and maintain consistent art direction across iterative sessions.

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

## 📂 Skill: `stitch-session-manager`

**Purpose**  
Tracks multi-screen Stitch projects, ensuring every screen prompt, style decision, and recommendation is captured under `.claude/sessions/<project>/`.

**Highlights**
- `session:new`, `session:add`, `session:summary`, `session:export` flow
- Calls `authoring-stitch-prompts` automatically before logging new screens
- Extracts palette/typography cues to keep future prompts aligned
- Exports Markdown summaries for PM/design reviews

**Typical usage**
```
Start a new Stitch session for a fintech dashboard app.
Add a Dashboard screen with charts and summary cards.
Summarize my current Stitch session.
```

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
    ├── authoring-stitch-prompts/
    │   ├── SKILL.md
    │   ├── REFERENCE.md
    │   ├── EXAMPLES.md
    │   ├── evaluation.json
    │   └── templates/
    │       └── authoring-stitch-prompts-template.md
    └── session-manager/
        ├── SKILL.md
        ├── WORKFLOW.md
        ├── EXAMPLES.md
        └── TROUBLESHOOTING.md
```

Supporting drafts or research notes (e.g., `skills/session-manager/draft.md`) stay alongside the production Skill for future revisions.

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

## 🧩 Combined Workflow

1. `Start a new Stitch session for a mobile banking app.`  
   → Session directories created under `.claude/sessions/mobile-banking/`.

2. `Add a Dashboard screen showing MRR, Churn, and Revenue charts.`  
   → `authoring-stitch-prompts` condenses the brief and logs it via `session:add`.

3. `Add a Settings screen with same color palette and typography.`  
   → `session:style` extracts palette cues before the new prompt is authored.

4. `Summarize my current Stitch session.` / `End session and export summary.`  
   → Markdown handoff with screen list, style notes, and recommendations.

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
