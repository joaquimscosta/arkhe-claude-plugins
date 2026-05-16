#!/usr/bin/env bash
#
# bump-version.sh — bump version numbers across declared files,
# with drift detection and repo-wide audit for missed files.
#
# Adopted from external-repos/superpowers/scripts/bump-version.sh, extended
# with per-plugin scoping for arkhe's per-plugin versioning model.
#
# Requires: jq.
#
# Usage:
#   bump-version.sh [flags] <new-version>   Bump matching files to new version
#   bump-version.sh [flags] --check         Report current versions (detect drift)
#   bump-version.sh [flags] --audit         Check + grep repo for old version strings
#
# Flags:
#   --plugin <name>   Filter to a single plugin's manifests
#   --skip-shims      Exclude .gemini-extensions/ and .codex-marketplace/ paths
#                     (Claude-only mode for backward compat)
#
# Examples:
#   bump-version.sh --plugin core 2.3.0          # Bump core's 3 manifests
#   bump-version.sh --plugin core --skip-shims 2.3.0   # Bump core Claude only
#   bump-version.sh --check                       # All declared paths
#   bump-version.sh --plugin core --check         # Just core's paths
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG="$REPO_ROOT/.version-bump.json"

if [[ ! -f "$CONFIG" ]]; then
  echo "error: .version-bump.json not found at $CONFIG" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required (brew install jq)" >&2
  exit 1
fi

# --- flag parsing ---

FILTER_PLUGIN=""
FILTER_SKIP_SHIMS=0
POSITIONAL=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plugin)
      [[ -n "${2:-}" ]] || { echo "error: --plugin requires a value" >&2; exit 1; }
      FILTER_PLUGIN="$2"
      shift 2
      ;;
    --plugin=*)
      FILTER_PLUGIN="${1#--plugin=}"
      shift
      ;;
    --skip-shims)
      FILTER_SKIP_SHIMS=1
      shift
      ;;
    --check|--audit|--help|-h)
      POSITIONAL+=("$1")
      shift
      ;;
    --*)
      echo "error: unknown flag '$1'" >&2
      exit 1
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

set -- "${POSITIONAL[@]:-}"

# --- helpers ---

# Read a dotted field path from a JSON file.
# Handles both simple ("version") and nested ("plugins.0.version") paths.
read_json_field() {
  local file="$1" field="$2"
  local jq_path
  jq_path=$(echo "$field" | sed -E 's/\.([0-9]+)/[\1]/g' | sed 's/^/./' | sed 's/\.\././g')
  jq -r "$jq_path" "$file"
}

# Write a dotted field path in a JSON file, preserving formatting.
write_json_field() {
  local file="$1" field="$2" value="$3"
  local jq_path
  jq_path=$(echo "$field" | sed -E 's/\.([0-9]+)/[\1]/g' | sed 's/^/./' | sed 's/\.\././g')
  local tmp="${file}.tmp"
  jq "$jq_path = \"$value\"" "$file" > "$tmp" && mv "$tmp" "$file"
}

# Read declared files from config, applying --plugin and --skip-shims filters.
# Outputs lines of "path<TAB>field"
declared_files() {
  local jq_filter='.files[]'

  if [[ -n "$FILTER_PLUGIN" ]]; then
    jq_filter="$jq_filter | select(.plugin == \"$FILTER_PLUGIN\")"
  fi

  if [[ "$FILTER_SKIP_SHIMS" -eq 1 ]]; then
    jq_filter="$jq_filter | select((.platform // \"claude\") == \"claude\")"
  fi

  jq -r "$jq_filter | \"\(.path)\t\(.field)\"" "$CONFIG"
}

# Read the audit exclude patterns from config.
audit_excludes() {
  jq -r '.audit.exclude[]' "$CONFIG" 2>/dev/null
}

