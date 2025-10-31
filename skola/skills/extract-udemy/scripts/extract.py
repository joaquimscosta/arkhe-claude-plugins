#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
# -*- coding: utf-8 -*-
"""
Udemy Course Extractor

Main script for extracting Udemy course content including structure,
transcripts, and metadata.

Usage:
    uv run extract.py "https://SITE.udemy.com/course/course-name/" [output-dir]
"""

import sys
import os
import re
import json
import argparse
import logging
import threading
from pathlib import Path
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_client import UdemyAPIClient, _print_error, _print_warning, _print_success, _print_progress
from auth import Authenticator
from file_writer import CourseFileWriter
from content_extractors import ArticleExtractor, QuizExtractor, ResourceExtractor, ExternalResourceLinker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def parse_course_url(url):
    """
    Extract course information from Udemy URL.

    Args:
        url: Udemy course URL

    Returns:
        dict with 'site', 'course_id', 'course_slug'
    """
    parsed = urlparse(url)
    site = parsed.netloc

    # Extract course slug from path
    # Example: /course/react-complete-guide/ → react-complete-guide
    match = re.search(r'/course/([^/]+)', parsed.path)
    if not match:
        raise ValueError(f"Could not extract course ID from URL: {url}")

    course_slug = match.group(1)

    return {
        'site': site,
        'course_slug': course_slug,
        'base_url': f"{parsed.scheme}://{site}"
    }


def get_project_root():
    """
    Get project root for skola-research/udemy/.

    Priority:
    1. SKOLA_RESEARCH_DIR env var (if set) + '/udemy'
    2. Upward search for 'skola-research' directory + '/udemy'
    3. Path.cwd() / 'skola-research' / 'udemy' (fallback)

    Returns:
        Path: Absolute path to skola-research/udemy directory
    """
    # Check environment variable
    env_base = os.getenv('SKOLA_RESEARCH_DIR')
    if env_base:
        return Path(env_base).expanduser().resolve() / 'udemy'

    # Upward search for skola-research
    current = Path.cwd().resolve()
    while True:
        candidate = current / 'skola-research'
        if candidate.exists() and candidate.is_dir():
            return candidate / 'udemy'
        if current.parent == current:
            break
        current = current.parent

    # Fallback
    return Path.cwd() / 'skola-research' / 'udemy'


def validate_prerequisites(api_client, course_slug, course_url):
    """
    Run pre-flight checks before extraction.

    Args:
        api_client: UdemyAPIClient instance
        course_slug: Course identifier slug
        course_url: Full course URL

    Returns:
        dict: {'success': bool, 'issues': list, 'warnings': list}
    """
    print("🔍 Running pre-extraction validation...")
    print("-" * 60)

    results = {'success': True, 'issues': [], 'warnings': []}

    # 1. Check course enrollment
    print("  [1/3] Checking course enrollment...")
    course_id = api_client.resolve_course_id(course_slug)
    if not course_id:
        results['success'] = False
        results['issues'].append("Course not found in enrolled courses")
        _print_error(f"    ❌ Course not enrolled")
        _print_error(f"    → Please enroll at: {course_url}")
        return results
    _print_success(f"    ✓ Course enrolled (ID: {course_id})")

    # 2. Verify API access
    print("  [2/3] Verifying API access...")
    details = api_client.get_course_details(course_id)
    if not details:
        results['success'] = False
        results['issues'].append("Cannot access course details API")
        _print_error(f"    ❌ API access failed")
        return results
    _print_success(f"    ✓ API access confirmed")

    # 3. Test transcript availability
    print("  [3/3] Testing transcript access...")
    structure = api_client.get_course_structure(course_slug)
    if not structure:
        results['success'] = False
        results['issues'].append("Cannot fetch course structure")
        _print_error(f"    ❌ Course structure unavailable")
        return results

    # Find first video lecture and test transcript
    sections = structure.get('sections', [])
    has_video = False
    for section in sections:
        for lecture in section.get('lectures', []):
            asset = lecture.get('asset', {})
            if asset.get('asset_type') == 'Video':
                has_video = True
                lecture_id = lecture.get('id')
                test_transcript = api_client.get_lecture_transcript(course_id, lecture_id)
                if test_transcript:
                    _print_success(f"    ✓ Transcript access confirmed ({len(test_transcript)} segments)")
                else:
                    results['warnings'].append("Test lecture has no transcript")
                    _print_warning(f"    ⚠️  Test lecture has no transcript (may be expected)")
                break
        if has_video:
            break

    if not has_video:
        total_lectures = sum(len(s.get('lectures', [])) for s in sections)
        results['warnings'].append(f"No video lectures found ({total_lectures} total lectures)")
        _print_warning(f"    ⚠️  No video lectures found")

    print("-" * 60)

    # Display results
    if results['issues']:
        _print_error("❌ Validation FAILED:")
        for issue in results['issues']:
            _print_error(f"  - {issue}")
    elif results['warnings']:
        _print_warning("⚠️  Validation passed with warnings:")
        for warning in results['warnings']:
            _print_warning(f"  - {warning}")
    else:
        _print_success("✅ All validation checks passed!")

    print()
    return results


