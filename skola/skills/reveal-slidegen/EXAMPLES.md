# Reveal SlideGen — Usage Examples

Comprehensive examples demonstrating Reveal.js presentation generation from tutorial content.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Chained with Microlearn](#chained-with-microlearn)
- [Real-World Tutorial Conversion](#real-world-tutorial-conversion)
- [Custom Configuration](#custom-configuration)

---

## Basic Usage

### Example 1: Simple Tutorial Outline

Convert a basic tutorial outline into a Reveal.js presentation.

**Input file** (`tutorial.md`):
```markdown
# Build Tools: A Practical Intro

## Introduction
Build tools automate repetitive tasks in software development.

## Popular Tools
- npm (JavaScript)
- Maven (Java)
- Gradle (Java/Kotlin)

## Demo
Create a basic npm project and run build scripts.

## Recap
Build tools save time and reduce errors.
```

**Command:**
```bash
python skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py \
  --input tutorial.md \
  --output slides.html
```

**Output:**
```
[OK] Slide deck generated → slides.html
```

**When to use:** Simple tutorial outlines without time-coding or detailed narration.

---

## Chained with Microlearn

### Example 2: Microlearn Pipeline

Generate micro-learning content and convert to presentation slides in one workflow.

**Command:**
```bash
# Generate microlearn content, then convert to slides
cat topic.md | skill microlearn | skill reveal-slidegen > slides.html
```

**Alternative using script:**
```bash
skill microlearn docker-basics.md > microlearn-output.md
python skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py \
  --input microlearn-output.md \
  --output docker-slides.html
```

**When to use:** Creating short-form educational content that needs to be presented as slides.

---

## Real-World Tutorial Conversion

### Example 3: Complete Tutorial Package

Convert a comprehensive tutorial with time-coded outline, slide plan, narration, and demos.

**Input file** (`complete-tutorial.md`):
```markdown
# Kubernetes Basics Tutorial

## 1) Time-coded Outline

| Timestamp | Section | Description |
|-----------|---------|-------------|
| 00:00–00:20 | Intro | Welcome and overview |
| 00:20–02:00 | Concepts | What is Kubernetes? |
| 02:00–05:00 | Demo | Deploy first pod |
| 05:00–06:00 | Recap | Key takeaways |

## 2) Slide Deck Plan

### Slide 1: Title
- **Visual:** Kubernetes logo + container icons
- **On-screen text:** Kubernetes Basics: Container Orchestration
- **Notes:** Introduce Kubernetes as a container orchestration platform

### Slide 2: What is Kubernetes?
- **Visual:** Diagram showing pods, nodes, clusters
- **On-screen text:**
  - Container orchestration
  - Automated deployment
  - Self-healing infrastructure
- **Notes:** Explain the core concepts

### Slide 3: Demo - Deploy Your First Pod
- **Visual:** Terminal showing kubectl commands
- **On-screen text:**
  ```bash
  kubectl create deployment nginx --image=nginx
  kubectl get pods
  ```
- **Notes:** Walk through creating a basic deployment

## 3) Narration

Welcome to Kubernetes Basics. Today we'll explore container orchestration...
(detailed narration continues)

## 4) Common Pitfalls

- Forgetting to configure kubectl context
- Not understanding pod lifecycle
- Incorrect YAML indentation
```

**Command:**
```bash
python skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py \
  --input complete-tutorial.md \
  --output kubernetes-basics.html
```

**Expected output structure:**
- Title slide with Kubernetes branding
- Concept slides with Mermaid diagrams
- Demo slide with syntax-highlighted code blocks
- Recap slide summarizing key points
- Appendix with time-coded outline and pitfalls

**When to use:** Professional tutorial presentations with complete educational packages.

---

## Custom Configuration

### Example 4: Using Python Script with Custom Engine

Run the skill with a different engine or configuration.

**Command:**
```bash
python skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py \
  --input tutorial.md \
  --output slides.html \
  --engine nano-banana
```

**Alternative: Reading from stdin**
```bash
cat tutorial.md | python skola/skills/reveal-slidegen/scripts/generate_reveal_slidegen.py > slides.html
```

**When to use:** Integration with other tools or custom processing pipelines.

---

## Expected Output Features

All generated presentations include:

- ✅ Reveal.js v5 with `black` theme
- ✅ highlight.js syntax highlighting (`github-dark` theme)
- ✅ Mermaid v10 for diagrams
- ✅ Speaker notes plugin enabled
- ✅ Auto-animate transitions between slides
- ✅ Responsive design (mobile-friendly)
- ✅ Appendix section (when outline/pitfalls provided)

---

## Opening the Generated Presentation

After generation, open the HTML file in any modern browser:

```bash
# macOS
open slides.html

# Linux
xdg-open slides.html

# Windows
start slides.html

# Or simply drag the file into your browser
```

**Speaker notes access:** Press `S` during presentation to open speaker view.

---

## Integration Examples

### With Create-Tutorial Skill

```bash
# Generate tutorial, then create slides
skill create-tutorial api-design.md > tutorial-package.md
skill reveal-slidegen tutorial-package.md > api-design-slides.html
```

### With Extract-Udemy Skill

```bash
# Extract Udemy course content, convert to slides
skill extract-udemy https://udemy.com/course/example > course-content.md
skill reveal-slidegen course-content.md > course-slides.html
```

---

## Tips for Best Results

1. **Structure headings clearly:** Use `#`, `##`, `###` for slide hierarchy
2. **Include code blocks:** Use triple backticks with language hints
3. **Provide narration:** Add speaker notes for better presentations
4. **Use tables for timelines:** Time-coded outlines improve appendix
5. **Mark visuals:** Indicate diagrams/charts for Mermaid conversion
6. **Test locally:** Always open and review the generated HTML before sharing
