# Roadmap Plugin

<div align="center">
  <img src="../../assets/roadmap-plugin.jpg" alt="Roadmap Plugin" width="100%" />
</div>

Product management, roadmap analysis, and solution architecture for any project.

## Overview

The Roadmap plugin provides three complementary capabilities for project planning and analysis:

- **PM** — User stories, scope assessments, prioritization, and needs analysis
- **Roadmap** — Project status, gap tracking, blocker analysis, and risk mapping
- **Architect** — Module structure, API design, data models, and pattern conformance

Each capability is available as both a **skill** (quick analysis in chat) and an **agent** (produces persistent artifacts).

## Installation

```bash
/plugin marketplace add ./arkhe-claude-plugins
/plugin install roadmap@arkhe-claude-plugins
```

## Components

### Skills (Read-Only Analysis)

| Skill | Modes | Description |
|-------|-------|-------------|
| `pm` | `stories`, `prioritize`, `scope`, `validate`, `needs`, `compare`, `next` | Feature analysis from user perspective |
| `roadmap` | `status`, `gaps`, `next`, `delta`, `blockers`, `risks`, `update`, `specs` | Project health and progress tracking |
| `architect` | `module`, `api`, `data-model`, `boundaries`, `patterns`, `decisions`, `review`, `frontend` | System architecture analysis |

### Agents (Write Artifacts)

| Agent | Output Directory | Description |
|-------|-----------------|-------------|
| `product-manager` | `{output_dir}/requirements/` | User stories, scope docs, prioritization artifacts |
| `system-architect` | `{output_dir}/architecture/` | Design documents, ADRs, boundary analysis |
| `roadmap-analyst` | Report output | Comprehensive 6-phase project health report |

### Lane Discipline

Each component stays in its lane:

- **PM**: user stories, scope, prioritization. NOT code, ADRs, or architecture docs.
- **Architect**: design notes, ADRs, boundary analysis. NOT source code, tests, or config files.
- **Roadmap**: status tracking, gap analysis, risk mapping. NOT requirements or architecture docs.

## Configuration (Optional)

The plugin works out of the box with dynamic context discovery. For projects that want explicit configuration, create these optional files:

### `.arkhe.yaml` — Settings

```yaml
roadmap:
  output_dir: arkhe/roadmap              # Where artifacts are written (default: arkhe/roadmap)
  context_dir: .arkhe/roadmap            # Where context files live (default: .arkhe/roadmap)
  status_file: docs/PROJECT-STATUS.md    # Status doc path (default: docs/PROJECT-STATUS.md)
```

### `.arkhe/roadmap/` — Rich Context Files

```
.arkhe/roadmap/
├── project.md         # Project overview, personas, domain, constraints, phases
├── architecture.md    # Tech stack, modules, patterns, boundaries
└── documents.md       # Document map (key docs and their roles)
```

## Dynamic Context Discovery

When no configuration is present, skills automatically discover project context through (in priority order):

1. `.arkhe.yaml` — Read `roadmap:` section for settings
2. `.arkhe/roadmap/*.md` — Rich context files
3. `CLAUDE.md` + `README.md` — Project identity and scope
4. Build files — Auto-detect tech stack (Gradle, package.json, Cargo.toml, go.mod, pyproject.toml)
5. Directory structure — Detect module boundaries (`apps/*`, `src/*`, `packages/*`)
6. Documentation — Glob for docs, plans, ADRs, specs, gap analyses
7. Codebase scan — Tech-stack-aware patterns (last resort, mode-dependent)

## Module Maturity Scale

All components use a shared vocabulary for assessing module maturity:

| Level | Description |
|-------|-------------|
| Stub | Directory/package exists, maybe a placeholder |
| Domain Started | Entities/models/types defined |
| Service Layer | Business logic implemented |
| API Ready | Endpoints/routes exposed |
| Tested | Tests covering key paths |
| Production Ready | Fully tested, documented, monitoring-ready |

## Usage Examples

```bash
# PM skill
/roadmap:pm stories authentication
/roadmap:pm prioritize
/roadmap:pm scope dark-mode
/roadmap:pm compare SSR vs CSR

# Roadmap skill
/roadmap:roadmap status
/roadmap:roadmap gaps
/roadmap:roadmap blockers
/roadmap:roadmap update

# Architect skill
/roadmap:architect module payments
/roadmap:architect api user-profile
/roadmap:architect boundaries
/roadmap:architect patterns
```

## Cross-Project Compatibility

The plugin adapts to any tech stack through dynamic discovery:

- **Java/Kotlin**: Detects Gradle/Maven, scans for Spring modules, entities, controllers
- **JavaScript/TypeScript**: Detects package.json, scans for components, routes, hooks
- **Python**: Detects pyproject.toml/setup.py, scans for packages, models, views
- **Go**: Detects go.mod, scans for packages, handlers, models
- **Rust**: Detects Cargo.toml, scans for crates, modules, traits
