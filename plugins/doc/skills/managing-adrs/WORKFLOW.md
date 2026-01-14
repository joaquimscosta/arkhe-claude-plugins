# ADR Workflow

This document provides detailed step-by-step methodology for creating and managing Architecture Decision Records.

## Phase 1: Context Analysis

Before creating an ADR, gather context about the project:

### 1.1 Repository Detection

Check if the project is a git repository:
```bash
git rev-parse --git-dir 2>/dev/null
```

This helps determine:
- Where to store ADRs (near project root)
- Whether to track ADRs in version control

### 1.2 ADR Directory Discovery

Search for existing ADR directories in this order:

1. `docs/adr/` - Most common convention
2. `doc/adr/` - Alternative documentation structure
3. `architecture/decisions/` - Explicit architecture folder
4. `.adr/` - Hidden directory approach

If none found:
- Prompt user to create `docs/adr/`
- Use `--create-dir` flag with scripts

### 1.3 Existing ADR Analysis

When an ADR directory exists, analyze its contents:

```bash
ls -la docs/adr/*.md
```

Look for:
- `README.md` - Index file format
- `template.md` - Project-specific template
- Numbered ADRs - Naming convention used

---

## Phase 2: Template Detection

Analyze existing ADRs to match project conventions.

### 2.1 Naming Convention Detection

Common patterns:

| Pattern | Example | Usage |
|---------|---------|-------|
| `NNNN-title.md` | `0001-use-postgresql.md` | Most common |
| `NNN-title.md` | `001-use-postgresql.md` | Smaller projects |
| `ADR-NNNN-title.md` | `ADR-0001-use-postgresql.md` | Explicit prefix |

The scripts auto-detect padding width from existing files.

### 2.2 Section Structure Detection

Scan first 2-3 ADRs to identify sections in use:

**Required sections** (always present):
- `## Status`
- `## Date`
- Context/Problem description
- Decision statement
- Consequences

**Optional sections** (project-dependent):
- `## Technical Story`
- `## Decision Makers`
- `## Decision Drivers`
- `## Considered Options`
- `## Pros and Cons`
- `## Confirmation`
- `## More Information`

### 2.3 Template Selection

Based on analysis, use appropriate template:

| Project Has | Use Template |
|-------------|--------------|
| Simple ADRs with Status/Date/Context/Decision/Consequences | `minimal` |
| Full MADR-style with Options and Pros/Cons | `madr` |
| Custom template file | Copy and adapt existing |

---

## Phase 3: Auto-Numbering

Reliable numbering is critical for ADR management.

### 3.1 Parse Existing Numbers

Scan all `.md` files (excluding README.md, template.md):

```python
pattern = re.compile(r'^(?:ADR-)?(\d+)-.*\.md$', re.IGNORECASE)
```

Extract numbers and find maximum:

```python
max_number = 0
for filepath in adr_dir.glob('*.md'):
    match = pattern.match(filepath.name)
    if match:
        number = int(match.group(1))
        max_number = max(max_number, number)
next_number = max_number + 1
```

### 3.2 Handle Edge Cases

**Gaps in numbering:**
- Normal - gaps indicate superseded/deleted ADRs
- Continue from highest number

**Duplicate numbers:**
- Warn user
- Suggest renumbering or manual resolution

**No existing ADRs:**
- Start from 0001

### 3.3 Generate Filename

Convert title to kebab-case:

```python
slug = title.lower()
slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Remove special chars
slug = re.sub(r'\s+', '-', slug)          # Spaces to hyphens
slug = re.sub(r'-+', '-', slug)           # Collapse multiple hyphens
slug = slug.strip('-')                     # Trim leading/trailing
```

Result: `0005-use-postgresql-for-persistence.md`

---

## Phase 4: Content Generation

Creating the ADR content requires understanding the decision context.

### 4.1 Gather Information

Before writing, collect:

1. **Context**: Why is this decision needed?
2. **Problem**: What specific problem are we solving?
3. **Options**: What alternatives were considered?
4. **Decision**: What did we choose and why?
5. **Consequences**: What are the trade-offs?

### 4.2 Write Required Sections

**Status**: Always start as `Proposed`
```markdown
## Status
Proposed
```

**Date**: Use ISO 8601 format
```markdown
## Date
2026-01-10
```

**Context and Problem Statement**: 2-3 sentences
```markdown
## Context and Problem Statement
We need a database solution for our microservices architecture.
The solution must support complex queries, ACID transactions,
and scale to 10,000 concurrent users.
```

