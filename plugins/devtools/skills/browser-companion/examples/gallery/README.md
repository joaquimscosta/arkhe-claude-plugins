# Gallery example

A reference UI flavor for variant browsing: present the user with a sidebar of clickable variants and a main canvas that swaps to whichever they pick. Adapted from the tailwindplus-catalog gallery flow.

Use this when your skill needs to show side-by-side variants (component flavors, layout options, design directions) and capture which one the user chooses.

## Files

- `frame-template.html` — Tailwind CSS + Inter font frame. No fixed layout; your fragment provides the sidebar+canvas structure.
- `helper.js` — Captures clicks on `.variant-btn[data-variant]` elements and emits `{action: 'select-variant', payload: {variant}}` events.

## Invocation

```bash
PLUGIN_ROOT=$(dirname "$(dirname "$(which arkhe-preview)")")
EX="$PLUGIN_ROOT/skills/browser-companion/examples/gallery"

arkhe-preview start \
  --project-dir "$(pwd)" \
  --frame-template "$EX/frame-template.html" \
  --helper "$EX/helper.js"
```

## HTML pattern your agent writes

```html
<div class="flex h-full">
  <aside class="w-64 border-r border-gray-200 p-4 space-y-2 overflow-y-auto">
    <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Variants</h2>
    <button class="variant-btn block w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 text-sm" data-variant="hero-1">Hero — minimal</button>
    <button class="variant-btn block w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 text-sm" data-variant="hero-2">Hero — split image</button>
    <button class="variant-btn block w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 text-sm" data-variant="hero-3">Hero — centered</button>
  </aside>
  <main class="flex-1 p-6 overflow-y-auto">
    <p class="text-gray-500">Pick a variant on the left to preview.</p>
  </main>
</div>
```

The helper does NOT swap content in the main pane on its own — that's an agent-side concern. Your agent writes the chosen variant's HTML to `content/` as a new fragment, which triggers a server reload and pushes the variant to the browser.

## Event shape

```json
{
  "timestamp": "2026-05-21T...",
  "clientId": "abc123",
  "type": "click",
  "action": "select-variant",
  "payload": {"variant": "hero-1"},
  "text": "Hero — minimal",
  "id": null
}
```

## Notes on Tailwind CDN

The frame loads `cdn.tailwindcss.com`. This is fine for previews but not production. It also means custom Tailwind v4 `@theme {...}` directives in your fragments won't be processed — CDN Tailwind is v3-ish. If you need full v4 features, build your own frame with a precompiled CSS file.

## Attribution

Adapted from `internal-repos/tailwindplus/skills/tailwindplus-catalog/scripts/server/`. The original is an internal port of the superpowers brainstorm server (MIT, Jesse Vincent 2025), adapted for the Tailwind Plus catalog tooling.
