# SOPS + age Best Practices for Securing .env Files

**Researched:** 2026-03-20
**Sources:** getsops.io official docs (v3.12.1), getsops/sops GitHub issues and discussions, GitGuardian, Flux CD docs, Techno Tim, Hey Linux, OneUptime engineering guides

---

## Overview

SOPS (Secrets OPerationS) encrypts individual values within structured files (YAML, JSON, ENV, INI) while leaving keys in plaintext. This produces git-diff-friendly output — reviewers can see which variable changed without seeing its value. age is the recommended encryption backend: it is simple, modern, requires no infrastructure, and generates small keys with a single command.

SOPS works by generating a random per-file Data Encryption Key (DEK), encrypting each value with AES256-GCM using that DEK, then encrypting the DEK itself with your master key (age, GPG, AWS KMS, etc.). The encrypted DEK and metadata are stored inline in the `sops` block of the file. The master key (your age private key) never touches the actual secret values — only the DEK.

---

## 1. .sops.yaml Configuration Best Practices

### Basic Structure

Place `.sops.yaml` at the repository root. SOPS walks up the directory tree from the file being encrypted until it finds a `.sops.yaml`.

```yaml
creation_rules:
  - path_regex: \.env(\.encrypted)?$
    age: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p
```

### Rule Matching Order

Rules are evaluated **top to bottom; the first match wins**. Always place more specific rules before general ones:

```yaml
creation_rules:
  # Most specific first: production secrets
  - path_regex: environments/production/.*\.enc\.yaml$
    age: >-
      age1prod...,
      age1backup...

  # Staging with different key
  - path_regex: environments/staging/.*\.enc\.yaml$
    age: age1staging...

  # Catch-all for all other YAML
  - path_regex: .*\.enc\.yaml$
    age: age1dev...
```

### Recommended path_regex Patterns for .env Files

The following patterns are commonly used for `.env` file matching:

```yaml
# Match .env exactly (dotenv store auto-detected by filename)
- path_regex: (^|/)\.env$

# Match .env.encrypted (common naming convention)
- path_regex: (^|/)\.env\.encrypted$

# Match .env.enc (shorter convention)
- path_regex: (^|/)\.env\.enc$

# Match any .env variant: .env, .env.local, .env.production, etc.
- path_regex: (^|/)\.env(\.[a-zA-Z0-9]+)?$

# Match secrets files stored as YAML (preferred approach - see Section 3)
- path_regex: secrets(\.encrypted)?\.yaml$

# Named convention used in some teams
- path_regex: /*secrets(\.encrypted)?\.yaml$
```

A widely cited real-world pattern from dfrojas.com:
```yaml
creation_rules:
  - path_regex: /*secrets(\.encrypted)?.yaml$
    age: <age-public-key>
```

### Key Groups vs. Single age Recipients

**Single recipient** (solo developer or single environment):
```yaml
creation_rules:
  - path_regex: .*\.enc\.yaml$
    age: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p
```

**Multiple recipients** (any one key can decrypt — OR logic):
```yaml
creation_rules:
  - path_regex: .*\.enc\.yaml$
    age: >-
      age1developer...,
      age1cicd...,
      age1backup...
```

**Key groups with Shamir's Secret Sharing** (N-of-M required — AND logic):
```yaml
creation_rules:
  - path_regex: secrets/production/.*\.yaml$
    shamir_threshold: 2
    key_groups:
      - age:
          - age1teamlead...
      - age:
          - age1seniordev...
      - age:
          - age1backup...
```

With Shamir threshold 2 of 3, any two of the three key holders must participate to decrypt. This is appropriate for high-security production secrets. For most developer workflows, the multi-recipient (OR) approach is sufficient and far simpler to operate.

**Recommendation:** Use multiple recipients (OR) with one key per developer/machine plus a dedicated CI/CD key and a backup key. Reserve Shamir groups for compliance-critical production secrets.

### Additional .sops.yaml Options

Control which fields get encrypted (useful for YAML but irrelevant for dotenv format):

