#!/usr/bin/env bash
#
# validate-changelog.sh - Verify CHANGELOG.md has entry for specified version
#
# Usage: validate-changelog.sh <version>
# Example: validate-changelog.sh 1.4.0
#
# Exit codes:
#   0 - CHANGELOG entry found
#   1 - Missing arguments or CHANGELOG entry not found

set -euo pipefail

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
    echo "::error::Usage: validate-changelog.sh <version>"
    exit 1
fi

# Strip 'v' prefix if present
VERSION="${VERSION#v}"

CHANGELOG_FILE="CHANGELOG.md"

if [[ ! -f "$CHANGELOG_FILE" ]]; then
    echo "::error::$CHANGELOG_FILE not found"
    exit 1
fi

# Look for version header: ## [X.Y.Z] or ## [X.Y.Z] - DATE
# The header format follows Keep a Changelog: ## [1.4.0] - 2025-01-15
if grep -qE "^## \[$VERSION\]" "$CHANGELOG_FILE"; then
    echo "Found CHANGELOG entry for version $VERSION"
    exit 0
else
    echo "::error::No CHANGELOG entry found for version $VERSION"
    echo ""
    echo "Please add an entry to CHANGELOG.md with the header:"
    echo "  ## [$VERSION] - $(date +%Y-%m-%d)"
    echo ""
    echo "You can use the /changelog skill to generate the entry."
    exit 1
fi
