#!/usr/bin/env bash
# Pull Request creation workflow for Git workflow
# Handles PR creation across root repository and plan submodule

set -e

# Get script directory and source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_BASE_BRANCH="main"

# ============================================================================
# Argument Parsing
# ============================================================================

parse_arguments() {
    SCOPE=""
    BASE_BRANCH="$DEFAULT_BASE_BRANCH"
    DRAFT=false
    JSON_MODE=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json)
                JSON_MODE=true
                shift
                ;;
            --draft)
                DRAFT=true
                shift
                ;;
            --base)
                if [[ -n "${2:-}" ]] && [[ ! "$2" =~ ^-- ]]; then
                    BASE_BRANCH="$2"
                    shift 2
                else
                    error "--base requires a branch name"
                    exit 1
                fi
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
# Repository Context Detection
# ============================================================================

auto_detect_repository() {
    SCOPE=$(get_current_repository_context)
    info "Auto-detected repository: $SCOPE"
}

# ============================================================================
# Branch Validation
# ============================================================================

validate_branch_state() {
    local target_path="$1"

    cd "$target_path" || exit 1

    # Check current branch
    local current_branch
    current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

    if [[ -z "$current_branch" ]]; then
        error "Could not determine current branch"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "Could not determine current branch"
        exit 1
    fi

    # Cannot create PR from protected branches
    if is_protected_branch "$current_branch"; then
        error "Cannot create PR from protected branch: $current_branch"
        echo ""
        echo "You're currently on a protected branch. Please create a feature branch first:"
        echo "  git checkout -b feature/your-feature-name"
        echo ""
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "Cannot create PR from protected branch" "branch=$current_branch"
        exit 1
    fi

    # Check for uncommitted changes
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "⚠️  Warning: You have uncommitted changes in $SCOPE"
        echo ""
        echo "Uncommitted changes will NOT be included in the PR."
        read -p "Do you want to continue? [y/n]: " response
        if [[ "$response" != "y" ]]; then
            echo "PR creation cancelled"
            exit 1
        fi
    fi

    # Verify commits ahead of base branch
    local commits_ahead
    commits_ahead=$(git rev-list --count "${BASE_BRANCH}..HEAD" 2>/dev/null || echo "0")

    if [[ "$commits_ahead" -eq 0 ]]; then
        error "No commits ahead of $BASE_BRANCH"
        echo ""
        echo "Your branch has no new commits to create a PR."
        echo "Current branch: $current_branch"
        echo "Base branch: $BASE_BRANCH"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "No commits ahead of base branch" "base=$BASE_BRANCH" "current=$current_branch"
        exit 1
    fi

    success "$commits_ahead commits ahead of $BASE_BRANCH"

    # Return current branch
    echo "$current_branch"
}

# ============================================================================
# Remote Branch Management
# ============================================================================

ensure_branch_pushed() {
    local target_path="$1"
    local current_branch="$2"

    cd "$target_path" || exit 1

    # Check if branch exists on remote
    if ! git rev-parse --verify "origin/${current_branch}" >/dev/null 2>&1; then
        echo "📤 Branch not pushed to remote. Pushing now..."
        if git push -u origin "$current_branch"; then
            success "Branch pushed successfully"
        else
            error "Failed to push branch to remote"
            exit 1
        fi
    else
        success "Branch already pushed to remote"
    fi
}

# ============================================================================
# PR Existence Check
# ============================================================================

check_existing_pr() {
    local current_branch="$1"

    # Check if gh CLI is available
    if ! command -v gh &> /dev/null; then
        warn "GitHub CLI not found. Skipping PR existence check."
        return 0
    fi

    local existing_pr
    existing_pr=$(gh pr list --head "$current_branch" --json number,url,title,state --jq '.[0]' 2>/dev/null || echo "")

    if [[ -n "$existing_pr" && "$existing_pr" != "null" ]]; then
        local pr_number
        pr_number=$(echo "$existing_pr" | jq -r '.number')
        local pr_url
        pr_url=$(echo "$existing_pr" | jq -r '.url')
        local pr_title
        pr_title=$(echo "$existing_pr" | jq -r '.title')
        local pr_state
        pr_state=$(echo "$existing_pr" | jq -r '.state')

        echo "ℹ️  A pull request already exists for this branch:"
        echo "PR #$pr_number: $pr_title"
        echo "URL: $pr_url"
        echo "State: $pr_state"
        echo ""
        echo "What would you like to do?"
        echo "[u] Update PR (regenerate title/body from current commits)"
        echo "[v] View PR (open in browser)"
        echo "[c] Cancel"
        echo ""
        read -p "Choose an option [u/v/c]: " choice

        case "$choice" in
            u|U)
                info "Will update existing PR #$pr_number"
                # Return the PR number to signal update mode
                echo "UPDATE:$pr_number"
                return 0
                ;;
            v|V)
                info "Opening existing PR in browser..."
                gh pr view "$pr_number" --web 2>/dev/null || echo "$pr_url"
                [[ "$JSON_MODE" == "true" ]] && json_output "success" "PR viewed" "pr_number=$pr_number" "pr_url=$pr_url"
                exit 0
                ;;
            c|C|*)
                info "PR creation cancelled"
                [[ "$JSON_MODE" == "true" ]] && json_output "cancelled" "User cancelled" "pr_number=$pr_number"
                exit 0
                ;;
        esac
    fi
}

