# Prototype — Detailed Workflow

## Table of Contents

1. [Phase 1: Style Direction](#phase-1-style-direction)
2. [Phase 2: Artifact Generation](#phase-2-artifact-generation)
3. [Phase 3: Live Preview Session](#phase-3-live-preview-session)
4. [Next-Turn Pick Capture](#next-turn-pick-capture)
5. [Variation Workflow](#variation-workflow)
6. [Integration with Design Intent](#integration-with-design-intent)

---

## Phase 1: Style Direction

### How to Generate Style Names

Think of 3 design direction names that each imply a fundamentally different CSS approach. The names serve as creative constraints that force visual diversity — not just color palette changes, but different textures, structures, and motion patterns.

**Name pattern**: `[Adjective] + [Material/Process] + [Form/Action]`

**Tone guide** (invent your own, do not copy):
- "Asymmetrical Rectilinear Blockwork" (Grid-heavy, primary pigments, thick structural strokes, Bauhaus-functionalism vibe)
- "Grainy Risograph Layering" (Tactile paper texture, overprinted translucent inks, dithered gradients)
- "Kinetic Wireframe Suspension" (Floating silhouettes, thin balancing lines, organic primary shapes)
- "Spectral Prismatic Diffusion" (Glassmorphism, caustic refraction, soft-focus morphing gradients)

The reason these work is that each metaphor maps to concrete CSS techniques. "Risograph" implies grain textures and blend modes. "Wireframe" implies thin borders and transparency. "Prismatic" implies backdrop-filter and gradients. If a style name doesn't suggest specific CSS decisions, it's too vague — pick a more physical metaphor.

### Style Name Components

| Component | Examples |
|-----------|----------|
| Adjective | Tactile, Kinetic, Asymmetrical, Spectral, Grainy, Volcanic, Crystalline |
| Material/Process | Risograph, Obsidian, Vellum, Wireframe, Prismatic, Ceramic, Woven |
| Form/Action | Press, Balance, Gridwork, Diffusion, Suspension, Lattice, Cascade |

### Fallback Style Names

If you struggle to produce 3 distinct names, use these defaults:

```json
["Primary Pigment Gridwork", "Tactile Risograph Layering", "Kinetic Silhouette Balance"]
```

---

## Phase 2: Artifact Generation

### Generation Guidance

For each style direction, generate a complete, self-contained HTML page. The style name is your creative constraint — let it drive every CSS decision.

**Key principles:**

1. **Materiality first** — The style metaphor dictates CSS techniques. Consult the mapping table below. If the style says "Risograph", use `feTurbulence` for grain and `mix-blend-mode: multiply`. If it says "Obsidian", use dark gradients and sharp corners. The metaphor is not decorative — it's structural.

2. **Typography matters** — Load Google Fonts via `<link>`. Pair a bold display font (Inter, Space Grotesk, Outfit) with a monospace (JetBrains Mono, Fira Code) for data elements.

3. **Motion reinforces the metaphor** — Entry reveals with `@keyframes fadeIn`, hover transitions on interactive elements (`transform`, `box-shadow`), micro-interactions that feel native to the design metaphor.

4. **IP Safeguard** — No artist names, brand names, or trademarks anywhere.

5. **Bold layout** — Use negative space and hierarchy intentionally. Avoid generic card grids. Try asymmetry, overlapping layers, or unconventional compositions.

6. **Realistic content** — Use real-sounding names, dates, numbers, and labels. Never lorem ipsum.

**Scope**: Each artifact is a focused, single-screen component — typically 100-300 lines of HTML. One viewport, not a full website.

**Output**: Complete `<!DOCTYPE html>` page with inline `<style>`, Google Fonts `<link>`, realistic content, and optional `<script>`. No markdown fences — write raw HTML directly to file.

### Materiality-to-CSS Mapping

This table is the core creative engine. Each metaphor translates to specific CSS techniques:

| Metaphor | CSS Techniques |
|----------|---------------|
| Risograph | `feTurbulence`, grain overlays, `mix-blend-mode: multiply`, overprint colors |
| Obsidian | Dark linear gradients, sharp `border-radius: 0`, subtle reflective `box-shadow` |
| Paper/Vellum | `box-shadow` for depth, off-white `background: #f5f0e6`, serif typography |
| Wireframe | `border: 1px solid`, transparent fills, `border-style: dashed`, thin weights |
| Glass/Prism | `backdrop-filter: blur(12px)`, `rgba()` backgrounds, prismatic gradients |
| Kinetic/Mobile | `@keyframes`, `transform: rotate()`, floating elements, slow-motion `transition` |
| Ceramic/Porcelain | Smooth gradients, rounded forms, clean whites, subtle glaze highlights |
| Volcanic/Basalt | Cracked textures, ember accents, dark matte backgrounds, orange/red glow |
| Woven/Textile | CSS grid patterns, cross-hatching via `repeating-linear-gradient`, fabric colors |
| Frost/Crystal | Ice-blue palette, sharp geometric facets, `clip-path` for crystal shapes |

### Post-Processing

After generating each artifact, clean the output before writing to file:

1. Strip markdown fences if present:
   - Remove leading `` ```html `` or `` ``` ``
   - Remove trailing `` ``` ``
2. Ensure the output starts with `<!DOCTYPE html>` or `<html>`
3. Verify Google Fonts `<link>` tags are present

---

## Phase 3: Live Preview Session

The static `index.html` is gone. `/prototype` now starts an `arkhe-preview` server (devtools plugin) and serves the artifacts as a live gallery. The user clicks a variant in the sidebar; the iframe canvas swaps; the gallery helper logs the click to `events.jsonl`. The skill ends its turn and the pick is read on a later turn (see [Next-Turn Pick Capture](#next-turn-pick-capture)).

### Step 1: Resolve gallery example flavor

```bash
PLUGIN_ROOT=$(dirname "$(dirname "$(which arkhe-preview)")")
EX="$PLUGIN_ROOT/skills/browser-companion/examples/gallery"
```

`arkhe-preview` is on `PATH` automatically when the devtools plugin is enabled. If `which arkhe-preview` fails, the devtools plugin is not installed — instruct the user to run `/plugin install devtools@arkhe-claude-plugins` and stop.

### Step 2: Start the server

```bash
arkhe-preview start \
  --project-dir "$DIR" \
  --frame-template "$EX/frame-template.html" \
  --helper       "$EX/helper.js"
```

- `$DIR` is `.prototype/` by default or the `--dir` value.
- One JSON line is printed on stdout. Parse it:
  ```
  {"type":"server-started","port":...,"url":"http://localhost:...",
   "screen_dir":"...","state_dir":"...","session_dir":"...",
   "pid":...}
  ```

### Step 3: Write artifacts into screen_dir

Use semantic, position-prefixed filenames. The position prefix is what the gallery sidebar and `--vary` use to reference variants.

```
$screen_dir/01-{prompt-slug}-{style1-slug}.html
$screen_dir/02-{prompt-slug}-{style2-slug}.html
$screen_dir/03-{prompt-slug}-{style3-slug}.html
```

### Filename slug rules

- Prompt slug: `"minimalist todo list"` → `todo-list` (strip common words, lowercase, hyphenate, max 40 chars)
- Style slug: `"Tactile Risograph Press"` → `risograph-press`
- Full filename: `01-todo-list-risograph-press.html`

### Step 4: Write the top-level manifest

Write `$DIR/manifest.json` so `--vary` and `--continue` can find the session later. Schema:

```json
{
  "prompt": "minimalist todo list",
  "created": "2026-05-21",
  "url": "http://localhost:62477",
  "session_dir": "/abs/path/.prototype/.claude/preview/12345-1779000000",
  "screen_dir": "/abs/path/.prototype/.claude/preview/12345-1779000000/content",
  "state_dir":  "/abs/path/.prototype/.claude/preview/12345-1779000000/state",
  "artifacts": [
    {
      "position": 1,
      "style": "Tactile Risograph Press",
      "file": "01-todo-list-risograph-press.html",
      "abs_path": "/abs/path/.../content/01-todo-list-risograph-press.html"
    },
    {
      "position": 2,
      "style": "Kinetic Wireframe Suspension",
      "file": "02-todo-list-wireframe-suspension.html",
      "abs_path": "/abs/path/.../content/02-todo-list-wireframe-suspension.html"
    },
    {
      "position": 3,
      "style": "Obsidian Facet Grid",
      "file": "03-todo-list-obsidian-grid.html",
      "abs_path": "/abs/path/.../content/03-todo-list-obsidian-grid.html"
    }
  ]
}
```

If `$DIR/manifest.json` already exists, overwrite it — only one live session at a time per `$DIR`.

### Step 5: Write the gallery fragment LAST

Write this as `$screen_dir/99-gallery.html` AFTER all 3 artifact files. The server serves the newest screen at `GET /`, so the `99-` prefix + later-write order guarantees the gallery is the first thing the user sees.

```html
<div class="flex h-screen bg-white">
  <aside class="w-72 border-r border-gray-200 p-4 space-y-2 overflow-y-auto">
    <h2 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">{{prompt}}</h2>
    <button class="variant-btn block w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 text-sm border border-gray-200"
            data-variant="01" data-src="/files/{{file1}}">
      <span class="font-medium">01</span> &mdash; {{style1}}
    </button>
    <button class="variant-btn block w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 text-sm border border-gray-200"
            data-variant="02" data-src="/files/{{file2}}">
      <span class="font-medium">02</span> &mdash; {{style2}}
    </button>
    <button class="variant-btn block w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 text-sm border border-gray-200"
            data-variant="03" data-src="/files/{{file3}}">
      <span class="font-medium">03</span> &mdash; {{style3}}
    </button>
    <p class="text-xs text-gray-400 mt-4">Your click is logged to <code>events.jsonl</code>.</p>
  </aside>
  <main class="flex-1">
    <iframe id="canvas" class="w-full h-full border-0" src="/files/{{file1}}" title="Preview"></iframe>
  </main>
</div>
<script>
  // Self-contained iframe swap. The gallery helper (auto-injected by the
  // server) also captures the click and ships it to events.jsonl; both
  // listeners run independently.
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.variant-btn[data-variant]');
    if (!btn) return;
    const src = btn.dataset.src;
    if (src) document.getElementById('canvas').src = src;
    document.querySelectorAll('.variant-btn').forEach(b =>
      b.classList.remove('bg-gray-100', 'border-blue-500'));
    btn.classList.add('bg-gray-100', 'border-blue-500');
  });
</script>
```

Substitute `{{prompt}}`, `{{file1-3}}`, `{{style1-3}}` with the actual values. Keep the relative `/files/<filename>` paths — that route is served by the arkhe-preview server with a path-traversal guard scoped to `$screen_dir`.

### Step 6: Print the terminal summary

```
Prototype live preview ready.
  URL:        http://localhost:{{port}}
  Variants:   {{screen_dir}}
  Picks log:  {{state_dir}}/events.jsonl

  01 — {{style1}}
  02 — {{style2}}
  03 — {{style3}}

Click a variant. When you reply I'll read your pick from events.jsonl.
  /prototype --vary N        — generate 3 variations of variant N
  /prototype --continue      — re-read the latest pick
```

End the turn. Do not block. Do not poll.

---

## Next-Turn Pick Capture

The skill is turn-based — Phase 3 ends, the user picks at their leisure, and the pick is read on a later turn. There are two entry points.

### Explicit: `/prototype --continue`

1. Resolve `$DIR` (default `.prototype/`, or `--dir` value).
2. Read `$DIR/manifest.json`. If missing, tell the user no session exists in this directory and stop.
3. Read `$state_dir/events.jsonl` (one JSON object per line). If missing or empty, the user didn't click — report "no pick yet" and stop.
4. Filter for events where `action === "select-variant"`. The relevant field is `payload.variant` (e.g. `"01"`, `"02"`, `"03"`).
5. Take the **most recent** matching event (last line that matches, by file order). Resolve the variant code to the artifact via `manifest.artifacts`.
6. Report:
   ```
   You picked variant {{position}} — {{style}}
     File: {{abs_path}}
   
   Next:
     /prototype --vary {{position}}     — explore variations of this pick
     /design-intent implement {{abs_path}}
   ```

### Implicit: agent reads on the user's next message

If the previous skill turn ran `/prototype` and the user's next message is conversational ("ok", "I like the third one", "what did I pick?"), before responding:

1. Check whether `<cwd>/.prototype/manifest.json` exists (or whatever `--dir` was used).
2. If yes, read `events.jsonl` and apply the same select-variant resolution as `--continue`.
3. Merge the structured pick with the user's text. The user's text wins on disagreement; events.jsonl provides the structured payload (position, style, abs_path).

If `events.jsonl` is empty or absent, the user didn't click. Use their terminal text alone.

### Event schema

The gallery helper emits (server enriches with `timestamp` + `clientId`):

```json
{
  "type": "click",
  "action": "select-variant",
  "payload": {"variant": "02"},
  "text": "02 — Kinetic Wireframe Suspension",
  "id": null,
  "timestamp": "2026-05-21T13:20:30.010Z",
  "clientId": "b33c01707b2a048d"
}
```

The user may click multiple variants — that's exploration. The last `select-variant` event is the pick.

---

## Variation Workflow

When user passes `--vary N`:

### Step 0: Verify the live session is still alive

The session that wrote the original artifacts may have shut down between Phase 3 and now — the owner-pid watchdog exits the server when the agent process disappears, and the server auto-exits after 30 minutes of idle. If the server is dead, writing variation files succeeds but the browser never reloads (silent failure).

Run a status check before writing any files:

```bash
arkhe-preview status "$(python3 -c 'import json;print(json.load(open(".prototype/manifest.json"))["session_dir"])')"
```

- If `running: true` — proceed to Step 1, write variations into the existing `screen_dir`.
- If `running: false` — restart the server with the same `--project-dir`, copy the existing artifacts into the new `screen_dir`, write a new `manifest.json`, then proceed:
  ```bash
  PLUGIN_ROOT=$(dirname "$(dirname "$(which arkhe-preview)")")
  EX="$PLUGIN_ROOT/skills/browser-companion/examples/gallery"
  arkhe-preview start \
    --project-dir "$DIR" \
    --frame-template "$EX/frame-template.html" \
    --helper       "$EX/helper.js"
  # Copy artifacts named in manifest.artifacts[].file from the old screen_dir
  # into the new screen_dir. Rewrite manifest.json with the new session_dir /
  # screen_dir / state_dir / url.
  ```
  Then proceed to Step 1 using the *new* `screen_dir`.

### Step 1: Read manifest

Read `$DIR/manifest.json` to find the Nth artifact (`artifacts[N-1]`). If `manifest.json` is missing, glob `$DIR/.claude/preview/*/content/0N-*.html` and infer the original prompt from the filename (best-effort fallback).

### Step 2: Read existing artifact

Read the HTML at `artifacts[N-1].abs_path`. Understand its layout, palette, typography, structural approach.

### Step 3: Generate 3 variations

For each variation:
- Invent a unique design persona name based on a NEW physical metaphor (different from the original and from each other)
- Let the metaphor drive every CSS choice
- Generate a complete, self-contained HTML page

The goal is radical divergence. If the original was dark and angular, a variation might be light and organic. If it used heavy borders, a variation might use no borders.

### Step 4: Write variation files into screen_dir

- Files: `{original-slug}-var-1.html`, `-var-2.html`, `-var-3.html` (in `$screen_dir`)
- Rewrite `99-gallery.html` to point its 3 sidebar buttons at the new variations (use the same gallery fragment template; replace the `data-src` paths and labels)
- Update `manifest.json` with a `variations` array on the varied artifact:
  ```json
  {
    "position": 2,
    "style": "Kinetic Wireframe Suspension",
    "file": "02-todo-list-wireframe-suspension.html",
    "variations": [
      {"file": "todo-list-wireframe-suspension-var-1.html", "style": "Volcanic Ember Fracture"},
      {"file": "todo-list-wireframe-suspension-var-2.html", "style": "Folded Vellum Sheets"},
      {"file": "todo-list-wireframe-suspension-var-3.html", "style": "Frost Crystal Lattice"}
    ]
  }
  ```

The watcher detects the new files and broadcasts a reload; the user's browser pulls the updated gallery automatically.

---

## Integration with Design Intent

After prototyping, users can feed their preferred artifact into the full design-intent workflow:

1. **Pick a favorite**: User clicks a variant in the live gallery. The pick lands in `events.jsonl`.
2. **Resolve the pick**: Run `/prototype --continue` to get the absolute path of the picked artifact.
3. **Run `/design-intent`**: Reference the artifact path as the visual reference:
   ```
   /design-intent implement the UI from <abs_path-from-continue>
   ```
4. **The design-intent-specialist skill** will:
   - Analyze the HTML for layout, colors, typography, spacing
   - Check existing design intent patterns for conflicts
   - Implement using the project's actual component library and design system
5. **Save patterns**: Run `/save-patterns` to capture any new design decisions

This creates a pipeline: **rapid exploration** (prototype + live gallery) → **production implementation** (design-intent).
