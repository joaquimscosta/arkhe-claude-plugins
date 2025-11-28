#!/usr/bin/env bash

################################################################################
# update-claude-docs.sh
#
# Syncs official Claude Code documentation from the web to local files.
#
# Usage:
#   ./update-claude-docs.sh
#
# Requirements:
#   - Bash 3.2+ (macOS compatible)
#   - curl (with HTTPS support)
#
# Safety Features:
#   - Atomic file updates via temporary files
#   - Non-empty content validation before overwriting
#   - Automatic cleanup of temporary files on exit
#   - Graceful handling of individual file failures
#   - Preserves existing files when downloads fail
#
# Exit Codes:
#   0 - At least one file updated successfully
#   1 - All downloads failed or no files updated
################################################################################

set -euo pipefail

#------------------------------------------------------------------------------
# Configuration
#------------------------------------------------------------------------------

# Color codes for output
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[0;33m'
readonly NC='\033[0m' # No Color

# Script directory (where files will be saved)
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

# Temporary directory for downloads
TEMP_DIR=""

# Download timeout (seconds)
readonly CURL_TIMEOUT=30

# User agent string
readonly USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

#------------------------------------------------------------------------------
# URL to Filename Mappings
#------------------------------------------------------------------------------

# Array of URL|filename pairs (compatible with Bash 3.2+)
# Format: "URL|FILENAME"
#
# IMPORTANT: To add new documentation URLs, follow these steps:
#
# 1. Add a new line below in the format:
#    "https://full-url-to-documentation.md|TARGET_FILENAME.md"
#
# 2. Choose a filename that follows the existing naming convention:
#    - Use UPPERCASE_WITH_UNDERSCORES.md (e.g., CLAUDE_4_BEST_PRACTICES.md)
#    - Make the name descriptive and consistent with other files
#
# 3. Run the sync script to download the new documentation:
#    cd docs && ./update-claude-docs.sh
#
# 4. Update the following files to reference the new documentation:
#    - README.md (main repository README)
#    - CLAUDE.md (plugin development guide)
#    - docs/README.md (developer documentation index)
#
# Custom files that should NEVER be added to this sync list:
# - SKILL_DEVELOPMENT_BEST_PRACTICES.md (custom lessons learned)
# - README.md (custom documentation index)
# - Any other files created specifically for this project
#
readonly URL_MAPPINGS=(
    "https://docs.claude.com/en/docs/claude-code/sub-agents.md|SUBAGENTS.md"
    "https://docs.claude.com/en/docs/claude-code/plugins.md|PLUGINS.md"
    "https://docs.claude.com/en/docs/claude-code/hooks-guide.md|HOOKS.md"
    "https://docs.claude.com/en/docs/claude-code/slash-commands.md|COMMANDS.md"
    "https://docs.claude.com/en/docs/claude-code/skills.md|SKILLS.md"
    "https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview.md|AGENT_SKILLS_OVERVIEW.md"
    "https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices.md|CLAUDE_4_BEST_PRACTICES.md"
    "https://code.claude.com/docs/en/settings.md|SETTINGS.md"
)

#------------------------------------------------------------------------------
# Cleanup Handler
#------------------------------------------------------------------------------

cleanup() {
    if [[ -n "${TEMP_DIR}" && -d "${TEMP_DIR}" ]]; then
        rm -rf -- "${TEMP_DIR}"
    fi
}

trap cleanup EXIT INT TERM

#------------------------------------------------------------------------------
# Utility Functions
#------------------------------------------------------------------------------

# Print colored status message
print_status() {
    local color="$1"
    local message="$2"
    printf "${color}%s${NC}\n" "${message}" >&2
}

# Check if Bash version is compatible
check_bash_version() {
    if (( BASH_VERSINFO[0] < 3 )); then
        print_status "${RED}" "Error: This script requires Bash 3.2 or higher (current: ${BASH_VERSION})"
        exit 1
    fi
}

# Check if curl is available
check_dependencies() {
    if ! command -v curl &>/dev/null; then
        print_status "${RED}" "Error: curl is required but not installed"
        exit 1
    fi
}

# Download a URL to a temporary file
# Args: $1 = URL, $2 = temp file path
# Returns: 0 on success, 1 on failure
download_file() {
    local url="$1"
    local temp_file="$2"

    # Download with proper error handling
    if curl --silent --fail --show-error \
            --max-time "${CURL_TIMEOUT}" \
            --user-agent "${USER_AGENT}" \
            --output "${temp_file}" \
            --location \
            "${url}" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Validate that file has non-empty content
# Args: $1 = file path
# Returns: 0 if valid, 1 if empty or invalid
validate_content() {
    local file="$1"

    # Check if file exists and is not empty
    if [[ ! -f "${file}" ]]; then
        return 1
    fi

    # Check if file has content (more than just whitespace)
    if [[ ! -s "${file}" ]]; then
        return 1
    fi

    # Check if file has at least some meaningful content (more than 10 bytes)
    local file_size
    file_size=$(stat -f%z "${file}" 2>/dev/null || stat -c%s "${file}" 2>/dev/null || echo 0)

    if (( file_size < 10 )); then
        return 1
    fi

    return 0
}

# Atomically update a file from temporary location
# Args: $1 = temp file, $2 = target file
atomic_update() {
    local temp_file="$1"
    local target_file="$2"

    # Move temp file to target (atomic on same filesystem)
    mv -f -- "${temp_file}" "${target_file}"
}

#------------------------------------------------------------------------------
# Main Processing
#------------------------------------------------------------------------------

main() {
    local success_count=0
    local failure_count=0
    local skip_count=0
    local total_count=${#URL_MAPPINGS[@]}

    # Validate environment
    check_bash_version
    check_dependencies

    # Create temporary directory
    TEMP_DIR=$(mktemp -d -t claude-docs.XXXXXX)

    # Process each URL|filename pair
    for mapping in "${URL_MAPPINGS[@]}"; do
        # Split on pipe character: URL|FILENAME
        local url="${mapping%%|*}"
        local filename="${mapping##*|}"
        local target_file="${SCRIPT_DIR}/${filename}"
        local temp_file="${TEMP_DIR}/${filename}.tmp"

        # Download to temporary file
        if ! download_file "${url}" "${temp_file}"; then
            print_status "${RED}" "✗ Failed to download: ${filename}"
            ((failure_count++))
            continue
        fi

        # Validate content is non-empty
        if ! validate_content "${temp_file}"; then
            print_status "${YELLOW}" "⊖ Skipped (empty content): ${filename}"
            ((skip_count++))
            continue
        fi

        # Atomically update target file
        if atomic_update "${temp_file}" "${target_file}"; then
            print_status "${GREEN}" "✓ Updated: ${filename}"
            ((success_count++))
        else
            print_status "${RED}" "✗ Failed to update: ${filename}"
            ((failure_count++))
        fi
    done

    # Print summary
    echo ""
    printf "${GREEN}✓${NC} %d updated, ${RED}✗${NC} %d failed, ${YELLOW}⊖${NC} %d skipped (empty)\n" \
        "${success_count}" "${failure_count}" "${skip_count}"

    # Exit code: success if at least one file updated
    if (( success_count > 0 )); then
        exit 0
    else
        exit 1
    fi
}

#------------------------------------------------------------------------------
# Entry Point
#------------------------------------------------------------------------------

main "$@"
