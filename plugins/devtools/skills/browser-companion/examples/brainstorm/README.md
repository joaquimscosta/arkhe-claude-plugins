# Brainstorm example

A reference UI flavor for agent-driven brainstorming: multi-choice option lists, card mockups, and a bottom indicator bar that tracks the user's selection state.

Use this when your skill needs to ask the user to pick between options (A/B/C card layouts, comparison mockups, multi-select tags) and you want a polished UI without writing your own frame template.

## Files

- `frame-template.html` — Header + scrollable content area + indicator bar. Provides CSS classes `.options`, `.option`, `.cards`, `.card`, `.selected`.
- `helper.js` — Captures `[data-choice]` clicks, exposes `toggleSelect(el)` for HTML fragments to use as `onclick` handlers, updates `#indicator-text` on selection changes.

## Invocation

```bash
# Resolve the skill's examples dir
PLUGIN_ROOT=$(dirname "$(dirname "$(which arkhe-preview)")")
EX="$PLUGIN_ROOT/skills/browser-companion/examples/brainstorm"

arkhe-preview start \
  --project-dir "$(pwd)" \
  --frame-template "$EX/frame-template.html" \
  --helper "$EX/helper.js"
```

## HTML pattern your agent writes

```html
<h2>Pick a hero layout</h2>
<div class="options" data-multiselect>
  <div class="option" data-choice="minimal" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Minimal</h3><p>Just a headline and a CTA.</p>
    </div>
  </div>
  <div class="option" data-choice="split" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>Split image</h3><p>Headline left, image right.</p>
    </div>
  </div>
</div>
```

Notes:
- Add `data-multiselect` to the container for multi-select; omit it for single-select (auto-deselects siblings).
- `onclick="toggleSelect(this)"` is provided by `helper.js` — no manual wiring needed.
- The `data-choice` value is what arrives in `events.jsonl` as the `choice` field.

## Event shape

```json
{
  "timestamp": "2026-05-21T...",
  "clientId": "abc123",
  "type": "click",
  "action": "choice",
  "choice": "minimal",
  "text": "Minimal Just a headline and a CTA.",
  "id": null
}
```

Tail `state/events.jsonl` to observe selections in real time.

## Attribution

Inherited from Jesse Vincent's superpowers project (`external-repos/superpowers/skills/brainstorming/scripts/`), MIT-licensed.
