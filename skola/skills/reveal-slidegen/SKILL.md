---
name: reveal-slidegen
description: Generates professional Reveal.js v5 HTML presentations from structured tutorial outlines, slide plans, and narration scripts. Use when the user provides time-coded outlines, slide plans, or narration documents and wants a ready-to-present deck with speaker notes, Mermaid diagrams, and syntax-highlighted code.
---

# Reveal SlideGen

Transform tutorial specifications into polished **Reveal.js v5** presentations that are
self-contained, browser-ready, and structured for technical education.

## Quick Start

1. Provide a structured tutorial package (outline, slide plan, narration, demos, pitfalls).
2. Skill parses sections and maps them to slides with `<section data-auto-animate>`.
3. Code, CLI, and flow descriptions become **highlight.js** or **Mermaid** blocks.
4. Narration cues become `<aside class="notes">`.
5. Appendices (time-coded outline, pitfalls, resources) are added automatically when present.

See [WORKFLOW.md](WORKFLOW.md) for full processing logic.

## Input Expectations

- Markdown document that may include:
  - **Time-coded outline** tables
  - **Slide plan** with visual + on-screen text + notes
  - **Narration / script** paragraphs
  - Optional demo instructions, repo tree, pitfalls, references
- Provide files via Claude Code context or reference paths (e.g., `tutorial_outline.md`).

## Output Requirements

- Single standalone HTML file:
  - Reveal.js v5 `black` theme + `fade` transitions
  - highlight.js `github-dark` syntax theme
  - Mermaid v10 enabled globally
  - Notes plugin included and populated
- Slide flow target: 10–12 sections (Title → Concept → Tools → Demo → Recap → CTA + optional Appendix).
- Each slide uses `<section data-auto-animate>` with clear hierarchy and whitespace.
- Speaker notes draw from narration cues; appendices summarize outlines/resources when provided.

## Prompt Logic

When invoked, ensure the model:

1. Parses headings/segments to determine slide titles and ordering.
2. Converts “Visual” guidance into diagrams (Mermaid), screenshots, or code blocks.
3. Renders CLI/code snippets using `<pre><code class="language-x">`.
4. Injects `<aside class="notes">` blocks with condensed narration per slide.
5. Validates the final HTML contains `<div class="reveal">` before returning.

## Post-Processing Rules

- Always inline CDN references (`reveal.js@5`, `highlight.js@11.9`, `mermaid@10`).
- Include appendix when a time-coded outline or pitfalls list exists.
- Wrap terminal style output in `<pre class="terminal">` if noted as CLI/terminal.
- Strip leftover markdown; return valid HTML5 only.

## Configuration Defaults

| Parameter | Description | Default |
| --------- | ----------- | ------- |
| `theme` | Reveal.js theme | `black` |
| `syntax_theme` | highlight.js theme | `github-dark` |
| `transition` | Slide transition | `fade` |
| `enable_mermaid` | Load Mermaid support | `true` |
| `show_notes` | Include speaker notes plugin | `true` |
| `show_appendix` | Add appendix section when inputs exist | `true` |

## Usage Examples

See [EXAMPLES.md](EXAMPLES.md) for:
- Basic tutorial outline conversion
- Chaining with microlearn skill
- Real-world tutorial package conversion
- Custom configuration options

## Common Issues

**"Slides not rendering"**
- Verify HTML contains `<div class="reveal">` container
- Check browser console for CDN loading errors

**"Code blocks not highlighted"**
- Ensure code blocks use proper language classes
- Verify highlight.js script loaded

For complete troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Supporting Files

- [WORKFLOW.md](WORKFLOW.md) — Detailed transformation pipeline and integration notes
- [EXAMPLES.md](EXAMPLES.md) — Complete usage examples and integration patterns
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Error handling and common issues
- `scripts/generate_reveal_slidegen.py` — CLI runner for standalone execution
