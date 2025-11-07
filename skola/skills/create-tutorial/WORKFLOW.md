# Create Tutorial Workflow

This document provides a step-by-step process for generating complete tutorial packages (blog + video).

---

## Overview

The tutorial creation process follows 7 key steps:

1. **Intake** - Gather information and parse requirements
2. **Mode Selection** - Apply adaptive logic to determine depth
3. **Outline** - Draft structure using templates
4. **Blog Article** - Generate article.md
5. **Video Package** - Create script, chapters, thumbnail brief
6. **SEO & Metadata** - Generate seo.yaml
7. **Validation** - Run validation script

Each step has specific inputs, outputs, and validation checkpoints.

---

## Step 1: Intake

### Goal
Understand what tutorial to create and gather all necessary context.

### Actions

1. **Read provided source code** (if applicable)
   ```
   Use tools: Read, Grep, Glob
   - Read relevant source files
   - Search for key patterns or functions
   - Understand the codebase structure
   ```

2. **Analyze user request**
   - What is the topic?
   - Is there a specific language/framework mentioned?
   - Are there any files or repos linked?
   - What is the implied scope?

3. **Ask clarifying questions** (max 3, only if critical details are missing)
   - **Target language/framework** (if not obvious)
     - "Is this for Python, JavaScript, Java, or Kotlin?"
   - **Audience level** (if ambiguous)
     - "Is your audience beginner, intermediate, or advanced?"
   - **Desired depth** (only if very unclear)
     - "Do you want a quick intro (5-10 min), a detailed tutorial (30-60 min), or a multi-part series?"

   **When NOT to ask:**
   - Language is clear from code or context
   - User already specified "beginner tutorial" or "quick intro"
   - Request is specific enough to infer answers

### Outputs
- Clear understanding of:
  - Topic/feature to teach
  - Target language and framework
  - Audience level
  - Whether code is provided or needs to be created

### Validation Checkpoint
- [ ] Topic is clearly defined
- [ ] Language/framework is known
- [ ] Audience level is determined (beginner/intermediate/advanced)
- [ ] Any provided code has been read and understood

---

## Step 2: Mode Selection

### Goal
Determine the appropriate tutorial depth using adaptive logic.

### Decision Logic

Apply keyword analysis and input length assessment:

#### Quick Start Mode
**Triggers:**
- Keywords: "intro", "quick", "overview", "beginner", "example", "basics"
- Short user prompt (<100 words)
- Single-feature or narrow topic
- User explicitly requests "quick" tutorial

**Select when:** User wants a fast, practical introduction

---

#### Deep Dive Mode
**Triggers:**
- Keywords: "detailed", "explain", "deep dive", "comprehensive", "walkthrough", "guide"
- Medium prompt (100-300 words)
- Intermediate concept with multiple aspects
- User wants thorough understanding

**Select when:** User wants complete understanding with theory + practice

---

#### Workshop Series Mode
**Triggers:**
- Keywords: "series", "advanced", "build project", "from scratch", "complete course", "multi-part"
- Long prompt (>300 words) or explicit series request
- Complex system with multiple dependencies
- User mentions "part 1", "series", or multiple related topics

**Select when:** User wants cumulative, comprehensive learning journey

---

### Default
If unclear after analysis, **default to Deep Dive mode** (most versatile).

### Actions
1. Analyze user input for keywords
2. Measure input length
3. Assess topic complexity
4. Make mode selection
5. **State the choice explicitly** in your initial response:
   - "I'll create a **Quick Start** tutorial (5-10 min)..."
   - "I'll create a **Deep Dive** tutorial (45 min)..."
   - "I'll create a **Workshop Series** (3 parts)..."

### Outputs
- Selected mode (Quick Start | Deep Dive | Workshop)
- Justification for selection
- Expected time/length

### Validation Checkpoint
- [ ] Mode is selected based on explicit criteria
- [ ] User is informed of the mode choice
- [ ] Time estimate is provided

---

## Step 3: Outline

### Goal
Create a structural outline following the appropriate template.

### Actions

