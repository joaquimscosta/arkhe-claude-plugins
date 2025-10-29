# YouTube Content Extraction: Examples

This document provides real-world examples of YouTube content extraction with the `extracting-youtube` skill.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).

---

## Table of Contents

1. [Single Video Extraction](#single-video-extraction)
2. [Playlist Extraction](#playlist-extraction)
3. [Short URL Format](#short-url-format)
4. [Custom Output Directory](#custom-output-directory)
5. [Transcript Only Mode](#transcript-only-mode)
6. [Skip Thumbnails](#skip-thumbnails)
7. [Handling Missing Transcripts](#handling-missing-transcripts)
8. [Large Playlist Extraction](#large-playlist-extraction)

## Single Video Extraction

### Basic Example

**Command:**
```bash
uv run arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Output:**
```
============================================================
YouTube Content Extractor
============================================================
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

🔌 Initializing YouTube client...
  ✓ Client ready

📋 Parsing URL...
  ✓ Content type: video

🔧 Initializing transcript extractor...
  ✓ Extractor ready

📹 Extracting video: dQw4w9WgXcQ
  Fetching metadata...
  ✓ Title: Rick Astley - Never Gonna Give You Up
  📁 Output: skola-research/youtube/Rick-Astley-Never-Gonna-Give-You-Up

  Extracting transcript...
  ✓ Transcript saved
  Saving metadata...
  ✓ Metadata saved
  Downloading thumbnail...
  ✓ Thumbnail saved

✓ Extraction complete!
  Transcripts: 1
  Thumbnails: 1
  Output: skola-research/youtube/Rick-Astley-Never-Gonna-Give-You-Up

✓ Done!
```

**Files Created:**
```
skola-research/youtube/Rick-Astley-Never-Gonna-Give-You-Up/
├── README.md
├── metadata.json
├── transcript.md
└── resources/
    └── thumbnail.jpg
```

### Example README.md Output

```markdown
# Rick Astley - Never Gonna Give You Up (Official Video)

## Video Information

**Channel:** Rick Astley
**Duration:** 3:33
**Upload Date:** 2009-10-25
**Views:** 1,400,000,000
**URL:** https://www.youtube.com/watch?v=dQw4w9WgXcQ

## Description

The official video for "Never Gonna Give You Up" by Rick Astley

## Chapters

- **00:00** - Intro
- **00:16** - Verse 1
- **00:46** - Chorus
- **01:25** - Verse 2
- **02:35** - Bridge
- **02:57** - Final Chorus

---

**Extracted:** 2025-01-26T10:30:00.000000
```

### Example Transcript Output

```markdown
# Rick Astley - Never Gonna Give You Up

**Video URL:** https://www.youtube.com/watch?v=dQw4w9WgXcQ
**Language:** en
**Transcript Type:** Manual

---

## Transcript

[00:00] We're no strangers to love

[00:04] You know the rules and so do I

[00:08] A full commitment's what I'm thinking of

[00:12] You wouldn't get this from any other guy
```

## Playlist Extraction

### Basic Playlist Example

**Command:**
```bash
uv run arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py \
  "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
```

**Output:**
```
============================================================
YouTube Content Extractor
============================================================
URL: https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf

🔌 Initializing YouTube client...
  ✓ Client ready

📋 Parsing URL...
  ✓ Content type: playlist

🔧 Initializing transcript extractor...
  ✓ Extractor ready

📚 Extracting playlist: PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf
  Fetching playlist metadata...
  ✓ Playlist: Python Tutorial for Beginners
  ✓ Videos: 12

  📁 Output: skola-research/youtube/Python-Tutorial-for-Beginners

  Saving playlist metadata...
  ✓ Playlist metadata saved

  Extracting 12 videos...

  [001/012] Introduction to Python
    ✓ Transcript saved
    ✓ Thumbnail saved

  [002/012] Variables and Data Types
    ✓ Transcript saved
    ✓ Thumbnail saved

  [003/012] Control Flow - If Statements
    ⚠️  No transcript available

  ...

============================================================
Playlist Extraction Complete!
============================================================
Playlist: Python Tutorial for Beginners
Output: skola-research/youtube/Python-Tutorial-for-Beginners

Statistics:
  Total videos: 12
  Transcripts extracted: 10
  No transcript: 2
  Failed: 0

Files created:
  skola-research/youtube/Python-Tutorial-for-Beginners/README.md
  skola-research/youtube/Python-Tutorial-for-Beginners/metadata.json
  Transcripts: 10 files
  Thumbnails: 12 files
============================================================

✓ Done!
```

**Files Created:**
```
skola-research/youtube/Python-Tutorial-for-Beginners/
├── README.md
├── metadata.json
├── 001-Introduction-to-Python.md
├── 002-Variables-and-Data-Types.md
├── 003-Control-Flow-If-Statements.md
├── ...
└── resources/
    ├── 001-thumbnail.jpg
    ├── 002-thumbnail.jpg
    ├── 003-thumbnail.jpg
    └── ...
```

## Short URL Format

YouTube's short URL format (`youtu.be`) is fully supported:

**Command:**
```bash
uv run arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py \
  "https://youtu.be/dQw4w9WgXcQ"
```

This works identically to the full URL format.

## Custom Output Directory

Override the default directory name (derived from video/playlist title):

**Command:**
```bash
uv run arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --output-dir rickroll-classic
```

**Output Path:**
```
skola-research/youtube/rickroll-classic/
├── README.md
├── metadata.json
├── transcript.md
└── resources/
    └── thumbnail.jpg
```

**Use Cases:**
- Shorter, cleaner directory names
- Avoiding special characters in path
- Organizing related content with consistent naming
- Re-extracting to a different location

## Transcript Only Mode

Extract only transcripts, skip metadata files and thumbnails:

**Command:**
```bash
uv run arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --transcript-only
```

**Files Created:**
```
skola-research/youtube/Rick-Astley-Never-Gonna-Give-You-Up/
└── transcript.md
```

**Use Cases:**
- Quick transcript-only extraction
- Saving disk space
- Focusing on text content only
- Batch processing many videos for transcripts

## Skip Thumbnails

Extract metadata and transcripts but skip thumbnail downloads:

**Command:**
```bash
uv run arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --skip-thumbnails
```

**Files Created:**
```
skola-research/youtube/Rick-Astley-Never-Gonna-Give-You-Up/
├── README.md
├── metadata.json
├── transcript.md
└── resources/
    (empty)
```

**Use Cases:**
- Saving bandwidth
- Faster extraction
- Thumbnails not needed for your use case

## Handling Missing Transcripts

### Video Without Transcript

Some videos don't have transcripts available:

**Output:**
```
📹 Extracting video: ABC123XYZ
  Fetching metadata...
  ✓ Title: Music Video Without Captions
  📁 Output: skola-research/youtube/Music-Video-Without-Captions

  Extracting transcript...
  ⚠️  No transcript available
  Saving metadata...
  ✓ Metadata saved
  Downloading thumbnail...
  ✓ Thumbnail saved

✓ Extraction complete!
  Transcripts: 0
  Thumbnails: 1
  Output: skola-research/youtube/Music-Video-Without-Captions
```

**Files Created:**
```
skola-research/youtube/Music-Video-Without-Captions/
├── README.md
├── metadata.json
└── resources/
    └── thumbnail.jpg
```

Note: `transcript.md` is **not** created when no transcript is available.

### Playlist with Mixed Transcript Availability

**Output Example:**
```
Statistics:
  Total videos: 20
  Transcripts extracted: 15
  No transcript: 4
  Failed: 1
```

The extraction continues even when some videos don't have transcripts.

## Large Playlist Extraction

### Example: 50+ Video Playlist

**Command:**
```bash
uv run arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py \
  "https://www.youtube.com/playlist?list=LARGE_PLAYLIST_ID"
```

**Notes:**
- Each video extraction waits 1 second (rate limiting)
- Total time: ~1-2 seconds per video
- 50 videos = ~2-3 minutes total
- **Current Limitation**: Playlists over ~200 videos may not be fully extracted due to pagination not being implemented yet
- Progress shown for each video
- Can be interrupted with Ctrl+C and resumed later

**Progress Output:**
```
  [001/053] Introduction
    ✓ Transcript saved
    ✓ Thumbnail saved

  [002/053] Getting Started
    ✓ Transcript saved
    ✓ Thumbnail saved

  [003/053] Basic Concepts
    ⚠️  No transcript available

  [004/053] Advanced Topics
    ✓ Transcript saved
    ✓ Thumbnail saved

  ...
```

**Best Practices for Large Playlists:**
- Use `--skip-thumbnails` to speed up extraction
- Use `--transcript-only` if you only need text
- Run in background with output redirection:
  ```bash
  uv run extract.py "URL" > extraction.log 2>&1 &
  ```

## Error Recovery

### Network Error During Extraction

If a network error occurs mid-extraction:

```
  [023/050] Video Title
    ✗ Error: Network timeout

Transcript Extraction Issues:
  ✗ 1 errors occurred

✗ Extraction failed
```

**Recovery:**
- Check network connection
- Re-run the command
- The script will re-create the output directory
- Previously extracted files will be overwritten

### Invalid URL

**Command:**
```bash
uv run extract.py "https://youtube.com/invalid"
```

**Output:**
```
📋 Parsing URL...
✗ Error: Could not extract video or playlist ID from URL: https://youtube.com/invalid
```

## Combining Options

### Playlist, Custom Directory, No Thumbnails

**Command:**
```bash
uv run arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID" \
  --output-dir python-course \
  --skip-thumbnails
```

### Video, Transcript Only, Custom Directory

**Command:**
```bash
uv run arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py \
  "https://youtu.be/VIDEO_ID" \
  --transcript-only \
  --output-dir lecture-transcript
```

## Using with Claude Code

When Claude Code invokes this skill automatically:

**User:** "Can you extract the transcript from https://youtube.com/watch?v=dQw4w9WgXcQ?"

**Claude Code:**
1. Detects YouTube URL in message
2. Auto-invokes extract-youtube skill
3. Executes extraction script
4. Summarizes results for user

**Claude's Response:**
```
I've extracted the content from that YouTube video. Here's what was saved:

📁 Output: skola-research/youtube/Rick-Astley-Never-Gonna-Give-You-Up/

Files created:
- README.md - Video information and description
- metadata.json - Structured video data
- transcript.md - Full English transcript with timestamps
- resources/thumbnail.jpg - Video thumbnail

The transcript is 3:33 long and includes manual captions.
```

## Advanced: Programmatic Usage

You can also import and use the modules directly in Python:

```python
from youtube_client import YouTubeClient
from transcript_extractor import TranscriptExtractor
from file_writer import YouTubeFileWriter
from pathlib import Path

# Initialize clients
client = YouTubeClient()
transcript_extractor = TranscriptExtractor()

# Parse URL
url_info = client.parse_url("https://youtube.com/watch?v=VIDEO_ID")
video_id = url_info['video_id']

# Get metadata
metadata = client.get_video_metadata(video_id)

# Extract transcript
transcript_data = transcript_extractor.extract(video_id)

# Save files
output_path = Path("skola-research/youtube/my-video")
file_writer = YouTubeFileWriter(output_path, 'video')
file_writer.create_directory_structure()
file_writer.save_video_readme(metadata)
file_writer.save_metadata_json(metadata)

if transcript_data:
    transcript_md = transcript_extractor.format_as_markdown(
        transcript_data,
        metadata['title'],
        metadata['url']
    )
    file_writer.save_transcript(transcript_md)
```

This allows for custom workflows and integration with other tools.

---

## Summary

The `extracting-youtube` skill automates:
- ✅ Single video and playlist extraction
- ✅ Multiple URL format support (youtube.com, youtu.be, shorts)
- ✅ Flexible output options (custom directories, transcript-only, skip thumbnails)
- ✅ Graceful handling of missing transcripts
- ✅ Large playlist support with progress tracking
- ✅ Programmatic usage via Python modules

**Result**: Comprehensive YouTube content archives for offline study and research.

For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

*Last Updated: 2025-10-27*