# Resolve a glob pattern in a path against the repo. Supports a single `*`
# segment per path. Returns expanded paths, one per line.
expand_path() {
  local path="$1"
  if [[ "$path" != *"*"* ]]; then
    echo "$path"
    return
  fi
  ( cd "$REPO_ROOT" && for p in $path; do
      [[ -e "$p" ]] && echo "$p"
    done )
}

# Validate that --plugin matched at least one file.
validate_plugin_filter() {
  if [[ -z "$FILTER_PLUGIN" ]]; then
    return 0
  fi
  local count
  count=$(declared_files | wc -l | tr -d ' ')
  if [[ "$count" -eq 0 ]]; then
    echo "error: --plugin '$FILTER_PLUGIN' matched no entries in $CONFIG" >&2
    echo "Available plugins:" >&2
    jq -r '.files[].plugin' "$CONFIG" 2>/dev/null | sort -u | sed 's/^/  /' >&2
    exit 1
  fi
}

# --- commands ---

cmd_check() {
  validate_plugin_filter

  # Each arkhe plugin owns its own version, so cross-plugin "drift" is
  # informational, not an error. Only missing files count as real errors.
  local has_error=0
  local versions=()

  if [[ -n "$FILTER_PLUGIN" ]]; then
    echo "Version check (plugin: $FILTER_PLUGIN, skip-shims: $FILTER_SKIP_SHIMS):"
  else
    echo "Version check:"
  fi
  echo ""

  while IFS=$'\t' read -r raw_path field; do
    while IFS= read -r path; do
      local fullpath="$REPO_ROOT/$path"
      if [[ ! -f "$fullpath" ]]; then
        printf "  %-50s  MISSING\n" "$path ($field)"
        has_error=1
        continue
      fi
      local ver
      ver=$(read_json_field "$fullpath" "$field" 2>/dev/null || echo "(no field)")
      printf "  %-50s  %s\n" "$path ($field)" "$ver"
      [[ "$ver" != "(no field)" && "$ver" != "null" ]] && versions+=("$ver")
    done < <(expand_path "$raw_path")
  done < <(declared_files)

  echo ""

  if [[ ${#versions[@]} -eq 0 ]]; then
    echo "warning: no version values found in declared files"
    return 0
  fi

  local unique
  unique=$(printf '%s\n' "${versions[@]}" | sort -u | wc -l | tr -d ' ')
  if [[ "$unique" -gt 1 ]]; then
    if [[ -n "$FILTER_PLUGIN" ]]; then
      echo "error: plugin '$FILTER_PLUGIN' has version drift across its manifests:" >&2
      printf '%s\n' "${versions[@]}" | sort | uniq -c | sort -rn | while read -r count ver; do
        echo "  $ver ($count files)" >&2
      done
      return 1
    fi
    echo "Per-plugin versions (informational; each plugin owns its release cycle):"
    printf '%s\n' "${versions[@]}" | sort | uniq -c | sort -rn | while read -r count ver; do
      echo "  $ver ($count files)"
    done
  else
    echo "All declared files are in sync at ${versions[0]}"
  fi

  return $has_error
}

cmd_audit() {
  local check_status=0
  cmd_check || check_status=$?
  echo ""

  local current_version
  current_version=$(
    while IFS=$'\t' read -r raw_path field; do
      while IFS= read -r path; do
        local fullpath="$REPO_ROOT/$path"
        [[ -f "$fullpath" ]] && read_json_field "$fullpath" "$field" 2>/dev/null
      done < <(expand_path "$raw_path")
    done < <(declared_files) | grep -v '^null$' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}'
  )

  if [[ -z "$current_version" ]]; then
    echo "error: could not determine current version" >&2
    return 1
  fi

  echo "Audit: scanning repo for version string '$current_version'..."
  echo ""

  local -a exclude_args=()
  while IFS= read -r pattern; do
    [[ -z "$pattern" ]] && continue
    exclude_args+=("--exclude=$pattern" "--exclude-dir=$pattern")
  done < <(audit_excludes)

  exclude_args+=("--exclude-dir=.git" "--exclude-dir=node_modules" "--exclude-dir=external-repos" "--binary-files=without-match")

  local -a declared_paths=()
  while IFS=$'\t' read -r raw_path _field; do
    while IFS= read -r path; do
      declared_paths+=("$path")
    done < <(expand_path "$raw_path")
  done < <(declared_files)

  local found_undeclared=0
  while IFS= read -r match; do
    local match_file
    match_file=$(echo "$match" | cut -d: -f1)
    local rel_path="${match_file#$REPO_ROOT/}"
    local is_declared=0
    for dp in "${declared_paths[@]}"; do
      if [[ "$rel_path" == "$dp" ]]; then
        is_declared=1
        break
      fi
    done
    if [[ "$is_declared" -eq 0 ]]; then
      if [[ "$found_undeclared" -eq 0 ]]; then
        echo "UNDECLARED files containing '$current_version':"
        found_undeclared=1
      fi
      echo "  $match"
    fi
  done < <(grep -rn "${exclude_args[@]}" -F "$current_version" "$REPO_ROOT" 2>/dev/null || true)

  if [[ "$found_undeclared" -eq 0 ]]; then
    echo "No undeclared files contain the version string. All clear."
  else
    echo ""
    echo "Review the above files — if they should be bumped, add them to .version-bump.json"
    echo "If they should be skipped, add them to the audit.exclude list."
  fi

  return $((check_status | found_undeclared))
}

cmd_bump() {
  local new_version="$1"

  if ! echo "$new_version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+'; then
    echo "error: '$new_version' doesn't look like a version (expected X.Y.Z)" >&2
    exit 1
  fi

  validate_plugin_filter

  if [[ -n "$FILTER_PLUGIN" ]]; then
    if [[ "$FILTER_SKIP_SHIMS" -eq 1 ]]; then
      echo "Bumping plugin '$FILTER_PLUGIN' (Claude only) to $new_version..."
    else
      echo "Bumping plugin '$FILTER_PLUGIN' to $new_version..."
    fi
  else
    if [[ "$FILTER_SKIP_SHIMS" -eq 1 ]]; then
      echo "Bumping all Claude manifests to $new_version..."
    else
      echo "Bumping all declared files to $new_version..."
    fi
  fi
  echo ""

  while IFS=$'\t' read -r raw_path field; do
    while IFS= read -r path; do
      local fullpath="$REPO_ROOT/$path"
      if [[ ! -f "$fullpath" ]]; then
        echo "  SKIP (missing): $path"
        continue
      fi
      local old_ver
      old_ver=$(read_json_field "$fullpath" "$field" 2>/dev/null || echo "n/a")
      write_json_field "$fullpath" "$field" "$new_version"
      printf "  %-50s  %s -> %s\n" "$path ($field)" "$old_ver" "$new_version"
    done < <(expand_path "$raw_path")
  done < <(declared_files)

  echo ""
  echo "Done. Running audit to check for missed files..."
  echo ""
  cmd_audit
}

# --- main ---

case "${1:-}" in
  --check)
    cmd_check
    ;;
  --audit)
    cmd_audit
    ;;
  --help|-h|"")
    cat <<'EOF'
Usage: bump-version.sh [flags] <new-version> | [flags] --check | [flags] --audit

Commands:
  <new-version>     Bump matching files to the given version
  --check           Show current versions, detect drift
  --audit           Check + scan repo for undeclared version references

Flags:
  --plugin <name>   Filter to a single plugin's manifests
  --skip-shims      Exclude .gemini-extensions/ and .codex-marketplace/ paths
                    (Claude-only mode for backward compat)

Examples:
  bump-version.sh --plugin core 2.3.0
  bump-version.sh --plugin core --skip-shims 2.3.0
  bump-version.sh --plugin core --check
EOF
    exit 0
    ;;
  *)
    cmd_bump "$1"
    ;;
esac
