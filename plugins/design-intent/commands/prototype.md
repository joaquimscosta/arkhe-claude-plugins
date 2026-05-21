---
description: Rapid UI prototyping — generates 3 visually distinct HTML/CSS components from a text prompt and serves them in a live browser gallery
argument-hint: "<component description> [--vary <1|2|3>] [--dir <output-dir>] [--continue]"
---

# Prototype

Generate rapid UI prototypes following the **prototype** skill. Input: $ARGUMENTS

Generate all 3 artifacts in one pass — do not pause between them or ask for confirmation. The value is seeing 3 diverse approaches side-by-side in a live gallery.

If `$ARGUMENTS` contains `--continue`, read the user's pick from the most recent prototype session's `events.jsonl` and report it instead.
