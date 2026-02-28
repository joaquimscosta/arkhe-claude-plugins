#!/bin/bash
# =============================================================================
# Security Scan Script
# Runs Trivy (vulnerability scanning) and Gitleaks (secret detection)
# Auto-detects project structure — works with any repository layout.
# =============================================================================
#
# Usage:
#   ./scripts/security-scan.sh                    # Full scan (auto-detect + git history)
#   ./scripts/security-scan.sh --quick            # Quick scan (skip git history)
#   ./scripts/security-scan.sh --output-dir DIR   # Custom report output directory
#   ./scripts/security-scan.sh --help             # Show help
#
# Output:
#   - Console summary with pass/fail status
#   - JSON reports in reviews/security/ (or custom --output-dir)
#
# Prerequisites:
#   brew install trivy gitleaks jq
#
# =============================================================================

set -uo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
REPORTS_DIR="$PROJECT_ROOT/reviews/security"
SEVERITY="HIGH,CRITICAL"

# Counters
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# Options
QUICK_MODE=false

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_status() {
    local status=$1
    local message=$2
    case $status in
        "pass")
            echo -e "  ${GREEN}✓${NC} $message"
            ((PASS_COUNT++))
            ;;
        "fail")
            echo -e "  ${RED}✗${NC} $message"
            ((FAIL_COUNT++))
            ;;
        "skip")
            echo -e "  ${YELLOW}○${NC} $message (skipped)"
            ((SKIP_COUNT++))
            ;;
        "info")
            echo -e "  ${BLUE}ℹ${NC} $message"
            ;;
    esac
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed.${NC}"
        echo "Install with: brew install $1"
        exit 1
    fi
}

# =============================================================================
# Auto-Detection Functions
# =============================================================================

discover_app_dirs() {
    # Discover application directories by looking for dependency manifests
    local manifests=("package.json" "requirements.txt" "pyproject.toml" "go.mod"
                     "pom.xml" "build.gradle" "build.gradle.kts" "Cargo.toml"
                     "Gemfile" "composer.json" "mix.exs" "pubspec.yaml")
    local found_dirs=()

    for manifest in "${manifests[@]}"; do
        while IFS= read -r file; do
            local dir
            dir="$(dirname "$file")"
            # Skip common vendored/generated directories
            [[ "$dir" == *node_modules* ]] && continue
            [[ "$dir" == *vendor* ]] && continue
            [[ "$dir" == *.git* ]] && continue
            [[ "$dir" == *__pycache__* ]] && continue
            [[ "$dir" == *target* ]] && continue
            [[ "$dir" == *build* ]] && continue
            [[ "$dir" == *dist* ]] && continue
            found_dirs+=("$dir")
        done < <(find "$PROJECT_ROOT" -maxdepth 3 -name "$manifest" \
            -not -path "*/node_modules/*" \
            -not -path "*/.git/*" \
            -not -path "*/vendor/*" 2>/dev/null)
    done

    printf '%s\n' "${found_dirs[@]}" | sort -u
}

discover_iac_dirs() {
    # Discover Infrastructure-as-Code directories
    local found_dirs=()

    # Terraform files
    while IFS= read -r file; do
        found_dirs+=("$(dirname "$file")")
    done < <(find "$PROJECT_ROOT" -maxdepth 3 -name "*.tf" \
        -not -path "*/.terraform/*" \
        -not -path "*/.git/*" 2>/dev/null)

    # Known IaC directory patterns
    for pattern in "k8s" "kubernetes" "helm" "ansible" "terraform" "infrastructure" "deploy" "infra"; do
        if [ -d "$PROJECT_ROOT/$pattern" ]; then
            found_dirs+=("$PROJECT_ROOT/$pattern")
        fi
    done

    printf '%s\n' "${found_dirs[@]}" | sort -u
}

# =============================================================================
# Trivy Scan Functions
# =============================================================================

scan_app_dir() {
    local app_dir="$1"
    local dir_name
    dir_name="$(basename "$app_dir")"
    local rel_path="${app_dir#"$PROJECT_ROOT"/}"

    echo ""
    echo -e "  ${BOLD}Scanning $rel_path...${NC}"

    local skip_args=""
    # Auto-skip common generated directories
    for skip in ".next" ".pnpm-store" "node_modules" "__pycache__" "target" "dist" "build"; do
        if [ -d "$app_dir/$skip" ]; then
            skip_args="$skip_args --skip-dirs $skip"
        fi
    done

    local report_name="trivy-${dir_name}.json"

    if trivy fs "$app_dir" \
        --severity "$SEVERITY" \
        $skip_args \
        --format json \
        --output "$REPORTS_DIR/$report_name" \
        --quiet 2>/dev/null; then

        local vuln_count
        vuln_count=$(jq '[.Results[]?.Vulnerabilities // [] | length] | add // 0' "$REPORTS_DIR/$report_name" 2>/dev/null || echo "0")
        if [ "$vuln_count" -eq 0 ]; then
            print_status "pass" "$rel_path: No HIGH/CRITICAL vulnerabilities"
        else
            print_status "fail" "$rel_path: $vuln_count vulnerabilities found"
        fi
    else
        print_status "fail" "$rel_path: Scan failed"
    fi
}

