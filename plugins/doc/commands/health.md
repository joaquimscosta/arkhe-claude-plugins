---
description: Run documentation health checks (freshness, links, drift, cross-doc consistency)
argument-hint: "scan | check <path> | links | drift <path> | cross-doc | claude-md | report"
---

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
```

## Integration

Invoke the Skill tool with skill name "doc:doc-freshness" and arguments: `$ARGUMENTS`
