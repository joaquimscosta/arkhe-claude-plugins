#!/usr/bin/env bash
set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────
VERBATIM_FILES=(shared.py link_checker.py version_checker.py scan_freshness.py)
MANUAL_FILES=(claude_md_checker.py frontmatter_onboard.py)

# ── Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_SCRIPTS="$SCRIPT_DIR"

ACTION_REPO=""
YES_FLAG=false

for arg in "$@"; do
  case "$arg" in
    -y|--yes) YES_FLAG=true ;;
    -h|--help)
      echo "Usage: $(basename "$0") <path-to-docs-health-action> [-y|--yes]"
      echo ""
      echo "Syncs checker scripts from docs-health-action into this plugin."
      echo ""
      echo "  Verbatim-copies: ${VERBATIM_FILES[*]}"
      echo "  Manual review:   ${MANUAL_FILES[*]}"
      echo ""
      echo "Options:"
      echo "  -y, --yes   Skip confirmation prompts"
      echo "  -h, --help  Show this help"
      exit 0
      ;;
    -*) echo "Unknown flag: $arg"; exit 1 ;;
    *) ACTION_REPO="$arg" ;;
  esac
done

if [[ -z "$ACTION_REPO" ]]; then
  echo "Usage: $(basename "$0") <path-to-docs-health-action> [-y|--yes]"
  echo ""
  echo "Syncs checker scripts from docs-health-action into this plugin."
  echo "Example: $(basename "$0") ~/Projects/docs-health-action"
  exit 1
fi

ACTION_SCRIPTS="$ACTION_REPO/scripts"

# ── Validate ───────────────────────────────────────────────────────────
if [[ ! -d "$ACTION_SCRIPTS" ]]; then
  echo "ERROR: Cannot find action scripts at: $ACTION_SCRIPTS"
  echo "       Make sure the path points to the docs-health-action repo root."
  exit 1
fi

echo "=== Sync from docs-health-action ==="
echo "Source:      $(cd "$ACTION_SCRIPTS" && pwd)"
echo "Destination: $PLUGIN_SCRIPTS"
echo ""

# Validate all source files exist
missing=false
for f in "${VERBATIM_FILES[@]}" "${MANUAL_FILES[@]}"; do
  if [[ ! -f "$ACTION_SCRIPTS/$f" ]]; then
    echo "ERROR: Missing in action repo: $ACTION_SCRIPTS/$f"
    missing=true
  fi
done
if $missing; then exit 1; fi

# ── Helpers ────────────────────────────────────────────────────────────
confirm() {
  if $YES_FLAG; then return 0; fi
  local prompt="$1"
  read -r -p "$prompt [y/N] " answer
  [[ "$answer" =~ ^[Yy]$ ]]
}

# ── Verbatim copies ───────────────────────────────────────────────────
echo "── Verbatim files ──"
copied=0
skipped_identical=0
skipped_declined=0

for f in "${VERBATIM_FILES[@]}"; do
  src="$ACTION_SCRIPTS/$f"
  dst="$PLUGIN_SCRIPTS/$f"

  if [[ ! -f "$dst" ]]; then
    echo "  [new] $f — does not exist in plugin yet"
    if confirm "  Copy $f?"; then
      cp "$src" "$dst"
      echo "  [copied] $f"
      copied=$((copied + 1))
    else
      echo "  [skipped] $f"
      skipped_declined=$((skipped_declined + 1))
    fi
    continue
  fi

  if diff -q "$src" "$dst" >/dev/null 2>&1; then
    echo "  [ok] $f — already identical"
    skipped_identical=$((skipped_identical + 1))
    continue
  fi

  changes=$(diff "$src" "$dst" | grep -c '^[<>]' || true)
  echo "  [changed] $f — $changes lines differ"
  if confirm "  Overwrite $f?"; then
    cp "$src" "$dst"
    echo "  [copied] $f"
    ((copied++))
  else
    echo "  [skipped] $f"
    ((skipped_declined++))
  fi
done

# ── Manual review ─────────────────────────────────────────────────────
echo ""
echo "── Files requiring manual review ──"
echo "(These have plugin-specific customizations — do NOT copy blindly)"
echo ""

needs_review=0

for f in "${MANUAL_FILES[@]}"; do
  src="$ACTION_SCRIPTS/$f"
  dst="$PLUGIN_SCRIPTS/$f"

  if [[ ! -f "$dst" ]]; then
    echo "  [new] $f — does not exist in plugin (copy manually if needed)"
    needs_review=$((needs_review + 1))
    continue
  fi

  if diff -q "$src" "$dst" >/dev/null 2>&1; then
    echo "  [ok] $f — already in sync"
    continue
  fi

  ((needs_review++))
  echo "┌─── $f: action (a) vs plugin (b) ───"
  diff -u "$src" "$dst" || true
  echo "└────────────────────────────────────────────"
  echo ""

  case "$f" in
    claude_md_checker.py)
      echo "  PRESERVE in plugin:"
      echo "    - Arkhe-specific _NAME_OVERRIDES dict values"
      echo "  MERGE from action:"
      echo "    - has_plugins guard (prevents crash without plugins/ dir)"
      echo "    - Any new check logic or bug fixes"
      ;;
    frontmatter_onboard.py)
      echo "  PRESERVE in plugin:"
      echo "    - Arkhe-specific CANDIDATE_PATTERNS whitelist"
      echo "  MERGE from action:"
      echo "    - patterns parameter on public functions (API flexibility)"
      echo "    - _count_skipped() single-call optimization (efficiency bug fix)"
      echo "    - Any new check logic or bug fixes"
      ;;
  esac
  echo ""
done

# ── Summary ───────────────────────────────────────────────────────────
echo ""
echo "=== Summary ==="
echo "  Copied:            $copied"
echo "  Already identical: $skipped_identical"
echo "  Declined:          $skipped_declined"
echo "  Need manual merge: $needs_review"

if ((needs_review > 0)); then
  echo ""
  echo "Review the diffs above and manually merge changes for the flagged files."
fi