# ============================================================================
# PR Title Generation
# ============================================================================

generate_pr_title() {
    local target_path="$1"

    cd "$target_path" || exit 1

    # Get commit history
    local commits
    commits=$(git log "${BASE_BRANCH}..HEAD" --pretty=format:"%s" 2>/dev/null || echo "")

    if [[ -z "$commits" ]]; then
        echo "Update implementation"
        return
    fi

    # Count commit types
    local feat_count
    feat_count=$(echo "$commits" | grep -c "feat" || echo "0")
    local fix_count
    fix_count=$(echo "$commits" | grep -c "fix" || echo "0")
    local refactor_count
    refactor_count=$(echo "$commits" | grep -c "refactor" || echo "0")

    # Determine primary type
    local pr_type="feat"
    local max_count=$feat_count

    if [[ $fix_count -gt $max_count ]]; then
        pr_type="fix"
        max_count=$fix_count
    fi

    if [[ $refactor_count -gt $max_count ]]; then
        pr_type="refactor"
    fi

    # Get emoji
    local emoji
    emoji=$(get_commit_emoji "$pr_type")

    # Extract scope from repository name
    local pr_scope
    case "$SCOPE" in
        "plan")
            pr_scope="planning"
            ;;
        "root")
            # For root, determine scope from commits
            if echo "$commits" | grep -q "backend"; then
                pr_scope="backend"
            elif echo "$commits" | grep -q "frontend"; then
                pr_scope="frontend"
            elif echo "$commits" | grep -q "infra"; then
                pr_scope="infra"
            elif echo "$commits" | grep -q "docs"; then
                pr_scope="docs"
            else
                pr_scope="core"
            fi
            ;;
        *)
            pr_scope="core"
            ;;
    esac

    # Extract description from first commit
    local description
    description=$(echo "$commits" | head -1 | sed -E 's/^[^:]+: *//')

    echo "$emoji $pr_type($pr_scope): $description"
}

# ============================================================================
# PR Body Generation
# ============================================================================

generate_pr_body() {
    local target_path="$1"

    cd "$target_path" || exit 1

    # Get commit messages
    local commits
    commits=$(git log "${BASE_BRANCH}..HEAD" --pretty=format:"- %s" 2>/dev/null || echo "")

    # Extract issue references
    local issue_refs
    issue_refs=$(git log "${BASE_BRANCH}..HEAD" --pretty=format:"%s %b" | grep -oE "#[0-9]+" | sort -u | tr '\n' ' ' || echo "")

    # Build PR body
    cat <<EOF
## Issue

${issue_refs:+- resolves: $issue_refs}

## Why is this change needed?

This PR includes the following changes:

$commits

## Changes Made

$(git diff --stat "${BASE_BRANCH}..HEAD" | tail -1)

## Testing

- [ ] Tests added/updated
- [ ] Manual testing completed
- [ ] No breaking changes

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated (if needed)
EOF
}

# ============================================================================
# PR Update
# ============================================================================

update_pull_request() {
    local target_path="$1"
    local pr_number="$2"
    local title="$3"
    local body="$4"

    cd "$target_path" || exit 1

    # Check if gh CLI is available
    if ! command -v gh &> /dev/null; then
        error "GitHub CLI not found. Please install: https://cli.github.com"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "GitHub CLI not found"
        exit 1
    fi

    info "Updating PR #$pr_number..."

    # Update PR title and body
    if gh pr edit "$pr_number" --title "$title" --body "$body"; then
        success "Pull request updated successfully!"

        # Get updated PR details
        local pr_details
        pr_details=$(gh pr view "$pr_number" --json url,state,isDraft --jq '.')
        local pr_url
        pr_url=$(echo "$pr_details" | jq -r '.url')
        local pr_state
        pr_state=$(echo "$pr_details" | jq -r '.state')
        local is_draft
        is_draft=$(echo "$pr_details" | jq -r '.isDraft')

        echo ""
        echo "📝 Updated Title: $title"
        echo "🔗 URL: $pr_url"
        echo "🎯 Base: $BASE_BRANCH"
        if [[ "$is_draft" == "true" ]]; then
            echo "📋 Status: Draft"
        else
            echo "📋 Status: Ready for review"
        fi

        [[ "$JSON_MODE" == "true" ]] && json_output "success" "PR updated" "pr_url=$pr_url" "pr_number=$pr_number" "base=$BASE_BRANCH"
    else
        error "Failed to update pull request"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "Failed to update PR" "pr_number=$pr_number"
        exit 1
    fi
}

