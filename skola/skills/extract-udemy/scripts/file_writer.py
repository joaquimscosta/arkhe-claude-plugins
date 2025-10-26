#!/usr/bin/env python3
"""
Course File Writer

Handles file organization and writing for extracted course content.
Creates directory structure and saves transcripts in organized format.
"""

import os
import re
from pathlib import Path
from datetime import datetime


class CourseFileWriter:
    """
    Manages file operations for course extraction.

    Creates directory structure and saves course content
    (transcripts, README, resources) in organized format.
    """

    def __init__(self, output_path, course_name, course_url, project_root):
        """
        Initialize file writer.

        Args:
            output_path: Path where course content will be saved
            course_name: Course identifier/slug
            course_url: Original course URL
            project_root: Path to project root (for accessing templates)
        """
        self.output_path = Path(output_path)
        self.course_name = course_name
        self.course_url = course_url
        self.project_root = Path(project_root)

        # Directory structure
        self.transcripts_dir = self.output_path / 'transcripts'
        self.articles_dir = self.output_path / 'articles'
        self.quizzes_dir = self.output_path / 'quizzes'
        self.slides_dir = self.output_path / 'slides'
        self.resources_dir = self.output_path / 'resources'

        # Template file - look in skill's templates directory first, fallback to project root
        skill_template = Path(__file__).parent.parent / 'templates' / 'course-readme-template.md'
        project_template = self.project_root / 'templates' / 'course-readme-template.md'

        if skill_template.exists():
            self.template_file = skill_template
        elif project_template.exists():
            self.template_file = project_template
        else:
            # Use skill path as default (will use fallback template if not found)
            self.template_file = skill_template

        # Track created files
        self.created_files = []

        # Track extraction statistics by type
        self.extraction_stats = {
            'transcripts': 0,
            'articles': 0,
            'quizzes': 0,
            'resources': 0
        }

    def create_directory_structure(self):
        """
        Create the course directory structure.

        Creates:
        - Main course directory
        - transcripts/ subdirectory
        - slides/ subdirectory
        - resources/ subdirectory
        - resources/git-repo.md placeholder
        """
        try:
            # Create main directory
            self.output_path.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            self.transcripts_dir.mkdir(exist_ok=True)
            self.articles_dir.mkdir(exist_ok=True)
            self.quizzes_dir.mkdir(exist_ok=True)
            self.slides_dir.mkdir(exist_ok=True)
            self.resources_dir.mkdir(exist_ok=True)

            # Create placeholder files
            git_repo_file = self.resources_dir / 'git-repo.md'
            if not git_repo_file.exists():
                with open(git_repo_file, 'w') as f:
                    f.write("# Git Repositories\n\n")
                    f.write("Links to course code repositories and samples:\n\n")
                    f.write("- TODO: Add repository links\n")

            return True

        except Exception as e:
            print(f"✗ Error creating directory structure: {e}")
            return False

    def save_course_readme(self, course_data):
        """
        Generate and save course README from template.

        Args:
            course_data: Course information dict with title, sections, etc.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read template
            template_content = self._read_template()

            # Replace placeholders
            readme_content = template_content

            # Course name
            course_title = course_data.get('title', self.course_name)
            readme_content = readme_content.replace('{COURSE_NAME}', course_title)

            # Course URL
            readme_content = readme_content.replace('{COURSE_URL}', self.course_url)

            # Date
            today = datetime.now().strftime('%Y-%m-%d')
            readme_content = readme_content.replace('{DATE}', today)

            # Extract instructor name
            instructors = course_data.get('visible_instructors', [])
            instructor_name = 'TODO: Add instructor name'
            if instructors:
                # Get first instructor's display name
                instructor_name = instructors[0].get('display_name', instructors[0].get('title', instructor_name))

            # Populate course metadata from API
            replacements = {
                '{INSTRUCTOR_NAME}': instructor_name,
                '{COURSE_LEVEL}': course_data.get('instructional_level', 'TODO: Beginner / Intermediate / Advanced').title(),
                '{COURSE_DESCRIPTION}': course_data.get('headline', 'TODO: Add a brief description of what this course covers.'),
                '{COURSE_DURATION}': self._format_duration(course_data.get('estimated_content_length', 0)),
                '{NUM_SUBSCRIBERS}': f"{course_data.get('num_subscribers', 0):,}",
                '{COURSE_RATING}': f"{course_data.get('rating', 0):.1f}",
            }

            for placeholder, value in replacements.items():
                readme_content = readme_content.replace(placeholder, value)

            # Add course structure info
            sections = course_data.get('sections', [])
            if sections:
                structure_section = self._generate_structure_section(sections)
                # Insert after the Structure section
                readme_content = readme_content.replace(
                    '## Key Takeaways',
                    f'{structure_section}\n\n## Key Takeaways'
                )

            # Save README
            readme_file = self.output_path / 'README.md'
            with open(readme_file, 'w') as f:
                f.write(readme_content)

            self.created_files.append(str(readme_file))
            return True

        except Exception as e:
            print(f"⚠️  Error creating README: {e}")
            return False

    def _format_duration(self, seconds):
        """
        Format duration in seconds to human-readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            str: Formatted duration (e.g., "5h 30m")
        """
        if not seconds or seconds == 0:
            return "TODO: Add course duration"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)

        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{seconds}s"

    def _read_template(self):
        """Read README template file."""
        if self.template_file.exists():
            with open(self.template_file, 'r') as f:
                return f.read()
        else:
            # Return minimal template if file doesn't exist
            return """# {COURSE_NAME}

