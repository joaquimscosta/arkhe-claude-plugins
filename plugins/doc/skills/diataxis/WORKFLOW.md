# Diataxis Workflow

Step-by-step methodology for applying the Diataxis framework to a project's documentation.

## Table of Contents

1. [Phase 1: Discover](#phase-1-discover)
2. [Phase 2: Classify](#phase-2-classify)
3. [Phase 3: Audit](#phase-3-audit)
4. [Phase 4: Validate](#phase-4-validate)
5. [Phase 5: Scaffold](#phase-5-scaffold)
6. [Phase 6: Reorganize](#phase-6-reorganize)

---

## Phase 1: Discover

**Goal:** Understand the current state of documentation before making changes.

### Steps

1. Identify the docs directory:
   ```bash
   ls docs/  # or doc/, documentation/
   ```

2. Count and list all markdown files:
   ```bash
   find docs -name "*.md" | wc -l
   ```

3. Check if a `.diataxis-config.json` exists (indicates prior Diataxis setup)

4. Look for existing structure patterns:
   - Are docs already in subdirectories?
   - Is there a README or index?
   - Are there numbered (J.D) prefixes?

### Decision Points

- **No docs directory**: Jump to [Phase 5: Scaffold](#phase-5-scaffold)
- **Few docs (< 5)**: Skip audit, go to [Phase 2: Classify](#phase-2-classify)
- **Many docs (5+)**: Proceed to [Phase 2: Classify](#phase-2-classify)

---

## Phase 2: Classify

**Goal:** Determine which Diataxis quadrant each document belongs to.

### Steps

1. Classify all markdown files:
   ```bash
   uv run scripts/diataxis_classify.py docs/*.md --verbose
   ```

2. Review the results table. For each file, check:
   - Is the quadrant assignment correct?
   - Is the confidence level acceptable?
   - Are any files flagged as "collapsed"?

3. For low-confidence files, read the document and decide manually:
   - Does it teach through guided practice? → **Tutorial**
   - Does it solve a specific task? → **How-to**
   - Does it describe system facts? → **Reference**
   - Does it explain concepts or decisions? → **Explanation**

4. For collapsed documents, decide:
   - **Split**: Separate into multiple focused documents
   - **Accept**: Some docs legitimately serve dual purposes (e.g., README)

### Distinguishing Tutorial vs How-to

This is the hardest classification distinction. Key differentiators:

| Signal | Tutorial | How-to |
|--------|----------|--------|
| **Length** | Long, complete journey | Short, focused task |
| **Starts with** | "What you'll learn" / prerequisites | Problem statement / "You need to..." |
| **Steps** | Sequential, all required | May have alternatives |
| **Context** | Provides full setup | Assumes existing project |
| **Tone** | "Let's create..." | "Run the following..." |
| **Code** | Builds up incrementally | Complete solutions |

### JSON Output

For scripting or integration:
```bash
uv run scripts/diataxis_classify.py docs/*.md --json > classification.json
```

---

## Phase 3: Audit

**Goal:** Assess documentation coverage across all four quadrants.

### Steps

1. Run the audit:
   ```bash
   uv run scripts/diataxis_audit.py --dir docs
   ```

2. Review the coverage report:
   - **Quadrant distribution**: Are all four quadrants represented?
   - **Coverage gaps**: Which quadrants are missing or underrepresented?
   - **Collapsed documents**: Which docs need splitting?
   - **Quality score**: Target 70+ for mature projects

3. Address gaps by planning new documents:

   | Missing Quadrant | What to Write |
   |-----------------|---------------|
   | Tutorial | Getting-started guide, first project walkthrough |
   | How-to | Task-specific guides (deploy, configure, migrate) |
   | Reference | API docs, config options, CLI reference |
   | Explanation | Architecture overview, design rationale |

### Quality Score Breakdown

The quality score (0-100) has four components:

- **Coverage balance (25)**: How evenly docs are distributed across quadrants
- **Quadrant purity (25)**: Penalty for collapsed documents
- **Classification confidence (25)**: Average confidence of classifications
- **Documentation volume (25)**: Total documentation depth

---

## Phase 4: Validate

**Goal:** Check that documents maintain quadrant purity — each doc focuses on one type.

### Steps

1. Run validation:
   ```bash
   uv run scripts/diataxis_validate.py --dir docs
   ```

2. Review warnings:
   - **DX001-DX004**: Quadrant mixing — content from one quadrant appears in another
   - **DX005-DX006**: Classification issues — unclear or collapsed documents
   - **DX007-DX010**: Best practice suggestions — missing recommended sections

3. For each warning, decide:
   - **Fix**: Move the mixed content to the correct quadrant document
   - **Accept**: Some warnings are acceptable (e.g., a README with both setup steps and config reference)

### CI Integration

Use `--strict` to fail CI on warnings:
```bash
uv run scripts/diataxis_validate.py --dir docs --strict
```

### Single File Validation

Validate a specific file:
```bash
uv run scripts/diataxis_validate.py --file docs/getting-started.md
```

---

## Phase 5: Scaffold

**Goal:** Create a Diataxis-aware folder structure for new or existing projects.

### Steps

1. Preview the scaffold:
   ```bash
   uv run scripts/diataxis_scaffold.py --dry-run
   ```

2. Choose a layout:
   - **Folders** (default, recommended for 10+ docs):
     ```bash
     uv run scripts/diataxis_scaffold.py --layout folders
     ```
     Creates: `tutorials/`, `how-to/`, `reference/`, `explanation/`

   - **Flat** (for smaller projects):
     ```bash
     uv run scripts/diataxis_scaffold.py --layout flat
     ```
     Creates: Hub README with quadrant sections

3. Optionally create a config file:
   ```bash
   uv run scripts/diataxis_scaffold.py --init-config
   ```

### Folder Layout Output

```
docs/
├── README.md                    # Hub page with quadrant overview
├── tutorials/
│   └── README.md                # Guidelines for writing tutorials
├── how-to/
│   └── README.md                # Guidelines for writing how-to guides
├── reference/
│   └── README.md                # Guidelines for writing reference docs
└── explanation/
    └── README.md                # Guidelines for writing explanations
```

---

## Phase 6: Reorganize

**Goal:** Move existing documents into the Diataxis structure.

### Steps

1. After scaffolding and classifying, move documents:
   ```bash
   # Move tutorials
   mv docs/getting-started.md docs/tutorials/
   mv docs/first-project.md docs/tutorials/

   # Move how-to guides
   mv docs/deploy-guide.md docs/how-to/
   mv docs/configure-auth.md docs/how-to/

   # Move reference docs
   mv docs/api-reference.md docs/reference/
   mv docs/config-options.md docs/reference/

   # Move explanations
   mv docs/architecture.md docs/explanation/
   mv docs/design-decisions.md docs/explanation/
   ```

2. Handle collapsed documents:
   - Read the document and identify the mixed sections
   - Extract reference tables → `reference/`
   - Extract conceptual sections → `explanation/`
   - Keep the core content in the appropriate quadrant

3. Update cross-references:
   ```bash
   # Find all references to moved files
   grep -r "getting-started.md" docs/
   ```

4. Re-run audit to verify improvements:
   ```bash
   uv run scripts/diataxis_audit.py --dir docs
   ```

---

## Coordination with Other Skills

### With doc-coauthoring

After classifying a document's quadrant, suggest the appropriate writing style:

- **Tutorial**: Use doc-coauthoring's Full Collaborative workflow with encouraging tone
- **How-to**: Use Streamlined workflow, recipe-style
- **Reference**: Use Streamlined workflow with table-heavy patterns
- **Explanation**: Use Full Collaborative workflow with narrative prose

### With jd-docs

The Diataxis skill operates independently of Johnny.Decimal structure. If both are active:

- Diataxis classifies by **content type** (what kind of doc)
- J.D classifies by **topic area** (where it belongs organizationally)
- A doc can be in `20-architecture/` (J.D area) and classified as "explanation" (Diataxis quadrant)
