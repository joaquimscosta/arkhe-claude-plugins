# Bash Scripting Examples

Complete script templates and usage patterns following defensive programming practices.

## Basic Production Script Template

```bash
#!/usr/bin/env bash
#
# Script: backup-database.sh
# Description: Production database backup with rotation
# Author: Your Name
# Version: 1.0.0
# Requirements: Bash 4.4+, pg_dump, aws-cli

set -Eeuo pipefail
shopt -s inherit_errexit
IFS=$'\n\t'

# Constants
readonly SCRIPT_NAME="${0##*/}"
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly BACKUP_RETENTION_DAYS=7

# Variables
VERBOSE=0
DRY_RUN=0
tmpdir=""

# Error handling
trap 'echo "Error at line $LINENO: exit $?" >&2' ERR

cleanup() {
  [[ -n "$tmpdir" ]] && rm -rf "$tmpdir"
}
trap cleanup EXIT

# Logging functions
log() {
  local level="$1"; shift
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] [$level] $SCRIPT_NAME: $*" >&2
}

log_info() { log INFO "$@"; }
log_error() { log ERROR "$@"; }
log_debug() { [[ $VERBOSE -eq 1 ]] && log DEBUG "$@" || true; }

# Usage message
usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] <database-name>

Create a compressed database backup and upload to S3.

OPTIONS:
  -h, --help          Show this help message
  -v, --verbose       Enable verbose output
  -n, --dry-run       Dry run mode (don't upload)
  -b, --bucket NAME   S3 bucket name (required)

EXAMPLES:
  $SCRIPT_NAME -b my-backups production_db
  $SCRIPT_NAME --dry-run --verbose production_db

EXIT CODES:
  0  Success
  1  General error
  2  Missing dependencies
  3  Backup failed
  4  Upload failed
EOF
}

# Check dependencies
check_dependencies() {
  local missing=()

  for cmd in pg_dump aws gzip; do
    command -v "$cmd" &>/dev/null || missing+=("$cmd")
  done

  if [[ ${#missing[@]} -gt 0 ]]; then
    log_error "Missing required commands: ${missing[*]}"
    return 2
  fi
}

# Main backup function
backup_database() {
  local db_name="$1"
  local s3_bucket="$2"
  local backup_file="$db_name-$(date +%Y%m%d-%H%M%S).sql.gz"
  local backup_path="$tmpdir/$backup_file"

  log_info "Starting backup of database: $db_name"

  # Create backup with progress
  if ! pg_dump "$db_name" | gzip > "$backup_path"; then
    log_error "Database backup failed"
    return 3
  fi

  local size=$(du -h "$backup_path" | cut -f1)
  log_info "Backup created: $backup_file ($size)"

  # Upload to S3
  if [[ $DRY_RUN -eq 0 ]]; then
    log_info "Uploading to S3: s3://$s3_bucket/$backup_file"

    if ! aws s3 cp "$backup_path" "s3://$s3_bucket/$backup_file"; then
      log_error "S3 upload failed"
      return 4
    fi

    log_info "Upload successful"
  else
    log_info "[DRY RUN] Would upload: $backup_file"
  fi
}

# Main execution
main() {
  local s3_bucket=""
  local db_name=""

  # Parse arguments
  while getopts "hvnb:-:" opt; do
    case "$opt" in
      h) usage; exit 0 ;;
      v) VERBOSE=1 ;;
      n) DRY_RUN=1 ;;
      b) s3_bucket="$OPTARG" ;;
      -) # Long options
        case "$OPTARG" in
          help) usage; exit 0 ;;
          verbose) VERBOSE=1 ;;
          dry-run) DRY_RUN=1 ;;
          bucket) s3_bucket="${!OPTIND}"; OPTIND=$((OPTIND + 1)) ;;
          bucket=*) s3_bucket="${OPTARG#*=}" ;;
          *) log_error "Unknown option: --$OPTARG"; usage >&2; exit 1 ;;
        esac
        ;;
      *) usage >&2; exit 1 ;;
    esac
  done
  shift $((OPTIND - 1))

  # Validate arguments
  if [[ $# -lt 1 ]]; then
    log_error "Missing required argument: database-name"
    usage >&2
    exit 1
  fi

  if [[ -z "$s3_bucket" ]]; then
    log_error "Missing required option: --bucket"
    usage >&2
    exit 1
  fi

  db_name="$1"

  # Check dependencies
  check_dependencies || exit $?

  # Create temp directory
  tmpdir=$(mktemp -d)
  log_debug "Created temp directory: $tmpdir"

  # Execute backup
  backup_database "$db_name" "$s3_bucket" || exit $?

  log_info "Backup completed successfully"
}

main "$@"
```