scan_iac_dir() {
    local iac_dir="$1"
    local dir_name
    dir_name="$(basename "$iac_dir")"
    local rel_path="${iac_dir#"$PROJECT_ROOT"/}"

    echo ""
    echo -e "  ${BOLD}Scanning IaC: $rel_path...${NC}"

    local report_name="trivy-iac-${dir_name}.json"

    if trivy config "$iac_dir" \
        --severity "$SEVERITY" \
        --format json \
        --output "$REPORTS_DIR/$report_name" \
        --quiet 2>/dev/null; then

        local misconfig_count
        misconfig_count=$(jq '[.Results[]?.Misconfigurations // [] | length] | add // 0' "$REPORTS_DIR/$report_name" 2>/dev/null || echo "0")
        if [ "$misconfig_count" -eq 0 ]; then
            print_status "pass" "$rel_path: No HIGH/CRITICAL misconfigurations"
        else
            print_status "fail" "$rel_path: $misconfig_count misconfigurations found"
        fi
    else
        print_status "fail" "$rel_path: IaC scan failed"
    fi
}

show_help() {
    echo "Security Scan Script - Trivy + Gitleaks"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --quick          Skip git history scan (faster)"
    echo "  --output-dir DIR Custom report output directory (default: reviews/security/)"
    echo "  --help           Show this help message"
    echo ""
    echo "Auto-detects project structure by scanning for:"
    echo "  - App dependencies: package.json, requirements.txt, go.mod, pom.xml, etc."
    echo "  - IaC configs: *.tf files, k8s/, terraform/, infrastructure/ directories"
    echo "  - Git history: secrets detection via Gitleaks"
    echo ""
    echo "Output:"
    echo "  Reports saved to: reviews/security/ (or custom --output-dir)"
    echo ""
    echo "Prerequisites:"
    echo "  brew install trivy gitleaks jq"
}

# =============================================================================
# Parse Arguments
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --output-dir)
            REPORTS_DIR="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# =============================================================================
# Main Script
# =============================================================================

cd "$PROJECT_ROOT" || exit 1

print_header "Security Scan"
echo ""
echo -e "  ${BOLD}Project:${NC}  $PROJECT_ROOT"
echo -e "  ${BOLD}Mode:${NC}     $([ "$QUICK_MODE" = true ] && echo "Quick (no git history)" || echo "Full")"
echo -e "  ${BOLD}Severity:${NC} $SEVERITY"

# Check prerequisites
print_header "Checking Prerequisites"
check_command trivy
print_status "pass" "trivy installed ($(trivy --version 2>&1 | head -1))"
check_command gitleaks
print_status "pass" "gitleaks installed ($(gitleaks version 2>&1))"

# Create reports directory
mkdir -p "$REPORTS_DIR"
print_status "info" "Reports directory: $REPORTS_DIR"

# =============================================================================
# Auto-Detect and Scan Application Directories
# =============================================================================

print_header "Trivy Vulnerability Scans"

APP_DIRS=$(discover_app_dirs)
if [ -z "$APP_DIRS" ]; then
    print_status "skip" "No application directories found (no dependency manifests detected)"
else
    while IFS= read -r dir; do
        scan_app_dir "$dir"
    done <<< "$APP_DIRS"
fi

# =============================================================================
# Auto-Detect and Scan IaC Directories
# =============================================================================

IAC_DIRS=$(discover_iac_dirs)
if [ -n "$IAC_DIRS" ]; then
    print_header "Trivy IaC Scans"
    while IFS= read -r dir; do
        scan_iac_dir "$dir"
    done <<< "$IAC_DIRS"
fi

# =============================================================================
# Gitleaks Scan
# =============================================================================

print_header "Gitleaks Secret Detection"

if [ "$QUICK_MODE" = true ]; then
    print_status "skip" "Git history scan (--quick mode)"
else
    echo ""
    echo -e "  ${BOLD}Scanning git history for secrets...${NC}"
    if gitleaks detect \
        --source . \
        --report-path "$REPORTS_DIR/gitleaks.json" \
        --report-format json \
        --verbose 2>&1 | tail -5; then
        print_status "pass" "No secrets detected in git history"
    else
        LEAK_COUNT=$(jq 'length' "$REPORTS_DIR/gitleaks.json" 2>/dev/null || echo "?")
        print_status "fail" "Secrets detected: $LEAK_COUNT findings"
    fi
fi

# =============================================================================
# Summary
# =============================================================================

print_header "Summary"
echo ""
echo -e "  ${GREEN}Passed:${NC}  $PASS_COUNT"
echo -e "  ${RED}Failed:${NC}  $FAIL_COUNT"
echo -e "  ${YELLOW}Skipped:${NC} $SKIP_COUNT"
echo ""
echo -e "  ${BOLD}Reports:${NC} $REPORTS_DIR/"
ls -1 "$REPORTS_DIR"/*.json 2>/dev/null | sed 's/^/    /'
echo ""

# Exit with appropriate code
if [ "$FAIL_COUNT" -gt 0 ]; then
    echo -e "${RED}${BOLD}Security scan found issues. Review reports above.${NC}"
    exit 1
else
    echo -e "${GREEN}${BOLD}Security scan passed!${NC}"
    exit 0
fi
