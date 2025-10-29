#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "youtube-transcript-api>=0.6.0",
# ]
# ///

from youtube_transcript_api import YouTubeTranscriptApi
import youtube_transcript_api

print("youtube-transcript-api version:", getattr(youtube_transcript_api, '__version__', 'unknown'))
print("\nAvailable methods on YouTubeTranscriptApi:")
print([m for m in dir(YouTubeTranscriptApi) if not m.startswith('_')])

# Test with a video ID
video_id = "8xXV4FeaF9M"
print(f"\nTesting with video ID: {video_id}")

try:
    result = YouTubeTranscriptApi.get_transcript(video_id)
    print("✓ get_transcript() works!")
    print(f"  Got {len(result)} transcript entries")
except Exception as e:
    print(f"✗ get_transcript() failed: {e}")

try:
    result = YouTubeTranscriptApi.list_transcripts(video_id)
    print("✓ list_transcripts() works!")
    print(f"  Result type: {type(result)}")
except Exception as e:
    print(f"✗ list_transcripts() failed: {e}")
