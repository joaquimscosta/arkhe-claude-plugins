# 🧠 Google Stitch Prompt Authoring Skill

> A Claude Agent Skill that transforms plain text or design specs into optimized **Google Stitch prompts** for UI generation.

---

## 🚀 Overview

This Skill helps you write and refine **Google Stitch prompts** — concise, directive design instructions that follow Stitch’s best practices for generating responsive, Figma-ready UI layouts.

Stitch (an experimental Google Labs tool) turns natural language and optional wireframes into UI designs and front-end code.  
This Skill ensures your prompts are short, atomic, and layout-aware, enabling Stitch to render clean, structured UIs with minimal rework.

---

## 🧩 Capabilities

✅ Converts **natural text** or **UI spec files** into Stitch-ready prompts  
✅ Enforces **atomic prompting** (one main goal per prompt)  
✅ Embeds **visual style cues** (3–6 per prompt)  
✅ Formats output with Stitch’s **preferred structure**  
✅ Supports **refinements, image references, and iterative edits**  
✅ Includes evaluation suite for testing Skill accuracy

---

## 📁 Directory Structure

```

google-stitch/
├── SKILL.md                     # Core skill definition (metadata + logic)
├── reference.md                 # Condensed best practices for Stitch prompting
├── examples.md                  # Input → optimized output examples
├── evaluation.json              # Test suite for validation
└── templates/
└── stitch-prompt-template.md # Output format template

````

---

## ⚙️ Installation

### 1. Create Skill Folder

For a personal Skill:

```bash
mkdir -p ~/.claude/skills/google-stitch
````

For a project-level Skill (shared via git):

```bash
mkdir -p .claude/skills/google-stitch
```

### 2. Copy Files

Place all provided files (`SKILL.md`, `reference.md`, `examples.md`, `evaluation.json`, and the `templates` directory) into that folder.

### 3. Restart Claude Code

Restart Claude Code to load the new Skill:

```bash
claude --restart
```

Claude automatically discovers Skills from:

* `~/.claude/skills/` (personal)
* `.claude/skills/` (project)
* Installed plugins containing `skills/`

---

## 🧠 Usage

After setup, simply ask Claude to optimize or create a Stitch prompt:

```
Optimize this description into a Google Stitch prompt:
"A mobile wellness app with dashboards and habit tracking."
```

or

```
Convert this spec file into a Stitch prompt:
# Dashboard
- Sidebar: navigation (Home, Reports, Settings)
- Main: KPI cards + revenue chart
- Style: minimal, deep blue accents
```

Claude will automatically invoke the **authoring-stitch-prompts** Skill.

---

## 🧩 Example Output

> Design a responsive web dashboard for a wellness app.
> Include: sidebar navigation (Home, Reports, Settings), header with user profile, KPI cards (Calories, Sleep, Steps), and a trend chart.
> Style: calm, pastel tones, rounded cards, sans-serif font, minimal shadows.
> Optimize for desktop first, single-column on mobile.

---

## 🧪 Running Evaluations

You can verify the Skill’s quality using the included evaluation suite.

### Run Tests

Ask Claude directly:

```
Evaluate the authoring-stitch-prompts Skill using evaluation.json
```

Claude will:

* Execute 5 representative scenarios
* Compare output against expected behavior
* Report any deviations or weaknesses (e.g., verbosity, missing style cues)

### Extend Evaluations

To add more test cases, edit `evaluation.json` and append new entries:

```json
{
  "id": "new_test_case",
  "query": "Create a prompt for a fintech dashboard with charts and alerts.",
  "expected_behavior": [
    "Includes clear UI nouns and concise visual style cues.",
    "Follows the Stitch template and avoids overlong descriptions."
  ]
}
```

---

## 🧭 Design Philosophy

This Skill embodies the principles outlined in Anthropic’s **Agent Skill Best Practices**:

* Concise over verbose (under 1000 words)
* Clear description & purpose in frontmatter
* One atomic task per prompt
* Declarative, not conversational tone
* Structured outputs for predictable activation

It integrates **progressive disclosure**, so extended examples and reference materials are only read when needed.

---

## 🧩 Integration Ideas

You can combine this Skill with:

* **Design System Assistant Skill:** ensure Stitch prompts follow brand guidelines
* **Prompt History Logger:** track changes and iterations
* **Code Export Validator:** check generated code snippets for consistency

---

## 🧾 Version History

| Version    | Date       | Notes                                                                   |
| ---------- | ---------- | ----------------------------------------------------------------------- |
| **v1.0.0** | 2025-11-10 | Initial release — converts specs and text into Stitch-optimized prompts |

---

## 📚 References

* [Google Developers Blog – Introducing Stitch](https://developers.googleblog.com/en/stitch-a-new-way-to-design-uis/)
* [Google AI Developers Forum – Stitch Prompt Guide](https://discuss.ai.google.dev/t/stitch-prompt-guide/83844)
* [Index.dev – Google Stitch Review](https://www.index.dev/blog/google-stitch-ai-review-for-ui-designers)
* [Bitovi – Product Designer’s Review](https://www.bitovi.com/blog/google-stitch-a-product-designers-review)
* [Anthropic Docs – Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
* [Anthropic Docs – Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

---

## 💡 Tip for Team Use

Add this Skill to your repo’s `.claude/skills/` folder and commit it:

```bash
git add .claude/skills/google-stitch
git commit -m "Add Google Stitch Prompt Authoring Skill"
git push
```

When teammates pull the latest changes, the Skill automatically activates in their Claude Code environment — no extra setup needed.

---

**Author:** Cloud Native Technical Writer
**Skill Type:** Prompt Optimization (Design AI)
**Target Model:** Claude Code (Sonnet / Opus)
**License:** MIT (customizable for team use)

```

---

## ✅ Your Final Skill Package (Complete)

```

google-stitch/
├── README.md
├── SKILL.md
├── reference.md
├── examples.md
├── evaluation.json
└── templates/
└── stitch-prompt-template.md

```
