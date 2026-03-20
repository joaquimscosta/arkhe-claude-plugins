# SOPS Setup Examples

## Example 1: Fresh Setup (Nothing Installed)

**User**: `/devtools:sops-setup`

**Detection output**:
```json
{
  "tools": {
    "sops": { "installed": false },
    "age": { "installed": false }
  },
  "age_key": { "exists": false, "expected_path": "/home/user/.config/sops/age/keys.txt" },
  "project": {
    "sops_yaml": { "exists": false },
    "env_files": [".env.local"],
    "encrypted_files": [],
    "gitignore": { "exists": true, "ignores_env": false, "ignores_encrypted": false }
  },
  "os": "macos"
}
```

**Status table**:
```
| Component | Status | Detail |
|-----------|--------|--------|
| sops | missing | — |
| age | missing | — |
| age key | missing | expected: ~/.config/sops/age/keys.txt |
| .sops.yaml | missing | — |
| .env files | 1 found | .env.local |
| encrypted | 0 found | — |
| .gitignore | needs update | .env* not ignored |
```

**Flow**:
1. Install tools → `brew install sops age`
2. Generate machine key → displays public key `age1abc...`, sets `chmod 600`
3. Generate backup key → displays full key output, user saves to 1Password
4. Create `.sops.yaml` → machine key + backup key as recipients
5. Set up `.gitattributes` → adds `sopsdiffer` for readable diffs
6. Update `.gitignore` → adds `.env*` rules
7. Encrypt → converts `.env.local` to YAML → encrypts → `.env.local.enc.yaml`
8. Summary with next steps

---

## Example 2: Tools Installed, Adding to New Project

**User**: `/devtools:sops-setup`

**Detection output**:
```json
{
  "tools": {
    "sops": { "installed": true, "version": "3.9.4" },
    "age": { "installed": true, "version": "1.2.0" }
  },
  "age_key": {
    "exists": true,
    "public_key": "age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p"
  },
  "project": {
    "sops_yaml": { "exists": false },
    "env_files": [".env.local", ".env.production"],
    "encrypted_files": [],
    "gitignore": { "exists": true, "ignores_env": true, "ignores_encrypted": false }
  },
  "os": "linux"
}
```

**Flow**:
1. Tools installed → skip (shows versions)
2. Age key exists → skip (shows truncated public key)
3. Backup key → user says "Skip" (already has one from previous project)
4. Create `.sops.yaml` → machine key only
5. Set up `.gitattributes` → adds sopsdiffer
6. `.gitignore` already ignores `.env*` → skip
7. Encrypt → user selects both → `.env.local.enc.yaml` and `.env.production.enc.yaml`
8. Summary — 4 actions (config, gitattributes, encrypt 2 files)

---

## Example 3: Second Machine Joining Existing Project

The project already has `.sops.yaml` and encrypted files. A new machine clones and runs setup.

**Detection output**:
```json
{
  "tools": {
    "sops": { "installed": true, "version": "3.9.4" },
    "age": { "installed": true, "version": "1.2.0" }
  },
  "age_key": {
    "exists": true,
    "public_key": "age1newmachine..."
  },
  "project": {
    "sops_yaml": {
      "exists": true,
      "authorized_keys": ["age1originalmachine..."],
      "key_count": 1
    },
    "env_files": [],
    "encrypted_files": [".env.local.enc.yaml"],
    "gitignore": { "exists": true, "ignores_env": true, "ignores_encrypted": false }
  },
  "os": "macos"
}
```

**Flow**:
1. Tools installed → skip
2. Age key exists → skip
3. `.sops.yaml` exists but **missing this machine's key** → offer to add
4. User confirms → key added to `.sops.yaml`
5. Attempt to decrypt → fails because files were encrypted before this key was added
6. Tell user: "On the original machine, run `/devtools:sops-add-key` with your public key (`age1newmachine...`), then pull the re-encrypted files and run `/devtools:sops-decrypt`"
