# Examples: Johnny.Decimal Documentation

## Example 1: Scaffolding a New Project

**Scenario:** Fresh project with no docs directory.

```bash
$ uv run scripts/jd_init.py --dry-run
Scaffolding J.D structure at: /projects/my-app/docs/ (dry-run)

  Would create: /projects/my-app/docs/
  Would create: /projects/my-app/docs/README.md
  Would create: /projects/my-app/docs/00-getting-started/
  Would create: /projects/my-app/docs/00-getting-started/README.md
  Would create: /projects/my-app/docs/10-product/
  Would create: /projects/my-app/docs/10-product/README.md
  Would create: /projects/my-app/docs/20-architecture/
  Would create: /projects/my-app/docs/20-architecture/README.md
  Would create: /projects/my-app/docs/30-research/
  Would create: /projects/my-app/docs/30-research/README.md
  Would create: /projects/my-app/docs/90-archive/
  Would create: /projects/my-app/docs/90-archive/README.md

Would create: 12 items
```

**Generated `docs/README.md`:**

```markdown
# My App Documentation

[Brief project description]

## Quick Start

- [Getting started guide](./00-getting-started/)

## Documentation Index

<!-- JD:INDEX:START -->

| Prefix | Area | Purpose |
|--------|------|---------|
| `00-` | [`00-getting-started/`](./00-getting-started/) | Onboarding, setup, quick start, MVP, and phase planning |
| `10-` | [`10-product/`](./10-product/) | Product specs, features, roadmap, design, and branding |
| `20-` | [`20-architecture/`](./20-architecture/) | Technical decisions, system design, and integration |
| `30-` | [`30-research/`](./30-research/) | Research notes, spikes, investigations, and reference material |
| `90-` | [`90-archive/`](./90-archive/) | Historical and deprecated documentation |

<!-- JD:INDEX:END -->

## Folder Convention

Documentation uses the [Johnny.Decimal](https://johnnydecimal.com/) numbering system.
...
```

---

## Example 2: Monorepo with Product Sub-Trees

**Scenario:** Monorepo with two products (like Papia Studio).

```bash
$ uv run scripts/jd_init.py --root docs/skrebe
$ uv run scripts/jd_init.py --root docs/papia-asr
```

**Result:**

```
docs/
├── README.md                  (manually created hub page)
├── glossary.md                (shared terminology)
├── adr/                       (shared ADRs)
├── skrebe/
│   ├── README.md
│   ├── 00-getting-started/
│   ├── 10-product/
│   ├── 20-architecture/
│   ├── 30-research/
│   └── 90-archive/
└── papia-asr/
    ├── README.md
    ├── 00-getting-started/
    ├── 10-product/
    ├── 20-architecture/
    ├── 30-research/
    └── 90-archive/
```

Each product gets its own J.D structure with independent area directories.

---

## Example 3: Custom Area Scheme

**Scenario:** DevOps-heavy project needs `40-operations` and `50-runbooks`.

```bash
$ uv run scripts/jd_init.py --init-config
```

Edit `.jd-config.json`:

```json
{
  "version": 1,
  "root": "docs",
  "areas": {
    "00": "getting-started",
    "10": "product",
    "20": "architecture",
    "30": "research",
    "40": "operations",
    "50": "runbooks",
    "90": "archive"
  },
  "products": [],
  "ignore": ["adr", "*.pdf"],
  "readme_format": "table"
}
```

Then scaffold:

```bash
$ uv run scripts/jd_init.py --dry-run
Scaffolding J.D structure at: /projects/infra/docs/ (dry-run)

  ...
  Would create: /projects/infra/docs/40-operations/
  Would create: /projects/infra/docs/40-operations/README.md
  Would create: /projects/infra/docs/50-runbooks/
  Would create: /projects/infra/docs/50-runbooks/README.md
  ...
```

---

## Example 4: Validating an Existing Project

**Scenario:** Running validation against an established docs directory.

```bash
$ uv run scripts/jd_validate.py --dir docs/skrebe
Johnny.Decimal Validation Report
========================================
Directory: /projects/papia-studio/docs/skrebe

Areas found: 5
  + 00-mvp
  + 10-product
  + 20-architecture
  + 30-research
  + 90-archive

Warnings: 3
  ! Orphan file: alupec-linting-deep-dive.md
  ! Orphan file: article.md
  ! Orphan file: test-report-alupec-linting.md

Info: 1
  - Standard area not present: 00-getting-started/

Result: PASS (5 areas, 0 errors, 3 warnings)
```

**With strict mode:**

