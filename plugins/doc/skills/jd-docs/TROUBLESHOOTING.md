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

## 11. Area Prefix Already Taken

**Symptom:** `jd_add_area.py` reports "Prefix 'XX' already in config" or "already exists on disk".

**Solutions:**
- Check existing areas: `ls -d docs/[0-9][0-9]-*/`
- Choose a different prefix (multiples of 10: 40, 50, 60, 70, 80)
- If the area exists on disk but not in config, add it manually to `.jd-config.json`

## 12. Invalid Prefix (Not Multiple of 10)

**Symptom:** `jd_add_area.py` reports "Prefix 'XX' is not a multiple of 10".

**Explanation:** J.D convention uses multiples of 10 for top-level areas (00, 10, 20, ..., 90).

**Solutions:**
- Use a valid prefix: `--prefix 40`, `--prefix 50`, etc.
- If you intentionally need a non-standard prefix (e.g., `41` for a sub-category), create the directory manually

## 13. Classification Shows All Low Confidence

**Symptom:** `jd_classify.py` reports all files as low confidence.

**Common causes:**
- Filenames are generic (e.g., `notes.md`, `draft.md`, `todo.md`)
- Content doesn't contain classification keywords
- Custom areas not in the keyword table

**Solutions:**
- Use `--no-content` to see filename-only results, then add content
- Use Claude-driven classification for ambiguous files (ask Claude to suggest areas)
- Move files manually with `jd_add.py` and specify the target area

## 14. File Already Exists in Target Area

**Symptom:** `jd_add.py` reports "File already exists" at destination.

**Solutions:**
- Use `--name` to specify a different filename: `--name alternative-name.md`
- Check if the existing file is the same document (duplicate)
- Remove or archive the existing file first

## 15. Cross-References Not Auto-Updated

**Symptom:** After moving a file with `jd_add.py`, other docs still link to the old path.

**Explanation:** Cross-reference updates are intentionally NOT automated — the script prints suggestions but does not modify other files, to avoid accidental breakage.

**Solutions:**
- Review the suggested replacements printed by `jd_add.py`
- Use find-and-replace to update links in the affected files
- Run `jd_validate.py` to catch any remaining orphan references

## 16. Filename Normalization Unexpected

**Symptom:** The auto-normalized filename is not what you expected.

**Examples:**
- `Tech_Stack_v2.md` → `tech-stack-v2.md` (underscores become hyphens)
- `SETUP Guide!.md` → `setup-guide.md` (special chars stripped)
- `.gitkeep` → `.gitkeep` (hidden files unchanged)

**Solutions:**
- Preview first with `--dry-run` to see the normalized name
- Use `--name` to override: `jd_add.py file.md 20 --name my-preferred-name.md`

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

---

## Diataxis Integration Issues

### Quadrant column shows "-" for all files

**Symptom:** `--diataxis` flag shows `-` in the Quadrant and Q. Conf columns.

**Cause:** The diataxis skill scripts are not found at the expected path.

**Fix:** Ensure the diataxis skill is installed alongside jd-docs:
```bash
ls plugins/doc/skills/diataxis/scripts/diataxis_classify.py
```

If missing, install the diataxis skill or the quadrant column will remain empty (JD classification still works).

### --diataxis-move fails with "area not found"

**Symptom:** Files not routed to Diataxis areas, warning printed.

**Cause:** The 41-44 Diataxis area directories don't exist in the docs structure.

**Fix:** Scaffold with `--diataxis` first:
```bash
uv run scripts/jd_init.py --diataxis
```
