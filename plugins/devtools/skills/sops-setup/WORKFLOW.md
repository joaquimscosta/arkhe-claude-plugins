# SOPS Setup Workflow

Detailed per-step flows. Each step follows the pattern: detect existing state, ask user preferences via `AskUserQuestion`, show confirmation, then execute.

**Format note**: All encryption uses YAML format (not dotenv) to avoid SOPS bug #1435. The `dotenv_yaml.py` helper script handles conversion transparently.

---

## Step 1: Install Tools

**Detect**: Check `tools.sops.installed` and `tools.age.installed`

**If both installed**: Skip — show versions and move to next step.

**If missing**: Show install commands based on `os` field.

### macOS

```bash
brew install sops age
```

### Linux (Debian/Ubuntu)

```bash
# age
sudo apt-get update && sudo apt-get install -y age

# sops — download latest binary
SOPS_VERSION=$(curl -s https://api.github.com/repos/getsops/sops/releases/latest | grep tag_name | cut -d '"' -f 4)
curl -Lo /tmp/sops "https://github.com/getsops/sops/releases/download/${SOPS_VERSION}/sops-${SOPS_VERSION}.linux.amd64"
sudo install -m 755 /tmp/sops /usr/local/bin/sops
rm /tmp/sops
```

### Linux (Other)

```bash
# age — from source or binary
# https://github.com/FiloSottile/age/releases

# sops — from binary
# https://github.com/getsops/sops/releases
```

**AskUserQuestion**:
- Install now (run commands above)
- I'll install manually (skip, re-run setup after)

**Post-install**: Re-run detector to verify tools are available.

---

## Step 2: Generate Machine Key

**Detect**: Check `age_key.exists`

**If exists**: Show the public key (truncated) and path. Skip to next step.

**If missing**:

1. Create the directory:
   ```bash
   mkdir -p ~/.config/sops/age
   ```

2. Generate the key pair:
   ```bash
   age-keygen -o ~/.config/sops/age/keys.txt
   ```

3. Set secure permissions:
   ```bash
   chmod 600 ~/.config/sops/age/keys.txt
   ```

4. Extract and display the public key:
   ```bash
   grep "public key:" ~/.config/sops/age/keys.txt
   ```

5. Tell user:
   > **Save this public key somewhere safe** (password manager, secure note).
   > You'll need it when authorizing this machine on other projects.
   > The private key stays at `~/.config/sops/age/keys.txt` — never share it.

---

## Step 3: Generate Backup Key

**AskUserQuestion**:
- Generate backup key (Recommended) — creates a recovery key for disaster scenarios
- Skip — can add one later via `/devtools:sops-add-key`

**If generating**:

1. Generate a key pair (output to stdout, NOT saved to disk):
   ```bash
   age-keygen
   ```
   This outputs:
   ```
   # created: 2024-01-15T10:30:00Z
   # public key: age1backupkeyhere...
   AGE-SECRET-KEY-1PRIVATEBACKUPKEYHERE...
   ```

2. Display the full output and tell user:
   > **CRITICAL: Copy this ENTIRE output (including the AGE-SECRET-KEY- line) to a secure location:**
   > - Password manager (1Password, Bitwarden, etc.)
   > - Encrypted USB drive
   > - Printed and stored in a safe
   >
   > This is your disaster recovery key. If you lose access to all machines,
   > this key can decrypt everything. It will NOT be saved to this machine.

3. Extract and store the public key for use in `.sops.yaml` (Step 4).

---

## Step 4: Create `.sops.yaml`

**Detect**: Check `project.sops_yaml.exists`

**If exists with current machine key**: Show config summary, skip to next step.

**If exists without current key**: Offer to add this machine's key:

`AskUserQuestion`:
- Add my key to existing .sops.yaml
- Replace .sops.yaml entirely
- Skip (keep current config)

**If missing**:

Write `.sops.yaml` to project root. Include machine key + backup key (if generated):

```yaml
creation_rules:
  - path_regex: (^|/)\.env\.[^/]+\.enc\.yaml$
    age: >-
      <machine-public-key>,
      <backup-public-key>
```

If no backup key was generated:
```yaml
creation_rules:
  - path_regex: (^|/)\.env\.[^/]+\.enc\.yaml$
    age: >-
      <machine-public-key>
```

---

## Step 5: Set Up `.gitattributes`

**Detect**: Check if `.gitattributes` exists and contains `sopsdiffer`

**If already configured**: Skip.

**If missing**:

1. Append to `.gitattributes` (create if doesn't exist):
   ```
   *.enc.yaml diff=sopsdiffer
   ```

2. Configure git locally:
   ```bash
   git config diff.sopsdiffer.textconv "sops decrypt"
   ```

3. This enables `git diff` to show decrypted content for encrypted files, making code review easier.

---

## Step 6: Update `.gitignore`

**Detect**: Check `project.gitignore`

**Actions needed** (show as confirmation table):

| Check | Current | Needed | Action |
|-------|---------|--------|--------|
| `.env*` ignored | yes/no | yes | Add if missing |
| `*.enc.yaml` ignored | yes/no | no | Remove if present |

If `.gitignore` doesn't exist, create it.

If changes needed, `AskUserQuestion`:
- Apply changes (show diff preview)
- Skip

**Append to `.gitignore`** (if `.env*` rules missing):
```
# Secrets — never commit plaintext env files
.env
.env.*
!.env.example
```

**Remove from `.gitignore`** (if `*.enc.yaml` is ignored):
Remove lines containing `enc.yaml` pattern.

---

## Step 7: Encrypt Files

**Detect**: Check `project.env_files`

**If empty**: Skip — no files to encrypt.

**If non-empty**:

`AskUserQuestion` (multiSelect: true) — list each `.env*` file:
- `.env.local`
- `.env.production`
- etc.

For each selected file, convert and encrypt:
```bash
# Convert dotenv → YAML
python3 ${CLAUDE_SKILL_DIR}/scripts/dotenv_yaml.py to-yaml <file> > <file>.enc.yaml.tmp

# Encrypt the YAML
sops --encrypt <file>.enc.yaml.tmp > <file>.enc.yaml

# Clean up temp file
rm <file>.enc.yaml.tmp
```

Verify:
```bash
test -s <file>.enc.yaml && echo "OK" || echo "FAILED"
```

---

## Step 8: Confirmation Summary

Show a complete table of all actions taken during the session:

```
## Setup Complete

| Step | Action | Result |
|------|--------|--------|
| Tools | sops 3.9.4, age 1.2.0 | installed |
| Machine key | Generated | age1abc...def |
| Backup key | Generated | age1xyz...uvw (saved offline) |
| Permissions | chmod 600 keys.txt | done |
| Config | .sops.yaml created | 2 keys authorized |
| Git | .gitattributes updated | sopsdiffer configured |
| Git | .gitignore updated | .env* ignored |
| Encrypt | .env.local → .env.local.enc.yaml | done |

## Next Steps
- Commit .sops.yaml, .gitattributes, and *.enc.yaml files to git
- On another machine: clone, install sops+age, place age key, run /devtools:sops-decrypt
- To add another machine: /devtools:sops-add-key with the new machine's public key
- To encrypt after .env changes: /devtools:sops-encrypt
- To decrypt after pulling: /devtools:sops-decrypt
```