```bash
$ uv run scripts/jd_validate.py --dir docs/skrebe --strict
...
Result: FAIL (strict mode) (5 areas, 0 errors, 3 warnings)
```

**Fixing the warnings:**
- Move orphan files to appropriate areas (e.g., `alupec-linting-deep-dive.md` → `30-research/`)
- The `00-mvp` vs `00-getting-started` mismatch is informational only (project uses `00-mvp` instead of the default name)

---

## Example 5: Generating a Documentation Index

**Table format (default):**

```bash
$ uv run scripts/jd_index.py --dir docs/skrebe --dry-run
Scanning: /projects/papia-studio/docs/skrebe
Format: table
Areas found: 5
Total documents: 19

Would update: /projects/papia-studio/docs/skrebe/README.md

--- Index content ---
| Prefix | Area | Docs | Description |
|--------|------|------|-------------|
| `00-` | [`00-mvp/`](./00-mvp/) | 10 docs | Onboarding, setup, quick start, MVP |
| `10-` | [`10-product/`](./10-product/) | 4 docs | Specs, features, roadmap, design |
| `20-` | [`20-architecture/`](./20-architecture/) | 7 docs | Tech decisions, system design |
| `30-` | [`30-research/`](./30-research/) | 7 docs | Research, spikes, investigations |
| `90-` | [`90-archive/`](./90-archive/) | 6 docs | Historical/deprecated docs |
--- End ---
```

**Tree format:**

```bash
$ uv run scripts/jd_index.py --dir docs/skrebe --format tree --dry-run
...
--- Index content ---
- **[`00-mvp/`](./00-mvp/)** — Onboarding, setup, quick start, MVP
  - [Dictionary Extraction Strategy](./00-mvp/dictionary-extraction-strategy.md)
  - [Execution Plan](./00-mvp/execution-plan.md)
  - [Requirements](./00-mvp/requirements.md)
  - [Roadmap](./00-mvp/roadmap.md)
  ...
- **[`10-product/`](./10-product/)** — Specs, features, roadmap, design
  - [Design System](./10-product/design-system.md)
  - [Editor Features](./10-product/editor-features.md)
  ...
--- End ---
```

---

## Example 6: Migrating Flat Docs

**Scenario:** Project has 8 markdown files in a flat `docs/` directory.

When you say "organize my docs into Johnny Decimal areas", Claude will:

1. **List all files:**
   ```
   docs/
   ├── README.md
   ├── api-design.md
   ├── deployment-guide.md
   ├── getting-started.md
   ├── performance-research.md
   ├── product-roadmap.md
   ├── system-architecture.md
   ├── team-conventions.md
   └── old-design-v1.md
   ```

2. **Propose classification:**

   | File | Target Area | Reason |
   |------|------------|--------|
   | getting-started.md | `00-getting-started/` | Filename keyword match |
   | product-roadmap.md | `10-product/` | "product" keyword |
   | api-design.md | `20-architecture/` | Design/architecture topic |
   | system-architecture.md | `20-architecture/` | "architecture" keyword |
   | team-conventions.md | `20-architecture/` | Conventions = architecture |
   | performance-research.md | `30-research/` | "research" keyword |
   | deployment-guide.md | `20-architecture/` | Ops guide (or custom `40-operations/`) |
   | old-design-v1.md | `90-archive/` | "v1" version suffix |
   | README.md | _(keep in place)_ | Root README |

3. **Ask for confirmation**, then move files and update the README index.

---

## Example 7: Adding a Custom Area

**Scenario:** DevOps-heavy project needs a `40-operations` area after initial scaffold.

```bash
$ uv run scripts/jd_add_area.py --prefix 40 --name operations \
    --description "Deployment, monitoring, and runbooks" --dry-run
Adding area 40-operations (dry-run)

  Would create: /projects/infra/docs/40-operations/
  Would create: /projects/infra/docs/40-operations/README.md

  Would update: /projects/infra/.jd-config.json
    + "40": "operations"

Re-indexing...
Would update: /projects/infra/docs/README.md

--- Index content ---
| Prefix | Area | Docs | Description |
|--------|------|------|-------------|
| `00-` | [`00-getting-started/`](./00-getting-started/) | 3 docs | Onboarding, setup, quick start, MVP |
| `10-` | [`10-product/`](./10-product/) | 2 docs | Specs, features, roadmap, design |
| `20-` | [`20-architecture/`](./20-architecture/) | 4 docs | Tech decisions, system design |
| `30-` | [`30-research/`](./30-research/) | 1 doc | Research, spikes, investigations |
| `40-` | [`40-operations/`](./40-operations/) | — |  |
| `90-` | [`90-archive/`](./90-archive/) | — | Historical/deprecated docs |
--- End ---

Would create: 2 items
```

