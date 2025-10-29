#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "youtube-transcript-api>=0.6.0",
# ]
# ///
# -*- coding: utf-8 -*-
"""
YouTube Content Extractor

Main script for extracting YouTube video and playlist content including
transcripts and metadata.

Usage:
    uv run extract.py "https://youtube.com/watch?v=VIDEO_ID"
    uv run extract.py "https://youtube.com/playlist?list=PLAYLIST_ID"

    # Or make executable and run directly:
    chmod +x extract.py
    ./extract.py "https://youtube.com/watch?v=VIDEO_ID"
"""

import sys
import os
import argparse
import logging
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from youtube_client import YouTubeClient
from transcript_extractor import TranscriptExtractor
from file_writer import YouTubeFileWriter, sanitize_directory_name

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root():
    """
    Get the project root directory for youtube-research/.

    Uses current working directory (where Claude Code is running) as base.
    """
    return Path.cwd() / 'youtube-research'


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Extract YouTube video and playlist content including transcripts and metadata.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract single video
  uv run extract.py "https://youtube.com/watch?v=dQw4w9WgXcQ"

  # Extract playlist
  uv run extract.py "https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

  # Short URL
  uv run extract.py "https://youtu.be/dQw4w9WgXcQ"

  # Custom output directory
  uv run extract.py "URL" --output-dir my-video
        """
    )

    parser.add_argument('url', help='YouTube video or playlist URL')
    parser.add_argument('--output-dir', help='Custom output directory (default: video/playlist title)')
    parser.add_argument(
        '--skip-thumbnails',
        action='store_true',
        help='Skip downloading thumbnail images'
    )
    parser.add_argument(
        '--transcript-only',
        action='store_true',
        help='Only extract transcripts, skip metadata files'
    )

    return parser.parse_args()


def extract_video(
    client: YouTubeClient,
    transcript_extractor: TranscriptExtractor,
    video_id: str,
    output_dir: str,
    skip_thumbnails: bool = False,
    transcript_only: bool = False
):
    """
    Extract content from a single video.

    Args:
        client: YouTubeClient instance
        transcript_extractor: TranscriptExtractor instance
        video_id: YouTube video ID
        output_dir: Output directory name
        skip_thumbnails: Skip thumbnail download
        transcript_only: Only extract transcript
    """
    print(f"\n📹 Extracting video: {video_id}")

    # Fetch metadata
    print("  Fetching metadata...")
    metadata = client.get_video_metadata(video_id)

    if not metadata:
        print("  ✗ Failed to fetch metadata")
        return False

    video_title = metadata.get('title', 'Unknown Video')
    print(f"  ✓ Title: {video_title}")

    # Determine output directory
    if not output_dir:
        output_dir = sanitize_directory_name(video_title)

    project_root = get_project_root()
    output_path = project_root / output_dir

    print(f"  📁 Output: {output_path}\n")

    # Initialize file writer
    file_writer = YouTubeFileWriter(output_path, 'video')
    file_writer.create_directory_structure()

    # Extract transcript
    print("  Extracting transcript...")
    transcript_data = transcript_extractor.extract(video_id)

    if transcript_data:
        transcript_markdown = transcript_extractor.format_as_markdown(
            transcript_data,
            video_title,
            metadata.get('url', '')
        )
        file_writer.save_transcript(transcript_markdown)
        print("  ✓ Transcript saved")
    else:
        print("  ⚠️  No transcript available")

    if not transcript_only:
        # Save metadata
        print("  Saving metadata...")
        file_writer.save_metadata_json(metadata)
        file_writer.save_video_readme(metadata)
        print("  ✓ Metadata saved")

        # Download thumbnail
        if not skip_thumbnails:
            print("  Downloading thumbnail...")
            thumbnail_url = metadata.get('thumbnail_url')
            if thumbnail_url:
                if file_writer.save_thumbnail(thumbnail_url):
                    print("  ✓ Thumbnail saved")
                else:
                    print("  ⚠️  Thumbnail download failed")

    # Statistics
    stats = file_writer.get_statistics()
    print(f"\n✓ Extraction complete!")
    print(f"  Transcripts: {stats['transcripts']}")
    print(f"  Thumbnails: {stats['thumbnails']}")
    print(f"  Output: {output_path}")

    return True


def extract_playlist(
    client: YouTubeClient,
    transcript_extractor: TranscriptExtractor,
    playlist_id: str,
    output_dir: str,
    skip_thumbnails: bool = False,
    transcript_only: bool = False
):
    """
    Extract content from a playlist.

    Args:
        client: YouTubeClient instance
        transcript_extractor: TranscriptExtractor instance
        playlist_id: YouTube playlist ID
        output_dir: Output directory name
        skip_thumbnails: Skip thumbnail download
        transcript_only: Only extract transcripts
    """
    print(f"\n📚 Extracting playlist: {playlist_id}")

    # Fetch playlist metadata
    print("  Fetching playlist metadata...")
    playlist_metadata = client.get_playlist_metadata(playlist_id)

    if not playlist_metadata:
        print("  ✗ Failed to fetch playlist metadata")
        return False

    playlist_title = playlist_metadata.get('title', 'Unknown Playlist')
    videos = playlist_metadata.get('videos', [])
    video_count = len(videos)

    print(f"  ✓ Playlist: {playlist_title}")
    print(f"  ✓ Videos: {video_count}\n")

    if video_count == 0:
        print("  ⚠️  No videos found in playlist")
        return False

    # Determine output directory
    if not output_dir:
        output_dir = sanitize_directory_name(playlist_title)

    project_root = get_project_root()
    output_path = project_root / output_dir

    print(f"  📁 Output: {output_path}\n")

    # Initialize file writer
    file_writer = YouTubeFileWriter(output_path, 'playlist')
    file_writer.create_directory_structure()

    # Save playlist metadata
    if not transcript_only:
        print("  Saving playlist metadata...")
        file_writer.save_metadata_json(playlist_metadata)
        file_writer.save_playlist_readme(playlist_metadata)
        print("  ✓ Playlist metadata saved\n")

    # Extract each video
    print(f"  Extracting {video_count} videos...")
    print()

    transcript_stats = {
        'success': 0,
        'failed': 0,
        'no_transcript': 0
    }

    for idx, video in enumerate(videos, 1):
        video_id = video.get('id')
        video_title = video.get('title', 'Unknown')

        print(f"  [{idx:03d}/{video_count:03d}] {video_title}")

        if not video_id:
            print(f"    ⚠️  No video ID")
            transcript_stats['failed'] += 1
            continue

        # Extract transcript
        transcript_data = transcript_extractor.extract(video_id)

        if transcript_data:
            # Format filename with number prefix
            filename = f"{idx:03d}-{sanitize_directory_name(video_title)}"

            transcript_markdown = transcript_extractor.format_as_markdown(
                transcript_data,
                video_title,
                video.get('url', '')
            )
            file_writer.save_transcript(transcript_markdown, filename)
            print(f"    ✓ Transcript saved")
            transcript_stats['success'] += 1
        else:
            print(f"    ⚠️  No transcript available")
            transcript_stats['no_transcript'] += 1

        # Download thumbnail
        if not skip_thumbnails and not transcript_only:
            thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
            filename = f"{idx:03d}-thumbnail"
            if file_writer.save_thumbnail(thumbnail_url, filename):
                print(f"    ✓ Thumbnail saved")

        # Rate limiting: wait 1 second between videos
        if idx < video_count:
            time.sleep(1)

        print()

    # Summary
    print("=" * 60)
    print("Playlist Extraction Complete!")
    print("=" * 60)
    print(f"Playlist: {playlist_title}")
    print(f"Output: {output_path}")
    print(f"\nStatistics:")
    print(f"  Total videos: {video_count}")
    print(f"  Transcripts extracted: {transcript_stats['success']}")
    print(f"  No transcript: {transcript_stats['no_transcript']}")
    print(f"  Failed: {transcript_stats['failed']}")

    stats = file_writer.get_statistics()
    print(f"\nFiles created:")
    print(f"  {output_path}/README.md")
    print(f"  {output_path}/metadata.json")
    if stats['transcripts'] > 0:
        print(f"  Transcripts: {stats['transcripts']} files")
    if stats['thumbnails'] > 0:
        print(f"  Thumbnails: {stats['thumbnails']} files")

    print("=" * 60)

    return True


def main():
    """Main entry point."""
    # Check Python version
    if sys.version_info < (3, 8):
        print("=" * 60)
        print("ERROR: Python 3.8+ Required")
        print("=" * 60)
        print(f"Current Python version: {sys.version.split()[0]}")
        print("Required: Python 3.8 or higher")
        print("\nPlease run with:")
        print("  uv run extract.py <youtube-url>")
        print("=" * 60)
        sys.exit(1)

    # Parse arguments
    args = parse_arguments()

    print("=" * 60)
    print("YouTube Content Extractor")
    print("=" * 60)
    print(f"URL: {args.url}\n")

    try:
        # Initialize client
        print("🔌 Initializing YouTube client...")
        client = YouTubeClient()
        print("  ✓ Client ready\n")

        # Parse URL
        print("📋 Parsing URL...")
        url_info = client.parse_url(args.url)
        content_type = url_info['type']
        print(f"  ✓ Content type: {content_type}\n")

        # Initialize transcript extractor
        print("🔧 Initializing transcript extractor...")
        transcript_extractor = TranscriptExtractor()
        print("  ✓ Extractor ready\n")

        # Extract content based on type
        if content_type == 'video':
            video_id = url_info['video_id']
            success = extract_video(
                client,
                transcript_extractor,
                video_id,
                args.output_dir,
                args.skip_thumbnails,
                args.transcript_only
            )
        elif content_type == 'playlist':
            playlist_id = url_info['playlist_id']
            success = extract_playlist(
                client,
                transcript_extractor,
                playlist_id,
                args.output_dir,
                args.skip_thumbnails,
                args.transcript_only
            )
        else:
            print(f"  ✗ Unknown content type: {content_type}")
            success = False

        # Show transcript extractor statistics
        trans_stats = transcript_extractor.get_statistics()
        if trans_stats['error'] > 0 or trans_stats['disabled'] > 0:
            print("\nTranscript Extraction Issues:")
            if trans_stats['disabled'] > 0:
                print(f"  ⚠️  {trans_stats['disabled']} videos have transcripts disabled")
            if trans_stats['error'] > 0:
                print(f"  ✗ {trans_stats['error']} errors occurred")

        if success:
            print("\n✓ Done!")
            sys.exit(0)
        else:
            print("\n✗ Extraction failed")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Extraction interrupted by user")
        sys.exit(1)
    except Exception as error:
        print(f"\n✗ Error: {str(error)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
