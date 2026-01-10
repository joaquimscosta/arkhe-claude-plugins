---
description: Explain complex code through clear narratives and visual diagrams
---

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

This command invokes the **code-explanation** skill with: `$ARGUMENTS`

For comprehensive examples and detailed methodology, see:
- [WORKFLOW.md](../skills/code-explanation/WORKFLOW.md)
- [EXAMPLES.md](../skills/code-explanation/EXAMPLES.md)
