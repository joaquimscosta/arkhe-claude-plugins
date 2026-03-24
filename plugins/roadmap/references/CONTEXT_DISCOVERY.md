# Context Discovery Protocol

Canonical discovery protocol shared by all roadmap plugin skills and agents. Execute all phases in order before producing any output.

## Phase 1: Configuration

Read `.arkhe.yaml` from the project root. Extract the `roadmap:` section:

```yaml
roadmap:
  output_dir: arkhe/roadmap       # Default: arkhe/roadmap
  context_dir: .arkhe/roadmap     # Default: .arkhe/roadmap
  status_file: docs/PROJECT-STATUS.md  # Default: docs/PROJECT-STATUS.md
```

## Phase 2: Johnny Decimal Detection

Check if the project uses Johnny Decimal documentation structure:

1. Read `.jd-config.json` at project root -- if present, use its `root` (default: `docs`) and `areas` map
2. If no config, glob for `docs/[0-9][0-9]-*/` -- if 2+ matches exist, J.D structure is present

If J.D detected, supplement Phase 5 globs:

| J.D Area | Scan Pattern | Content Type |
|----------|-------------|--------------|
| `{jd_root}/00-*/**/*.md` | Getting started | Planning, requirements, setup |
| `{jd_root}/10-*/**/*.md` | Product | Specs, features, roadmap, design |
| `{jd_root}/20-*/**/*.md` | Architecture | ADRs, system design, tech decisions |
| `{jd_root}/30-*/**/*.md` | Research | Technical spikes, investigations |
| `{jd_root}/90-*/**/*.md` | Archive | Skip unless searching historical context |

Keep existing non-J.D paths (`plan/**/*.md`, `specs/**/*.md`) as fallback.

## Phase 3: Rich Context

If `{context_dir}` exists (default: `.arkhe/roadmap`), read all `.md` files -- especially:

| File | Content |
|------|---------|
| `project.md` | Project overview, personas, domain, constraints, phases |
| `architecture.md` | Tech stack, modules, patterns, boundaries |
| `documents.md` | Document map (key docs and their roles) |

If context files are missing or stale, run `/roadmap:refresh init` to scaffold them or `/roadmap:refresh check` to detect drift.

## Phase 4: Project Identity

Read `CLAUDE.md` and `README.md` from the project root. Extract:
- Project purpose and scope
- Key constraints and conventions
- Tech stack and architecture overview
- Target users or personas

## Phase 5: Documentation Scan

Glob for planning and documentation files:

```
docs/**/*.md
plan/**/*.md
specs/**/*.md
arkhe/specs/*/spec.md
```

Categorize findings:
- **Status documents**: PROJECT-STATUS.md, roadmap.md, CHANGELOG.md
- **Gap analyses**: Documents identifying missing features or capabilities
- **Specs**: Feature specifications with requirements
- **ADRs**: Architecture Decision Records
- **Research**: Technical research and investigation documents

## Phase 6: Build File Detection

Detect tech stack from build files. See [TECH_STACK_DETECTION.md](TECH_STACK_DETECTION.md) for the full detection table and tech-stack-aware scan patterns.

## Phase 7: Codebase Scan

Glob for directory structure to understand module boundaries:

```
apps/*, src/*, packages/*, libs/*, modules/*, internal/*, cmd/*
```

For each discovered module, note its name and contents. The depth of this scan varies by role:
- **PM**: Light scan -- detect modules, routes, models
- **Architect**: Deep scan -- also detect framework patterns, architecture patterns, database patterns (see [TECH_STACK_DETECTION.md](TECH_STACK_DETECTION.md) Architecture-Specific Scanning)
- **Roadmap**: Thorough scan -- count source files, test files, migrations per module; check for TODOs/FIXMEs/stubs
