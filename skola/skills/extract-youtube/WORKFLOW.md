# YouTube Content Extraction: Detailed Workflow

This document provides a detailed step-by-step breakdown of the YouTube content extraction process.

For quick start instructions, see [SKILL.md](SKILL.md).

## Overview

The extraction process follows these high-level steps:

1. **Setup** - Install dependencies and verify environment
2. **URL Parsing** - Detect content type (video/playlist) and extract IDs
3. **Metadata Extraction** - Fetch video/playlist information from YouTube
4. **Transcript Extraction** - Download English captions using youtube-transcript-api
5. **File Organization** - Save content in structured format
6. **Resource Download** - Download thumbnails (optional)

## Detailed Workflow

### 1. Setup

#### Install uv Package Manager

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Zero Setup - Dependencies Auto-Install

The script uses **inline script metadata** (PEP 723), which means:
- Dependencies are declared within the script itself
- On first run, `uv` automatically creates an isolated virtual environment
- The required `youtube-transcript-api` package is auto-installed
- No manual dependency installation needed!

**First run will show:**
```bash
uv run extract.py "URL"
# Creating virtual environment...
# Installing dependencies: youtube-transcript-api>=0.6.0
# Running script...
```

**Subsequent runs are instant:**
```bash
uv run extract.py "URL"
# Running script... (environment already exists)
```

### 2. URL Parsing

The script accepts various YouTube URL formats:

**Video URLs:**
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`

**Playlist URLs:**
- `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- `https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID` (treated as playlist)

**Parsing Process:**

1. Parse URL using `urllib.parse.urlparse()`
2. Extract query parameters
3. Check for `list=` parameter (indicates playlist)
4. Extract video ID from various URL patterns
5. Validate video ID format (11 characters: `[A-Za-z0-9_-]{11}`)
6. Return content type and IDs

### 3. Metadata Extraction

#### For Single Videos

The metadata extractor fetches the YouTube page HTML and extracts:

**Data Extracted:**
- Title (from `<meta property="og:title">` or `<title>` tag)
- Channel name (from `"author"` JSON field)
- Description (from `<meta property="og:description">`)
- Duration (from `"lengthSeconds"` JSON field, formatted as HH:MM:SS or MM:SS)
- Upload date (from `"uploadDate"` JSON field)
- View count (from `"viewCount"` JSON field)
- Thumbnail URL (constructed from video ID: `https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg`)
- Chapters (parsed from description if timestamps present)

**Chapter Detection:**

Chapters are extracted from the video description by looking for timestamp patterns:

```
00:00 Introduction
01:23 Main Topic
05:45 Conclusion
```

Pattern: `(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)`

#### For Playlists

The metadata extractor:

1. Fetches playlist page HTML
2. Extracts `ytInitialData` JSON object from page
3. Navigates JSON structure to extract:
   - Playlist title
   - Playlist description
   - List of videos with IDs and titles
4. Returns structured playlist metadata

**JSON Navigation Path:**
```
ytInitialData
  └─ sidebar
      └─ playlistSidebarRenderer
          └─ items[0]
              └─ playlistSidebarPrimaryInfoRenderer
                  ├─ title.runs[0].text (playlist title)
                  └─ description.simpleText (description)

  └─ contents
      └─ twoColumnBrowseResultsRenderer
          └─ tabs[0]
              └─ tabRenderer
                  └─ content
                      └─ sectionListRenderer
                          └─ contents[0]
                              └─ itemSectionRenderer
                                  └─ contents[0]
                                      └─ playlistVideoListRenderer
                                          └─ contents[] (video list)
```

### 4. Transcript Extraction

The transcript extractor uses `youtube-transcript-api` to fetch captions.

**Extraction Priority:**

1. **Manual transcripts** - Human-created captions (preferred)
2. **Auto-generated transcripts** - Machine-generated captions
3. **Translated transcripts** - Translate available transcript to English

**Process:**

1. Call `YouTubeTranscriptApi.list_transcripts(video_id)`
2. Try to find manually created English transcript
3. If not found, try to find auto-generated English transcript
4. If not found, try to translate any available transcript to English
5. Fetch transcript data (list of caption entries)
6. Format transcript with timestamps

**Transcript Format:**

Each transcript entry contains:
- `start`: Start time in seconds (float)
- `duration`: Duration in seconds (float)
- `text`: Caption text (string)

**Output Format:**

```markdown
[00:00] Introduction to the topic
[00:15] First main point being discussed
[01:23] Second main point with detailed explanation
```

Timestamps are formatted as:
- `MM:SS` for videos under 1 hour
- `HH:MM:SS` for videos 1 hour or longer

### 5. File Organization

#### Directory Structure

**Single Video:**
```
skola-research/youtube/
└── video-title/
    ├── README.md           # Video information and description
    ├── metadata.json       # Structured metadata
    ├── transcript.md       # Transcript with timestamps
    └── resources/
        └── thumbnail.jpg   # Video thumbnail (if downloaded)
```

