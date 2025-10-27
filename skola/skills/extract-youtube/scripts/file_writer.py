#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Writer

Handles file organization and output for YouTube content extraction.
Mirrors the Udemy extraction pattern.
"""

import os
import json
import re
import urllib.request
from pathlib import Path
from typing import Dict, Optional
import logging


class YouTubeFileWriter:
    """Organize and write extracted YouTube content to files."""

    def __init__(self, output_path: Path, content_type: str):
        """
        Initialize file writer.

        Args:
            output_path: Base output directory
            content_type: 'video' or 'playlist'
        """
        self.output_path = Path(output_path)
        self.content_type = content_type
        self.resources_path = self.output_path / 'resources'

        self.statistics = {
            'transcripts': 0,
            'thumbnails': 0,
            'metadata': 0
        }

    def create_directory_structure(self):
        """Create output directory structure."""
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.resources_path.mkdir(exist_ok=True)

        logging.info(f"Created directory: {self.output_path}")
        logging.info(f"Created directory: {self.resources_path}")

    def save_video_readme(self, metadata: Dict[str, any]):
        """
        Save README.md for a single video.

        Args:
            metadata: Video metadata
        """
        readme_path = self.output_path / 'README.md'

        content = [
            f"# {metadata.get('title', 'Unknown Video')}",
            "",
            "## Video Information",
            "",
            f"**Channel:** {metadata.get('channel', 'Unknown')}",
            f"**Duration:** {metadata.get('duration', 'Unknown')}",
            f"**Upload Date:** {metadata.get('upload_date', 'Unknown')}",
            f"**Views:** {self._format_number(metadata.get('view_count'))}",
            f"**URL:** {metadata.get('url', '')}",
            "",
            "## Description",
            "",
            metadata.get('description', 'No description available.'),
            ""
        ]

        # Add chapters if available
        chapters = metadata.get('chapters', [])
        if chapters:
            content.extend([
                "## Chapters",
                ""
            ])
            for chapter in chapters:
                timestamp = chapter.get('timestamp', '')
                title = chapter.get('title', '')
                content.append(f"- **{timestamp}** - {title}")
            content.append("")

        # Add extraction info
        content.extend([
            "---",
            "",
            "**Extracted:** " + self._get_timestamp(),
            ""
        ])

        readme_path.write_text('\n'.join(content), encoding='utf-8')
        logging.info(f"Created README.md: {readme_path}")

    def save_playlist_readme(self, metadata: Dict[str, any]):
        """
        Save README.md for a playlist.

        Args:
            metadata: Playlist metadata
        """
        readme_path = self.output_path / 'README.md'

        content = [
            f"# {metadata.get('title', 'Unknown Playlist')}",
            "",
            "## Playlist Information",
            "",
            f"**Videos:** {metadata.get('video_count', 0)}",
            f"**URL:** {metadata.get('url', '')}",
            ""
        ]

        # Add description if available
        description = metadata.get('description', '')
        if description:
            content.extend([
                "## Description",
                "",
                description,
                ""
            ])

        # Add video list
        videos = metadata.get('videos', [])
        if videos:
            content.extend([
                "## Videos",
                ""
            ])
            for idx, video in enumerate(videos, 1):
                video_title = video.get('title', 'Unknown')
                video_url = video.get('url', '')
                content.append(f"{idx}. [{video_title}]({video_url})")
            content.append("")

        # Add extraction info
        content.extend([
            "---",
            "",
            "**Extracted:** " + self._get_timestamp(),
            ""
        ])

        readme_path.write_text('\n'.join(content), encoding='utf-8')
        logging.info(f"Created README.md: {readme_path}")

    def save_metadata_json(self, metadata: Dict[str, any]):
        """
        Save metadata as JSON file.

        Args:
            metadata: Video or playlist metadata
        """
        metadata_path = self.output_path / 'metadata.json'

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        self.statistics['metadata'] += 1
        logging.info(f"Saved metadata: {metadata_path}")

    def save_transcript(
        self,
        transcript_markdown: str,
        filename: Optional[str] = None
    ):
        """
        Save transcript as markdown file.

        Args:
            transcript_markdown: Formatted transcript content
            filename: Custom filename (without extension) or None for default
        """
        if filename is None:
            filename = 'transcript'

        # Sanitize filename
        filename = self._sanitize_filename(filename)

        transcript_path = self.output_path / f'{filename}.md'
        transcript_path.write_text(transcript_markdown, encoding='utf-8')

        self.statistics['transcripts'] += 1
        logging.info(f"Saved transcript: {transcript_path}")

    def save_thumbnail(
        self,
        thumbnail_url: str,
        filename: Optional[str] = None
    ) -> bool:
        """
        Download and save video thumbnail.

        Args:
            thumbnail_url: URL to thumbnail image
            filename: Custom filename or None for default

        Returns:
            True if successful, False otherwise
        """
        if filename is None:
            filename = 'thumbnail'

        # Sanitize filename
        filename = self._sanitize_filename(filename)

        # Determine file extension from URL
        ext = self._get_thumbnail_extension(thumbnail_url)
        thumbnail_path = self.resources_path / f'{filename}.{ext}'

        try:
            # Download thumbnail
            req = urllib.request.Request(
                thumbnail_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            with urllib.request.urlopen(req) as response:
                thumbnail_data = response.read()

            # Save thumbnail
            thumbnail_path.write_bytes(thumbnail_data)

            self.statistics['thumbnails'] += 1
            logging.info(f"Saved thumbnail: {thumbnail_path}")
            return True

        except Exception as e:
            logging.warning(f"Failed to download thumbnail: {str(e)}")
            return False

    def get_statistics(self) -> Dict[str, int]:
        """Get file writing statistics."""
        return self.statistics.copy()

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)

        # Replace spaces and special chars with hyphens
        filename = re.sub(r'[\s]+', '-', filename)

        # Remove leading/trailing hyphens and dots
        filename = filename.strip('-.')

        # Limit length
        if len(filename) > 200:
            filename = filename[:200]

        return filename or 'untitled'

    @staticmethod
    def _format_number(num: Optional[int]) -> str:
        """Format large numbers with commas."""
        if num is None:
            return 'Unknown'
        return f'{num:,}'

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp as ISO format string."""
        from datetime import datetime
        return datetime.now().isoformat()

    @staticmethod
    def _get_thumbnail_extension(url: str) -> str:
        """Determine image extension from URL."""
        if '.jpg' in url or '.jpeg' in url:
            return 'jpg'
        elif '.png' in url:
            return 'png'
        elif '.webp' in url:
            return 'webp'
        else:
            return 'jpg'  # Default


def sanitize_directory_name(name: str) -> str:
    """
    Sanitize directory name for filesystem.

    Args:
        name: Original directory name

    Returns:
        Sanitized directory name
    """
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)

    # Replace spaces with hyphens
    name = re.sub(r'\s+', '-', name)

    # Remove leading/trailing hyphens and dots
    name = name.strip('-.')

    # Limit length
    if len(name) > 200:
        name = name[:200]

    return name or 'untitled'
