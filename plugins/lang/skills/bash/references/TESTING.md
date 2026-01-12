# Bash Testing Frameworks

Comprehensive guide to testing Bash scripts with bats-core, shellspec, and other frameworks.

## bats-core (Recommended)

Modern, actively maintained Bash testing framework with TAP output.

### Installation

```bash
# macOS
brew install bats-core

# Ubuntu/Debian
sudo apt-get install bats

# From source
git clone https://github.com/bats-core/bats-core.git
cd bats-core
sudo ./install.sh /usr/local
```

### Basic Test Structure

```bash
#!/usr/bin/env bats
# test/script.bats

# Runs before each test
setup() {
  # Load script under test
  load '../script.sh'

  # Create test environment
  export TEST_DIR="$(mktemp -d)"
}

# Runs after each test
teardown() {
  # Cleanup
  rm -rf "$TEST_DIR"
}

@test "function returns success" {
  run my_function "arg1" "arg2"
  [ "$status" -eq 0 ]
  [ "$output" = "expected output" ]
}

@test "function handles errors" {
  run my_function "invalid"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "Error:" ]]
}
```

### Running Tests

```bash
# Run all tests
bats test/

# Run specific file
bats test/script.bats

# Verbose output
bats --tap test/

# Pretty formatter
bats --pretty test/

# Filter tests by name
bats --filter "pattern" test/
```

### Assertions

```bash
@test "status code assertions" {
  run command
  [ "$status" -eq 0 ]    # Success
  [ "$status" -ne 0 ]    # Failure
  [ "$status" -eq 2 ]    # Specific code
}

@test "output assertions" {
  run echo "hello world"
  [ "$output" = "hello world" ]           # Exact match
  [[ "$output" =~ hello ]]               # Regex match
  [ "${lines[0]}" = "hello world" ]      # First line
  [ "${#lines[@]}" -eq 1 ]              # Line count
}

@test "file assertions" {
  run create_file "$TEST_DIR/file.txt"
  [ -f "$TEST_DIR/file.txt" ]           # File exists
  [ -r "$TEST_DIR/file.txt" ]           # Readable
  [ -x "$TEST_DIR/script.sh" ]          # Executable
  [ -s "$TEST_DIR/file.txt" ]           # Non-empty
}
```

### Helper Libraries

**bats-support** - Additional assertions:

```bash
# Install
brew tap kaos/shell
brew install bats-support

# Use in tests
load '/usr/local/lib/bats-support/load.bash'
load '/usr/local/lib/bats-assert/load.bash'

@test "with helpers" {
  run command
  assert_success
  assert_output "expected"
  assert_line --index 0 "first line"
  refute_output --partial "error"
}
```

### Mocking

```bash
@test "mock external command" {
  # Create mock function
  function curl() {
    echo "MOCK: curl $*"
    return 0
  }
  export -f curl

  run my_script_that_uses_curl
  assert_success
  assert_output --partial "MOCK: curl"
}

@test "mock with temp script" {
  # Create mock executable
  cat > "$TEST_DIR/mock-curl" <<'EOF'
#!/bin/bash
echo "MOCK RESPONSE"
exit 0
EOF
  chmod +x "$TEST_DIR/mock-curl"

  # Add to PATH
  export PATH="$TEST_DIR:$PATH"

  run my_script
  assert_success
}
```

### Skipping Tests

```bash
@test "not implemented yet" {
  skip "Waiting for feature X"
  run new_feature
}

@test "only on Linux" {
  if [[ "$(uname)" != "Linux" ]]; then
    skip "Linux only"
  fi

  run linux_specific_command
  assert_success
}
```

### Parallel Execution

```bash
# Run tests in parallel (4 jobs)
bats --jobs 4 test/

# Use GNU parallel
find test -name "*.bats" | parallel -j 4 bats {}
```

## shellspec (BDD-Style)

Behavior-driven testing framework with rich features.

### Installation

