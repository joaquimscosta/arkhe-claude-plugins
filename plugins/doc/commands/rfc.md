---
description: Manage architecture RFCs (create, review, list, update)
argument-hint: "<action> [args]  (create <topic> | review <path> | list | update <path>)"
---

# RFC Command

Manage architecture RFCs: create new proposals, review existing ones, list the pipeline, or update sections.

## Examples

```
/rfc create event-driven notifications architecture
/rfc review docs/rfcs/0003-event-driven-notifications.md
/rfc list
/rfc update docs/rfcs/0003-event-driven-notifications.md
```

## Integration

Invoke the Skill tool with skill name "doc:rfc" and arguments: `$ARGUMENTS`
