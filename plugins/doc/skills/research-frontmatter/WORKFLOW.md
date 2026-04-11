# Research Frontmatter Workflow

## Phase 1: Path Resolution

Before validating or creating research documents, resolve the research directory:

1. **Auto-detect**: Run `resolve_research_path.py` to find the active path
2. **JD structure**: If `.jd-config.json` exists, the script reads `areas` to find the research prefix
3. **Fallback**: Without JD config, defaults to `docs/research/`

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/resolve_research_path.py --format json
```

### Path Resolution Algorithm

```
project_root/
├── .jd-config.json          ← Step 1: Check for this file
│   areas: {"30": "research"} ← Step 2: Find research area
│   root: "docs"              ← Step 3: Read docs root
└── docs/
    └── 30-research/          ← Step 4: Construct path
```

If no `.jd-config.json`:
```
project_root/
└── docs/
    └── research/             ← Fallback path
```

## Phase 2: Validation

### Full Validation

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py --format text
```

Runs all 16 checks (RD001-RD016):
- Frontmatter presence and field validation
- Section structure (Executive Summary, References)
- README index accuracy
- Staleness detection

### Staleness-Only

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py --staleness-only
```

Only runs RD016: compares `last_updated` in frontmatter against git modification date.

### Filtering by Severity

```bash
# Only errors (skip warnings and suggestions)
uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py --min-severity error

# Include suggestions
uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py --min-severity suggestion
```

## Phase 3: Creating New Research Documents

1. Copy the `TEMPLATE.md` from the research directory
2. Fill in the 5 required frontmatter fields:
   - `title`: Human-readable title
   - `version`: Start at `1.0.0`
   - `status`: `Draft` for initial creation
   - `created`: Today's date (YYYY-MM-DD)
   - `last_updated`: Same as created initially
3. Write the Executive Summary section
4. Add a References section (even if empty initially)
5. Add an entry to the README.md index table

## Phase 4: Integration with deep-research

When the deep-research skill promotes cached research to project docs:

1. The `promote.py` script resolves the output path using JD-aware detection
2. Promoted files include full YAML frontmatter (5 required + extended fields)
3. The README index is auto-updated by `index_generator.py`
4. After promotion, run validation to confirm compliance:
   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py --format text
   ```

## Phase 5: README Index Maintenance

The README.md index table must stay synchronized with research files:

| Column | Source |
|--------|--------|
| Topic | Frontmatter `title` (linked to file) |
| Version | Frontmatter `version` |
| Status | Frontmatter `status` |
| Created | Frontmatter `created` |
| Last Updated | Frontmatter `last_updated` |

RD013 flags files missing from the index. RD014 flags mismatches between index and frontmatter. RD015 flags index entries pointing to deleted files.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | CRITICAL or ERROR issues found |
| 2 | Only WARNING or SUGGESTION issues found |
