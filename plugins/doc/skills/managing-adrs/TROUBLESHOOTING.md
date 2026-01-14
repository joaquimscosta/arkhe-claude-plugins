# ADR Troubleshooting

This document covers common issues and their solutions when working with ADRs.

## Issue 1: No ADR Directory Found

**Error:**
```
Error: No ADR directory found.
Searched: docs/adr, doc/adr, architecture/decisions, .adr
```

**Cause:** The script couldn't find an existing ADR directory in any of the standard locations.

**Solutions:**

1. **Create the directory:**
   ```bash
   uv run adr_create.py --title "Your Title" --create-dir
   ```

2. **Specify custom path:**
   ```bash
   uv run adr_create.py --title "Your Title" --dir my/custom/path
   ```

3. **Create manually:**
   ```bash
   mkdir -p docs/adr
   ```

---

## Issue 2: Template Detection Failed

**Symptom:** New ADR doesn't match existing style.

**Cause:** Existing ADRs have non-standard format that wasn't detected.

**Solutions:**

1. **Use explicit template:**
   ```bash
   uv run adr_create.py --title "Title" --template madr
   ```

2. **Edit after creation:** Create with default, then manually adjust to match project style.

3. **Create project template:** Add a `template.md` file to your ADR directory that Claude can reference.

---

## Issue 3: Numbering Conflicts

**Symptom:** Two ADRs have the same number.

**Cause:** Manual creation bypassed auto-numbering, or concurrent creation.

**Solutions:**

1. **Renumber manually:** Rename the file with a new number:
   ```bash
   mv 0005-duplicate.md 0006-duplicate.md
   ```

2. **Update references:** Search for links to the old number:
   ```bash
   grep -r "ADR-0005" docs/adr/
   ```

3. **Regenerate index:**
   ```bash
   uv run adr_index.py --dir docs/adr
   ```

---

## Issue 4: README.md Parse Errors

**Symptom:** Index table is malformed or missing entries.

**Solutions:**

1. **Regenerate completely:**
   ```bash
   uv run adr_index.py --dir docs/adr
   ```
   This overwrites the entire README.md.

2. **Check ADR format:** Ensure each ADR has:
   - `# ` heading with title
   - `## Status` section with value on next line
   - `## Date` section with YYYY-MM-DD format

3. **Verify dry run first:**
   ```bash
   uv run adr_index.py --dir docs/adr --dry-run
   ```

---

## Issue 5: Supersession Not Working

**Error:**
```
Error: Could not update status in 0005-old-decision.md
The file may have a non-standard format.
```

**Cause:** The ADR doesn't have a standard `## Status` section.

**Solutions:**

1. **Check Status format:** Ensure the ADR has:
   ```markdown
   ## Status
   Accepted
   ```
   (Status value must be on the line immediately after the heading)

2. **Manual update:** Edit the old ADR directly:
   ```markdown
   ## Status
   Superseded by [ADR-0012](0012-new-decision.md)
   ```

3. **Add Status section:** If missing, add it after the title.

---

## Issue 6: Permission Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'docs/adr/0005-new.md'
```

**Cause:** File system permissions prevent writing.

**Solutions:**

1. **Check directory permissions:**
   ```bash
   ls -la docs/adr/
   ```

2. **Fix ownership:**
   ```bash
   sudo chown -R $USER docs/adr/
   ```

3. **Check if file is locked:** Close any editors that have the file open.

---

## Issue 7: uv Not Found

**Error:**
```
bash: uv: command not found
```

**Cause:** uv is not installed or not in PATH.

**Solutions:**

1. **Install uv:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Add to PATH:**
   ```bash
   export PATH="$HOME/.cargo/bin:$PATH"
   ```

3. **Use Python directly:**
   ```bash
   python3 scripts/adr_create.py --title "Title"
   ```

---

## Issue 8: Date Format Issues

**Symptom:** Date not appearing in index table.

**Cause:** Date section uses wrong format.

**Required format:**
```markdown
## Date
2026-01-10
```

**Common mistakes:**
- `January 10, 2026` (wrong format)
- `10-01-2026` (wrong order)
- `2026/01/10` (wrong separator)

**Solution:** Use ISO 8601 format: `YYYY-MM-DD`

---

## Issue 9: Status Not Recognized

**Symptom:** Status shows as "Unknown" in index.

**Cause:** Status value not on the line immediately after heading.

**Wrong:**
```markdown
## Status

Accepted
```
(Empty line between heading and value)

**Correct:**
```markdown
## Status
Accepted
```

---

## Issue 10: Title Extraction Failed

**Symptom:** Title shows as filename in index.

**Cause:** ADR missing proper heading or using wrong format.

**Required format:**
```markdown
# ADR-0005: Use PostgreSQL for Persistence
```
or
```markdown
# Use PostgreSQL for Persistence
```

**Common mistakes:**
- Missing `#` (plain text title)
- Using `##` instead of `#`
- Extra formatting in title (bold, links)

---

## Debugging Tips

### Verify ADR Structure

Check if an ADR has the required sections:

```bash
grep -E "^## (Status|Date|Context)" docs/adr/0005-*.md
```

### Test Regex Patterns

The scripts use these patterns:

```python
# Filename number extraction
r'^(?:ADR-)?(\d+)-.*\.md$'

# Status extraction
r'^##\s+Status\s*\n+([^\n#]+)'

# Date extraction
r'^##\s+Date\s*\n+(\d{4}-\d{2}-\d{2})'

# Title extraction
r'^#\s+(?:ADR-\d+:\s*)?(.+)$'
```

### Dry Run Everything

Before making changes, preview with `--dry-run`:

```bash
uv run adr_index.py --dir docs/adr --dry-run
```

### Check Script Output

Scripts provide helpful output:

```bash
uv run adr_create.py --title "Test" --dir docs/adr
# Created: docs/adr/0006-test.md
# Number: ADR-0006
# Next: Run adr_index.py to update README.md
```

---

## Getting Help

If issues persist:

1. **Check file encoding:** Ensure UTF-8 encoding
2. **Look for hidden characters:** Use `cat -A filename.md`
3. **Validate markdown:** Use a markdown linter
4. **Review examples:** See [EXAMPLES.md](EXAMPLES.md)

---

## Related Resources

- [SKILL.md](SKILL.md) - Quick reference
- [WORKFLOW.md](WORKFLOW.md) - Detailed methodology
- [EXAMPLES.md](EXAMPLES.md) - Real-world examples
