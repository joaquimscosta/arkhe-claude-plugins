---
name: documentation-generation
description: Generate documentation from code including API docs, READMEs, architecture guides, and technical references. Use when user mentions "generate docs", "create documentation", "write README", "API documentation", "document this code", or needs any documentation artifacts. Routes to docs-architect agent for comprehensive 10+ page documentation.
---

# Documentation Generation

Generate documentation artifacts from code with appropriate depth based on scope.

## Quick Decision: Simple vs Comprehensive

| Documentation Need | Approach |
|--------------------|----------|
| README for a module | Use patterns below |
| API reference | Use OpenAPI patterns below |
| Single component docs | Use patterns below |
| **Full system documentation** | Use `docs-architect` agent |
| **Architecture guides (10+ pages)** | Use `docs-architect` agent |
| **Technical manuals** | Use `docs-architect` agent |

## When to Use docs-architect Agent

Route to the agent for comprehensive documentation needs:

```
Use the docs-architect agent to create comprehensive documentation for [system/module]
```

The agent excels at:
- Deep codebase analysis
- 10-100+ page technical documentation
- Architecture documentation with rationale
- Multi-chapter technical manuals

## Quick Patterns

### README Generation

```markdown
# Project Name

Brief description (1-2 sentences)

## Features
- Feature 1
- Feature 2

## Installation
[Installation steps]

## Quick Start
[Minimal working example]

## Configuration
[Key configuration options]

## API Reference
[Link or inline reference]

## Contributing
[Contribution guidelines]

## License
[License type]
```

### API Documentation (OpenAPI)

```yaml
openapi: 3.0.0
info:
  title: API Name
  version: 1.0.0
paths:
  /resource:
    get:
      summary: Get resources
      responses:
        '200':
          description: Success
```

### Component Documentation

```markdown
## ComponentName

**Purpose**: What it does (1 sentence)

**Props/Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|

**Usage**:
[Code example]

**Notes**:
- Important behavior
- Edge cases
```

### Function Documentation

```markdown
## functionName

**Purpose**: What it does

**Parameters**:
- `param1` (Type): Description
- `param2` (Type): Description

**Returns**: Type - Description

**Example**:
[Code example]

**Throws**: ErrorType - When condition
```

## Documentation Quality Checklist

- [ ] Purpose clear in first sentence
- [ ] Installation/setup instructions complete
- [ ] Working examples included
- [ ] Edge cases documented
- [ ] API contracts specified
- [ ] Configuration options listed

## Output Formats

| Format | Use Case |
|--------|----------|
| Markdown | READMEs, guides, wikis |
| OpenAPI/Swagger | REST API documentation |
| JSDoc/TSDoc | Inline code documentation |
| Docstrings | Python documentation |

## Resources

- [WORKFLOW.md](WORKFLOW.md) - Step-by-step documentation workflows
- [EXAMPLES.md](EXAMPLES.md) - Complete documentation templates

## Integration

This skill auto-invokes on documentation keywords. For explicit control, use `/doc-generate`.

For comprehensive documentation (architecture guides, technical manuals), invoke:
```
Use the docs-architect agent to document [scope]
```
