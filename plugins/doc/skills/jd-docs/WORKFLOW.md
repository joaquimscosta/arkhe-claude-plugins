# Workflow: Johnny.Decimal Documentation

Six-phase methodology for creating and maintaining J.D documentation structures.

## Phase 1: Discovery and Context Analysis

Determine the project's current state before taking action.

1. **Detect project root** — Look for `.git/` or `.jd-config.json`
2. **Search for existing docs** — Check `docs/`, `doc/`, `documentation/`, project root
3. **Load configuration** — Read `.jd-config.json` if present, otherwise use defaults
4. **Classify current state**:
   - **Empty**: No docs directory exists
   - **Flat**: Docs directory with unorganized files
   - **Partial J.D**: Some numbered areas but incomplete
   - **Full J.D**: Complete structure following conventions

## Phase 2: Configuration Resolution

Resolve the area scheme and settings for this project.

1. **Check for `.jd-config.json`** in project root
2. **Merge with defaults** — Missing fields get default values
3. **Resolve product sub-trees** — Monorepo vs single-product
4. **Determine docs root** — From config `root` field or default `docs/`

### Config Format

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

**Fields:**
- `version` — Config format version (always `1`)
- `root` — Docs root relative to project root
- `areas` — Map of two-digit prefix to kebab-case area name
- `products` — Product sub-tree names (each gets its own J.D structure)
- `ignore` — Directories and glob patterns to skip
- `readme_format` — `"table"` or `"tree"` for index generation

## Phase 3: Scaffolding (New Projects)

For **Empty** or **New sub-tree** states:

1. Run `jd_init.py` to create the structure:
   ```bash
   uv run scripts/jd_init.py --dry-run   # Preview first
   uv run scripts/jd_init.py              # Create structure
   ```

2. What gets created:
   - Root `docs/` directory
   - Area directories: `00-getting-started/`, `10-product/`, etc.
   - Root `README.md` with area index table and folder convention explanation
   - Per-area `README.md` stubs with purpose descriptions

3. For monorepos with product sub-trees:
   ```bash
   uv run scripts/jd_init.py --root docs/product-a
   uv run scripts/jd_init.py --root docs/product-b
   ```

4. Optionally create `.jd-config.json`:
   ```bash
   uv run scripts/jd_init.py --init-config
   ```

## Phase 4: Validation

For **Partial J.D** or **Full J.D** states:

1. Run `jd_validate.py`:
   ```bash
   uv run scripts/jd_validate.py --dir docs
   ```

2. Checks performed:
   - **ERROR**: Directory name doesn't match `NN-kebab-case` pattern
   - **WARNING**: Orphan `.md` files in docs root
   - **WARNING**: Area missing `README.md`
   - **INFO**: Standard area not present (compared to config/defaults)

3. For strict CI enforcement:
   ```bash
   uv run scripts/jd_validate.py --dir docs --strict
   ```

## Phase 5: Index Generation

For any state with existing areas:

1. Run `jd_index.py`:
   ```bash
   uv run scripts/jd_index.py --dir docs --dry-run    # Preview
   uv run scripts/jd_index.py --dir docs               # Update README
   ```

2. Index formats:
   - **Table** (default): Area, doc count, description
   - **Tree**: Hierarchical with individual document links

3. Marker comments for README preservation:
   ```markdown
   <!-- JD:INDEX:START -->
   (generated content)
   <!-- JD:INDEX:END -->
   ```
   Content outside markers is preserved on re-generation.

## Phase 6: Migration (Claude-Driven)

For **Flat** state — existing docs that need reorganization.

This phase is handled interactively by Claude, not by a script.

### Step 1: Analyze Existing Files

List all files in the docs directory and classify them:

```
File                        → Suggested Area
requirements.md             → 00-getting-started/
roadmap.md                  → 00-getting-started/
design-system.md            → 10-product/
branding.md                 → 10-product/
tech-stack.md               → 20-architecture/
integration-strategy.md     → 20-architecture/
kriolu-resources.md         → 30-research/
alternative-strategies.md   → 30-research/
old-plan-v0.md              → 90-archive/
```

### Classification Heuristics

| Area | Filename Keywords |
|------|-------------------|
| `00` | mvp, requirements, roadmap, phase, setup, getting-started, execution-plan, next-steps, checklist |
| `10` | product, branding, features, priority, design-system, editor, spec, ux |
| `20` | architecture, tech-stack, integration, structure, refactor, strategy, stack, system-design |
| `30` | research, resources, analysis, investigation, alternatives, sources, audit, spike |
| `90` | archive, old, deprecated, historical, retrospective, v0, v1, legacy |

### Step 2: Present Migration Plan

Show the user a table of proposed moves and ask for confirmation.

### Step 3: Execute

Move files using standard file operations. For each file:
1. Create target area directory if it doesn't exist
2. Move the file
3. Check for internal cross-references (relative links to moved files) and update if found — some links may need manual review

### Step 4: Regenerate Index

Run `jd_index.py` to update the README with the new structure.

## Ongoing Maintenance

After initial setup:

- **Adding new docs**: Place in the appropriate `NN-area/` directory
- **Re-indexing**: Run `jd_index.py --dir docs` after adding/removing docs
- **Validation**: Run `jd_validate.py --dir docs` periodically or in CI
- **New areas**: Add to `.jd-config.json` areas map, create directory manually or re-run `jd_init.py`
