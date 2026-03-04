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
- `/research list` - Show research for current project (scoped by git repo)
- `/research list --all` - Show all cached research across all projects

## Context

**Arguments:** $ARGUMENTS

## Instructions

Parse the arguments to determine the operation.

**IMPORTANT:** The `scripts/` path references below are relative to the `deep-research` skill directory. Resolve the absolute path by finding the skill at `plugins/core/skills/deep-research/scripts/` (or use Glob to locate `deep-research/scripts/cache_manager.py`).

### Operation: Research Topic (default)
If arguments don't start with `promote`, `refresh`, or `list`:

**Cache-first approach** — check cache BEFORE spawning the agent to avoid unnecessary agent overhead on cache hits:

1. **Resolve script path:** Use Glob to find `**/deep-research/scripts/cache_manager.py` and note the directory.

2. **Check cache:** Run:
   ```bash
   python3 {scripts_dir}/cache_manager.py check "{topic}"
   ```
   Parse the JSON output. It returns `exists`, `slug`, `expired`, `expires_at`, `researched_at`.

3. **If cache hit (exists=true, expired=false):**
   - Read the cached content directly:
     ```bash
     python3 {scripts_dir}/cache_manager.py get "{slug}"
     ```
   - Parse the JSON output and present the content to the user.
   - Report cache status: HIT, source: Cached, path, expiration date.
   - Suggest: `/research promote {slug}` to add to project docs.
   - **Do NOT spawn the agent.** This is the fast path.

4. **If cache expired (exists=true, expired=true):**
   - Read and return the cached content (same as cache hit).
   - Warn the user: "Cache expired. Returning cached content but refresh recommended."
   - Suggest: `/research refresh {slug}` to update.
   - **Do NOT spawn the agent.** Return stale content with the warning.

5. **If cache miss (exists=false):**
   - Spawn the `deep-researcher` agent using the Agent tool (subagent_type: `core:deep-researcher`).
   - Pass the topic and the resolved `scripts_dir` path so the agent can use `cache_manager.py put` to cache results.
   - The agent will conduct research via EXA tools, cache the results, and report findings.

### Operation: Promote
If arguments start with `promote <slug>`:

1. Resolve the script path as above.
2. Execute:
   ```bash
   python3 {scripts_dir}/promote.py {slug}
   ```
3. Parse the JSON output from the script.
4. If `success` is true, report: "Promoted {slug} to {path}"
5. If `success` is false, report the error message.

### Operation: Refresh
If arguments start with `refresh <slug>`:

1. Spawn the `deep-researcher` agent using the Agent tool (subagent_type: `core:deep-researcher`).
2. Instruct it to:
   - Bypass cache and conduct fresh research via EXA
   - Use `cache_manager.py put` to save results (replacing existing cache entry)
   - Check if a promoted version exists at `docs/research/{slug}.md`
   - If promoted: use `promote.py {slug} --refresh` to update Tier 2 while preserving TEAM-NOTES
3. Report what was updated.

### Operation: List
If arguments start with `list`:

**Fast path** — no agent needed:

1. Resolve the script path.
2. Determine scope:
   - `list` (no flags) → project-scoped (auto-detected from git repo)
   - `list --all` → show all entries across all projects
   - `list --project <name>` → filter by specific project
3. Run:
   ```bash
   python3 {scripts_dir}/cache_manager.py list --format json [--all | --project <name>]
   ```
   Pass `--all` if the user requests all entries.
4. Parse the JSON output (object with `entries` array and `filter` metadata).
5. Scan `docs/research/` directory for promoted entries.
6. Display inventory in formatted markdown:

```markdown
## Research Inventory

### Cached (Tier 1)
| Slug | Title | Researched | Expires | Status |
|------|-------|------------|---------|--------|
| domain-driven-design | Domain-Driven Design | 2025-01-14 | 2025-02-13 | Valid |

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
# Research a topic (checks cache first — instant if cached)
/research domain-driven design
/research event sourcing patterns
/research "React Server Components"

# Promote to project docs
/research promote domain-driven-design

# Force refresh (always re-researches)
/research refresh domain-driven-design

# View inventory for current project (instant — no agent needed)
/research list

# View all research across all projects
/research list --all
```
