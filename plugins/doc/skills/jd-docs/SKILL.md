---
name: jd-docs
description: Scaffold, validate, and maintain Johnny.Decimal documentation structure
  for software projects. Use when user mentions "Johnny Decimal", "J.D docs",
  "docs structure", "organize docs", "documentation layout", "scaffold docs",
  "docs migration", "generate index", "docs index", editing files in numbered
  directories (00-*, 10-*, 20-*), or discussing documentation organization.
---

# Johnny.Decimal Documentation

Scaffold, validate, and maintain [Johnny.Decimal](https://johnnydecimal.com/) documentation structure with sensible defaults and per-project customization.

## Auto-Invoke Triggers

This skill activates when:
1. **Keywords**: "Johnny Decimal", "J.D docs", "docs structure", "organize documentation"
2. **Editing numbered docs**: Files in `NN-name/` directories (00-*, 10-*, 20-*, etc.)
3. **Discussing doc organization**: Folder layout, area schemes, doc migration

## Capabilities

### 1. Scaffolding (jd_init.py)
- Create J.D directory tree with README templates
- Default: `00-getting-started`, `10-product`, `20-architecture`, `30-research`, `90-archive`
- Per-project customization via `.jd-config.json`
- Product sub-trees for monorepos (e.g., `docs/skrebe/`, `docs/papia-asr/`)

### 2. Validation (jd_validate.py)
- Check directory names match `NN-kebab-case` convention
- Detect orphan files outside area directories
- Verify README.md presence in each area
- Report compliance score with pass/fail result

### 3. Index Generation (jd_index.py)
- Generate/update root README.md with documentation index
- Table or tree format output
- Preserves custom README content via marker comments

### 4. Migration (Claude-driven)
- Analyze existing flat docs/ directory
- Classify files into J.D areas using naming heuristics
- Suggest and execute reorganization interactively
- See [WORKFLOW.md](WORKFLOW.md) Phase 6 for details

## Default Area Scheme

| Prefix | Name | Purpose |
|--------|------|---------|
| `00-` | getting-started | Onboarding, setup, quick start, MVP |
| `10-` | product | Specs, features, roadmap, design, branding |
| `20-` | architecture | Tech decisions, system design, integration |
| `30-` | research | Spikes, investigations, reference material |
| `90-` | archive | Historical/deprecated docs |

Gap at 40-80 left for per-project customization (e.g., `40-operations`).

## Config File (.jd-config.json)

Optional per-project override at project root:

```json
{
  "version": 1,
  "root": "docs",
  "areas": {
    "00": "getting-started",
    "10": "product",
    "20": "architecture",
    "30": "research",
    "90": "archive"
  },
  "products": [],
  "ignore": ["adr", "*.pdf"],
  "readme_format": "table"
}
```

Created with `jd_init.py --init-config`. All fields have sensible defaults.

## Scripts

Located in `scripts/` directory, using uv for execution:

### jd_init.py
```bash
uv run scripts/jd_init.py                          # Create docs/ with defaults
uv run scripts/jd_init.py --root docs/skrebe       # Product sub-tree
uv run scripts/jd_init.py --product skrebe         # Same, using --product flag
uv run scripts/jd_init.py --init-config            # Also create .jd-config.json
uv run scripts/jd_init.py --dry-run                # Preview only
```

### jd_validate.py
```bash
uv run scripts/jd_validate.py --dir docs
uv run scripts/jd_validate.py --dir docs/skrebe --strict
```

### jd_index.py
```bash
uv run scripts/jd_index.py --dir docs
uv run scripts/jd_index.py --dir docs --format tree --dry-run
```

## Quick Start

```bash
# Auto-invoke by saying:
"Scaffold a Johnny Decimal docs structure for this project"
"Validate if my docs follow Johnny Decimal conventions"
"Generate a docs index for my README"
"Help me organize my flat docs into numbered areas"
```

## Progressive Disclosure

- **Level 2**: [WORKFLOW.md](WORKFLOW.md) — Step-by-step methodology
- **Level 3**: [EXAMPLES.md](EXAMPLES.md) — Real-world examples
- **Level 4**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Error handling

## Related Resources

- Johnny.Decimal: https://johnnydecimal.com/
- Papia Studio example: Real-world J.D implementation
