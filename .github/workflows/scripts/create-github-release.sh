#!/usr/bin/env bash
#
# create-github-release.sh - Create GitHub Release via gh CLI
#
# Usage: create-github-release.sh <tag>
# Example: create-github-release.sh v1.4.0
#
# Prerequisites:
#   - GH_TOKEN environment variable set
#   - release_notes.md file exists
#
# Exit codes:
#   0 - Release created successfully
#   1 - Missing arguments or release creation failed

set -euo pipefail

TAG="${1:-}"

if [[ -z "$TAG" ]]; then
    echo "::error::Usage: create-github-release.sh <tag>"
    exit 1
fi

# Ensure tag has 'v' prefix
if [[ ! "$TAG" =~ ^v ]]; then
    TAG="v$TAG"
fi

RELEASE_NOTES_FILE="release_notes.md"

if [[ ! -f "$RELEASE_NOTES_FILE" ]]; then
    echo "::error::$RELEASE_NOTES_FILE not found. Run extract-release-notes.sh first."
    exit 1
fi

if [[ -z "${GH_TOKEN:-}" ]]; then
    echo "::error::GH_TOKEN environment variable not set"
    exit 1
fi

# Create the release
# - Uses the tag that was created/verified earlier
# - Reads body from release_notes.md
# - No custom artifacts (GitHub auto-includes source tarball/zipball)
gh release create "$TAG" \
    --title "$TAG" \
    --notes-file "$RELEASE_NOTES_FILE"

echo "Successfully created GitHub Release $TAG"
