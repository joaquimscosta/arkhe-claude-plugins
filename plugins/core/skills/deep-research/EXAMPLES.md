# Deep Research Examples

Real-world usage examples for the deep-research skill.

## Basic Research

### Research a New Topic (Cache Miss)

```
User: /research domain-driven design

Claude: Researching "domain-driven design"...

Normalized slug: domain-driven-design
Cache status: MISS (not found)

Conducting research via EXA...

## Research: Domain-Driven Design

**Cache:** Miss
**Source:** Fresh research via EXA
**Path:** ~/.claude/plugins/research/entries/domain-driven-design/

### Summary

Domain-Driven Design (DDD) is a software development approach that focuses on
modeling complex business domains. Key concepts include:

- **Bounded Contexts**: Explicit boundaries where domain models apply
- **Ubiquitous Language**: Shared vocabulary between developers and domain experts
- **Aggregates**: Clusters of entities treated as a single unit
- **Domain Events**: Significant occurrences in the domain

### Key Insights

- Strategic DDD (boundaries, contexts) often more valuable than tactical patterns
- Start with modular monolith, extract microservices later
- 95% of projects may not need full tactical DDD

💡 Run `/research promote domain-driven-design` to add to project docs.
```

### Research with Cache Hit

```
User: /research DDD

Claude: Researching "DDD"...

Normalized slug: domain-driven-design (via alias)
Cache status: HIT (valid until 2025-02-13)

## Research: Domain-Driven Design

**Cache:** Hit
**Source:** Cached (researched 2025-01-14)
**Expires:** 2025-02-13
**Path:** ~/.claude/plugins/research/entries/domain-driven-design/

[Returns cached content...]

💡 Run `/research refresh domain-driven-design` to get fresh research.
```

### Research with Expired Cache

```
User: /research event sourcing

Claude: Researching "event sourcing"...

Normalized slug: event-sourcing
Cache status: EXPIRED (was valid until 2024-12-31)

⚠️ Cache expired. Returning cached content but refresh recommended.

## Research: Event Sourcing

**Cache:** Expired
**Source:** Cached (researched 2024-12-01)
**Expired:** 2024-12-31
**Path:** ~/.claude/plugins/research/entries/event-sourcing/

[Returns cached content...]

💡 Run `/research refresh event-sourcing` to update with fresh research.
```

## Promotion

### Promote to Project Docs

```
User: /research promote domain-driven-design

Claude: Promoting domain-driven-design to project docs...

✅ Promoted to docs/research/domain-driven-design.md

The file includes:
- AUTO-GENERATED section with research content
- TEAM-NOTES section for project-specific context

Next steps:
1. Edit the TEAM-NOTES section to add project context
2. Commit to version control for team access
3. Future refreshes will preserve your team notes
```

### Promote Non-Existent Research

```
User: /research promote microservices

Claude: ❌ Error: Research not found in cache.

The topic "microservices" hasn't been researched yet.

Run `/research microservices` first, then promote.
```

## Refresh

### Refresh Cached Research

```
User: /research refresh domain-driven-design

Claude: Refreshing domain-driven-design...

Conducting fresh research via EXA...

✅ Refresh complete

Updated:
- ~/.claude/plugins/research/entries/domain-driven-design/ (cache)
- docs/research/domain-driven-design.md (preserved team notes)

Changes:
- New sources from 2025
- Updated best practices section
- Added Spring Modulith integration guidance
```

### Refresh with Team Notes Preserved

```
User: /research refresh event-sourcing

Claude: Refreshing event-sourcing...

Found promoted version at docs/research/event-sourcing.md
Detected TEAM-NOTES section - will preserve.

Conducting fresh research via EXA...

✅ Refresh complete

Updated:
- Cache: Fully replaced
- docs/research/event-sourcing.md:
  - AUTO-GENERATED: Updated with fresh content
  - TEAM-NOTES: Preserved (contains team context)

Your team notes remain intact:
> "We use event sourcing in the Order aggregate. See OrderEventStore.java"
```

## Inventory

### List All Research

```
User: /research list

Claude: ## Research Inventory

### Cached (Tier 1: ~/.claude/plugins/research/)

| Slug | Title | Researched | Expires | Status |
|------|-------|------------|---------|--------|
| domain-driven-design | Domain-Driven Design | 2025-01-14 | 2025-02-13 | ✅ Valid |
| event-sourcing | Event Sourcing | 2025-01-10 | 2025-02-09 | ✅ Valid |
| cqrs | CQRS Pattern | 2024-11-15 | 2024-12-15 | ⚠️ Expired |
| react-hooks | React Hooks | 2025-01-05 | 2025-02-04 | ✅ Valid |

### Promoted (Tier 2: docs/research/)

| Slug | Title | Promoted | Team Notes |
|------|-------|----------|------------|
| domain-driven-design | Domain-Driven Design | 2025-01-14 | ✅ Yes |
| event-sourcing | Event Sourcing | 2025-01-12 | ✅ Yes |

### Summary
- **Cached:** 4 topics (1 expired)
- **Promoted:** 2 topics (both with team notes)

💡 Commands:
- `/research <topic>` - Research new topic
- `/research promote <slug>` - Promote to project docs
- `/research refresh <slug>` - Update existing research
```

## Natural Language Triggers

The skill auto-triggers on research-related phrases:

### "Research this pattern"

```
User: Can you research the repository pattern for me?

Claude: [Skill auto-triggers]

Researching "repository pattern"...
[Proceeds with research flow]
```

### "Look up best practices"

```
User: I need to look up best practices for API versioning

Claude: [Skill auto-triggers]

Researching "api versioning best practices"...
[Proceeds with research flow]
```

### "Investigate how others implement"

```
User: Can you investigate how others implement circuit breakers?

Claude: [Skill auto-triggers]

Researching "circuit breaker pattern"...
[Proceeds with research flow]
```

## Cross-Project Benefit

### Scenario: Research in Project A, Use in Project B

```
# In Project A (e-commerce)
User: /research domain-driven design
Claude: [Researches and caches at ~/.claude/plugins/research/]

# Later, in Project B (fintech)
User: /research DDD
Claude: Cache status: HIT (researched in another project)
[Returns cached content - no external API call needed]
```

## Edge Cases

### Research with Special Characters

```
User: /research "C# async/await patterns"

Claude: Researching "C# async/await patterns"...

Normalized slug: csharp-async-await-patterns
[Proceeds with research]
```

### Ambiguous Topic Clarification

```
User: /research ES

Claude: Clarifying "ES"...

Found multiple possible matches:
1. event-sourcing (alias: ES)
2. elasticsearch (alias: ES)

Which topic did you mean?
1. Event Sourcing - Domain event persistence pattern
2. Elasticsearch - Search and analytics engine

[Waits for user selection]
```
