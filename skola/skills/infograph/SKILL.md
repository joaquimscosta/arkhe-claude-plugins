---
name: infographic
description: Generates or improves technical-education infographics (programming, AI/ML, algorithms, cloud, architecture) using a modular framework. Use when asked to plan, draft, or refine an infographic; when given a topic + audience; or when provided a structured layout/wireframe to render. Allows structured JSON layout input for deterministic composition. Allowed tools: Read, Write, Execute.
allowed-tools: Read, Write, Execute
---

# Infographic Designer

A Claude Code Skill that plans, drafts, and improves **technical education infographics** using a reusable framework. It supports:
- **Generate**: Produce a layout + content plan; optionally render via Gemini (image).
- **Improve**: Audit an existing plan or image description and return fixes; optionally re-render.

## When to use
- Topic + audience provided (e.g., “Kotlin coroutines for Android devs”).
- Need a clear **template** (Concept Map, Process Flow, Algorithm Breakdown, Comparison Matrix, Architecture Snapshot, How-To Ladder).
- Provided **structured layout** and want consistent rendering.
- Asked to **improve** clarity, hierarchy, or accessibility.

## Quick start

**Generate (plan → optional render)**
1. Create plan:
   - Use `references/*` to choose template and produce numbered regions with content.
2. (Optional) Render:
   - Execute `scripts/generate_infograph.py` with `--mode text` (free-form) or `--mode structured` (JSON wireframe).

**Improve (audit → revise → optional re-render)**
1. Run the “Audit Checklist” from `08_Checklist.md`.
2. Produce a revised plan and (optionally) re-render.

## Inputs
- **Text brief**: topic, audience, single takeaway, infographic type, constraints.
- **Structured layout** (optional): JSON object:
```json
{
  "title": "Kotlin Coroutines: Structured Concurrency",
  "canvas": {"width": 1600, "height": 1000},
  "regions": [
    {"id":"r1","type":"title","x":64,"y":48,"w":1472,"h":120,"text":"Kotlin Coroutines: Structured Concurrency"},
    {"id":"r2","type":"panel","x":64,"y":200,"w":720,"h":300,"label":"Problem","bullets":["Callback pyramids","Cancellation leaks"]},
    {"id":"r3","type":"diagram","x":816,"y":200,"w":720,"h":300,"label":"Parent/child scopes"},
    {"id":"r4","type":"code","x":64,"y":532,"w":1472,"h":360,"code":"// sample coroutineScope {...}"}
  ],
  "palette":"light",
  "notes":"WCAG AA; ≤80 words per panel"
}
````

## Outputs

* **Plan** (always): numbered wireframe + content (≤80 words/panel), style tokens, accessibility notes.
* **Image file(s)** (optional): PNG(s) saved to `./output/`.
* **Nano Banana prompts** (when using nanobanana engine): SAE-ALD styled natural-language prompt saved to `{basename}_{timestamp}_nanobanana_prompt.txt`.

## Core procedure

1. Read `02_Core_Principles.md` (clarity, hierarchy, flow, cognitive load, accessibility) .
2. Select **template** from `05_Templates.md` (Concept Map / Process Flow / Algorithm Breakdown / Comparison Matrix / Architecture Snapshot / How-To Ladder) .
3. Generate **numbered wireframe** with regions and labels.
4. Place content into regions; keep one takeaway; 3–5 chunks; avoid color-only semantics; add alt text .
5. Run **Checklist** from `08_Checklist.md`; adjust.
6. (Optional) Execute `scripts/generate_infograph.py` to render via Gemini (precise, layout-aware) or Nano Banana (styled, SAE-ALD).

## Engine Behavior

- **Gemini** → Structured rendering from JSON (layout-aware, region coordinates respected)
- **Nano Banana** → Uses SAE-ALD (Subject–Action–Environment–Art Style–Lighting–Details) natural-language prompts
  - Layout JSON is *flattened* into a narrative description
  - Ideal for aesthetic, brand-friendly, or conceptual infographic styles
  - Output prompt logged to `{basename}_{timestamp}_nanobanana_prompt.txt` for reproducibility

## File map

* References (modular framework) live in `references/` for **progressive disclosure** and token efficiency .
* Rendering script in `scripts/` (executed; not loaded to context) for deterministic output .

## Common issues (quick fixes)

* **Overcrowding / weak hierarchy** → reduce to one takeaway; 3–5 chunks; increase contrast/spacing .
* **Ambiguous arrows** → orthogonal connectors; label edges with verb+noun; minimize crossings .
* **Low contrast / color-only cues** → enforce WCAG AA; add icons/patterns; alt text .
* **Skill not triggering** → ensure “infographic”, “diagram”, “layout”, “template”, or “wireframe” appears in request; metadata is specific .

## See also

* `WORKFLOW.md` — step-by-step flows
* `EXAMPLES.md` — generation & improvement examples
* `TROUBLESHOOTING.md` — keys, deps, structured JSON validation