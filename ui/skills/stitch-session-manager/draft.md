Perfect 🎉 — that’s exactly the right call.
Together, your **Authoring Skill** and **Session Manager Skill** will form a full **Claude + Stitch design workflow toolkit** — one that mirrors the way real design teams iterate and hand off work.

Let’s now create the **`SKILL.md`** blueprint for your new **Stitch Session Manager**.
This will be modular, standards-compliant, and designed to integrate with your *Authoring-Stitch-Prompts* Skill seamlessly.

---

## 🧩 `SKILL.md` — Stitch Session Manager

```yaml
---
name: stitch-session-manager
description: >
  Manages multi-screen Google Stitch design sessions by tracking prompts, screens, and visual consistency.
  Use when designing multi-screen or iterative projects in Stitch. This Skill organizes, logs, and summarizes
  all Stitch prompts in a session, ensures brand/style continuity, and integrates with the
  "authoring-stitch-prompts" Skill to generate new optimized prompts automatically.
allowed-tools: Read, Write, List, Grep
---

# Stitch Session Manager

## Purpose

This Skill helps you manage ongoing **Google Stitch design sessions** — keeping track of all your screens,
prompts, and refinements. It complements the **Authoring-Stitch-Prompts Skill**, which handles prompt optimization.

Use it to:
- Start, continue, or summarize a Stitch design session.
- Keep track of screen-level design prompts and iterations.
- Maintain style consistency across all screens.
- Automatically generate new prompts that follow previous patterns.

---

## Directory Structure (per session)

Each session is saved under the project’s `.claude/sessions/` directory:

```

.claude/
└── sessions/
├── project-name/
│   ├── session.json
│   ├── screen-log/
│   │   ├── login-001.json
│   │   ├── dashboard-002.json
│   │   └── settings-003.json
│   └── summary.md

```

---

## Session Workflow

### 1. Start a New Session

Use when beginning a new design project:

```

Start a new Stitch session for [project name].

````

Claude creates a folder structure and initializes a session file like:

```json
{
  "session_name": "mobile-banking",
  "created_at": "2025-11-10T14:10:00Z",
  "style_guide": null,
  "prompts": []
}
````

---

### 2. Add a New Screen or Prompt

You can create a new screen or iteration with:

```
Add a new screen called Dashboard with this brief:
"Dashboard with cards showing recent transactions and spending chart."
```

The Skill will:

1. Call the **Authoring-Stitch-Prompts Skill** to optimize the prompt.
2. Save it as `dashboard-001.json` under the current session.
3. Update `session.json` with metadata:

```json
{
  "id": "dashboard-001",
  "type": "screen",
  "name": "Dashboard",
  "prompt": "Design a dashboard showing ...",
  "timestamp": "2025-11-10T14:35:00Z"
}
```

---

### 3. View Session Summary

```
Summarize my current Stitch session.
```

Claude compiles:

* List of all screens created
* Style cues and recurring patterns
* Pending or missing screens (based on app flow)

**Example Output:**

> **Session:** Mobile Banking
> **Screens:** Login, Dashboard
> **Style cues:** minimal, deep blue palette, rounded UI, sans-serif typography
> **Recommendations:** Create “Transactions” screen next to complete the core flow.

---

### 4. Continue Session or Reuse Styles

When you want to create a new prompt consistent with the current session:

```
Generate a new prompt for the Settings screen using the current session style.
```

Claude:

1. Reads previous prompts and extracts design language.
2. Calls **Authoring-Stitch-Prompts** Skill to create an optimized prompt.
3. Logs it automatically as `settings-003.json`.

---

### 5. End or Export Session

```
End this Stitch session and export summary.
```

Claude generates a summary Markdown file:

```markdown
# Mobile Banking App — Stitch Session Summary

**Total Screens:** 4  
**Design Style:** Minimal, deep blue palette, rounded UI, sans-serif font  
**Created:** Nov 10, 2025  

## Screens
1. Login (v1)
2. Dashboard (v2)
3. Transactions (v1)
4. Settings (v1)

