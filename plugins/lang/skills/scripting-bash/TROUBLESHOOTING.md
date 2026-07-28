# Bash Scripting Troubleshooting

Common pitfalls, errors, and their solutions when writing production Bash scripts.

## Common Pitfalls

### 1. Word Splitting and Globbing

**❌ WRONG:**
```bash
# Breaks on filenames with spaces
for file in $(ls *.txt); do
  echo "$file"
done

# Unsafe variable expansion
files=$(find . -name "*.txt")
for file in $files; do  # Unquoted!
  echo "$file"
done
```

**✅ CORRECT:**
```bash
# Binary-safe file iteration
find . -name "*.txt" -print0 | while IFS= read -r -d '' file; do
  echo "$file"
done

# Or use array
readarray -d '' files < <(find . -name "*.txt" -print0)
for file in "${files[@]}"; do
  echo "$file"
done
```

**Why it fails:**
- Unquoted expansions split on `$IFS` (space, tab, newline by default)
- Glob characters (`*`, `?`, `[`) expand unexpectedly
- Filenames with spaces/newlines break iteration

### 2. Unquoted Variable Expansions

**❌ WRONG:**
```bash
cp $source $destination
rm -rf $tmpdir/*
```

**✅ CORRECT:**
```bash
cp "$source" "$destination"
rm -rf "${tmpdir:?}"/*  # Also validates tmpdir is set
```

**Why it fails:**
- Spaces in paths cause arguments to split
- Empty variables can cause dangerous operations
- Glob expansion can match unintended files

### 3. Missing Cleanup Traps

**❌ WRONG:**
```bash
tmpfile=$(mktemp)
# ... do work ...
rm "$tmpfile"  # Never reached if script exits early
```

**✅ CORRECT:**
```bash
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT
# ... do work ...
# Cleanup happens automatically on exit
```

**Why it fails:**
- Errors, signals, or early exits skip manual cleanup
- Resources leak (temp files, processes, file descriptors)
- Partial state left behind

### 4. Relying on `set -e` Alone

**❌ WRONG:**
```bash
set -e
command1
command2 || true  # Accidentally disables errexit
command3  # Won't exit even if this fails
```

**✅ CORRECT:**
```bash
set -Eeuo pipefail
trap 'echo "Error at line $LINENO" >&2' ERR

command1 || {
  echo "command1 failed" >&2
  exit 1
}

command2 || {
  echo "command2 failed" >&2
  exit 1
}
```

**Why it fails:**
- `set -e` doesn't work in all contexts (functions, conditionals, pipelines)
- Silent failures in pipes (`cmd1 | cmd2` only checks cmd2)
- Hard to debug without error traps

### 5. Using `echo` for Data Output

**❌ WRONG:**
```bash
# Unsafe for data that might start with -
echo "$user_input"

# Inconsistent across platforms
echo -n "prompt: "  # -n handling varies
```

**✅ CORRECT:**
```bash
# Always safe, predictable
printf '%s\n' "$user_input"

# Portable no-newline output
printf '%s' "prompt: "
```

**Why it fails:**
- `echo` interprets escape sequences differently across shells/platforms
- Leading `-` in data can be interpreted as options
- No portable way to control newline behavior

### 6. Unsafe Array Population

**❌ WRONG:**
```bash
# Breaks on whitespace and glob chars
files=($(find . -name "*.txt"))
```

**✅ CORRECT:**
```bash
# Binary-safe array population
readarray -d '' files < <(find . -name "*.txt" -print0)

# Or with mapfile (alias for readarray)
mapfile -d '' files < <(find . -name "*.txt" -print0)
```

**Why it fails:**
- Command substitution splits on `$IFS`
- Filenames with newlines break array
- Glob patterns in filenames expand

### 7. Ignoring Binary-Safe File Handling

**❌ WRONG:**
```bash
# Breaks on filenames with newlines
find . -name "*.txt" | while read file; do
  echo "$file"
done
```

**✅ CORRECT:**
```bash
# NUL-separated (binary-safe)
find . -name "*.txt" -print0 | while IFS= read -r -d '' file; do
  echo "$file"
done
```

