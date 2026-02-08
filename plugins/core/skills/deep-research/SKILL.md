---
name: deep-research
description: >
  Deep research on technical topics using EXA tools with intelligent two-tier caching.
  Use when user asks to research a topic, investigate best practices, look up information,
  find patterns, or explore architectures. Also invoked by /research command.
  Triggers: "research", "look up", "investigate", "deep dive", "find information about",
  "what are best practices for", "how do others implement".
---

# Deep Research

Coordinate deep technical research with intelligent caching for cross-project reuse and team knowledge sharing.

## Quick Start

When research is needed:

1. **Check cache first** - Read `~/.claude/plugins/research/index.json`
2. **If cached and valid** - Return cached content, note source
3. **If cache miss or expired** - Invoke `deep-researcher` agent
4. **Report findings** - Include cache status and promote suggestion

## Cache Architecture

| Tier | Location | Purpose | Shared |
|------|----------|---------|--------|
| 1 | `~/.claude/plugins/research/` | Fast, cross-project | User only |
| 2 | `docs/research/` | Curated, version controlled | Team |

## Operations

| Operation | Trigger | Action |
|-----------|---------|--------|
| Research | `/research <topic>` or natural language | Check cache → research if needed → cache results |
| Promote | `/research promote <slug>` | Cache → project docs with section markers |
| Refresh | `/research refresh <slug>` | Force re-research, preserve team notes |
| List | `/research list` | Show inventory of cached + promoted |

## Slug Normalization

Convert topics to cache keys:
- "Domain-Driven Design" → `domain-driven-design`
- "DDD" → `domain-driven-design` (via alias)
- "React Hooks" → `react-hooks`

## Output Format

After research, report:
```
## Research: {Topic}

**Cache:** {Hit | Miss | Expired}
**Source:** {Cached | Fresh research}
**Path:** ~/.claude/plugins/research/entries/{slug}/

[Brief summary of findings]

💡 Run `/research promote {slug}` to add to project docs.
```

## Promote Script

When promoting cached research to project docs, execute the promote script:

```bash
python3 scripts/promote.py {slug}
```

The `scripts/` path is relative to this skill's directory and resolves automatically.

The script reads from cache, adds section markers (AUTO-GENERATED + TEAM-NOTES), writes to `docs/research/{slug}.md`, and updates the README index.

Parse the JSON output:
- Success: `{"success": true, "message": "...", "slug": "...", "path": "..."}`
- Failure: `{"success": false, "message": "...", "slug": "..."}`

## Agent Delegation

For actual research execution, delegate to `deep-researcher` agent:
- Has MCP tool access (EXA web search, code context)
- Handles cache read/write operations
- Structures research output consistently

## Additional Resources

- [WORKFLOW.md](WORKFLOW.md) - Detailed process flows
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
