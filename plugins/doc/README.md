# Doc Plugin

Multi-purpose documentation toolkit for generating comprehensive technical documentation.

## Domain

📚 **Documentation** (generation, explanation, diagrams)

## Components

### Skills

- **doc-coauthoring**: Auto-invoked collaborative documentation workflow for all documentation types. Covers proposals, specs, decision docs, READMEs, API docs, architecture guides, and more. Uses a structured 3-stage process: Context Gathering, Refinement & Structure, and Reader Testing. Triggers on "write documentation", "create README", "draft proposal", "API docs", "architecture docs", "technical spec", "design doc", "decision doc", or "RFC".

- **diagramming**: Auto-invoked Mermaid diagram generator for flowcharts, sequence diagrams, ERDs, state machines, architecture diagrams, and more. Triggers when you mention diagram-related keywords or explicitly use the `/diagram` command. Provides comprehensive examples and troubleshooting for all diagram types.

- **code-explanation**: Auto-invoked code explanation skill that provides clear narratives, visual diagrams, and step-by-step breakdowns for complex code. Triggers on "explain this code", "how does this work", or when using `/code-explain`. Supports algorithm visualization, design pattern explanation, and progressive complexity levels.

- **managing-adrs**: Auto-invoked ADR (Architecture Decision Record) management for creating and maintaining technical decision documentation. Triggers on keywords like "ADR", "architecture decision", or when editing files in `docs/adr/`. Features auto-numbering, template detection (minimal or MADR 4.0), README index updates, and supersession workflow. Includes Python scripts using `uv` for deterministic operations.

### Commands

- **/code-explain**: Explains code in detail using the code-explanation skill. Generates visual diagrams, step-by-step breakdowns, and identifies patterns and gotchas. Perfect for understanding complex codebases.

- **/diagram**: Create or edit Mermaid diagrams with manual control. Supports all diagram types: flowcharts, sequence diagrams, ERDs, state diagrams, Gantt charts, pie charts, git graphs, user journeys, quadrant charts, and timelines.

## Use Cases

✅ System architecture documentation
✅ Generating comprehensive technical documentation
✅ Creating architecture diagrams and system visualizations
✅ Explaining complex code sections
✅ API documentation and technical manuals
✅ Architecture Decision Records (ADRs)
✅ Proposals, specs, and decision documents

## Applies To

- Full-stack application documentation
- System architecture visualization (Mermaid diagrams)
- Code explanation and technical writing
- API documentation and reference guides
- Technical proposals and decision docs

## Installation

```bash
# Add the marketplace
/plugin marketplace add ./arkhe-claude-plugins

# Install the doc plugin
/plugin install doc@arkhe-claude-plugins
```

## Usage

After installation, all commands and skills will be available:

```bash
# Use documentation commands
/code-explain src/services/auth/jwt-validator.ts

# Create diagrams (manual control)
/diagram user authentication flow with login and validation
/diagram sequence diagram for API communication

# Auto-invoke doc-coauthoring skill by mentioning documentation keywords
"Write a README for the authentication module"
"Create API documentation for src/api/users"
"Draft a proposal for the new caching layer"
"I need a technical spec for the notification system"

# Auto-invoke diagramming skill
"Create a flowchart for the payment process"
"I need an ERD for the database schema"
```

## Examples

### Documentation Co-Authoring

```bash
# READMEs and code docs (uses streamlined 2-stage workflow)
"Write a README for this project"
"Create API documentation for the users endpoint"
"Document the configuration options"

# Proposals and specs (uses full 3-stage workflow with Reader Testing)
"Draft a technical proposal for migrating to microservices"
"Write a design doc for the new caching layer"
"Create a decision document for choosing PostgreSQL"
```

### Code Explanation

```bash
/code-explain src/utils/data-transformer.ts
/code-explain the caching strategy in api/cache-manager.js
```

### Diagram Generation

```bash
# Method 1: Use /diagram command for explicit control
/diagram create a sequence diagram showing the authentication flow
/diagram generate an ERD for the database schema
/diagram flowchart for user registration process

# Method 2: Auto-invoke by mentioning diagram keywords
"I need a state diagram for the order lifecycle"
"Can you visualize the API flow with a sequence diagram?"
"Create a Gantt chart for the project timeline"
```

### ADR Management

```bash
# Auto-invoke by mentioning ADR keywords
"Create an ADR for using PostgreSQL"
"Document this architecture decision about authentication"
"I need to record why we chose React Query over Redux"

# Supersede an existing ADR
"Supersede ADR-0005 with a new caching strategy"

# Use scripts directly
uv run doc/skills/managing-adrs/scripts/adr_create.py --title "Use Redis for caching"
uv run doc/skills/managing-adrs/scripts/adr_create.py --title "..." --template madr
uv run doc/skills/managing-adrs/scripts/adr_index.py --dir docs/adr
```

## Common Workflows

### Documentation Workflow

1. **Collaborative documentation**:
   ```bash
   "I need to write documentation for the REST API"
   # Claude will offer the structured workflow with Context Gathering,
   # Refinement & Structure, and (optionally) Reader Testing stages
   ```

2. **Explain complex code**:
   ```bash
   /code-explain the algorithm implementation in processor.ts
   ```

3. **Create diagrams**:
   ```bash
   /diagram create a component diagram showing the system architecture
   # Or use auto-invoke:
   "I need a flowchart for the deployment process"
   ```

## Version

1.2.0
