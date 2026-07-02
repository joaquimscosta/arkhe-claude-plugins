# Prototype — Troubleshooting

## Common Issues

### `arkhe-preview: command not found`

**Symptom**: Phase 3 fails because `arkhe-preview` is not on `PATH`.

**Cause**: The devtools plugin (which ships the `arkhe-preview` CLI) is not installed.

**Solution**:
```bash
/plugin install devtools@arkhe-claude-plugins
```
Then retry `/prototype`. The CLI lives at `plugins/devtools/bin/arkhe-preview`; Claude Code adds plugin `bin/` directories to `PATH` automatically while the plugin is enabled.

---

### Server failed to start within 5 seconds

**Symptom**: `arkhe-preview start` exits non-zero with `{"error": "Server failed to start within 5 seconds"}` or `{"error": "Server started but was killed. Retry with --foreground."}`.

**Causes**:
- Port collision on the random port the server picked
- Background-process reaping (Codex CI, Windows/Git Bash, Gemini CLI)
- Node not on `PATH`

**Solutions**:
1. Re-run `arkhe-preview start ...` — the random port changes each run.
2. If on Windows / Codex / Gemini, pass `--foreground` and run the command in a backgroundable shell (see [browser-companion WORKFLOW.md](../../../devtools/skills/browser-companion/WORKFLOW.md)).
3. Pin a known-free port: `arkhe-preview start --port 8080 ...`.
4. Verify `node --version` works in the same shell where `arkhe-preview` is invoked.

---

### `/prototype --continue` says "no pick yet"

**Symptom**: User clicked a variant in the browser but `--continue` says they didn't.

**Causes**:
1. `events.jsonl` doesn't exist — the user clicked a non-`.variant-btn` element, or the WebSocket never connected
2. The session under `manifest.state_dir` is stale (server already shut down due to owner-pid watchdog or 30-minute idle timeout, but `manifest.json` still points to it)
3. The wrong `--dir` is being passed to `--continue`

**Solutions**:
1. Check `arkhe-preview status <session_dir>` (from `manifest.session_dir`). If `running: false`, restart with `/prototype <original prompt>`.
2. Check the browser dev tools console for WebSocket errors. The helper auto-reconnects; if connection is impossible, events never reach the server.
3. Pass the same `--dir` to both invocations: `/prototype foo --dir ./mockups` and `/prototype --continue --dir ./mockups`.
4. If `events.jsonl` exists but has no `select-variant` events, the user clicked on the iframe content rather than the sidebar buttons. Remind them the variant buttons live in the LEFT SIDEBAR of the gallery page.

---

### Server died mid-session

**Symptom**: Browser loses its WebSocket, no more reloads on file changes.

**Causes**:
- Owner-pid watchdog: the server exits when the agent/shell process that started it dies
- 30-minute idle timeout (no HTTP/WS activity)
- The user manually killed the process

**Solutions**:
1. `arkhe-preview status <session_dir>` to confirm `running: false`.
2. Re-run `/prototype <original prompt>` to start a fresh session. The previous `screen_dir` still has the artifacts; the new session gets a fresh `screen_dir` under a new session id.
3. To survive longer agent loops, the `--owner-pid 0` flag on `arkhe-preview start` disables the watchdog. Only use this for long-lived workflows — it relies on the 30-minute idle timeout for cleanup.

---

### HTML Output Contains Markdown Fences

**Symptom**: Generated HTML starts with `` ```html `` or ends with `` ``` ``

**Solution**: Strip markdown fences before writing files:
- Remove leading `` ```html `` or `` ``` `` and any whitespace after
- Remove trailing `` ``` `` and any whitespace before
- Verify the result starts with `<!DOCTYPE html>` or `<html>`

---

### All 3 Artifacts Look Too Similar

**Symptom**: The design variations feel like color swaps rather than distinct approaches

**Causes**:
- Style direction names are too generic (e.g., "Modern Clean", "Elegant Simple")
- The metaphors don't translate to concrete CSS techniques

**Solutions**:
1. Ensure style names follow the pattern: `[Adjective] + [Material/Process] + [Form/Action]`
2. Each metaphor should imply different CSS techniques (see materiality-to-CSS mapping in WORKFLOW.md)
3. Regenerate with more specific creative examples in the style direction prompt
4. The examples should span different visual dimensions: texture vs structure vs motion vs color

---

### Google Fonts Not Loading

**Symptom**: Artifacts display in system fonts instead of the specified Google Fonts

**Causes**:
- Missing `<link>` tag in HTML `<head>`
- Incorrect font family name in CSS
- No internet connection when viewing the file

**Solutions**:
1. Verify each artifact has a Google Fonts `<link>` tag:
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
   ```
2. Ensure `font-family` in CSS matches the imported font name exactly
3. For offline use, consider adding a system font fallback stack

---

### `--vary` Fails to Find the Artifact

**Symptom**: `/prototype --vary 2` doesn't know which file is artifact 2

**Causes**:
- `manifest.json` is missing from the output directory
- The manifest was manually edited or corrupted
- The session directory was renamed or moved

**Solutions**:
1. Check that `$DIR/manifest.json` exists and contains the `artifacts` array
2. If missing, the skill falls back to globbing `$DIR/.claude/preview/*/content/0N-*.html` and inferring the original prompt from the filename
3. Regenerate with `/prototype <original prompt>` to create a fresh manifest

---

### Iframes in the Gallery Show "Forbidden" or 404

**Symptom**: Clicking a variant shows a blank iframe or the browser shows a 403/404 from `/files/<name>`.

**Causes**:
- The `data-src` in `99-gallery.html` doesn't match a real file in `screen_dir`
- A path-traversal attempt (`/files/../../etc/passwd`) — blocked by the server's path guard (this is correct behavior)

**Solutions**:
1. Verify each artifact file exists in `screen_dir` with the exact filename used in `data-src`
2. Re-write `99-gallery.html` after any rename of artifact files
3. Run `curl -fsS <url>/files/<filename>` to confirm the file is reachable

---

### Large Token Usage

**Symptom**: Generation takes a long time or hits token limits

**Cause**: Each HTML artifact can be 200-500 lines. Generating 3 in one response is token-heavy.

**Solutions**:
1. Keep the component description focused and specific
2. For complex components, prototype a single section rather than a full page
3. Use simpler prompts: "login form" generates faster than "full e-commerce checkout flow"

---

### Artifacts Reference Artist Names or Brands

**Symptom**: Generated HTML contains references to specific artists, brands, or copyrighted works

**Solution**: The IP safeguard in the prompt should prevent this. If it occurs:
1. Remove the offending references manually
2. Regenerate with a stronger safeguard instruction
3. The prompt explicitly states "No artist names, brand names, or trademarks" — if this is being ignored, add a more emphatic instruction

---

## When to Ask for Help

- If the skill fails to generate valid HTML after multiple attempts
- If `arkhe-preview` fails to start despite the troubleshooting above (the issue may be in the devtools plugin's [browser-companion](../../../devtools/skills/browser-companion/TROUBLESHOOTING.md))
- If you need to customize the gallery template or helper for a specific design system or framework
