# Skola Plugin

Tutorial creation and educational content extraction toolkit for Claude Code.

## Components

### Agents

- **tutorial-engineer**: Creates step-by-step tutorials and educational content from code. Transforms complex concepts into progressive learning experiences with hands-on examples.

### Skills

- **extracting-udemy**: Extract complete Udemy course content including video transcripts, articles, quizzes, downloadable resources (PDFs, code files), and external links. Auto-invoked when Udemy URLs are provided.
- **extracting-youtube**: Extract YouTube video transcripts and metadata including video details, playlist structure, and English captions. Auto-invoked when YouTube URLs are provided.

### Commands

- **/extract**: Extract educational content from various sources (Udemy, YouTube, blogs) by providing a URL. Auto-detects source and delegates to appropriate extraction skill.
- **/teach-code**: Educational code explanation that breaks down complex logic into understandable concepts with examples, visual diagrams, and step-by-step narratives for learners at all levels.

## Installation

```bash
# Add the marketplace
/plugin marketplace add ./arkhe-claude-plugins

# Install the skola plugin
/plugin install skola@arkhe-claude-plugins
```

## Migration from Standalone Udemy Plugin

If you previously installed the standalone `udemy` plugin, you should migrate to the unified `skola` plugin:

```bash
# Uninstall the deprecated udemy plugin
/plugin uninstall udemy@arkhe-claude-plugins

# Reinstall skola to get latest version with extraction capabilities
/plugin uninstall skola@arkhe-claude-plugins
/plugin install skola@arkhe-claude-plugins
```

All Udemy extraction functionality is preserved and enhanced in the `extracting-udemy` skill.

## Usage

### Tutorial Creation

```bash
# Use the tutorial-engineer agent
/agents
# Select: tutorial-engineer

# Use educational code explanation
/teach-code src/auth/middleware.ts
/teach-code the authentication flow in this codebase
```

### Content Extraction

**Auto-invoke (recommended)**:
Claude Code will automatically invoke the appropriate extraction skill when you:
- Provide a Udemy course URL or YouTube video/playlist URL
- Mention extracting/downloading educational content
- Ask to analyze course structure or get video transcripts

**Manual command**:
```bash
# Extract from any supported source
/extract https://www.udemy.com/course/python-complete/

# Claude will auto-detect the source and use the appropriate extractor
```

### Udemy Extraction

The `extracting-udemy` skill extracts:

1. **Video Transcripts** - VTT captions converted to timestamped plain text
2. **Articles** - HTML lectures converted to markdown
3. **Quizzes** - Structured quiz data in YAML/JSON format
4. **Resources** - Downloads supplementary files (PDFs, code files, etc.)
5. **External Links** - Extracts and categorizes URLs mentioned in content
6. **Course Metadata** - Instructor, duration, rating, description

**Requirements**:
- Python 3.8+ (verify with `python3 --version`)
- Valid Udemy session in `skola-research/udemy/cookies.json`
- Must be enrolled in the course
- Standard library only (no pip packages needed)

**Authentication Setup**:

Create `skola-research/udemy/cookies.json` in your project root:

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

**Output Structure**:

Extracted courses are saved in `skola-research/udemy/{course-slug}/`:

```
skola-research/udemy/
└── course-name/
    ├── README.md           # Course metadata
    ├── transcripts/        # Video transcripts
    ├── articles/           # HTML lectures as markdown
    ├── quizzes/           # Quiz questions and answers
    └── resources/         # Downloaded files and catalogs
```

**Detailed Documentation**:

For comprehensive usage, troubleshooting, and examples:
- `skills/extract-udemy/SKILL.md` - Complete skill documentation
- `skills/extract-udemy/EXAMPLES.md` - Usage examples
- `skills/extract-udemy/TROUBLESHOOTING.md` - Common issues and solutions
- `skills/extract-udemy/WORKFLOW.md` - Step-by-step implementation details

### YouTube Extraction

The `extracting-youtube` skill extracts:

1. **Video Transcripts** - English captions (manual or auto-generated) with timestamps
2. **Video Metadata** - Title, channel, duration, upload date, description, views
3. **Playlist Structure** - All videos in playlist with metadata
4. **Chapter/Timestamps** - Video chapters if available in description
5. **Thumbnails** - Video thumbnail images

**Requirements**:
- Python 3.8+ (verify with `python3 --version`)
- uv package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Dependencies: `uv pip install youtube-transcript-api`
- No authentication required (public YouTube data only)

**Output Structure**:

Extracted content is saved in `skola-research/youtube/{video-or-playlist-title}/`:

**Single Video:**
```
skola-research/youtube/
└── video-title/
    ├── README.md           # Video metadata and description
    ├── metadata.json       # Structured video data
    ├── transcript.md       # English transcript with timestamps
    └── resources/
        └── thumbnail.jpg   # Video thumbnail
```

**Playlist:**
```
skola-research/youtube/
└── playlist-title/
    ├── README.md               # Playlist overview and video list
    ├── metadata.json           # Playlist metadata
    ├── 001-first-video.md      # First video transcript
    ├── 002-second-video.md     # Second video transcript
    └── resources/
        ├── 001-thumbnail.jpg
        └── 002-thumbnail.jpg
```

**Detailed Documentation**:

For comprehensive usage, troubleshooting, and examples:
- `skills/extract-youtube/SKILL.md` - Complete skill documentation
- `skills/extract-youtube/EXAMPLES.md` - Usage examples
- `skills/extract-youtube/TROUBLESHOOTING.md` - Common issues and solutions
- `skills/extract-youtube/WORKFLOW.md` - Step-by-step implementation details

## Use Cases

### Tutorial Creation
- Creating step-by-step tutorials from existing code
- Building progressive learning experiences
- Explaining complex algorithms and patterns
- Generating hands-on coding exercises
- Creating educational content for onboarding
- Teaching programming concepts with real examples

### Content Extraction
- Extracting Udemy courses for offline study
- Extracting YouTube videos and playlists with transcripts
- Archiving educational content for research
- Creating searchable transcripts from video courses
- Downloading course resources and supplementary materials
- Building local knowledge bases from online courses
- Analyzing course structure and content organization

## Recommended Companion Plugins

For comprehensive educational content workflows, consider installing:
- **doc** plugin - For generating documentation and diagrams (`docs-architect`, `mermaid` skill, `/diagram` command)
- **ai** plugin - For AI engineering tutorials (`ai-engineer`, `prompt-engineer`, `context-manager`)

## Future Enhancements

Planned additions to the content extraction capabilities:

- **Blog Articles** - Tutorial and article extraction from educational blogs
- **Other MOOCs** - Coursera, edX, LinkedIn Learning
- **Documentation Sites** - MDN, official docs, technical guides
- **Coding Platforms** - LeetCode, HackerRank problem extraction

## Version

1.2.0 - Added YouTube extraction skill (videos and playlists)
1.1.0 - Added Udemy extraction skill and `/extract` command
