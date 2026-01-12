---
description: Generate comprehensive documentation from code with AI-powered analysis
---

# Documentation Generation

Generate documentation for your codebase, from quick READMEs to comprehensive technical manuals.

## Usage

```
/doc-generate <scope or documentation type>
```

## Examples

### Quick Documentation

```
/doc-generate README for the authentication module
/doc-generate API docs for src/api/users
/doc-generate configuration reference
```

### Comprehensive Documentation

For deep analysis and long-form documentation (10+ pages), use the docs-architect agent:

```
Use the docs-architect agent to create comprehensive documentation for [system]
```

## Documentation Types

| Type | Command Example | Output |
|------|-----------------|--------|
| README | `/doc-generate README for auth module` | Project README |
| API Reference | `/doc-generate API docs for /api/*` | OpenAPI spec |
| Configuration | `/doc-generate config reference` | Config table |
| Module Docs | `/doc-generate docs for utils/` | Module documentation |
| **Architecture** | Use docs-architect agent | 10-100+ page guide |
| **Technical Manual** | Use docs-architect agent | Comprehensive manual |

## When to Use docs-architect Agent

For complex documentation needs:
- Full system architecture documentation
- Technical manuals and ebooks
- Multi-chapter documentation
- Deep codebase analysis

```
Use the docs-architect agent to document the entire payment processing system
```

## Output Formats

- **Markdown** - READMEs, guides, wikis
- **OpenAPI/Swagger** - REST API documentation
- **JSDoc/TSDoc** - Inline code documentation

## Tips

1. **Be specific** about what you want documented
2. **Specify the format** if you have a preference
3. **Use the agent** for comprehensive documentation needs

## Integration

This command invokes the **documentation-generation** skill with: `$ARGUMENTS`

For detailed workflows and templates, see:
- [WORKFLOW.md](../skills/documentation-generation/WORKFLOW.md)
- [EXAMPLES.md](../skills/documentation-generation/EXAMPLES.md)
