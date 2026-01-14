# Deep Research Workflow

Detailed process flows for the deep-research skill.

## Research Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER REQUEST                                │
│              "Research event sourcing patterns"                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  1. NORMALIZE TO SLUG                           │
│                                                                 │
│  Input: "event sourcing patterns"                               │
│  Output: "event-sourcing-patterns"                              │
│                                                                 │
│  Rules:                                                         │
│  - Lowercase all characters                                     │
│  - Replace spaces with hyphens                                  │
│  - Remove special characters                                    │
│  - Check alias mappings                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   2. CHECK CACHE                                │
│                                                                 │
│  Path: ~/.claude/plugins/research/index.json                    │
│                                                                 │
│  Lookup by:                                                     │
│  - Direct slug match                                            │
│  - Alias match (e.g., "ES" → "event-sourcing")                  │
│                                                                 │
│  If found, check expiration:                                    │
│  - expires_at > now → VALID                                     │
│  - expires_at <= now → EXPIRED (suggest refresh)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
               CACHE HIT           CACHE MISS
                    │                   │
                    ▼                   ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│   3a. RETURN CACHED     │ │   3b. CONDUCT RESEARCH  │
│                         │ │                         │
│ Read content.md from:   │ │ Invoke deep-researcher  │
│ ~/.claude/plugins/      │ │ agent with EXA tools:   │
│   research/entries/     │ │                         │
│   {slug}/content.md     │ │ - web_search_exa for    │
│                         │ │   concepts & guides     │
│ Report:                 │ │ - get_code_context_exa  │
│ - Cache status          │ │   for implementations   │
│ - Expiration date       │ │                         │
│ - Content summary       │ │ Structure results in    │
│                         │ │ standard format         │
└─────────────────────────┘ └─────────────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────┐
                    │        4. CACHE RESULTS         │
                    │                                 │
                    │ Create entry directory:         │
                    │ ~/.claude/plugins/research/     │
                    │   entries/{slug}/               │
                    │                                 │
                    │ Write:                          │
                    │ - metadata.json (timestamps,    │
                    │   aliases, tags)                │
                    │ - content.md (full research)    │
                    │                                 │
                    │ Update index.json               │
                    └─────────────────────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────┐
                    │       5. REPORT TO USER         │
                    │                                 │
                    │ - Cache status (hit/miss)       │
                    │ - Brief summary                 │
                    │ - File path                     │
                    │ - Promote suggestion            │
                    └─────────────────────────────────┘
```

## Promote Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  /research promote {slug}                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  1. READ FROM CACHE                             │
│                                                                 │
│  Path: ~/.claude/plugins/research/entries/{slug}/content.md     │
│                                                                 │
│  If not found → Error: "Research not cached. Run /research      │
│                         {topic} first."                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                2. ADD SECTION MARKERS                           │
│                                                                 │
│  Wrap existing content:                                         │
│  <!-- AUTO-GENERATED: Start -->                                 │
│  {cached content}                                               │
│  <!-- AUTO-GENERATED: End -->                                   │
│                                                                 │
│  Add team section:                                              │
│  <!-- TEAM-NOTES: Start -->                                     │
│  ## Team Context                                                │
│  [Add project-specific notes here]                              │
│  <!-- TEAM-NOTES: End -->                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. WRITE TO PROJECT DOCS                           │
│                                                                 │
│  Path: docs/research/{slug}.md                                  │
│                                                                 │
│  Create docs/research/ if doesn't exist                         │
│  Add promoted_at timestamp to frontmatter                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               4. UPDATE PROJECT INDEX                           │
│                                                                 │
│  Path: docs/research/README.md                                  │
│                                                                 │
│  Add/update entry in index table:                               │
│  | Slug | Title | Promoted | Has Team Notes |                   │
│  |------|-------|----------|----------------|                   │
│  | {slug} | {title} | {date} | No |                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   5. CONFIRM TO USER                            │
│                                                                 │
│  "Promoted to docs/research/{slug}.md"                          │
│  "Edit TEAM-NOTES section to add project context"               │
└─────────────────────────────────────────────────────────────────┘
```

