---
name: prototype
description: Rapid UI prototyping — generates 3 visually distinct HTML/CSS components from a text prompt and serves them in a live browser gallery. Use when user runs /prototype, asks to "prototype a UI", "mock up a component", "generate HTML mockups", "create UI variations", "design exploration", "quick UI concept", or wants to see multiple visual approaches to a component. Also trigger when user says "show me different ways to build...", "explore different designs for...", or wants rapid visual exploration of a UI idea — even without saying "prototype" explicitly.
argument-hint: "<component description> [--vary <1|2|3>] [--dir <output-dir>] [--continue]"
---

# Prototype

Generate 3 visually distinct, high-fidelity HTML/CSS UI components from a single text prompt, then serve them in a live browser gallery so the user can click through and pick a favorite. Each component adopts a unique design persona based on physical/material metaphors — producing genuinely different visual approaches, not just color swaps.

## Quick Start

Parse `$ARGUMENTS` for the component description, optional `--vary N` flag, optional `--dir <path>`, and optional `--continue` flag.

- If `--continue` is present, skip to [Next-Turn Pick Capture](#next-turn-pick-capture).
- If `--vary N` is present, skip to the [Variation Workflow](#variation-workflow).
- Otherwise, follow Phases 1-3 below in a single pass — do not pause between phases or ask for confirmation.

If the description is vague ("button", "form"), just generate. The value is speed. Interpret generously.

### Phase 1: Style Direction

Think of 3 distinct design direction names using physical/material metaphors. Pattern: `[Adjective] + [Material/Process] + [Form/Action]`.

Each metaphor should imply different CSS techniques — not just colors. See the materiality-to-CSS mapping in [WORKFLOW.md](WORKFLOW.md).

Examples (invent your own):
- "Asymmetrical Rectilinear Blockwork" (Grid-heavy, primary pigments)
- "Grainy Risograph Layering" (`feTurbulence` grain, `mix-blend-mode: multiply`)
- "Kinetic Wireframe Suspension" (thin lines, floating silhouettes)
- "Spectral Prismatic Diffusion" (`backdrop-filter`, caustic refraction)

### Phase 2: Artifact Generation

For each style, generate a complete, self-contained `<!DOCTYPE html>` page (100-300 lines):

1. **Materiality**: the style metaphor drives every CSS choice
2. **Typography**: Google Fonts via `<link>`, pair a bold sans with a refined monospace
3. **Motion**: subtle CSS animations and hover transitions
4. **IP Safeguard**: no artist names, brand names, or trademarks
5. **Layout**: bold negative space, avoid generic card grids
6. **Content**: realistic placeholder content, not lorem ipsum

Output: raw HTML (no markdown fences), with inline `<style>` and Google Fonts `<link>`.

### Phase 3: Live Preview Session

Start an `arkhe-preview` live session (from the devtools plugin) and write the artifacts into the session's `content/`. The server serves the gallery fragment, watches for changes, and logs the user's variant pick to `events.jsonl`.

1. Resolve the gallery example flavor:
   ```bash
   PLUGIN_ROOT=$(dirname "$(dirname "$(which arkhe-preview)")")
   EX="$PLUGIN_ROOT/skills/browser-companion/examples/gallery"
   ```
2. Start the server:
   ```bash
   arkhe-preview start \
     --project-dir "$DIR" \
     --frame-template "$EX/frame-template.html" \
     --helper       "$EX/helper.js"
   ```
   `$DIR` defaults to `.prototype/`, or the value of `--dir`.
3. Parse the JSON line on stdout to get `url`, `screen_dir`, `state_dir`, `session_dir`.
4. Write each artifact into `$screen_dir`:
   - `01-{prompt-slug}-{style1-slug}.html`
   - `02-...`
   - `03-...`
5. Write `$DIR/manifest.json` (top-level pointer used by `--vary` / `--continue`). See [WORKFLOW.md](WORKFLOW.md) for the schema.
6. Write `99-gallery.html` LAST into `$screen_dir` so it has the newest mtime and is served at `GET /`. Template + inline swap-on-click JS in [WORKFLOW.md](WORKFLOW.md).
7. Print the terminal summary (URL, content/pick paths, variant names, next-step hints) and **end the turn**.

The user clicks a variant in the sidebar; the iframe canvas swaps; the gallery helper.js logs the click to `events.jsonl` (no agent involvement needed during the click).

## Next-Turn Pick Capture

This skill follows a turn-based loop, not realtime polling. After Phase 3 ends, the user picks at their leisure. Read their pick when they next reply.

**Two paths to the pick:**

1. **Explicit (`/prototype --continue`)**: read `$DIR/manifest.json`, then read `manifest.state_dir/events.jsonl`. Find the most recent event with `action === "select-variant"`. Report the chosen position + style, and offer next steps (`/prototype --vary N` to iterate; `/design-intent ...` to implement).

2. **Implicit (next user message)**: if the previous turn ran `/prototype` and the user's next message is conversational ("ok", "I like the second one", "what did I pick?"), check whether `manifest.json` exists in the most recent prototype dir (default `.prototype/`); if so, read `events.jsonl` and merge the structured pick with the user's text before responding.

If `events.jsonl` doesn't exist or has no `select-variant` events, the user didn't click — fall back to their terminal text only.

See [WORKFLOW.md](WORKFLOW.md) for the event schema and the resolution steps.

## Variation Workflow

When `--vary N` is passed (N = 1, 2, or 3):

0. Run `arkhe-preview status <manifest.session_dir>`. If the server is dead (owner-pid watchdog or 30-min idle), restart it with the same `--project-dir` and copy existing artifacts into the new `screen_dir` before continuing. See [WORKFLOW.md](WORKFLOW.md) for the restart recipe.
1. Read `$DIR/manifest.json` to find the Nth artifact (`artifacts[N-1].abs_path` or `.file` inside `screen_dir`).
2. Read the existing artifact HTML to ground the variations.
3. Generate 3 radical conceptual variations using NEW physical metaphors (different from the original and from each other).
4. Write variation files into `$screen_dir` as `{original-slug}-var-1.html`, `-var-2.html`, `-var-3.html`.
5. Update `99-gallery.html` to show the variations (or write `99-gallery-vary.html` LAST). Update `manifest.json` with a `variations` array.

See [WORKFLOW.md](WORKFLOW.md) for the full variation workflow.

## References

- [WORKFLOW.md](WORKFLOW.md) — Manifest schema, gallery fragment template, materiality-to-CSS mapping, arkhe-preview details
- [EXAMPLES.md](EXAMPLES.md) — Usage examples and sample sessions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues (port collision, server not starting, can't find pick)
