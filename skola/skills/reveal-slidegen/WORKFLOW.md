# Reveal SlideGen — WORKFLOW

**Skill:** `reveal-slidegen`  
**Version:** 1.0.0  
**Engine:** Claude Code (Nano Banana compatible)  
**Goal:** Convert structured tutorial packages into standalone Reveal.js decks.

---

## Overview

This workflow maps multi-section markdown outlines into interactive Reveal.js v5
presentations with Mermaid diagrams, syntax-highlighted code, and speaker notes.

---

## 1. Input Collection

Accept a single markdown package that can include:

- Time-coded outline tables
- Slide deck plan (visual, on-screen text, speaker notes)
- Narration or script blocks
- Demo instructions, repo trees, pitfalls, resources

> Example snippet:
>
> ```markdown
> ### 1) Time-coded Outline
> | Timestamp | Section | Description |
> | 00:00–00:20 | Intro | Welcome message |
>
> ### 2) Slide Deck Plan
> **Slide 1: Title**
> - Visual: npm, Gradle, Maven logos
> - On-screen text: Build Tools: A Practical Intro
> ```

---

## 2. Processing Logic

1. **Parse** sections/headings to identify slide order.
2. **Segment** slides: convert deck plan items into `<section data-auto-animate>`.
3. **Transform visuals**:
   - Flowcharts → Mermaid
   - CLI/code → `<pre><code class="language-x">`
4. **Extract narration** into `<aside class="notes">`.
5. **Compile** Reveal.js shell with CDN links + highlight.js + Mermaid plugin.
6. **Append appendix** containing outlines, pitfalls, resources when present.

---

## 3. Output

- Single HTML file (Reveal.js v5, black theme, fade transition).
- highlight.js `github-dark` syntax theme.
- Notes + Mermaid plugins enabled.
- Optional Appendix slide group summarizing outlines/pitfalls/resources.

Suggested output path: `slides/<topic>.html`.

---

## 4. Invocation Patterns

### Direct Claude Code

```bash
skill reveal-slidegen tutorial_outline.md > slides.html
```

### With Microlearn Chain

```bash
skill microlearn topic.md | skill reveal-slidegen > slides.html
```

### Nano Banana CLI

```bash
nb run reveal-slidegen --input tutorial_outline.md --output deck.html
```

---

## 5. Validation Checklist

- `<div class="reveal">` container present.
- highlight.js + Mermaid scripts load exactly once.
- Speaker notes exist for slides with narration.
- Title + Recap slides included.
- Appendix created when `Time-coded Outline` or `Common Pitfalls` provided.

---

## 6. Configurable Parameters

| Parameter | Description | Default |
| --------- | ----------- | ------- |
| `theme` | Reveal.js theme | `black` |
| `syntax_theme` | highlight.js theme | `github-dark` |
| `transition` | Slide animation | `fade` |
| `enable_mermaid` | Include Mermaid plugin | `true` |
| `show_appendix` | Add appendix slide group | `true` |
| `show_notes` | Render speaker notes | `true` |

---

## 7. Compatible Skills

| Skill | Purpose | Example Chain |
| ----- | ------- | ------------- |
| `microlearn` | Short-form educational text | `microlearn → reveal-slidegen` |
| `generate-infograph` | Visual infographic briefs | `generate-infograph → reveal-slidegen` |
| `api-ui-contract` | API documentation slides | `api-ui-contract → reveal-slidegen` |

---

## 8. Developer Notes

- Maintain clean HTML—no stray markdown or duplicated CDN links.
- Keep dependencies to CDN scripts/styles; no bundling required.
- Mention resulting file path or name so users can open it quickly.
- Maintainer: `@bravdigital` — License MIT — Last updated 2025-11-15.
