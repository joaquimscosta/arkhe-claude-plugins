#!/usr/bin/env bash
# Common utilities for Git workflow commands
# Shared functions for commit, PR, and branching workflows
#
# ============================================================================
# Output Guidelines
# ============================================================================
#
# Use STDERR (>&2) for:
#   - Actual errors (via error() function)
#   - Warnings (via warn() function)
#
# Use STDOUT (default echo) for:
#   - Interactive prompts and questions
#   - User action confirmations (e.g., "Commit cancelled")
#   - Informational messages (via info() function)
#   - Success messages (via success() function)
#   - Debug/diagnostic info (e.g., "Path: /some/path")
#   - Progress updates
#
# Why? Claude Code displays stderr in RED, which should be reserved for
# actual errors. Interactive prompts, confirmations, and informational
# messages should use stdout for a better user experience.
#
# ============================================================================

set -e

# ============================================================================
# Core Path Resolution Functions
# ============================================================================

# Get the project root, working from any directory in the repository
# Works whether you're in root repo or the plan submodule
get_monorepo_root() {
    if SUPERPROJECT=$(git rev-parse --show-superproject-working-tree 2>/dev/null) && [ -n "$SUPERPROJECT" ]; then
        # We're in a submodule
        echo "$SUPERPROJECT"
    else
        # We're in the root repository or standalone repo
        git rev-parse --show-toplevel 2>/dev/null || {
            echo "❌ Error: Not in a git repository" >&2
            exit 1
        }
    fi
}

# Resolve a scope name to an absolute repository path
# Args:
#   $1 - scope ("root" or "plan")
# Returns: absolute path to the repository
resolve_repository_path() {
    local scope="$1"
    local monorepo_root
    monorepo_root="$(get_monorepo_root)"

    case "$scope" in
        "root")
            echo "$monorepo_root"
            ;;
        "plan")
            echo "$monorepo_root/plan"
            ;;
        *)
            # Invalid scope
            echo "$monorepo_root"
            ;;
    esac
}

# ============================================================================
# Repository Detection Functions
# ============================================================================

