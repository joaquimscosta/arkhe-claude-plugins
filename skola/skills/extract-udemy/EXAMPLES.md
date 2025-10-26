# Usage Examples

Comprehensive examples demonstrating all features of the Udemy Course Extractor.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Content Type Selection](#content-type-selection)
- [Resource Extraction](#resource-extraction)
- [Large Course Handling](#large-course-handling)
- [Real-World Examples](#real-world-examples)

---

## Basic Usage

### Example 1: Extract Everything (Default)

Extract all content types from a course:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/data-structures-and-algorithms-java/"
```

**Output:**
```
============================================================
Udemy Course Extractor
============================================================
Course URL: https://risesmart.udemy.com/course/data-structures-and-algorithms-java/

📋 Parsing course URL...
  Site: risesmart.udemy.com
  Course: data-structures-and-algorithms-java

🔐 Initializing authentication...
  ✓ Loaded 2 cookies from cookies.json
  ✓ Authentication successful

📚 Fetching course structure...
  ✓ Course: Java Data Structures & Algorithms + LEETCODE Exercises
  ✓ Sections: 41
  ✓ Total lectures: 150

📜 Extracting course content...
  Processing 150 lectures...

  Section 1/41: Introduction
    2 lectures
    [001] ✓ Overview (Please Watch) [transcript]
    [002] ✓ Code Editor [transcript, resources(1 files)]

  Section 2/41: Big O
    11 lectures
    [003] ✓ Big O: Intro [transcript, resources(1 files)]
    [004] ✓ Big O: Worst Case [transcript]
    ...

============================================================
Extraction Complete!
============================================================
Course: Java Data Structures & Algorithms + LEETCODE Exercises

Statistics:
  Sections: 41
  Total lectures: 150
  Transcripts: 142
  Articles: 2
  Quizzes: 0
  Resources: 61
  Skipped: 89

Resource Download Statistics:
  ✓ 110 files downloaded (0.5MB)

Files created:
  udemy-research/data-structures-and-algorithms-java/README.md
  udemy-research/data-structures-and-algorithms-java/transcripts/ (142 files)
  udemy-research/data-structures-and-algorithms-java/articles/ (2 files)
  udemy-research/data-structures-and-algorithms-java/resources/ (61 catalogs)
```

**Result Structure:**
```
udemy-research/data-structures-and-algorithms-java/
├── README.md
├── transcripts/
│   ├── 001-overview-please-watch.txt
│   ├── 002-code-editor.txt
│   ├── 003-big-o-intro.txt
│   └── ... (142 total)
├── articles/
│   ├── 015-pointers.md
│   └── 150-thank-you.md
└── resources/
    ├── 002-code-editor/
    │   └── Visual-Studio-Code-Dark-Plus.jar (3.1KB)
    ├── 003-big-o-intro/
    │   └── Big-O-Notes.pdf (111KB)
    ├── 019-ll-constructor/
    │   ├── EXERCISE-LL-Constructor.txt
    │   └── SOLUTION-LL-Constructor.txt
    ├── ... (61 lecture resource directories)
    ├── 002-code-editor-resources.md
    ├── 003-big-o-intro-resources.md
    └── external-links.md
```

---

## Content Type Selection

### Example 2: Transcripts Only

Extract only video transcripts (fastest, smallest output):

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/react-complete-guide/" \
  --content-types video
```

**Use case**: Quick transcript archive for searchability

**Output:**
```
Statistics:
  Transcripts: 285
  Articles: 0
  Quizzes: 0
  Resources: 0

Files created:
  udemy-research/react-complete-guide/README.md
  udemy-research/react-complete-guide/transcripts/ (285 files)
```

### Example 3: Articles and Transcripts

Extract videos and articles, skip resources:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/python-bootcamp/" \
  --content-types video,article
```

**Use case**: Text-based content for offline reading, without large resource downloads

**Output:**
```
[001] ✓ Course Introduction [transcript]
[002] ✓ Setup Guide [article(technical_resource)]
[003] ✓ Python Basics [transcript]
[012] ✓ Coding Challenge Solution [article(coding_solution)]
...
```

### Example 4: Resources Only (Catalog Mode)

Create resource catalogs without downloading files:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/web-development-bootcamp/" \
  --content-types resource \
  --no-download-resources
```

**Use case**: Survey what resources are available before downloading

**Output:**
```
Statistics:
  Resources: 45

Files created:
  udemy-research/web-development-bootcamp/resources/ (45 catalog files)

# Each catalog file lists resources with URLs for manual download:
resources/010-html-basics-resources.md:
  - cheatsheet.pdf (250KB) - https://udemy.com/...
  - starter-code.zip (1.2MB) - https://udemy.com/...
```

---

## Resource Extraction

### Example 5: Download All Resources (Default)

Download all supplementary files (PDFs, code, etc.):

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/data-structures-and-algorithms-java/" \
  --content-types resource
```

**Before Bug Fix (2025-10-18):**
```
Statistics:
  Resources: 0  ❌ BROKEN

# No files downloaded despite 63 lectures having resources
```

**After Bug Fix (2025-10-18):**
```
Statistics:
  Resources: 61  ✅ WORKING

Resource Download Statistics:
  ✓ 110 files downloaded (0.5MB)

Files created:
  resources/002-code-editor/Visual-Studio-Code-Dark-Plus.jar
  resources/003-big-o-intro/Big-O-Notes.pdf
  resources/019-ll-constructor/EXERCISE-LL-Constructor.txt
  resources/019-ll-constructor/SOLUTION-LL-Constructor.txt
  ... (110 total files)
```

### Example 6: Limit Resource Download Size

Download only resources under 50MB:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/unreal-engine-5/" \
  --content-types resource \
  --max-resource-size 50
```

**Output:**
```
Resource Download Statistics:
  ✓ 25 files downloaded (45MB)
  ⊘ 3 files skipped (exceeded size limit)

# Large files listed in catalog for manual download
```

### Example 7: Skip Promotional Content

Extract main course content, skip promotional lectures:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/complete-web-developer/" \
  --skip-promotional
```

**Output:**
```
[001] ✓ Introduction [transcript]
[025] ⊘ Bonus: Free Course! - Promotional (skipped)
[050] ✓ JavaScript Fundamentals [transcript]
[100] ⊘ Special Offer - Promotional (skipped)
...

Statistics:
  Transcripts: 145
  Skipped: 8 (promotional)
```

---

## Large Course Handling

### Example 8: Large Course with 500+ Lectures

Extract a massive course with automatic pagination:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/complete-python-bootcamp/" \
  --content-types video,article
```

**Output:**
```
📚 Fetching course structure...
    Requesting page 1...
    Requesting page 2...
    Requesting page 3...
  ✓ Retrieved 550 curriculum items across 3 page(s)
  ✓ Course: Complete Python Bootcamp
  ✓ Sections: 35
  ✓ Total lectures: 383

# Extraction takes ~5-10 minutes with rate limiting
# Progress shown in real-time

Statistics:
  Transcripts: 375
  Articles: 8
  Skipped: 0
```

### Example 9: Resume After Interruption

If extraction is interrupted, re-run with same command:

```bash
# First run interrupted at lecture 100/300
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/large-course/"

# ^C (interrupted)

# Re-run with same command:
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/large-course/"

# Script will overwrite files (idempotent)
# Already-downloaded resources will be re-downloaded
```

**Note**: Currently not truly resumable, but re-running is safe (idempotent)

---

## Real-World Examples

### Example 10: First Run - API Discovery Workflow

When extracting from a new course, the script discovers API endpoints:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://newsite.udemy.com/course/machine-learning-course/"
```

**Output:**
```
📚 Fetching course structure...
  Resolving course slug to ID...
  ✓ Resolved 'machine-learning-course' to ID: 9876543
  Fetching course details...
  ✓ Retrieved course details
  Fetching course structure...
    Requesting page 1...
  ✓ Retrieved 150 curriculum items across 1 page(s)

# Script uses documented endpoints from API.md
# If endpoints fail, falls back to discovery
```

### Example 11: Content Analysis Before Extraction

Analyze course content types before extracting:

```bash
# Run analysis first
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/tools/analyze_content_types.py \
  "https://risesmart.udemy.com/course/data-structures-and-algorithms-java/" \
  analysis-report.json
```

**Output:**
```
============================================================
Content Type Analysis Tool
============================================================

📊 Overall Statistics:
  Total Lectures: 150
  Lectures with Transcripts: 142
  Lectures with Downloadable Resources: 63
  Lectures with Quizzes: 0
  Lectures with Coding Exercises: 3

📝 Content Types Detected:
  video: 145
  coding_exercise: 3
  article: 2

✅ Currently Extracted:
  - Video Transcripts: 142 lectures
  - Articles: 2 lectures

⚠️  Not Currently Extracted:
  - Downloadable Resources: 63 lectures have resources
  - Coding Exercises: 3 exercise lectures

💡 Implementation Recommendations:

1. [HIGH] Resource Downloader
   Description: Download and organize 63 supplementary resources
   Implementation: Already implemented in ResourceExtractor - needs activation

# Now you know what to extract!

# Extract only the valuable parts:
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/data-structures-and-algorithms-java/" \
  --content-types video,resource
```

### Example 12: Extract Quiz Data

Extract quiz questions for review:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/aws-certified-solutions-architect/" \
  --content-types quiz \
  --quiz-format yaml
```

**Output Structure:**
```yaml
# quizzes/025-section-2-quiz.yaml

quiz_id: 12345
title: "Section 2: EC2 Fundamentals Quiz"
questions:
  - question: "What is the purpose of an AMI?"
    type: "multiple-choice"
    options:
      - "Amazon Machine Image - template for EC2 instances"
      - "Amazon Memory Instance"
      - "Automated Machine Intelligence"
    correct_answer: "Amazon Machine Image - template for EC2 instances"

  - question: "Which instance type is best for compute-intensive workloads?"
    type: "multiple-choice"
    options:
      - "T2.micro"
      - "C5.large"
      - "R5.large"
    correct_answer: "C5.large"
```

### Example 13: Extract External Links

Extract all external resources mentioned in the course:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/react-complete-guide/" \
  --content-types video,article
```

**Output File:** `resources/external-links.md`

```markdown
# External Resources

Links to external resources mentioned throughout the course.

**Total Unique Resources**: 15

## GitHub Repositories

### [react-course-examples](https://github.com/instructor/react-course-examples)

**URL**: https://github.com/instructor/react-course-examples

**Mentioned in**:
- Lecture 5: Setup (transcript)
- Lecture 10: Components (article)
- Lecture 50: Advanced Patterns (transcript)

## Documentation

### [React Official Docs](https://react.dev)

**URL**: https://react.dev

**Mentioned in**:
- Lecture 3: What is React? (transcript)
- Lecture 8: JSX Deep Dive (article)
...
```

### Example 14: Custom Output Directory

Extract to a specific directory:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/data-structures-and-algorithms-java/" \
  --output-dir my-dsa-course
```

**Result:**
```
Files created:
  udemy-research/my-dsa-course/README.md
  udemy-research/my-dsa-course/transcripts/
  udemy-research/my-dsa-course/resources/
  ...
```

### Example 15: Full-Featured Extraction

Extract everything with all options enabled:

```bash
python3 arkhe-claude-plugins/skola/skills/extract-udemy/scripts/extract.py \
  "https://risesmart.udemy.com/course/complete-web-development/" \
  --content-types video,article,quiz,resource \
  --download-resources \
  --max-resource-size 200 \
  --skip-promotional \
  --quiz-format yaml \
  --output-dir web-dev-2024
```

**Output:**
```
============================================================
Extraction Complete!
============================================================
Course: Complete Web Development Bootcamp

Statistics:
  Sections: 45
  Total lectures: 420
  Transcripts: 380
  Articles: 25
  Quizzes: 8
  Resources: 95
  Skipped: 12 (promotional)

Resource Download Statistics:
  ✓ 150 files downloaded (125MB)
  ⊘ 5 files skipped (exceeded 200MB limit)

Files created:
  udemy-research/web-dev-2024/README.md
  udemy-research/web-dev-2024/transcripts/ (380 files)
  udemy-research/web-dev-2024/articles/ (25 files)
  udemy-research/web-dev-2024/quizzes/ (8 files)
  udemy-research/web-dev-2024/resources/ (95 catalogs, 150 downloaded files)
```

---

## Performance Tips

### Fastest Extraction
```bash
# Transcripts only, skip everything else
--content-types video
```

### Most Complete Extraction
```bash
# Everything with downloads
--content-types video,article,quiz,resource --download-resources
```

### Minimal Disk Usage
```bash
# Catalogs only, no file downloads
--content-types video,article,quiz --no-download-resources
```

### Handling Rate Limits
```python
# If you get rate limited, increase delay in extract.py:
time.sleep(1.0)  # Instead of 0.5
```

---

## What Each Content Type Produces

| Content Type | Files Created | Typical Size | Use Case |
|--------------|---------------|--------------|----------|
| `video` | `transcripts/XXX-title.txt` | 2-10KB per file | Searchable text, notes, review |
| `article` | `articles/XXX-title.md` | 5-20KB per file | Reference guides, bonus content |
| `quiz` | `quizzes/XXX-title.yaml` | 1-5KB per file | Self-testing, exam prep |
| `resource` | `resources/XXX-*/files` + catalogs | Varies widely | Code files, PDFs, cheat sheets |

---

## See Also

- [SKILL.md](SKILL.md) - Core usage guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Error handling
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details
