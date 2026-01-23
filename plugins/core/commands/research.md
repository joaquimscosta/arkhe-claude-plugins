---
description: >
  Deep research on technical topics with intelligent caching.
  Supports: research, promote, refresh, and list operations.
  Example: "/research domain-driven design" or "/research promote ddd"
argument-hint: "<topic> | promote <slug> | refresh <slug> | list"
---

# Research

## Usage

- `/research <topic>` - Research a topic (checks cache first)
- `/research promote <slug>` - Promote cached research to project docs
- `/research refresh <slug>` - Force refresh of cached research
- `/research list` - Show all cached and promoted research

## Context

**Arguments:** $ARGUMENTS

## Instructions

Parse the arguments to determine the operation:

### Operation: Research Topic (default)
If arguments don't start with `promote`, `refresh`, or `list`:

1. Use the Task tool to spawn the `deep-researcher` agent (subagent_type: "core:deep-researcher")
2. Pass the topic for research
3. The agent will:
   - Check cache at `~/.claude/plugins/research/`
   - Return cached content if valid (not expired)
   - Conduct new research via EXA if cache miss
   - Save results to cache
   - Report findings with cache status

### Operation: Promote
If arguments start with `promote <slug>`:

1. Run the promote script to handle the promotion:
   ```bash
   python plugins/core/skills/deep-research/scripts/promote.py {slug}
   ```
2. Parse the JSON output from the script
3. If success is true, report: "Promoted {slug} to {path}"
4. If success is false, report the error message

### Operation: Refresh
If arguments start with `refresh <slug>`:

1. Use the Task tool to spawn the `deep-researcher` agent
2. Instruct it to bypass cache and conduct fresh research
3. For Tier 1 (cache): Replace entirely
4. For Tier 2 (promoted): Only update AUTO-GENERATED sections, preserve TEAM-NOTES
5. Report what was updated

### Operation: List
If arguments equal `list`:

1. Read `~/.claude/plugins/research/index.json` for cached entries
2. Scan `docs/research/` for promoted entries
3. Display inventory:

```markdown
## Research Inventory

### Cached (Tier 1)
| Slug | Title | Researched | Expires | Status |
|------|-------|------------|---------|--------|
| domain-driven-design | Domain-Driven Design | 2025-01-14 | 2025-02-13 | Valid |
| react-hooks | React Hooks | 2024-12-01 | 2024-12-31 | Expired |

### Promoted (Tier 2)
| Slug | Title | Promoted | Has Team Notes |
|------|-------|----------|----------------|
| domain-driven-design | Domain-Driven Design | 2025-01-14 | Yes |
```

## Cache Location

- **Tier 1 (User Cache):** `~/.claude/plugins/research/`
- **Tier 2 (Project Docs):** `docs/research/` (configurable)

## Examples

```bash
# Research a topic
/research domain-driven design
/research event sourcing patterns
/research "React Server Components"

# Promote to project docs
/research promote domain-driven-design

# Force refresh
/research refresh domain-driven-design

# View inventory
/research list
```
