---
name: infographic-designer
description: Generates or improves technical-education infographics (programming, AI/ML, algorithms, cloud, architecture) using a modular framework. Use when asked to plan, draft, or refine an infographic; when given a topic + audience; or when provided a structured layout/wireframe to render. Allows structured JSON layout input for deterministic composition. Allowed tools: Read, Write, Execute.
allowed-tools: Read, Write, Execute
---

# Infographic Designer
A Claude Code Skill that plans, drafts, and improves **technical education infographics** using a reusable framework. It supports generate and improve operations.

## When to use
- Topic + audience provided (e.g., “Kotlin coroutines for Android devs”)
- Need a clear **template** (Concept Map, Process Flow, Algorithm Breakdown, etc.)
- Provided **structured layout** and want consistent rendering.
- Asked to **improve** clarity, hierarchy, or accessibility.

## Quick start
**Generate (plan → optional render)**
1. Create plan (select template, number regions)
2. (Optional) Render via script: `scripts/generate_infograph.py --mode structured`

**Improve (audit → revise → optional re-render)**
1. Audit checklist in `08_Checklist.md`
2. Revise, validate, re-render if needed

## Inputs / Outputs
- **Input**: text brief or JSON wireframe
- **Output**: plan + optional PNG(s) saved to `./output/`

See `WORKFLOW.md`, `EXAMPLES.md`, and `references/` for details.
