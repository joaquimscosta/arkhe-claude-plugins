# browser-companion — Workflow & Protocol

Detailed contract documentation for `arkhe-preview` and the server it launches.

## CLI Contract (semver-bound from devtools v2.4.0)

### `arkhe-preview start [options]`

| Option | Type | Default | Effect |
|---|---|---|---|
| `--project-dir <path>` | path | `/tmp/arkhe-preview-<id>/` | Session lives at `<path>/.claude/preview/<id>/` |
| `--frame-template <path>` | path | `<skill>/scripts/frame-template.html` | Override default frame |
| `--helper <path>` | path | `<skill>/scripts/helper.js` | Override default helper |
| `--port <N>` | int | random in 49152-65535 | Pin a specific port |
| `--host <H>` | string | `127.0.0.1` | Bind interface |
| `--url-host <H>` | string | matches `--host` | Hostname shown in URL JSON |
| `--owner-pid <PID>` | int or 0 | parent-of-parent | Watchdog target; `0` disables |
| `--foreground` | flag | off | Run in current shell (no `nohup`) |
| `--background` | flag | off | Force background mode |

**stdout (success):** One JSON line:
```json
{"type":"server-started","port":54123,"host":"127.0.0.1","url_host":"localhost","url":"http://localhost:54123","screen_dir":"…/content","state_dir":"…/state","session_dir":"…","pid":12345}
```

**stdout (error):** `{"error": "…"}` to stderr, exit 1 (user error) or 2 (server crashed).

### `arkhe-preview stop <session-dir>`

Sends SIGTERM, waits up to 2s, escalates to SIGKILL. Removes `.pid` and `.log` files. Removes the whole session directory if under `/tmp/*`; keeps it otherwise so content can be reviewed.

**stdout:** `{"status":"stopped"}` | `{"status":"not_running"}` | `{"status":"failed", "error":"…"}` (exit 2)

### `arkhe-preview status <session-dir>`

Reads `state/server.pid` and `state/server-info`. Probes liveness with `kill -0`. Always exits 0.

**stdout:** `{"running":bool, "pid":int|null, "url":string|null}`

## Session Layout

```
<base>/.claude/preview/<session-id>/        ← project-dir mode
/tmp/arkhe-preview-<session-id>/            ← /tmp mode (default)
├── content/                                ← Agent writes HTML fragments here
├── state/
│   ├── server-info                         ← Same JSON as `start` stdout
│   ├── events.jsonl                        ← Append-only browser events
│   ├── server.pid                          ← Plain integer
│   ├── server.log                          ← Server stdout/stderr (background mode)
│   └── server-stopped                      ← Final reason on clean shutdown
└── logs/                                   ← Reserved for future use
```

Session IDs are `<PPID>-<unix-timestamp>`. Reasonably unique for hand-driven sessions; consumers needing strict uniqueness should provide their own `--project-dir` per run.

## Event Schema

Every WS message from a browser client is appended to `events.jsonl` as one JSON object per line.

**Server-injected fields** (added only if not already present):
- `timestamp` — ISO 8601 UTC, e.g. `"2026-05-21T12:34:56.789Z"`
- `clientId` — random 16-hex-char per-WS-connection ID

**Default helper output** (from `scripts/helper.js`):
```json
{
  "timestamp": "2026-05-21T12:34:56.789Z",
  "clientId": "a1b2c3d4e5f6g7h8",
  "type": "click",
  "action": "<value of [data-event] attr>",
  "payload": {"<other-data-attr>": "value", ...},
  "text": "<element text, trimmed to 200 chars>",
  "id": "<DOM id or null>"
}
```

**Custom helpers** can emit any JSON they want via `window.arkhePreview.send({...})`. The server persists verbatim plus the two injected fields.

## WebSocket Protocol

Server-to-browser:
- `{"type":"reload"}` — Reload page (broadcast on every new/updated HTML file in `content/`)

Browser-to-server:
- Any JSON object — persisted to `events.jsonl`

Wire details (RFC 6455):
- Server is unmasked (per spec for server→client)
- Client frames MUST be masked (server rejects unmasked frames)
- Frame sizes: 7-bit, 16-bit (≤65535), and 64-bit length all supported
- TEXT (0x01), CLOSE (0x08), PING (0x09), PONG (0x0A) opcodes handled

## Frame Template Contract

Required:
- A complete HTML document (`<!DOCTYPE html>`-rooted)
- Contains either `<!-- FRAGMENT -->` (canonical) or `<!-- CONTENT -->` (legacy alias) as a marker comment

On each `GET /` request, the server:
1. Reads the newest `.html` file in `content/`
2. If the file is a *fragment* (no `<!DOCTYPE>` / `<html>` prefix), wraps it by replacing the marker comment with the fragment body
3. If the file is a full document, serves it as-is (frame is bypassed)
4. Injects the helper as `<script>...</script>` before `</body>` (or appended if no closing body tag)

## Helper Contract

