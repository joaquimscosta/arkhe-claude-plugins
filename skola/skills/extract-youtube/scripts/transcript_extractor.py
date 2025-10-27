#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transcript Extractor

Handles transcript extraction from YouTube videos using youtube-transcript-api.
"""

from typing import Dict, List, Optional
import logging

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable
    )
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False
    logging.warning(
        "youtube-transcript-api not found. "
        "Install with: uv pip install youtube-transcript-api"
    )


class TranscriptExtractor:
    """Extract and format YouTube video transcripts."""

    def __init__(self):
        self.statistics = {
            'success': 0,
            'no_transcript': 0,
            'disabled': 0,
            'unavailable': 0,
            'error': 0
        }

    def extract(self, video_id: str, language: str = 'en') -> Optional[Dict[str, any]]:
        """
        Extract transcript for a video.

        Args:
            video_id: YouTube video ID
            language: Preferred language code (default: 'en')

        Returns:
            dict with transcript data or None if unavailable
        """
        if not TRANSCRIPT_API_AVAILABLE:
            logging.error("youtube-transcript-api not installed")
            self.statistics['error'] += 1
            return None

        try:
            # Try to get transcript list
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Prefer manually created transcripts over auto-generated
            transcript = None

            try:
                # Try to get manual transcript in preferred language
                transcript = transcript_list.find_manually_created_transcript([language])
            except NoTranscriptFound:
                try:
                    # Fallback to auto-generated transcript
                    transcript = transcript_list.find_generated_transcript([language])
                except NoTranscriptFound:
                    # Try to translate any available transcript to English
                    try:
                        available_transcripts = list(transcript_list)
                        if available_transcripts:
                            transcript = available_transcripts[0].translate(language)
                    except Exception:
                        pass

            if not transcript:
                logging.warning(f"No {language} transcript found for video {video_id}")
                self.statistics['no_transcript'] += 1
                return None

            # Fetch the transcript data
            transcript_data = transcript.fetch()

            result = {
                'video_id': video_id,
                'language': language,
                'is_generated': transcript.is_generated,
                'is_translatable': transcript.is_translatable,
                'entries': transcript_data,
                'text': self._format_transcript(transcript_data)
            }

            self.statistics['success'] += 1
            return result

        except TranscriptsDisabled:
            logging.warning(f"Transcripts disabled for video {video_id}")
            self.statistics['disabled'] += 1
            return None

        except VideoUnavailable:
            logging.error(f"Video {video_id} is unavailable")
            self.statistics['unavailable'] += 1
            return None

        except Exception as e:
            logging.error(f"Error extracting transcript for {video_id}: {str(e)}")
            self.statistics['error'] += 1
            return None

    def _format_transcript(self, transcript_data: List[Dict]) -> str:
        """
        Format transcript data as plain text with timestamps.

        Args:
            transcript_data: List of transcript entries

        Returns:
            Formatted transcript text
        """
        lines = []

        for entry in transcript_data:
            timestamp = self._format_timestamp(entry['start'])
            text = entry['text'].strip()

            # Clean up text (remove newlines, extra spaces)
            text = ' '.join(text.split())

            lines.append(f"[{timestamp}] {text}")

        return '\n\n'.join(lines)

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as HH:MM:SS or MM:SS timestamp.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60

        if hours > 0:
            return f'{hours:02d}:{minutes:02d}:{secs:02d}'
        else:
            return f'{minutes:02d}:{secs:02d}'

    def format_as_markdown(
        self,
        transcript_data: Dict[str, any],
        video_title: str,
        video_url: str
    ) -> str:
        """
        Format transcript as markdown document.

        Args:
            transcript_data: Transcript data from extract()
            video_title: Video title
            video_url: Video URL

        Returns:
            Markdown formatted transcript
        """
        lines = [
            f"# {video_title}",
            "",
            f"**Video URL:** {video_url}",
            f"**Language:** {transcript_data['language']}",
            f"**Transcript Type:** {'Auto-generated' if transcript_data['is_generated'] else 'Manual'}",
            "",
            "---",
            "",
            "## Transcript",
            ""
        ]

        # Add formatted transcript text
        lines.append(transcript_data['text'])

        return '\n'.join(lines)

    def get_statistics(self) -> Dict[str, int]:
        """Get extraction statistics."""
        return self.statistics.copy()

    def reset_statistics(self):
        """Reset extraction statistics."""
        for key in self.statistics:
            self.statistics[key] = 0
