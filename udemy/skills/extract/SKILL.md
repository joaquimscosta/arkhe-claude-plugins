---
name: Udemy Course Extractor
description: Extract complete Udemy course content including video transcripts, articles, quizzes, downloadable resources (PDFs, code files), and external links. Use when user provides a Udemy course URL, mentions extracting/downloading/scraping/archiving Udemy content, analyzing course structure, or wants offline access to course materials.
---

# Udemy Course Extractor

Extract complete course content from Udemy for offline study and research.

## When to Use This Skill

Use this skill when the user:
- Provides a Udemy course URL
- Asks to extract/download Udemy course content
- Wants to research or analyze a Udemy course
- Mentions getting transcripts, resources, or materials from Udemy lectures

## What This Skill Extracts

1. **Video Transcripts** - VTT captions converted to timestamped plain text
2. **Articles** - HTML lectures converted to markdown
3. **Quizzes** - Structured quiz data in YAML/JSON format
4. **Resources** - Downloads supplementary files (PDFs, code files, etc.)
5. **External Links** - Extracts and categorizes URLs mentioned in content
6. **Course Metadata** - Instructor, duration, rating, description

## Requirements

- **Python**: 3.8+ (verify with `python3 --version`)
- **Authentication**: Valid Udemy session in `cookies.json`
- **Access**: Must be enrolled in the course
- **Libraries**: Standard library only (no pip packages needed)

## Quick Start

### Basic Extraction (All Content Types)

```bash
python3 arkhe-claude-plugins/udemy/skills/extract/scripts/extract.py \
  "https://SITE.udemy.com/course/course-name/"
```

**Important:** Run the script from your project root directory (where `udemy-research/` should be created).
The script uses the current working directory to locate `udemy-research/cookies.json`.

### Extract Specific Content Types

```bash
# Only transcripts and articles
python3 arkhe-claude-plugins/udemy/skills/extract/scripts/extract.py \
  "https://SITE.udemy.com/course/course-name/" \
  --content-types video,article

# Only resources (without downloading files)
python3 arkhe-claude-plugins/udemy/skills/extract/scripts/extract.py \
  "https://SITE.udemy.com/course/course-name/" \
  --content-types resource \
  --no-download-resources
```

### Advanced Options

```bash
python3 arkhe-claude-plugins/udemy/skills/extract/scripts/extract.py \
  "https://SITE.udemy.com/course/course-name/" \
  --content-types video,article,quiz,resource \
  --skip-promotional \
  --quiz-format yaml \
  --download-resources \
  --max-resource-size 100 \
  --output-dir custom-directory-name
```

**Available Options:**
- `--content-types` - Comma-separated: video, article, quiz, resource (default: all)
- `--skip-promotional` - Skip bonus/promotional lectures
- `--quiz-format` - Quiz output format: yaml or json (default: yaml)
- `--download-resources` - Download resource files (enabled by default)
- `--no-download-resources` - Only create resource catalog, skip downloads
- `--max-resource-size` - Max download size in MB (default: 100)
- `--output-dir` - Custom directory name (default: course slug from URL)

## Output Structure

Courses are created in `udemy-research/{course-slug}/`:

```
udemy-research/
└── course-name/
    ├── README.md                # Course metadata (auto-populated from API)
    ├── transcripts/             # Video transcripts with timestamps
    │   ├── 001-introduction.txt
    │   ├── 002-getting-started.txt
    │   └── ...
    ├── articles/                # HTML lectures as markdown
    │   ├── 010-important-tips.md
    │   ├── 025-bonus-content.md
    │   └── ...
    ├── quizzes/                 # Quiz questions and answers
    │   ├── 015-section-quiz.yaml
    │   └── ...
    └── resources/               # Downloaded files and catalogs
        ├── 002-code-editor/
        │   └── Visual-Studio-Code-Theme.jar
        ├── 003-big-o/
        │   └── Big-O-Notes.pdf
        ├── 019-exercise/
        │   ├── EXERCISE-LinkedList.txt
        │   └── SOLUTION-LinkedList.txt
        ├── 002-code-editor-resources.md
        ├── 003-big-o-resources.md
        └── external-links.md    # Categorized external URLs
```

## Workflow

See [WORKFLOW.md](WORKFLOW.md) for detailed step-by-step implementation.

**High-level process**:
1. **Authenticate** - Load session cookies from `cookies.json`
2. **Resolve Course ID** - Convert URL slug to numeric ID via API
3. **Fetch Course Structure** - Get sections and lectures from curriculum API
4. **Extract Content** - Process each lecture for transcripts, articles, quizzes, resources, and external links
5. **Generate README** - Create course metadata summary

## Authentication

Uses cookie-based authentication from `udemy-research/cookies.json`:

```json
{
  "access_token": "your-token",
  "client_id": "your-client-id"
}
```

Extract cookies from browser:
1. Log into Udemy in browser
2. Open DevTools → Application → Cookies
3. Copy `access_token` and `client_id`
4. Save to `cookies.json`

**Note**: Cookies expire after ~24 hours. Refresh as needed.

## File Locations

When running this skill, the script uses the **current working directory** as the base:

- **Cookies:** `udemy-research/cookies.json` (in current working directory)
- **Output:** `udemy-research/{course-slug}/` (in current working directory)

**Example:**
If you're running Claude Code from `/Users/you/projects/myproject/`, files will be created at:
- `/Users/you/projects/myproject/udemy-research/cookies.json`
- `/Users/you/projects/myproject/udemy-research/{course-slug}/`

This design works whether the plugin is installed locally or from a Git repository marketplace.

## Common Issues

**"Could not find course with slug"**
- Ensure you're enrolled in the course
- Course must appear in "My Courses"
- Script queries your enrolled courses to resolve slug → ID

**"No resources found" (but you see files in UI)**
- Fixed in 2025-10-18 update
- Ensure using latest version with `supplementary_assets` parsing

**"SyntaxError" or "invalid syntax"**
- Use `python3` command (not `python`)
- Verify Python 3.8+ with `python3 --version`

For complete troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Examples

See [EXAMPLES.md](EXAMPLES.md) for detailed examples including:
- Full course extraction
- Selective content type extraction
- Resource-only extraction
- Handling large courses
- API discovery workflow

## Implementation Details

For technical details about the extractors, API endpoints, and implementation:
- See `../../../udemy-research/UDEMY_PLATFORM_REFERENCE.md` for platform details and API documentation
- See `../../../udemy-research/FUTURE_EXTRACTORS_ROADMAP.md` for planned features

## Related Files

**Core Scripts:**
- `scripts/extract.py` - Main extraction orchestrator
- `scripts/api_client.py` - API client with endpoint discovery
- `scripts/content_extractors.py` - Article, quiz, resource, link extractors
- `scripts/file_writer.py` - File organization and saving
- `scripts/auth.py` - Cookie-based authentication

**Documentation:**
- `TROUBLESHOOTING.md` - Complete error handling guide
- `EXAMPLES.md` - Detailed usage examples
- `../../../udemy-research/UDEMY_PLATFORM_REFERENCE.md` - Platform details and API documentation
- `../../../udemy-research/QUICKSTART.md` - Quick start guide
