---
name: architect
description: "Analyze system architecture, module structure, API contracts, data models, and code patterns. Use when designing systems, reviewing module boundaries, evaluating API designs, analyzing data models, checking pattern conformance, tracing architectural decisions, or reviewing frontend architecture. Triggers: architecture, module design, API design, data model, boundaries, patterns, decisions, frontend architecture."
argument-hint: "[--deep] module <name> | api <feature> | data-model <feature> | boundaries | patterns | decisions | frontend <feature>"
allowed-tools: Read, Glob, Grep, Write
---

# System Architect

Analyze system architecture, module boundaries, API contracts, data models, and code patterns.

## Workflow

### Step 1: Context Discovery

Run the shared context discovery protocol in [CONTEXT_DISCOVERY.md](../../references/CONTEXT_DISCOVERY.md) (all phases, deep scan for Phase 7). Also glob for architecture-specific documents:

```
docs/adr/**/*.md, docs/architecture/**/*.md, docs/design/**/*.md
```

Then perform architecture-specific scans from [TECH_STACK_DETECTION.md](../../references/TECH_STACK_DETECTION.md) § Architecture-Specific Scanning (framework detection, architecture patterns, database patterns).

### Step 2: Validate Discovery

Before proceeding, verify sufficient context was gathered:

- **Tech stack detected** — at least one primary language/framework identified
- **Source structure mapped** — module or directory layout is clear
- **Existing patterns found** — at least one architectural pattern (layering, naming, API style) identified

If any check fails, report what is missing and ask the user for clarification before continuing. Do not guess at architecture when the codebase lacks sufficient artifacts.

### Step 3: Parse Arguments

Parse from `$ARGUMENTS`:

| Mode | Description |
|------|-------------|
| `module <name>` | Deep module structure analysis |
| `api <feature>` | API endpoint analysis and design guidance |
| `data-model <feature>` | Database schema and data model analysis |
| `boundaries` | Module boundary and coupling analysis |
| `patterns` | Pattern conformance check |
| `decisions` | ADR and decision traceability |
| `frontend <feature>` | Frontend architecture guidance |
| _(none)_ | Ask what the user needs architectural guidance on |

### Step 4: Execute Mode

| Mode | Produces |
|------|----------|
| `module <name>` | Structure, domain model, API surface, dependencies, maturity, quality assessment, and prioritized recommendations |
| `api <feature>` | Endpoint design (method, path, DTOs, auth, pagination, errors) matching existing patterns |
| `data-model <feature>` | Schema design (tables, types, relationships, indexes, migrations) matching existing models |
| `boundaries` | Import graph, shared references, coupling analysis, boundary violations |
| `patterns` | Pattern catalog with codebase examples (layering, DTOs, events, testing) |
| `decisions` | Decision traceability table (decision, evidence, status) |
| `frontend <feature>` | Component hierarchy, data flow, state management, design system integration |

See [WORKFLOW.md](WORKFLOW.md) for detailed execution steps per mode.

### Step 5: Present Output

- **Conversational with optional file persistence** — deliver analysis in chat, offer to save
- **Diagram-friendly** — use Mermaid diagrams when they clarify relationships
- **Pattern-consistent** — always reference existing codebase patterns
- **Practical** — recommendations must be implementable
- **Scoped** — answer the specific question; do not redesign the whole system

### Step 6: Offer File Persistence

After producing the analysis, ask the user:

> **Save this analysis to `{output_dir}/architecture/{filename}.md`?**

Where `{output_dir}` comes from `.arkhe.yaml` (default: `arkhe/roadmap`).

| Mode | Filename Pattern |
|------|-----------------|
| `module <name>` | `module-{name}.md` |
| `api <feature>` | `api-{feature-slug}.md` |
| `data-model <feature>` | `data-model-{feature-slug}.md` |
| `boundaries` | `boundary-analysis.md` |
| `patterns` | `pattern-catalog.md` |
| `decisions` | `decision-traceability.md` |
| `frontend <feature>` | `frontend-{feature-slug}.md` |

## Deep Mode (`--deep`)

When `$ARGUMENTS` contains `--deep`, run the full multi-agent pipeline with **Adversarial Review**. A red team agent actively tries to break the proposed architecture.

See [WORKFLOW.md](WORKFLOW.md) § Deep Pipeline for the 5-phase execution protocol.

**Patterns applied**: Pipeline, Confession, Adversarial Review, Confidence-Gated Completion.

## Lane Discipline

See the System Architect section of [LANE_DISCIPLINE.md](../../references/LANE_DISCIPLINE.md). Stay in your lane.

## References

- [WORKFLOW.md](WORKFLOW.md) — Detailed mode execution workflows
- [EXAMPLES.md](EXAMPLES.md) — Usage examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues and fixes
