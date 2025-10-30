#!/usr/bin/env bash
# Branch creation script for Git workflow
# Creates feature branches with optimized short naming: {type}/{number}-{word1}-{word2}

set -e

# Get script directory and source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# ============================================================================
# Helper Functions
# ============================================================================

# Map keyword to commit type (Bash 3.2 compatible)
keyword_to_type() {
    local keyword="$1"
    case "$keyword" in
        # feat keywords
        add|create|implement|new|update|improve|enhance|optimize)
            echo "feat"
            ;;
        # fix keywords
        fix|bug|resolve|correct|repair)
            echo "fix"
            ;;
        # refactor keywords
        refactor|rename|reorganize|restructure|rewrite)
            echo "refactor"
            ;;
        # chore keywords
        remove|delete|clean|cleanup)
            echo "chore"
            ;;
        # docs keywords
        docs|document|documentation)
            echo "docs"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Check if word is a commit type keyword
is_commit_type_keyword() {
    local word="$1"
    [[ -n "$(keyword_to_type "$word")" ]]
}

# ============================================================================
# Argument Parsing
# ============================================================================

parse_arguments() {
    JSON_MODE=false
    FEATURE_DESCRIPTION=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json)
                JSON_MODE=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                FEATURE_DESCRIPTION="$FEATURE_DESCRIPTION $1"
                shift
                ;;
        esac
    done

    # Trim leading/trailing spaces
    FEATURE_DESCRIPTION="${FEATURE_DESCRIPTION## }"
    FEATURE_DESCRIPTION="${FEATURE_DESCRIPTION%% }"

    if [[ -z "$FEATURE_DESCRIPTION" ]]; then
        error "Feature description is required"
        echo ""
        show_usage
        exit 1
    fi
}

show_usage() {
    cat <<EOF
Usage: $0 [--json] <feature_description>

Creates a new feature branch with optimized short naming.

Format: {type}/{number}-{word1}-{word2}

Examples:
  $0 add newsletter signup
  # Creates: feat/003-newsletter-signup

  $0 fix authentication bug
  # Creates: fix/004-authentication-bug

  $0 refactor content planner agent
  # Creates: refactor/005-content-planner

Options:
  --json    Output results in JSON format
  --help    Show this help message
EOF
}

# ============================================================================
# Commit Type Detection
# ============================================================================

detect_commit_type() {
    local description="$1"
    local first_word

    # Convert to lowercase and get first word
    first_word=$(echo "$description" | tr '[:upper:]' '[:lower:]' | awk '{print $1}')

    # Check if first word matches any keyword
    local detected_type
    detected_type=$(keyword_to_type "$first_word")

    if [[ -n "$detected_type" ]]; then
        echo "$detected_type"
        return 0
    fi

    # Default to feat
    echo "feat"
}

# ============================================================================
# Keyword Removal
# ============================================================================

remove_commit_type_keywords() {
    local description="$1"
    local words=()

    # Convert to lowercase and split into words
    local lowercase
    lowercase=$(echo "$description" | tr '[:upper:]' '[:lower:]')

    # Read words into array
    while IFS= read -r word; do
        words+=("$word")
    done < <(echo "$lowercase" | tr ' ' '\n')

    # Filter out commit type keywords
    local filtered_words=()
    for word in "${words[@]}"; do
        # Skip if word is a commit type keyword
        if ! is_commit_type_keyword "$word"; then
            filtered_words+=("$word")
        fi
    done

    # Join words back together
    echo "${filtered_words[*]}"
}

# ============================================================================
# Branch Name Generation
# ============================================================================

