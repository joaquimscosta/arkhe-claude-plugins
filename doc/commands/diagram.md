---
description: Create or edit Mermaid diagrams for flowcharts, sequence diagrams, ERDs, state machines, and more
---

# Diagram Command

Generate professional Mermaid diagrams for documentation, system architecture, process flows, and data visualization.

## Usage

```
/diagram <description of what you want to visualize>
```

## Supported Diagram Types

- **Flowcharts** - Process flows, decision trees, workflows
- **Sequence Diagrams** - API interactions, system communication, user flows
- **Class Diagrams** - Object-oriented design, database models
- **State Diagrams** - State machines, lifecycle flows
- **ERD (Entity Relationship)** - Database schemas, data models
- **Gantt Charts** - Project timelines, task scheduling
- **Pie Charts** - Data distributions, proportions
- **Git Graphs** - Branch strategies, version control flows
- **User Journeys** - User experience mapping, customer flows
- **Quadrant Charts** - Priority matrices, feature analysis
- **Timeline Diagrams** - Historical events, product evolution

## Examples

### Create a flowchart for user authentication:
```
/diagram user authentication flow with login, validation, and redirect to dashboard
```

### Generate a sequence diagram for API communication:
```
/diagram sequence diagram showing client, API gateway, auth service, and database interactions for user registration
```

### Create an ERD for a blog platform:
```
/diagram entity relationship diagram for a blog with users, posts, comments, and tags
```

### Generate a Gantt chart for project timeline:
```
/diagram gantt chart for a 3-month product development project with planning, development, testing, and deployment phases
```

### Create a state diagram for order processing:
```
/diagram state diagram showing order lifecycle from draft to delivered with payment and shipping states
```

### Refactor an existing diagram:
```
/diagram refactor this mermaid diagram to add error handling states and improve styling
[paste existing diagram]
```

## Features

- **Auto-selection** of the most appropriate diagram type based on your description
- **Professional styling** with colors, shapes, and layouts optimized for readability
- **Both basic and styled versions** provided for flexibility
- **Comments and documentation** explaining complex syntax
- **Rendering instructions** for different platforms (GitHub, GitLab, documentation sites)
- **Alternative suggestions** if a different diagram type might work better

## Tips

1. **Be specific** about what you want to visualize
2. **Mention the diagram type** if you have a preference (otherwise it will be auto-selected)
3. **Include key entities/steps** you want represented
4. **Specify styling preferences** if desired (colors, themes, layout direction)
5. **Provide context** for better diagram structure (e.g., "for API documentation" vs "for executive presentation")

## Output Format

The command will provide:

1. **Complete Mermaid code** ready to use
2. **Rendering preview** showing how it will look
3. **Usage instructions** for your target platform
4. **Styling options** and customization suggestions
5. **Alternative approaches** if applicable

## Integration

This command invokes the **Mermaid Diagram Generator** skill, which can also be automatically triggered when you mention diagram-related keywords in your conversations.

For detailed examples and troubleshooting, see the skill documentation in `doc/skills/mermaid/`.

## Related Resources

- **Examples**: See comprehensive diagram examples in `doc/skills/mermaid/EXAMPLES.md`
- **Troubleshooting**: Common issues and solutions in `doc/skills/mermaid/TROUBLESHOOTING.md`
- **Mermaid Documentation**: https://mermaid.js.org
- **Live Editor**: https://mermaid.live (test and preview diagrams)