**Decision**: Clear statement with justification
```markdown
## Decision
We will use PostgreSQL as our primary database because it provides
excellent query performance, mature tooling, and our team has
extensive experience with it.
```

**Consequences**: Both positive and negative
```markdown
## Consequences

**Positive:**
- Full ACID transaction support
- Mature ecosystem with excellent tooling
- Team has deep expertise

**Negative:**
- Horizontal scaling requires additional setup (PgBouncer, read replicas)
- Schema migrations need careful planning
```

### 4.3 Add Optional Sections (MADR 4.0)

**Decision Drivers**: Forces influencing the decision
```markdown
## Decision Drivers
- ACID compliance is required for financial transactions
- Team has 5+ years PostgreSQL experience
- Need for complex JOIN queries
- Budget constraints favor open-source solutions
```

**Considered Options**: All alternatives evaluated
```markdown
## Considered Options
1. PostgreSQL
2. MongoDB
3. CockroachDB
4. Amazon Aurora
```

**Pros and Cons**: Detailed analysis
```markdown
## Pros and Cons of the Options

### PostgreSQL
- Good, because team has deep expertise
- Good, because excellent query optimizer
- Bad, because horizontal scaling is complex

### MongoDB
- Good, because easy horizontal scaling
- Bad, because no ACID transactions across documents
- Bad, because team lacks experience
```

---

## Phase 5: Index Update

Keep README.md synchronized with ADR files.

### 5.1 Parse Existing Index

If README.md exists, extract the current table format:

```markdown
| Number | Title | Status | Date |
|--------|-------|--------|------|
| 0001 | [Use PostgreSQL](0001-use-postgresql.md) | Accepted | 2026-01-05 |
```

### 5.2 Scan ADR Files

For each `.md` file (excluding README.md, template.md):

1. Extract number from filename
2. Extract title from `# ` heading
3. Extract status from `## Status` section
4. Extract date from `## Date` section

### 5.3 Generate Updated Index

Sort by number and regenerate table:

```python
adrs.sort(key=lambda x: x['number'])

for adr in adrs:
    row = f"| {adr['number']:04d} | [{adr['title']}]({adr['filename']}) | {adr['status']} | {adr['date']} |"
    rows.append(row)
```

### 5.4 Preserve Custom Content

The scripts generate a complete README.md with:
- Header explaining ADRs
- Index table
- Lifecycle explanation
- Creation instructions
- References

If you have custom content, manually merge after running the script.

---

## Phase 6: Supersession Handling

When an ADR is replaced by a new decision.

### 6.1 When to Supersede

Supersede an ADR when:
- The decision is fundamentally changed
- Technology is replaced entirely
- Requirements have significantly shifted

Do NOT supersede when:
- Making minor updates (edit in place)
- Adding clarifications (add to existing ADR)
- Implementing the decision (that's not a new decision)

### 6.2 Supersession Workflow

1. **Create new ADR** with the new decision
2. **Update old ADR status** to "Superseded by [ADR-NNNN]"
3. **Add reference** in new ADR: "Supersedes [ADR-NNNN]"
4. **Update README.md** index

Example using scripts:
```bash
# Create new ADR
uv run adr_create.py --title "Use Redis for Session Storage" --template madr

# Link them together (e.g., old=5, new=12)
uv run adr_supersede.py --old 5 --new 12 --dir docs/adr

# Update index
uv run adr_index.py --dir docs/adr
```

### 6.3 Resulting Changes

**Old ADR (0005-use-memcached.md):**
```markdown
## Status
Superseded by [ADR-0012](0012-use-redis-for-session-storage.md)
```

**New ADR (0012-use-redis-for-session-storage.md):**
```markdown
## Status
Accepted

Supersedes: [ADR-0005](0005-use-memcached.md)
```

---

## Best Practices

### Do

- Write ADRs when decisions are made, not after
- Keep context concise but complete
- Include concrete examples where helpful
- Link to related ADRs and resources
- Review ADRs periodically for relevance

### Don't

- Delete ADRs (supersede instead)
- Make ADRs too long (split if needed)
- Skip the "why" - it's the most valuable part
- Forget to update the index
- Leave ADRs in "Proposed" indefinitely

### Timing

| ADR Size | Target Time |
|----------|-------------|
| Minimal | 15-30 minutes |
| Standard | 30-60 minutes |
| Complex (with research) | 1-2 hours |

---

## Related Resources

- [SKILL.md](SKILL.md) - Quick reference
- [EXAMPLES.md](EXAMPLES.md) - Real-world examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Error handling
