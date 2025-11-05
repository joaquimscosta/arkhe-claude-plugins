---
name: create-tutorial
description: Creates developer tutorials as blog articles and YouTube video packages from code or technical topics. Automatically adapts tutorial depth (Quick Start, Deep Dive, or Workshop) based on user input. Targets Python, JavaScript, Java, Kotlin for cloud, Kubernetes, Docker, AI, and general software topics. Produces Markdown articles, video scripts, SEO metadata, chapters, and thumbnail briefs. Use when user wants to create tutorials, write technical content, turn code into learning materials, or generate YouTube educational content.
allowed-tools: Read, Grep, Glob, Write
---

# Create Tutorial

Transform code and technical topics into high-quality developer tutorials with both **blog articles** and **YouTube video packages**. Uses adaptive depth logic to automatically select the right scope and format.

## When to Use This Skill

Use this skill when the user:
- Wants to turn source code or a repo into a tutorial
- Needs to create a **YouTube tutorial** with script, chapters, and thumbnail
- Asks to write a technical blog post or article
- Mentions creating tutorials for cloud/Kubernetes/Docker/AI topics
- Needs tutorial content in **Python, JavaScript, Java, or Kotlin**
- Wants to plan a tutorial series or workshop

## What This Skill Creates

This skill can generate any combination of:

1. **Blog Article (article.md)** - Complete Markdown tutorial with runnable code, challenges, and checkpoints
2. **Video Script (video_script.md)** - YouTube-ready script with hook, sections, B-roll cues, and CTA
3. **Chapter Markers (chapters.json)** - Timestamp-based video chapters
4. **SEO Metadata (seo.yaml)** - Title, description, keywords, tags, reading time
5. **Thumbnail Brief (thumb_brief.md)** - Visual concepts, text overlays, color guidance

## Quick Start

1. **Provide input**: Share code files, repo URL, or topic description
2. **Clarify if needed**: Skill will ask up to 3 questions if target audience/depth is unclear
3. **Auto-select mode**: Skill detects Quick Start, Deep Dive, or Workshop based on keywords
4. **Generate outputs**: Receive blog article and/or video package
5. **Validate**: Optional validation script checks structure and completeness

## Adaptive Depth Logic

This skill automatically selects the appropriate tutorial depth based on your input.

### 🔹 Quick Start Mode

**Triggers:**
- Keywords: *"intro", "quick", "overview", "beginner", "example"*
- Short prompt (<100 words)
- Narrow/single-feature topic

**Style:**
- 3–5 concise sections
- Immediate runnable example
- Minimal theory, fast application
- One short challenge
- **Time:** 5–10 minutes

**Example Topics:**
- "Quick intro to Python enumerate"
- "5-minute Docker container example"
- "JavaScript async/await basics"

---

### 🔸 Deep Dive Mode

**Triggers:**
- Keywords: *"detailed", "explain", "deep dive", "comprehensive", "walkthrough"*
- Medium prompt (100–300 words)
- Intermediate concept

**Style:**
- 5–8 structured sections
- Theory + practical walkthrough + error handling
- 2–3 challenges with reflection
- Conceptual understanding emphasis
- **Time:** 30–60 minutes

**Example Topics:**
- "Building a REST API with FastAPI"
- "Kubernetes Ingress with Java Spring Boot"
- "React Context API explained"

---

### 🔶 Workshop Series Mode

**Triggers:**
- Keywords: *"series", "advanced", "build project", "from scratch", "complete course"*
- Long/multi-part request (>300 words)
- Complex system with multiple dependencies

**Style:**
- Multi-part sequence (3–5 modules)
- Each part: concept + code + exercise + reflection
- Mastery and cumulative learning
- Experimentation and customization
- **Time:** 90+ minutes total

**Example Topics:**
- "React State Management series"
- "End-to-end Kubernetes deployment"
- "Building a full-stack app from scratch"

---

**Default:** If unclear, defaults to **Deep Dive** mode.

## Target Languages & Topics

### Languages
- **Python** - FastAPI, Flask, Django, CLI tools, data science
- **JavaScript** - React, Node.js, Express, Next.js, frontend
- **Java** - Spring Boot, microservices, enterprise apps
- **Kotlin** - Android, backend, multiplatform

### Topics
- **Cloud** - AWS, GCP, Azure, serverless, cloud-native
- **Kubernetes** - Deployments, Services, Ingress, StatefulSets, operators
- **Docker** - Containerization, Compose, multi-stage builds
- **CI/CD** - GitHub Actions, GitLab CI, Jenkins, testing pipelines
- **AI/LLMs** - Integrations, prompt engineering, RAG, agents
- **Security** - Authentication, authorization, secrets management
- **Observability** - Logging, metrics, tracing, monitoring

## Writing Principles

### Core Philosophy
Transform complex topics into confidence through applied learning. Move learners from *confused → curious → confident*.

### Structure
- **Lead with runnable code** - Show first, explain after
- **Progress incrementally** - Simple → advanced
- **Include mistakes** - Intentional debugging examples
- **Plain language** - Mentor-like, not academic
- **Frequent validation** - Progress checkpoints
- **Clear takeaways** - Reinforce key concepts

### Format Requirements
- Numbered sections (`## 1. Introduction`)
- Syntax-highlighted code blocks with expected outputs
- Tips in blockquotes (`> 💡 Tip`, `> ⚠️ Warning`)
- Progress checkpoints: `--- Progress Check ---`
- Collapsible solutions: `<details><summary>Solution</summary>...</details>`
- Always end with **Summary** and **Next Steps**