```yaml
creation_rules:
  - path_regex: .*secrets.*\.yaml$
    age: age1...
    encrypted_regex: ^(data|stringData|password|secret|token|key|credential)$
    # OR use encrypted_suffix to encrypt only keys ending with _secret:
    # encrypted_suffix: _secret
```

For store-level formatting:
```yaml
stores:
  yaml:
    indent: 2
  json:
    indent: 2
creation_rules:
  - ...
```

---

## 2. age Key Management

### Default Storage Locations

SOPS looks for the age private key file at:

| Platform | Default path |
|----------|-------------|
| Linux    | `$XDG_CONFIG_HOME/sops/age/keys.txt` → `$HOME/.config/sops/age/keys.txt` |
| macOS    | `$XDG_CONFIG_HOME/sops/age/keys.txt` → `$HOME/Library/Application Support/sops/age/keys.txt` |
| Windows  | `%AppData%\sops\age\keys.txt` |

The file format is one age X25519 identity per line; lines beginning with `#` are comments and ignored.

### Generating a Key

```bash
age-keygen -o ~/.config/sops/age/keys.txt
# Output: Public key: age1ql3z7hjy54pw3...
```

Or generate to a named file for multi-key setups:
```bash
age-keygen -o ~/keys/project-dev.agekey
```

### File Permissions

Set permissions to owner-read-only immediately after generation. This is critical — any other process running as your user can read the key if permissions are left open:

```bash
chmod 600 ~/.config/sops/age/keys.txt
# Verify
ls -la ~/.config/sops/age/keys.txt
# Should show: -rw------- 1 user group ...
```

### Overriding Key Location

```bash
# Point to a specific file
export SOPS_AGE_KEY_FILE=/path/to/key.agekey

# Or pass the key value directly (useful in CI/CD)
export SOPS_AGE_KEY="AGE-SECRET-KEY-1..."

# Or use a command to retrieve the key (e.g., from a vault)
export SOPS_AGE_KEY_CMD="op read op://vault/sops-age-key/credential"
```

### Multi-Machine Workflow

Two valid approaches:

**Option A: Per-machine keys (recommended for teams)**
Each machine or developer generates their own key. All public keys are listed in `.sops.yaml`. Files are encrypted for all recipients simultaneously.

```bash
# Developer Alice on machine 1
age-keygen -o ~/.config/sops/age/keys.txt
# Note public key: age1alice...

# Developer Bob on machine 2
age-keygen -o ~/.config/sops/age/keys.txt
# Note public key: age1bob...
```

In `.sops.yaml`:
```yaml
creation_rules:
  - path_regex: secrets.*\.yaml$
    age: >-
      age1alice...,
      age1bob...,
      age1cicd...
```

Anyone with any of these private keys can decrypt. To add a new machine, add the new public key to `.sops.yaml`, then run `sops updatekeys` on all encrypted files.

**Option B: Shared key (solo developer, multiple machines)**
Generate one key, store it securely (password manager, 1Password, Bitwarden), and retrieve it on each machine. Less auditable but simpler for single-developer projects.

```bash
# Store in 1Password, then retrieve on new machine:
op read "op://Personal/SOPS Age Key/key" > ~/.config/sops/age/keys.txt
chmod 600 ~/.config/sops/age/keys.txt
```

### Key Backup Strategy

Private keys are the single point of failure. If lost, all encrypted files are permanently unreadable.

Recommended backup approaches (in order of preference):
1. **Password manager** (1Password, Bitwarden, KeePassXC) — store the full `keys.txt` content as a secure note
2. **Offline hardware** — print the key or write it to an encrypted USB drive stored physically separate from your machines
3. **Dedicated backup age recipient** — generate a separate backup key, include its public key in all `.sops.yaml` rules, store the backup private key offline. If your primary key is lost, you can still decrypt with the backup.

```yaml
# Include a backup recipient in all rules
creation_rules:
  - path_regex: .*secrets.*\.yaml$
    age: >-
      age1primary...,
      age1backup-stored-offline...
```

**Never commit private keys to git.** Add to `.gitignore`:
```
*.agekey
keys.txt
# but NOT .sops.yaml — that should be committed
```

### CI/CD Key Management

CI/CD environments should have their own dedicated age key — never reuse developer keys:

