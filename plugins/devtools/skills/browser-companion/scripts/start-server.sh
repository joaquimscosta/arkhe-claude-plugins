#!/usr/bin/env bash
# Start the arkhe-preview server and output connection info as JSON.
#
# Usage: start-server.sh [options]
#
# Options:
#   --project-dir <path>      Place session under <path>/.claude/preview/<id>/
#                             (default: /tmp/arkhe-preview-<id>/)
#   --frame-template <path>   Override frame template HTML
#   --helper <path>           Override browser-side helper JS
#   --port <N>                Force a specific port (default: random 49152-65535)
#   --host <H>                Bind address (default: 127.0.0.1)
#   --url-host <H>            Hostname shown in returned URL JSON (default: matches --host)
#   --owner-pid <PID>         Watchdog: stop when PID disappears (default: PPID parent)
#                             Use 0 to disable watchdog.
#   --foreground              Run in current shell instead of nohup'ing
#   --background              Force background mode (overrides auto-foreground)
#
# Derived from the superpowers project (MIT, Jesse Vincent 2025).
# See ../WORKFLOW.md > Attribution.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
PROJECT_DIR=""
FOREGROUND="false"
FORCE_BACKGROUND="false"
BIND_HOST="127.0.0.1"
URL_HOST=""
PORT=""
FRAME_TEMPLATE=""
HELPER=""
OWNER_PID_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir)     PROJECT_DIR="$2"; shift 2 ;;
    --frame-template)  FRAME_TEMPLATE="$2"; shift 2 ;;
    --helper)          HELPER="$2"; shift 2 ;;
    --port)            PORT="$2"; shift 2 ;;
    --host)            BIND_HOST="$2"; shift 2 ;;
    --url-host)        URL_HOST="$2"; shift 2 ;;
    --owner-pid)       OWNER_PID_OVERRIDE="$2"; shift 2 ;;
    --foreground|--no-daemon)  FOREGROUND="true"; shift ;;
    --background|--daemon)     FORCE_BACKGROUND="true"; shift ;;
    *) echo "{\"error\": \"Unknown argument: $1\"}" >&2; exit 1 ;;
  esac
done

if [[ -z "$URL_HOST" ]]; then
  if [[ "$BIND_HOST" == "127.0.0.1" || "$BIND_HOST" == "localhost" ]]; then
    URL_HOST="localhost"
  else
    URL_HOST="$BIND_HOST"
  fi
fi

# Some environments reap detached/background processes. Auto-foreground when detected.
if [[ -n "${CODEX_CI:-}" && "$FOREGROUND" != "true" && "$FORCE_BACKGROUND" != "true" ]]; then
  FOREGROUND="true"
fi

# Windows/Git Bash reaps nohup background processes. Auto-foreground when detected.
if [[ "$FOREGROUND" != "true" && "$FORCE_BACKGROUND" != "true" ]]; then
  case "${OSTYPE:-}" in
    msys*|cygwin*|mingw*) FOREGROUND="true" ;;
  esac
  if [[ -n "${MSYSTEM:-}" ]]; then
    FOREGROUND="true"
  fi
fi

# Resolve frame template + helper to absolute paths (so server.cjs can find them
# regardless of cwd). Defaults are sibling files in this scripts/ dir.
if [[ -z "$FRAME_TEMPLATE" ]]; then
  FRAME_TEMPLATE="$SCRIPT_DIR/frame-template.html"
fi
if [[ -z "$HELPER" ]]; then
  HELPER="$SCRIPT_DIR/helper.js"
