# Troubleshooting: Johnny.Decimal Documentation

## 1. No Docs Directory Found

**Symptom:** `jd_init.py` doesn't know where to create the structure.

**Solutions:**
- Use `--root` to specify explicitly: `uv run scripts/jd_init.py --root docs`
- Ensure you're running from the project root (where `.git/` lives)
- Create the directory manually first: `mkdir docs`

## 2. Config File Not Found

**Symptom:** Scripts use defaults instead of custom config.

**Solutions:**
- Create config: `uv run scripts/jd_init.py --init-config`
- Place `.jd-config.json` at project root (same level as `.git/`)
- Specify path explicitly: `--config path/to/.jd-config.json`

## 3. Invalid Area Name

**Symptom:** Validation reports "does not match NN-kebab-case pattern".

**Expected pattern:** `^[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$`

**Common causes:**
- Uppercase letters: `20-Architecture` → rename to `20-architecture`
- Underscores: `20-tech_stack` → rename to `20-tech-stack`
- Spaces: `20 - architecture` → rename to `20-architecture`
- Missing prefix: `architecture` → rename to `20-architecture`

## 4. Orphan Files Detected

**Symptom:** Validation warns about `.md` files in docs root.

**Solutions:**
- Move files to the appropriate area directory
- If the file belongs at root (like `glossary.md`), it's expected — the script only flags non-standard root files
- Add to ignore patterns in `.jd-config.json`: `"ignore": ["adr", "*.pdf", "glossary.md"]`

## 5. Area Numbering Mismatch

**Symptom:** Validation reports "Standard area not present: 00-getting-started/" but project uses `00-mvp`.

**Explanation:** This is informational, not an error. The project uses a custom name for the `00-` area.

**Solutions:**
- Ignore the info message (it's not a warning or error)
- Update `.jd-config.json` to match your naming: `"00": "mvp"`

## 6. Index Appended to End of README

**Symptom:** `jd_index.py` appends the index at the bottom of README.md instead of where you want it.

**Explanation:** On first run without markers, the script appends the index with markers at the end. This is by design — the script prints a tip to reposition them.

**Solutions:**
- After the first run, move the marker block to the desired position in your README:
  ```markdown
  ## Documentation Index

  <!-- JD:INDEX:START -->
  (generated content)
  <!-- JD:INDEX:END -->
  ```
- On subsequent runs, `jd_index.py` will update content between the markers
- Content outside markers is always preserved

## 7. Permission Errors

**Symptom:** "Permission denied" when creating directories or files.

**Solutions:**
- Check directory permissions: `ls -la docs/`
- Ensure the current user owns the docs directory
- On macOS, check for extended attributes: `xattr -l docs/`

## 8. uv Not Found

**Symptom:** `command not found: uv` when running scripts.

**Solutions:**
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or run with Python directly: `python3 scripts/jd_init.py --help`
- Check PATH includes uv: `which uv`

## 9. Products Config Not Working

**Symptom:** Product sub-trees not created automatically from `products` in config.

**Explanation:** The `products` config field records which products exist for reference, but `jd_init.py` scaffolds one tree per invocation. Run it once per product.

**Solutions:**
- Use `--product` for each product:
  ```bash
  uv run scripts/jd_init.py --product skrebe
  uv run scripts/jd_init.py --product papia-asr
  ```
  This creates `docs/skrebe/` and `docs/papia-asr/` with J.D areas in each.
- Or use `--root` directly:
  ```bash
  uv run scripts/jd_init.py --root docs/skrebe
  uv run scripts/jd_init.py --root docs/papia-asr
  ```

## 10. Index Shows Wrong Document Count

**Symptom:** `jd_index.py` reports fewer documents than expected.

**Common causes:**
- Files with non-`.md` extensions are not counted (only Markdown)
- `README.md` files inside areas are excluded from count (they're structure, not content)
- Files matching ignore patterns are skipped
- Check ignore list: `"ignore": ["adr", "*.pdf"]` in config

## Debugging Tips

**Verify structure:**
```bash
# List all J.D area directories
ls -d docs/[0-9][0-9]-*/

# Count docs per area
for d in docs/[0-9][0-9]-*/; do
  echo "$d: $(ls $d/*.md 2>/dev/null | wc -l) docs"
done
```

**Test naming regex:**
```bash
# Valid names
echo "00-getting-started" | grep -E '^[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$'
echo "20-architecture" | grep -E '^[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$'

# Invalid names (should not match)
echo "20-Architecture" | grep -E '^[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$'
```

**Preview before changing:**
Always use `--dry-run` before any write operation:
```bash
uv run scripts/jd_init.py --dry-run
uv run scripts/jd_index.py --dir docs --dry-run
```