## Course Information

- **Course Name**: {COURSE_NAME}
- **Platform**: Udemy
- **URL**: {COURSE_URL}
- **Date Added**: {DATE}

## Description

TODO: Add course description

## Structure

This directory contains:

- `transcripts/` - Video transcripts organized by lecture
- `slides/` - Course slides and presentations
- `resources/` - Additional materials and references

## Progress Tracker

- [ ] Course started
- [ ] Transcripts extracted
- [ ] Course completed
"""

    def _generate_structure_section(self, sections):
        """Generate course structure section for README."""
        structure = "\n## Course Structure\n\n"

        total_lectures = sum(len(s.get('lectures', [])) for s in sections)
        structure += f"**Total Sections**: {len(sections)}\n"
        structure += f"**Total Lectures**: {total_lectures}\n\n"

        structure += "### Sections\n\n"

        for idx, section in enumerate(sections, 1):
            section_title = section.get('title', f'Section {idx}')
            lecture_count = len(section.get('lectures', []))
            structure += f"{idx}. **{section_title}** ({lecture_count} lectures)\n"

        return structure

    def save_transcript(self, lecture_number, lecture_title, transcript_data):
        """
        Save lecture transcript to file.

        Args:
            lecture_number: Lecture sequence number (for filename)
            lecture_title: Lecture title
            transcript_data: List of transcript cues with timestamps and text

        Returns:
            str: Filename of saved transcript, or None if failed
        """
        if not transcript_data:
            return None

        try:
            # Generate filename
            filename = self._generate_transcript_filename(lecture_number, lecture_title)
            filepath = self.transcripts_dir / filename

            # Format transcript content
            content = self._format_transcript(transcript_data, lecture_title)

            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            self.created_files.append(str(filepath))
            self.extraction_stats['transcripts'] += 1
            return filename

        except Exception as e:
            print(f"⚠️  Error saving transcript: {e}")
            return None

    def _generate_transcript_filename(self, lecture_number, lecture_title):
        """
        Generate sanitized filename for transcript.

        Args:
            lecture_number: Lecture number (1-indexed)
            lecture_title: Raw lecture title

        Returns:
            str: Sanitized filename (e.g., "001-introduction-to-react.txt")
        """
        # Sanitize title
        sanitized = self._sanitize_filename(lecture_title)

        # Add lecture number prefix
        filename = f"{lecture_number:03d}-{sanitized}.txt"

        return filename

    def _sanitize_filename(self, title):
        """
        Sanitize string for use in filename.

        Args:
            title: Raw title string

        Returns:
            str: Sanitized filename-safe string
        """
        # Convert to lowercase
        sanitized = title.lower()

        # Replace spaces and special chars with hyphens
        sanitized = re.sub(r'[^\w\s-]', '', sanitized)
        sanitized = re.sub(r'[-\s]+', '-', sanitized)

        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')

        # Limit length
        max_length = 100
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip('-')

        # Ensure not empty
        if not sanitized:
            sanitized = 'lecture'

        return sanitized

    def _format_transcript(self, transcript_data, lecture_title):
        """
        Format transcript data as plain text with timestamps.

        Args:
            transcript_data: List of transcript cues
            lecture_title: Title of the lecture

        Returns:
            str: Formatted transcript text
        """
        lines = []

        # Add header
        lines.append(f"# {lecture_title}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Process transcript data
        for cue in transcript_data:
            # Handle different data formats
            if isinstance(cue, dict):
                # Format 1: {time: "00:00", text: "..."}
                timestamp = cue.get('time', cue.get('start', '00:00'))
                text = cue.get('text', '')

                # Format 2: {startTime: 123, text: "..."}
                if not timestamp or timestamp == '00:00':
                    start_time = cue.get('startTime', cue.get('start_time', 0))
                    if isinstance(start_time, (int, float)):
                        timestamp = self._seconds_to_timestamp(start_time)

            elif isinstance(cue, str):
                # Plain text without timestamps
                timestamp = None
                text = cue
            else:
                continue

            # Clean text
            text = self._clean_transcript_text(text)

            if text:
                if timestamp:
                    lines.append(f"[{timestamp}] {text}")
                else:
                    lines.append(text)

        return '\n'.join(lines)

    def _seconds_to_timestamp(self, seconds):
        """
        Convert seconds to MM:SS timestamp format.

        Args:
            seconds: Time in seconds (int or float)

        Returns:
            str: Timestamp in MM:SS format
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def _clean_transcript_text(self, text):
        """
        Clean transcript text (remove extra whitespace, etc.).

        Args:
            text: Raw transcript text

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove common VTT artifacts
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'&nbsp;', ' ', text)  # Replace nbsp
        text = re.sub(r'&amp;', '&', text)   # Replace HTML entities

        return text.strip()

    def get_created_files(self):
        """
        Get list of all files created during extraction.

        Returns:
            list: Paths of created files
        """
        return self.created_files

    def get_statistics(self):
        """
        Get statistics about created files.

        Returns:
            dict: Statistics including file counts and sizes
        """
        stats = {
            'total_files': len(self.created_files),
            'transcripts': self.extraction_stats['transcripts'],
            'articles': self.extraction_stats['articles'],
            'quizzes': self.extraction_stats['quizzes'],
            'resources': self.extraction_stats['resources'],
            'total_size_bytes': sum(
                os.path.getsize(f) for f in self.created_files if os.path.exists(f)
            )
        }

        return stats

    def save_article(self, lecture_number, lecture_title, article_data):
        """
        Save article content to markdown file.

        Args:
            lecture_number: Lecture sequence number
            lecture_title: Lecture title
            article_data: Dict with 'content', 'metadata', 'article_type'

        Returns:
            str: Filename of saved article, or None if failed
        """
        if not article_data or not article_data.get('content'):
            return None

        try:
            # Generate filename
            filename = self._generate_article_filename(lecture_number, lecture_title)
            filepath = self.articles_dir / filename

            # Format article with frontmatter
            content = self._format_article(
                lecture_title,
                article_data.get('content', ''),
                article_data.get('metadata', {}),
                article_data.get('article_type', 'general'),
                lecture_number,
                article_data.get('lecture_id')
            )

            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            self.created_files.append(str(filepath))
            self.extraction_stats['articles'] += 1
            return filename

        except Exception as e:
            print(f"⚠️  Error saving article: {e}")
            return None

    def _generate_article_filename(self, lecture_number, lecture_title):
        """
        Generate sanitized filename for article.

        Args:
            lecture_number: Lecture number (1-indexed)
            lecture_title: Raw lecture title

        Returns:
            str: Sanitized filename (e.g., "006-multiexecutor-solution.md")
        """
        sanitized = self._sanitize_filename(lecture_title)
        filename = f"{lecture_number:03d}-{sanitized}.md"
        return filename

    def _format_article(self, title, content, metadata, article_type, lecture_number, lecture_id):
        """
        Format article with YAML frontmatter and markdown content.

        Args:
            title: Article title
            content: Markdown content
            metadata: Additional metadata dict
            article_type: Type of article (coding_solution, technical_resource, etc.)
            lecture_number: Lecture sequence number
            lecture_id: Lecture ID from API

        Returns:
            str: Formatted article content with frontmatter
        """
        lines = []

        # Add frontmatter
        lines.append("---")
        lines.append(f"lecture_number: {lecture_number}")
        lines.append(f"title: \"{title}\"")
        lines.append(f"type: {article_type}")
        if lecture_id:
            lines.append(f"lecture_id: {lecture_id}")
        if metadata.get('asset_type'):
            lines.append(f"asset_type: {metadata['asset_type']}")
        if metadata.get('time_estimation'):
            lines.append(f"estimated_time_minutes: {metadata['time_estimation'] // 60}")
        lines.append("---")
        lines.append("")

        # Add title as h1
        lines.append(f"# {title}")
        lines.append("")

        # Add content
        lines.append(content)

        return '\n'.join(lines)

    def save_quiz(self, lecture_number, lecture_title, quiz_data, output_format='yaml'):
        """
        Save quiz data to structured file.

        Args:
            lecture_number: Lecture sequence number
            lecture_title: Lecture title
            quiz_data: Dict with 'questions' and 'metadata'
            output_format: Output format ('yaml' or 'json')

        Returns:
            str: Filename of saved quiz, or None if failed
        """
        if not quiz_data or not quiz_data.get('questions'):
            return None

        try:
            # Generate filename
            extension = 'yaml' if output_format == 'yaml' else 'json'
            sanitized = self._sanitize_filename(lecture_title)
            filename = f"{lecture_number:03d}-{sanitized}.{extension}"
            filepath = self.quizzes_dir / filename

            # Format quiz data
            quiz_content = {
                'lecture_number': lecture_number,
                'title': lecture_title,
                'lecture_id': quiz_data.get('lecture_id'),
                'metadata': quiz_data.get('metadata', {}),
                'questions': quiz_data.get('questions', [])
            }

            # Save as YAML or JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                if output_format == 'yaml':
                    import yaml
                    yaml.dump(quiz_content, f, default_flow_style=False, sort_keys=False)
                else:
                    import json
                    json.dump(quiz_content, f, indent=2)

            self.created_files.append(str(filepath))
            self.extraction_stats['quizzes'] += 1
            return filename

        except ImportError as e:
            print(f"⚠️  Missing required library for {output_format} format: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Error saving quiz: {e}")
            return None

    def save_resource_catalog(self, lecture_number, lecture_title, resource_data):
        """
        Save resource catalog to markdown file.

        Args:
            lecture_number: Lecture sequence number
            lecture_title: Lecture title
            resource_data: Dict with 'resources' list

        Returns:
            str: Filename of saved catalog, or None if failed
        """
        if not resource_data or not resource_data.get('resources'):
            return None

        try:
            # Generate filename
            sanitized = self._sanitize_filename(lecture_title)
            filename = f"{lecture_number:03d}-{sanitized}-resources.md"
            filepath = self.resources_dir / filename

            # Format resource catalog
            lines = []
            lines.append(f"# Resources: {lecture_title}")
            lines.append("")
            lines.append(f"**Lecture**: {lecture_number}")
            lines.append("")

            resources = resource_data.get('resources', [])
            downloaded_count = resource_data.get('metadata', {}).get('downloaded_count', 0)

            if downloaded_count > 0:
                lines.append(f"**Downloaded Files**: {downloaded_count}/{len(resources)}")
                lines.append("")

            for resource in resources:
                lines.append(f"## {resource.get('filename', 'Unknown')}")
                lines.append(f"- **Type**: {resource.get('file_type', 'Unknown')}")
                if resource.get('size'):
                    size_mb = resource['size'] / (1024 * 1024)
                    lines.append(f"- **Size**: {size_mb:.2f} MB")

                # Show download status
                if resource.get('downloaded'):
                    local_file = resource.get('local_filename', {}).get('filename', 'unknown')
                    lines.append(f"- **Status**: ✓ Downloaded as `{local_file}`")
                else:
                    lines.append(f"- **Status**: Not downloaded")
                    lines.append(f"- **Download URL**: [{resource.get('filename')}]({resource.get('url', '#')})")
                lines.append("")

            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            self.created_files.append(str(filepath))
            self.extraction_stats['resources'] += 1
            return filename

        except Exception as e:
            print(f"⚠️  Error saving resource catalog: {e}")
            return None

    def save_resource_file(self, lecture_number, lecture_title, resource_download_data):
        """
        Save a downloaded resource file.

        Args:
            lecture_number: Lecture sequence number
            lecture_title: Lecture title
            resource_download_data: Dict with 'filename', 'content', 'size' from download

        Returns:
            str: Filename of saved resource, or None if failed
        """
        if not resource_download_data:
            return None

        try:
            filename = resource_download_data.get('filename', 'unknown')
            content = resource_download_data.get('content')
            size = resource_download_data.get('size', 0)

            if not content:
                print(f"⚠️  No content to save for {filename}")
                return None

            # Create lecture-specific subdirectory for resources
            lecture_resource_dir = self.resources_dir / f"{lecture_number:03d}-{self._sanitize_filename(lecture_title)}"
            lecture_resource_dir.mkdir(exist_ok=True)

            # Save file
            filepath = lecture_resource_dir / filename

            # Write binary content
            with open(filepath, 'wb') as f:
                f.write(content)

            self.created_files.append(str(filepath))
            size_mb = size / (1024 * 1024)
            print(f"      ✓ Saved {filename} ({size_mb:.1f}MB)")

            return filename

        except Exception as e:
            print(f"⚠️  Error saving resource file {filename}: {e}")
            return None

    def save_external_links(self, links_summary):
        """
        Save external links summary to resources directory.

        Args:
            links_summary: Dict with categorized external links

        Returns:
            str: Filename of saved links file, or None if failed
        """
        if not links_summary or links_summary.get('total_resources', 0) == 0:
            return None

        try:
            filepath = self.resources_dir / 'external-links.md'

            lines = []
            lines.append("# External Resources")
            lines.append("")
            lines.append("Links to external resources mentioned throughout the course.")
            lines.append("")
            lines.append(f"**Total Unique Resources**: {links_summary.get('total_resources', 0)}")
            lines.append("")

            # Category sections
            category_labels = {
                'github': 'GitHub Repositories',
                'stackoverflow': 'Stack Overflow',
                'documentation': 'Documentation',
                'youtube': 'YouTube Videos',
                'medium': 'Medium Articles',
                'dev_to': 'Dev.to Articles',
                'other': 'Other Resources'
            }

            by_category = links_summary.get('by_category', {})

            for category, label in category_labels.items():
                resources = by_category.get(category, [])
                if not resources:
                    continue

                lines.append(f"## {label}")
                lines.append("")

                for resource in resources:
                    url = resource.get('url', '')
                    domain = resource.get('domain', 'unknown')
                    mentioned_in = resource.get('mentioned_in', [])

                    lines.append(f"### [{domain}]({url})")
                    lines.append("")
                    lines.append(f"**URL**: {url}")
                    lines.append("")
                    lines.append(f"**Mentioned in**:")
                    for mention in mentioned_in:
                        lecture_num = mention.get('lecture_number', '?')
                        lecture_title = mention.get('lecture_title', 'Unknown')
                        content_type = mention.get('content_type', 'unknown')
                        lines.append(f"- Lecture {lecture_num}: {lecture_title} ({content_type})")
                    lines.append("")

            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            self.created_files.append(str(filepath))
            print(f"  ✓ Saved external links catalog ({links_summary.get('total_resources', 0)} resources)")

            return 'external-links.md'

        except Exception as e:
            print(f"⚠️  Error saving external links: {e}")
            return None


# Example usage
if __name__ == '__main__':
    # Use current working directory as base (works for both local and Git-installed plugins)
    project_root = Path.cwd() / 'udemy-research'

    # Test file writer
    writer = CourseFileWriter(
        output_path=project_root / 'test-course',
        course_name='test-course',
        course_url='https://example.udemy.com/course/test/',
        project_root=project_root
    )

    # Create structure
    writer.create_directory_structure()

    # Test transcript save
    test_transcript = [
        {'time': '00:00', 'text': 'Welcome to this course.'},
        {'time': '00:05', 'text': 'In this lecture, we will learn about React.'},
        {'time': '00:12', 'text': 'Let\'s get started!'}
    ]

    filename = writer.save_transcript(
        lecture_number=1,
        lecture_title='Introduction to React',
        transcript_data=test_transcript
    )

    print(f"✓ Test transcript saved: {filename}")
    print(f"✓ Created {len(writer.get_created_files())} files")