The helper is plain browser-side JavaScript injected inline on every page load. The server reads it from disk on startup; changes require a server restart.

Minimum behaviors a helper SHOULD implement:
1. Connect a WebSocket to `ws://<window.location.host>`
2. React to `{type:'reload'}` by reloading the page
3. Surface a `window.arkhePreview.send(event)` (or equivalent) for programmatic sends

The default helper additionally captures clicks on `[data-event]` elements automatically.

## Lifecycle

```
start-server.sh
  ↓ writes state/server.pid
  ↓ nohup node server.cjs
server.cjs
  ↓ creates content/ and state/
  ↓ fs.watch(content/) → on .html change → broadcast {reload}
  ↓ listen on random port
  ↓ writes state/server-info
  ↓ every 60s: check owner PID + idle timeout

  ── Shutdown triggers ─────────────────────────────
   • SIGTERM/SIGINT (stop-server.sh sends SIGTERM)
   • PREVIEW_OWNER_PID disappears (5s poll)
   • 30 minutes idle (no WS activity, no new content files)
  ──────────────────────────────────────────────────

  ↓ shutdown(reason)
  ↓ writes state/server-stopped
  ↓ unlinks state/server-info
  ↓ closes server, process.exit(0)
```

## Owner-PID Watchdog

The watchdog exists to prevent orphaned background servers when the parent agent process exits. Default behavior:

- `start-server.sh` resolves the owner as `ppid(ppid(self))` — i.e., the grandparent of the script. The immediate parent (`$PPID`) is an ephemeral shell that dies as soon as the script returns; its parent is typically the long-lived agent process.
- If the watchdog target dies, server shuts down within ~5 seconds.
- If the watchdog target is **already dead at startup** (common in WSL, Tailscale SSH, nested shells), `server.cjs` logs `owner-pid-invalid` and disables the watchdog — falls back to the 30-minute idle timer.
- Pass `--owner-pid 0` to disable the watchdog entirely. Useful for long-lived hands-on debugging sessions.

## Path Resolution (Cross-Plugin)

When `bin/arkhe-preview` is invoked by a skill in *any* plugin:

```bash
src="${BASH_SOURCE[0]}"               # /path/to/devtools/bin/arkhe-preview
[[ -L "$src" ]] && src="$(readlink "$src")"
bin_dir="$(cd "$(dirname "$src")" && pwd)"
plugin_root="$(cd "$bin_dir/.." && pwd)"
script_dir="$plugin_root/skills/browser-companion/scripts"
```

This works regardless of `cwd` at invocation time (smoke-tested in `arkhe/specs/005-browser-companion/smoke-test-log.md`). Symlinked installs are unwrapped one level — sufficient for marketplace installs.

## Environment Variables (server.cjs)

For consumers invoking `node server.cjs` directly (e.g., custom orchestrators):

| Variable | Purpose | Default |
|---|---|---|
| `PREVIEW_DIR` | Session dir (parent of `content/` and `state/`) | `/tmp/arkhe-preview` |
| `PREVIEW_PORT` | Listen port | random 49152-65535 |
| `PREVIEW_HOST` | Bind interface | `127.0.0.1` |
| `PREVIEW_URL_HOST` | Hostname in URL JSON | matches `PREVIEW_HOST` |
| `PREVIEW_FRAME_TEMPLATE` | Absolute path to frame HTML | `<__dirname>/frame-template.html` |
| `PREVIEW_HELPER` | Absolute path to helper JS | `<__dirname>/helper.js` |
| `PREVIEW_OWNER_PID` | Watchdog target | unset (no watchdog) |

`start-server.sh` is the recommended entry — it handles port retry, foreground heuristics, and PID-file lifecycle. Bare `node server.cjs` is for direct integration only.

## Security Notes

- Default bind is `127.0.0.1` — not reachable from other hosts on the network
- Path-traversal denied: `GET /files/<name>` resolves only files under `content/`; anything that escapes via `..` returns 403
- No CSRF protection, no auth — local-dev only
- Frame template is rendered as raw HTML — do not point at untrusted templates

## Attribution

The server code (`server.cjs`, `start-server.sh`, `stop-server.sh`, frame/helper structure) is derived from Jesse Vincent's [superpowers](https://github.com/obra/superpowers) project, released under the MIT license. Generalizations made for this fork:

- Env var prefix `BRAINSTORM_*` → `PREVIEW_*`
- Configurable frame template and helper paths (formerly hardcoded siblings)
- Persist *all* WS events to `events.jsonl` (dropped the `if (event.choice)` filter)
- Filename `events` → `events.jsonl` for clarity
- No "wipe events on new screen" behavior (was brainstorm-specific)
- Added `status-server.sh` and SIGTERM/SIGINT handlers for clean `stop-server.sh` integration

License terms (MIT, full text in `external-repos/superpowers/LICENSE`):

> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so [...]
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND [...]

Modifications by Arkhe (Joaquim Costa, 2026) are also MIT-licensed.