generate_branch_name() {
    local description="$1"
    local feature_num="$2"

    # Step 1: Detect commit type
    local commit_type
    commit_type=$(detect_commit_type "$description")

    # Step 2: Remove commit type keywords from description
    local clean_description
    clean_description=$(remove_commit_type_keywords "$description")

    # Step 3: Sanitize description (replace non-alphanumeric with dashes)
    local sanitized
    sanitized=$(echo "$clean_description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')

    # Step 4: Extract first 2 words
    local words
    words=$(echo "$sanitized" | tr '-' '\n' | grep -v '^$' | head -2 | tr '\n' '-' | sed 's/-$//')

    # Step 5: Construct branch name
    echo "${commit_type}/${feature_num}-${words}"
}

# ============================================================================
# Feature Number Management
# ============================================================================

get_next_feature_number() {
    local monorepo_root
    monorepo_root="$(get_monorepo_root)"

    local specs_dir="$monorepo_root/${FEATURE_DIR:-plan/specs}"

    # Create directory if it doesn't exist
    mkdir -p "$specs_dir"

    # Find highest feature number
    local highest=0
    if [[ -d "$specs_dir" ]]; then
        for dir in "$specs_dir"/*; do
            [[ -d "$dir" ]] || continue
            local dirname
            dirname=$(basename "$dir")
            local number
            number=$(echo "$dirname" | grep -o '^[0-9]\+' || echo "0")
            number=$((10#$number))
            if [[ "$number" -gt "$highest" ]]; then
                highest=$number
            fi
        done
    fi

    local next=$((highest + 1))
    printf "%03d" "$next"
}

# ============================================================================
# Branch Creation
# ============================================================================

create_branch() {
    local branch_name="$1"
    local feature_num="$2"
    local monorepo_root
    monorepo_root="$(get_monorepo_root)"

    cd "$monorepo_root" || exit 1

    # Check if branch already exists
    if git rev-parse --verify "$branch_name" >/dev/null 2>&1; then
        error "Branch already exists: $branch_name"
        echo ""
        echo "To switch to this branch, run:"
        echo "  git checkout $branch_name"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "Branch already exists" "branch=$branch_name"
        exit 1
    fi

    # Create and checkout new branch
    if git checkout -b "$branch_name"; then
        success "Created and checked out branch: $branch_name"

        # Create feature directory only if spec-kit is installed (checks for .specify directory)
        if [[ -d "$monorepo_root/.specify" ]]; then
            local feature_dir="$monorepo_root/${FEATURE_DIR:-plan/specs}/$branch_name"
            mkdir -p "$feature_dir"
        fi

        return 0
    else
        error "Failed to create branch: $branch_name"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "Failed to create branch" "branch=$branch_name"
        exit 1
    fi
}

# ============================================================================
# Main Workflow
# ============================================================================

main() {
    # Parse arguments
    parse_arguments "$@"

    # Get monorepo root
    local monorepo_root
    monorepo_root="$(get_monorepo_root)"

    # Get next feature number
    info "Determining next feature number..."
    local feature_num
    feature_num=$(get_next_feature_number)

    # Generate branch name
    info "Generating branch name from: $FEATURE_DESCRIPTION"
    local branch_name
    branch_name=$(generate_branch_name "$FEATURE_DESCRIPTION" "$feature_num")

    # Show proposed branch name
    echo ""
    echo "Proposed branch name: $branch_name"
    echo ""
    read -p "Create this branch? [Y/n]: " response
    response="${response:-y}"

    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Branch creation cancelled"
        [[ "$JSON_MODE" == "true" ]] && json_output "cancelled" "User cancelled"
        exit 0
    fi

    # Create branch
    echo ""
    create_branch "$branch_name" "$feature_num"

    # Show summary
    echo ""
    echo "✨ Branch created successfully!"
    echo ""
    echo "📋 Branch: $branch_name"
    echo "🔢 Feature number: $feature_num"

    # Only display spec directory if spec-kit is installed
    if [[ -d "$monorepo_root/.specify" ]]; then
        echo "📁 Spec directory: ${FEATURE_DIR:-plan/specs}/$branch_name"
    fi

    echo ""
    echo "Next steps:"
    echo "  1. Make your changes"
    echo "  2. Commit with: /commit"
    echo "  3. Create PR with: /create-pr"

    # JSON output if requested
    if [[ "$JSON_MODE" == "true" ]]; then
        json_output "success" "Branch created" "branch=$branch_name" "feature_num=$feature_num" "spec_dir=${FEATURE_DIR:-plan/specs}/$branch_name"
    fi
}

# Run main workflow
main "$@"
