---
description: Extract educational content from various sources (Udemy courses, YouTube videos, blog articles) by providing a URL. Auto-detects source and delegates to appropriate extraction skill.
---

# Extract Educational Content

Extract educational content from multiple sources for offline study, research, and analysis.

## Supported Sources

- **Udemy** - Course content including video transcripts, articles, quizzes, and resources
- **YouTube** - Video transcripts and metadata for videos and playlists
- **Blog Articles** - *(Coming soon)* Article content and code examples

## How to Use

Simply provide the URL of the educational content you want to extract:

```
/extract https://www.udemy.com/course/python-complete/
```

The command will:
1. Analyze the URL to detect the source platform
2. Automatically invoke the appropriate extraction skill
3. Guide you through any required setup (authentication, etc.)
4. Extract and organize the content

## URL Pattern Detection

The command identifies sources based on URL patterns:

- **Udemy**: `udemy.com/course/*`
- **YouTube**: `youtube.com/watch?v=*` or `youtu.be/*` or `youtube.com/playlist?list=*`
- **Blog**: Other educational content URLs → *(Coming soon)*

## Requirements by Source

### Udemy
- Python 3.8+
- Valid Udemy session cookies in `skola-research/udemy/cookies.json`
- Must be enrolled in the course

### YouTube
- Python 3.8+
- uv package manager
- No authentication required for public videos

### Blog Articles (Coming Soon)
- Python 3.8+
- No authentication required for public articles

## Examples

### Extract Udemy Course
```
/extract https://www.udemy.com/course/complete-python-bootcamp/
```

### Extract YouTube Video
```
/extract https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Extract YouTube Playlist
```
/extract https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf
```

### Extract Blog Article (Coming Soon)
```
/extract https://realpython.com/python-classes/
```

## Output

All extracted content is organized in source-specific directories:

```
skola-research/
├── udemy/              # Udemy courses
├── youtube/            # YouTube videos and playlists
└── blog/               # Blog articles (coming soon)
```

Each source maintains its own directory structure optimized for that content type.

## Error Handling

**Unsupported URL**: If the URL doesn't match any known source pattern, you'll receive a message listing supported sources and a request to use the source-specific skill directly.

**Authentication Required**: For sources requiring authentication (like Udemy), you'll be guided through the setup process.

**Rate Limiting**: Some platforms have rate limits. The extractors handle this automatically with retries and backoff.

## Direct Skill Access

You can also invoke extraction skills directly without using this command. Claude Code will auto-invoke them when appropriate context is detected (e.g., mentioning "extract this Udemy course").

## Future Enhancements

Planned additions to this unified extraction command:

- YouTube video and playlist extraction
- Blog article and tutorial extraction
- Coursera, edX, and other MOOC platforms
- Documentation site extraction (MDN, official docs)
- Interactive coding platform extraction (LeetCode, HackerRank)