# ============================================================================
# PR Creation
# ============================================================================

create_pull_request() {
    local target_path="$1"
    local title="$2"
    local body="$3"

    cd "$target_path" || exit 1

    # Check if gh CLI is available
    if ! command -v gh &> /dev/null; then
        error "GitHub CLI not found. Please install: https://cli.github.com"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "GitHub CLI not found"
        exit 1
    fi

    # Build gh command
    local gh_cmd="gh pr create --title \"$title\" --body \"$body\" --base $BASE_BRANCH"

    if [[ "$DRAFT" == "true" ]]; then
        gh_cmd="$gh_cmd --draft"
    fi

    # Create PR
    local pr_url
    pr_url=$(eval "$gh_cmd" 2>&1)

    if [[ $? -eq 0 ]]; then
        success "Pull request created successfully!"

        # Extract PR number from URL
        local pr_number
        pr_number=$(echo "$pr_url" | grep -oE "[0-9]+$" || echo "")

        echo ""
        echo "📝 Title: $title"
        echo "🔗 URL: $pr_url"
        echo "🎯 Base: $BASE_BRANCH"
        if [[ "$DRAFT" == "true" ]]; then
            echo "📋 Status: Draft"
        else
            echo "📋 Status: Ready for review"
        fi

        [[ "$JSON_MODE" == "true" ]] && json_output "success" "PR created" "pr_url=$pr_url" "pr_number=$pr_number" "base=$BASE_BRANCH"
    else
        error "Failed to create pull request"
        echo "$pr_url"
        [[ "$JSON_MODE" == "true" ]] && json_output "error" "Failed to create PR" "message=$pr_url"
        exit 1
    fi
}

# ============================================================================
# Main Workflow
# ============================================================================

main() {
    # Parse arguments
    parse_arguments "$@"

    # Step 1: Determine scope (from args or auto-detect)
    if [[ -z "$SCOPE" ]]; then
        auto_detect_repository
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

    info "Creating PR for $SCOPE"
    echo "Base branch: $BASE_BRANCH"
    echo ""

    # Step 3: Validate branch state
    echo "Validating branch state..."
    local current_branch
    current_branch=$(validate_branch_state "$target_path")

    # Step 4: Ensure branch is pushed
    ensure_branch_pushed "$target_path" "$current_branch"

    # Step 5: Check for existing PR
    local existing_pr_check
    existing_pr_check=$(check_existing_pr "$current_branch")

    # Parse check result for update mode
    local update_mode=false
    local pr_number=""
    if [[ "$existing_pr_check" =~ ^UPDATE:([0-9]+)$ ]]; then
        update_mode=true
        pr_number="${BASH_REMATCH[1]}"
    fi

    # Step 6: Generate PR title
    echo "Generating PR title..."
    local pr_title
    pr_title=$(generate_pr_title "$target_path")

    echo ""
    if [[ "$update_mode" == "true" ]]; then
        echo "Generated updated PR title:"
    else
        echo "Generated PR title:"
    fi
    echo "$pr_title"
    echo ""
    read -p "Use this title? [y/n/edit]: " approval

    case "$approval" in
        y)
            # Use generated title
            ;;
        edit|n)
            read -p "Enter your PR title: " custom_title
            pr_title="$custom_title"
            ;;
        *)
            warn "Invalid response. Using generated title."
            ;;
    esac

    # Step 7: Generate PR body
    local pr_body
    pr_body=$(generate_pr_body "$target_path")

    # Step 8: Create or Update PR
    if [[ "$update_mode" == "true" ]]; then
        echo "Updating pull request #$pr_number..."
        update_pull_request "$target_path" "$pr_number" "$pr_title" "$pr_body"
    else
        echo "Creating pull request..."
        create_pull_request "$target_path" "$pr_title" "$pr_body"
    fi
}

# Run main workflow
main "$@"