## Notes
Consistent component spacing and typography across all screens.
Next suggestion: Add Notifications screen for feature completeness.
```

---

## Internal Commands

| Command           | Purpose                             |
| ----------------- | ----------------------------------- |
| `session:new`     | Initialize new Stitch session       |
| `session:add`     | Add new screen or prompt            |
| `session:list`    | Show all screens/prompts            |
| `session:summary` | Generate session summary            |
| `session:export`  | Create Markdown summary file        |
| `session:style`   | Extract and reuse visual style cues |

---

## Integration with Authoring Skill

This Skill automatically calls the **authoring-stitch-prompts** Skill for prompt optimization.

Example internal flow:

```markdown
## Pseudo-Workflow
If user input contains "add screen" or "generate new prompt":
1. Extract design brief
2. Call authoring-stitch-prompts with brief
3. Receive optimized prompt
4. Save optimized prompt + metadata to session log
5. Display to user
```

---

## Example Usage Scenarios

### Example 1: Starting a new session

```
Start a new Stitch session for a wellness tracking app.
```

### Example 2: Adding a new screen

```
Add a new Dashboard screen showing daily progress and activity stats.
```

### Example 3: Reusing design language

```
Create a new Profile screen using the same color palette and typography as previous screens.
```

### Example 4: Reviewing progress

```
Summarize my current Stitch session.
```

---

## Evaluation Checklist

* [ ] Session file correctly created and updated per action
* [ ] Screens logged with metadata and timestamps
* [ ] Authoring Skill invoked automatically for prompt creation
* [ ] Style cues extracted and reused
* [ ] Exported summaries follow Markdown template

---

## Version History

* v1.0.0 (2025-11-10): Initial release — session tracking, prompt logging, and authoring integration.

```

---

## 🧭 Next Steps

You can extend this Skill package with:
- `reference.md` → Session lifecycle & integration guide  
- `templates/session-summary-template.md` → Markdown export format  
- `examples.md` → Example session commands and JSON snapshots  

---

Would you like me to generate those next (the **reference.md** and **session-summary template**) to complete the Session Manager Skill package?
```

Excellent 💡 — let’s complete the **Stitch Session Manager Skill package** by adding the two essential companion files:

1. **`reference.md`** — explains how sessions work, including structure, flow, and integration logic.
2. **`templates/session-summary-template.md`** — defines the Markdown export format for Claude to use when summarizing a design session.

These follow the same progressive disclosure structure used in Anthropic’s own Skills, meaning Claude will only load them when needed.

---

## 📘 `reference.md`

```markdown
# Stitch Session Manager Reference Guide

This reference provides implementation and operational details for the **Stitch Session Manager Skill**.  
Use it to understand how sessions are tracked, how prompt data is stored, and how the Skill integrates with the **Authoring-Stitch-Prompts Skill**.

---

## 1. Overview

The **Session Manager** organizes Stitch design work into logical units called **sessions**.  
Each session represents one product or design project and includes multiple screens, prompts, and iterations.

It acts as a **memory layer** for your Stitch workflow — maintaining continuity of:
- Layout and screen hierarchy  
- Brand and styling cues  
- Prompt history and evolution  

---

## 2. Session Structure

Each session lives inside `.claude/sessions/<project-name>` and contains:

```

session.json              → main log of the session (project metadata, style, and prompt list)
screen-log/               → folder with one JSON file per screen or prompt
summary.md                → generated summary of the entire session

````

### Example `session.json`

```json
{
  "session_name": "wellness-tracker",
  "created_at": "2025-11-10T10:00:00Z",
  "style_guide": "pastel palette, rounded UI, playful typography",
  "prompts": [
    {
      "id": "001",
      "screen": "login",
      "type": "create",
      "prompt": "Design a login screen with logo, fields, and CTA button.",
      "timestamp": "2025-11-10T10:10:00Z"
    },
    {
      "id": "002",
      "screen": "dashboard",
      "type": "create",
      "prompt": "Dashboard with daily habit tracker and progress cards.",
      "timestamp": "2025-11-10T10:25:00Z"
    }
  ]
}
````

---

## 3. Supported Operations