1. **Select template**
   - Reference `templates/article_template.md`
   - Adapt section count to selected mode:
     - Quick Start: 4 sections (What You'll Learn, Why, Example, Challenge, Summary)
     - Deep Dive: 8 sections (full template)
     - Workshop: Multiple parts, each following Deep Dive structure

2. **Draft outline**
   ```markdown
   ## 1. What You'll Build
   - [Specific outcome 1]
   - [Specific outcome 2]

   ## 2. Concept Overview
   - [Key concept explanation]

   ## 3. Minimal Example
   - [Code snippet plan]

   ## 4. Guided Steps
   ### Step 1: [Action]
   ### Step 2: [Action]
   ### Step 3: [Action]

   ## 5. Challenge
   - [Exercise idea]

   ## 6-8. Troubleshooting, Summary, Next Steps
   ```

3. **Ensure each section includes:**
   - Concept introduction
   - Runnable code example
   - Explanation of what's happening
   - Validation/checkpoint (where appropriate)

### Outputs
- Structured outline with section titles and bullet points
- Code examples identified (to be written in next step)

### Validation Checkpoint
- [ ] Outline follows template structure
- [ ] Each section has a clear purpose
- [ ] Progression is logical (simple → complex)
- [ ] Includes challenges and checkpoints

---

## Step 4: Blog Article

### Goal
Generate the complete `article.md` with all content filled in.

### Actions

1. **Use the outline from Step 3** as scaffolding

2. **Write each section following pedagogical principles:**
   - **Lead with code** - Show runnable example first
   - **Explain after** - Break down what the code does
   - **Progress incrementally** - Each step builds on previous
   - **Include output** - Show expected results
   - **Add checkpoints** - Regular validation points

3. **Code quality requirements:**
   - All code must be **runnable** (or clearly marked as pseudo-code)
   - Include language tags in code fences (```python, ```javascript, etc.)
   - Show expected output after code blocks
   - Add comments for non-obvious parts

4. **Formatting requirements:**
   - Numbered sections (`## 1.`, `## 2.`, etc.)
   - Tips in blockquotes (`> 💡 Tip:`)
   - Warnings in blockquotes (`> ⚠️ Warning:`)
   - Collapsible solutions: `<details><summary>Solution</summary>...</details>`
   - Progress checks: `--- Progress Check ---` with checkboxes

5. **Required sections (customize based on mode):**
   - What You'll Build/Learn (with clear outcomes)
   - Concept Overview (the "why")
   - Minimal Runnable Example (copy-paste ready)
   - Guided Steps (incremental implementation)
   - Challenge (hands-on exercise with solution)
   - Troubleshooting (common errors + fixes)
   - Summary (recap with checkmarks)
   - Next Steps (where to go from here)

### Outputs
- Complete `article.md` file
- All code tested (or verified as logical)
- All sections filled with quality content

### Validation Checkpoint
- [ ] Article follows template structure
- [ ] All code blocks have language tags
- [ ] Expected outputs are shown
- [ ] Challenges have collapsible solutions
- [ ] Troubleshooting section covers common issues
- [ ] Summary recap includes checkmarks
- [ ] Next steps provide clear direction

---

## Step 5: Video Package

### Goal
Create YouTube-ready video script, chapters, and thumbnail brief.

### Actions

#### 5.1: Video Script (video_script.md)

Reference `templates/video_script_template.md` and create:

1. **Hook (10-20 seconds)**
   - Attention-grabbing opening
   - State the outcome clearly
   - Example: "In the next 10 minutes, you'll build a REST API with auto-generated docs."

2. **Agenda (20-30 seconds)**
   - List 3-4 things viewers will learn
   - Keep on screen briefly

3. **Sections (match article structure)**
   - Context & Why (1-2 min)
   - Prerequisites (30 sec - defer details to description)
   - Main content sections (demo + explanation)
   - Add timing estimates

4. **Stage directions:**
   - Screen capture cues ("Switch to terminal")
   - B-roll suggestions ("Show diagram of architecture")
   - On-screen text overlays ("Key term: API endpoint")

5. **Recap (1 min)**
   - Summarize key achievements
   - Show final working result

6. **Call to Action (30-45 sec)**
   - Like, subscribe, comment
   - Mention next video or related content
   - Direct to resources in description

7. **Outro (15 sec)**
   - Closing statement
   - End card placeholders

**Pacing notes:**
- Hook/Agenda: Fast
- Explanations: Moderate
- Demos: Moderate (can speed up in post)
- Recap/CTA: Fast

#### 5.2: Chapters (chapters.json)

Create timestamp-based chapter markers:

1. **Extract key sections** from video script
2. **Estimate timings** based on content density
   - Hook: 0:00
   - Agenda: 0:20
   - Concept: 1:00
   - Implementation starts: 2:30
   - Major milestones: every 2-3 min
   - Recap: near end

3. **Format as JSON array:**
   ```json
   [
     {"time": "00:00", "title": "Hook & Outcome"},
     {"time": "00:20", "title": "What We'll Cover"},
     {"time": "02:30", "title": "Building Feature X"}
   ]
   ```

4. **Keep chapter titles concise** (under 50 chars)

#### 5.3: Thumbnail Brief (thumb_brief.md)

Reference `templates/thumbnail_brief_template.md` and specify:

1. **Visual concepts** (1-3 ideas)
   - Primary concept (e.g., "Split screen: before/after")
   - Alternative concepts if needed

2. **Text overlays:**
   - Primary text: 2-5 words max
   - Example: "FastAPI in 10 Min"
   - Font guidance: Bold, high contrast

3. **Color palette:**
   - Primary color (vibrant, stands out)
   - Secondary color (background)
   - Accent color (text highlight)
   - Ensure 4.5:1 contrast ratio minimum

4. **Composition:**
   - Layout structure (left/right split, centered, etc.)
   - Focal point
   - Rule of thirds application

5. **Platform considerations:**
   - Must be readable at 200px width (mobile)
   - High contrast for visibility
   - No text too small

### Outputs
- `video_script.md` - Complete shooting script
- `chapters.json` - Timestamp markers
- `thumb_brief.md` - Thumbnail design specification

### Validation Checkpoint
- [ ] Video script includes hook, agenda, sections, recap, CTA
- [ ] Script has stage directions and timing estimates
- [ ] Chapters align with video script sections
- [ ] Chapter timestamps are in MM:SS format
- [ ] Thumbnail brief specifies visual concept, text, colors
- [ ] Thumbnail text is under 5 words

---

## Step 6: SEO & Metadata

### Goal
Generate optimized metadata for discoverability.

### Actions

Reference `templates/seo_template.yaml` and create:

1. **Title optimization:**
   - Include primary keyword
   - Under 60 characters
   - Compelling and clear
   - Example: "Build a REST API with FastAPI in 10 Minutes"

2. **Slug creation:**
   - URL-friendly version of title
   - Lowercase, hyphens, no special chars
   - Example: "build-rest-api-fastapi-10-minutes"

3. **Description (150-160 chars):**
   - Include key benefit
   - Add call to action
   - Use target keyword naturally
   - Example: "Learn to build a production-ready REST API with FastAPI. Includes validation, docs, and deployment. Perfect for Python developers."

4. **Keywords (3-5):**
   - Primary: Main topic (e.g., "fastapi tutorial")
   - Secondary: Related terms (e.g., "python rest api")
   - Long-tail: Specific phrases (e.g., "fastapi beginners guide")

5. **Tags (8-12):**
   - Language: python, javascript, java, kotlin
   - Framework: fastapi, react, spring
   - Topic: kubernetes, docker, cloud, ai
   - Level: beginner, intermediate, advanced
   - Type: tutorial, guide, demo
   - Specific tools: kubectl, npm, etc.

6. **Additional metadata:**
   - `reading_time_min`: Estimated reading time
   - `target_audience`: Who this is for
   - `difficulty`: Skill level required
   - `code_languages`: Array of languages used
   - `technologies`: Array of tools/platforms

7. **YouTube-specific (if video):**
   - `youtube.tags`: Array of video tags
   - `youtube.category_id`: 28 (Science & Technology)
   - `youtube.playlist`: Playlist ID if part of series
   - `hashtags`: Social media hashtags

### Outputs
- `seo.yaml` - Complete SEO metadata file

### Validation Checkpoint
- [ ] Title is under 60 characters
- [ ] Description is 150-160 characters
- [ ] 3-5 primary keywords identified
- [ ] 8-12 tags selected
- [ ] Reading time estimated
- [ ] Target audience specified
- [ ] All required YAML fields populated

---

## Step 7: Validation

### Goal
Verify all outputs meet quality standards.

### Actions

#### 7.1: Manual Review

Check each file for:

1. **article.md:**
   - [ ] All sections present and complete
   - [ ] Code blocks have language tags
   - [ ] Expected outputs shown
   - [ ] Challenges have solutions
   - [ ] No broken internal links
   - [ ] Markdown renders correctly

2. **video_script.md:**
   - [ ] Hook is compelling
   - [ ] Sections have timing estimates
   - [ ] Stage directions are clear
   - [ ] CTA is present
   - [ ] Script is natural/conversational

3. **chapters.json:**
   - [ ] Valid JSON syntax
   - [ ] Times are in MM:SS format
   - [ ] Times are sequential
   - [ ] Chapter titles are concise

4. **seo.yaml:**
   - [ ] Valid YAML syntax
   - [ ] All required fields present
   - [ ] Title under 60 chars
   - [ ] Description 150-160 chars
   - [ ] Keywords and tags appropriate

5. **thumb_brief.md:**
   - [ ] Visual concept is clear
   - [ ] Text overlay under 5 words
   - [ ] Color palette specified
   - [ ] Readable at 200px width

#### 7.2: Automated Validation (Optional)

Run validation script:

```bash
python3 scripts/validate_tutorial.py article.md video_script.md
```

The script checks for:
- Required sections in article.md
- Required elements in video_script.md
- Valid JSON/YAML syntax
- Common formatting issues

**Exit codes:**
- `0` - All checks passed
- `1` - Warnings (non-critical issues)
- `2` - Errors (critical issues)

Fix any reported issues and re-run.

#### 7.3: Consistency Check

Verify consistency across files:
- [ ] Tutorial title matches across all files
- [ ] Topic/language consistent
- [ ] Time estimates align (reading time ≈ video length)
- [ ] SEO keywords match article content
- [ ] Video chapters align with article sections

### Outputs
- All files validated and error-free
- Validation report (if using script)

### Validation Checkpoint
- [ ] All manual checks passed
- [ ] Validation script (if run) exits with code 0
- [ ] Consistency verified across files
- [ ] Ready for delivery

---

## Step 8: Deliver

### Goal
Provide files to user with clear documentation.

### Actions

1. **Organize files** in appropriate directory:
   ```
   tutorials/
     [tutorial-slug]/
       article.md
       video_script.md
       chapters.json
       seo.yaml
       thumb_brief.md
   ```

2. **Provide summary** to user:
   ```
   ✅ Tutorial created: [Title]

   Mode: [Quick Start | Deep Dive | Workshop]
   Language: [Python | JavaScript | Java | Kotlin]
   Topic: [Cloud | Kubernetes | Docker | AI | ...]
   Audience: [Beginner | Intermediate | Advanced]
   Time: [X minutes]

   Files generated:
   - article.md (blog tutorial)
   - video_script.md (YouTube script)
   - chapters.json (video chapters)
   - seo.yaml (metadata)
   - thumb_brief.md (thumbnail design)

   Next steps:
   - Review article.md for accuracy
   - Customize video_script.md for your style
   - Share thumb_brief.md with designer
   - Publish and promote!
   ```

3. **Highlight any customization needs:**
   - Placeholder values that need filling
   - Code examples that should be tested
   - Links that need updating

### Outputs
- Complete tutorial package
- Summary message with file list
- Customization notes

---

## Common Workflow Variations

### Variation 1: Article Only (No Video)

**Skip:**
- Step 5.1: Video script
- Step 5.2: Chapters
- Step 5.3: Thumbnail brief

**Keep:**
- Steps 1-4: Intake through Blog Article
- Step 6: SEO (but omit video-specific fields)
- Step 7: Validation (article + SEO only)

---

### Variation 2: Video Only (No Blog)

**Skip:**
- Step 4: Blog Article (or create minimal outline)

**Focus on:**
- Step 5: Video package (script, chapters, thumbnail)
- Step 6: SEO (video-specific metadata)

**Note:** Consider creating a short blog post as YouTube description text.

---

### Variation 3: Workshop Series

**Repeat** Steps 3-7 for each part:
- Part 1: Fundamentals (Quick Start or Deep Dive)
- Part 2: Intermediate concepts (Deep Dive)
- Part 3: Advanced integration (Deep Dive)
- (Optional Part 4-5)

**Additional considerations:**
- **Cross-reference** between parts
- **Consistent branding** in thumbnails
- **Series metadata** in SEO (series name, part number)
- **Playlist** for video series
- **Progress tracking** across parts

---

## Tools & Commands Reference

### Reading Code
```bash
# Read specific file
Read file_path

# Search for pattern
Grep pattern="function_name" path="src/"

# Find files
Glob pattern="**/*.py"
```

### Creating Files
```bash
# Write new file
Write file_path="tutorials/article.md" content="..."

# Edit existing file
Edit file_path="tutorials/article.md" old_string="..." new_string="..."
```

### Validation
```bash
# Run validation script
python3 scripts/validate_tutorial.py article.md video_script.md
```

---

## Troubleshooting the Workflow

### Issue: User request is too vague

**Symptom:** Can't determine topic, language, or depth
**Solution:** Ask clarifying questions (Step 1)
**Max:** 3 questions, make them concise

---

### Issue: Code examples don't work

**Symptom:** Syntax errors, logic issues
**Solution:**
- Verify code logic before including
- Test with language-specific validators
- Include error handling in examples
- Show expected output to validate

---

### Issue: Tutorial too long/complex

**Symptom:** Output exceeds time estimate or feels overwhelming
**Solution:**
- Re-evaluate mode selection (maybe Quick Start instead of Deep Dive)
- Use collapsible `<details>` sections for optional content
- Move advanced topics to "Next Steps" section
- Break into Workshop Series if necessary

---

### Issue: Mode selection unclear

**Symptom:** User input doesn't clearly match any mode
**Solution:**
- Default to **Deep Dive**
- State assumption explicitly to user
- Allow user to request different depth if needed

---

### Issue: Validation script fails

**Symptom:** Script exits with code 2 (errors)
**Solution:**
- Read error messages carefully
- Check for missing required sections
- Verify JSON/YAML syntax
- Re-run after fixes

---

## Workflow Checklist (Quick Reference)

Copy this checklist for each tutorial creation:

```
Tutorial: [Topic Name]
Mode: [Quick Start | Deep Dive | Workshop]

[ ] Step 1: Intake
    [ ] Read source code (if provided)
    [ ] Ask clarifying questions (max 3)
    [ ] Understand topic, language, audience

[ ] Step 2: Mode Selection
    [ ] Analyze keywords and input length
    [ ] Select mode with justification
    [ ] State choice to user

[ ] Step 3: Outline
    [ ] Select appropriate template
    [ ] Draft section structure
    [ ] Plan code examples

[ ] Step 4: Blog Article
    [ ] Write all sections
    [ ] Ensure code is runnable
    [ ] Add challenges with solutions
    [ ] Include troubleshooting
    [ ] Add summary and next steps

[ ] Step 5: Video Package
    [ ] Write video script with hook/CTA
    [ ] Create chapter markers
    [ ] Write thumbnail brief

[ ] Step 6: SEO & Metadata
    [ ] Optimize title (<60 chars)
    [ ] Write description (150-160 chars)
    [ ] Select keywords and tags
    [ ] Complete seo.yaml

[ ] Step 7: Validation
    [ ] Manual review all files
    [ ] Run validation script
    [ ] Check consistency across files
    [ ] Fix any issues

[ ] Step 8: Deliver
    [ ] Organize files
    [ ] Provide summary to user
    [ ] Note any customization needs
```

---

## Version History

- **v1.0.0** - Initial workflow documentation
