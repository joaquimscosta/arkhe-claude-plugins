# Doc Plugin

Multi-purpose documentation toolkit for generating comprehensive technical documentation.

## Domain

📚 **Documentation** (generation, explanation, diagrams)

## Components

### Agents

- **docs-architect**: Creates comprehensive technical documentation from existing codebases. Analyzes architecture, design patterns, and implementation details to produce long-form technical manuals and ebooks. Perfect for documenting complex software architectures.

- **mermaid-expert**: Create Mermaid diagrams for flowcharts, sequences, ERDs, and architectures. Masters syntax for all diagram types and styling. Use for visualizing system architectures, data flows, and technical diagrams.

### Commands

- **/doc-generate**: Automated documentation generation that extracts information from code, creates clear explanations, and maintains consistency across documentation types. Use for generating project documentation.

- **/code-explain**: Explains code in detail, breaking down complex logic into understandable concepts with examples and use cases. Perfect for understanding complex codebases and technical implementations.

## Use Cases

✅ System architecture documentation
✅ Generating comprehensive technical documentation
✅ Creating architecture diagrams and system visualizations
✅ Explaining complex code sections
✅ API documentation and technical manuals

## Applies To

- Full-stack application documentation
- System architecture visualization (Mermaid diagrams)
- Code explanation and technical writing
- API documentation and reference guides

## Installation

```bash
# Add the marketplace
/plugin marketplace add ./arkhe-claude-plugins

# Install the doc plugin
/plugin install doc@arkhe-claude-plugins
```

## Usage

After installation, all agents, commands, and skills will be available:

```bash
# Use specialized agents
/agents
# Select from: docs-architect, mermaid-expert

# Use documentation commands
/doc-generate for the user authentication module
/code-explain src/services/auth/jwt-validator.ts
```

## Examples

### Architecture Documentation

```bash
# Use docs-architect agent
/agents
# Select: docs-architect
"Create comprehensive documentation for the authentication module"
```

### Code Explanation

```bash
/code-explain src/utils/data-transformer.ts
/code-explain the caching strategy in api/cache-manager.js
```

### Architecture Diagrams

```bash
# Use mermaid-expert agent
/agents
# Select: mermaid-expert
"Create a sequence diagram showing the authentication flow"
"Generate an ERD for the database schema"
```

## Common Workflows

### Documentation Workflow

1. **Generate documentation**:
   ```bash
   /doc-generate for the REST API endpoints
   ```

2. **Explain complex code**:
   ```bash
   /code-explain the algorithm implementation in processor.ts
   ```

3. **Create diagrams**:
   ```bash
   /agents
   # Select: mermaid-expert
   "Create a component diagram showing the system architecture"
   ```

## Version

1.0.0
