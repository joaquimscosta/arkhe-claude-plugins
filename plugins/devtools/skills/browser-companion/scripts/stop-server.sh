#!/usr/bin/env bash
# Stop the arkhe-preview server and clean up.
#
# Usage: stop-server.sh <session_dir>
#
# Kills the server process. Only deletes the session directory when it matches
# the default ephemeral pattern (/tmp/arkhe-preview-<id>/). Project-dir
# sessions under .claude/preview/<id>/ are preserved so content can be
# reviewed after shutdown — even when the project itself lives under /tmp.
#
# Derived from the superpowers project (MIT, Jesse Vincent 2025).

set -euo pipefail

SESSION_DIR="${1:-}"

if [[ -z "$SESSION_DIR" ]]; then
  echo '{"error": "Usage: stop-server.sh <session_dir>"}' >&2
  exit 1
fi

STATE_DIR="${SESSION_DIR}/state"
PID_FILE="${STATE_DIR}/server.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo '{"status": "not_running"}'
  exit 0
fi

pid=$(cat "$PID_FILE")

# Try to stop gracefully, fallback to force if still alive
kill "$pid" 2>/dev/null || true

# Wait for graceful shutdown (up to ~2s)
for i in {1..20}; do
  if ! kill -0 "$pid" 2>/dev/null; then
    break
  fi
  sleep 0.1
done

# If still running, escalate to SIGKILL
if kill -0 "$pid" 2>/dev/null; then
  kill -9 "$pid" 2>/dev/null || true
  sleep 0.1
fi

if kill -0 "$pid" 2>/dev/null; then
  echo '{"status": "failed", "error": "process still running"}' >&2
  exit 2
fi

rm -f "$PID_FILE" "${STATE_DIR}/server.log" 2>/dev/null || true

# Only delete sessions that match the default ephemeral pattern. Project-dir
# sessions (PROJECT/.claude/preview/<id>) are preserved even if PROJECT is
# under /tmp — including the corner case where PROJECT itself starts with
# 'arkhe-preview-'. The second guard catches that: bash glob '*' is greedy
# across '/', so /tmp/arkhe-preview-foo/.claude/preview/<id> would match the
# first pattern alone; the second guard rejects any path containing
# '/.claude/preview/' as a project-dir session.
if [[ "$SESSION_DIR" == /tmp/arkhe-preview-* && "$SESSION_DIR" != */.claude/preview/* ]]; then
  rm -rf "$SESSION_DIR"
fi

echo '{"status": "stopped"}'
