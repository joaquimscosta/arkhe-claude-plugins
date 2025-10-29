# Udemy Course Extractor: Detailed Workflow

This document provides a detailed step-by-step breakdown of the extraction process.

For quick start instructions, see [SKILL.md](SKILL.md).

## Overview

The extraction process follows 5 main steps:

1. **Authenticate** - Load session cookies
2. **Resolve Course ID** - Convert URL slug to numeric ID
3. **Fetch Course Structure** - Get sections and lectures from API
4. **Extract Content** - Process each lecture for transcripts, articles, quizzes, resources, links
5. **Generate README** - Create course metadata summary

---

## File Locations

When running this skill, the script uses the **current working directory** as the base:

- **Cookies:** `skola-research/udemy/cookies.json` (in current working directory)
- **Output:** `skola-research/udemy/{course-slug}/` (in current working directory)

**Example:**
If you're running Claude Code from `/Users/you/projects/myproject/`, files will be created at:
- `/Users/you/projects/myproject/skola-research/udemy/cookies.json`
- `/Users/you/projects/myproject/skola-research/udemy/{course-slug}/`

This design works whether the plugin is installed locally or from a Git repository marketplace.

---

## Step 1: Authentication

Load session cookies from `skola-research/udemy/cookies.json`:

**Cookie file format** (`skola-research/udemy/cookies.json`):
```json
{
  "access_token": "your-token",
  "client_id": "your-client-id"
}
```

**Required cookies**:
- `access_token` - Your Udemy session token
- `client_id` - Your Udemy client ID

**Extract cookies from browser**:
1. Log into Udemy in browser
2. Open DevTools → Application → Cookies
3. Copy `access_token` and `client_id` values
4. Save to `skola-research/udemy/cookies.json`

**Note**: Cookies expire after ~24 hours. Refresh as needed.

---

## Step 2: Resolve Course ID

Convert URL slug to numeric course ID:

```python
# Query /api-2.0/users/me/subscribed-courses/
# Match by slug, extract numeric ID
```

**Process**:
1. Extract slug from course URL (e.g., "python-bootcamp")
2. Query user's enrolled courses via API
3. Search for matching slug in results
4. Extract numeric course ID

**Why needed**: Udemy's API requires numeric course IDs, but URLs use slugs.

---

## Step 3: Fetch Course Structure

Retrieve complete course curriculum:

```python
# GET /api-2.0/courses/{course_id}/subscriber-curriculum-items/
# Pagination supported (200 items per page)
# Parse sections and lectures
```

**Data retrieved**:
- Section titles and ordering
- Lecture titles, types, and IDs
- Content type indicators (video, article, quiz)
- Supplementary asset information

**Pagination**: Large courses may require multiple API calls (200 items per page).

---

## Step 4: Extract Content

For each lecture, extract applicable content types:

### Video Transcripts

```python
# GET lecture details with caption URLs
# Download VTT file
# Parse timestamps and text
# Save as: {number:03d}-{title}.txt
```

**Process**:
1. Request lecture details from API
2. Extract caption URL (VTT format)
3. Download VTT file
4. Parse timestamps and text content
5. Convert to plain text with timestamps
6. Save to `transcripts/{number:03d}-{title}.txt`

**Format**: Timestamped plain text for easy searching and reading.

---

### Articles

```python
# Extract HTML body from lecture data
# Convert to markdown (preserve code blocks, links, formatting)
# Detect article type (solution, guide, promotional)
# Save with YAML frontmatter
```

**Process**:
1. Extract HTML body from lecture data
2. Convert HTML to markdown
3. Preserve code blocks, links, and formatting
4. Detect article type (solution, guide, promotional)
5. Add YAML frontmatter with metadata
6. Save to `articles/{number:03d}-{title}.md`

**Types detected**:
- Solutions (exercise answers)
- Guides (reference material)
- Promotional (bonus content)

---

### Quizzes

```python
# Extract quiz questions and answers
# Structure as YAML or JSON
# Include question types, correct answers
```

**Process**:
1. Request quiz data from API
2. Extract questions and answer options
3. Identify correct answers
4. Structure as YAML or JSON (user choice)
5. Save to `quizzes/{number:03d}-{title}.yaml`

**Includes**:
- Question text
- Answer options
- Correct answer indicators
- Question types (multiple choice, true/false, etc.)

---

### Resources

```python
# Parse supplementary_assets from lecture data
# Download files (PDFs, code, etc.) if enabled
# Create organized subdirectories per lecture
# Generate markdown catalog
```

**Process**:
1. Parse `supplementary_assets` from lecture data
2. Extract file URLs and metadata
3. Download files if `--download-resources` enabled
4. Create subdirectory per lecture: `resources/{number:03d}-{title}/`
5. Save files to subdirectory
6. Generate markdown catalog: `resources/{number:03d}-{title}-resources.md`

**File types**:
- PDFs (notes, slides)
- Code files (source code, exercises)
- Archives (ZIP, TAR)
- Other supplementary materials

**Catalog includes**:
- File names and sizes
- Download URLs
- File descriptions

---

### External Links

```python
# Scan transcripts and articles for URLs
# Categorize (GitHub, docs, StackOverflow, etc.)
# Track which lectures mentioned each link
# Generate summary markdown
```

**Process**:
1. Scan all transcripts and articles for URLs
2. Extract and deduplicate URLs
3. Categorize by domain (GitHub, docs, StackOverflow, etc.)
4. Track which lectures mentioned each URL
5. Generate summary: `resources/external-links.md`

**Categories**:
- GitHub repositories
- Official documentation
- StackOverflow questions
- Blog posts
- Other resources

---

## Step 5: Generate README

Create course metadata summary:

```python
# Fetch course details from API
# Populate template with:
# - Title, instructor, rating, students
# - Duration, level, description
# - Section/lecture structure
```

**Process**:
1. Request course details from API
2. Extract metadata (title, instructor, rating, etc.)
3. Populate README template
4. Add section/lecture structure outline
5. Save to `{course-slug}/README.md`

**README includes**:
- Course title and instructor
- Rating and student count
- Duration and difficulty level
- Course description
- Section structure with lecture counts
- Links to extracted content directories

---

## Summary

The complete workflow processes a Udemy course through these stages:

1. **Authenticate** → Load cookies
2. **Resolve ID** → Slug to numeric ID
3. **Fetch Structure** → Get course curriculum
4. **Extract Content** → Process each lecture
   - Transcripts from videos
   - Articles as markdown
   - Quiz data
   - Downloadable resources
   - External links
5. **Generate README** → Course summary

**Output**: Organized directory structure with all course content for offline access.

For usage examples, see [EXAMPLES.md](EXAMPLES.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
