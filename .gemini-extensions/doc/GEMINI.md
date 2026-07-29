# doc

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Gemini equivalents. Install the `core` extension if you have not already.

@../../plugins/core/skills/using-arkhe-skills/SKILL.md

## Skills

- **adr** — Create, review, and manage Architecture Decision Records (ADRs) with auto-numbering, template detection, quality review, and index maintenance. Use when user mentions "ADR", "architecture decision", "document this decision", "create ADR", "review ADR", editing ADR files (docs/adr/, doc/adr/, .adr/), or discussing architectural choices and tradeoffs.
- **code-explanation** — Explains complex code through clear narratives, visual diagrams, and step-by-step breakdowns. Use when user asks to explain code, understand algorithms, analyze design patterns, wants code walkthroughs, or mentions "explain this code", "how does this work", "code breakdown", or "understand this function".
- **diagramming** — Creates Mermaid and ASCII diagrams for flowcharts, architecture, ERDs, state machines, mindmaps, and more. Use when user mentions diagram, flowchart, mermaid, ASCII diagram, text diagram, terminal diagram, visualize, C4, mindmap, architecture diagram, sequence diagram, ERD, or needs visual documentation.
- **diataxis** — Audit, classify, validate, and scaffold documentation using the Diataxis framework (Tutorials, How-to guides, Reference, Explanation). Use when user mentions "diataxis", "documentation framework", "quadrant", "doc audit", "doc coverage", "collapsed document", "tutorial vs how-to", "quadrant purity", "documentation types", or wants to classify docs by type.
- **doc-coauthoring** — Guide users through structured collaborative documentation creation. Use when user wants to write documentation, update README, create architecture docs, draft proposals, technical specs, decision docs, refactor documentation, create API docs, or document code.
- **doc-freshness** — Detect documentation drift, stale references, and cross-document inconsistencies in any project. Scans for code-doc drift (API/function changes not reflected in docs), cross-doc drift (conflicting information across documents), and stale references (broken links, deleted files, outdated versions). Use when checking "doc freshness", "stale docs", "documentation drift", "broken links", "outdated documentation", "doc accuracy", "docs out of date", "doc audit", "doc health", or "verify documentation".
- **jd-docs** — Scaffold, validate, and maintain Johnny.Decimal documentation structure for software projects. Use when user mentions "Johnny Decimal", "J.D docs", "docs structure", "organize docs", "documentation layout", "scaffold docs", "docs migration", "generate index", "docs index", "add area", "classify docs", "move doc", editing files in numbered directories (00-*, 10-*, 20-*), or discussing documentation organization.
- **research-frontmatter** — Validate and enforce standard YAML frontmatter on research documents with JD-aware path resolution. Use when creating, editing, or validating research files, when user mentions "research metadata", "research frontmatter", "research staleness", "validate research", "RD-rules", or "research docs validation".
- **rfc** — Manage architecture RFCs: create, review, list, update, and transition status. Use when user mentions "RFC", "technical proposal", "architecture proposal", or wants to draft, review, list, update, or change status of RFCs.

## Commands

See `commands/` directory for transpiled Gemini TOML commands.
