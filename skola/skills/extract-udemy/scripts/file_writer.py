#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Course File Writer

Handles file organization and writing for extracted course content.
Creates directory structure and saves transcripts in organized format.
"""

import os
import re
import json
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

        # Track all resources for consolidated summary
        self.all_resources = []  # List of dicts: {section, lecture_number, lecture_title, resources, failed_resources}

        # Phase 2: Progress tracking for resume capability
        self.progress_file = self.output_path / '.extraction_progress.json'
        self.completed_lectures = self._load_progress()

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

    def _load_progress(self):
        """
        Load progress from previous extraction.

        Returns:
            set: Set of completed lecture IDs
        """
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('completed_lectures', []))
            except Exception as e:
                print(f"  ⚠️  Could not load progress file: {e}")
        return set()

    def mark_lecture_complete(self, lecture_id):
        """
        Mark a lecture as successfully extracted.

        Args:
            lecture_id: Unique identifier for the lecture
        """
        self.completed_lectures.add(str(lecture_id))
        self._save_progress()

    def _save_progress(self):
        """Save current extraction progress to file."""
        import time
        try:
            with open(self.progress_file, 'w') as f:
                json.dump({
                    'completed_lectures': list(self.completed_lectures),
                    'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=2)
        except Exception as e:
            print(f"  ⚠️  Could not save progress: {e}")

    def is_lecture_complete(self, lecture_id):
        """
        Check if a lecture was already extracted.

        Args:
            lecture_id: Unique identifier for the lecture

        Returns:
            bool: True if lecture was already completed
        """
        return str(lecture_id) in self.completed_lectures

    def clear_progress(self):
        """Delete progress file after successful completion."""
        try:
            if self.progress_file.exists():
                self.progress_file.unlink()
        except Exception as e:
            print(f"  ⚠️  Could not delete progress file: {e}")

    def _calculate_directory_sizes(self):
        """
        Calculate sizes of content directories.

        Returns:
            dict: Directory sizes in human-readable format
        """
        def get_dir_size(directory):
            """Get total size of directory in bytes."""
            total = 0
            try:
                for entry in os.scandir(directory):
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += get_dir_size(entry.path)
            except Exception:
                pass
            return total

        def format_size(bytes_size):
            """Format bytes to human-readable size."""
            if bytes_size == 0:
                return "0 B"
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.1f} TB"

        sizes = {}
        directories = {
            'transcripts': self.transcripts_dir,
            'articles': self.articles_dir,
            'resources': self.resources_dir,
            'quizzes': self.quizzes_dir
        }

        for name, directory in directories.items():
            if directory.exists():
                size_bytes = get_dir_size(directory)
                sizes[name] = format_size(size_bytes)
                sizes[f'{name}_bytes'] = size_bytes
            else:
                sizes[name] = "0 B"
                sizes[f'{name}_bytes'] = 0

        return sizes

    def update_readme_with_stats(self, course_data, external_links_count=0):
        """
        Update README.md with actual extraction statistics after extraction completes.

        Args:
            course_data: Course information dict
            external_links_count: Number of external links found

        Returns:
            bool: True if successful
        """
        try:
            readme_file = self.output_path / 'README.md'
            if not readme_file.exists():
                return False

            # Read current README
            with open(readme_file, 'r') as f:
                content = f.read()

            # Calculate directory sizes
            sizes = self._calculate_directory_sizes()

            # Get course structure info
            sections = course_data.get('sections', [])
            num_sections = len(sections)
            num_lectures = sum(len(s.get('lectures', [])) for s in sections)

            # Get rating count
            num_ratings = course_data.get('num_reviews', 0)

            # Get last updated date
            last_updated = course_data.get('last_update_date', '')
            if last_updated:
                try:
                    # Try parsing common date formats
                    from datetime import datetime as dt_parser
                    for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d']:
                        try:
                            dt = dt_parser.strptime(last_updated.replace('Z', '+00:00')[:19], fmt[:19])
                            last_updated = dt.strftime('%B %Y')
                            break
                        except ValueError:
                            continue
                    else:
                        # Fallback if date parsing fails
                        last_updated = 'Recently'
                except:
                    # Fallback if date parsing fails
                    last_updated = 'Recently'
            else:
                last_updated = 'Unknown'

            # Current date for extraction
            extraction_date = datetime.now().strftime('%B %d, %Y')

            # Get instructor bio if available
            instructor_bio = ''
            instructors = course_data.get('visible_instructors', [])
            if instructors and len(instructors) > 0:
                instructor = instructors[0]
                job_title = instructor.get('job_title', '')
                if job_title:
                    instructor_bio = f"- {job_title}"

            # Generate course sections formatted list
            course_sections_formatted = ""
            for idx, section in enumerate(sections, 1):
                section_title = section.get('title', f'Section {idx}')
                lecture_count = len(section.get('lectures', []))
                course_sections_formatted += f"{idx}. **{section_title}** ({lecture_count} lectures)\n"

            # Replace all template variables
            replacements = {
                '{NUM_RATINGS}': f"{num_ratings:,}",
                '{LAST_UPDATED}': last_updated,
                '{EXTRACTION_DATE}': extraction_date,
                '{NUM_SECTIONS}': str(num_sections),
                '{NUM_LECTURES}': str(num_lectures),
                '{NUM_TRANSCRIPTS}': str(self.extraction_stats['transcripts']),
                '{NUM_ARTICLES}': str(self.extraction_stats['articles']),
                '{NUM_RESOURCES}': str(len(self.all_resources)),
                '{NUM_EXTERNAL_LINKS}': str(external_links_count),
                '{TRANSCRIPTS_SIZE}': sizes.get('transcripts', '0 B'),
                '{ARTICLES_SIZE}': sizes.get('articles', '0 B'),
                '{RESOURCES_SIZE}': sizes.get('resources', '0 B'),
                '{COURSE_SLUG}': self.course_name,
                '{COURSE_SECTIONS}': course_sections_formatted.rstrip(),
                '{INSTRUCTOR_BIO}': instructor_bio
            }

            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)

            # Write updated README
            with open(readme_file, 'w') as f:
                f.write(content)

            return True

        except Exception as e:
            print(f"⚠️  Error updating README with stats: {e}")
            return False

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

    def track_resources(self, section_title, lecture_number, lecture_title, resource_data):
        """
        Track resources for consolidated summary file (replaces save_resource_catalog).

        Args:
            section_title: Section title
            lecture_number: Lecture sequence number
            lecture_title: Lecture title
            resource_data: Dict with 'resources' list and 'metadata'

        Returns:
            bool: True if tracked successfully
        """
        if not resource_data or not resource_data.get('resources'):
            return False

        try:
            resources = resource_data.get('resources', [])
            metadata = resource_data.get('metadata', {})

            # Separate successful and failed downloads
            downloaded_resources = []
            failed_resources = []

            for resource in resources:
                # Update resource with actual file size from disk if available
                if resource.get('downloaded'):
                    # Try to get actual file size from disk
                    sanitized_title = self._sanitize_filename(lecture_title)
                    resource_dir = self.resources_dir / f"{lecture_number:03d}-{sanitized_title}"
                    filename = resource.get('filename', '')
                    if filename:
                        filepath = resource_dir / filename
                        if filepath.exists():
                            actual_size = os.path.getsize(filepath)
                            resource['size'] = actual_size  # Update with actual size

                    downloaded_resources.append(resource)
                else:
                    failed_resources.append(resource)

            # Add to tracking list
            self.all_resources.append({
                'section_title': section_title,
                'lecture_number': lecture_number,
                'lecture_title': lecture_title,
                'resources': downloaded_resources,
                'failed_resources': failed_resources,
                'metadata': metadata
            })

            self.extraction_stats['resources'] += 1
            return True

        except Exception as e:
            print(f"⚠️  Error tracking resources: {e}")
            return False

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

    def generate_downloaded_resources_summary(self, config=None):
        """
        Generate consolidated DOWNLOADED_RESOURCES.md file at course root.

        Args:
            config: Configuration dict with max_file_size_mb, etc.

        Returns:
            str: Filename of generated summary, or None if failed
        """
        if not self.all_resources:
            print("  ⓘ No resources to summarize")
            return None

        try:
            filepath = self.output_path / 'DOWNLOADED_RESOURCES.md'

            # Calculate statistics
            total_resources = sum(len(r['resources']) + len(r['failed_resources']) for r in self.all_resources)
            total_downloaded = sum(len(r['resources']) for r in self.all_resources)
            total_failed = sum(len(r['failed_resources']) for r in self.all_resources)

            # Calculate total size
            total_size_bytes = 0
            file_type_stats = {}

            for resource_group in self.all_resources:
                for resource in resource_group['resources']:
                    size = resource.get('size', 0)
                    total_size_bytes += size

                    file_type = resource.get('file_type', 'Unknown')
                    if file_type not in file_type_stats:
                        file_type_stats[file_type] = {'count': 0, 'size': 0}
                    file_type_stats[file_type]['count'] += 1
                    file_type_stats[file_type]['size'] += size

            total_size_mb = total_size_bytes / (1024 * 1024)

            # Build markdown content
            lines = []
            lines.append("# Downloaded Resources")
            lines.append("")
            lines.append("## Summary Statistics")
            lines.append("")
            lines.append(f"**Total Resources**: {total_resources} files")
            lines.append(f"**Successfully Downloaded**: {total_downloaded}/{total_resources} ({100 * total_downloaded / total_resources if total_resources > 0 else 0:.1f}%)")
            lines.append(f"**Total Size**: {total_size_mb:.1f} MB")
            lines.append(f"**Failed Downloads**: {total_failed}")
            lines.append("")

            # File types breakdown
            if file_type_stats:
                lines.append("### File Types Breakdown")
                for file_type, stats in sorted(file_type_stats.items()):
                    size_mb = stats['size'] / (1024 * 1024)
                    lines.append(f"- **{file_type}**: {stats['count']} files ({size_mb:.1f} MB)")
                lines.append("")

            lines.append("---")
            lines.append("")

            # Group resources by section
            resources_by_section = {}
            for resource_group in self.all_resources:
                section_title = resource_group['section_title']
                if section_title not in resources_by_section:
                    resources_by_section[section_title] = []
                resources_by_section[section_title].append(resource_group)

            # Output by section
            for section_title, resource_groups in resources_by_section.items():
                lines.append(f"## {section_title}")
                lines.append("")

                for rg in resource_groups:
                    lecture_number = rg['lecture_number']
                    lecture_title = rg['lecture_title']
                    resources = rg['resources']

                    if not resources:
                        continue

                    lines.append(f"### Lecture {lecture_number}: {lecture_title}")

                    for resource in resources:
                        filename = resource.get('filename', 'Unknown')
                        size = resource.get('size', 0)
                        size_mb = size / (1024 * 1024)

                        # Generate brief description from lecture title (2-3 words)
                        description = self._generate_resource_description(lecture_title, filename)

                        lines.append(f"- **{filename}** ({size_mb:.1f} MB) - {description}")
                        lines.append(f"  - Status: ✓ Downloaded")

                        # Build relative path to resource
                        sanitized_title = self._sanitize_filename(lecture_title)
                        rel_path = f"resources/{lecture_number:03d}-{sanitized_title}/{filename}"
                        lines.append(f"  - Location: `{rel_path}`")

                    lines.append("")

                lines.append("---")
                lines.append("")

            # Failed downloads section
            if total_failed > 0:
                lines.append("## Failed Downloads")
                lines.append("")

                for resource_group in self.all_resources:
                    failed_resources = resource_group['failed_resources']
                    if not failed_resources:
                        continue

                    lecture_number = resource_group['lecture_number']
                    lecture_title = resource_group['lecture_title']

                    lines.append(f"### Lecture {lecture_number}: {lecture_title}")

                    for resource in failed_resources:
                        filename = resource.get('filename', 'Unknown')
                        size = resource.get('size', 0)
                        size_mb = size / (1024 * 1024)

                        lines.append(f"- **{filename}** ({size_mb:.1f} MB)")

                        # Determine failure reason
                        max_size_mb = config.get('max_resource_size_mb', 100) if config else 100
                        if size_mb > max_size_mb:
                            reason = f"File size exceeds limit ({max_size_mb} MB)"
                        else:
                            reason = "Download failed (network error or unavailable)"

                        lines.append(f"  - Reason: {reason}")
                        if resource.get('url'):
                            lines.append(f"  - URL: {resource.get('url')}")

                    lines.append("")

                lines.append("---")
                lines.append("")

            # Download configuration
            lines.append("## Download Configuration")
            lines.append("")
            max_size = config.get('max_resource_size_mb', 100) if config else 100
            lines.append(f"- **Max file size limit**: {max_size} MB")
            lines.append(f"- **Download enabled**: Yes")
            lines.append(f"- **Extraction date**: {datetime.now().strftime('%B %d, %Y')}")
            lines.append("")

            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            self.created_files.append(str(filepath))
            print(f"  ✓ Generated DOWNLOADED_RESOURCES.md ({total_downloaded} resources)")

            return 'DOWNLOADED_RESOURCES.md'

        except Exception as e:
            print(f"⚠️  Error generating downloaded resources summary: {e}")
            return None

    def _generate_resource_description(self, lecture_title, filename):
        """
        Generate a brief 2-3 word description from lecture title context.

        Args:
            lecture_title: Lecture title
            filename: Resource filename

        Returns:
            str: Brief description
        """
        # Extract key words from lecture title
        # Remove common words and punctuation
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'part', 'lecture'}

        title_words = lecture_title.lower().replace('-', ' ').split()
        key_words = [w for w in title_words if w not in common_words and len(w) > 2]

        # Take first 2-3 meaningful words
        description_words = key_words[:3] if len(key_words) >= 3 else key_words[:2] if len(key_words) >= 2 else key_words

        if not description_words:
            # Fallback to filename
            filename_base = filename.rsplit('.', 1)[0]
            description_words = filename_base.replace('-', ' ').replace('_', ' ').split()[:3]

        # Capitalize and join
        description = ' '.join(word.capitalize() for word in description_words)

        return description if description else "Course resource"


# Example usage
if __name__ == '__main__':
    # Use current working directory as base (works for both local and Git-installed plugins)
    project_root = Path.cwd() / 'skola-research' / 'udemy'

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
