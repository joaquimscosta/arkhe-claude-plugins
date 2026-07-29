#!/usr/bin/env bash
#
# release.sh - Automate the full release process
#
# Usage:
#   release.sh <version>                               Repo-wide release (no manifest bump)
#   release.sh --plugin <name> <version>               Per-plugin: bump 3 manifests + release
#   release.sh --plugin <name> --skip-shims <version>  Per-plugin Claude-only (legacy)
#
# Examples:
#   release.sh 1.6.0
#   release.sh --plugin core 2.3.0
#   release.sh --plugin core --skip-shims 2.3.0
#
# This script:
#   1. Validates version format
#   2. (Optional) Bumps plugin manifests via bump-version.sh
#   3. Checks CHANGELOG.md entry exists
#   4. Adds comparison link to CHANGELOG.md (if missing)
#   5. Commits and pushes changes
#   6. Triggers the GitHub Actions release workflow
#   7. Monitors workflow and reports result
#
# Prerequisites:
#   - gh CLI installed and authenticated
#   - Git configured with push access
#   - CHANGELOG.md entry already added for the version

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Output Helpers ---

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

function print_error() {
    echo -e "${RED}Error: $1${NC}" >&2
}

function print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

function print_banner() {
    local color="$1"
    local message="$2"
    echo -e "${color}=======================================${NC}"
    echo -e "${color}  $message${NC}"
    echo -e "${color}=======================================${NC}"
}

# --- Validation Functions ---

function validate_version_arg() {
    if [[ -z "${1:-}" ]]; then
        print_error "Version required"
        echo "Usage: release.sh [--plugin <name>] [--skip-shims] <version>"
        echo "Example: release.sh 1.6.0"
        echo "Example: release.sh --plugin core 2.3.0"
        exit 1
    fi
}

function validate_semver_format() {
    local version="$1"
    if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_error "Invalid version format '$version'"
        echo "Expected semantic version (e.g., 1.6.0)"
        exit 1
    fi
}

function check_changelog_entry() {
    local version="$1"
    local changelog="$2"

    echo "Checking CHANGELOG.md for version $version..."
    if ! grep -qE "^## \[$version\]" "$changelog"; then
        print_error "No CHANGELOG entry found for version $version"
        echo ""
        echo "Please add an entry to CHANGELOG.md with the header:"
        echo "  ## [$version] - $(date +%Y-%m-%d)"
        echo ""
        echo "Tip: Use '/changelog' in Claude Code to generate the entry."
        exit 1
    fi
    print_success "CHANGELOG entry found"
}

function check_release_not_exists() {
    local tag="$1"

    echo "Checking if release $tag already exists..."
    if gh release view "$tag" &>/dev/null; then
        print_error "Release $tag already exists"
        echo "Delete it first with: gh release delete $tag --yes"
        exit 1
    fi
    print_success "Release does not exist"
}

# --- Changelog Link Management ---

function get_previous_version() {
    local version="$1"
    local changelog="$2"

    # Find the second version header (first is current version)
    local prev
    prev=$(grep -E "^## \[[0-9]+\.[0-9]+\.[0-9]+\]" "$changelog" \
        | head -2 \
        | tail -1 \
        | sed 's/.*\[\([0-9.]*\)\].*/\1/')

    # Return empty if this is the first version
    if [[ "$prev" == "$version" ]]; then
        echo ""
    else
        echo "$prev"
    fi
}

