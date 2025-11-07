---
name: microlearn
description: Generates microlearning content (short video scripts, infographic briefs, micro-blogs) for programming, software engineering, cloud/Kubernetes/Docker/DevOps, and AI topics with automatic multilingual output (English, Kriolu/KEA, Portuguese). Use when the user requests short-form learning assets derived from code or topics, or repurposing long tutorials into micro-lessons. Includes SEO metadata and thumbnail briefs.
allowed-tools: Read, Grep, Glob, Write
---

# Microlearn

Produce concise, high-impact microlearning assets for developer education:
- **Short video scripts** (YouTube Shorts/TikTok/Reels, ~30–90s)
- **Infographic briefs** (IG/LinkedIn/Twitter/X)
- **Micro-blogs** (100–250 words)
- **SEO metadata** and **thumbnail briefs**

## When to Use
- Turn a programming/AI concept or code snippet into a micro-lesson
- Repurpose an existing long tutorial into multiple short units
- Create social-first learning artifacts (video/infographic/micro-blog)

## Automatic Language Mode
- Detect language from request or environment; default **English**.
- Supported: **English (en)**, **Kriolu / Kabuverdianu (kea)**, **Portuguese (pt)**
- Always label the output language at the top (e.g., `Language: Kriolu (KEA)`).
- If user asks for multiple languages, generate **parallel outputs** in order: EN → KEA → PT.

## Formats (choose any/all)
- `video_script.md` — Hook → Concept → Demo/Visual → Takeaway → CTA
- `infographic_brief.md` — Headline → Visual Metaphor → 3–5 Facts → Color/Typeface → Layout notes
- `micro_blog.md` — ≤250 words, code or visual anchor, 1-sentence takeaway
- `seo.yaml` — title/slug/description/keywords/tags
- `thumb_brief.md` — 1–3 visual concepts + 2–5 word overlay text

## Core Principles (microlearning)
- **One concept per unit**; ruthless scoping
- **Timebox**: 30–90 seconds (or ≤150 words)
- **Show, then tell**: runnable code/visual anchor first
- **Retrieval cues**: recap line + CTA
- **Continuity**: link to the next micro-lesson

## Supported Topics & Stacks
- **Languages**: Python, JavaScript, Java, Kotlin
- **Domains**: Cloud, Kubernetes, Docker, CI/CD, tests, observability, security, AI/LLMs

## Workflow (high level)
1. **Intake**: Read code/topic; if ambiguous, ask ≤3 targeted questions (audience level, platform, depth).
2. **Mode**: quick unit (~60s) or chain (series of 3–5 units).
3. **Draft**: Use template in `assets/templates/micro_lesson_template.md`.
4. **Localize**: Auto-generate in requested language(s); adapt idioms & tone.
5. **Extras**: Generate `seo.yaml` and `thumb_brief.md` if video or social.
6. **Validate**: (optional) run `scripts/validate_microlesson.py`.

## Output Files (suggested names)
- `video_script.md`, `infographic_brief.md`, `micro_blog.md`, `seo.yaml`, `thumb_brief.md`

## Style & Tone
- Mentor-like, clear, encouraging
- Use short sentences, bold anchors, and code comments with expected output
- For Kriolu/KEA & Portuguese: prefer natural, informal register; keep tech terms in English when common (e.g., "container", "pod", "commit") unless strong localized term exists

## Examples
See [EXAMPLES.md](EXAMPLES.md)

## Troubleshooting
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## References
- [MICROLEARNING_FOUNDATIONS.md](references/MICROLEARNING_FOUNDATIONS.md)

## Version
- v1.0.0 – Initial release
