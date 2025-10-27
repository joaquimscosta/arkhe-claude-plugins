#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Client

Handles URL parsing, video/playlist detection, and metadata extraction
for YouTube content.
"""

import re
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Tuple


class YouTubeURLParser:
    """Parse and validate YouTube URLs."""

    # YouTube video ID is exactly 11 characters: [A-Za-z0-9_-]{11}
    VIDEO_ID_PATTERN = re.compile(r'[A-Za-z0-9_-]{11}')

    @staticmethod
    def parse_url(url: str) -> Dict[str, any]:
        """
        Parse YouTube URL and extract video/playlist information.

        Args:
            url: YouTube URL

        Returns:
            dict with 'type' (video/playlist), 'video_id', 'playlist_id'

        Raises:
            ValueError: If URL format is invalid
        """
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)

        result = {
            'type': None,
            'video_id': None,
            'playlist_id': None,
            'url': url
        }

        # Check for playlist
        if 'list' in query_params:
            result['playlist_id'] = query_params['list'][0]
            result['type'] = 'playlist'

        # Extract video ID from various URL formats
        video_id = None

        # Format: youtube.com/watch?v=VIDEO_ID
        if 'v' in query_params:
            video_id = query_params['v'][0]

        # Format: youtu.be/VIDEO_ID
        elif parsed.netloc == 'youtu.be':
            path_parts = parsed.path.strip('/').split('/')
            if path_parts:
                video_id = path_parts[0]

        # Format: youtube.com/embed/VIDEO_ID or youtube.com/v/VIDEO_ID
        elif '/embed/' in parsed.path or '/v/' in parsed.path:
            match = re.search(r'/(embed|v)/([A-Za-z0-9_-]{11})', parsed.path)
            if match:
                video_id = match.group(2)

        # Format: youtube.com/shorts/VIDEO_ID
        elif '/shorts/' in parsed.path:
            match = re.search(r'/shorts/([A-Za-z0-9_-]{11})', parsed.path)
            if match:
                video_id = match.group(2)

        # Validate video ID format
        if video_id and YouTubeURLParser.VIDEO_ID_PATTERN.fullmatch(video_id):
            result['video_id'] = video_id
            if result['type'] is None:
                result['type'] = 'video'

        if result['type'] is None:
            raise ValueError(f"Could not extract video or playlist ID from URL: {url}")

        return result


class YouTubeMetadataExtractor:
    """Extract metadata from YouTube videos and playlists."""

    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

    def _fetch_page(self, url: str) -> str:
        """Fetch YouTube page content."""
        req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')

    def _extract_json_data(self, html: str, pattern: str) -> Optional[Dict]:
        """Extract JSON data from YouTube page HTML."""
        match = re.search(pattern, html)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def get_video_metadata(self, video_id: str) -> Dict[str, any]:
        """
        Extract metadata for a single video.

        Args:
            video_id: YouTube video ID

        Returns:
            dict with video metadata
        """
        url = f'https://www.youtube.com/watch?v={video_id}'
        html = self._fetch_page(url)

        metadata = {
            'id': video_id,
            'url': url,
            'title': self._extract_title(html),
            'channel': self._extract_channel(html),
            'description': self._extract_description(html),
            'duration': self._extract_duration(html),
            'upload_date': self._extract_upload_date(html),
            'view_count': self._extract_view_count(html),
            'thumbnail_url': f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg',
            'chapters': self._extract_chapters(html)
        }

        return metadata

    def get_playlist_metadata(self, playlist_id: str) -> Dict[str, any]:
        """
        Extract metadata for a playlist.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            dict with playlist metadata and video list
        """
        url = f'https://www.youtube.com/playlist?list={playlist_id}'
        html = self._fetch_page(url)

        # Extract initial data JSON
        initial_data = self._extract_json_data(
            html,
            r'var ytInitialData = ({.*?});'
        )

        videos = []
        playlist_title = 'Unknown Playlist'
        playlist_description = ''

        if initial_data:
            # Navigate the complex YouTube JSON structure
            try:
                # Extract playlist title
                sidebar = initial_data.get('sidebar', {})
                playlist_renderer = (
                    sidebar.get('playlistSidebarRenderer', {})
                    .get('items', [{}])[0]
                    .get('playlistSidebarPrimaryInfoRenderer', {})
                )

                title_runs = playlist_renderer.get('title', {}).get('runs', [])
                if title_runs:
                    playlist_title = title_runs[0].get('text', playlist_title)

                # Extract playlist description
                desc_runs = playlist_renderer.get('description', {}).get('simpleText', '')
                playlist_description = desc_runs

                # Extract videos
                contents = (
                    initial_data.get('contents', {})
                    .get('twoColumnBrowseResultsRenderer', {})
                    .get('tabs', [{}])[0]
                    .get('tabRenderer', {})
                    .get('content', {})
                    .get('sectionListRenderer', {})
                    .get('contents', [{}])[0]
                    .get('itemSectionRenderer', {})
                    .get('contents', [{}])[0]
                    .get('playlistVideoListRenderer', {})
                    .get('contents', [])
                )

                for item in contents:
                    video_renderer = item.get('playlistVideoRenderer', {})
                    if video_renderer:
                        video_id = video_renderer.get('videoId')
                        if video_id:
                            video_title_runs = video_renderer.get('title', {}).get('runs', [])
                            video_title = video_title_runs[0].get('text', 'Unknown') if video_title_runs else 'Unknown'

                            videos.append({
                                'id': video_id,
                                'title': video_title,
                                'url': f'https://www.youtube.com/watch?v={video_id}'
                            })
            except (KeyError, IndexError):
                pass

        metadata = {
            'id': playlist_id,
            'url': url,
            'title': playlist_title,
            'description': playlist_description,
            'video_count': len(videos),
            'videos': videos
        }

        return metadata

    def _extract_title(self, html: str) -> str:
        """Extract video title from HTML."""
        # Try og:title meta tag
        match = re.search(r'<meta property="og:title" content="(.*?)"', html)
        if match:
            return self._unescape_html(match.group(1))

        # Fallback to <title> tag
        match = re.search(r'<title>(.*?)</title>', html)
        if match:
            title = match.group(1)
            # Remove " - YouTube" suffix
            return self._unescape_html(title.replace(' - YouTube', ''))

        return 'Unknown Title'

    def _extract_channel(self, html: str) -> str:
        """Extract channel name from HTML."""
        match = re.search(r'"author":"(.*?)"', html)
        if match:
            return self._unescape_html(match.group(1))
        return 'Unknown Channel'

    def _extract_description(self, html: str) -> str:
        """Extract video description from HTML."""
        match = re.search(r'<meta property="og:description" content="(.*?)"', html)
        if match:
            return self._unescape_html(match.group(1))
        return ''

    def _extract_duration(self, html: str) -> Optional[str]:
        """Extract video duration from HTML."""
        match = re.search(r'"lengthSeconds":"(\d+)"', html)
        if match:
            seconds = int(match.group(1))
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60

            if hours > 0:
                return f'{hours}:{minutes:02d}:{secs:02d}'
            else:
                return f'{minutes}:{secs:02d}'
        return None

    def _extract_upload_date(self, html: str) -> Optional[str]:
        """Extract upload date from HTML."""
        match = re.search(r'"uploadDate":"(.*?)"', html)
        if match:
            return match.group(1)
        return None

    def _extract_view_count(self, html: str) -> Optional[int]:
        """Extract view count from HTML."""
        match = re.search(r'"viewCount":"(\d+)"', html)
        if match:
            return int(match.group(1))
        return None

    def _extract_chapters(self, html: str) -> List[Dict[str, str]]:
        """Extract video chapters from description."""
        # Chapters are typically in the description in format: 00:00 Chapter Name
        chapters = []
        description = self._extract_description(html)

        # Look for timestamp patterns (00:00 or 0:00)
        chapter_pattern = re.compile(r'(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)')

        for line in description.split('\n'):
            match = chapter_pattern.match(line.strip())
            if match:
                timestamp = match.group(1)
                title = match.group(2).strip()
                chapters.append({
                    'timestamp': timestamp,
                    'title': title
                })

        return chapters

    @staticmethod
    def _unescape_html(text: str) -> str:
        """Unescape HTML entities."""
        from html import unescape
        return unescape(text)


class YouTubeClient:
    """Main client for YouTube operations."""

    def __init__(self):
        self.url_parser = YouTubeURLParser()
        self.metadata_extractor = YouTubeMetadataExtractor()

    def parse_url(self, url: str) -> Dict[str, any]:
        """Parse YouTube URL."""
        return self.url_parser.parse_url(url)

    def get_video_metadata(self, video_id: str) -> Dict[str, any]:
        """Get metadata for a video."""
        return self.metadata_extractor.get_video_metadata(video_id)

    def get_playlist_metadata(self, playlist_id: str) -> Dict[str, any]:
        """Get metadata for a playlist."""
        return self.metadata_extractor.get_playlist_metadata(playlist_id)
