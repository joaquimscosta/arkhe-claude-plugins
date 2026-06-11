#!/usr/bin/env bash
# Report arkhe-preview server status.
#
# Usage: status-server.sh <session_dir>
#
# Always exits 0 — status is informational, not a failure condition. Inspect
# stdout JSON for liveness.

set -euo pipefail

SESSION_DIR="${1:-}"

if [[ -z "$SESSION_DIR" ]]; then
  echo '{"error": "Usage: status-server.sh <session_dir>"}' >&2
  exit 1
fi

STATE_DIR="${SESSION_DIR}/state"
PID_FILE="${STATE_DIR}/server.pid"
INFO_FILE="${STATE_DIR}/server-info"

if [[ ! -f "$PID_FILE" ]]; then
  echo '{"running": false, "pid": null, "url": null, "reason": "no pid file"}'
  exit 0
fi

pid=$(cat "$PID_FILE")
url="null"
if [[ -f "$INFO_FILE" ]]; then
  url="$(grep -oE '"url":"[^"]+"' "$INFO_FILE" | head -1 | cut -d: -f2- | tr -d '"' || true)"
  if [[ -z "$url" ]]; then
    url="null"
  else
    url="\"$url\""
  fi
fi

if kill -0 "$pid" 2>/dev/null; then
  echo "{\"running\": true, \"pid\": $pid, \"url\": $url}"
else
  echo "{\"running\": false, \"pid\": $pid, \"url\": $url, \"reason\": \"pid file present but process not alive\"}"
fi
