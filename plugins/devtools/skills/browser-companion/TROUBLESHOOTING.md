# browser-companion — Troubleshooting

Common issues and fixes for `arkhe-preview`.

## `arkhe-preview: command not found`

**Symptom:** The bin wrapper isn't on PATH.

**Causes & fixes:**

1. **Devtools plugin not enabled** — run `/plugin install devtools@arkhe-claude-plugins` and then `/reload-plugins`.
2. **PATH not refreshed after install** — run `/reload-plugins`. Claude Code re-scans plugin `bin/` directories on reload, not automatically on every shell.
3. **Plugin install failed** — check `/plugin` output for errors. Try `/plugin uninstall devtools` followed by `/plugin install devtools@arkhe-claude-plugins`.
4. **Multiple devtools versions installed** — `which -a arkhe-preview` will show duplicates. Uninstall any stale copy.

**Quick verification:**

```bash
command -v arkhe-preview   # Should print a path under .../plugins/devtools/bin/
which -a arkhe-preview     # Should print exactly one path
```

## `Server failed to start within 5 seconds`

**Symptom:** `start-server.sh` exits 1 with the timeout error after `nohup`ing the server.

**Causes & fixes:**

1. **Port collision** — every port in the random range may be in use (rare, but possible if many servers are running). Pass `--port <N>` to pin a specific known-free port, or kill stale processes:
   ```bash
   pgrep -fa 'server.cjs' | head
   ```
2. **Process reaper killing background `nohup`'d processes** — common under Codex CI, Windows Git Bash, MSYS. The script auto-detects these and switches to foreground mode, but if you're somewhere else with similar behavior, pass `--foreground` explicitly.
3. **Node.js not installed** — verify with `command -v node`. Install Node 18+ (e.g., via `nvm`, `fnm`, or your system package manager).
4. **Node crashed on startup** — read the server log:
   ```bash
   cat <session-dir>/state/server.log
   ```

## Server starts but browser shows `Connection refused`

**Symptom:** `arkhe-preview start` succeeds, prints a URL, but opening the URL fails.

**Causes & fixes:**

1. **Wrong host** — the default bind is `127.0.0.1`, so requests from other hosts on the network will fail. Use `--host 0.0.0.0 --url-host <your-LAN-IP>` to expose externally (note: no auth — local-trust only).
2. **VPN / proxy rewriting localhost** — try the raw IP form: `curl http://127.0.0.1:<port>/` instead of `localhost`.
3. **Server crashed after the ready message** — check `state/server.log` and `state/server-stopped`. The latter contains the shutdown reason if it died cleanly.

## Server keeps stopping unexpectedly

**Symptom:** Server is running, then dies a few seconds or minutes later. `state/server-stopped` contains a reason.

**Causes & fixes:**

| `server-stopped` reason | Cause | Fix |
|---|---|---|
| `owner process exited` | Watchdog target died. PPID resolution is fragile under nested shells, WSL, Tailscale SSH, etc. | Pass `--owner-pid 0` to disable the watchdog. Idle timeout (30 min) still applies. |
| `idle timeout` | No WS activity for 30 minutes. | Reload the browser to re-establish WS, or just restart the server. |
| `SIGTERM` / `SIGINT` | Something explicitly sent it (likely `stop-server.sh`). | Expected — that's the graceful path. |

## Owner-PID resolution is wrong (Tailscale SSH, WSL, nested shells)

**Symptom:** Server logs `owner-pid-invalid` at startup, or shuts down with `owner process exited` even though the agent is still running.

**Cause:** `start-server.sh` resolves the owner as `ppid(ppid(self))`. In some environments — Tailscale SSH, WSL, Docker shells, or anything that nests shells unusually — that target is wrong.

**Fix:** Pass `--owner-pid <PID>` with the agent's actual PID. Or pass `--owner-pid 0` to disable the watchdog and rely on the 30-minute idle timeout.