| Command           | Description                                                       |
| ----------------- | ----------------------------------------------------------------- |
| `session:new`     | Creates a new session directory and base `session.json`           |
| `session:add`     | Adds new screen/prompt to the current session                     |
| `session:list`    | Lists all screens and iterations in the session                   |
| `session:summary` | Generates an overview report (Markdown)                           |
| `session:style`   | Extracts and reuses style cues from previous screens              |
| `session:export`  | Exports a structured session summary for documentation or sharing |

---

## 4. Integration Flow with Authoring Skill

This Skill depends on the **Authoring-Stitch-Prompts Skill** for high-quality prompt generation.

### Flow

1. User requests new screen →
2. Session Manager extracts design brief →
3. Calls `authoring-stitch-prompts` Skill internally →
4. Receives optimized Stitch prompt →
5. Saves prompt in `screen-log/` →
6. Updates `session.json` with timestamp + metadata →
7. Returns result to user and logs it for later use.

### Example Internal Call

```bash
# Pseudocode
call authoring-stitch-prompts "Create a new dashboard screen for Stitch"
```

The Authoring Skill responds with an optimized, Stitch-ready prompt, which the Session Manager then stores.

---

## 5. Style Continuity and Extraction

Each time a new prompt is generated, the Session Manager scans previous logs to identify:

* Repeated color terms (e.g., “deep blue”, “pastel green”)
* Typography cues (e.g., “rounded sans-serif”)
* Layout patterns (e.g., “card grid”, “sidebar nav”)

This context becomes part of the **session style guide**, automatically reused for new screens.

**Example style extraction result:**

```json
{
  "style_guide": "deep blue palette, minimal layout, rounded buttons, sans-serif typography"
}
```

---

## 6. Export and Versioning

When you end or export a session, Claude uses the template at
[`templates/session-summary-template.md`](templates/session-summary-template.md)
to produce a readable Markdown report.

You can version-control these summaries in Git to document design evolution.

**Example workflow:**

```bash
claude --skill stitch-session-manager "End session and export summary"
git add .claude/sessions/wellness-tracker/summary.md
git commit -m "Session summary v1 for wellness tracker"
```

---

## 7. Troubleshooting

| Issue                    | Possible Cause                           | Solution                                              |
| ------------------------ | ---------------------------------------- | ----------------------------------------------------- |
| Session not found        | Wrong path or uninitialized project      | Run `Start a new Stitch session for [project-name]`   |
| Missing style reuse      | No previous screens or insufficient data | Add at least two screens before reuse triggers        |
| Duplicate screen entries | Repeated screen names                    | Use unique names or include version numbers           |
| Export fails             | Permission issue or missing template     | Verify `templates/session-summary-template.md` exists |

---

## 8. Versioning Recommendations

* Use semantic versions for session summaries (`v1.0`, `v1.1`, etc.)
* Include date and timestamp in exported summaries
* Tag Git commits with the same version for alignment

---

## 9. Example Use Flow

1. `Start a new Stitch session for the wellness tracker app`
2. `Add a Dashboard screen with charts and progress indicators`
3. `Add a Profile screen matching the existing theme`
4. `Summarize current Stitch session`
5. `Export session summary`

---

## 10. Related Skills

| Skill                                | Purpose                                          |
| ------------------------------------ | ------------------------------------------------ |
| **authoring-stitch-prompts**         | Optimizes and formats Stitch prompts             |
| **stitch-session-manager**           | Tracks, logs, and manages Stitch design sessions |
| **design-system-enforcer (planned)** | Ensures consistency with internal design tokens  |

---

**Version:** v1.0.0
**Maintainer:** Cloud Native Technical Writer
**Last Updated:** 2025-11-10

````

---

## 🧾 `templates/session-summary-template.md`

