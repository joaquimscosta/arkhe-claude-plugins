# Modern Bash 5.x Features

Comprehensive guide to Bash 5.x features with version detection and fallback strategies.

## Version Detection

Always check Bash version before using modern features:

```bash
# Check major version
if (( BASH_VERSINFO[0] >= 5 )); then
  echo "Bash 5.x features available"
fi

# Check specific version
if (( BASH_VERSINFO[0] == 5 && BASH_VERSINFO[1] >= 2 )); then
  echo "Bash 5.2+ features available"
fi

# Full version info
echo "Bash ${BASH_VERSION}"
echo "Major: ${BASH_VERSINFO[0]}, Minor: ${BASH_VERSINFO[1]}, Patch: ${BASH_VERSINFO[2]}"
```

## Bash 5.0 Features (2019-01)

### Associative Array Improvements

```bash
# Better handling of unset keys
declare -A config
echo "${config[nonexistent]}"  # Returns empty, doesn't error

# Improved iteration
for key in "${!config[@]}"; do
  echo "$key: ${config[$key]}"
done
```

### Case Modification (`${parameter@U}`, `${parameter@L}`)

```bash
text="Hello World"

# Uppercase transformation
echo "${text@U}"  # HELLO WORLD

# Lowercase transformation
echo "${text@L}"  # hello world

# Capitalize first letter
echo "${text,}"   # hello World (lowercase first)
echo "${text^}"   # Hello world (uppercase first)
echo "${text^^}"  # HELLO WORLD (all uppercase)
echo "${text,,}"  # hello world (all lowercase)
```

### Enhanced `wait` Command

```bash
# Wait for any background job to complete
sleep 5 &
sleep 10 &
wait -n  # Returns when first job completes
echo "One job completed"
```

## Bash 5.1 Features (2020-12)

### Enhanced Parameter Transformations

```bash
# Assignment format
declare -a arr=(one two three)
echo "${arr[@]@A}"  # declare -a arr=([0]="one" [1]="two" [2]="three")

# Useful for saving/restoring state
saved_config="${config[@]@A}"
# ... modify config ...
eval "$saved_config"  # Restore original
```

### `compat` Shopt Options

```bash
# Enable Bash 4.4 compatibility mode
shopt -s compat44

# Disable to use Bash 5.x features
shopt -u compat44
```

### `SRANDOM` Variable

```bash
# Cryptographically secure random numbers (32-bit)
echo "$SRANDOM"

# Generate random hex string
printf '%08x\n' "$SRANDOM"
```

## Bash 5.2 Features (2022-09)

### `varredir_close` Option

```bash
# Automatically close file descriptors assigned to variables
shopt -s varredir_close

{variable}<file  # FD stored in $variable, auto-closed when out of scope
```

### Improved `exec` Error Handling

```bash
# exec now sets error codes more consistently
exec 2>/nonexistent/path  # Now properly reports error
echo $?  # Non-zero exit code
```

### `EPOCHREALTIME` Variable

```bash
# Microsecond-precision timestamp
echo "$EPOCHREALTIME"  # e.g., 1699564322.123456

# Measure execution time
start="$EPOCHREALTIME"
# ... operation ...
end="$EPOCHREALTIME"

# Calculate duration in microseconds
duration=$(awk "BEGIN {print ($end - $start) * 1000000}")
echo "Duration: ${duration}µs"
```

### `BASH_REMATCH` Enhancements

```bash
# Better handling in conditional expressions
if [[ $text =~ ([0-9]+)-([0-9]+)-([0-9]+) ]]; then
  year="${BASH_REMATCH[1]}"
  month="${BASH_REMATCH[2]}"
  day="${BASH_REMATCH[3]}"
  echo "Date: $year-$month-$day"
fi
```

## Bash 4.4+ Features (Still Relevant)

### Parameter Transformation Operators

```bash
text="hello world"

# Shell-quoted output (Bash 4.4+)
echo "${text@Q}"  # 'hello world'

# Escape sequence expansion (Bash 4.4+)
escaped="hello\nworld"
echo "${escaped@E}"  # hello
                     # world

# Prompt expansion (Bash 4.4+)
PS1='\u@\h:\w\$ '
echo "${PS1@P}"  # user@hostname:/path$
```

### `mapfile` with Custom Delimiter

```bash
# Read with custom delimiter (Bash 4.4+)
mapfile -d ':' fields <<< "field1:field2:field3"
for field in "${fields[@]}"; do
  echo "Field: $field"
done
```

### `shopt -s inherit_errexit`

```bash
# Better error propagation in command substitution (Bash 4.4+)
set -e
shopt -s inherit_errexit

# Subshells now inherit errexit
result=$(false; echo "never reached")  # Exits due to inherit_errexit
```

### Locale-Aware Case Modification

```bash
# Locale-aware transformations (Bash 4.4+)
text="Stra\u00dfe"  # German street (ß)

echo "${text@L}"  # locale-aware lowercase
echo "${text@U}"  # locale-aware uppercase
```

## Feature Detection Pattern

Create portable scripts that use modern features when available:

```bash
#!/usr/bin/env bash

# Feature detection function
has_feature() {
  local feature="$1"

  case "$feature" in
    bash5)
      (( BASH_VERSINFO[0] >= 5 ))
      ;;
    bash52)
      (( BASH_VERSINFO[0] == 5 && BASH_VERSINFO[1] >= 2 ))
      ;;
    bash44)
      (( BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 4 )) || (( BASH_VERSINFO[0] >= 5 ))
      ;;
    *)
      return 1
      ;;
  esac
}

# Use with fallback
if has_feature bash52; then
  # Use EPOCHREALTIME
  start="$EPOCHREALTIME"
else
  # Fallback to date
  start=$(date +%s.%N)
fi
```