```bash
# Install
curl -fsSL https://git.io/shellspec | sh

# Or with package manager
brew install shellspec
```

### Basic Spec

```bash
#shellspec
# spec/script_spec.sh

Describe 'my_script'
  Include script.sh

  It 'returns success for valid input'
    When call my_function "valid"
    The status should eq 0
    The output should eq "success"
  End

  It 'returns error for invalid input'
    When call my_function "invalid"
    The status should eq 1
    The stderr should include "Error"
  End
End
```

### Running Specs

```bash
# Run all specs
shellspec

# Run specific spec
shellspec spec/script_spec.sh

# Verbose output
shellspec --format documentation

# Coverage report
shellspec --kcov
```

### Mocking with shellspec

```bash
Describe 'with mocks'
  mock_curl() {
    echo "MOCK: $*"
  }

  It 'uses mocked command'
    curl() { mock_curl "$@"; }

    When call script_using_curl
    The output should include "MOCK"
  End
End
```

### Pending Specs

```bash
Describe 'future feature'
  Pending 'implement X'

  It 'will do something'
    # Test code here
  End
End
```

## shunit2 (xUnit-Style)

Traditional xUnit-style testing framework.

### Installation

```bash
# Download
curl -L https://raw.githubusercontent.com/kward/shunit2/master/shunit2 > shunit2
chmod +x shunit2
```

### Basic Test

```bash
#!/bin/bash
# test_script.sh

# Source script under test
. ./script.sh

# Setup function
setUp() {
  TEST_DIR="$(mktemp -d)"
}

# Teardown function
tearDown() {
  rm -rf "$TEST_DIR"
}

# Test functions (must start with 'test')
testFunctionSuccess() {
  result=$(my_function "input")
  assertEquals "expected output" "$result"
}

testFunctionFailure() {
  my_function "invalid" 2>/dev/null
  assertNotEquals 0 $?
}

# Load shunit2
. ./shunit2
```

### Running Tests

```bash
./test_script.sh
```

## Coverage Analysis

### kcov (Code Coverage)

```bash
# Install kcov
brew install kcov  # macOS
sudo apt-get install kcov  # Ubuntu

# Run with coverage
kcov --exclude-pattern=/usr coverage/ bats test/

# View coverage report
open coverage/index.html
```

### Manual Coverage Tracking

```bash
#!/usr/bin/env bats
# Track which functions are tested

setup() {
  declare -gA COVERED_FUNCTIONS=()
}

test_coverage() {
  COVERED_FUNCTIONS["$1"]=1
}

teardown_file() {
  # Report coverage
  echo "Covered functions: ${!COVERED_FUNCTIONS[@]}"
}

@test "function A" {
  test_coverage "function_a"
  run function_a
  assert_success
}
```

## Test Organization

### Directory Structure

```
project/
├── script.sh
├── lib/
│   ├── utils.sh
│   └── config.sh
└── test/
    ├── test_helper.bash      # Shared test utilities
    ├── script.bats           # Main script tests
    ├── lib/
    │   ├── utils.bats        # Library tests
    │   └── config.bats
    └── fixtures/             # Test data
        ├── input.txt
        └── expected.txt
```

### Test Helper

```bash
# test/test_helper.bash

# Shared setup
setup_test_environment() {
  export TEST_DIR="$(mktemp -d)"
  export PATH="$TEST_DIR:$PATH"
}

# Shared teardown
cleanup_test_environment() {
  rm -rf "$TEST_DIR"
}

# Custom assertions
assert_file_contains() {
  local file="$1"
  local pattern="$2"
  grep -q "$pattern" "$file" || {
    echo "File $file does not contain: $pattern"
    return 1
  }
}

# Mock helpers
create_mock_command() {
  local command="$1"
  local response="$2"

  cat > "$TEST_DIR/$command" <<EOF
#!/bin/bash
echo "$response"
EOF
  chmod +x "$TEST_DIR/$command"
}
```