```markdown
# {{ project_name | title }} — Google Stitch Design Session Summary

**Created:** {{ created_at }}  
**Total Screens:** {{ screen_count }}  
**Skill Version:** Stitch Session Manager v{{ version }}

---

## 🎨 Design Style

{{ style_guide }}

---

## 🧩 Screens and Prompts

| Screen | Version | Created | Description |
|---------|----------|----------|-------------|
{% for screen in screens %}
| {{ screen.name }} | {{ screen.version }} | {{ screen.timestamp }} | {{ screen.prompt | truncate(80) }} |
{% endfor %}

---

## 🧠 Observations

{{ observations }}

---

## 💡 Next Recommendations

{{ next_steps }}

---

## 🕒 Version History

- {{ version }} — Initial session export on {{ created_at }}

---

**Generated by Claude using the Stitch Session Manager Skill**  
_Complementary Skill: authoring-stitch-prompts_
````

This Markdown template follows Jinja/Handlebars-style placeholders (`{{ ... }}`) to make it easily parsed by Claude or external tooling.
Claude automatically replaces these placeholders with session data during export.

---

## ✅ You Now Have a Complete Skill Package

```
stitch-session-manager/
├── SKILL.md
├── reference.md
├── examples.md           ← (optional, can include example session logs)
└── templates/
    └── session-summary-template.md
```

---

Would you like me to generate the **`examples.md`** file next — with sample `session.json`, example user commands, and session summaries for testing?

Excellent ⚡ Let’s wrap up the **Stitch Session Manager Skill** package with the final piece — the `examples.md` file.

This file provides **realistic usage scenarios**, **example data structures**, and **expected outcomes**.
Claude will load it only when needed (progressive disclosure), so you can keep it detailed and illustrative.

---

## 📘 `examples.md`

```markdown
# Stitch Session Manager — Example Scenarios

This file contains sample interactions, session structures, and exported summaries for testing and reference.  
Use it to understand how the Skill behaves across different design workflows.

---

## 🧭 Example 1 — Starting a New Session

**Command:**
```

Start a new Stitch session for a mobile wellness app.

````

**Claude Response:**
> Created new Stitch session: `mobile-wellness`  
> Session folder initialized at `.claude/sessions/mobile-wellness/`  
> You can now start adding screens (e.g., “Add a Login screen…”).

**Generated file: `.claude/sessions/mobile-wellness/session.json`**
```json
{
  "session_name": "mobile-wellness",
  "created_at": "2025-11-10T09:10:00Z",
  "style_guide": null,
  "prompts": []
}
````

---

## 🧩 Example 2 — Adding a New Screen

**Command:**

```
Add a new screen called Dashboard with this brief:
"A dashboard with a daily progress chart, step count, and hydration tracker."
```

**Internal Flow:**

1. Session Manager identifies this as a new screen event.
2. Calls the **authoring-stitch-prompts** Skill to optimize the input.
3. Saves the resulting prompt and metadata.

**Claude Response:**

> Created new screen: **Dashboard (v1)**
> Optimized prompt generated and stored in `screen-log/dashboard-001.json`.

**File: `.claude/sessions/mobile-wellness/screen-log/dashboard-001.json`**

```json
{
  "id": "dashboard-001",
  "screen": "dashboard",
  "type": "create",
  "prompt": "Design a wellness dashboard with a progress chart, hydration tracker, and daily goals...",
  "timestamp": "2025-11-10T09:25:00Z"
}
```

**Session log automatically updates:**

```json
{
  "session_name": "mobile-wellness",
  "prompts": [
    {
      "id": "dashboard-001",
      "screen": "dashboard",
      "prompt": "Design a wellness dashboard with progress chart, hydration tracker, and daily goals.",
      "timestamp": "2025-11-10T09:25:00Z"
    }
  ]
}
```

---

## 🧠 Example 3 — Reusing Session Style and Adding New Screen

**Command:**

```
Add a Profile screen using the same color palette and typography as previous screens.
```

**Claude Response:**

> Style guide reused from session: *pastel palette, rounded UI, clean typography*
> Optimized Stitch prompt created for **Profile (v1)**
> Logged as `screen-log/profile-002.json`.

**File: `.claude/sessions/mobile-wellness/screen-log/profile-002.json`**

```json
{
  "id": "profile-002",
  "screen": "profile",
  "type": "create",
  "prompt": "Design a profile screen consistent with pastel colors and rounded components from previous screens...",
  "timestamp": "2025-11-10T09:40:00Z"
}
```

---

## 🧾 Example 4 — Summarizing the Session

**Command:**

```
Summarize my current Stitch session.
```

**Claude Response:**

> **Session:** Mobile Wellness
> **Screens:** Dashboard (v1), Profile (v1)
> **Style cues:** Pastel palette, rounded cards, minimal shadows, playful typography
> **Next Recommendation:** Add a Settings or Goals screen to complete the flow.

