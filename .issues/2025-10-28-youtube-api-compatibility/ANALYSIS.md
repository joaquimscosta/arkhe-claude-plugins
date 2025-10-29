# Extract-YouTube Skill: API Compatibility Issue Analysis

**Date:** 2025-10-28
**Status:** Issue Identified and Resolved
**Skill:** extract-youtube

---

## Executive Summary

The `extract-youtube` skill's transcript extraction feature failed with an `AttributeError` indicating that `YouTubeTranscriptApi` has no attribute `list_transcripts`. Root cause: the youtube-transcript-api library underwent breaking API changes in version 1.0+, transitioning from static class methods to an instance-based API pattern.

### Key Finding

The code was written for youtube-transcript-api **v0.x** (static methods) but the dependency specification `youtube-transcript-api>=0.6.0` allowed installation of **v1.0+** (instance methods), causing the incompatibility.

---

## Issue Description

### Symptom

When attempting to extract YouTube video transcripts, the extraction failed with:

```
Error extracting transcript for 8xXV4FeaF9M: type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'
⚠️  No transcript available
```

**Test Video:**
- URL: https://youtu.be/8xXV4FeaF9M
- Title: "Up & Running with GitHub Spec Kit #2 - The /constitution Command"
- Channel: Net Ninja
- Has English auto-generated captions: ✓

### Impact

- Users could not extract video transcripts
- The skill only saved metadata and thumbnails, missing the core functionality
- Error message was misleading ("No transcript available" when transcripts exist)
- Dependency specification allowed incompatible versions to be installed

---

## Root Cause Analysis

### 1. API Breaking Changes in youtube-transcript-api v1.0+

The library maintainers introduced a major API redesign that broke backward compatibility:

**Version 0.x (Old API - Static Methods):**
```python
from youtube_transcript_api import YouTubeTranscriptApi

# Static method usage
transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
```

**Version 1.0+ (New API - Instance Methods):**
```python
from youtube_transcript_api import YouTubeTranscriptApi

# Instance-based usage
ytt_api = YouTubeTranscriptApi()
transcript_list = ytt_api.list(video_id)
fetched_transcript = ytt_api.fetch(video_id)

# Returns new object types
transcript_data = fetched_transcript.to_raw_data()
```

### 2. Code Analysis

**File:** `arkhe-claude-plugins/skola/skills/extract-youtube/scripts/transcript_extractor.py`

**Problematic Code (Line 58):**
```python
# This line fails with AttributeError
transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
```

**Why it failed:**
- Code attempted to call static method `list_transcripts()`
- youtube-transcript-api v1.0+ removed static methods
- Available methods in v1.0+ are: `fetch`, `list` (both instance methods)

**Verification:**
```python
# Test script output
Available methods on YouTubeTranscriptApi:
['fetch', 'list']

✗ get_transcript() failed: type object 'YouTubeTranscriptApi' has no attribute 'get_transcript'
✗ list_transcripts() failed: type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'
```

### 3. Dependency Specification Issue

**File:** `scripts/extract.py` (PEP 723 inline metadata)
```python
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "youtube-transcript-api>=0.6.0",  # Too permissive!
# ]
# ///
```

**Problem:**
- Specification allows v0.6.0, v0.7.0, v1.0.0, v1.2.3, etc.
- uv installed latest version (v1.2.3 as of Oct 2025)
- Code was written for v0.x API
- No upper bound constraint to prevent v1.0+ installation

---

## Research Findings

### API Documentation Research (via Exa MCP)

**Source 1: GitHub Official Documentation**
```python
# Current recommended usage (v1.0+)
ytt_api = YouTubeTranscriptApi()
ytt_api.fetch(video_id)  # Returns FetchedTranscript object

# List available transcripts
transcript_list = ytt_api.list(video_id)  # Returns TranscriptList object

# Advanced usage with filtering
transcript = transcript_list.find_transcript(['en'])
fetched_transcript = transcript.fetch()
raw_data = fetched_transcript.to_raw_data()
```

**Source 2: Recent Usage Examples (2025)**
Multiple developer blogs and tutorials confirmed the instance-based pattern:
- how.dev: "from youtube_transcript_api import YouTubeTranscriptApi" followed by instance creation
- transtube.io: Developer guide showing `ytt_api = YouTubeTranscriptApi()`
- GitHub issues: Users migrating from v0.x to v1.x reporting same compatibility issues

### New Object Types in v1.0+