fi
# Convert to absolute paths
case "$FRAME_TEMPLATE" in /*) ;; *) FRAME_TEMPLATE="$(cd "$(dirname "$FRAME_TEMPLATE")" && pwd)/$(basename "$FRAME_TEMPLATE")" ;; esac
case "$HELPER" in /*) ;; *) HELPER="$(cd "$(dirname "$HELPER")" && pwd)/$(basename "$HELPER")" ;; esac

if [[ ! -f "$FRAME_TEMPLATE" ]]; then
  echo "{\"error\": \"Frame template not found: $FRAME_TEMPLATE\"}" >&2
  exit 1
fi
if [[ ! -f "$HELPER" ]]; then
  echo "{\"error\": \"Helper script not found: $HELPER\"}" >&2
  exit 1
fi

# Generate unique session directory
SESSION_ID="$$-$(date +%s)"

if [[ -n "$PROJECT_DIR" ]]; then
  SESSION_DIR="${PROJECT_DIR}/.claude/preview/${SESSION_ID}"
else
  SESSION_DIR="/tmp/arkhe-preview-${SESSION_ID}"
fi

STATE_DIR="${SESSION_DIR}/state"
PID_FILE="${STATE_DIR}/server.pid"
LOG_FILE="${STATE_DIR}/server.log"

# Create fresh session directory with content and state peers
mkdir -p "${SESSION_DIR}/content" "$STATE_DIR" "${SESSION_DIR}/logs"

# Kill any existing server (if PID file is from a prior run that crashed)
if [[ -f "$PID_FILE" ]]; then
  old_pid=$(cat "$PID_FILE")
  kill "$old_pid" 2>/dev/null || true
  rm -f "$PID_FILE"
fi

# Resolve the owning process PID. By default we use the grandparent of this
# script ($PPID's parent), which is typically the agent/harness — $PPID itself
# is an ephemeral shell that dies as soon as this script exits.
if [[ -n "$OWNER_PID_OVERRIDE" ]]; then
  OWNER_PID="$OWNER_PID_OVERRIDE"
else
  OWNER_PID="$(ps -o ppid= -p "$PPID" 2>/dev/null | tr -d ' ' || true)"
  if [[ -z "$OWNER_PID" || "$OWNER_PID" == "1" ]]; then
    OWNER_PID="$PPID"
  fi
fi

# 0 means "no watchdog" — empty the env var so server.cjs skips owner checks.
if [[ "$OWNER_PID" == "0" ]]; then
  OWNER_PID=""
fi

# Build the env exports for the server
ENV_VARS=(
  "PREVIEW_DIR=$SESSION_DIR"
  "PREVIEW_HOST=$BIND_HOST"
  "PREVIEW_URL_HOST=$URL_HOST"
  "PREVIEW_FRAME_TEMPLATE=$FRAME_TEMPLATE"
  "PREVIEW_HELPER=$HELPER"
)
if [[ -n "$PORT" ]]; then
  ENV_VARS+=("PREVIEW_PORT=$PORT")
fi
if [[ -n "$OWNER_PID" ]]; then
  ENV_VARS+=("PREVIEW_OWNER_PID=$OWNER_PID")
fi

# Foreground mode for environments that reap detached/background processes.
if [[ "$FOREGROUND" == "true" ]]; then
  echo "$$" > "$PID_FILE"
  exec env "${ENV_VARS[@]}" node "$SCRIPT_DIR/server.cjs"
fi

# Start server, capturing output to log file.
# Use nohup to survive shell exit; disown to remove from job table.
nohup env "${ENV_VARS[@]}" node "$SCRIPT_DIR/server.cjs" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
disown "$SERVER_PID" 2>/dev/null || true
echo "$SERVER_PID" > "$PID_FILE"

# Wait for server-started message (check log file)
for i in {1..50}; do
  if grep -q "server-started" "$LOG_FILE" 2>/dev/null; then
    # Verify server is still alive after a short window (catches process reapers)
    alive="true"
    for _ in {1..20}; do
      if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        alive="false"
        break
      fi
      sleep 0.1
    done
    if [[ "$alive" != "true" ]]; then
      echo "{\"error\": \"Server started but was killed. Retry with --foreground.\"}" >&2
      exit 1
    fi
    grep "server-started" "$LOG_FILE" | head -1
    exit 0
  fi
  sleep 0.1
done

echo '{"error": "Server failed to start within 5 seconds"}' >&2
exit 1
