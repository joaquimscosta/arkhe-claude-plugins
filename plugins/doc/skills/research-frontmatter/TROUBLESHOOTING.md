# Research Frontmatter Troubleshooting

## No research directory found

**Error**: `No research directory found at docs/research`

**Cause**: The resolved path doesn't exist yet.

**Fix**:
1. Check resolved path: `uv run ${CLAUDE_SKILL_DIR}/scripts/resolve_research_path.py`
2. Create the directory: `mkdir -p docs/research`
3. If using JD structure, scaffold with jd-docs first: `jd_init.py`

## JD config not detected

**Symptom**: Path resolves to `docs/research/` even though you have JD structure.

**Cause**: `.jd-config.json` is missing or doesn't have a research area.

**Fix**:
1. Verify file exists: `ls .jd-config.json`
2. Check areas include research: `cat .jd-config.json | python3 -m json.tool`
3. Ensure at least one area name contains "research" (case-insensitive)

## Custom JD area not matched

**Symptom**: JD config exists but research path falls back to `docs/research/`.

**Cause**: No area name contains the substring "research".

**Fix**: Rename the area to include "research", e.g.:
```json
{
  "areas": {
    "30": "spikes-and-research"
  }
}
```

## PyYAML not installed

**Symptom**: Script works but may fail on complex frontmatter (nested YAML, multi-line strings).

**Cause**: PyYAML is optional; the fallback parser handles simple key-value pairs only.

**Fix**:
```bash
pip install pyyaml
# or in CI:
pip install pyyaml
```

The scripts work without PyYAML for standard research frontmatter (simple key-value fields).

## Import errors

**Error**: `ModuleNotFoundError: No module named 'shared'`

**Cause**: Script not run from correct directory, or `sys.path` issue.

**Fix**: Run via `uv run` with full path:
```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py
```

Or with explicit Python:
```bash
python3 plugins/doc/skills/research-frontmatter/scripts/validate_research_docs.py
```

## RD016 false positives

**Symptom**: Staleness warnings for files where only whitespace or formatting changed.

**Cause**: Git modification date reflects any commit touching the file, including non-substantive changes.

**Fix**: Update `last_updated` to match the git date, or use `--min-severity error` to skip warnings:
```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py --min-severity error
```

## README index not found

**Symptom**: RD013 errors for all files.

**Cause**: No `README.md` in the research directory.

**Fix**: Create a README.md with the index table:
```markdown
# Research

| Topic | Version | Status | Created | Last Updated |
|-------|---------|--------|---------|--------------|
| [Doc Title](filename.md) | 1.0.0 | Published | 2026-01-01 | 2026-01-01 |
```