## Output Formats

### Blog Article (article.md)

Complete Markdown tutorial with:
- H1 title with metadata (audience, time, prerequisites)
- Numbered sections following pedagogical structure
- Runnable code blocks with language tags
- Expected output comments
- Tips, warnings, and pro tips
- Progress checkpoints
- Challenges with collapsible solutions
- Troubleshooting section
- Summary and next steps

**Structure:**
1. What You'll Build/Learn
2. Concept Overview (the "Why")
3. Minimal Runnable Example
4. Guided Steps
5. Variations (optional)
6. Challenge
7. Troubleshooting & Common Pitfalls
8. Summary & Next Steps

### Video Script (video_script.md)

YouTube-ready script with:
- **Hook** (10–20s) - Grab attention, state outcome
- **Agenda** - What viewers will learn
- **Sections** - Match article structure with:
  - Stage directions (screen capture, B-roll)
  - On-screen text cues
  - Timing estimates
- **Callouts** - Key points to emphasize
- **Recap** - Summarize learning
- **CTA** - Subscribe, comment, next video
- **End cards** - Suggestions for related content

### Chapters (chapters.json)

JSON array of timestamp markers:
```json
[
  {"time": "00:00", "title": "Hook & Outcome"},
  {"time": "00:30", "title": "Prerequisites & Setup"},
  {"time": "02:15", "title": "Core Concept Explained"},
  {"time": "05:40", "title": "Hands-on Demo"},
  {"time": "08:20", "title": "Common Pitfalls"},
  {"time": "10:00", "title": "Recap & Next Steps"}
]
```

### SEO Metadata (seo.yaml)

```yaml
title: "Practical title under 60 chars"
slug: "url-friendly-slug"
description: "Compelling 150-160 char description for search results"
keywords: ["primary", "secondary", "tertiary"]
tags: ["python", "kubernetes", "tutorial"]
reading_time_min: 12
target_audience: "intermediate developers"
difficulty: "intermediate"
```

### Thumbnail Brief (thumb_brief.md)

Visual guidance for designers:
- **Concepts** - 1–3 bold visual ideas
- **Text overlays** - 2–5 words maximum
- **Color palette** - High contrast, readable at 200px
- **Composition** - Rule of thirds, focal point
- **Platform notes** - YouTube mobile vs desktop considerations

## Execution Logic

When generating a tutorial:

1. **Read source code** (if provided) using Read, Grep, Glob tools
2. **Ask clarifying questions** (max 3) only if critical details missing:
   - Target language/framework
   - Audience level (beginner/intermediate/advanced)
   - Desired depth (or let adaptive logic decide)
3. **Detect mode** using keyword analysis and input length
4. **Select template** (Quick Start / Deep Dive / Workshop)
5. **Draft outline** following template structure
6. **Generate article.md** with all pedagogical elements
7. **Create video package** (script, chapters, thumbnail) if requested
8. **Generate SEO metadata** for discoverability
9. **Validate outputs** using validation script (optional)

## Examples

See [EXAMPLES.md](EXAMPLES.md) for complete, production-ready demonstrations of each mode:

- **Quick Start** (5-10 min): Python `enumerate()` - Shows concise tutorial structure with minimal theory, immediate runnable code, and one challenge
- **Deep Dive** (45 min): FastAPI REST API - Demonstrates comprehensive tutorial with theory, guided steps, variations, troubleshooting, and video package
- **Workshop Series** (90 min): React State Management - Illustrates multi-part progressive learning with 4 interconnected tutorials building cumulative understanding

Each example includes complete output files: article.md, video_script.md, chapters.json, seo.yaml, and thumb_brief.md to serve as reference templates.

---

## File Locations

Generated files are saved in the current working directory (or a `tutorials/` subdirectory if requested).

**Default filenames:**
- `article.md` - Blog tutorial
- `video_script.md` - YouTube script
- `chapters.json` - Video chapters
- `seo.yaml` - SEO metadata
- `thumb_brief.md` - Thumbnail brief

**Naming convention:** Include language/topic for clarity (e.g., `kubernetes-ingress-python-fastapi-article.md`).

## Common Issues

### Ambiguous Scope
**Symptom:** Unclear what depth or format to use
**Solution:** Ask the 3 clarifying questions (language, audience, depth)

### Output Too Long/Complex
**Symptom:** Tutorial feels overwhelming
**Solution:** Switch to Quick Start mode or use collapsible `<details>` blocks

### Missing Runnable Code
**Symptom:** No concrete examples
**Solution:** Always include minimal runnable snippet first; verify it works

### Audience Mismatch
**Symptom:** Tutorial too basic/advanced for intended readers
**Solution:** Ask clarifying questions and adjust tone/pace accordingly

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete guide.

## Examples

See [EXAMPLES.md](EXAMPLES.md) for detailed real-world examples including:
- Quick Start: Docker + Python FastAPI (5 min)
- Deep Dive: Kubernetes Ingress + Java Spring (45 min)
- Workshop: React + Node + K8s deployment (3-part series)

## Related Files

- [WORKFLOW.md](WORKFLOW.md) - Step-by-step implementation guide
- [EXAMPLES.md](EXAMPLES.md) - Complete usage examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and fixes
- [templates/](templates/) - Output templates for all formats
- [scripts/validate_tutorial.py](scripts/validate_tutorial.py) - Validation script

## Requirements

- **Claude Code**: Compatible with skill system
- **Python** (optional): For validation script (3.8+)
- **Tools**: Read, Grep, Glob, Write

No authentication or external APIs required.
