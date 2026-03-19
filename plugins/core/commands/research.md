---
description: >
  Deep research on technical topics with intelligent caching.
  Supports: research, promote, refresh, and list operations.
  Example: "/research domain-driven design" or "/research promote ddd"
argument-hint: "<topic> | promote <slug> | refresh <slug> | list [--all]"
---

# Research

**Arguments:** $ARGUMENTS

**Scripts:** `plugins/core/skills/deep-research/scripts/` — use this path directly. If it fails, fall back to Glob for `**/deep-research/scripts/cache_manager.py`.

## Dispatch

Parse arguments to determine the operation:

### Research (default — no keyword prefix)

Cache-first approach using a single `fetch` call:

1. Run: `python3 {scripts}/cache_manager.py fetch "{topic}"`
2. Parse the JSON output:
   - **`exists=true`, `cache_status=valid`:** Present the `content` field to the user. Report cache HIT, path, expiration. Suggest `/research promote {slug}`.
   - **`exists=true`, `expired=true`:** Present the `content` field. Warn: "Cache expired — returning cached content." Suggest `/research refresh {slug}`. Do NOT spawn agent.
   - **`exists=false`:** Spawn `deep-researcher` agent (subagent_type: `core:deep-researcher`). Pass the topic and `scripts` path so the agent can cache results via `cache_manager.py put`.

### Promote (`promote <slug>`)

1. Run: `python3 {scripts}/promote.py {slug}`
2. Parse JSON output. Report success path or error.

### Refresh (`refresh <slug>`)

1. Spawn `deep-researcher` agent (subagent_type: `core:deep-researcher`).
2. Instruct it to: bypass cache, research fresh via EXA, cache with `cache_manager.py put`, then run `promote.py {slug} --refresh` if `docs/research/{slug}.md` exists.

### List (`list [--all | --project <name>]`)

1. Run: `python3 {scripts}/cache_manager.py list --format json [--all | --project <name>]`
2. Scan `docs/research/` for promoted entries.
3. Display as formatted markdown table with Cached (Tier 1) and Promoted (Tier 2) sections.

## Cache Tiers

- **Tier 1 (User):** `~/.claude/plugins/research/` — cross-project, 30-day TTL
- **Tier 2 (Team):** `docs/research/` — version controlled, editable