## Practical Examples

### High-Precision Timing

```bash
# Bash 5.2+
if (( BASH_VERSINFO[0] == 5 && BASH_VERSINFO[1] >= 2 )); then
  start="$EPOCHREALTIME"
  # ... operation ...
  end="$EPOCHREALTIME"
  duration=$(awk "BEGIN {printf \"%.6f\", $end - $start}")
  echo "Duration: ${duration}s"
else
  # Fallback
  start=$(date +%s.%N 2>/dev/null || date +%s)
  # ... operation ...
  end=$(date +%s.%N 2>/dev/null || date +%s)
  duration=$(awk "BEGIN {printf \"%.6f\", $end - $start}")
  echo "Duration: ${duration}s"
fi
```

### Safe Uppercase Conversion

```bash
# Bash 5.0+
if (( BASH_VERSINFO[0] >= 5 )); then
  uppercase="${text@U}"
else
  # Fallback to tr
  uppercase=$(echo "$text" | tr '[:lower:]' '[:upper:]')
fi
```

### Secure Random Numbers

```bash
# Bash 5.1+
if (( BASH_VERSINFO[0] == 5 && BASH_VERSINFO[1] >= 1 )); then
  random_num="$SRANDOM"
else
  # Fallback to /dev/urandom
  random_num=$(od -An -N4 -tu4 </dev/urandom | tr -d ' ')
fi
```

## Version-Specific Shell Options

```bash
# List all available shell options for current version
shopt | sort

# Bash 5.x specific options
if (( BASH_VERSINFO[0] >= 5 )); then
  shopt -s globskipdots    # Skip . and .. in glob expansion
  shopt -s assoc_expand_once  # Expand associative array subscripts only once
fi

# Bash 4.4+ specific options
if (( BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 4 )) || (( BASH_VERSINFO[0] >= 5 )); then
  shopt -s inherit_errexit    # Inherit errexit in command substitutions
  shopt -s localvar_inherit   # Local variables inherit values
fi
```

## Minimum Version Requirements

### Recommended Minimum: Bash 4.4

Bash 4.4 (2016) provides essential modern features:
- `inherit_errexit` for reliable error handling
- `@Q`, `@E`, `@P`, `@A` transformations
- `mapfile -d` for custom delimiters
- Improved `[[` and `(())` operators

### Check Version and Exit

```bash
#!/usr/bin/env bash

# Require Bash 4.4+
if (( BASH_VERSINFO[0] < 4 )) ||
   (( BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] < 4 )); then
  echo "Error: This script requires Bash 4.4 or higher" >&2
  echo "Current version: $BASH_VERSION" >&2
  exit 1
fi
```

## Compatibility Matrix

| Feature | Bash 4.4 | Bash 5.0 | Bash 5.1 | Bash 5.2 |
|---------|----------|----------|----------|----------|
| `${var@Q}` | ✅ | ✅ | ✅ | ✅ |
| `${var@U}` | ❌ | ✅ | ✅ | ✅ |
| `${var@L}` | ❌ | ✅ | ✅ | ✅ |
| `${var@A}` | ✅ | ✅ | ✅ | ✅ |
| `inherit_errexit` | ✅ | ✅ | ✅ | ✅ |
| `SRANDOM` | ❌ | ❌ | ✅ | ✅ |
| `EPOCHREALTIME` | ❌ | ❌ | ❌ | ✅ |
| `wait -n` | ✅ | ✅ | ✅ | ✅ |
| `varredir_close` | ❌ | ❌ | ❌ | ✅ |

## Migration Guide

### From Bash 3.x to 4.4+

```bash
# Before (Bash 3.x)
IFS=',' read -a fields <<< "$csv_line"  # Basic array

# After (Bash 4.4+)
mapfile -d ',' fields <<< "$csv_line"   # Better array handling
```

### From Bash 4.x to 5.x

```bash
# Before (Bash 4.x)
upper=$(echo "$text" | tr '[:lower:]' '[:upper:]')

# After (Bash 5.0+)
upper="${text@U}"  # Built-in, faster, no subprocess
```

## Testing Across Versions

### Docker-Based Testing

```bash
#!/bin/bash
# test-versions.sh

for version in 4.4 5.0 5.1 5.2; do
  echo "Testing with Bash $version..."
  docker run --rm -v "$PWD:/work" -w /work "bash:$version" ./script.sh
done
```

### CI Matrix

```yaml
strategy:
  matrix:
    bash-version: ['4.4', '5.0', '5.1', '5.2']

steps:
  - name: Test with Bash ${{ matrix.bash-version }}
    run: |
      docker run --rm -v "$PWD:/work" -w /work \
        bash:${{ matrix.bash-version }} \
        bats test/
```

## Performance Comparison

Modern Bash features are often significantly faster than external commands:

```bash
# Benchmark uppercase conversion
iterations=10000

# External command (slow)
time for ((i=0; i<iterations; i++)); do
  result=$(echo "$text" | tr '[:lower:]' '[:upper:]')
done

# Built-in (fast - Bash 5.0+)
time for ((i=0; i<iterations; i++)); do
  result="${text@U}"
done
```

Typical results:
- External `tr`: ~15-20 seconds
- Built-in `@U`: ~0.1-0.2 seconds (100x faster)

## References

- [Bash 5.2 Release Notes](https://lists.gnu.org/archive/html/bash-announce/2022-09/msg00000.html)
- [Bash 5.1 Release Notes](https://lists.gnu.org/archive/html/bash-announce/2020-12/msg00000.html)
- [Bash 5.0 Release Notes](https://lists.gnu.org/archive/html/bash-announce/2019-01/msg00000.html)
- [Bash 4.4 Release Notes](https://lists.gnu.org/archive/html/bash-announce/2016-09/msg00000.html)
- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html)
