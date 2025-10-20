#!/usr/bin/env python3
"""
Content Extractors

Specialized extractors for different Udemy content types:
- Articles (HTML content)
- Quizzes (questions and answers)
- Resources (supplementary files)

Each extractor handles conversion, formatting, and error handling
for its specific content type.
"""

import re
import html
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    Base class for content extractors.

    Provides common functionality for extracting and processing
    different types of Udemy course content.
    """

    def __init__(self, api_client, config=None):
        """
        Initialize content extractor.

        Args:
            api_client: UdemyAPIClient instance for API requests
            config: Optional configuration dict with extraction settings
        """
        self.api_client = api_client
        self.config = config or {}

        # Extraction statistics
        self.stats = {
            'success': 0,
            'partial': 0,
            'failed': 0,
            'skipped': 0
        }

    def extract(self, lecture_data):
        """
        Extract content from lecture data.

        Must be implemented by subclasses.

        Args:
            lecture_data: Lecture information from API

        Returns:
            dict: Extracted content with metadata, or None if failed
        """
        raise NotImplementedError("Subclasses must implement extract()")

    def get_statistics(self):
        """Get extraction statistics."""
        return self.stats.copy()

    def _clean_html_text(self, text):
        """
        Clean HTML text by removing tags and decoding entities.

        Args:
            text: Raw HTML text

        Returns:
            str: Cleaned plain text
        """
        if not text:
            return ""

        # Decode HTML entities
        text = html.unescape(text)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Clean up whitespace
        text = ' '.join(text.split())

        return text.strip()


class ArticleExtractor(ContentExtractor):
    """
    Extractor for article-based lectures.

    Converts HTML article content to clean markdown format,
    preserving code blocks, formatting, and structure.
    """

    def extract(self, lecture_data):
        """
        Extract article content from lecture.

        Args:
            lecture_data: Lecture information dict

        Returns:
            dict: Article data with markdown content and metadata
        """
        lecture_id = lecture_data.get('id')
        title = lecture_data.get('title', 'Untitled')

        try:
            # Get article HTML from asset
            asset = lecture_data.get('asset', {})

            # Try different fields where article content might be
            html_content = (
                asset.get('body') or
                asset.get('view_html') or
                lecture_data.get('view_html') or
                lecture_data.get('description', '')
            )

            if not html_content:
                logger.warning(f"Lecture {lecture_id} ({title}): No article content found")
                self.stats['skipped'] += 1
                return None

            # Convert HTML to markdown
            markdown_content = self._html_to_markdown(html_content)

            if not markdown_content:
                logger.warning(f"Lecture {lecture_id} ({title}): Markdown conversion produced empty content")
                # Fallback: return raw HTML
                markdown_content = f"```html\n{html_content}\n```"
                self.stats['partial'] += 1
            else:
                self.stats['success'] += 1

            # Detect article type
            article_type = self._detect_article_type(title, markdown_content)

            return {
                'type': 'article',
                'article_type': article_type,
                'lecture_id': lecture_id,
                'title': title,
                'content': markdown_content,
                'metadata': {
                    'asset_type': asset.get('asset_type'),
                    'time_estimation': asset.get('time_estimation', 0)
                }
            }

        except Exception as e:
            logger.error(f"Lecture {lecture_id} ({title}): Article extraction failed - {e}")
            self.stats['failed'] += 1
            return None

    def _detect_article_type(self, title, content):
        """
        Detect the type of article based on title and content.

        Args:
            title: Article title
            content: Article content

        Returns:
            str: Article type (coding_solution, technical_resource, promotional, general)
        """
        title_lower = title.lower()
        content_lower = content.lower()

        # Check for solution articles
        if 'solution' in title_lower:
            return 'coding_solution'

        # Check for promotional content
        if any(word in title_lower for word in ['bonus', 'keep learning', 'certificate']):
            return 'promotional'

        # Check for technical resources
        if any(word in title_lower for word in ['additional resource', 'tips', 'guide', 'reference']):
            return 'technical_resource'

        # Check content for code
        if '```' in content or 'public class' in content or 'def ' in content:
            return 'coding_solution'

        return 'general'

    def _html_to_markdown(self, html_content):
        """
        Convert HTML to markdown format.

        Uses simple regex-based conversion. For production,
        consider using html2text or markdownify libraries.

        Args:
            html_content: Raw HTML string

        Returns:
            str: Markdown formatted content
        """
        if not html_content:
            return ""

        # Start with the HTML content
        md = html_content

        # Convert headings
        md = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', md, flags=re.DOTALL)
        md = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', md, flags=re.DOTALL)
        md = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', md, flags=re.DOTALL)
        md = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', md, flags=re.DOTALL)

        # Convert bold and italic
        md = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', md, flags=re.DOTALL)
        md = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', md, flags=re.DOTALL)
        md = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', md, flags=re.DOTALL)
        md = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', md, flags=re.DOTALL)

        # Convert code blocks
        md = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'```\n\1\n```', md, flags=re.DOTALL)
        md = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```', md, flags=re.DOTALL)

        # Convert inline code
        md = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', md, flags=re.DOTALL)

        # Convert links - keep original URLs
        md = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', md, flags=re.DOTALL)

        # Convert images - keep remote URLs
        md = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>', r'![\2](\1)', md, flags=re.DOTALL)
        md = re.sub(r'<img[^>]*src="([^"]*)"[^>]*/?>',  r'![Image](\1)', md, flags=re.DOTALL)

        # Convert lists
        md = re.sub(r'<ul[^>]*>(.*?)</ul>', lambda m: self._convert_list(m.group(1), ordered=False), md, flags=re.DOTALL)
        md = re.sub(r'<ol[^>]*>(.*?)</ol>', lambda m: self._convert_list(m.group(1), ordered=True), md, flags=re.DOTALL)

        # Convert paragraphs to double newlines
        md = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', md, flags=re.DOTALL)

        # Convert line breaks
        md = re.sub(r'<br\s*/?>', '\n', md)

        # Remove remaining HTML tags
        md = re.sub(r'<[^>]+>', '', md)

        # Decode HTML entities
        md = html.unescape(md)

        # Clean up excessive newlines (more than 2 consecutive)
        md = re.sub(r'\n{3,}', '\n\n', md)

        # Remove leading/trailing whitespace from lines
        md = '\n'.join(line.rstrip() for line in md.split('\n'))

        return md.strip()

    def _convert_list(self, list_content, ordered=False):
        """
        Convert HTML list items to markdown.

        Args:
            list_content: Inner HTML of ul/ol tag
            ordered: Whether this is an ordered list

        Returns:
            str: Markdown list
        """
        items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, flags=re.DOTALL)

        result = []
        for i, item in enumerate(items, 1):
            # Clean the item text
            item_text = re.sub(r'<[^>]+>', '', item).strip()

            if ordered:
                result.append(f"{i}. {item_text}")
            else:
                result.append(f"- {item_text}")

        return '\n' + '\n'.join(result) + '\n'


class QuizExtractor(ContentExtractor):
    """
    Extractor for quiz and coding exercise content.

    Extracts questions, options, and answers in structured format.
    """

    def extract(self, lecture_data):
        """
        Extract quiz data from lecture.

        Args:
            lecture_data: Lecture information dict

        Returns:
            dict: Quiz data with questions and metadata
        """
        lecture_id = lecture_data.get('id')
        title = lecture_data.get('title', 'Untitled')

        try:
            # Check if this is a quiz
            asset = lecture_data.get('asset', {})
            quiz_data = lecture_data.get('quiz', asset.get('quiz'))

            if not quiz_data:
                logger.debug(f"Lecture {lecture_id} ({title}): No quiz data found")
                self.stats['skipped'] += 1
                return None

            # Extract quiz information
            questions = self._parse_quiz_questions(quiz_data)

            if not questions:
                logger.warning(f"Lecture {lecture_id} ({title}): Quiz has no parseable questions")
                self.stats['partial'] += 1
                return None

            self.stats['success'] += 1

            return {
                'type': 'quiz',
                'lecture_id': lecture_id,
                'title': title,
                'questions': questions,
                'metadata': {
                    'question_count': len(questions),
                    'quiz_type': quiz_data.get('type', 'unknown')
                }
            }

        except Exception as e:
            logger.error(f"Lecture {lecture_id} ({title}): Quiz extraction failed - {e}")
            self.stats['failed'] += 1
            return None

    def _parse_quiz_questions(self, quiz_data):
        """
        Parse quiz questions from quiz data.

        Args:
            quiz_data: Quiz information from API

        Returns:
            list: List of question dicts
        """
        questions = []

        # Quiz data structure varies, attempt to parse
        question_list = quiz_data.get('questions', [])

        for idx, q in enumerate(question_list, 1):
            question_dict = {
                'id': idx,
                'text': q.get('question', q.get('prompt', '')),
                'type': q.get('type', 'multiple_choice'),
                'options': q.get('options', q.get('answers', [])),
                'correct_answer': q.get('correct_answer', q.get('correct_response'))
            }

            questions.append(question_dict)

        return questions


class ResourceExtractor(ContentExtractor):
    """
    Extractor for supplementary resources and downloadable files.

    Downloads supplementary files (PDFs, code files, etc.) if enabled in config.
    """

    def __init__(self, api_client, config=None):
        """Initialize resource extractor with download capability."""
        super().__init__(api_client, config)
        self.download_enabled = self.config.get('download_resources', True)
        self.max_file_size_mb = self.config.get('max_resource_size_mb', 100)

        # Track download statistics
        self.download_stats = {
            'downloaded': 0,
            'skipped_size': 0,
            'failed_download': 0,
            'total_bytes': 0
        }

    def extract(self, lecture_data):
        """
        Extract and optionally download resources from lecture.

        Args:
            lecture_data: Lecture information dict

        Returns:
            dict: Resource data with download info
        """
        lecture_id = lecture_data.get('id')
        title = lecture_data.get('title', 'Untitled')

        try:
            # Extract supplementary assets
            supp_assets = lecture_data.get('supplementary_assets', [])

            if not supp_assets:
                self.stats['skipped'] += 1
                return None

            resources = []

            for asset in supp_assets:
                resource = {
                    'filename': asset.get('filename', 'Unknown'),
                    'file_type': asset.get('asset_type', 'Unknown'),
                    'url': asset.get('download_urls', {}).get('File', [{}])[0].get('file', ''),
                    'size': asset.get('size_in_bytes', 0),
                    'asset_id': asset.get('id'),
                    'downloaded': False,
                    'download_path': None
                }

                # Download file if enabled
                if self.download_enabled and resource['url']:
                    download_result = self._download_resource(resource)
                    if download_result:
                        resource['downloaded'] = True
                        resource['download_path'] = download_result
                        resource['local_filename'] = download_result
                        self.download_stats['downloaded'] += 1
                        self.download_stats['total_bytes'] += resource['size']
                    else:
                        self.download_stats['failed_download'] += 1

                resources.append(resource)

            self.stats['success'] += 1

            return {
                'type': 'resources',
                'lecture_id': lecture_id,
                'title': title,
                'resources': resources,
                'metadata': {
                    'resource_count': len(resources),
                    'download_enabled': self.download_enabled,
                    'downloaded_count': sum(1 for r in resources if r.get('downloaded'))
                }
            }

        except Exception as e:
            logger.error(f"Lecture {lecture_id} ({title}): Resource extraction failed - {e}")
            self.stats['failed'] += 1
            return None

    def _download_resource(self, resource):
        """
        Download a resource file.

        Args:
            resource: Resource dict with url, filename, size

        Returns:
            str: Filename if successful, None otherwise
        """
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError, URLError
        import os

        url = resource.get('url')
        filename = resource.get('filename', 'unknown')
        size_bytes = resource.get('size', 0)
        size_mb = size_bytes / (1024 * 1024)

        if not url:
            logger.debug(f"No download URL for {filename}")
            return None

        # Check file size limit
        if size_mb > self.max_file_size_mb:
            logger.warning(f"Skipping {filename} - size {size_mb:.1f}MB exceeds limit of {self.max_file_size_mb}MB")
            self.download_stats['skipped_size'] += 1
            return None

        try:
            # Prepare request with auth headers
            headers = self.api_client.auth_headers.copy()
            req = Request(url, headers=headers)

            # Download file
            logger.info(f"Downloading {filename} ({size_mb:.1f}MB)...")

            with urlopen(req, timeout=60) as response:
                if response.status == 200:
                    content = response.read()

                    # Return filename and content for file_writer to save
                    # We don't save here because file_writer manages paths
                    return {
                        'filename': filename,
                        'content': content,
                        'size': len(content)
                    }
                else:
                    logger.warning(f"HTTP {response.status} when downloading {filename}")
                    return None

        except HTTPError as e:
            logger.error(f"HTTP Error {e.code} downloading {filename}")
            return None
        except URLError as e:
            logger.error(f"Network error downloading {filename}: {e.reason}")
            return None
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            return None

    def get_download_statistics(self):
        """Get download statistics."""
        return self.download_stats.copy()


class ExternalResourceLinker(ContentExtractor):
    """
    Extractor for external resources mentioned in transcripts and articles.

    Scans content for URLs and categorizes them (GitHub, docs, StackOverflow, etc.).
    """

    def __init__(self, api_client, config=None):
        """Initialize external resource linker."""
        super().__init__(api_client, config)

        # URL pattern categories
        self.url_patterns = {
            'github': r'github\.com/[\w-]+/[\w-]+',
            'stackoverflow': r'stackoverflow\.com/questions/\d+',
            'documentation': r'(?:docs?\.|documentation)',
            'youtube': r'(?:youtube\.com|youtu\.be)',
            'medium': r'medium\.com',
            'dev_to': r'dev\.to'
        }

        # Track found resources
        self.found_resources = {
            'github': [],
            'stackoverflow': [],
            'documentation': [],
            'youtube': [],
            'medium': [],
            'dev_to': [],
            'other': []
        }

    def scan_content(self, content, content_type, lecture_number, lecture_title):
        """
        Scan content for external URLs.

        Args:
            content: Text content to scan
            content_type: Type of content ('transcript' or 'article')
            lecture_number: Lecture sequence number
            lecture_title: Lecture title

        Returns:
            list: Found URLs with metadata
        """
        if not content:
            return []

        import re
        from urllib.parse import urlparse

        # Find all URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        found_urls = re.findall(url_pattern, content, re.IGNORECASE)

        resources = []
        for url in found_urls:
            # Clean URL
            url = url.rstrip('.,;:)')

            # Categorize URL
            category = 'other'
            for cat, pattern in self.url_patterns.items():
                if re.search(pattern, url, re.IGNORECASE):
                    category = cat
                    break

            # Extract domain
            try:
                parsed = urlparse(url)
                domain = parsed.netloc
            except:
                domain = 'unknown'

            resource = {
                'url': url,
                'category': category,
                'domain': domain,
                'mentioned_in': {
                    'lecture_number': lecture_number,
                    'lecture_title': lecture_title,
                    'content_type': content_type
                }
            }

            resources.append(resource)
            self.found_resources[category].append(resource)

        return resources

    def generate_summary(self):
        """
        Generate summary of all found external resources.

        Returns:
            dict: Categorized resources
        """
        summary = {
            'total_resources': sum(len(resources) for resources in self.found_resources.values()),
            'by_category': {}
        }

        for category, resources in self.found_resources.items():
            if resources:
                # Deduplicate by URL
                unique_resources = {}
                for resource in resources:
                    url = resource['url']
                    if url not in unique_resources:
                        unique_resources[url] = {
                            'url': url,
                            'domain': resource['domain'],
                            'category': category,
                            'mentioned_in': [resource['mentioned_in']]
                        }
                    else:
                        unique_resources[url]['mentioned_in'].append(resource['mentioned_in'])

                summary['by_category'][category] = list(unique_resources.values())

        return summary


# Example usage
if __name__ == '__main__':
    # Test HTML to markdown conversion
    test_html = """
    <h2>Example Article</h2>
    <p>This is a <strong>test</strong> paragraph with <code>inline code</code>.</p>
    <pre><code>public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}</code></pre>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    """

    extractor = ArticleExtractor(api_client=None)
    markdown = extractor._html_to_markdown(test_html)
    print("Converted Markdown:")
    print(markdown)
