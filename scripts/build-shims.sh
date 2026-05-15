#!/usr/bin/env bash
# Orchestrate Gemini and Codex shim generation for all arkhe plugins.
#
# Reads .claude-plugin/marketplace.json to enumerate plugins. Runs the two
# Python generators (transpile-commands.py, generate-codex-agents-md.py),
# then writes per-plugin Gemini and Codex manifests, GEMINI.md context files,
# and skills symlinks. Idempotent: re-running produces no diff.
#
# Requires: bash 4+, jq, python3 (3.8+).

set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
PLUGINS_DIR="$REPO_ROOT/plugins"
GEMINI_ROOT="$REPO_ROOT/.gemini-extensions"
CODEX_ROOT="$REPO_ROOT/.codex-marketplace"
TRANSPILE="$REPO_ROOT/scripts/transpile-commands.py"
CODEX_GEN="$REPO_ROOT/scripts/generate-codex-agents-md.py"
READMES_GEN="$REPO_ROOT/scripts/update-plugin-readmes.py"

err() { printf 'build-shims: %s\n' "$*" >&2; exit 1; }

[[ -f "$MARKETPLACE" ]] || err "marketplace.json not found at $MARKETPLACE"
command -v jq >/dev/null 2>&1 || err "jq is required (brew install jq)"
command -v python3 >/dev/null 2>&1 || err "python3 is required"
[[ -x "$TRANSPILE" ]] || err "transpile-commands.py not executable: $TRANSPILE"
[[ -x "$CODEX_GEN" ]] || err "generate-codex-agents-md.py not executable: $CODEX_GEN"
[[ -x "$READMES_GEN" ]] || err "update-plugin-readmes.py not executable: $READMES_GEN"

# Step 1: run Python generators (idempotent; they write their own outputs).
python3 "$TRANSPILE"
python3 "$CODEX_GEN"
python3 "$READMES_GEN"

# Atomic write: render to temp file, only move into place if content differs.
# Keeps mtimes stable across runs and prevents partial files on crash.
write_if_changed() {
    local dest="$1" tmp
    tmp=$(mktemp "${dest}.tmp.XXXXXX")
    cat >"$tmp"
    chmod 0644 "$tmp"
    if [[ -f "$dest" ]] && cmp -s "$tmp" "$dest"; then
        rm -f "$tmp"
    else
        mv "$tmp" "$dest"
    fi
    # Self-heal mode (no-op when already 0644). Cheap and keeps git happy.
    chmod 0644 "$dest" 2>/dev/null || true
}

# Idempotent symlink: create if missing, replace only if target differs.
ensure_symlink() {
    local link_path="$1" target="$2"
    if [[ -L "$link_path" ]]; then
        local current
        current=$(readlink "$link_path")
        [[ "$current" == "$target" ]] && return 0
        rm "$link_path"
    elif [[ -e "$link_path" ]]; then
        err "$link_path exists and is not a symlink"
    fi
    ln -s "$target" "$link_path"
}

# Render a per-plugin GEMINI.md: bootstrap pointer + skill index.
# Reads SKILL.md description fields directly (one-line strip).
render_gemini_md() {
    local plugin="$1"
    local skills_dir="$PLUGINS_DIR/$plugin/skills"
    printf '# %s\n\n' "$plugin"
    printf '> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Gemini equivalents. Install the `core` extension if you have not already.\n\n'
    printf '@../../plugins/core/skills/using-arkhe-skills/SKILL.md\n\n'
    if [[ -d "$skills_dir" ]]; then
        printf '## Skills\n\n'
        local skill_md
        for skill_md in "$skills_dir"/*/SKILL.md; do
            [[ -f "$skill_md" ]] || continue
            local skill_name skill_desc
            skill_name=$(basename "$(dirname "$skill_md")")
            # Pull a single-line `description:` from YAML frontmatter.
            # Extract description from YAML frontmatter. Handles inline
            # values, folded (`>`), and literal (`|`) block scalars by
            # joining indented continuation lines with a single space.
            skill_desc=$(awk '
                BEGIN { fm = 0; in_desc = 0; desc = "" }
                /^---[[:space:]]*$/ {
                    if (fm == 0) { fm = 1; next }
                    if (in_desc && desc != "") print desc
                    exit
                }
                fm == 1 {
                    if (in_desc) {
                        if (/^[[:space:]]/) {
                            line = $0
                            sub(/^[[:space:]]+/, "", line)
                            if (line != "") desc = (desc == "" ? line : desc " " line)
                            next
                        }
                        print desc; exit
                    }
                    if (/^description:/) {
                        val = $0
                        sub(/^description:[[:space:]]*/, "", val)
                        sub(/^"/, "", val); sub(/"$/, "", val)
                        if (val == ">" || val == "|" || val == ">-" || val == "|-") {
                            in_desc = 1; desc = ""
                        } else { print val; exit }
                    }
                }
            ' "$skill_md")
            # Escape '@' in description text. Gemini's ImportProcessor parses
            # bare `@token` patterns as filesystem imports (e.g., Java
            # annotations like @RestController in spring-boot skill descriptions
            # cause ENOENT errors). HTML entity &#64; survives this preprocessor
            # and renders identically for the model.
            local desc_safe="${skill_desc//@/&#64;}"
            printf -- '- **%s** — %s\n' "$skill_name" "${desc_safe:-(no description)}"
        done
        printf '\n'
    fi
    printf '## Commands\n\nSee `commands/` directory for transpiled Gemini TOML commands.\n'
}

# Step 2: per-plugin manifests + symlinks.
# Using `while IFS=... read` with process substitution keeps the loop in the
# parent shell so plugin_count survives. Avoids `mapfile` (Bash 4+; macOS
# ships 3.2).
plugin_count=0
while IFS=$'\t' read -r plugin description; do
    [[ -n "$plugin" ]] || continue
    plugin_json="$PLUGINS_DIR/$plugin/.claude-plugin/plugin.json"
    [[ -f "$plugin_json" ]] || err "missing plugin manifest: $plugin_json"

    version=$(jq -r '.version // "0.0.0"' "$plugin_json")

    # --- Gemini extension ---
    gemini_dir="$GEMINI_ROOT/$plugin"
    mkdir -p "$gemini_dir"
    jq -n --arg name "$plugin" --arg desc "$description" --arg ver "$version" \
        '{name: $name, description: $desc, version: $ver, contextFileName: "GEMINI.md"}' \
        | write_if_changed "$gemini_dir/gemini-extension.json"
    render_gemini_md "$plugin" | write_if_changed "$gemini_dir/GEMINI.md"
    ensure_symlink "$gemini_dir/skills" "../../plugins/$plugin/skills"

    # --- Codex marketplace ---
    codex_dir="$CODEX_ROOT/$plugin"
    mkdir -p "$codex_dir"
    jq -n --arg name "$plugin" --arg desc "$description" --arg ver "$version" \
        '{name: $name, description: $desc, version: $ver}' \
        | write_if_changed "$codex_dir/plugin.json"
    ensure_symlink "$codex_dir/skills" "../../plugins/$plugin/skills"

    plugin_count=$((plugin_count + 1))
done < <(jq -r '.plugins[] | [.name, .description] | @tsv' "$MARKETPLACE")

printf 'build-shims: %d plugins processed\n' "$plugin_count"