### Using Test Helper

```bash
#!/usr/bin/env bats
# test/script.bats

load test_helper

setup() {
  setup_test_environment
}

teardown() {
  cleanup_test_environment
}

@test "uses custom assertion" {
  echo "hello" > "$TEST_DIR/file.txt"
  assert_file_contains "$TEST_DIR/file.txt" "hello"
}

@test "uses mock helper" {
  create_mock_command "curl" "MOCK RESPONSE"
  run curl
  [ "$output" = "MOCK RESPONSE" ]
}
```

## Integration Testing

### Testing with Docker

```bash
@test "script works in container" {
  skip_if_no_docker

  docker run --rm \
    -v "$PWD:/work" \
    -w /work \
    bash:5.2 \
    ./script.sh --test

  [ $? -eq 0 ]
}

skip_if_no_docker() {
  command -v docker &>/dev/null || skip "Docker not available"
}
```

### Testing with Multiple Shells

```bash
@test "works with different shells" {
  local shells=(bash zsh)

  for shell in "${shells[@]}"; do
    command -v "$shell" &>/dev/null || continue

    run $shell script.sh
    [ "$status" -eq 0 ]
  done
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]

    steps:
      - uses: actions/checkout@v3

      - name: Install bats
        run: |
          if [[ "$RUNNER_OS" == "Linux" ]]; then
            sudo apt-get install -y bats
          else
            brew install bats-core
          fi

      - name: Run tests
        run: bats test/

      - name: Generate coverage
        run: |
          sudo apt-get install -y kcov
          kcov coverage/ bats test/

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          directory: ./coverage
```

### GitLab CI

```yaml
test:
  image: bash:5.2
  before_script:
    - apk add --no-cache bats
  script:
    - bats test/
  coverage: '/^Covered: (\d+\.\d+)%/'
```

## Best Practices

### 1. Test Naming

```bash
# Good: Descriptive, specific
@test "backup_database creates compressed file with timestamp"

# Bad: Vague
@test "test1"
```

### 2. One Assertion Per Test

```bash
# Good: Focused
@test "function returns success" {
  run my_function
  [ "$status" -eq 0 ]
}

@test "function outputs expected message" {
  run my_function
  [ "$output" = "success" ]
}

# Bad: Multiple concerns
@test "function works" {
  run my_function
  [ "$status" -eq 0 ]
  [ "$output" = "success" ]
  [ -f "output.txt" ]
}
```

### 3. Test Independence

```bash
# Good: Self-contained
@test "creates file" {
  local tmpfile="$TEST_DIR/test.txt"
  create_file "$tmpfile"
  [ -f "$tmpfile" ]
}

# Bad: Depends on other tests
@test "reads file" {
  # Assumes previous test created file!
  content=$(cat "$tmpfile")
}
```

### 4. Edge Cases

```bash
@test "handles empty input" {
  run my_function ""
  [ "$status" -eq 1 ]
}

@test "handles whitespace" {
  run my_function "  "
  [ "$status" -eq 1 ]
}

@test "handles special characters" {
  run my_function '$`!@#'
  [ "$status" -eq 0 ]
}
```

## Debugging Tests

### Enable Trace

```bash
@test "debug with trace" {
  set -x  # Enable trace
  run my_function
  set +x  # Disable trace
  [ "$status" -eq 0 ]
}
```

### Print Variables

```bash
@test "debug variables" {
  run my_function
  echo "status: $status"
  echo "output: $output"
  echo "lines: ${lines[@]}"
  [ "$status" -eq 0 ]
}
```

### Run Single Test

```bash
# Run only matching tests
bats --filter "specific test name" test/
```

## References

- [bats-core Documentation](https://bats-core.readthedocs.io/)
- [shellspec Documentation](https://shellspec.info/)
- [shunit2 Documentation](https://github.com/kward/shunit2)
- [kcov Code Coverage](https://github.com/SimonKagstrom/kcov)
