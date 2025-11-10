---
name: stitch-session-manager
description: >
  Manages multi-screen Google Stitch design sessions by tracking prompts, screens, and shared style language.
  Use when you need continuity across Stitch prompts, want to append or summarize sessions, or must export
  screen histories for reviews. Triggers on phrases like "start/continue Stitch session", "log screen", or
  "summarize Stitch progress".
allowed-tools: Read, Write, List, Grep
---

# Stitch Session Manager

## Quick Start
- `Start a new Stitch session for [project]` → creates `.claude/sessions/<project>/session.json`.
- `Add a screen called [name] with this brief: ...` → optimizes prompt via `stitch-prompt`, logs as `<slug>-###.json`.
- `Summarize my current Stitch session` → returns screen list, visual patterns, next-step suggestions.
- `Generate a new prompt for [screen] using current session style` → reuses stored cues before calling the authoring skill.
- `End this Stitch session and export summary` → writes Markdown summary under the session folder.

## Output Structure
- `session.json`: metadata (`session_name`, timestamps, style guide notes, prompt index).
- `screen-log/<slug>-###.json`: individual prompt payloads (raw brief, optimized prompt, status, references).
- `summary.md`: exportable brief for reviews or handoffs.
- All files live under `.claude/sessions/<project>/`.

## Commands & Triggers
| Command | Trigger phrases | Result |
| --- | --- | --- |
| `session:new` | "start a new Stitch session" | Initialize directories + base metadata. |
| `session:add` | "add screen", "log prompt", "iterate screen" | Capture new screen, call authoring skill, persist JSON. |
| `session:list` | "show session screens" | Return ordered list of screens + status. |
| `session:summary` | "summarize session", "what have we made" | Produce textual summary + style cues. |
| `session:style` | "reuse style", "match previous look" | Extract palette, typography, tone for new prompts. |
| `session:export` | "export session", "end session" | Finalize summary.md with totals + next steps. |

## Workflow
Follow the abbreviated loop: initialize → add/update screens → reference session memory → export.  
See [WORKFLOW.md](WORKFLOW.md) for detailed branching logic, file formats, and pseudo-commands.

## Style Memory & Integration
- Before writing a new prompt, the Skill scans existing `session.json` + latest screen logs to extract design cues (color, typography, density, component patterns).
- It then calls **`stitch-prompt`** with:
  - Original user brief.
  - Session style payload (palette, layout bias, voice).
  - Optional constraints (responsive targets, export needs).
- Returned prompt is saved back to the log and surfaced to the user for immediate Stitch use.
- When no stylistic precedent exists, fall back to user-provided cues and update session metadata once the first screen is logged.

## Examples
Representative transcripts for starting sessions, logging iterations, and exporting summaries live in [EXAMPLES.md](EXAMPLES.md). Use them to mirror tone, prompt framing, and file naming.

## Common Issues
High-level fixes are below; detailed diagnosis (including directory repair scripts) is in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
- Missing session folder → re-run `session:new` or point to existing `.claude/sessions/<project>`.
- Style drift → run `session:style` to restate cues before adding new screens.
- Duplicate screen names → the Skill auto-increments suffixes; confirm desired slug before export.

## Version History
- v1.0.0 (2025-02-10): Initial release — session management companion to `stitch-prompt`.