## Error Handling Patterns

### Pattern 1: Command Failure with Context

```bash
if ! some_command arg1 arg2; then
  log_error "some_command failed with args: arg1 arg2"
  exit 1
fi
```

### Pattern 2: Capturing Output on Failure

```bash
if ! output=$(command 2>&1); then
  log_error "Command failed with output: $output"
  exit 1
fi
```

### Pattern 3: Conditional Execution

```bash
command || {
  log_error "Command failed"
  cleanup_function
  exit 1
}
```

## File Processing Patterns

### Pattern 1: Safe File Iteration

```bash
# WRONG - Dangerous, breaks on spaces/glob chars
for file in $(ls *.txt); do
  echo "$file"
done

# CORRECT - Binary-safe, handles all filenames
find . -name "*.txt" -print0 | while IFS= read -r -d '' file; do
  echo "$file"
done
```

### Pattern 2: Array Population

```bash
# Populate array from find
readarray -d '' files < <(find . -name "*.txt" -print0)

# Process array
for file in "${files[@]}"; do
  echo "Processing: $file"
done
```

### Pattern 3: File Validation

```bash
validate_file() {
  local file="$1"

  [[ -e "$file" ]] || { log_error "File does not exist: $file"; return 1; }
  [[ -f "$file" ]] || { log_error "Not a regular file: $file"; return 1; }
  [[ -r "$file" ]] || { log_error "File not readable: $file"; return 1; }

  return 0
}

# Usage
if ! validate_file "$input_file"; then
  exit 1
fi
```

## Platform Compatibility Patterns

### Pattern 1: Platform Detection

```bash
detect_platform() {
  case "$(uname -s)" in
    Linux*)   echo "linux" ;;
    Darwin*)  echo "macos" ;;
    CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
    *)        echo "unknown" ;;
  esac
}

readonly PLATFORM=$(detect_platform)
```

### Pattern 2: GNU vs BSD Tools

```bash
# sed in-place editing
if [[ $PLATFORM == "macos" ]]; then
  sed -i '' 's/old/new/' "$file"  # BSD sed
else
  sed -i 's/old/new/' "$file"     # GNU sed
fi

# date formatting
if [[ $PLATFORM == "macos" ]]; then
  date -u -r "$timestamp" '+%Y-%m-%d'  # BSD date
else
  date -u -d "@$timestamp" '+%Y-%m-%d'  # GNU date
fi
```

### Pattern 3: Command Fallbacks

```bash
# Use GNU tools if available, fall back to BSD
if command -v greadlink &>/dev/null; then
  READLINK="greadlink"  # GNU coreutils on macOS
else
  READLINK="readlink"
fi

canonical_path=$($READLINK -f "$path")
```

## Testing Examples

### bats-core Test Suite

```bash
#!/usr/bin/env bats
# test/backup-database.bats

setup() {
  # Create test environment
  export TEST_DB="test_database"
  export TEST_BUCKET="test-bucket"

  # Mock pg_dump
  function pg_dump() {
    echo "MOCK DATABASE DUMP"
  }
  export -f pg_dump

  # Mock aws
  function aws() {
    echo "MOCK AWS UPLOAD: $*"
    return 0
  }
  export -f aws
}

teardown() {
  # Cleanup test environment
  unset TEST_DB TEST_BUCKET
}

@test "script shows usage with --help" {
  run ./backup-database.sh --help
  [[ "$status" -eq 0 ]]
  [[ "$output" =~ "Usage:" ]]
}

@test "script fails without required arguments" {
  run ./backup-database.sh
  [[ "$status" -eq 1 ]]
  [[ "$output" =~ "Missing required argument" ]]
}

@test "dry-run mode doesn't upload" {
  run ./backup-database.sh --dry-run --bucket "$TEST_BUCKET" "$TEST_DB"
  [[ "$status" -eq 0 ]]
  [[ "$output" =~ "DRY RUN" ]]
  [[ "$output" =~ "Would upload" ]]
}

@test "backup succeeds with valid arguments" {
  run ./backup-database.sh --bucket "$TEST_BUCKET" "$TEST_DB"
  [[ "$status" -eq 0 ]]
  [[ "$output" =~ "Backup completed successfully" ]]
}

@test "verbose mode shows debug output" {
  run ./backup-database.sh --verbose --bucket "$TEST_BUCKET" "$TEST_DB"
  [[ "$status" -eq 0 ]]
  [[ "$output" =~ "DEBUG" ]]
}
```