function add_comparison_link() {
    local version="$1"
    local changelog="$2"
    local repo_url="$3"

    echo "Checking comparison links..."

    # Skip if link already exists
    if grep -qE "^\[$version\]:" "$changelog"; then
        print_success "Comparison link already exists"
        return 0
    fi

    print_warning "Adding comparison link for $version..."

    local prev_version
    prev_version=$(get_previous_version "$version" "$changelog")

    # Build comparison link based on whether previous version exists
    local compare_link
    if [[ -n "$prev_version" ]]; then
        compare_link="[$version]: $repo_url/compare/v$prev_version...v$version"
    else
        compare_link="[$version]: $repo_url/releases/tag/v$version"
    fi

    # Update [Unreleased] link and add new version link
    if ! grep -qE "^\[Unreleased\]:" "$changelog"; then
        print_warning "Warning: Could not find [Unreleased] link to update"
        echo "Please manually add: $compare_link"
        return 0
    fi

    # Update Unreleased to point to new version, then add version link
    sed -i.bak "s|\[Unreleased\]:.*|[Unreleased]: $repo_url/compare/v$version...HEAD|" "$changelog"
    sed -i.bak "/^\[Unreleased\]:/a\\
$compare_link" "$changelog"
    rm -f "$changelog.bak"

    print_success "Added comparison link"
}

# --- Git Operations ---

