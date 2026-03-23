# Diataxis Examples

Real-world usage examples for all Diataxis skill operations.

---

## Example 1: Classify a Project's Documentation

**Scenario:** You have a project with 8 markdown files in `docs/` and want to understand their Diataxis breakdown.

```bash
$ uv run scripts/diataxis_classify.py docs/*.md --verbose

File                  | Quadrant    | Confidence | Collapsed | Reason
----------------------+-------------+------------+-----------+----------------------------
getting-started.md    | tutorial    | high       | No        | Title: 'getting-started'; Structure: numbered_steps(12)
deploy-guide.md       | how-to      | high       | No        | Title: 'deploy'; Content: 'run the following'
api-reference.md      | reference   | high       | No        | Title: 'reference'; Structure: tables(15), parameter_tables(3)
architecture.md       | explanation | medium     | Yes (E+R) | Title: 'architecture'; Structure: long_paragraphs(4)
config-options.md     | reference   | high       | No        | Title: 'config'; Structure: parameter_tables(2)
setup-guide.md        | how-to      | medium     | No        | Title: 'setup', 'guide'; Content: 'configure the'
design-decisions.md   | explanation | high       | No        | Title: 'design'; Content: 'the reason', 'the tradeoff'
README.md             | tutorial    | low        | No        | Structure: numbered_steps(3)
                        Scores: explanation: 0.00, how-to: 0.25, reference: 0.20, tutorial: 0.30

Summary: 8 files classified
  tutorial: 2
  how-to: 2
  reference: 2
  explanation: 2
  collapsed: 1 (mixed quadrants)
```

**Key observations:**
- `architecture.md` is collapsed (mixes Explanation + Reference) — consider splitting
- `README.md` has low confidence — it's a mixed-purpose file, which is normal for READMEs

---

## Example 2: Audit Documentation Coverage

**Scenario:** Run a coverage audit to find gaps.

```bash
$ uv run scripts/diataxis_audit.py --dir docs

Diataxis Documentation Audit
========================================
Directory: /projects/my-app/docs
Total documents: 8

Quadrant Coverage
--------------------
  Tutorial    : ██░░░░░░░░ 2 docs (25%)  [getting-started.md, README.md]
  How-to      : ██░░░░░░░░ 2 docs (25%)  [deploy-guide.md, setup-guide.md]
  Reference   : ██░░░░░░░░ 2 docs (25%)  [api-reference.md, config-options.md]
  Explanation : ██░░░░░░░░ 2 docs (25%)  [architecture.md, design-decisions.md]

Collapsed Documents (mixed quadrants)
--------------------
  ! architecture.md — mixes Explanation + Reference
    Suggestion: Split into architecture-explanation.md and architecture-reference.md

Quality Score: 73/100
  Coverage balance:          25/25
  Quadrant purity:           22/25
  Classification confidence: 18/25
  Documentation volume:      8/25

Result: PASS (8 docs, 1 collapsed, 0 unclassified)
```

---

## Example 3: Validate Quadrant Purity

**Scenario:** Check that your tutorial doesn't accidentally include reference content.

```bash
$ uv run scripts/diataxis_validate.py --file docs/getting-started.md

Diataxis Purity Validation Report
========================================
Directory: /projects/my-app/docs
Files validated: 1

Info: 1
  - DX008 getting-started.md — Tutorial missing 'What You'll Learn' section

Result: PASS (1 files, 0 errors, 0 warnings, 1 info)
```

**Scenario:** Validate all docs for CI.

```bash
$ uv run scripts/diataxis_validate.py --dir docs --strict

Diataxis Purity Validation Report
========================================
Directory: /projects/my-app/docs
Files validated: 8

Warnings: 2
  ! DX001 getting-started.md (line 85) — Tutorial contains 8 table rows (reference-style content)
    Suggestion: Move parameter/option tables to a separate Reference document
  ! DX006 architecture.md — Collapsed document: mixes Explanation + Reference
    Suggestion: Consider splitting into separate explanation and reference documents

Info: 1
  - DX008 getting-started.md — Tutorial missing 'What You'll Learn' section

Result: WARN (8 files, 0 errors, 2 warnings, 1 info)
```

With `--strict`, exit code is 1 (CI fails on warnings).

---

## Example 4: Scaffold a New Diataxis Structure

**Scenario:** Set up Diataxis folders for a new project.

```bash
$ uv run scripts/diataxis_scaffold.py --dry-run

Scaffolding Diataxis structure at: docs/ [folders] (dry-run)

  Would create: docs/
  Would create: docs/README.md
  Would create: docs/tutorials/
  Would create: docs/tutorials/README.md
  Would create: docs/how-to/
  Would create: docs/how-to/README.md
  Would create: docs/reference/
  Would create: docs/reference/README.md
  Would create: docs/explanation/
  Would create: docs/explanation/README.md

Would create: 10 items
```

```bash
$ uv run scripts/diataxis_scaffold.py --init-config

Scaffolding Diataxis structure at: docs/ [folders]

  ...

Created: 10 items

Next steps:
  1. Add documentation to each quadrant directory
  2. Run: uv run diataxis_audit.py --dir docs to check coverage
  3. Run: uv run diataxis_validate.py --dir docs to check purity
```

**Flat layout** for smaller projects:

```bash
$ uv run scripts/diataxis_scaffold.py --layout flat --dry-run

Scaffolding Diataxis structure at: docs/ [flat] (dry-run)

  Would create: docs/
  Would create: docs/README.md

Would create: 2 items
```

---

## Example 5: JSON Output for Scripting

**Scenario:** Pipe classification results to another tool.

```bash
$ uv run scripts/diataxis_classify.py docs/api-reference.md --json

[
  {
    "file": "/projects/my-app/docs/api-reference.md",
    "primary_quadrant": "reference",
    "confidence": "high",
    "score": 0.85,
    "scores": {
      "tutorial": 0.0,
      "how-to": 0.1,
      "reference": 0.85,
      "explanation": 0.05
    },
    "is_collapsed": false,
    "collapsed_quadrants": [],
    "signals": {
      "reference": [
        "title:reference",
        "title:api",
        "heading:parameters",
        "heading:endpoints",
        "structural:tables(15)",
        "structural:parameter_tables(3)"
      ]
    },
    "reason": "Title: 'reference', 'api'; Structure: tables(15), parameter_tables(3)"
  }
]
```

---

## Example 6: Handling Collapsed Documents

**Scenario:** `architecture.md` is flagged as collapsed (mixes Explanation + Reference).

**Step 1:** Understand why:
```bash
$ uv run scripts/diataxis_classify.py docs/architecture.md --verbose

File              | Quadrant    | Confidence | Collapsed | Reason
------------------+-------------+------------+-----------+---------
architecture.md   | explanation | medium     | Yes (E+R) | Title: 'architecture'; Structure: long_paragraphs(4)
                    Scores: explanation: 0.45, how-to: 0.10, reference: 0.35, tutorial: 0.00
```

Both explanation (0.45) and reference (0.35) score above 0.3, and the ratio is < 2:1.

**Step 2:** Read the doc and identify sections to split:
- Conceptual sections ("Why we chose microservices", "Design principles") → `explanation/architecture-overview.md`
- Factual sections ("Service endpoints", "Configuration matrix") → `reference/architecture-reference.md`

**Step 3:** Re-validate after splitting:
```bash
$ uv run scripts/diataxis_validate.py --file docs/explanation/architecture-overview.md
# Should pass with no DX006 warning
```
