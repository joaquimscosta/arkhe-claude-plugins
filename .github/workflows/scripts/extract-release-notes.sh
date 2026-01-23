#!/usr/bin/env bash
#
# extract-release-notes.sh - Extract version section from CHANGELOG.md
#
# Usage: extract-release-notes.sh <version>
# Example: extract-release-notes.sh 1.4.0
#
# Output: Creates release_notes.md with the extracted content
#
# Exit codes:
#   0 - Release notes extracted successfully
#   1 - Missing arguments or extraction failed

set -euo pipefail

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
    echo "::error::Usage: extract-release-notes.sh <version>"
    exit 1
fi

# Strip 'v' prefix if present
VERSION="${VERSION#v}"

CHANGELOG_FILE="CHANGELOG.md"
OUTPUT_FILE="release_notes.md"

if [[ ! -f "$CHANGELOG_FILE" ]]; then
    echo "::error::$CHANGELOG_FILE not found"
    exit 1
fi

# Extract content between ## [VERSION] and the next ## [ header
# Using awk for reliable multi-line extraction
awk -v version="$VERSION" '
    # Match the start of our target version section
    /^## \[/ {
        # Check if this is our target version
        if ($0 ~ "^## \\[" version "\\]") {
            capture = 1
            next  # Skip the header line itself
        } else if (capture) {
            # We hit the next version section, stop capturing
            exit
        }
    }
    # Capture lines when in our target section
    capture { print }
' "$CHANGELOG_FILE" > "$OUTPUT_FILE"

# Check if we captured anything
if [[ ! -s "$OUTPUT_FILE" ]]; then
    echo "::error::Failed to extract release notes for version $VERSION"
    echo "Ensure CHANGELOG.md has content under the ## [$VERSION] header"
    exit 1
fi

# Remove leading blank lines
sed -i.bak '/./,$!d' "$OUTPUT_FILE" && rm -f "$OUTPUT_FILE.bak"

# Remove trailing blank lines
sed -i.bak -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$OUTPUT_FILE" && rm -f "$OUTPUT_FILE.bak"

echo "Extracted release notes for version $VERSION to $OUTPUT_FILE"
