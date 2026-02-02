#!/usr/bin/env bash
#
# release.sh - Automate the full release process
#
# Usage: release.sh <version>
# Example: release.sh 1.6.0
#
# This script:
#   1. Validates version format
#   2. Checks CHANGELOG.md entry exists
#   3. Adds comparison link to CHANGELOG.md (if missing)
#   4. Commits and pushes CHANGELOG.md changes
#   5. Triggers the GitHub Actions release workflow
#   6. Monitors workflow and reports result
#
# Prerequisites:
#   - gh CLI installed and authenticated
#   - Git configured with push access
#   - CHANGELOG.md entry already added for the version

set -euo pipefail

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
        echo "Usage: release.sh <version>"
        echo "Example: release.sh 1.6.0"
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

    # Skip if no changes
    if git diff --quiet "$changelog" 2>/dev/null; then
        return 0
    fi

    echo ""
    echo "CHANGELOG.md has uncommitted changes."
    read -p "Commit and push? [y/N] " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Skipping commit. Run manually before triggering workflow."
        exit 0
    fi

    git add "$changelog"
    git commit -m "docs: prepare release $version"
    git push origin main
    print_success "Changes committed and pushed"
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
    local version="${1:-}"

    # Validate inputs
    validate_version_arg "$version"
    version="${version#v}"  # Strip 'v' prefix if present
    validate_semver_format "$version"

    local changelog="CHANGELOG.md"
    local repo_url
    repo_url=$(gh repo view --json url -q '.url')

    echo "Preparing release v$version..."
    echo ""

    # Pre-flight checks
    check_changelog_entry "$version" "$changelog"
    check_release_not_exists "v$version"

    # Update changelog links
    add_comparison_link "$version" "$changelog" "$repo_url"

    # Commit if needed
    commit_changelog_changes "$version" "$changelog"

    # Trigger and monitor workflow
    trigger_workflow "$version"
    wait_for_workflow "$version" "$repo_url"
}

main "$@"
