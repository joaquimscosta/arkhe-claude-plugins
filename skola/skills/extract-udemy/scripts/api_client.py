#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Udemy API Client

Handles API requests to Udemy platform with hybrid approach:
1. Read documented endpoints from API.md
2. Fall back to discovery if endpoints not documented
3. Update API.md with new discoveries
"""

import json
import time
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, quote


class UdemyAPIClient:
    """
    Client for interacting with Udemy API.

    Implements hybrid approach:
    - Use documented endpoints from API.md
    - Discover new endpoints if needed
    - Update API.md with findings
    """

    def __init__(self, base_url, auth_headers, project_root):
        """
        Initialize API client.

        Args:
            base_url: Base URL for Udemy site (e.g., https://risesmart.udemy.com)
            auth_headers: Authentication headers from Authenticator
            project_root: Path to project root directory
        """
        self.base_url = base_url.rstrip('/')
        self.auth_headers = auth_headers
        self.project_root = Path(project_root)
        self.api_doc_file = self.project_root / 'API.md'

        # Track discovered endpoints
        self.discovered_endpoints = []
        self.documented_endpoints = {}

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # seconds between requests

        # Load documented endpoints
        self._read_api_documentation()

    def _read_api_documentation(self):
        """Read and parse API.md for documented endpoints."""
        if not self.api_doc_file.exists():
            return

        try:
            with open(self.api_doc_file, 'r') as f:
                content = f.read()

            # Parse documented endpoints
            # Look for patterns like:
            # GET https://SITE.udemy.com/api-2.0/courses/{course_id}/...

            # Course structure endpoint
            if 'cached-subscriber-curriculum-items' in content:
                self.documented_endpoints['course_structure'] = \
                    '/api-2.0/courses/{course_id}/cached-subscriber-curriculum-items'

            # Transcript endpoint
            if 'captions' in content or 'asset' in content:
                # Try to find the exact pattern
                caption_match = re.search(
                    r'/api-2\.0/asset[s]?/\{[^}]+\}/caption[s]?',
                    content
                )
                if caption_match:
                    self.documented_endpoints['transcript'] = caption_match.group(0)
                else:
                    # Default pattern
                    self.documented_endpoints['transcript'] = '/api-2.0/assets/{asset_id}/captions'

        except Exception as e:
            print(f"⚠️  Could not read API.md: {e}")

    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, endpoint, method='GET', data=None):
        """
        Make HTTP request to Udemy API.

        Args:
            endpoint: API endpoint path (will be joined with base_url)
            method: HTTP method (GET, POST, etc.)
            data: Request body data (for POST requests)

        Returns:
            dict: JSON response data or None if failed
        """
        self._rate_limit()

        url = urljoin(self.base_url, endpoint)

        try:
            # Prepare request
            headers = self.auth_headers.copy()

            req = Request(url, headers=headers, method=method)

            if data:
                req.data = json.dumps(data).encode('utf-8')

            # Make request
            with urlopen(req, timeout=30) as response:
                if response.status == 200:
                    content = response.read().decode('utf-8')
                    return json.loads(content)
                else:
                    print(f"⚠️  HTTP {response.status} for {endpoint}")
                    return None

        except HTTPError as e:
            print(f"⚠️  HTTP Error {e.code} for {endpoint}")
            if e.code == 401:
                print("    Authentication may be required or has expired")
            elif e.code == 404:
                print("    Endpoint not found - may need discovery")
            return None

        except URLError as e:
            print(f"⚠️  Network error for {endpoint}: {e.reason}")
            return None

        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON response from {endpoint}")
            return None

        except Exception as e:
            print(f"⚠️  Unexpected error for {endpoint}: {e}")
            return None

    def resolve_course_id(self, course_slug):
        """
        Resolve course slug to numeric course ID.

        Args:
            course_slug: Course identifier from URL (e.g., "java-multithreading-concurrency-performance-optimization")

        Returns:
            int: Numeric course ID, or None if not found
        """
        print(f"  Resolving course slug to ID...")

        # If it's already numeric, return as-is
        if str(course_slug).isdigit():
            return int(course_slug)

        # Fetch enrolled courses to find the ID
        page = 1
        while True:
            endpoint = f'/api-2.0/users/me/subscribed-courses/?page_size=100&page={page}'
            data = self._make_request(endpoint)

            if not data:
                return None

            results = data.get('results', [])
            if not results:
                break

            # Search for matching course by URL slug
            for course in results:
                url = course.get('url', '')
                published_title = course.get('published_title', '')

                # Check if URL or published_title matches the slug
                if course_slug in url or published_title == course_slug:
                    course_id = course.get('id')
                    if course_id:
                        print(f"  ✓ Resolved '{course_slug}' to ID: {course_id}")
                        return course_id

            # Check if there are more pages
            if not data.get('next'):
                break

            page += 1

        print(f"  ✗ Could not find course with slug: {course_slug}")
        return None

    def get_course_details(self, course_id):
        """
        Fetch detailed course information (metadata, description, instructor, etc.).

        Args:
            course_id: Numeric course ID

        Returns:
            dict: Course details or None if failed
        """
        print(f"  Fetching course details...")

        endpoint = (
            f'/api-2.0/courses/{course_id}/'
            f'?fields[course]=title,headline,description,instructional_level,'
            f'estimated_content_length,num_subscribers,rating,visible_instructors,'
            f'locale,created,published_time'
        )

        data = self._make_request(endpoint)

        if data:
            print(f"  ✓ Retrieved course details")
            return data
        else:
            print(f"  ⚠️  Could not fetch course details")
            return None

    def get_course_structure(self, course_slug):
        """
        Fetch course structure (sections and lectures) with pagination support.

        Args:
            course_slug: Course identifier from URL (can be numeric ID or slug)

        Returns:
            dict: Course data with sections and lectures, or None if failed
        """
        # Resolve slug to numeric ID
        course_id = self.resolve_course_id(course_slug)
        if not course_id:
            return None

        # Fetch course details first
        course_details = self.get_course_details(course_id)

        # Use the discovered endpoint pattern with pagination
        print(f"  Fetching course structure...")

        all_items = []
        page = 1

        while True:
            endpoint = (
                f'/api-2.0/courses/{course_id}/subscriber-curriculum-items/'
                f'?fields[asset]=results,title,external_url,time_estimation,download_urls,slide_urls,filename,asset_type,captions,media_license_token,course_is_drmed,media_sources,stream_urls,body'
                f'&fields[chapter]=object_index,title,sort_order'
                f'&fields[lecture]=id,title,object_index,asset,supplementary_assets,view_html'
                f'&page_size=200'
                f'&page={page}'
            )

            print(f"    Requesting page {page}...")
            data = self._make_request(endpoint)

            if not data:
                if page == 1:
                    # First page failed, try fallback
                    print("  Documented endpoint failed, attempting discovery...")
                    return self._discover_course_structure(course_id, course_slug)
                else:
                    # Subsequent page failed, might be end of pagination
                    break

            results = data.get('results', [])
            if not results:
                break

            all_items.extend(results)

            # Check if there are more pages
            if not data.get('next'):
                break

            page += 1

        if all_items:
            print(f"  ✓ Retrieved {len(all_items)} curriculum items across {page} page(s)")
            # Pass both slug (for display) and ID (for API calls)
            return self._parse_course_structure({'results': all_items}, course_slug, course_id, course_details)
        else:
            print("  ✗ No curriculum items found")
            return None

    def _parse_course_structure(self, data, course_slug, course_id=None, course_details=None):
        """
        Parse course structure from API response.

        Args:
            data: Raw API response
            course_slug: Course identifier

        Returns:
            dict: Normalized course structure
        """
        # Handle different response formats
        # Common Udemy API response structures:

        # Format 1: Direct results array
        if isinstance(data, dict) and 'results' in data:
            items = data['results']
        # Format 2: Direct array
        elif isinstance(data, list):
            items = data
        else:
            items = []

        # Parse sections and lectures
        sections = []
        current_section = None

        for item in items:
            item_type = item.get('_class', item.get('type', ''))

            if item_type == 'chapter':
                # This is a section/chapter
                if current_section:
                    sections.append(current_section)

                current_section = {
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'lectures': []
                }

            elif item_type == 'lecture':
                # This is a lecture
                if not current_section:
                    # Create default section if none exists
                    current_section = {
                        'id': 0,
                        'title': 'Main Content',
                        'lectures': []
                    }

                lecture = {
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'asset': item.get('asset', {}),
                    'supplementary_assets': item.get('supplementary_assets', [])
                }

                current_section['lectures'].append(lecture)

        # Add last section
        if current_section:
            sections.append(current_section)

        # Build base course data
        course_data = {
            'title': course_slug.replace('-', ' ').title(),
            'slug': course_slug,
            'id': course_id if course_id else course_slug,
            'sections': sections
        }

        # Merge in course details if available
        if course_details:
            course_data.update({
                'title': course_details.get('title', course_data['title']),
                'headline': course_details.get('headline', ''),
                'description': course_details.get('description', ''),
                'instructional_level': course_details.get('instructional_level', ''),
                'estimated_content_length': course_details.get('estimated_content_length', 0),
                'num_subscribers': course_details.get('num_subscribers', 0),
                'rating': course_details.get('rating', 0),
                'visible_instructors': course_details.get('visible_instructors', []),
                'locale': course_details.get('locale', {}),
                'created': course_details.get('created', ''),
                'published_time': course_details.get('published_time', '')
            })

        return course_data

    def _discover_course_structure(self, course_id, course_slug):
        """
        Attempt to discover course structure endpoint.

        Args:
            course_id: Numeric course ID
            course_slug: Course slug string

        Returns:
            dict: Course structure or None if discovery failed
        """
        # Common Udemy API endpoint patterns to try
        patterns = [
            f'/api-2.0/courses/{course_id}/cached-subscriber-curriculum-items',
            f'/api-2.0/courses/{course_id}/curriculum-items',
            f'/api-2.0/courses/{course_id}/public-curriculum-items',
            f'/api-2.0/courses/{course_id}/subscriber-curriculum-items',
        ]

        for pattern in patterns:
            print(f"  Trying: {pattern}")
            data = self._make_request(pattern)

            if data:
                # Success! Record this endpoint
                self.discovered_endpoints.append({
                    'type': 'course_structure',
                    'pattern': pattern,
                    'description': 'Course structure (sections and lectures)',
                    'example_response': self._truncate_json(data)
                })

                return self._parse_course_structure(data, course_slug)

        print("  ✗ Could not discover course structure endpoint")
        return None

    def get_lecture_transcript(self, course_id, lecture_id):
        """
        Fetch transcript for a lecture.

        Args:
            course_id: Course identifier
            lecture_id: Lecture identifier

        Returns:
            list: Transcript data with timestamps, or None if not available
        """
        if not lecture_id:
            return None

        # Use the discovered endpoint to get lecture details with captions
        endpoint = f'/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}/?fields[asset]=captions&fields[lecture]=asset'

        print(f"    Fetching transcript for lecture {lecture_id}...")
        data = self._make_request(endpoint)

        if not data:
            print(f"      ✗ Could not fetch lecture details")
            return None

        # Extract captions from response
        asset = data.get('asset', {})
        captions = asset.get('captions', [])

        if not captions:
            print(f"      ⚠️  No captions available for this lecture")
            return None

        # Find English captions
        for caption in captions:
            locale_id = caption.get('locale_id', '')
            if locale_id.startswith('en'):
                vtt_url = caption.get('url')
                if vtt_url:
                    print(f"      ✓ Found English transcript")
                    return self._download_and_parse_vtt(vtt_url)

        print(f"      ⚠️  No English captions found")
        return None

    def _download_and_parse_vtt(self, vtt_url):
        """
        Download and parse VTT transcript file.

        Args:
            vtt_url: URL to VTT file (may include secure token)

        Returns:
            list: Parsed transcript with timestamps [{'time': '00:05', 'text': '...'}, ...]
        """
        try:
            # VTT URLs from Udemy include secure tokens and expire after ~4.5 hours
            req = Request(vtt_url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')

            # Parse VTT format
            # Example VTT:
            # WEBVTT
            #
            # 1
            # 00:00:00.000 --> 00:00:05.000
            # Welcome to the course

            cues = []
            lines = content.split('\n')

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Look for timestamp lines (supports both HH:MM:SS.mmm and MM:SS.mmm formats)
                # Udemy uses MM:SS.mmm for lectures under 1 hour: 00:00.120 --> 00:02.840
                # Longer lectures use HH:MM:SS.mmm format: 01:23:45.678 --> 01:23:50.000
                if '-->' in line:
                    # Try MM:SS.mmm format first (most common for Udemy)
                    match = re.match(r'(\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}\.\d{3})', line)
                    if not match:
                        # Try HH:MM:SS.mmm format for longer videos
                        match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', line)

                    if match:
                        start_time = match.group(1)

                        # Get text from next line(s) until blank line or next timestamp
                        i += 1
                        text_parts = []
                        while i < len(lines):
                            text_line = lines[i].strip()
                            if not text_line or '-->' in text_line or text_line.isdigit():
                                break
                            text_parts.append(text_line)
                            i += 1

                        if text_parts:
                            cues.append({
                                'time': self._parse_vtt_time(start_time),
                                'text': ' '.join(text_parts)
                            })
                        continue

                i += 1

            if cues:
                print(f"        ✓ Parsed {len(cues)} transcript segments")
                return cues
            else:
                print(f"        ⚠️  No transcript content found in VTT file")
                return None

        except HTTPError as e:
            print(f"        ⚠️  HTTP Error {e.code} downloading VTT")
            if e.code == 403:
                print(f"        Secure token may have expired")
            return None
        except Exception as e:
            print(f"        ⚠️  Could not download/parse VTT: {e}")
            return None


    def _parse_vtt_time(self, time_str):
        """
        Convert VTT timestamp to simple format.

        Handles both formats:
        - MM:SS.mmm (00:05.000) -> 00:05
        - HH:MM:SS.mmm (01:00:05.000) -> 60:05
        """
        parts = time_str.split(':')

        if len(parts) == 2:
            # MM:SS.mmm format
            minutes = int(parts[0])
            seconds = int(float(parts[1]))
            return f"{minutes:02d}:{seconds:02d}"
        elif len(parts) == 3:
            # HH:MM:SS.mmm format - convert to total minutes
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(float(parts[2]))
            total_minutes = hours * 60 + minutes
            return f"{total_minutes:02d}:{seconds:02d}"

        return "00:00"

    def _truncate_json(self, data, max_length=500):
        """Truncate JSON for documentation purposes."""
        json_str = json.dumps(data, indent=2)
        if len(json_str) > max_length:
            return json_str[:max_length] + '\n  ...\n}'
        return json_str

    def has_new_endpoints(self):
        """Check if new endpoints were discovered."""
        return len(self.discovered_endpoints) > 0

    def update_api_documentation(self):
        """Update API.md with newly discovered endpoints."""
        if not self.discovered_endpoints:
            return

        try:
            # Read existing content
            if self.api_doc_file.exists():
                with open(self.api_doc_file, 'r') as f:
                    existing_content = f.read()
            else:
                existing_content = "# Udemy API Documentation\n\n"

            # Prepare new content
            new_section = "\n\n---\n\n## Discovered Endpoints\n\n"
            new_section += f"**Discovery Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            for endpoint in self.discovered_endpoints:
                new_section += f"### {endpoint['type']}\n\n"
                new_section += f"**Description**: {endpoint['description']}\n\n"
                new_section += f"**Endpoint Pattern**:\n```\n{endpoint['pattern']}\n```\n\n"
                new_section += f"**Example Response**:\n```json\n{endpoint['example_response']}\n```\n\n"

            # Append to file
            with open(self.api_doc_file, 'a') as f:
                f.write(new_section)

            print(f"  ✓ Updated {self.api_doc_file}")

        except Exception as e:
            print(f"  ⚠️  Could not update API.md: {e}")

    def detect_content_type(self, lecture_data):
        """
        Detect the type of content in a lecture.

        Args:
            lecture_data: Lecture information dict from API

        Returns:
            str: Content type ('video', 'article', 'coding_solution',
                 'technical_resource', 'quiz', 'promotional', 'unknown')
        """
        # Get asset information
        asset = lecture_data.get('asset', {})
        asset_type = asset.get('asset_type', '').lower()
        title = lecture_data.get('title', '').lower()

        # Video content
        if asset_type == 'video' or asset.get('media_sources'):
            return 'video'

        # Article content - further classify
        if asset_type == 'article' or asset.get('body') or asset.get('view_html'):
            # Check title for specific patterns
            if 'solution' in title:
                return 'coding_solution'
            elif any(word in title for word in ['quiz', 'exercise', 'practice']):
                # Could be inline quiz or coding exercise
                if 'quiz' in title:
                    return 'quiz'
                else:
                    return 'coding_exercise'
            elif any(word in title for word in ['bonus', 'keep learning', 'certificate', 'congratulations']):
                return 'promotional'
            elif any(word in title for word in ['additional resource', 'tips', 'guide', 'reference']):
                return 'technical_resource'
            else:
                return 'article'

        # E-book or document
        if asset_type == 'e-book' or asset_type == 'file':
            return 'ebook'

        # Unknown type
        return 'unknown'


# Example usage
if __name__ == '__main__':
    from auth import Authenticator

    # Use current working directory as base (works for both local and Git-installed plugins)
    project_root = Path.cwd() / 'skola-research' / 'udemy'

    try:
        # Initialize auth
        auth = Authenticator(project_root)
        headers = auth.get_auth_headers()

        # Initialize client
        client = UdemyAPIClient(
            base_url='https://risesmart.udemy.com',
            auth_headers=headers,
            project_root=project_root
        )

        print("✓ API Client initialized successfully!")

    except Exception as e:
        print(f"✗ Error: {e}")