## Refresh Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  /research refresh {slug}                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              1. CONDUCT FRESH RESEARCH                          │
│                                                                 │
│  Bypass cache, invoke deep-researcher agent                     │
│  Use EXA tools for new content                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               2. UPDATE TIER 1 CACHE                            │
│                                                                 │
│  Replace entirely:                                              │
│  - metadata.json (new timestamps)                               │
│  - content.md (new content)                                     │
│  - index.json entry                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         3. CHECK FOR PROMOTED VERSION                           │
│                                                                 │
│  Path: docs/research/{slug}.md                                  │
│                                                                 │
│  If exists → Update Tier 2                                      │
│  If not → Done                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                 EXISTS            NOT FOUND
                    │                   │
                    ▼                   ▼
┌─────────────────────────┐        ┌──────────┐
│   4. UPDATE TIER 2      │        │   DONE   │
│                         │        └──────────┘
│ Parse existing file:    │
│ - Extract TEAM-NOTES    │
│ - Replace AUTO-GENERATED│
│   with new content      │
│ - Preserve TEAM-NOTES   │
│ - Update timestamps     │
└─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   5. REPORT TO USER                             │
│                                                                 │
│  "Refreshed {slug}"                                             │
│  "Updated: Tier 1 cache"                                        │
│  "Updated: docs/research/{slug}.md (preserved team notes)"      │
└─────────────────────────────────────────────────────────────────┘
```

## File Structures

### Tier 1 Cache Entry

```
~/.claude/plugins/research/entries/{slug}/
├── metadata.json
│   {
│     "slug": "domain-driven-design",
│     "title": "Domain-Driven Design",
│     "aliases": ["DDD", "domain driven design"],
│     "tags": ["architecture", "patterns", "modeling"],
│     "researched_at": "2025-01-14T10:30:00Z",
│     "expires_at": "2025-02-13T10:30:00Z",
│     "sources": [
│       {"url": "https://...", "title": "..."}
│     ]
│   }
│
└── content.md
    ---
    slug: domain-driven-design
    title: Domain-Driven Design
    ...
    ---

    # Domain-Driven Design

    ## Overview
    ...
```

### Tier 2 Promoted Entry

```
docs/research/{slug}.md

---
slug: domain-driven-design
title: Domain-Driven Design
promoted_at: 2025-01-14T12:00:00Z
last_refreshed: 2025-01-14T10:30:00Z
---

<!-- AUTO-GENERATED: Start -->
# Domain-Driven Design

## Overview
[Auto-generated content...]

<!-- AUTO-GENERATED: End -->

<!-- TEAM-NOTES: Start -->
## Team Context

- We use DDD in our Order Management bounded context
- See `src/order/` for implementation
- Contact @jane for DDD questions

<!-- TEAM-NOTES: End -->
```

### Index Files

**Tier 1 Index** (`~/.claude/plugins/research/index.json`):
```json
{
  "domain-driven-design": {
    "slug": "domain-driven-design",
    "title": "Domain-Driven Design",
    "aliases": ["DDD", "domain driven design"],
    "researched_at": "2025-01-14T10:30:00Z",
    "expires_at": "2025-02-13T10:30:00Z"
  },
  "event-sourcing": {
    "slug": "event-sourcing",
    "title": "Event Sourcing",
    "aliases": ["ES"],
    "researched_at": "2025-01-10T08:00:00Z",
    "expires_at": "2025-02-09T08:00:00Z"
  }
}
```

**Tier 2 Index** (`docs/research/README.md`):
```markdown
# Research Index

Curated technical research for this project.

| Topic | Promoted | Last Refreshed | Team Notes |
|-------|----------|----------------|------------|
| [Domain-Driven Design](domain-driven-design.md) | 2025-01-14 | 2025-01-14 | Yes |
| [Event Sourcing](event-sourcing.md) | 2025-01-12 | 2025-01-10 | No |
```