**Why it fails:**
- Newlines in filenames split into multiple entries
- Trailing/leading whitespace stripped by default
- Only NUL (`\0`) is safe delimiter (can't appear in paths)

## Debugging Techniques

### Enable Trace Mode

```bash
# Add to script for debugging
set -x  # Print commands as they execute

# Or run with trace
bash -x script.sh

# Selective tracing
set -x      # Enable
# ... code to debug ...
set +x      # Disable
```

### Error Context with Line Numbers

```bash
# Enhanced error trap
trap 'echo "Error in ${BASH_SOURCE[0]}:$LINENO: command \"$BASH_COMMAND\" exited with $?" >&2' ERR
```

### Function Call Stack

```bash
# Print stack trace on error
print_stack_trace() {
  local frame=0
  echo "Stack trace:" >&2
  while caller $frame; do
    ((frame++))
  done
}

trap print_stack_trace ERR
```

### Verbose Logging

```bash
# Debug wrapper
debug() {
  [[ ${DEBUG:-0} -eq 1 ]] && echo "[DEBUG] $*" >&2 || true
}

# Usage
debug "Variable value: $var"
debug "Entering function: ${FUNCNAME[1]}"
```

### Dry Run Mode

```bash
DRY_RUN=${DRY_RUN:-0}

maybe_run() {
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[DRY RUN] Would execute: $*" >&2
  else
    "$@"
  fi
}

# Usage
maybe_run rm -rf /important/directory
```

## ShellCheck Integration Issues

### Issue: False Positives

**Problem:**
```bash
# ShellCheck SC2086: Double quote to prevent globbing
for host in $HOSTLIST; do  # Intentional word splitting
  ssh "$host" "uptime"
done
```

**Solution:**
```bash
# Disable specific check with comment
# shellcheck disable=SC2086
for host in $HOSTLIST; do
  ssh "$host" "uptime"
done

# Or use array (better)
IFS=',' read -ra hosts <<< "$HOSTLIST"
for host in "${hosts[@]}"; do
  ssh "$host" "uptime"
done
```

### Issue: Unused Variables

**Problem:**
```bash
# ShellCheck SC2034: Variable appears unused
readonly VERSION="1.0.0"  # Used in sourced files
```

**Solution:**
```bash
# Suppress if genuinely used elsewhere
# shellcheck disable=SC2034
readonly VERSION="1.0.0"

# Or export if used by child processes
export VERSION="1.0.0"
```

## Platform Compatibility Issues

### Issue: GNU vs BSD `sed`

**Problem:**
```bash
# Works on Linux, fails on macOS
sed -i 's/old/new/' file
```

**Solution:**
```bash
# Portable in-place edit
if [[ "$(uname)" == "Darwin" ]]; then
  sed -i '' 's/old/new/' file  # macOS
else
  sed -i 's/old/new/' file     # Linux
fi

# Or use temp file (most portable)
sed 's/old/new/' file > file.tmp && mv file.tmp file
```

### Issue: Date Command Differences

**Problem:**
```bash
# GNU date syntax doesn't work on macOS
date -d "2023-01-01" +%s
```

**Solution:**
```bash
# Portable date handling
if [[ "$(uname)" == "Darwin" ]]; then
  # macOS (BSD date)
  timestamp=$(date -j -f "%Y-%m-%d" "2023-01-01" +%s)
else
  # Linux (GNU date)
  timestamp=$(date -d "2023-01-01" +%s)
fi
```

### Issue: Missing Commands

**Problem:**
```bash
# Script fails if readlink not available
canonical=$(readlink -f "$path")
```

**Solution:**
```bash
# Check before using
if command -v readlink &>/dev/null; then
  canonical=$(readlink -f "$path")
else
  # Fallback implementation
  canonical=$(cd "$(dirname "$path")" && pwd -P)/$(basename "$path")
fi
```

## Testing Issues

### Issue: Tests Pass Locally, Fail in CI

**Problem:**
- Different Bash versions
- Different tool versions (GNU vs BSD)
- Different environment variables

**Solution:**
```bash
# Test matrix in CI
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    bash-version: ['4.4', '5.0', '5.2']

# Version detection in tests
@test "check bash version" {
  run bash --version
  [[ "$output" =~ "version ${EXPECTED_BASH_VERSION}" ]]
}

# Environment isolation
setup() {
  # Save current environment
  export SAVED_PATH="$PATH"

  # Set up test environment
  export PATH="/test/bin:$PATH"
}

teardown() {
  # Restore environment
  export PATH="$SAVED_PATH"
}
```

### Issue: Mock Not Working

**Problem:**
```bash
# Function mock not visible in subshell
function aws() { echo "MOCK"; }
export -f aws

# Fails: subshell doesn't see mock
result=$(aws s3 ls)
```

**Solution:**
```bash
# Use BATS helper for mocking
load test_helper

@test "mock aws command" {
  # Create mock in PATH
  function aws() {
    echo "MOCK AWS: $*"
  }
  export -f aws

  # Call in same shell (not subshell)
  run aws s3 ls
  [[ "$output" == "MOCK AWS: s3 ls" ]]
}
```

## Performance Issues

### Issue: Slow File Processing

**Problem:**
```bash
# Slow: spawns process for each file
for file in *.txt; do
  cat "$file" | grep pattern
done
```

**Solution:**
```bash
# Fast: single grep invocation
grep pattern *.txt

# Or parallel processing
find . -name "*.txt" -print0 |
  xargs -0 -P "$(nproc)" grep pattern
```

### Issue: Repeated Command Substitutions

**Problem:**
```bash
# Slow: runs date 1000 times
for i in {1..1000}; do
  echo "$(date +%s): Processing $i"
done
```

**Solution:**
```bash
# Fast: run date once
timestamp=$(date +%s)
for i in {1..1000}; do
  echo "$timestamp: Processing $i"
done
```

## Security Issues

### Issue: Command Injection

**Problem:**
```bash
# Dangerous: user input in command
eval "grep '$user_pattern' file.txt"
```

**Solution:**
```bash
# Safe: pass as argument
grep "$user_pattern" file.txt

# Or use array for complex commands
cmd=(grep "$user_pattern" file.txt)
"${cmd[@]}"
```

### Issue: Path Traversal

**Problem:**
```bash
# Dangerous: user can specify ../../../etc/passwd
cat "$user_specified_file"
```

**Solution:**
```bash
# Validate path is within allowed directory
validate_path() {
  local path="$1"
  local allowed_dir="/safe/directory"

  # Resolve to canonical path
  local canonical=$(cd "$(dirname "$path")" && pwd -P)/$(basename "$path")

  # Check if within allowed directory
  [[ "$canonical" == "$allowed_dir"/* ]] || {
    echo "Error: Path outside allowed directory" >&2
    return 1
  }
}

if validate_path "$user_specified_file"; then
  cat "$user_specified_file"
fi
```

### Issue: Temporary File Race Condition

**Problem:**
```bash
# Insecure: predictable name, race condition
tmpfile="/tmp/myapp-$$"
echo "data" > "$tmpfile"
```

**Solution:**
```bash
# Secure: unpredictable name, atomic creation
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT
echo "data" > "$tmpfile"
```

## Getting Help

### Run ShellCheck

```bash
shellcheck --enable=all script.sh
```

### Check Bash Version

```bash
bash --version
echo "Bash ${BASH_VERSION} (${BASH_VERSINFO[0]}.${BASH_VERSINFO[1]})"
```

### Test Platform Compatibility

```bash
# Test on multiple platforms
docker run --rm -v "$PWD:/work" -w /work bash:5.2 ./script.sh
docker run --rm -v "$PWD:/work" -w /work bash:4.4 ./script.sh
```

### Enable Comprehensive Debugging

```bash
# Maximum debug output
set -Eeuxo pipefail
export PS4='+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
```

## Additional Resources

- [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls) - Comprehensive list
- [ShellCheck Wiki](https://github.com/koalaman/shellcheck/wiki) - Explanations for each check
- [Bash FAQ](https://mywiki.wooledge.org/BashFAQ) - Common questions and answers
- [Stack Overflow: bash tag](https://stackoverflow.com/questions/tagged/bash) - Community help
