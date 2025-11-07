#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
# -*- coding: utf-8 -*-
"""
Tutorial Validation Script

Validates tutorial outputs for structural correctness and completeness.

Usage:
    uv run validate_tutorial.py article.md [video_script.md] [chapters.json] [seo.yaml]

    # Or with python3 (requires pyyaml installed):
    python3 validate_tutorial.py article.md [video_script.md] [chapters.json] [seo.yaml]

Exit Codes:
    0 - All checks passed
    1 - Warnings (non-critical issues)
    2 - Errors (critical issues preventing use)
"""

import sys
import re
import json
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Any


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ Warning: {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ Error: {text}{Colors.END}")


# Article validation patterns
ARTICLE_REQUIRED_SECTIONS = [
    (r"^#\s+.+", "H1 title"),
    (r"^\*\*Audience:\*\*", "Audience metadata"),
    (r"^\*\*Language", "Language/stack metadata"),
    (r"^##\s+\d+\.\s+What You'll (Build|Learn)", "Section 1: What You'll Build/Learn"),
    (r"^##\s+\d+\.\s+Concept Overview", "Section 2: Concept Overview"),
    (r"^##\s+\d+\.\s+Minimal (Runnable )?Example", "Section 3: Minimal Example"),
    (r"^##\s+\d+\.\s+Guided Steps", "Section 4: Guided Steps"),
    (r"^##\s+\d+\.\s+Challenge", "Challenge section"),
    (r"^##\s+\d+\.\s+Troubleshooting", "Troubleshooting section"),
    (r"^##\s+\d+\.\s+Summary", "Summary section"),
]

ARTICLE_RECOMMENDED = [
    (r"```[\w]+", "Code blocks with language tags"),
    (r">\s+💡", "Tips (💡)"),
    (r">\s+⚠️", "Warnings (⚠️)"),
    (r"---\s+Progress Check\s+---", "Progress checkpoints"),
    (r"<details><summary>", "Collapsible solutions"),
    (r"\*\*Expected Output:\*\*|\*\*Output:\*\*", "Expected outputs"),
]

# Video script validation patterns
SCRIPT_REQUIRED_SECTIONS = [
    (r"(?i)(hook|opening)", "Hook/Opening"),
    (r"(?i)agenda", "Agenda"),
    (r"(?i)(sections?|content)", "Main sections"),
    (r"(?i)(cta|call to action|subscribe)", "Call to Action"),
]

SCRIPT_RECOMMENDED = [
    (r"\[\d{2}:\d{2}", "Timing estimates [MM:SS]"),
    (r"(?i)(visual|screen|b-roll)", "Visual/stage directions"),
    (r"(?i)on-screen", "On-screen text cues"),
]

# SEO validation
SEO_REQUIRED_FIELDS = [
    "title",
    "slug",
    "description",
    "keywords",
    "tags",
    "reading_time_min",
    "target_audience",
    "difficulty",
]


def check_file_exists(path: Path) -> Tuple[bool, str]:
    """Check if file exists and is readable"""
    if not path.exists():
        return False, f"File not found: {path}"
    if not path.is_file():
        return False, f"Not a file: {path}"
    try:
        path.read_text(encoding="utf-8")
        return True, ""
    except Exception as e:
        return False, f"Cannot read file: {e}"


def validate_article(path: Path) -> Tuple[List[str], List[str]]:
    """
    Validate blog article structure.
    Returns (errors, warnings)
    """
    errors = []
    warnings = []

    exists, msg = check_file_exists(path)
    if not exists:
        errors.append(msg)
        return errors, warnings

    content = path.read_text(encoding="utf-8")

    # Check required sections
    for pattern, description in ARTICLE_REQUIRED_SECTIONS:
        if not re.search(pattern, content, flags=re.MULTILINE):
            errors.append(f"Missing required section: {description}")

    # Check recommended elements
    for pattern, description in ARTICLE_RECOMMENDED:
        if not re.search(pattern, content, flags=re.MULTILINE):
            warnings.append(f"Missing recommended element: {description}")

    # Check for code blocks without language tags
    untagged_code = re.findall(r"^```\s*$", content, flags=re.MULTILINE)
    if untagged_code:
        warnings.append(f"Found {len(untagged_code)} code blocks without language tags")

    # Check for broken internal links
    internal_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
    for link_text, link_url in internal_links:
        if link_url.startswith('#'):
            # Internal anchor
            anchor = link_url[1:]
            # Check if anchor exists in headers
            headers = re.findall(r"^#+\s+(.+)$", content, flags=re.MULTILINE)
            anchor_texts = [h.lower().replace(' ', '-').replace('.', '') for h in headers]
            if anchor.lower() not in anchor_texts:
                warnings.append(f"Potentially broken internal link: {link_url}")

    # Check for numbered sections
    sections = re.findall(r"^##\s+(\d+)\.", content, flags=re.MULTILINE)
    if sections:
        section_nums = [int(n) for n in sections]
        expected = list(range(1, len(section_nums) + 1))
        if section_nums != expected:
            warnings.append(f"Section numbering is non-sequential: {section_nums}")

    # Check article length (should be substantial)
    word_count = len(content.split())
    if word_count < 500:
        warnings.append(f"Article is quite short ({word_count} words). Expected 500+.")
    elif word_count > 5000:
        warnings.append(f"Article is very long ({word_count} words). Consider breaking into series.")

    return errors, warnings


def validate_video_script(path: Path) -> Tuple[List[str], List[str]]:
    """
    Validate video script structure.
    Returns (errors, warnings)
    """
    errors = []
    warnings = []

    exists, msg = check_file_exists(path)
    if not exists:
        errors.append(msg)
        return errors, warnings

    content = path.read_text(encoding="utf-8")

    # Check required sections
    for pattern, description in SCRIPT_REQUIRED_SECTIONS:
        if not re.search(pattern, content, flags=re.MULTILINE):
            errors.append(f"Missing required section: {description}")

    # Check recommended elements
    for pattern, description in SCRIPT_RECOMMENDED:
        if not re.search(pattern, content, flags=re.MULTILINE):
            warnings.append(f"Missing recommended element: {description}")

    # Check for timing format consistency
    timings = re.findall(r"\[(\d{1,2}:\d{2})", content)
    if timings:
        for i, timing in enumerate(timings[:-1]):
            current = timing_to_seconds(timing)
            next_time = timing_to_seconds(timings[i + 1])
            if current >= next_time:
                warnings.append(f"Non-sequential timing: {timing} -> {timings[i + 1]}")

    return errors, warnings


def timing_to_seconds(timing: str) -> int:
    """Convert MM:SS or HH:MM:SS to seconds"""
    parts = timing.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def validate_chapters(path: Path) -> Tuple[List[str], List[str]]:
    """
    Validate chapters JSON file.
    Returns (errors, warnings)
    """
    errors = []
    warnings = []

    exists, msg = check_file_exists(path)
    if not exists:
        errors.append(msg)
        return errors, warnings

    try:
        content = path.read_text(encoding="utf-8")
        chapters = json.loads(content)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return errors, warnings

    # Check structure
    if not isinstance(chapters, list):
        errors.append("Chapters must be a JSON array")
        return errors, warnings

    if len(chapters) == 0:
        errors.append("Chapters array is empty")
        return errors, warnings

    # Validate each chapter
    for i, chapter in enumerate(chapters):
        if not isinstance(chapter, dict):
            errors.append(f"Chapter {i} is not an object")
            continue

        if "time" not in chapter:
            errors.append(f"Chapter {i} missing 'time' field")
        else:
            time = chapter["time"]
            if not re.match(r"^\d{1,2}:\d{2}$", time):
                errors.append(f"Chapter {i} has invalid time format: {time} (expected MM:SS)")

        if "title" not in chapter:
            errors.append(f"Chapter {i} missing 'title' field")
        else:
            title = chapter["title"]
            if len(title) > 100:
                warnings.append(f"Chapter {i} title is very long ({len(title)} chars)")

    # Check for sequential times
    times = []
    for i, chapter in enumerate(chapters):
        if "time" in chapter:
            times.append(timing_to_seconds(chapter["time"]))

    for i in range(len(times) - 1):
        if times[i] >= times[i + 1]:
            warnings.append(f"Non-sequential chapter times at index {i}: {chapters[i]['time']} -> {chapters[i+1]['time']}")

    # Check that first chapter starts at 0:00
    if times and times[0] != 0:
        warnings.append(f"First chapter should start at 00:00, but starts at {chapters[0]['time']}")

    return errors, warnings


def validate_seo(path: Path) -> Tuple[List[str], List[str]]:
    """
    Validate SEO YAML file.
    Returns (errors, warnings)
    """
    errors = []
    warnings = []

    exists, msg = check_file_exists(path)
    if not exists:
        errors.append(msg)
        return errors, warnings

    try:
        content = path.read_text(encoding="utf-8")
        seo_data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")
        return errors, warnings

    if not isinstance(seo_data, dict):
        errors.append("SEO file must be a YAML object")
        return errors, warnings

    # Check required fields
    for field in SEO_REQUIRED_FIELDS:
        if field not in seo_data:
            errors.append(f"Missing required field: {field}")

    # Validate specific fields
    if "title" in seo_data:
        title_len = len(seo_data["title"])
        if title_len > 60:
            warnings.append(f"Title is too long ({title_len} chars). Recommended: under 60 chars.")
        elif title_len < 10:
            warnings.append(f"Title is very short ({title_len} chars).")

    if "description" in seo_data:
        desc_len = len(seo_data["description"])
        if desc_len < 50 or desc_len > 160:
            warnings.append(f"Description length ({desc_len} chars) outside optimal range (50-160 chars).")

    if "slug" in seo_data:
        slug = seo_data["slug"]
        if not re.match(r"^[a-z0-9-]+$", slug):
            warnings.append(f"Slug contains non-URL-friendly characters: {slug}")

    if "keywords" in seo_data:
        keywords = seo_data["keywords"]
        if not isinstance(keywords, list):
            errors.append("Keywords must be an array")
        elif len(keywords) < 3:
            warnings.append(f"Only {len(keywords)} keywords. Recommended: 3-5.")
        elif len(keywords) > 10:
            warnings.append(f"Too many keywords ({len(keywords)}). Recommended: 3-5 primary.")

    if "tags" in seo_data:
        tags = seo_data["tags"]
        if not isinstance(tags, list):
            errors.append("Tags must be an array")
        elif len(tags) < 5:
            warnings.append(f"Only {len(tags)} tags. Recommended: 8-12.")
        elif len(tags) > 20:
            warnings.append(f"Too many tags ({len(tags)}). Recommended: 8-12.")

    if "reading_time_min" in seo_data:
        reading_time = seo_data["reading_time_min"]
        if not isinstance(reading_time, (int, float)):
            errors.append(f"reading_time_min must be a number, got: {type(reading_time).__name__}")

    return errors, warnings


def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Usage: validate_tutorial.py article.md [video_script.md] [chapters.json] [seo.yaml]{Colors.END}")
        print(f"\nValidates tutorial files for structural correctness.")
        print(f"\nExit codes:")
        print(f"  0 - All checks passed")
        print(f"  1 - Warnings (non-critical issues)")
        print(f"  2 - Errors (critical issues)")
        sys.exit(1)

    all_errors = []
    all_warnings = []

    # Validate article (required)
    article_path = Path(sys.argv[1])
    print_header(f"Validating Article: {article_path.name}")
    errors, warnings = validate_article(article_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    if errors:
        for error in errors:
            print_error(error)
    if warnings:
        for warning in warnings:
            print_warning(warning)
    if not errors and not warnings:
        print_success("Article validation passed!")

    # Validate video script (optional)
    if len(sys.argv) >= 3:
        script_path = Path(sys.argv[2])
        print_header(f"Validating Video Script: {script_path.name}")
        errors, warnings = validate_video_script(script_path)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

        if errors:
            for error in errors:
                print_error(error)
        if warnings:
            for warning in warnings:
                print_warning(warning)
        if not errors and not warnings:
            print_success("Video script validation passed!")

    # Validate chapters (optional)
    if len(sys.argv) >= 4:
        chapters_path = Path(sys.argv[3])
        print_header(f"Validating Chapters: {chapters_path.name}")
        errors, warnings = validate_chapters(chapters_path)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

        if errors:
            for error in errors:
                print_error(error)
        if warnings:
            for warning in warnings:
                print_warning(warning)
        if not errors and not warnings:
            print_success("Chapters validation passed!")

    # Validate SEO (optional)
    if len(sys.argv) >= 5:
        seo_path = Path(sys.argv[4])
        print_header(f"Validating SEO: {seo_path.name}")
        errors, warnings = validate_seo(seo_path)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

        if errors:
            for error in errors:
                print_error(error)
        if warnings:
            for warning in warnings:
                print_warning(warning)
        if not errors and not warnings:
            print_success("SEO validation passed!")

    # Summary
    print_header("Validation Summary")
    print(f"Files checked: {len(sys.argv) - 1}")
    print(f"Errors: {len(all_errors)}")
    print(f"Warnings: {len(all_warnings)}")

    if all_errors:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILED{Colors.END}")
        print(f"{Colors.RED}Fix errors before using these files.{Colors.END}")
        sys.exit(2)
    elif all_warnings:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠  VALIDATION PASSED WITH WARNINGS{Colors.END}")
        print(f"{Colors.YELLOW}Consider addressing warnings for better quality.{Colors.END}")
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL VALIDATIONS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}Tutorial files are ready to use.{Colors.END}")
        sys.exit(0)


if __name__ == "__main__":
    main()
