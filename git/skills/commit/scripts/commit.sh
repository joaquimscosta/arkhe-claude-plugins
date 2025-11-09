#!/usr/bin/env bash
# Commit workflow for Git workflow
# Handles commits across root repository and plan submodule

set -e

# Get script directory and source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# ============================================================================
# Configuration
# ============================================================================

# Valid scopes: root (main repository) and plan (planning submodule)
VALID_SCOPES=("root" "plan")

# ============================================================================
# Argument Parsing
# ============================================================================

parse_arguments() {
    SCOPE=""
    FLAG=""
    JSON_MODE=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json)
                JSON_MODE=true
                shift
                ;;
            --no-verify|--full-verify)
                FLAG="$1"
                shift
                ;;
            -*)
                error "Unknown flag: $1"
                exit 1
                ;;
            *)
                if [[ -z "$SCOPE" ]]; then
                    SCOPE="$1"
                fi
                shift
                ;;
        esac
    done
}

# ============================================================================
# Interactive Selection
# ============================================================================

interactive_repository_selection() {
    # Build array of repositories with changes (Bash 3.2+ compatible)
    local repos_with_changes=()
    while IFS= read -r line; do
        repos_with_changes+=("$line")
    done < <(detect_repositories_with_changes)

    if [[ ${#repos_with_changes[@]} -eq 0 ]]; then
        error "No changes detected in any repository"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "No changes detected"
        exit 1
    fi

    if [[ ${#repos_with_changes[@]} -eq 1 ]]; then
        # Auto-select the only repository with changes
        SCOPE="${repos_with_changes[0]}"
        info "Auto-selected: $SCOPE (only repository with changes)"
        return 0
    fi

    # Multiple repositories with changes - show interactive selection
    echo "Found changes in:"
    local i=1
    for repo in "${repos_with_changes[@]}"; do
        local repo_path
        repo_path=$(resolve_repository_path "$repo")
        local change_count
        change_count=$(cd "$repo_path" && git status --porcelain | wc -l | tr -d ' ')
        echo "$i. $repo ($change_count files modified)"
        ((i++))
    done
    echo ""
    echo "Which repository would you like to commit?"
    read -p "Enter number (1-${#repos_with_changes[@]}): " selection

    if [[ ! "$selection" =~ ^[0-9]+$ ]] || [[ "$selection" -lt 1 ]] || [[ "$selection" -gt ${#repos_with_changes[@]} ]]; then
        error "Invalid selection: $selection"
        exit 1
    fi

    SCOPE="${repos_with_changes[$((selection-1))]}"
    success "Selected: $SCOPE"
}

# ============================================================================
# File Staging
# ============================================================================

stage_files() {
    local target_path="$1"

    cd "$target_path" || exit 1

    # Check if any files are already staged
    local staged
    staged=$(git diff --cached --name-only)

    if [[ -z "$staged" ]]; then
        # No files staged, check for unstaged changes
        local unstaged
        unstaged=$(git status --porcelain)

        if [[ -z "$unstaged" ]]; then
            error "No changes to commit in $SCOPE"
            [[ "$JSON_MODE" == "true" ]] && json_output "error" "No changes to commit" "scope=$SCOPE"
            exit 1
        fi

        # Stage all changes
        git add .
        success "Staged all changes in $SCOPE"
    else
        info "Using already staged files in $SCOPE"
        # Show what's staged
        git diff --cached --name-status
    fi
}

# ============================================================================
# Commit Message Generation
# ============================================================================

suggest_commit_message() {
    local target_path="$1"
    local scope_name="$2"

    cd "$target_path" || exit 1

    # Determine commit type
    local commit_type
    commit_type=$(determine_commit_type "$target_path")

    # Get emoji
    local emoji
    emoji=$(get_commit_emoji "$commit_type")

    # Analyze changes to generate description
    local files_changed
    files_changed=$(git diff --cached --name-only | head -5)

    # Extract a simple scope from the repository name
    local commit_scope
    case "$scope_name" in
        "plan")
            commit_scope="planning"
            ;;
        "root")
            # For root, detect subsystem based on files changed
            if echo "$files_changed" | grep -q "^backend/"; then
                commit_scope="backend"
            elif echo "$files_changed" | grep -q "^frontend/"; then
                commit_scope="frontend"
            elif echo "$files_changed" | grep -q "^infrastructure/"; then
                commit_scope="infra"
            elif echo "$files_changed" | grep -q "^docs/"; then
                commit_scope="docs"
            else
                commit_scope="core"
            fi
            ;;
        *)
            commit_scope="core"
            ;;
    esac

    # Generate a simple description based on files changed
    local description
    if echo "$files_changed" | grep -q "\.kt"; then
        description="update Kotlin implementation"
    elif echo "$files_changed" | grep -q "\.ts\|\.tsx\|\.js\|\.jsx"; then
        description="update frontend components"
    elif echo "$files_changed" | grep -q "\.md"; then
        description="update documentation"
    elif echo "$files_changed" | grep -q "build\.gradle\.kts\|package\.json"; then
        description="update dependencies"
    elif echo "$files_changed" | grep -q "\.tf"; then
        description="update infrastructure"
    else
        description="update implementation"
    fi

    # Construct the suggested message
    echo "$emoji $commit_type($commit_scope): $description"
}

# ============================================================================
# Commit Creation
# ============================================================================

create_commit() {
    local target_path="$1"
    local message="$2"

    cd "$target_path" || exit 1

    # Create the commit
    git commit -m "$message"

    if [[ $? -eq 0 ]]; then
        # Verify no Claude Code footer was added
        local commit_msg
        commit_msg=$(git log -1 --pretty=%B)

        if echo "$commit_msg" | grep -q "Generated with.*Claude Code\|Co-Authored-By: Claude"; then
            error "CRITICAL: Claude Code footer detected in commit message!"
            error "This violates the no-footer policy."
            echo ""
            echo "Commit message contains prohibited attribution:"
            echo "$commit_msg" | grep -E "Generated with.*Claude Code|Co-Authored-By: Claude"
            echo ""
            error "Please report this issue - the commit was created but contains unwanted attribution."
            exit 1
        fi

        success "Committed changes in $SCOPE"
        echo "📝 Commit: $message"
        local branch
        branch=$(git rev-parse --abbrev-ref HEAD)
        echo "🔗 Branch: $branch"
    else
        error "Commit failed"
        echo "Please check the error message above"
        exit 1
    fi
}

# ============================================================================
# Post-Commit Summary
# ============================================================================

show_post_commit_summary() {
    local target_path="$1"

    cd "$target_path" || exit 1

    echo ""
    echo "Latest commit:"
    git log -1 --oneline

    echo ""
    echo "📤 Ready to push? Run: git push"

    # Special handling for plan submodule commits
    if [[ "$SCOPE" == "plan" ]]; then
        echo ""
        handle_submodule_reference_update
    fi
}

# ============================================================================
# Submodule Reference Update
# ============================================================================

handle_submodule_reference_update() {
    local monorepo_root
    monorepo_root="$(get_monorepo_root)"

    # Check root repository status
    cd "$monorepo_root" || return 0

    local root_status
    root_status=$(git status --porcelain 2>/dev/null || echo "")

    # Check if plan/ submodule is modified
    if ! echo "$root_status" | grep -q "^ M plan$"; then
        # No submodule reference change detected
        return 0
    fi

    # Count non-submodule changes
    local other_changes
    other_changes=$(echo "$root_status" | grep -v "^ M plan$" | wc -l | tr -d ' ')

    # Determine prompt based on whether root has other changes
    local prompt_message
    local default_response

    if [[ "$other_changes" -eq 0 ]]; then
        # Only plan/ is modified - clean case
        prompt_message="📤 Commit submodule reference to root? [Y/n]"
        default_response="y"
    else
        # Root has other changes - mixed case
        echo "⚠️  Root repository has other uncommitted changes."
        prompt_message="📤 Commit submodule reference separately? [y/N]"
        default_response="n"
    fi

    # Show prompt
    read -p "$prompt_message: " response
    response="${response:-$default_response}"

    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        # User declined or chose not to commit
        if [[ "$other_changes" -gt 0 ]]; then
            echo ""
            echo "ℹ️  Note: The root repository shows plan/ as modified."
            echo "   You can commit it later with: /commit root"
        fi
        return 0
    fi

    # User accepted - commit the submodule reference
    echo ""
    echo "Committing submodule reference..."

    # Stage only the plan/ submodule
    git add plan

    # Get the new submodule commit hash
    local submodule_hash
    submodule_hash=$(git diff --cached plan | grep "^+Subproject commit" | awk '{print $3}' | cut -c1-7)

    # Generate commit message
    local commit_message="🔖 chore(submodule): update plan to ${submodule_hash}"

    # Create the commit
    if git commit -m "$commit_message" >/dev/null 2>&1; then
        # Verify no Claude Code footer was added
        local commit_msg
        commit_msg=$(git log -1 --pretty=%B)

        if echo "$commit_msg" | grep -q "Generated with.*Claude Code\|Co-Authored-By: Claude"; then
            error "CRITICAL: Claude Code footer detected in submodule commit!"
            error "This violates the no-footer policy."
            echo ""
            echo "Commit message contains prohibited attribution:"
            echo "$commit_msg" | grep -E "Generated with.*Claude Code|Co-Authored-By: Claude"
            echo ""
            error "Please report this issue - the commit was created but contains unwanted attribution."
            return 1
        fi

        success "Submodule reference committed"
        echo "📝 Commit: $commit_message"
        echo "🔗 Branch: $(git rev-parse --abbrev-ref HEAD)"
        echo ""
        echo "📤 Ready to push? Run: git push"
    else
        error "Failed to commit submodule reference"
        return 1
    fi
}

# ============================================================================
# Main Workflow
# ============================================================================

main() {
    # Parse arguments
    parse_arguments "$@"

    # Step 1: Determine scope (from args or interactive selection)
    if [[ -z "$SCOPE" ]]; then
        interactive_repository_selection
    fi

    # Step 2: Resolve target repository path
    local target_path
    target_path=$(resolve_repository_path "$SCOPE")

    # Validate the path exists
    if [[ ! -d "$target_path" ]]; then
        error "Repository not found: $SCOPE"
        echo "Path: $target_path"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "Repository not found" "scope=$SCOPE" "path=$target_path"
        exit 1
    fi

    # Validate it's a git repository
    if ! git -C "$target_path" rev-parse --git-dir >/dev/null 2>&1; then
        error "Not a git repository: $SCOPE"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "Not a git repository" "scope=$SCOPE"
        exit 1
    fi

    # Step 3: Check branch protection
    echo "Checking branch protection..."
    local current_branch
    current_branch=$(check_branch_protection "$target_path" "$SCOPE")
    success "Current branch: $current_branch (safe to commit)"

    # Step 4: Run pre-commit checks
    if ! run_scope_checks "$SCOPE" "$FLAG"; then
        echo ""
        echo "⚠️  Pre-commit checks failed."
        read -p "Do you want to commit anyway? (not recommended) [y/n]: " response
        if [[ "$response" != "y" ]]; then
            echo "Commit cancelled"
            exit 1
        fi
    else
        success "Pre-commit checks passed"
    fi

    # Step 5: Stage files
    echo "Staging files..."
    stage_files "$target_path"

    # Step 6: Suggest commit message
    echo "Analyzing changes..."
    local suggested_message
    suggested_message=$(suggest_commit_message "$target_path" "$SCOPE")

    echo ""
    echo "Suggested commit message:"
    echo "$suggested_message"
    echo ""
    read -p "Approve this message? [y/n/edit]: " approval

    local final_message="$suggested_message"
    case "$approval" in
        y)
            final_message="$suggested_message"
            ;;
        edit)
            read -p "Enter your commit message: " custom_message
            final_message="$custom_message"
            ;;
        n)
            read -p "Enter your commit message: " custom_message
            final_message="$custom_message"
            ;;
        *)
            error "Invalid response. Using suggested message."
            final_message="$suggested_message"
            ;;
    esac

    # Step 7: Create commit
    echo "Creating commit..."
    create_commit "$target_path" "$final_message"

    # Step 8: Show post-commit summary
    show_post_commit_summary "$target_path"

    # JSON output if requested
    if [[ "$JSON_MODE" == "true" ]]; then
        local commit_hash
        commit_hash=$(cd "$target_path" && git rev-parse --short HEAD)
        json_output "success" "Commit created" "scope=$SCOPE" "branch=$current_branch" "commit=$commit_hash"
    fi
}

# Run main workflow
main "$@"
