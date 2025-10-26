# Doc Plugin

Multi-purpose documentation toolkit for generating comprehensive technical documentation.

## Domain

📚 **Documentation** (generation, explanation, diagrams)

## Components

### Agents

- **docs-architect**: Creates comprehensive technical documentation from existing codebases. Analyzes architecture, design patterns, and implementation details to produce long-form technical manuals and ebooks. Perfect for documenting complex software architectures.

### Skills

- **mermaid**: Auto-invoked Mermaid diagram generator for flowcharts, sequence diagrams, ERDs, state machines, architecture diagrams, and more. Triggers when you mention diagram-related keywords or explicitly use the `/diagram` command. Provides comprehensive examples and troubleshooting for all diagram types.

### Commands

- **/doc-generate**: Automated documentation generation that extracts information from code, creates clear explanations, and maintains consistency across documentation types. Use for generating project documentation. Auto-invokes the mermaid skill when diagram generation is needed.

- **/code-explain**: Explains code in detail, breaking down complex logic into understandable concepts with examples and use cases. Perfect for understanding complex codebases and technical implementations.

- **/diagram**: Create or edit Mermaid diagrams with manual control. Supports all diagram types: flowcharts, sequence diagrams, ERDs, state diagrams, Gantt charts, pie charts, git graphs, user journeys, quadrant charts, and timelines.

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
# Select from: docs-architect

# Use documentation commands
/doc-generate for the user authentication module
/code-explain src/services/auth/jwt-validator.ts

# Create diagrams (manual control)
/diagram user authentication flow with login and validation
/diagram sequence diagram for API communication

# Auto-invoke skill by mentioning keywords
"Create a flowchart for the payment process"
"I need an ERD for the database schema"
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
   /diagram create a component diagram showing the system architecture
   # Or use auto-invoke:
   "I need a flowchart for the deployment process"
   ```

## Version

1.0.0