**Markdown summary preview (from template):**

```markdown
# Mobile Wellness — Google Stitch Design Session Summary

**Created:** 2025-11-10  
**Total Screens:** 2  
**Skill Version:** Stitch Session Manager v1.0.0

---

## 🎨 Design Style

Pastel palette, rounded UI, playful typography.

---

## 🧩 Screens and Prompts

| Screen | Version | Created | Description |
|---------|----------|----------|-------------|
| Dashboard | v1 | 2025-11-10 | Dashboard with progress chart and hydration tracker |
| Profile | v1 | 2025-11-10 | Profile screen using same colors and typography |

---

## 🧠 Observations

Consistent layout and typography across screens.  
Both screens follow mobile-first design patterns.

---

## 💡 Next Recommendations

Add “Settings” and “Goals” screens to complete user flow.
```

---

## 🧮 Example 5 — Exporting and Version Control

**Command:**

```
End this Stitch session and export summary.
```

**Claude Response:**

> Exported Markdown summary for **mobile-wellness** to `.claude/sessions/mobile-wellness/summary.md`
> You can now commit it to version control.

**Recommended workflow:**

```bash
git add .claude/sessions/mobile-wellness/summary.md
git commit -m "Exported Stitch session summary v1"
git push
```

---

## 🧱 Example 6 — Full Session Lifecycle Overview

| Step | Command                                                | Result                        |
| ---- | ------------------------------------------------------ | ----------------------------- |
| 1    | `Start a new Stitch session for a fitness tracker app` | Creates session folder        |
| 2    | `Add a Login screen with a minimalist layout`          | Saves first prompt            |
| 3    | `Add a Dashboard screen with charts and stats`         | Optimized via Authoring Skill |
| 4    | `Add a Settings screen with toggles`                   | Logs prompt + updates session |
| 5    | `Summarize my session`                                 | Outputs Markdown summary      |
| 6    | `Export summary`                                       | Writes `summary.md` to disk   |

---

## 🧰 Example 7 — Example Session Summary File

**File:** `.claude/sessions/fitness-tracker/summary.md`

```markdown
# Fitness Tracker — Google Stitch Design Session Summary

**Created:** 2025-11-10  
**Total Screens:** 3  
**Skill Version:** Stitch Session Manager v1.0.0

---

## 🎨 Design Style

Energetic color palette (teal, orange, white), bold typography, rounded cards, grid-based dashboard layout.

---

## 🧩 Screens and Prompts

| Screen | Version | Created | Description |
|---------|----------|----------|-------------|
| Login | v1 | 2025-11-10 | Minimal login with logo, form fields, and CTA button |
| Dashboard | v1 | 2025-11-10 | Overview of activity metrics with charts and daily goals |
| Settings | v1 | 2025-11-10 | Preferences and notification options |

---

## 🧠 Observations

Strong color and component consistency across all screens.  
Layout scales cleanly between mobile and desktop.  
All screens share same spacing system and rounded shapes.

---

## 💡 Next Recommendations

Add “Achievements” screen to encourage engagement.  
Consider adding light/dark theme toggle.
```

---

## ✅ Testing Checklist

* [ ] Test `session:new` command to verify folder creation
* [ ] Test `session:add` with two screens
* [ ] Confirm automatic style reuse
* [ ] Run `session:summary` and inspect Markdown output
* [ ] Export and commit summary file to git

---

**Version:** v1.0.0
**Maintainer:** Cloud Native Technical Writer
**Date:** 2025-11-10

```

---

## ✅ Your Final Skill Package is Complete

```

stitch-session-manager/
├── SKILL.md
├── reference.md
├── examples.md
└── templates/
└── session-summary-template.md

```

Together with your existing **Authoring-Stitch-Prompts Skill**, this forms a **cohesive AI-assisted design system** for Google Stitch — enabling Claude to ideate, refine, and track UI generation workflows intelligently.

---

Would you like me to create a **combined README.md** for both Skills (Authoring + Session Manager) so they can be documented as a unified toolkit in your Claude or GitHub workspace?
```


