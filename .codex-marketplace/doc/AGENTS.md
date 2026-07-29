# doc — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

Multi-purpose documentation toolkit (generation, explanation, diagrams, RFCs, health)

## Skills

- **adr** — Create, review, and manage Architecture Decision Records (ADRs) with auto-numbering, template detection, quality review, and index maintenance. Use when user mentions "ADR", "architecture decision",…
- **code-explanation** — Explains complex code through clear narratives, visual diagrams, and step-by-step breakdowns. Use when user asks to explain code, understand algorithms, analyze design patterns, wants code walkthroug…
- **diagramming** — Creates Mermaid and ASCII diagrams for flowcharts, architecture, ERDs, state machines, mindmaps, and more. Use when user mentions diagram, flowchart, mermaid, ASCII diagram, text diagram, terminal di…
- **diataxis** — Audit, classify, validate, and scaffold documentation using the Diataxis framework (Tutorials, How-to guides, Reference, Explanation). Use when user mentions "diataxis", "documentation framework", "q…
- **doc-coauthoring** — Guide users through structured collaborative documentation creation. Use when user wants to write documentation, update README, create architecture docs, draft proposals, technical specs, decision do…
- **doc-freshness** — Detect documentation drift, stale references, and cross-document inconsistencies in any project. Scans for code-doc drift (API/function changes not reflected in docs), cross-doc drift (conflicting in…
- **jd-docs** — Scaffold, validate, and maintain Johnny.Decimal documentation structure for software projects. Use when user mentions "Johnny Decimal", "J.D docs", "docs structure", "organize docs", "documentation l…
- **research-frontmatter** — Validate and enforce standard YAML frontmatter on research documents with JD-aware path resolution. Use when creating, editing, or validating research files, when user mentions "research metadata", "…
- **rfc** — Manage architecture RFCs: create, review, list, update, and transition status. Use when user mentions "RFC", "technical proposal", "architecture proposal", or wants to draft, review, list, update, or…

## Commands as Trigger Phrases

### When the user says "/doc:code-explain"

Explain complex code through clear narratives and visual diagrams

# Code Explanation

Explain complex code sections, algorithms, design patterns, or system architectures with visual aids and step-by-step breakdowns.

## Usage

```
/code-explain <file path or code description>
```

## Examples

### Explain a specific file:
```
/code-explain src/utils/data-transformer.ts
```

### Explain a concept in context:
```
/code-explain the caching strategy in api/cache-manager.js
```

### Explain an algorithm:
```
/code-explain the sorting algorithm in utils/sort.py
```

### Explain a design pattern:
```
/code-explain how the observer pattern is used in event-handler.ts
```

## What You Get

1. **Overview** - What the code does (1-2 sentences)
2. **Key Concepts** - Programming concepts identified
3. **Visual Diagrams** - Mermaid flowcharts, class diagrams, or sequence diagrams
4. **Step-by-Step Breakdown** - Logic explained with line references
5. **Common Questions** - Anticipated "why" and "what if" answers
6. **Gotchas** - Non-obvious behavior and edge cases

## Explanation Depth

The explanation depth adapts to code complexity:

| Complexity | Approach |
|------------|----------|
| Simple | Quick overview, key points |
| Moderate | Diagrams, step-by-step breakdown |
| Complex | Full analysis with patterns, pitfalls, alternatives |

## Tips

- **Be specific** - Point to exact files or functions
- **Provide context** - Mention your experience level if you want simpler/deeper explanations
- **Ask follow-ups** - Request deeper dives into specific parts

## Integration

Invoke the Skill tool with skill name "doc:code-explanation" and arguments: `$ARGUMENTS`

For comprehensive examples and detailed methodology, see:
- [WORKFLOW.md](../skills/code-explanation/WORKFLOW.md)
- [EXAMPLES.md](../skills/code-explanation/EXAMPLES.md)

### When the user says "/doc:diagram"

Create Mermaid or ASCII diagrams for flowcharts, architecture, ERDs, C4 models, mindmaps, and more

# Diagram Command

Create professional diagrams for documentation, architecture, and visualization.

## Examples

```
/diagram user authentication flow with login, validation, and redirect
/diagram sequence diagram showing client, API gateway, and database interactions
/diagram ERD for a blog with users, posts, comments, and tags
/diagram ASCII diagram showing request flow from client to API servers
/diagram C4 context diagram for an e-commerce platform
/diagram mindmap for mobile app features
```

## Integration

Invoke the Skill tool with skill name "doc:diagramming" and arguments: `$ARGUMENTS`

### When the user says "/doc:health" (args: "scan | check <path> | links | drift <path> | cross-doc | claude-md | onboard | report | setup")

Run documentation health checks (freshness, links, drift, cross-doc consistency)

# Documentation Health

Unified documentation health analysis. Detects stale docs, broken links, version drift, and cross-document inconsistencies.

## Modes

| Mode | Description |
|------|-------------|
| `scan` | Full analysis (links, versions, staleness, drift) |
| `links` | Broken links only (fast) |
| `check <path>` | Focused analysis on one file/directory |
| `drift <path>` | Code-doc drift for a specific doc |
| `cross-doc` | Cross-document consistency check |
| `report` | Full scan + persist report |
| `claude-md` | CLAUDE.md structural drift detection |
| `onboard` | Suggest/apply tracking frontmatter to docs |
| `setup` | Scaffold GitHub Actions workflow for automated doc health CI |
| _(none)_ | Same as `scan` |

## Examples

```
/doc:health
/doc:health links
/doc:health check README.md
/doc:health drift docs/api-reference.md
/doc:health cross-doc
/doc:health claude-md
/doc:health onboard
/doc:health report
/doc:health setup
```

## Integration

Invoke the Skill tool with skill name "doc:doc-freshness" and arguments: `$ARGUMENTS`

### When the user says "/doc:rfc" (args: "<action> [args]  (create <topic> | review <path> | list | update <path>)")

Manage architecture RFCs (create, review, list, update)

# RFC Command

Manage architecture RFCs: create new proposals, review existing ones, list the pipeline, or update sections.

## Examples

```
/rfc create event-driven notifications architecture
/rfc review docs/rfcs/0003-event-driven-notifications.md
/rfc list
/rfc update docs/rfcs/0003-event-driven-notifications.md
```

## Integration

Invoke the Skill tool with skill name "doc:rfc" and arguments: `$ARGUMENTS`