**Playlist:**
```
skola-research/youtube/
└── playlist-title/
    ├── README.md               # Playlist overview and video list
    ├── metadata.json           # Playlist metadata
    ├── 001-first-video.md      # First video transcript
    ├── 002-second-video.md     # Second video transcript
    ├── 003-third-video.md      # Third video transcript
    └── resources/
        ├── 001-thumbnail.jpg
        ├── 002-thumbnail.jpg
        └── 003-thumbnail.jpg
```

#### File Naming

**Directory Names:**
- Derived from video/playlist title
- Invalid characters removed: `< > : " / \ | ? *`
- Spaces replaced with hyphens
- Truncated to 200 characters maximum

**Playlist Transcript Files:**
- Format: `{number:03d}-{sanitized-title}.md`
- Example: `001-introduction-to-python.md`

#### File Contents

**README.md for Video:**
```markdown
# Video Title

## Video Information

**Channel:** Channel Name
**Duration:** 12:34
**Upload Date:** 2025-01-15
**Views:** 1,234,567
**URL:** https://youtube.com/watch?v=VIDEO_ID

## Description

Video description text here...

## Chapters

- **00:00** - Introduction
- **01:23** - Main Topic
- **05:45** - Conclusion

---

**Extracted:** 2025-01-26T10:30:00.000000
```

**README.md for Playlist:**
```markdown
# Playlist Title

## Playlist Information

**Videos:** 25
**URL:** https://youtube.com/playlist?list=PLAYLIST_ID

## Description

Playlist description if available...

## Videos

1. [First Video Title](https://youtube.com/watch?v=VIDEO_ID_1)
2. [Second Video Title](https://youtube.com/watch?v=VIDEO_ID_2)
...

---

**Extracted:** 2025-01-26T10:30:00.000000
```

**metadata.json:**
Contains complete structured data for programmatic access.

**transcript.md:**
```markdown
# Video Title

**Video URL:** https://youtube.com/watch?v=VIDEO_ID
**Language:** en
**Transcript Type:** Manual

---

## Transcript

[00:00] First caption text here

[00:15] Second caption text continues

[01:23] More transcript content
```

### 6. Resource Download

#### Thumbnails

YouTube thumbnails are available at:
- `https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg` (1920x1080, preferred)
- `https://i.ytimg.com/vi/{video_id}/hqdefault.jpg` (480x360, fallback)

**Download Process:**

1. Construct thumbnail URL from video ID
2. Send HTTP request with User-Agent header
3. Save image data to `resources/` directory
4. Handle errors gracefully (log warning, continue)

**File Naming:**
- Single video: `thumbnail.jpg`
- Playlist: `{number:03d}-thumbnail.jpg`

## Error Handling

### Common Errors and Recovery

**No Transcript Available:**
- Log warning
- Continue with metadata extraction
- Note in output statistics

**Transcripts Disabled:**
- Log warning
- Skip transcript for this video
- Increment `disabled` counter

**Video Unavailable:**
- Log error
- Skip this video
- Increment `unavailable` counter

**Playlist Parsing Failed:**
- Fall back to basic video list
- Continue with available data

**Thumbnail Download Failed:**
- Log warning
- Continue without thumbnail
- Don't fail entire extraction

### Rate Limiting

**Between Videos in Playlist:**
- Wait 1 second between each video
- Prevents overwhelming YouTube servers
- Reduces chance of rate limiting

**Best Practices:**
- Don't extract same content repeatedly
- Use reasonable delays between requests
- Respect YouTube's terms of service

## Output Statistics

The script tracks and reports:

**Transcript Extraction:**
- `success`: Successfully extracted
- `no_transcript`: No transcript available
- `disabled`: Transcripts disabled
- `unavailable`: Video unavailable
- `error`: Extraction errors

**File Writing:**
- `transcripts`: Number of transcript files created
- `thumbnails`: Number of thumbnail images downloaded
- `metadata`: Number of metadata files created

**Final Report:**

```
Statistics:
  Total videos: 25
  Transcripts extracted: 22
  No transcript: 2
  Failed: 1

Files created:
  Transcripts: 22 files
  Thumbnails: 22 files
```

## Advanced Usage

### Custom Output Directory

```bash
uv run extract.py "URL" --output-dir my-custom-name
```

### Skip Thumbnails

```bash
uv run extract.py "URL" --skip-thumbnails
```

### Transcript Only

```bash
uv run extract.py "URL" --transcript-only
```

This skips README.md, metadata.json, and thumbnail downloads.

## Integration with Claude Code

When this skill is triggered by Claude Code:

1. User provides YouTube URL in conversation
2. Skill YAML frontmatter `description` triggers auto-invocation
3. Claude Code loads SKILL.md instructions
4. Claude executes extraction script via Bash tool
5. Results are summarized and presented to user

The skill is designed to work from any working directory by using `Path.cwd() / 'skola-research' / 'youtube'` as the base output path.

---

## Summary

The YouTube extraction workflow automates:
1. ✅ URL parsing and content type detection
2. ✅ Metadata extraction from YouTube pages
3. ✅ Transcript extraction with language preference
4. ✅ Structured file organization
5. ✅ Resource downloading (thumbnails)
6. ✅ Error handling and statistics tracking

**Result**: Comprehensive YouTube content archives for offline study and research.

For examples, see [EXAMPLES.md](EXAMPLES.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

*Last Updated: 2025-10-27*
