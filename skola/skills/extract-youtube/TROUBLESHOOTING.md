# YouTube Content Extraction: Troubleshooting

This document provides solutions to common issues when using the `extracting-youtube` skill.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).
For examples, see [EXAMPLES.md](EXAMPLES.md).

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Dependency Problems](#dependency-problems)
3. [URL Parsing Errors](#url-parsing-errors)
4. [Transcript Extraction Failures](#transcript-extraction-failures)
5. [Metadata Extraction Issues](#metadata-extraction-issues)
6. [File Permission Errors](#file-permission-errors)
7. [Network and Rate Limiting](#network-and-rate-limiting)
8. [Performance Issues](#performance-issues)

---

## Installation Issues

### Python Version Too Old

**Error:**
```
ERROR: Python 3.8+ Required
Current Python version: 3.7.9
```

**Solution:**

When using `uv run`, Python version is automatically managed. The script declares `requires-python = ">=3.8"` in its inline metadata, so uv will use an appropriate Python version.

```bash
# uv automatically handles Python versions
uv run extract.py "URL"

# If you need to install a specific Python version:
uv python install 3.11
```

**Note:** With the inline script metadata approach, Python version issues are rare because uv manages the Python environment automatically.

### uv Not Installed

**Error:**
```bash
uv: command not found
```

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell or source profile
source ~/.bashrc  # or ~/.zshrc

# Verify installation
uv --version
```

---

## Dependency Problems

### youtube-transcript-api Not Found

**Error:**
```
ModuleNotFoundError: No module named 'youtube_transcript_api'
```

**This should NOT happen when using `uv run`!**

The script uses inline script metadata (PEP 723), which means dependencies are automatically installed on first run.

**Solution:**
```bash
# Use uv run (recommended - auto-installs dependencies)
uv run extract.py "URL"

# If error persists, check the script has inline metadata:
head -n 10 extract.py
# Should show:
# #!/usr/bin/env -S uv run --script
# # /// script
# # requires-python = ">=3.8"
# # dependencies = [
# #     "youtube-transcript-api>=0.6.0",
# # ]
# # ///
```

**If running with python3 directly (not recommended):**
```bash
# You'll need to manually install dependencies
python3 -m pip install youtube-transcript-api

# But it's better to use uv run instead
uv run extract.py "URL"
```

### Import Errors After Installation

**Error:**
```
ImportError: cannot import name 'YouTubeTranscriptApi'
```

**Solution:**

This usually happens when mixing different installation methods. Use `uv run` consistently:

```bash
# Clear any cached environments and run with uv
uv cache clean
uv run extract.py "URL"

# Install to correct Python version
python3 -m pip install youtube-transcript-api

# Or use uv with specific Python
uv pip install --python python3 youtube-transcript-api
```

### Permission Denied During Installation

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Install to user directory (no sudo needed)
uv pip install --user youtube-transcript-api

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
uv pip install youtube-transcript-api
```

---

## URL Parsing Errors

### Could Not Extract Video ID

**Error:**
```
✗ Error: Could not extract video or playlist ID from URL: https://youtube.com/...
```

**Common Causes:**
1. Invalid URL format
2. Unsupported URL type
3. Typo in URL

**Supported Formats:**
```
✓ https://www.youtube.com/watch?v=VIDEO_ID
✓ https://youtu.be/VIDEO_ID
✓ https://www.youtube.com/embed/VIDEO_ID
✓ https://www.youtube.com/v/VIDEO_ID
✓ https://www.youtube.com/shorts/VIDEO_ID
✓ https://www.youtube.com/playlist?list=PLAYLIST_ID

✗ https://youtube.com/channel/... (not supported)
✗ https://youtube.com/@username (not supported)
✗ https://m.youtube.com/... (remove 'm.' to use www.)
```

**Solution:**
```bash
# Correct the URL format
# Bad:  https://m.youtube.com/watch?v=VIDEO_ID
# Good: https://www.youtube.com/watch?v=VIDEO_ID

# Copy URL from browser address bar or "Share" button
```

### Invalid Video ID Format

**Error:**
```
ValueError: Video ID format invalid
```

**Solution:**
- YouTube video IDs are exactly 11 characters: `[A-Za-z0-9_-]{11}`
- Example valid ID: `dQw4w9WgXcQ`
- Check that URL wasn't truncated or corrupted

---

## Transcript Extraction Failures

### No Transcript Available

**Warning:**
```
⚠️  No transcript available
```

**Possible Causes:**
1. Video has no captions/subtitles
2. Captions are disabled by uploader
3. Video is too new (captions not yet generated)
4. Non-English video with no English translation

**Solution:**
```bash
# Check if video has captions on YouTube:
# 1. Open video on youtube.com
# 2. Look for CC button in player controls
# 3. Click Settings > Subtitles/CC

# If no captions available:
# - Extraction will continue without transcript
# - Metadata and thumbnail will still be saved
# - Use --transcript-only to skip videos without transcripts
```

### Transcripts Disabled for Video

**Warning:**
```
⚠️  Transcripts disabled for video VIDEO_ID
```

**Cause:**
Channel owner has disabled transcript access.

**Solution:**
- No workaround available
- Extraction continues with metadata only
- Manually enable captions on YouTube if you're the owner

### Only Non-English Transcripts

The script tries to get English transcripts by:
1. Manual English captions
2. Auto-generated English captions
3. Translating available captions to English

**If this fails:**
```bash
# Manually check available languages on YouTube
# Consider modifying script to accept other languages:

# Edit transcript_extractor.py line ~70:
transcript_data = transcript_extractor.extract(video_id, language='es')  # Spanish
transcript_data = transcript_extractor.extract(video_id, language='fr')  # French
```

### Video Unavailable

**Error:**
```
✗ Video VIDEO_ID is unavailable
```

**Possible Causes:**
1. Video is private
2. Video was deleted
3. Video is age-restricted (requires login)
4. Video is region-restricted
5. Video is members-only

**Solution:**
- Verify video is accessible on youtube.com
- Check if you need to be logged in
- Try different video
- No programmatic workaround for private/restricted videos

---

## Metadata Extraction Issues

### Failed to Fetch Metadata

**Error:**
```
✗ Failed to fetch metadata
```

**Possible Causes:**
1. Network connection issues
2. YouTube rate limiting
3. YouTube page structure changed
4. Invalid video ID

**Solution:**
```bash
# Check network connection
ping youtube.com

# Wait and retry (rate limiting)
sleep 60
uv run extract.py "URL"

# Try with different video to test
uv run extract.py "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### Incomplete Metadata

**Symptom:**
Some fields show "Unknown" in README.md:
```markdown
**Channel:** Unknown Channel
**Duration:** Unknown
```

**Cause:**
YouTube HTML structure may have changed.

**Solution:**
- Metadata extraction still works for most fields
- Check `metadata.json` for raw data
- Report issue if consistently failing

### Playlist Has Zero Videos

**Warning:**
```
⚠️  No videos found in playlist
```

**Possible Causes:**
1. Empty playlist
2. Private/unlisted videos only
3. Playlist parsing failed

**Solution:**
```bash
# Verify playlist on youtube.com
# Check if playlist is public
# Try different playlist
```

### Large Playlist Limitation (200+ Videos)

**Warning:**
```
⚠️  Playlists with more than ~200 videos may be incompletely extracted
```

**Cause:**
The current implementation only extracts videos from YouTube's initial page load, which typically contains 100-200 videos. Very large playlists require pagination handling (continuation tokens) which is not yet implemented.

**How to Detect:**
Compare the extracted video count in your output with the total video count shown on YouTube or in the playlist README.md.

**Workarounds:**
- Extract the most important videos individually by their URLs
- Use YouTube Data API v3 for complete large playlist extraction
- This limitation will be addressed in a future release (v1.3.0)

**Example:**
```
# Playlist on YouTube shows: 300 videos
# After extraction: Only 150 videos extracted

Statistics:
  Total videos: 150  ← May be incomplete if playlist has 200+ videos
  Transcripts extracted: 145
```

If you need all videos from a very large playlist, extract individual video URLs manually or wait for pagination support in v1.3.0.

---

## File Permission Errors

### Cannot Create Directory

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'skola-research/youtube/...'
```

**Solution:**
```bash
# Check current directory permissions
ls -ld .

# Run from directory where you have write permissions
cd ~/Documents
python3 /path/to/extract.py "URL"

# Or use --output-dir with custom location
uv run extract.py "URL" --output-dir ~/Downloads/youtube-content
```

### Cannot Write File

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'transcript.md'
```

**Solution:**
```bash
# Check if file already exists and is read-only
ls -l skola-research/youtube/complete-python-course-2024/

# Remove read-only attribute
chmod u+w skola-research/youtube/complete-python-course-2024/*

# Or delete existing directory and re-extract
rm -rf skola-research/youtube/complete-python-course-2024/
uv run extract.py "URL"
```

### Disk Space Full

**Error:**
```
OSError: [Errno 28] No space left on device
```

**Solution:**
```bash
# Check available disk space
df -h .

# Free up space or use different location
uv run extract.py "URL" --output-dir /path/to/larger/disk/

# Use --skip-thumbnails to reduce space usage
uv run extract.py "URL" --skip-thumbnails

# Use --transcript-only for minimal files
uv run extract.py "URL" --transcript-only
```

---

## Network and Rate Limiting

### Connection Timeout

**Error:**
```
URLError: <urlopen error [Errno 60] Operation timed out>
```

**Solution:**
```bash
# Check internet connection
ping google.com

# Check YouTube accessibility
ping youtube.com

# Retry with better connection
uv run extract.py "URL"

# Consider using VPN if region-blocked
```

### HTTP 429: Too Many Requests

**Error:**
```
HTTPError: HTTP Error 429: Too Many Requests
```

**Cause:**
YouTube rate limiting due to too many requests.

**Solution:**
```bash
# Wait before retrying (15-30 minutes)
sleep 1800

# Extract playlists one at a time
# Avoid running multiple extractions simultaneously

# The script includes 1-second delays between playlist videos
# This should prevent most rate limiting
```

### HTTP 403: Forbidden

**Error:**
```
HTTPError: HTTP Error 403: Forbidden
```

**Possible Causes:**
1. IP blocked by YouTube
2. Missing or invalid User-Agent
3. Video is age-restricted or private

**Solution:**
```bash
# Wait and retry
sleep 300

# Check if video is accessible in browser
# Try from different network/IP

# For developers: Check User-Agent in youtube_client.py
```

---

## Performance Issues

### Slow Extraction

**Symptom:**
Extraction takes very long time.

**Causes:**
1. Large playlist (50+ videos)
2. Slow network connection
3. Rate limiting delays

**Solutions:**
```bash
# Skip thumbnails to speed up
uv run extract.py "URL" --skip-thumbnails

# Extract transcript only
uv run extract.py "URL" --transcript-only

# Run in background
uv run extract.py "URL" > extraction.log 2>&1 &

# Monitor progress
tail -f extraction.log
```

### Memory Usage High

**Symptom:**
Script uses lots of RAM during extraction.

**Cause:**
Processing large playlists or long videos.

**Solution:**
- This is normal for large extractions
- Script processes videos one at a time
- Memory is freed after each video
- Consider extracting smaller playlists

### Extraction Interrupted

**Symptom:**
Extraction stopped mid-process (Ctrl+C, network failure, etc.)

**Solution:**
```bash
# Simply re-run the command
# It will overwrite existing files and continue

uv run extract.py "URL"

# To resume a playlist extraction:
# 1. Check which videos were already extracted
# 2. Extract remaining videos individually
uv run extract.py "https://youtube.com/watch?v=VIDEO_ID"
```

---

## Debugging

### Enable Verbose Logging

**Edit extract.py:**
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(message)s'
)
```

### Check Script Execution

**Test components individually:**
```python
# Test URL parsing
python3 -c "
from youtube_client import YouTubeClient
client = YouTubeClient()
print(client.parse_url('https://youtube.com/watch?v=dQw4w9WgXcQ'))
"

# Test transcript extraction
python3 -c "
from transcript_extractor import TranscriptExtractor
extractor = TranscriptExtractor()
print(extractor.extract('dQw4w9WgXcQ'))
"
```

### Check Python Path

**If imports fail:**
```bash
# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Check current directory
pwd

# Ensure running from correct location
cd /path/to/arkhe-claude-plugins
python3 skola/skills/extract-youtube/scripts/extract.py "URL"
```

---

## Getting Help

If issues persist:

1. **Check GitHub Issues**: Search for similar problems
2. **Verify Dependencies**: Ensure `youtube-transcript-api` is up-to-date
3. **Test with Known Video**: Use `https://youtube.com/watch?v=dQw4w9WgXcQ`
4. **Check YouTube Status**: Visit https://www.youtube.com to ensure site is accessible
5. **Review Logs**: Look for specific error messages

**When reporting issues, include:**
- Python version (`python3 --version`)
- OS and version
- Full error message
- URL being extracted (if not private)
- Output of `uv pip list | grep youtube`

---

## Quick Reference

**Common Fixes:**

| Issue | Quick Fix |
|-------|-----------|
| ModuleNotFoundError | `uv pip install youtube-transcript-api` |
| Could not extract ID | Check URL format, use full URL |
| No transcript | Video has no captions, expected behavior |
| Permission denied | Run from writable directory |
| Network timeout | Check internet, retry later |
| Rate limited (429) | Wait 15-30 minutes, retry |
| Slow extraction | Use `--skip-thumbnails` or `--transcript-only` |

**Verification Commands:**
```bash
# Check environment
python3 --version          # Should be 3.8+
uv --version              # Should be installed
python3 -c "import youtube_transcript_api; print('OK')"  # Should print OK

# Test extraction
uv run extract.py "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

---

## Getting Help

If issues persist:

1. **Check Skill Documentation**: Review [SKILL.md](SKILL.md)
2. **Review Examples**: See [EXAMPLES.md](EXAMPLES.md)
3. **Verify Installation**:
   ```bash
   python3 --version
   uv --version
   python3 -c "import youtube_transcript_api; print('✓ Installed')"
   ```
4. **Check YouTube Status**: Some issues may be due to YouTube service changes
5. **Test with Known Working Video**: Try `https://youtube.com/watch?v=dQw4w9WgXcQ`

---

*Last Updated: 2025-10-27*
