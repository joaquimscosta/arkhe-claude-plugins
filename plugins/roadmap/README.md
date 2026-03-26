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

Each capability is available as both a **skill** (quick analysis in chat) and an **agent** (produces persistent artifacts). All three skills support a `--deep` flag that runs a multi-agent pipeline with quality gates, confidence scoring, and cross-perspective validation.

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
| `refresh` | `init`, `check`, `all`, `project`, `architecture`, `documents` | Context directory scaffolding and drift detection |

### Agents (Write Artifacts)

| Agent | Output Directory | Description |
|-------|-----------------|-------------|
| `product-manager` | `{output_dir}/requirements/` | User stories, scope docs, prioritization artifacts |
| `system-architect` | `{output_dir}/architecture/` | Design documents, ADRs, boundary analysis |
| `roadmap-analyst` | Report output | Comprehensive 6-phase project health report |
| `roadmap-critic` | N/A (read-only) | Quality reviewer for `--deep` pipelines. Scores artifacts using Confession Pattern |

### `--deep` Mode (Multi-Agent Pipelines)

Each skill supports `--deep` for a full multi-agent orchestration pipeline:

| Skill | `--deep` Pipeline | Patterns Used |
|-------|-------------------|---------------|
| `pm --deep` | Context Gatherer (Haiku) -> PM Analyst + Confession (Sonnet) -> Architect Feasibility (Haiku) -> Confidence Scoring (Haiku) | Pipeline, Confession, Critic-Actor, Specification-First |
| `architect --deep` | Context Gatherer (Haiku) -> Architecture Analyst + Confession (Sonnet) -> **Red Team Adversary** (Sonnet) -> Confidence Scoring (Haiku) | Pipeline, Confession, Adversarial Review |
| `roadmap --deep` | 2 Parallel Context Agents (Haiku) -> **3 Parallel Perspectives**: PM + Architect + Roadmap (Sonnet) -> Cross-Reference Synthesis (Sonnet) -> Confidence Scoring (Haiku) | Pipeline, Supervisor-Worker, Parallel Execution, Confession |

All `--deep` pipelines filter findings below confidence threshold (70) and tag uncertain findings with `[NEEDS VALIDATION]`.

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
# PM skill (light)
/roadmap:pm stories authentication
/roadmap:pm prioritize
/roadmap:pm scope dark-mode

# PM skill (deep -- multi-agent pipeline with quality gates)
/roadmap:pm --deep stories authentication
/roadmap:pm --deep scope dark-mode

# Roadmap skill (light)
/roadmap:roadmap status
/roadmap:roadmap gaps
/roadmap:roadmap blockers

# Roadmap skill (deep -- 3 parallel perspectives + cross-reference synthesis)
/roadmap:roadmap --deep health
/roadmap:roadmap --deep risks

# Architect skill (light)
/roadmap:architect module payments
/roadmap:architect boundaries

# Architect skill (deep -- adversarial review by red team agent)
/roadmap:architect --deep module payments
/roadmap:architect --deep boundaries
```

## Context Directory Refresh

Scaffold and maintain the `.arkhe/roadmap/` context directory:

```bash
# Check if context files are stale
/roadmap:refresh check

# Scaffold context directory for first time
/roadmap:refresh init

# Regenerate all context files from current codebase
/roadmap:refresh all

# Regenerate a single file
/roadmap:refresh architecture
```

Context files use a **hybrid format**: condensed summary (<300 tokens) for fast context injection + references to authoritative docs for deep analysis.

## Doc Freshness

> **Moved to the Doc plugin.** Use `/doc:health` instead of `/roadmap:doc-freshness`.

## Cross-Project Compatibility

The plugin adapts to any tech stack through dynamic discovery:

- **Java/Kotlin**: Detects Gradle/Maven, scans for Spring modules, entities, controllers
- **JavaScript/TypeScript**: Detects package.json, scans for components, routes, hooks
- **Python**: Detects pyproject.toml/setup.py, scans for packages, models, views
- **Go**: Detects go.mod, scans for packages, handlers, models
- **Rust**: Detects Cargo.toml, scans for crates, modules, traits