## Frame template not loading

**Symptom:** Browser shows the default frame instead of your custom one. Or `start` errors with `Frame template not found`.

**Causes & fixes:**

1. **Path is relative but cwd is wrong** — `--frame-template ./my-frame.html` is resolved relative to `cwd` when `start-server.sh` runs. The script does normalize to absolute, but if the relative path doesn't exist in `cwd`, you get a not-found error. Prefer absolute paths.
2. **Missing placeholder** — the template MUST contain `<!-- FRAGMENT -->` (canonical) or `<!-- CONTENT -->` (legacy alias). Without it, the agent's fragment has no insertion point and the page shows the empty frame.
3. **File permissions** — `start-server.sh` reads the template; it must be world-readable (`chmod a+r my-frame.html`).

## Helper script not running in the browser

**Symptom:** Page loads but clicks don't appear in `events.jsonl`; no auto-reload on new fragments.

**Causes & fixes:**

1. **Helper has a syntax error** — open browser DevTools → Console. JS errors will surface there. The helper is injected inline, so the line number references the injected `<script>` block.
2. **Custom helper doesn't connect a WebSocket** — minimum behavior the helper must implement is a WebSocket connection to `ws://<location.host>` and a reload handler. Look at `scripts/helper.js` for the reference shape.
3. **Page is a *full document* (has `<!DOCTYPE>` or `<html>`)** — the server *still* injects the helper script before `</body>` when the doc ends with a body tag, but if your full document lacks a closing `</body>`, the helper is appended after the existing markup. Verify the helper appears at the bottom of the served HTML:
   ```bash
   curl -s http://localhost:<port>/ | tail -5
   ```

## Events not being persisted

**Symptom:** Browser shows clicks fire (visible in DevTools network → WS frames), but `events.jsonl` stays empty.

**Causes & fixes:**

1. **WS message isn't valid JSON** — the server requires JSON-parseable messages. Plaintext frames are logged to stderr (visible in `state/server.log`) and dropped.
2. **Server doesn't have write permission on state/** — unusual, but happens if the session dir was created with restrictive umask. Check with `ls -la <session-dir>/state/` and `chmod` if needed.
3. **Stale tail** — if you're using `tail -f`, make sure you're looking at the *current* session's events.jsonl, not an older session. The session dir always has a unique `<PPID>-<timestamp>` suffix.

## Port already in use (`EADDRINUSE`)

**Symptom:** `start` retries 3 ports and then fails.

**Causes & fixes:**

1. **Another arkhe-preview is running** — list them: `pgrep -fa 'server.cjs'`. Stop with `arkhe-preview stop <session-dir>` (find session dirs under `/tmp/arkhe-preview-*` or `<project>/.claude/preview/*`).
2. **Some other dev server is on the port** — explicit `--port <N>` lets you pick around it.
3. **Recent crash left a TIME_WAIT socket** — wait ~60 seconds or pick a different port.

## Path traversal blocked (403)

**Symptom:** Browser requests like `/files/../etc/passwd` return 403.

**This is intentional.** The server resolves `/files/<name>` against `content/` and rejects any path that escapes it. If you legitimately need to serve files from outside the content dir, the server isn't the right tool — write them into `content/` first, or serve them via a different mechanism.

## `node: command not found`

**Symptom:** `start-server.sh` invokes `node server.cjs` but Node isn't installed.

**Fix:** Install Node.js 18 or later. The skill explicitly targets `node` on PATH; it does not bundle a runtime. Recommended installers: `nvm`, `fnm`, or your OS package manager.

```bash
command -v node && node --version  # should be ≥ v18.0.0
```

## Cross-references

- Full protocol details: [WORKFLOW.md](WORKFLOW.md)
- End-to-end examples: [EXAMPLES.md](EXAMPLES.md)
- Inherited upstream behavior: [WORKFLOW.md > Attribution](WORKFLOW.md#attribution)