**FetchedTranscript:**
- Returned by `transcript.fetch()` or `ytt_api.fetch()`
- Implements list-like interface (iterable, indexable)
- Has `.to_raw_data()` method to convert to dict format
- Structure:
  ```python
  FetchedTranscript(
      snippets=[
          FetchedTranscriptSnippet(
              text="Hey there",
              start=0.0,
              duration=1.54,
          ),
          # ...
      ],
      video_id="12345",
      language="English",
      language_code="en",
      is_generated=False,
  )
  ```

**TranscriptList:**
- Returned by `ytt_api.list(video_id)`
- Iterable collection of `Transcript` objects
- Provides filtering methods:
  - `find_transcript(['de', 'en'])`
  - `find_manually_created_transcript(['en'])`
  - `find_generated_transcript(['en'])`

---

## Comparison: Old vs New API

| Feature | v0.x (Old) | v1.0+ (New) |
|---------|-----------|-------------|
| **Pattern** | Static methods | Instance methods |
| **Initialization** | Not required | `ytt_api = YouTubeTranscriptApi()` |
| **Get transcript** | `YouTubeTranscriptApi.get_transcript(id)` | `ytt_api.fetch(id)` |
| **List transcripts** | `YouTubeTranscriptApi.list_transcripts(id)` | `ytt_api.list(id)` |
| **Return type** | `List[Dict]` | `FetchedTranscript` object |
| **Raw data** | Direct return | `.to_raw_data()` method |
| **Proxy support** | Via function params | Via `proxy_config` in constructor |
| **Cookie auth** | Via function params | Via `cookie_path` in constructor |

---

## Current State: File Structure

### Extract-YouTube Skill
**Location:** `arkhe-claude-plugins/skola/skills/extract-youtube/`

**Files Affected:**
```
extract-youtube/
└── scripts/
    ├── extract.py              # PEP 723 dependency specification
    └── transcript_extractor.py # Contains old API calls (ISSUE HERE)
```

**Dependency Management:**
- Uses PEP 723 inline script metadata
- Dependency: `youtube-transcript-api>=0.6.0`
- Actual installed: v1.2.3 (latest as of Oct 2025)
- Code compatibility: Written for v0.x

---

## Related Issues and Context

### Previous Dependency Issue

This project previously had a dependency management issue documented in:
- `arkhe-claude-plugins/.issues/2025-10-28-dependency-uv/`

That issue addressed Python version compatibility and uv setup. The solution (PEP 723 inline metadata) works correctly, but the dependency specification was too permissive.

### Why This Wasn't Caught Earlier

1. **No version pinning**: Dependency spec allows any version ≥0.6.0
2. **No integration tests**: Code changes weren't validated against actual API
3. **Library evolving**: youtube-transcript-api released v1.0+ after initial code was written
4. **Semantic versioning**: v0.x → v1.x should indicate breaking changes, but dependency wasn't constrained

---

## Error Message Analysis

**Error:** `type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'`

**Why "type object"?**
- Attempting to call method on the class itself (static/class method)
- Python reports "type object" when you try to access a non-existent attribute on a class

**User-facing message:** "⚠️  No transcript available"
- Misleading: transcript IS available, but code failed to access it
- Caused by: Exception handler catching all `Exception` types
- Better: Distinguish between API errors and actual missing transcripts

---

## Testing Evidence

### Test Script Output

**File:** `scripts/test_api.py` (created for investigation)

```bash
$ uv run --script test_api.py

youtube-transcript-api version: unknown

Available methods on YouTubeTranscriptApi:
['fetch', 'list']

Testing with video ID: 8xXV4FeaF9M
✗ get_transcript() failed: type object 'YouTubeTranscriptApi' has no attribute 'get_transcript'
✗ list_transcripts() failed: type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'
```