# Detect all repositories with changes
# Returns: array of scopes with changes (one per line)
detect_repositories_with_changes() {
    local monorepo_root
    monorepo_root="$(get_monorepo_root)"
    local repos_with_changes=()

    # Check root repository
    if cd "$monorepo_root" && [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
        repos_with_changes+=("root")
    fi

    # Check plan submodule
    local plan_path="$monorepo_root/plan"
    if [[ -d "$plan_path" ]] && cd "$plan_path" && [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
        repos_with_changes+=("plan")
    fi

    # Output results
    printf '%s\n' "${repos_with_changes[@]}"
}

# Get current repository context based on pwd
# Returns: scope name ("plan" or "root")
get_current_repository_context() {
    local current_dir
    current_dir="$(pwd)"
    local monorepo_root
    monorepo_root="$(get_monorepo_root)"

    # Check if we're in the plan submodule
    if [[ "$current_dir" =~ $monorepo_root/plan ]]; then
        echo "plan"
        return
    fi

    # Default to root
    echo "root"
}

# ============================================================================
# Branch Protection and Validation
# ============================================================================

# Check if branch is protected (main only)
# Args:
#   $1 - branch name
# Returns: 0 if protected, 1 if not
is_protected_branch() {
    local branch="$1"
    [[ "$branch" == "main" ]]
}

# Check branch protection for a repository
# Args:
#   $1 - target repository path
#   $2 - scope (optional: "root" or "plan")
# Returns: 0 if safe to commit, exits with error if protected
check_branch_protection() {
    local target_path="$1"
    local scope="${2:-root}"
    local current_branch

    cd "$target_path" || {
        echo "❌ Error: Cannot access repository: $target_path" >&2
        exit 1
    }

    current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

    if [[ -z "$current_branch" ]]; then
        echo "❌ Error: Could not determine current branch" >&2
        exit 1
    fi

    # Only enforce main branch protection for root repository
    # Plan submodule (documentation) can commit directly to main
    if is_protected_branch "$current_branch" && [[ "$scope" == "root" ]]; then
        echo "❌ Cannot commit to protected branch: $current_branch" >&2
        echo "" >&2
        echo "The main branch requires pull requests." >&2
        echo "Please create a feature branch first:" >&2
        echo "" >&2
        echo "  git checkout -b feature/your-feature-name" >&2
        echo "" >&2
        exit 1
    fi

    echo "$current_branch"
}

# ============================================================================
# Pre-commit Check Functions
# ============================================================================

# Run scope-specific pre-commit checks with smart detection
# Args:
#   $1 - scope ("root" or "plan")
#   $2 - flag (optional: "--no-verify", "--full-verify")
# Returns: 0 on success, 1 on failure
run_scope_checks() {
    local scope="$1"
    local flag="${2:-}"
    local monorepo_root
    monorepo_root="$(get_monorepo_root)"

    # Skip checks if --no-verify flag is set
    if [[ "$flag" == "--no-verify" ]]; then
        echo "⚠️  Skipping pre-commit checks (--no-verify flag)"
        return 0
    fi

    # Plan submodule: skip all checks (documentation only)
    if [[ "$scope" == "plan" ]]; then
        info "Skipping checks for plan submodule (documentation)"
        return 0
    fi

    # Run full build if --full-verify flag is set
    if [[ "$flag" == "--full-verify" ]]; then
        echo "Running full build verification..."
        cd "$monorepo_root"

        # Backend full build
        echo "Building backend..."
        cd "$monorepo_root/backend"
        ./gradlew build test || return 1

        # Frontend full build
        echo "Building frontend..."
        cd "$monorepo_root/frontend"
        npm run build || return 1

        success "Full build verification passed"
        return 0
    fi

    # Smart detection for root scope
    cd "$monorepo_root"

    # Get list of staged files
    local changed_files
    changed_files=$(git diff --cached --name-only 2>/dev/null || echo "")

    if [[ -z "$changed_files" ]]; then
        info "No staged files to check"
        return 0
    fi

    # Detect file types
    local has_kotlin=false
    local has_typescript=false

    if echo "$changed_files" | grep -q '\.kt$'; then
        has_kotlin=true
    fi

    if echo "$changed_files" | grep -q '\.(ts|tsx)$'; then
        has_typescript=true
    fi

    # Run appropriate checks based on detected file types
    local checks_run=false

    if [[ "$has_kotlin" == "true" ]]; then
        echo "Running backend checks (Kotlin files detected)..."
        cd "$monorepo_root/backend"
        ./gradlew detekt || return 1
        checks_run=true
    fi

    if [[ "$has_typescript" == "true" ]]; then
        echo "Running frontend checks (TypeScript files detected)..."
        cd "$monorepo_root/frontend"
        npx tsc --noEmit || return 1
        checks_run=true
    fi

    if [[ "$checks_run" == "false" ]]; then
        info "No code files detected that require type checking"
    else
        success "Pre-commit checks passed"
    fi

    return 0
}

# ============================================================================
# Commit Message Utilities
# ============================================================================

# Determine conventional commit type from git diff
# Args:
#   $1 - target repository path
# Returns: commit type (feat, fix, refactor, etc.)
determine_commit_type() {
    local target_path="$1"
    cd "$target_path" || return 1

    # Get diff statistics
    local diff_output
    diff_output=$(git diff --cached --stat 2>/dev/null || echo "")

    # Simple heuristic based on file patterns
    if echo "$diff_output" | grep -q "test\|spec"; then
        echo "test"
    elif echo "$diff_output" | grep -q "\.md\|README\|docs/"; then
        echo "docs"
    elif echo "$diff_output" | grep -q "build\.gradle\|package\.json\|pom\.xml"; then
        echo "build"
    elif echo "$diff_output" | grep -q "\.github\|\.gitlab\|Jenkinsfile"; then
        echo "ci"
    else
        # Default to feat for most changes
        echo "feat"
    fi
}

# Get emoji for commit type
# Args:
#   $1 - commit type
# Returns: emoji
get_commit_emoji() {
    local type="$1"
    case "$type" in
        "feat") echo "✨" ;;
        "fix") echo "🐛" ;;
        "refactor") echo "♻️" ;;
        "perf") echo "⚡" ;;
        "docs") echo "📝" ;;
        "style") echo "💄" ;;
        "test") echo "✅" ;;
        "build") echo "🏗️" ;;
        "ci") echo "👷" ;;
        "chore") echo "🔧" ;;
        *) echo "" ;;
    esac
}

# ============================================================================
# JSON Output Support
# ============================================================================

# Output JSON result
# Args:
#   $1 - status (success|error)
#   $2 - message
#   $3+ - additional key=value pairs
json_output() {
    local status="$1"
    local message="$2"
    shift 2

    echo "{"
    echo "  \"status\": \"$status\","
    echo "  \"message\": \"$message\""

    while [[ $# -gt 0 ]]; do
        local key="${1%%=*}"
        local value="${1#*=}"
        echo "  ,\"$key\": \"$value\""
        shift
    done

    echo "}"
}

# ============================================================================
# Utility Functions
# ============================================================================

# Check if file path exists
# Args:
#   $1 - file path
# Returns: 0 if exists, 1 if not
check_file() {
    [[ -f "$1" ]]
}

# Check if directory exists and has contents
# Args:
#   $1 - directory path
# Returns: 0 if exists and has contents, 1 if not
check_dir() {
    [[ -d "$1" && -n $(ls -A "$1" 2>/dev/null) ]]
}

# Print error message to stderr
# Args:
#   $@ - error message
error() {
    echo "❌ Error: $*" >&2
}

# Print warning message to stderr
# Args:
#   $@ - warning message
warn() {
    echo "⚠️  Warning: $*" >&2
}

# Print info message to stdout
# Args:
#   $@ - info message
info() {
    echo "ℹ️  $*"
}

# Print success message to stdout
# Args:
#   $@ - success message
success() {
    echo "✅ $*"
}
