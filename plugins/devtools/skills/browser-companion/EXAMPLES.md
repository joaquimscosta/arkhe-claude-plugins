# browser-companion — Examples

End-to-end walkthroughs of `arkhe-preview` in action. All examples assume the devtools plugin is enabled (`/plugin install devtools@arkhe-claude-plugins` + `/reload-plugins`), which puts `arkhe-preview` on PATH.

## Example 1: Hello fragment with default frame

The simplest possible flow. No custom frame, no custom helper.

```bash
# 1. Start a server scoped to the current project.
JSON=$(arkhe-preview start --project-dir "$(pwd)")
echo "$JSON"
# → {"type":"server-started","port":54123,"url":"http://localhost:54123","screen_dir":".../<id>/content","state_dir":".../<id>/state","session_dir":".../<id>","pid":12345}

# 2. Extract paths and tell the user.
SCREEN=$(echo "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['screen_dir'])")
STATE=$(echo  "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['state_dir'])")
SESSION=$(echo "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['session_dir'])")
URL=$(echo "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['url'])")
echo "→ Open $URL in your browser."

# 3. Write a fragment. Browser auto-reloads within 100ms.
cat > "$SCREEN/hello.html" <<'EOF'
<h2>Hello, world</h2>
<p>This page is wrapped in the default frame template.</p>
<button data-event="ok" data-source="hello">OK</button>
EOF

# 4. Wait for the user to click. Read what they did.
sleep 5
cat "$STATE/events.jsonl"
# → {"timestamp":"2026-05-21T...","clientId":"...","type":"click","action":"ok",
#    "payload":{"source":"hello"},"text":"OK","id":null}

# 5. Stop the server when done.
arkhe-preview stop "$SESSION"
```

## Example 2: Brainstorm-style multi-select with custom frame + helper

Use the bundled brainstorm example (lives in `examples/brainstorm/` inside the skill). Mirrors the original superpowers brainstorming flow.

```bash
PLUGIN_ROOT=$(dirname "$(dirname "$(which arkhe-preview)")")
BRAINSTORM_DIR="$PLUGIN_ROOT/skills/browser-companion/examples/brainstorm"

JSON=$(arkhe-preview start \
  --project-dir "$(pwd)" \
  --frame-template "$BRAINSTORM_DIR/frame-template.html" \
  --helper "$BRAINSTORM_DIR/helper.js")
SCREEN=$(echo "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['screen_dir'])")
STATE=$(echo  "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['state_dir'])")
SESSION=$(echo "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['session_dir'])")

# Write a multi-choice screen
cat > "$SCREEN/choices.html" <<'EOF'
<h2>Pick a layout direction</h2>
<div class="options" data-multiselect>
  <div class="option" data-choice="grid" data-event="choice" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content"><h3>Grid layout</h3><p>3-column responsive cards.</p></div>
  </div>
  <div class="option" data-choice="list" data-event="choice" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content"><h3>List layout</h3><p>Vertical stack with thumbnails.</p></div>
  </div>
  <div class="option" data-choice="kanban" data-event="choice" onclick="toggleSelect(this)">
    <div class="letter">C</div>
    <div class="content"><h3>Kanban</h3><p>Drag-and-drop columns.</p></div>
  </div>
</div>
EOF

# Wait, read events
tail -f "$STATE/events.jsonl" &
sleep 30
kill %1
arkhe-preview stop "$SESSION"
```

The brainstorm helper adds an indicator bar at the bottom of the page and tracks multi-select state.

## Example 3: Gallery-style variant browsing

Mirrors the tailwindplus-catalog gallery pattern.

```bash
PLUGIN_ROOT=$(dirname "$(dirname "$(which arkhe-preview)")")
GALLERY_DIR="$PLUGIN_ROOT/skills/browser-companion/examples/gallery"

JSON=$(arkhe-preview start \
  --project-dir "$(pwd)" \
  --frame-template "$GALLERY_DIR/frame-template.html" \
  --helper "$GALLERY_DIR/helper.js")
SCREEN=$(echo "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['screen_dir'])")

# Write a gallery page
cat > "$SCREEN/gallery.html" <<'EOF'
<aside class="variants">
  <button class="variant-btn" data-variant="hero-1" data-event="select-variant">Hero — minimal</button>
  <button class="variant-btn" data-variant="hero-2" data-event="select-variant">Hero — split</button>
  <button class="variant-btn" data-variant="hero-3" data-event="select-variant">Hero — centered</button>
</aside>
<main class="canvas">
  <p>Select a variant on the left to preview.</p>
</main>
EOF
```

The gallery helper emits `{type:"click", action:"select-variant", payload:{variant:"hero-1"}, ...}`.

## Example 4: Custom frame + custom helper (your own UI)

Bring your own.

```bash
# 1. Write your frame template — must contain <!-- FRAGMENT --> placeholder.
cat > /tmp/my-frame.html <<'EOF'
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>My UI</title>
<style>body { font-family: monospace; background: #111; color: #eee; }</style>
</head>
<body>
  <h1>Custom preview</h1>
  <main><!-- FRAGMENT --></main>
</body></html>
EOF

# 2. Write your helper — must connect WS, handle reload.
cat > /tmp/my-helper.js <<'EOF'
const ws = new WebSocket('ws://' + location.host);
ws.onmessage = (m) => { if (JSON.parse(m.data).type === 'reload') location.reload(); };
window.arkhePreview = { send: (e) => ws.send(JSON.stringify(e)) };
EOF

# 3. Start with your bring-your-own UI.
arkhe-preview start --project-dir "$PWD" \
  --frame-template /tmp/my-frame.html \
  --helper /tmp/my-helper.js
```

## Example 5: Tailing events.jsonl as the user interacts

Pattern for waiting on a specific user choice.

```bash
JSON=$(arkhe-preview start --project-dir "$PWD")
EVENTS=$(echo "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['state_dir']+'/events.jsonl')")
SCREEN=$(echo "$JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['screen_dir'])")

# Write a screen
echo '<button data-event="approve">Approve</button> <button data-event="reject">Reject</button>' \
  > "$SCREEN/decision.html"

# Block until the user clicks something (events.jsonl is append-only).
while [[ ! -s "$EVENTS" ]]; do sleep 0.5; done
LATEST=$(tail -n 1 "$EVENTS")
ACTION=$(echo "$LATEST" | python3 -c "import json,sys;print(json.load(sys.stdin)['action'])")
echo "User chose: $ACTION"
```

## Example 6: Two parallel sessions

Each `start` invocation creates a fresh session dir + port, so multiple servers coexist.

```bash
A=$(arkhe-preview start --project-dir "$PWD" --owner-pid 0)
B=$(arkhe-preview start --project-dir "$PWD" --owner-pid 0)
echo "$A"  # different port/session_dir from $B
echo "$B"

# Stop them independently:
arkhe-preview stop "$(echo "$A" | python3 -c 'import json,sys;print(json.load(sys.stdin)["session_dir"])')"
arkhe-preview stop "$(echo "$B" | python3 -c 'import json,sys;print(json.load(sys.stdin)["session_dir"])')"
```

## Example 7: Pinning a port (e.g., for an external tool)

```bash
arkhe-preview start --project-dir "$PWD" --port 8080
# If 8080 is in use, this fails with {"error":"Server failed to start..."}.
# Pick a different port or omit --port to let the server choose.
```