```bash
# Generate a CI/CD-specific key
age-keygen -o ci-key.agekey
cat ci-key.agekey  # Note public key and store private key in CI secret manager
```

Store the private key as a CI secret (GitHub Actions Secret, GitLab CI Variable, etc.), then reference at runtime:
```bash
# In CI pipeline
echo "$SOPS_AGE_PRIVATE_KEY" > /tmp/age-key.txt
export SOPS_AGE_KEY_FILE=/tmp/age-key.txt
sops decrypt secrets.enc.yaml
rm /tmp/age-key.txt  # Clean up immediately after use
```

---

## 3. Encryption Workflow

### Dotenv Native Format vs. YAML — Which to Use

This is a critical decision with significant practical implications.

**SOPS dotenv store limitations (known issues as of SOPS 3.x):**

1. **Not roundtrip-safe** (GitHub issue #1435, reported by SOPS maintainer felixfontein): The dotenv store escapes newlines as literal `\n` but does not escape backslashes themselves. This means `\n` in a value and a literal newline cannot be distinguished on round-trip.
2. **Quote stripping**: SOPS dotenv handling strips quotes during encryption (e.g., `ID="123#567"` becomes `ID=123#567` after decrypt), breaking dotenv parsers that rely on quoted values with special characters.
3. **Comment handling is fragile**: Inline comments and comments in non-dotenv-named files (e.g., `.env.example`) require explicit `--input-type dotenv --output-type dotenv` flags; without them the encrypted output defaults to JSON and comments are lost.
4. **No spec compatibility**: The SOPS dotenv parser is primitive — it assumes all keys are strings without `=`, does not support the full dotenv spec (multiline values, exports, etc.).
5. **Extension detection**: A file named `.env` is auto-detected as dotenv format. Files named `secrets.env` or `.env.encrypted` may not be detected correctly and require explicit `--input-type dotenv`.

**Recommendation: prefer YAML over native dotenv format.**

Store secrets as YAML and generate the `.env` file at runtime (during deployment or local dev setup). This avoids all dotenv store limitations and gains the full power of YAML processing (comments, structured data, `encrypted_regex`).

```yaml
# secrets.enc.yaml (stored in git, encrypted)
DATABASE_URL: postgres://user:pass@host/db
API_KEY: sk-abc123
REDIS_URL: redis://localhost:6379
```

Generate `.env` at runtime:
```bash
sops decrypt secrets.enc.yaml | python3 -c "
import sys, yaml
data = yaml.safe_load(sys.stdin)
for k, v in data.items():
    if k != 'sops':
        print(f'{k}={v}')
" > .env
```

Or use SOPS exec-env for direct injection without writing to disk:
```bash
sops exec-env secrets.enc.yaml 'your-command-here'
```

### When dotenv Format IS Appropriate

If your tooling strictly requires committing a `.env`-style file, use dotenv format but be aware of the limitations:

```bash
# Encrypt a .env file using dotenv store
sops encrypt --input-type dotenv --output-type dotenv .env > .env.enc

# Decrypt
sops decrypt --input-type dotenv --output-type dotenv .env.enc > .env
```

Always specify both `--input-type` and `--output-type` explicitly when working with dotenv files that do not have the `.env` extension, or when piping:

```bash
sops encrypt --input-type dotenv --output-type dotenv --in-place .env.encrypted
```

### File Naming Conventions

Common conventions observed in the wild, with trade-offs:

| Convention | Example | Notes |
|-----------|---------|-------|
| `.env.encrypted` | `.env.encrypted` | Clear semantic meaning; SOPS may not auto-detect dotenv format |
| `.env.enc` | `.env.enc` | Shorter; same auto-detection caveat |
| `secrets.enc.yaml` | `secrets.enc.yaml` | Recommended — YAML format, auto-detected, diff-friendly |
| `secrets.sops.yaml` | `secrets.sops.yaml` | Common in Kubernetes/Flux workflows |
| `secrets.yaml` | `secrets.yaml` | Simple; gitignore the plaintext, commit the encrypted version separately |

**Recommended convention:** Use `.enc.yaml` suffix (e.g., `secrets.enc.yaml`) to make it unambiguous that a file is SOPS-encrypted and to leverage YAML format. The `.enc.` infix is a strong visual signal and is easy to gitignore the non-encrypted counterpart.

---

## 4. Git Integration

### What to Commit vs. What to Gitignore

**Commit to git:**
- `.sops.yaml` — encryption rules, public keys, path patterns
- `*.enc.yaml`, `secrets.enc.yaml`, `.env.encrypted` — encrypted secret files
- `.gitattributes` (if using SOPS diff driver)

**Gitignore (never commit):**
- `*.agekey`, `keys.txt`, any file containing a private key
- `.env`, `*.env.local` — plaintext secret files
- `secrets.yaml` (if using the pattern of separate plaintext + encrypted files)

Example `.gitignore` additions:
```gitignore
# Age private keys - NEVER commit
*.agekey
keys.txt

# Plaintext secrets - encrypt before committing
.env
.env.local
.env.*.local
secrets.yaml

# But DO commit encrypted versions:
# !secrets.enc.yaml  (no negation needed if only encrypted files exist)
```

### Git Diff Integration

SOPS can show meaningful diffs by decrypting both versions before diffing. Add to `.gitattributes`:
```
*.enc.yaml diff=sopsdiffer
secrets.enc.yaml diff=sopsdiffer
.env.encrypted diff=sopsdiffer
```

Configure the git diff driver once per machine:
```bash
git config diff.sopsdiffer.textconv "sops decrypt"
```

Now `git diff` and `git log -p` show decrypted diffs. This works with GUI git clients too since they call `git diff` internally. Note: requires the decryption key to be present locally.

### Pre-Commit Hooks

**Option A: pre-commit framework with gitleaks** (catch any accidentally staged secret):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: local
    hooks:
      - id: check-sops-encrypted
        name: Verify .env files are not staged in plaintext
        entry: bash -c 'git diff --cached --name-only | grep -E "^\.env$|/\.env$" && echo "ERROR: Plaintext .env file staged for commit" && exit 1 || exit 0'
        language: system
        pass_filenames: false
```

**Option B: squat/pre-commit-sops** (validates that SOPS-managed files are actually encrypted):

```yaml
repos:
  - repo: https://github.com/squat/pre-commit-sops
    rev: 0.1.0
    hooks:
      - id: sops
        files: '(secrets|\.env\.encrypted)'
```

**Option C: yuvipanda/pre-commit-hook-ensure-sops** (any file with `secret` in its path must be SOPS-encrypted):

```yaml
repos:
  - repo: https://github.com/yuvipanda/pre-commit-hook-ensure-sops
    rev: v1.0
    hooks:
      - id: sops-encryption
```

**Option D: custom shell hook** (bare-minimum, no dependencies):

Create `.git/hooks/pre-commit` (make executable with `chmod +x`):
```bash
#!/bin/bash
# Block commits of plaintext .env files
if git diff --cached --name-only | grep -qE '(^|/)\.env$'; then
  echo "ERROR: Plaintext .env file staged. Encrypt with SOPS first."
  exit 1
fi

# Optionally check that .env.enc / secrets.enc.yaml contain the sops metadata marker
for f in $(git diff --cached --name-only | grep -E '\.enc\.(yaml|json)$'); do
  if ! grep -q '"sops":' "$f" && ! grep -q 'sops:' "$f"; then
    echo "ERROR: $f does not appear to be SOPS-encrypted"
    exit 1
  fi
done
```

**Important git history note:** If a plaintext secret is ever committed, the secret is in git history even after deletion. Use `git filter-repo` (or BFG Repo-Cleaner) to purge it, then rotate the exposed credential immediately. Pre-commit hooks prevent this but are bypassable with `git commit --no-verify` — defense in depth (gitleaks CI scan, branch protection) is required.

---

## 5. Security Considerations

### What Metadata is Exposed (in Plaintext)

The `sops` block appended to every encrypted file contains the following in cleartext:

```yaml
sops:
  age:
    - recipient: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p
      enc: |
        -----BEGIN AGE ENCRYPTED FILE-----
        ...
        -----END AGE ENCRYPTED FILE-----
  lastmodified: "2026-03-20T10:00:00Z"
  mac: ENC[AES256_GCM,...]
  version: 3.12.1
```

Exposed metadata:
- **Recipient public keys** — reveals which age public keys can decrypt the file (fingerprints are public by design, but this identifies who has access)
- **Modification timestamp** — reveals when the file was last changed
- **SOPS version** — can help target version-specific vulnerabilities
- **Encrypted DEK** — the per-file data key, encrypted with your master key (safe as long as the master key is not compromised)

For KMS backends: KMS ARNs, GCP resource IDs, and Azure vault URLs are also exposed. These reveal cloud account structure.

**Key names are always in plaintext.** If your variable names are themselves sensitive (e.g., `STRIPE_LIVE_SECRET_KEY`), the name reveals the type of credential even if the value is encrypted.

### Common Mistakes

1. **Committing the age private key.** The most catastrophic mistake. Add `*.agekey` and `keys.txt` to `.gitignore` and enforce this with pre-commit hooks.

2. **No backup of the age private key.** If the key is lost, all encrypted files are permanently unreadable. Always have at least one backup copy in a password manager or offline secure storage.

3. **Reusing the same key across all environments.** A compromised dev key then compromises prod secrets. Use separate keys per environment.

4. **Forgetting to run `sops updatekeys` after adding a new developer.** New team members listed in `.sops.yaml` cannot decrypt existing files until all existing encrypted files are updated. This is a silent failure — the file looks valid but won't decrypt.

5. **Using `--in-place` on a plaintext file without keeping a backup.** SOPS `--in-place` overwrites the file. If encryption fails mid-operation, the file may be corrupted. Always test with a copy first or ensure the plaintext is committed or otherwise recoverable.

6. **Storing age keys inside the project directory with broad permissions.** Keys stored as `./key.agekey` in a project root can be accidentally committed or read by other processes. Store keys in `~/.config/sops/age/keys.txt` with `chmod 600`.

7. **Using unencrypted_comment_regex carelessly.** A bug-class exists (GitHub issue #1672) where `unencrypted_comment_regex` can unexpectedly leave entire sections unencrypted rather than just the adjacent line. Test the output visually after encryption.

8. **Dotenv roundtrip data loss.** Using dotenv format for values containing backslashes or `\n` sequences leads to data corruption on decrypt due to the known roundtrip bug. Use YAML format instead.

9. **Not verifying MAC.** SOPS authenticates the entire file structure with a MAC. Never manually edit encrypted SOPS files with a text editor — use `sops edit` instead, which handles decryption, editing, and re-encryption atomically.

10. **Key service without authentication.** The SOPS keyservice forwarding mode has no authentication or encryption. Only use it over a trusted channel (e.g., an SSH tunnel), never over an untrusted network.

### Cryptographic Properties

- Each encrypted value uses AES256-GCM with a unique IV — semantically secure
- The MAC is computed over the entire key tree (concatenated key names provide AAD), preventing structural tampering
- Value length is preserved in ciphertext (known limitation, GitHub issue #815) — observable to anyone with access to the encrypted file
- The KMS/age master key only encrypts the DEK (~32 bytes), not the secrets themselves — this is the standard "envelope encryption" pattern

---

## 6. .sops.yaml path_regex Reference

All patterns use Go regexp syntax (RE2 engine — no lookaheads).

### Patterns for .env Files

```yaml
# Exact filename .env at any directory depth
- path_regex: (^|/)\.env$

# .env with any suffix (covers .env.local, .env.production, .env.test, etc.)
- path_regex: (^|/)\.env(\.[^/]+)?$

# Explicit encrypted variants
- path_regex: (^|/)\.env\.encrypted$
- path_regex: (^|/)\.env\.enc$

# Any file ending in .env.yaml or .env.enc.yaml
- path_regex: \.env(\.enc)?\.yaml$

# secrets.yaml / secrets.enc.yaml anywhere in the tree
- path_regex: (^|/)secrets(\.enc)?\.yaml$

# Kubernetes-style: matches *.sops.yaml
- path_regex: .*\.sops\.yaml$

# Files under a secrets/ directory
- path_regex: (^|/)secrets/.*\.(yaml|json)$
```

### Environment-Based Patterns

```yaml
creation_rules:
  # Production: two keys required (Shamir) or both recipients
  - path_regex: (^|/)production/.*\.enc\.yaml$
    age: >-
      age1prod-primary...,
      age1prod-backup...

  # Staging: one key
  - path_regex: (^|/)staging/.*\.enc\.yaml$
    age: age1staging...

  # Development: dev key only
  - path_regex: (^|/)development/.*\.enc\.yaml$
    age: age1dev...

  # Catch-all: encrypt everything else with dev key
  - path_regex: .*\.enc\.yaml$
    age: age1dev...
```

### Pattern Matching Notes

- Patterns match against the full file path as seen from the `.sops.yaml` location
- The path is normalized with forward slashes on all platforms
- Omitting `path_regex` entirely creates a catch-all that matches all files
- First matching rule wins — ordering is significant
- Be careful with overly broad patterns like `.*\.yaml$` — this will match `.sops.yaml` itself if you run SOPS from the repo root

---

## 7. sops updatekeys vs. Decrypt-then-Re-encrypt

### `sops updatekeys` (Recommended)

`updatekeys` reads the current `.sops.yaml` configuration and synchronizes the recipient list in each encrypted file **without changing the per-file data key or re-encrypting any values**.

Specifically:
- Re-wraps the existing DEK for new recipients (adds new `enc` blocks)
- Removes `enc` blocks for recipients no longer in `.sops.yaml`
- The encrypted values themselves are unchanged
- The MAC is unchanged (since the data key and values are unchanged)
- Produces a minimal diff — only the `sops.age` block changes

```bash
# Update a single file
sops updatekeys secrets.enc.yaml

# Non-interactive (for scripts)
sops updatekeys -y secrets.enc.yaml

# Update all encrypted files in a repo
find . -name "*.enc.yaml" -exec grep -l "sops:" {} \; | \
  xargs -I{} sops updatekeys -y {}
```

Workflow for adding a new team member:
1. New member generates `age-keygen -o ~/.config/sops/age/keys.txt` and shares public key
2. Update `.sops.yaml` to add their public key
3. Run `sops updatekeys -y` on all affected encrypted files
4. Commit the updated encrypted files — they now include an additional DEK copy for the new recipient

### `sops rotate` (Full Re-encryption)

`sops rotate` generates a **new** DEK and re-encrypts every value. Every encrypted field in the file changes, producing a large diff.

```bash
# Rotate data key in place (all values get new ciphertext)
sops rotate -i secrets.enc.yaml

# Rotate and simultaneously add/remove recipients
sops rotate -i --add-age age1newkey... --rm-age age1oldkey... secrets.enc.yaml
```

When to use `rotate` instead of `updatekeys`:
- A key is **compromised** — the old key holder may have cached the old DEK. Rotating generates a completely new DEK that the old holder cannot derive.
- You want to re-randomize all IVs and ciphertext for audit/compliance reasons.
- The official docs note: when removing a key, "it is recommended to rotate the data key using `-r`, otherwise, owners of the removed key may have had access to the data key in the past."

### Decision Guide

| Scenario | Use |
|---------|-----|
| Adding a new team member | `updatekeys` |
| Onboarding a new machine | `updatekeys` |
| Removing a departing team member (non-security incident) | `updatekeys` then later `rotate` |
| Key was compromised | `rotate` immediately |
| Periodic security hygiene rotation | `rotate` |
| CI/CD key rotation (routine) | `updatekeys` |

### Key Rotation Workflow (Full Rotation)

```bash
# Phase 1: Generate new key, add to .sops.yaml alongside old key
age-keygen -o new-key.agekey
# Edit .sops.yaml to include both old and new public keys

# Phase 2: Update all files to include new key (both keys can decrypt)
find . -name "*.enc.yaml" -exec grep -l "sops:" {} \; | \
  xargs -I{} sops updatekeys -y {}

# Verify decryption works with new key
SOPS_AGE_KEY_FILE=new-key.agekey sops decrypt secrets.enc.yaml

# Phase 3: Remove old key from .sops.yaml and re-encrypt with new key only
# Edit .sops.yaml to remove old key
find . -name "*.enc.yaml" -exec grep -l "sops:" {} \; | \
  xargs -I{} sops updatekeys -y {}

# Optional: rotate data key too (if old key may have been compromised)
find . -name "*.enc.yaml" -exec grep -l "sops:" {} \; | \
  xargs -I{} sops rotate -i {}

# Commit all changes
git add .sops.yaml **/*.enc.yaml
git commit -m "chore(secrets): rotate SOPS age keys"
```

---

## 8. Summary of Recommendations

| Decision | Recommendation |
|---------|---------------|
| Encryption backend | age (simpler than GPG, no infrastructure vs. cloud KMS) |
| File format for secrets | YAML (`.enc.yaml`) — avoid dotenv format due to roundtrip bugs |
| File naming | `secrets.enc.yaml` or `*.sops.yaml` — unambiguous, diff-friendly |
| Key storage | `~/.config/sops/age/keys.txt` with `chmod 600` |
| Key backup | Password manager + offline copy; include a backup recipient in all rules |
| Multi-developer access | Multiple recipients (OR logic) in `.sops.yaml` — one key per developer |
| Environments | Separate age keys per environment; never share prod key with dev |
| CI/CD | Dedicated CI key stored as CI secret; inject via `SOPS_AGE_KEY` env var |
| Adding recipient | `sops updatekeys -y` |
| Compromised key | `sops rotate -i` after removing old key from `.sops.yaml` |
| Git diff | `.gitattributes` with `diff=sopsdiffer` driver |
| Preventing accidents | pre-commit hooks (gitleaks + custom check) |
| `.sops.yaml` | Commit it — it contains only public keys and rules, no secrets |

---

## References

- [SOPS Official Documentation](https://getsops.io/docs/) — getsops.io
- [getsops/sops GitHub](https://github.com/getsops/sops) — source and issues (v3.12.1 latest as of 2026-02-22)
- [GitGuardian: A Comprehensive Guide to SOPS](https://blog.gitguardian.com/a-comprehensive-guide-to-sops/) — 2024-09-05
- [SOPS dotenv roundtrip issue #1435](https://github.com/getsops/sops/issues/1435) — felixfontein, 2024-02-10
- [SOPS dotenv docs request #1818](https://github.com/getsops/sops/issues/1818) — 2025-03-29
- [Rotating SOPS Keys - Techno Tim](https://technotim.com/posts/rotate-sops-encryption-keys/) — 2023-03-05
- [Using SOPS + age to Encrypt Files - Hey! Linux](https://blog.heylinux.com/en/2026/02/using-sops-age-to-encrypt-files/) — 2026-02
- [How to Rotate SOPS Age Keys Without Re-Encrypting All Files](https://oneuptime.com/blog/post/2026-03-13-how-to-rotate-sops-age-keys-without-re-encrypting-all-files-in-flux/view) — 2026-03-13
- [How to Configure SOPS Creation Rules in .sops.yaml](https://oneuptime.com/blog/post/2026-03-13-how-to-configure-sops-creation-rules-in-sops-yaml-for-flux/view) — 2026-03-13
- [SOPS Pre-Commit Hooks for Flux](https://oneuptime.com/blog/post/2026-03-13-how-to-set-up-sops-pre-commit-hooks-for-flux-repositories/view) — 2026-03-13
- [squat/pre-commit-sops](https://github.com/squat/pre-commit-sops) — pre-commit hook for SOPS validation
- [yuvipanda/pre-commit-hook-ensure-sops](https://github.com/yuvipanda/pre-commit-hook-ensure-sops) — pre-commit hook for SOPS enforcement
- [My recipe: SOPS + age - dfrojas.com](https://dfrojas.com/software/managing-sensitive-data-with-sops-%2B-age.html)
- [sops updatekeys discussion #919](https://github.com/getsops/sops/discussions/919) — felixfontein batch updatekeys command
- [Encrypted data reveals ciphertext length #815](https://github.com/mozilla/sops/issues/815) — known metadata leakage