**Error case — prefix already taken:**

```bash
$ uv run scripts/jd_add_area.py --prefix 20 --name operations
Error: Prefix '20' already in config as '20-architecture'
```

---

## Example 8: Classifying Unorganized Files

**Scenario:** Several markdown files sitting in the docs root need organizing.

```bash
$ uv run scripts/jd_classify.py docs/roadmap.md docs/api-design.md \
    docs/performance-research.md docs/old-plan-v1.md docs/random-notes.md
File                     | Suggested Area       | Confidence | Reason
-------------------------+----------------------+------------+-------------------------------
roadmap.md               | 00-getting-started   | high       | Filename: 'roadmap'
api-design.md            | 20-architecture      | high       | Filename: 'api'; Content: 'schema'
performance-research.md  | 30-research          | high       | Filename: 'research'
old-plan-v1.md           | 90-archive           | high       | Filename: 'old', 'v1'
random-notes.md          | (unknown)            | low        | No keyword matches

Summary: 4 high, 0 medium, 1 low confidence
  1 file(s) need Claude review (low confidence)
```

**Moving with preview:**

```bash
$ uv run scripts/jd_classify.py docs/*.md --move --dry-run
...
  Would move: roadmap.md -> 00-getting-started/roadmap.md
  Would move: api-design.md -> 20-architecture/api-design.md
  Would move: performance-research.md -> 30-research/performance-research.md
  Would move: old-plan-v1.md -> 90-archive/old-plan-v1.md
  Skip (low confidence): random-notes.md — flag for Claude review

Would move: 4 file(s)
```

**JSON output for scripting:**

```bash
$ uv run scripts/jd_classify.py docs/roadmap.md --json
[
  {
    "file": "docs/roadmap.md",
    "suggested_area": "00-getting-started",
    "suggested_prefix": "00",
    "confidence": "high",
    "score": 0.5,
    "reason": "Filename: 'roadmap'",
    "filename_matches": ["roadmap"],
    "content_matches": []
  }
]
```

---

## Example 9: Moving a File to an Area

**Scenario:** Moving a poorly named file to the correct area with auto-normalization.

```bash
$ uv run scripts/jd_add.py "docs/My Design Doc.md" 20 --dry-run
Moving file to 20-architecture/ (dry-run)

  Source:      /projects/my-app/docs/My Design Doc.md
  Destination: /projects/my-app/docs/20-architecture/my-design-doc.md
  Renamed:     My Design Doc.md -> my-design-doc.md

Cross-references found (1 occurrence(s)):
These files reference the old path and may need updating:

  00-getting-started/setup.md:15: See [design doc](../My Design Doc.md) for details

Suggested replacement: 'My Design Doc.md' -> '20-architecture/my-design-doc.md'

Would re-index after move.
```

**Moving by prefix:**

```bash
$ uv run scripts/jd_add.py docs/api-design.md 20
Moving file to 20-architecture/

  Source:      /projects/my-app/docs/api-design.md
  Destination: /projects/my-app/docs/20-architecture/api-design.md

  Moved successfully.

No cross-references found.

Re-indexing...
Updated: /projects/my-app/docs/README.md
```

**Override filename:**

```bash
$ uv run scripts/jd_add.py docs/notes.md 30 --name spike-caching-strategies.md
Moving file to 30-research/

  Source:      /projects/my-app/docs/notes.md
  Destination: /projects/my-app/docs/30-research/spike-caching-strategies.md
  Renamed:     notes.md -> spike-caching-strategies.md

  Moved successfully.
```

---

## Quick Reference

| Action | Script | Key Flags |
|--------|--------|-----------|
| Scaffold new structure | `jd_init.py` | `--root`, `--product`, `--init-config`, `--dry-run` |
| Validate existing structure | `jd_validate.py` | `--dir`, `--strict`, `--config` |
| Generate/update index | `jd_index.py` | `--dir`, `--format`, `--dry-run` |
| Migrate flat docs | _(Claude-driven)_ | Natural language request |
| Add new area | `jd_add_area.py` | `--prefix`, `--name`, `--description`, `--dry-run` |
| Classify files | `jd_classify.py` | `--move`, `--yes`, `--no-content`, `--json`, `--dry-run` |
| Move file to area | `jd_add.py` | `--name`, `--dry-run` |