class ParallelTranscriptDownloader:
    """Download transcripts in parallel with rate limiting."""

    def __init__(self, api_client, max_workers=2, rate_limit=0.5):
        """
        Initialize parallel downloader.

        Args:
            api_client: UdemyAPIClient instance
            max_workers: Number of parallel workers (default: 2)
            rate_limit: Minimum seconds between requests (default: 0.5)
        """
        self.api_client = api_client
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.last_request_time = time.time()
        self.lock = threading.Lock()
        logger.debug(f"Parallel downloader initialized with {max_workers} workers, rate limit: {rate_limit}s")

    def _download_with_rate_limit(self, course_id, lecture_id):
        """Download transcript with rate limiting."""
        with self.lock:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit:
                sleep_time = self.rate_limit - elapsed
                time.sleep(sleep_time)
            self.last_request_time = time.time()

        return self.api_client.get_lecture_transcript(course_id, lecture_id)

    def download_batch(self, course_id, lectures):
        """
        Download transcripts for a batch of lectures in parallel.

        Args:
            course_id: Course ID
            lectures: List of lecture dicts with 'id' and 'title'

        Returns:
            dict: Mapping of lecture_id -> transcript data (or None if failed)
        """
        results = {}
        futures = {}

        logger.debug(f"Starting parallel download of {len(lectures)} transcripts...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            for lecture in lectures:
                lecture_id = lecture.get('id')
                if lecture_id:
                    future = executor.submit(
                        self._download_with_rate_limit,
                        course_id,
                        lecture_id
                    )
                    futures[future] = lecture

            # Collect results as they complete
            for future in as_completed(futures):
                lecture = futures[future]
                lecture_id = lecture.get('id')
                try:
                    transcript = future.result()
                    results[lecture_id] = transcript
                    logger.debug(f"Completed download for lecture {lecture_id}")
                except Exception as e:
                    logger.error(f"Failed to download transcript for lecture {lecture_id}: {e}")
                    results[lecture_id] = None

        logger.debug(f"Parallel batch complete: {len([r for r in results.values() if r])} successful")
        return results


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Extract Udemy course content including transcripts, articles, quizzes, and resources.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all content types (default)
  uv run extract.py "https://SITE.udemy.com/course/java-multithreading/"

  # Extract only transcripts
  uv run extract.py "https://SITE.udemy.com/course/react-guide/" --content-types video

  # Extract videos and articles, skip promotional content
  uv run extract.py "URL" --content-types video,article --skip-promotional

  # Custom output directory
  uv run extract.py "URL" --output-dir my-course
        """
    )

    parser.add_argument('course_url', help='Udemy course URL')
    parser.add_argument('--output-dir', help='Custom output directory (default: course slug)')
    parser.add_argument(
        '--content-types',
        default='all',
        help='Comma-separated content types to extract: video,article,quiz,resource (default: all)'
    )
    parser.add_argument(
        '--skip-promotional',
        action='store_true',
        help='Skip promotional/bonus lectures'
    )
    parser.add_argument(
        '--quiz-format',
        choices=['yaml', 'json'],
        default='yaml',
        help='Output format for quizzes (default: yaml)'
    )
    parser.add_argument(
        '--download-resources',
        action='store_true',
        default=True,
        help='Download supplementary resource files (PDFs, code, etc.) - enabled by default'
    )
    parser.add_argument(
        '--no-download-resources',
        action='store_false',
        dest='download_resources',
        help='Skip downloading resource files, only create catalog'
    )
    parser.add_argument(
        '--max-resource-size',
        type=int,
        default=100,
        help='Maximum resource file size to download in MB (default: 100)'
    )

    # Phase 2: Robustness options
    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum retry attempts for failed requests (default: 3)'
    )
    parser.add_argument(
        '--no-retry',
        action='store_true',
        help='Disable retry logic (fail immediately on errors)'
    )
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Force fresh extraction, ignore any previous progress'
    )

    # Phase 3: Diagnostics options
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable verbose debug logging'
    )

    # Phase 4: Performance options
    parser.add_argument(
        '--parallel-workers',
        type=int,
        default=2,
        help='Number of parallel download workers (default: 2, max: 5)'
    )
    parser.add_argument(
        '--no-parallel',
        action='store_true',
        help='Disable parallel downloads (use sequential mode)'
    )

    return parser.parse_args()


def main():
    # Check Python version
    if sys.version_info < (3, 8):
        print("=" * 60)
        print("ERROR: Python 3.8+ Required")
        print("=" * 60)
        print(f"Current Python version: {sys.version.split()[0]}")
        print("Required: Python 3.8 or higher")
        print("\nPlease run with:")
        print("  uv run extract.py <course-url>")
        print("\nOr make script executable and run:")
        print("  ./extract.py <course-url>")
        print("=" * 60)
        sys.exit(1)

    # Parse arguments
    args = parse_arguments()

    # Configure logging based on debug flag
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S',
            force=True
        )
        logger.debug("Debug mode enabled")
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            force=True
        )

    course_url = args.course_url
    output_dir = args.output_dir

    # Parse content types
    if args.content_types == 'all':
        content_types = {'video', 'article', 'quiz', 'resource'}
    else:
        content_types = set(args.content_types.split(','))

    # Configuration
    config = {
        'content_types': content_types,
        'skip_promotional': args.skip_promotional,
        'quiz_format': args.quiz_format,
        'download_resources': args.download_resources,
        'max_resource_size_mb': args.max_resource_size
    }

    print("=" * 60)
    print("Udemy Course Extractor")
    print("=" * 60)
    print(f"Course URL: {course_url}\n")

    try:
        # Parse course URL
        print("📋 Parsing course URL...")
        course_info = parse_course_url(course_url)
        print(f"  Site: {course_info['site']}")
        print(f"  Course: {course_info['course_slug']}\n")

        # Determine output directory
        if not output_dir:
            output_dir = course_info['course_slug']

        project_root = get_project_root()
        output_path = project_root / output_dir

        print(f"📁 Output directory: {output_path}\n")

        # Initialize authenticator
        print("🔐 Initializing authentication...")
        auth = Authenticator(project_root)
        auth_headers = auth.get_auth_headers()
        print("  ✓ Authentication successful\n")

        # Initialize API client
        print("🔌 Initializing API client...")
        max_retries = 0 if args.no_retry else args.max_retries
        api_client = UdemyAPIClient(
            base_url=course_info['base_url'],
            auth_headers=auth_headers,
            project_root=project_root,
            max_retries=max_retries
        )
        print("  ✓ API client ready\n")

        # Run pre-extraction validation
        validation = validate_prerequisites(api_client, course_info['course_slug'], course_url)
        if not validation['success']:
            _print_error("\n❌ Cannot proceed with extraction. Please resolve the issues above.")
            sys.exit(1)

        # Initialize content extractors
        print("🔧 Initializing content extractors...")
        article_extractor = ArticleExtractor(api_client, config)
        quiz_extractor = QuizExtractor(api_client, config)
        resource_extractor = ResourceExtractor(api_client, config)
        external_link_scanner = ExternalResourceLinker(api_client, config)
        print("  ✓ Extractors ready\n")

        # Fetch course structure
        print("📚 Fetching course structure...")
        course_data = api_client.get_course_structure(course_info['course_slug'])

        if not course_data:
            _print_error("❌ Failed to fetch course structure")
            _print_error("    Verify you're enrolled in the course and cookies are valid")
            sys.exit(1)

        course_title = course_data.get('title', course_info['course_slug'])
        sections = course_data.get('sections', [])
        total_lectures = sum(len(s.get('lectures', [])) for s in sections)

        print(f"  ✓ Course: {course_title}")
        print(f"  ✓ Sections: {len(sections)}")
        print(f"  ✓ Total lectures: {total_lectures}\n")

        # Initialize file writer
        print("💾 Initializing file writer...")
        file_writer = CourseFileWriter(
            output_path=output_path,
            course_name=course_info['course_slug'],
            course_url=course_url,
            project_root=project_root
        )
        file_writer.create_directory_structure()
        print("  ✓ Directory structure created\n")

        # Handle resume functionality
        if args.no_resume and file_writer.progress_file.exists():
            print("🔄 Clearing previous progress (--no-resume flag)...")
            file_writer.clear_progress()
            print("  ✓ Progress cleared\n")
        elif file_writer.progress_file.exists():
            completed_count = len(file_writer.completed_lectures)
            remaining_count = total_lectures - completed_count
            _print_progress(f"🔄 Resuming previous extraction...")
            print(f"  {completed_count} lectures already completed, {remaining_count} remaining\n")

        # Save course metadata
        print("📝 Saving course metadata...")
        file_writer.save_course_readme(course_data)
        print("  ✓ README.md created\n")

        # Extract content
        print("📜 Extracting course content...")
        print(f"  Processing {total_lectures} lectures...")
        print(f"  Content types: {', '.join(sorted(content_types))}\n")

        lecture_number = 1
        extraction_counts = {
            'transcripts': 0,
            'articles': 0,
            'quizzes': 0,
            'resources': 0,
            'skipped': 0
        }

        for section_idx, section in enumerate(sections, 1):
            section_title = section.get('title', f'Section {section_idx}')
            lectures = section.get('lectures', [])

            print(f"  Section {section_idx}/{len(sections)}: {section_title}")
            print(f"    {len(lectures)} lectures")

            for lecture in lectures:
                lecture_id = lecture.get('id')
                lecture_title = lecture.get('title', f'Lecture {lecture_number}')

                if not lecture_id:
                    print(f"    [{lecture_number:03d}] ⚠️  {lecture_title} - No lecture ID")
                    extraction_counts['skipped'] += 1
                    lecture_number += 1
                    continue

                # Check if lecture already completed (resume functionality)
                if file_writer.is_lecture_complete(lecture_id):
                    print(f"    [{lecture_number:03d}] ⏭️  {lecture_title} - Already extracted (skipping)")
                    lecture_number += 1
                    continue

                # Detect content type
                content_type = api_client.detect_content_type(lecture)

                # Check if we should skip promotional content
                if config['skip_promotional'] and content_type == 'promotional':
                    print(f"    [{lecture_number:03d}] ⊘ {lecture_title} - Promotional (skipped)")
                    extraction_counts['skipped'] += 1
                    lecture_number += 1
                    continue

                # Track what was extracted for this lecture
                extracted_items = []

                # Extract video transcript
                if content_type == 'video' and 'video' in content_types:
                    transcript = api_client.get_lecture_transcript(
                        course_id=course_data['id'],
                        lecture_id=lecture_id
                    )
                    if transcript:
                        file_writer.save_transcript(
                            lecture_number=lecture_number,
                            lecture_title=lecture_title,
                            transcript_data=transcript
                        )
                        extraction_counts['transcripts'] += 1
                        extracted_items.append('transcript')

                        # Scan transcript for external links
                        transcript_text = ' '.join([cue.get('text', '') for cue in transcript])
                        external_link_scanner.scan_content(
                            transcript_text, 'transcript', lecture_number, lecture_title
                        )

                # Extract article content
                if content_type in ['article', 'coding_solution', 'technical_resource', 'promotional'] and 'article' in content_types:
                    article_data = article_extractor.extract(lecture)
                    if article_data:
                        file_writer.save_article(
                            lecture_number=lecture_number,
                            lecture_title=lecture_title,
                            article_data=article_data
                        )
                        extraction_counts['articles'] += 1
                        extracted_items.append(f"article({article_data['article_type']})")

                        # Scan article for external links
                        article_content = article_data.get('content', '')
                        external_link_scanner.scan_content(
                            article_content, 'article', lecture_number, lecture_title
                        )

                # Extract quiz
                if content_type == 'quiz' and 'quiz' in content_types:
                    quiz_data = quiz_extractor.extract(lecture)
                    if quiz_data:
                        file_writer.save_quiz(
                            lecture_number=lecture_number,
                            lecture_title=lecture_title,
                            quiz_data=quiz_data,
                            output_format=config['quiz_format']
                        )
                        extraction_counts['quizzes'] += 1
                        extracted_items.append('quiz')

                # Extract resources
                if 'resource' in content_types:
                    resource_data = resource_extractor.extract(lecture)
                    if resource_data:
                        # Save downloaded resource files
                        resources = resource_data.get('resources', [])
                        for resource in resources:
                            if resource.get('downloaded') and resource.get('download_path'):
                                file_writer.save_resource_file(
                                    lecture_number=lecture_number,
                                    lecture_title=lecture_title,
                                    resource_download_data=resource['download_path']
                                )

                        # Track resources for consolidated summary
                        file_writer.track_resources(
                            section_title=section_title,
                            lecture_number=lecture_number,
                            lecture_title=lecture_title,
                            resource_data=resource_data
                        )

                        # Update extracted items message
                        download_count = resource_data.get('metadata', {}).get('downloaded_count', 0)
                        if download_count > 0:
                            extracted_items.append(f"resources({download_count} files)")
                        else:
                            extracted_items.append('resources(catalog)')

                # Display result
                if extracted_items:
                    items_str = ', '.join(extracted_items)
                    print(f"    [{lecture_number:03d}] ✓ {lecture_title} [{items_str}]")
                else:
                    print(f"    [{lecture_number:03d}] ⚠️  {lecture_title} - No extractable content")
                    extraction_counts['skipped'] += 1

                # Mark lecture as complete for resume functionality
                file_writer.mark_lecture_complete(lecture_id)

                lecture_number += 1

                # Rate limiting: wait 0.5 seconds between requests
                time.sleep(0.5)

            print()  # Blank line between sections

        # Generate and save external links summary
        print("\n🔗 Processing external resource links...")
        links_summary = external_link_scanner.generate_summary()
        if links_summary and links_summary.get('total_resources', 0) > 0:
            file_writer.save_external_links(links_summary)
        else:
            print("  ⚠️  No external links found")

        # Generate consolidated downloaded resources summary
        print("\n📦 Generating downloaded resources summary...")
        file_writer.generate_downloaded_resources_summary(config)

        # Update README with final statistics
        print("\n📝 Updating README with extraction statistics...")
        links_count = links_summary.get('total_resources', 0) if links_summary else 0
        file_writer.update_readme_with_stats(course_data, links_count)

        # Clear progress file after successful completion
        if file_writer.progress_file.exists():
            file_writer.clear_progress()

        # Summary
        print("\n" + "=" * 60)
        print("Extraction Complete!")
        print("=" * 60)
        print(f"Course: {course_title}")
        print(f"Output: {output_path}")
        print(f"\nStatistics:")
        print(f"  Sections: {len(sections)}")
        print(f"  Total lectures: {total_lectures}")
        print(f"  Transcripts: {extraction_counts['transcripts']}")
        print(f"  Articles: {extraction_counts['articles']}")
        print(f"  Quizzes: {extraction_counts['quizzes']}")
        print(f"  Resources: {extraction_counts['resources']}")
        print(f"  Skipped: {extraction_counts['skipped']}")

        # Get file statistics
        stats = file_writer.get_statistics()
        print(f"\nFiles created:")
        print(f"  {output_path}/README.md")
        if stats['transcripts'] > 0:
            print(f"  {output_path}/transcripts/ ({stats['transcripts']} files)")
        if stats['articles'] > 0:
            print(f"  {output_path}/articles/ ({stats['articles']} files)")
        if stats['quizzes'] > 0:
            print(f"  {output_path}/quizzes/ ({stats['quizzes']} files)")
        if stats['resources'] > 0:
            print(f"  {output_path}/DOWNLOADED_RESOURCES.md")
            print(f"  {output_path}/resources/ ({stats['resources']} files)")

        # Show extractor statistics if any issues
        article_stats = article_extractor.get_statistics()
        quiz_stats = quiz_extractor.get_statistics()
        resource_stats = resource_extractor.get_statistics()

        # Show resource download statistics
        if config['download_resources'] and hasattr(resource_extractor, 'get_download_statistics'):
            download_stats = resource_extractor.get_download_statistics()
            if download_stats['downloaded'] > 0 or download_stats['failed_download'] > 0:
                print(f"\nResource Download Statistics:")
                if download_stats['downloaded'] > 0:
                    total_mb = download_stats['total_bytes'] / (1024 * 1024)
                    print(f"  ✓ {download_stats['downloaded']} files downloaded ({total_mb:.1f}MB)")
                if download_stats['skipped_size'] > 0:
                    print(f"  ⊘ {download_stats['skipped_size']} files skipped (exceeded size limit)")
                if download_stats['failed_download'] > 0:
                    print(f"  ✗ {download_stats['failed_download']} files failed to download")

        if article_stats['partial'] > 0 or article_stats['failed'] > 0:
            print(f"\nArticle Extraction Issues:")
            if article_stats['partial'] > 0:
                print(f"  ⚠️  {article_stats['partial']} articles saved as raw HTML (conversion failed)")
            if article_stats['failed'] > 0:
                print(f"  ✗ {article_stats['failed']} articles failed to extract")

        print("=" * 60)

        # Update API documentation if new endpoints were discovered
        if api_client.has_new_endpoints():
            print("\n📝 Updating API documentation with new endpoints...")
            api_client.update_api_documentation()
            print("  ✓ API.md updated")

        print("\n✓ Done!")

    except KeyboardInterrupt:
        _print_warning("\n\n⚠️  Extraction interrupted by user")
        sys.exit(1)
    except Exception as error:
        _print_error(f"\n❌ Unexpected error: {str(error)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