## CI/CD Integration Examples

### GitHub Actions Workflow

```yaml
name: Shell Script CI

on: [push, pull_request]

jobs:
  lint-and-test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        bash-version: ['4.4', '5.0', '5.1', '5.2']

    steps:
      - uses: actions/checkout@v3

      - name: Install Bash ${{ matrix.bash-version }}
        run: |
          if [[ "$RUNNER_OS" == "Linux" ]]; then
            sudo apt-get update
            sudo apt-get install -y bash=${{ matrix.bash-version }}*
          fi

      - name: Install ShellCheck
        run: |
          if [[ "$RUNNER_OS" == "Linux" ]]; then
            sudo apt-get install -y shellcheck
          else
            brew install shellcheck
          fi

      - name: Install shfmt
        run: |
          GO111MODULE=on go install mvdan.cc/sh/v3/cmd/shfmt@latest

      - name: Install bats-core
        run: |
          git clone https://github.com/bats-core/bats-core.git
          cd bats-core && sudo ./install.sh /usr/local

      - name: Run ShellCheck
        run: shellcheck --enable=all *.sh

      - name: Run shfmt
        run: shfmt -d -i 2 -ci -bn -sr -kp *.sh

      - name: Run tests
        run: bats test/
```

### Pre-commit Hook Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.5
    hooks:
      - id: shellcheck
        args: ['--enable=all']

  - repo: https://github.com/scop/pre-commit-shfmt
    rev: v3.7.0-1
    hooks:
      - id: shfmt
        args: ['-i', '2', '-ci', '-bn', '-sr', '-kp', '-w']

  - repo: https://github.com/openstack/bashate
    rev: 2.1.1
    hooks:
      - id: bashate
        args: ['--ignore=E006']
```

## Advanced Patterns

### Pattern 1: Parallel Processing

```bash
# Process files in parallel
find . -name "*.txt" -print0 |
  xargs -0 -P "$(nproc)" -I {} sh -c '
    process_file "$1"
  ' _ {}

# With error handling
errors=0
find . -name "*.txt" -print0 |
  xargs -0 -P "$(nproc)" -I {} sh -c '
    process_file "$1" || exit 255
  ' _ {} || errors=$?

if [[ $errors -ne 0 ]]; then
  log_error "Some files failed to process"
  exit 1
fi
```

### Pattern 2: JSON Output

```bash
# Generate structured JSON output
jq -n \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg status "success" \
  --arg files_processed "$file_count" \
  '{
    timestamp: $timestamp,
    status: $status,
    metrics: {
      files_processed: ($files_processed | tonumber)
    }
  }'
```

### Pattern 3: Co-process for Bidirectional Communication

```bash
# Start a co-process
coproc worker {
  while IFS= read -r line; do
    # Process input and respond
    result=$(echo "$line" | tr '[:lower:]' '[:upper:]')
    echo "$result"
  done
}

# Send data to co-process
echo "hello" >&"${worker[1]}"

# Read response
read -u "${worker[0]}" response
echo "Response: $response"

# Cleanup
exec {worker[0]}>&- {worker[1]}>&-
wait "$worker_PID"
```

## Performance Optimization Examples

### Before: Inefficient

```bash
# SLOW: Repeated command substitutions and subshells
for i in {1..1000}; do
  result=$(date +%s)
  echo "$result: $(basename "$file")"
done
```

### After: Optimized

```bash
# FAST: Single substitution, Bash built-in
timestamp=$(date +%s)
basename="${file##*/}"

for i in {1..1000}; do
  echo "$timestamp: $basename"
done
```

## Resource Management Pattern

```bash
# Comprehensive resource cleanup
declare -a CLEANUP_FILES=()
declare -a CLEANUP_DIRS=()

cleanup_resources() {
  local file dir

  # Remove files
  for file in "${CLEANUP_FILES[@]}"; do
    [[ -f "$file" ]] && rm -f "$file"
  done

  # Remove directories
  for dir in "${CLEANUP_DIRS[@]}"; do
    [[ -d "$dir" ]] && rm -rf "$dir"
  done
}

trap cleanup_resources EXIT

# Register resources for cleanup
tmpfile=$(mktemp)
CLEANUP_FILES+=("$tmpfile")

tmpdir=$(mktemp -d)
CLEANUP_DIRS+=("$tmpdir")
```