function commit_changelog_changes() {
    local version="$1"
    local changelog="$2"
    shift 2
    # Remaining args are additional paths to include in the commit (e.g.,
    # bumped manifest files when --plugin is in use).
    local -a extra_paths=("$@")

    # Build the list of paths to consider for staging.
    local -a paths=("$changelog")
    if [[ ${#extra_paths[@]} -gt 0 ]]; then
        paths+=("${extra_paths[@]}")
    fi

    # Skip if no changes across all paths.
    if git diff --quiet -- "${paths[@]}" 2>/dev/null; then
        return 0
    fi

    echo ""
    echo "Pending release changes:"
    git diff --stat -- "${paths[@]}" || true
    echo ""
    read -p "Commit and push? [y/N] " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Skipping commit. Run manually before triggering workflow."
        exit 0
    fi

    git add -- "${paths[@]}"
    git commit -m "chore: prepare release $version"
    git push origin main
    print_success "Changes committed and pushed"
}

# --- Manifest Bump ---

function bump_plugin_manifests() {
    local plugin="$1"
    local version="$2"
    local skip_shims="$3"

    local bump_script="$SCRIPT_DIR/bump-version.sh"
    if [[ ! -x "$bump_script" ]]; then
        print_error "bump-version.sh not found or not executable at $bump_script"
        exit 1
    fi

    echo "Bumping plugin '$plugin' manifests to $version..."
    local -a bump_args=("--plugin" "$plugin")
    if [[ "$skip_shims" -eq 1 ]]; then
        bump_args+=("--skip-shims")
    fi
    bump_args+=("$version")

    if ! "$bump_script" "${bump_args[@]}"; then
        print_error "bump-version.sh failed"
        exit 1
    fi
    print_success "Plugin manifests updated"
}

# Echo the relative paths bumped by bump-version.sh for the given plugin/mode,
# so the caller can include them in `git add`.
function bumped_manifest_paths() {
    local plugin="$1"
    local skip_shims="$2"
    local config="$REPO_ROOT/.version-bump.json"

    local jq_filter=".files[] | select(.plugin == \"$plugin\")"
    if [[ "$skip_shims" -eq 1 ]]; then
        jq_filter="$jq_filter | select((.platform // \"claude\") == \"claude\")"
    fi

    jq -r "$jq_filter | .path" "$config"
}

# --- Workflow Management ---

function trigger_workflow() {
    local version="$1"
    local tag="v$version"

    echo ""
    echo "Triggering release workflow for $tag..."
    gh workflow run release.yml -f version="$version"
    print_success "Workflow triggered"
}

function wait_for_workflow() {
    local version="$1"
    local repo_url="$2"

    echo ""
    echo "Waiting for workflow to start..."
    sleep 5

    local run_id
    run_id=$(gh run list --workflow=release.yml --limit=1 --json databaseId -q '.[0].databaseId')

    if [[ -z "$run_id" ]]; then
        print_error "Could not find workflow run"
        exit 1
    fi

    echo "Monitoring workflow run $run_id..."
    echo "View at: $repo_url/actions/runs/$run_id"
    echo ""

    # Poll for completion
    local status conclusion
    while true; do
        status=$(gh run view "$run_id" --json status,conclusion -q '.status')

        if [[ "$status" == "completed" ]]; then
            conclusion=$(gh run view "$run_id" --json conclusion -q '.conclusion')
            break
        fi

        echo "  Status: $status..."
        sleep 5
    done

    # Report result
    echo ""
    if [[ "$conclusion" == "success" ]]; then
        print_banner "$GREEN" "Release v$version created successfully!"
        echo ""
        echo "View release: $repo_url/releases/tag/v$version"
    else
        print_banner "$RED" "Workflow failed with: $conclusion"
        echo ""
        echo "View logs: $repo_url/actions/runs/$run_id"
        exit 1
    fi
}

# --- Main ---

function main() {
    # All git operations downstream use repo-relative paths; ensure cwd is the
    # repo root so `git add ./relative/path` resolves the same regardless of
    # where the developer invoked release.sh from.
    cd "$REPO_ROOT"

    # --- flag parsing ---
    local plugin=""
    local skip_shims=0
    local version=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --plugin)
                [[ -n "${2:-}" ]] || { print_error "--plugin requires a value"; exit 1; }
                plugin="$2"
                shift 2
                ;;
            --plugin=*)
                plugin="${1#--plugin=}"
                shift
                ;;
            --skip-shims)
                skip_shims=1
                shift
                ;;
            --help|-h)
                head -20 "$0" | sed 's/^# \{0,1\}//' | sed -n '/^Usage:/,/^$/p'
                exit 0
                ;;
            --*)
                print_error "Unknown flag '$1'"
                exit 1
                ;;
            *)
                if [[ -n "$version" ]]; then
                    print_error "Unexpected extra argument '$1'"
                    exit 1
                fi
                version="$1"
                shift
                ;;
        esac
    done

    # Validate inputs
    validate_version_arg "$version"
    version="${version#v}"  # Strip 'v' prefix if present
    validate_semver_format "$version"

    if [[ "$skip_shims" -eq 1 && -z "$plugin" ]]; then
        print_error "--skip-shims requires --plugin <name>"
        exit 1
    fi

    # Validate --plugin exists in .version-bump.json before any gh API calls.
    if [[ -n "$plugin" ]]; then
        local config="$REPO_ROOT/.version-bump.json"
        if ! jq -e --arg p "$plugin" '.files[] | select(.plugin == $p)' "$config" >/dev/null 2>&1; then
            print_error "--plugin '$plugin' not found in .version-bump.json"
            echo "Available plugins:"
            jq -r '.files[].plugin' "$config" | sort -u | sed 's/^/  /'
            exit 1
        fi
    fi

    local changelog="CHANGELOG.md"
    local repo_url
    repo_url=$(gh repo view --json url -q '.url')

    if [[ -n "$plugin" ]]; then
        echo "Preparing release v$version for plugin '$plugin' (skip-shims: $skip_shims)..."
    else
        echo "Preparing release v$version..."
    fi
    echo ""

    # Pre-flight checks
    check_changelog_entry "$version" "$changelog"
    check_release_not_exists "v$version"

    # Per-plugin manifest bump (before changelog link insertion so the bumped
    # manifests are part of the same commit).
    local -a manifest_paths=()
    if [[ -n "$plugin" ]]; then
        bump_plugin_manifests "$plugin" "$version" "$skip_shims"
        while IFS= read -r path; do
            [[ -n "$path" ]] && manifest_paths+=("$path")
        done < <(bumped_manifest_paths "$plugin" "$skip_shims")
    fi

    # Update changelog links
    add_comparison_link "$version" "$changelog" "$repo_url"

    # Commit if needed (includes bumped manifests when --plugin is set)
    commit_changelog_changes "$version" "$changelog" "${manifest_paths[@]}"

    # Trigger and monitor workflow
    trigger_workflow "$version"
    wait_for_workflow "$version" "$repo_url"
}

main "$@"