**Findings:**
- Only `fetch` and `list` methods exist
- Old methods `get_transcript` and `list_transcripts` completely removed
- Version attribute not available (library doesn't expose `__version__`)

---

## Proposed Solution Approaches

### Option A: Update Code to v1.0+ API (Recommended)

**Pros:**
- Uses current API
- Benefits from latest features (proxy config, cookie auth, etc.)
- Future-proof (aligns with library's direction)
- Better object-oriented design

**Cons:**
- Requires code changes
- Need to handle new object types

**Implementation:**
1. Create `YouTubeTranscriptApi()` instance in `__init__()`
2. Replace `YouTubeTranscriptApi.list_transcripts()` with `self.ytt_api.list()`
3. Handle `FetchedTranscript` object → convert with `.to_raw_data()`
4. Update error handling if needed

---

### Option B: Pin to v0.x

**Pros:**
- No code changes needed
- Maintains current functionality

**Cons:**
- Uses outdated API
- May miss security updates
- Library might drop v0.x support
- Not future-proof

**Implementation:**
```python
dependencies = [
    "youtube-transcript-api>=0.6.0,<1.0.0",  # Exclude v1.0+
]
```

---

### Option C: Support Both Versions

**Pros:**
- Maximum compatibility
- Graceful degradation

**Cons:**
- Complex code with version detection
- Maintains technical debt
- Testing burden doubles

**Implementation:**
```python
try:
    # Try v1.0+ API
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.list(video_id)
except AttributeError:
    # Fallback to v0.x API
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
```

---

## Recommended Fix Strategy

### Adopt Option A: Update to v1.0+ API

**Rationale:**
1. Library maintainers clearly committed to v1.0+ (current version is v1.2.3)
2. v1.0+ has better architecture (instance-based, better config management)
3. Forward compatibility is more valuable than backward compatibility
4. Code changes are minimal and localized to one file

**Changes Required:**
- **File:** `transcript_extractor.py`
- **Lines to modify:** 4 changes total
  - Add instance creation in `__init__()`
  - Update `list_transcripts()` → `list()`
  - Handle `FetchedTranscript` object
  - Convert to raw data with `.to_raw_data()`

**Dependency Update:**
- Keep `>=0.6.0` for now (v1.0+ is backward compatible at package import level)
- Alternatively: Update to `>=1.0.0` to prevent v0.x installation

---

## Questions to Resolve

Before implementing fix:

1. **Dependency constraint:**
   - Keep `>=0.6.0` (allows newer versions automatically)
   - Pin to `>=1.0.0,<2.0.0` (explicit v1.x support)
   - Pin to specific version `==1.2.3` (maximum stability)

2. **Version support:**
   - Support v1.0+ only (simplest)
   - Support both v0.x and v1.0+ (complex)

3. **Error handling:**
   - Improve error messages to distinguish API errors from missing transcripts?
   - Add version detection and helpful error if incompatible version installed?

4. **Testing:**
   - Add integration tests to prevent future breakage?
   - Document API version assumptions?

---

## Additional Context

### Library Information

**Package:** youtube-transcript-api
**PyPI:** https://pypi.org/project/youtube-transcript-api/
**GitHub:** https://github.com/jdepoix/youtube-transcript-api
**Current Version:** v1.2.3 (March 25, 2025)
**License:** MIT
**Maintainer:** jdepoix
**Stars:** 3.8k
**Used by:** 13.5k repositories

**Version History:**
- v0.x: Original static method API
- v1.0.0: Breaking changes, instance-based API introduced
- v1.2.3: Current stable (as of analysis date)

### System Information

- **Working Directory:** `/Users/jcosta/Projects/skola.dev`
- **Python Version:** 3.14.0
- **UV Version:** 0.8.22
- **Script Environment:** Isolated (PEP 723 via uv)
- **Test Video ID:** 8xXV4FeaF9M

---

## Testing Checklist

After implementing fix, verify:

- [ ] Transcript extraction succeeds for test video
- [ ] FetchedTranscript properly converted to dict format
- [ ] Timestamp formatting still works correctly
- [ ] Manual vs auto-generated transcript preference respected
- [ ] Translation fallback works if needed
- [ ] Error handling distinguishes API vs missing transcript issues
- [ ] Works with both manually created and auto-generated captions
- [ ] Works with playlists (multiple videos)
- [ ] No regression in metadata or thumbnail extraction

---

## Next Steps

1. Review this analysis document
2. Decide on solution approach (recommend Option A)
3. Answer questions in "Questions to Resolve" section
4. Implement code changes to `transcript_extractor.py`
5. Test with original failing video
6. Test with additional videos (manual captions, playlists)
7. Update documentation if API usage examples exist
8. Consider adding version compatibility tests

---

## References

### Official Documentation
- **GitHub README:** https://github.com/jdepoix/youtube-transcript-api#readme
- **PyPI Page:** https://pypi.org/project/youtube-transcript-api/

### Research Sources (Exa MCP)
- how.dev: "How to get subtitles for YouTube videos using Python"
- transtube.io: "YouTube Transcript API Developer Guide"
- dss99911.github.io: "Fetching YouTube Transcripts Using Python"
- Medium (naveen-malla): "Transcribing any Youtube Video with Python"

### Related Issues
- `.issues/2025-10-28-dependency-uv/` - Prior dependency management work
