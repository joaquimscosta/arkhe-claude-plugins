# Udemy Plugin

Udemy course content extraction skill for Claude Code.

## Components

### Skills

- **extract**: Extract complete Udemy course content including video transcripts, articles, quizzes, downloadable resources (PDFs, code files), and external links. Use when you provide a Udemy course URL or mention extracting/downloading/scraping/archiving Udemy content.

## What This Extracts

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

## Installation

```bash
# Add the marketplace
/plugin marketplace add ./arkhe-claude-plugins

# Install the udemy plugin
/plugin install udemy@arkhe-claude-plugins
```

## Usage

This is a **skill**, which means Claude Code will automatically invoke it when you:

- Provide a Udemy course URL
- Ask to extract/download Udemy course content
- Want to analyze a Udemy course structure
- Mention getting transcripts or resources from Udemy

### Example

```
Extract this Udemy course: https://www.udemy.com/course/python-complete/
```

Claude will automatically recognize this as a Udemy extraction task and use the skill.

## Authentication Setup

Create `udemy-research/cookies.json`:

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

## Output Structure

Extracted courses are saved in `udemy-research/{course-slug}/`:

```
udemy-research/
└── course-name/
    ├── README.md           # Course metadata
    ├── transcripts/        # Video transcripts
    ├── articles/           # HTML lectures as markdown
    ├── quizzes/           # Quiz questions and answers
    └── resources/         # Downloaded files and catalogs
```

## Documentation

### Skill Documentation

For detailed usage, troubleshooting, and examples, see the files in the skill directory:

- `SKILL.md` - Complete skill documentation
- `EXAMPLES.md` - Usage examples
- `TROUBLESHOOTING.md` - Common issues and solutions
- `WORKFLOW.md` - Step-by-step implementation details

### Developer Resources

Interested in understanding how this skill was built or creating your own skills?

- **[Agent Skills Overview](../docs/AGENT_SKILLS_OVERVIEW.md)** - Understand the architecture and progressive disclosure pattern used in this skill
- **[Skill Development Best Practices](../docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md)** - Learn from the lessons and patterns applied in building the Udemy extractor

The `extract` skill follows Claude Code's progressive disclosure architecture:
- **Level 1 (Metadata)**: Skill name and description for auto-discovery
- **Level 2 (Instructions)**: Quick start guide in SKILL.md
- **Level 3+ (Resources)**: Detailed docs and Python scripts loaded on-demand

This design keeps token usage minimal while providing comprehensive capabilities when needed.

## Version

1.0.0
