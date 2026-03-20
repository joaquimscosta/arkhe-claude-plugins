# SOPS Setup Troubleshooting

## Installation Issues

### `brew install` fails (macOS)

**Symptom**: `brew install sops age` fails or command not found.

**Fix**:
```bash
# Update Homebrew
brew update

# If brew itself isn't installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### `age` not in apt repositories (Linux)

**Symptom**: `apt-get install age` fails on older Ubuntu/Debian.

**Fix**: Install from binary:
```bash
AGE_VERSION=$(curl -s https://api.github.com/repos/FiloSottile/age/releases/latest | grep tag_name | cut -d '"' -f 4)
curl -Lo /tmp/age.tar.gz "https://github.com/FiloSottile/age/releases/download/${AGE_VERSION}/age-${AGE_VERSION}-linux-amd64.tar.gz"
tar -xzf /tmp/age.tar.gz -C /tmp
sudo install -m 755 /tmp/age/age /usr/local/bin/age
sudo install -m 755 /tmp/age/age-keygen /usr/local/bin/age-keygen
rm -rf /tmp/age /tmp/age.tar.gz
```

---

## Key Issues

### "no identity matched any of the recipients"

**Symptom**: `sops --decrypt` fails with this error.

**Cause**: The machine's age key is not listed in `.sops.yaml` when the file was encrypted.

**Fix**:
1. On a machine that CAN decrypt, run `/devtools:sops-add-key`
2. Paste the new machine's public key
3. This re-encrypts files for all authorized keys (using `sops updatekeys`)
4. Commit and push the updated `.sops.yaml` and `*.enc.yaml` files
5. Pull on the new machine and try decrypting again

### Age key file has wrong permissions

**Symptom**: Warnings about key file permissions.

**Fix**:
```bash
chmod 600 ~/.config/sops/age/keys.txt
```

### Lost age private key

**Symptom**: Cannot decrypt files, private key file is gone.

**Fix options**:
1. **If you have a backup key**: Place the backup private key at `~/.config/sops/age/keys.txt` and decrypt
2. **If another machine has access**: On that machine, run `/devtools:sops-add-key` with your new machine's public key
3. **If no backup and no other machine**: Secrets are lost. Generate a new key, recreate `.env` files manually, re-encrypt from scratch

This is why the setup wizard recommends generating a backup key.

---

## Encryption Issues

### "could not load config" when running sops

**Symptom**: `sops --encrypt` fails saying it can't find configuration.

**Cause**: `.sops.yaml` is missing or not in the current directory / parent.

**Fix**: Ensure `.sops.yaml` is in the project root and you're running sops from within the project directory tree.

### Encrypted file is empty

**Symptom**: `.enc.yaml` file was created but has 0 bytes.

**Cause**: Shell redirect (`>`) created the file before sops ran, and sops failed.

**Fix**:
1. Check for sops errors: `sops --encrypt file.yaml` (without redirect, shows output/errors)
2. Common causes: missing `.sops.yaml`, invalid age key, file permissions
3. After fixing, re-encrypt

### dotenv_yaml.py conversion errors

**Symptom**: Helper script fails to convert `.env` file.

**Common causes**:
- File uses non-standard dotenv syntax
- Binary content in env file
- Encoding issues (non-UTF8)

**Fix**: Check the `.env` file is valid UTF-8 with standard `KEY=value` format. Run the round-trip test:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/dotenv_yaml.py test .env.local
```

### Why not use dotenv format directly?

SOPS has a [known bug (#1435)](https://github.com/getsops/sops/issues/1435) where the dotenv store corrupts backslash sequences (`\\`, `\n`) on decrypt. The YAML format is roundtrip-safe. The `dotenv_yaml.py` helper handles conversion transparently.

---

## Git Issues

### Accidentally committed plaintext `.env` file

**Fix**:
1. Remove from git (keep local): `git rm --cached .env.local`
2. Ensure `.gitignore` has `.env*` rules
3. Commit: `git commit -m "remove plaintext env from tracking"`
4. **Important**: The secret is still in git history. Rotate any exposed credentials.
5. Optionally clean history: `git filter-branch` or BFG Repo-Cleaner

### `.enc.yaml` files showing as ignored by git

**Cause**: `.gitignore` has a pattern matching `*.yaml` or `*.enc.yaml`.

**Fix**: Remove the pattern from `.gitignore`. Encrypted YAML files are safe to commit — that's the whole point.

### Git diff shows binary/garbled content for `.enc.yaml`

**Cause**: `.gitattributes` sopsdiffer not configured.

**Fix**:
```bash
# Add to .gitattributes
echo '*.enc.yaml diff=sopsdiffer' >> .gitattributes

# Configure git
git config diff.sopsdiffer.textconv "sops decrypt"
```

Now `git diff` will show decrypted content for encrypted files.

---

## `sops updatekeys` Issues

### Command not found or unsupported

**Symptom**: `sops updatekeys` not recognized.

**Cause**: Older version of sops (pre-3.8).

**Fix**: Update sops or fall back to manual re-encryption:
```bash
sops --decrypt file.enc.yaml > file.tmp.yaml
sops --encrypt file.tmp.yaml > file.enc.yaml
rm file.tmp.yaml
```

### Key removed but old data still accessible

After removing a key from `.sops.yaml` and running `updatekeys`, the removed party could still decrypt if they cached the old data encryption key (DEK).

**Fix**: Run full key rotation to generate a new DEK:
```bash
sops rotate -i file.enc.yaml
```
This re-encrypts every value with a fresh DEK, invalidating any cached keys.
