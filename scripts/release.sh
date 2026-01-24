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

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VERSION="${1:-}"

# --- Validation ---

if [[ -z "$VERSION" ]]; then
    echo -e "${RED}Error: Version required${NC}"
    echo "Usage: release.sh <version>"
    echo "Example: release.sh 1.6.0"
    exit 1
fi

# Strip 'v' prefix if present
VERSION="${VERSION#v}"

# Validate semver format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Error: Invalid version format '$VERSION'${NC}"
    echo "Expected semantic version (e.g., 1.6.0)"
    exit 1
fi

TAG="v$VERSION"
CHANGELOG_FILE="CHANGELOG.md"
REPO_URL=$(gh repo view --json url -q '.url')

echo "Preparing release $TAG..."
echo ""

# --- Check CHANGELOG entry exists ---

echo "Checking CHANGELOG.md for version $VERSION..."
if ! grep -qE "^## \[$VERSION\]" "$CHANGELOG_FILE"; then
    echo -e "${RED}Error: No CHANGELOG entry found for version $VERSION${NC}"
    echo ""
    echo "Please add an entry to CHANGELOG.md with the header:"
    echo "  ## [$VERSION] - $(date +%Y-%m-%d)"
    echo ""
    echo "Tip: Use '/changelog' in Claude Code to generate the entry."
    exit 1
fi
echo -e "${GREEN}✓ CHANGELOG entry found${NC}"

# --- Check if release already exists ---

echo "Checking if release $TAG already exists..."
if gh release view "$TAG" &>/dev/null; then
    echo -e "${RED}Error: Release $TAG already exists${NC}"
    echo "Delete it first with: gh release delete $TAG --yes"
    exit 1
fi
echo -e "${GREEN}✓ Release does not exist${NC}"

# --- Add comparison link if missing ---

echo "Checking comparison links..."

# Find the previous version (the one after the current version header in CHANGELOG)
PREV_VERSION=$(grep -E "^## \[[0-9]+\.[0-9]+\.[0-9]+\]" "$CHANGELOG_FILE" | head -2 | tail -1 | sed 's/.*\[\([0-9.]*\)\].*/\1/')

if [[ -z "$PREV_VERSION" ]] || [[ "$PREV_VERSION" == "$VERSION" ]]; then
    # This is the first version or we couldn't find previous
    PREV_VERSION=""
fi

# Check if comparison link already exists for this version
if grep -qE "^\[$VERSION\]:" "$CHANGELOG_FILE"; then
    echo -e "${GREEN}✓ Comparison link already exists${NC}"
else
    echo -e "${YELLOW}Adding comparison link for $VERSION...${NC}"

    # Build the comparison link
    if [[ -n "$PREV_VERSION" ]]; then
        COMPARE_LINK="[$VERSION]: $REPO_URL/compare/v$PREV_VERSION...v$VERSION"
    else
        COMPARE_LINK="[$VERSION]: $REPO_URL/releases/tag/v$VERSION"
    fi

    # Find the line with [Unreleased] link and update it, then add new version link
    if grep -qE "^\[Unreleased\]:" "$CHANGELOG_FILE"; then
        # Update [Unreleased] to point to new version
        sed -i.bak "s|\[Unreleased\]:.*|[Unreleased]: $REPO_URL/compare/v$VERSION...HEAD|" "$CHANGELOG_FILE"

        # Add new version link after [Unreleased]
        sed -i.bak "/^\[Unreleased\]:/a\\
$COMPARE_LINK" "$CHANGELOG_FILE"

        rm -f "$CHANGELOG_FILE.bak"
        echo -e "${GREEN}✓ Added comparison link${NC}"
    else
        echo -e "${YELLOW}Warning: Could not find [Unreleased] link to update${NC}"
        echo "Please manually add: $COMPARE_LINK"
    fi
fi

# --- Check for uncommitted changes ---

if ! git diff --quiet "$CHANGELOG_FILE" 2>/dev/null; then
    echo ""
    echo "CHANGELOG.md has uncommitted changes."
    read -p "Commit and push? [y/N] " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add "$CHANGELOG_FILE"
        git commit -m "docs: prepare release $VERSION"
        git push origin main
        echo -e "${GREEN}✓ Changes committed and pushed${NC}"
    else
        echo -e "${YELLOW}Skipping commit. Run manually before triggering workflow.${NC}"
        exit 0
    fi
fi

# --- Trigger workflow ---

echo ""
echo "Triggering release workflow for $TAG..."
gh workflow run release.yml -f version="$VERSION"
echo -e "${GREEN}✓ Workflow triggered${NC}"

# --- Wait for workflow ---

echo ""
echo "Waiting for workflow to start..."
sleep 5

RUN_ID=$(gh run list --workflow=release.yml --limit=1 --json databaseId -q '.[0].databaseId')

if [[ -z "$RUN_ID" ]]; then
    echo -e "${RED}Error: Could not find workflow run${NC}"
    exit 1
fi

echo "Monitoring workflow run $RUN_ID..."
echo "View at: $REPO_URL/actions/runs/$RUN_ID"
echo ""

# Poll for completion
while true; do
    STATUS=$(gh run view "$RUN_ID" --json status,conclusion -q '.status')

    if [[ "$STATUS" == "completed" ]]; then
        CONCLUSION=$(gh run view "$RUN_ID" --json conclusion -q '.conclusion')
        break
    fi

    echo "  Status: $STATUS..."
    sleep 5
done

echo ""

if [[ "$CONCLUSION" == "success" ]]; then
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}  Release $TAG created successfully!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo "View release: $REPO_URL/releases/tag/$TAG"
else
    echo -e "${RED}═══════════════════════════════════════${NC}"
    echo -e "${RED}  Workflow failed with: $CONCLUSION${NC}"
    echo -e "${RED}═══════════════════════════════════════${NC}"
    echo ""
    echo "View logs: $REPO_URL/actions/runs/$RUN_ID"
    exit 1
fi
