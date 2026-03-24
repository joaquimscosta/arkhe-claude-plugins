# Refresh Skill — Examples

## Example 1: First-Time Init

**Command**: `/roadmap:refresh init`

**Context**: New project with no `.arkhe/roadmap/` directory.

**Output**:
```
## Context Directory Status

| File | Exists | Staleness |
|------|--------|-----------|
| project.md | No | — |
| architecture.md | No | — |
| documents.md | No | — |

Scaffolding `.arkhe/roadmap/` with all 3 context files...

[Runs context discovery, generates project.md]

**Write this to `.arkhe/roadmap/project.md`?**
> Yes

[Generates architecture.md]

**Write this to `.arkhe/roadmap/architecture.md`?**
> Yes

[Generates documents.md]

**Write this to `.arkhe/roadmap/documents.md`?**
> Yes

Context directory scaffolded with 3 files.
```

## Example 2: Check Mode — Detecting Stale Files

**Command**: `/roadmap:refresh check`

**Output**:
```
## Context Directory Status

| File | Exists | Staleness | Days | Commits Since | feat/fix |
|------|--------|-----------|------|---------------|----------|
| project.md | Yes | fresh | 3 | 2 | 0 |
| architecture.md | Yes | stale | 45 | 18 | 12 |
| documents.md | Yes | aging | 15 | 6 | 3 |

New modules not in architecture.md: payments, notifications

**Recommendations:**
- `architecture.md` is **stale** (45 days, 12 feat/fix commits). 2 new modules discovered.
  Run `/roadmap:refresh architecture` to regenerate.
- `documents.md` is **aging** (15 days, 3 feat/fix commits). Consider refreshing.
- `project.md` is **fresh**. No action needed.
```

## Example 3: Refreshing architecture.md After Adding Modules

**Command**: `/roadmap:refresh architecture`

**Output**:
```
## Current architecture.md
[shows current content]

## Proposed architecture.md
[shows new content with updated module inventory, new ADRs, refreshed tech stack]

**Changes detected:**
- Added modules: payments (12 source, 4 test), notifications (8 source, 2 test)
- New ADR: ADR-0015 Payment Gateway Selection
- Updated module file counts

**Write this to `.arkhe/roadmap/architecture.md`?**
> Yes

architecture.md updated.
```

## Example 4: Full Refresh After Major Release

**Command**: `/roadmap:refresh all`

**Output**:
```
## Context Directory Status

| File | Exists | Staleness | Days | Commits Since | feat/fix |
|------|--------|-----------|------|---------------|----------|
| project.md | Yes | stale | 60 | 45 | 22 |
| architecture.md | Yes | stale | 60 | 45 | 22 |
| documents.md | Yes | stale | 60 | 45 | 22 |

All files are stale. Regenerating all 3 files...

[Shows project.md diff, asks confirmation]
[Shows architecture.md diff, asks confirmation]
[Shows documents.md diff, asks confirmation]

All 3 context files regenerated.
```
