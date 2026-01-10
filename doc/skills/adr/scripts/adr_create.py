#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Create a new Architecture Decision Record with auto-numbering.

Usage:
    uv run adr_create.py --title "Use PostgreSQL for persistence"
    uv run adr_create.py --title "..." --dir docs/adr --template madr
    uv run adr_create.py --title "..." --create-dir
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# ADR directory search order
ADR_SEARCH_PATHS = [
    "docs/adr",
    "doc/adr",
    "architecture/decisions",
    ".adr",
]

# Minimal template (default)
MINIMAL_TEMPLATE = """# ADR-{number:04d}: {title}

## Status
Proposed

## Date
{date}

## Context and Problem Statement
[Describe the context and problem that led to this decision]

## Decision
[State the decision that was made and the justification]

## Consequences

**Positive:**
- [Positive consequence 1]

**Negative:**
- [Negative consequence 1]
"""

# Full MADR 4.0 template
MADR_TEMPLATE = """# ADR-{number:04d}: {title}

## Status
Proposed

## Date
{date}

## Decision Makers
- [List decision makers]

## Technical Story
[Optional: Link to issue or spec, e.g., #123]

## Context and Problem Statement
[Describe the context and problem in 2-3 sentences. You may articulate the problem as a question.]

## Decision Drivers
- [Driver 1, e.g., a force, facing concern, ...]
- [Driver 2, e.g., a force, facing concern, ...]

## Considered Options
1. [Option 1]
2. [Option 2]
3. [Option 3]

## Decision Outcome
Chosen option: "[Option N]", because [justification].

### Consequences

**Positive:**
- [Positive consequence 1]
- [Positive consequence 2]

**Negative:**
- [Negative consequence 1]

## Pros and Cons of the Options

### [Option 1]

[Description or link to more information]

- Good, because [argument]
- Bad, because [argument]

### [Option 2]

[Description or link to more information]

- Good, because [argument]
- Bad, because [argument]

### [Option 3]

[Description or link to more information]

- Good, because [argument]
- Bad, because [argument]

## More Information
[Optional: Links to related documentation, discussions, or prior art]
"""


def find_adr_directory(base_path: Path) -> Path | None:
    """Find existing ADR directory or return None."""
    for search_path in ADR_SEARCH_PATHS:
        adr_dir = base_path / search_path
        if adr_dir.exists() and adr_dir.is_dir():
            return adr_dir
    return None


def detect_numbering_style(adr_dir: Path) -> tuple[int, bool]:
    """Detect numbering padding and prefix style from existing ADRs.

    Returns:
        tuple: (padding_width, has_adr_prefix)
    """
    padding = 4  # Default padding
    has_prefix = False

    # Patterns to match ADR filenames
    patterns = [
        (re.compile(r'^ADR-(\d+)-', re.IGNORECASE), True),
        (re.compile(r'^(\d+)-'), False),
    ]

    for filepath in adr_dir.glob('*.md'):
        if filepath.name.lower() in ['readme.md', 'template.md']:
            continue
        for pattern, prefix in patterns:
            match = pattern.match(filepath.name)
            if match:
                num_str = match.group(1)
                padding = len(num_str)
                has_prefix = prefix
                return padding, has_prefix

    return padding, has_prefix


def get_next_adr_number(adr_dir: Path) -> int:
    """Scan existing ADRs and return next available number."""
    max_number = 0

    # Match patterns like: 0001-title.md, ADR-0001-title.md, 001-title.md
    pattern = re.compile(r'^(?:ADR-)?(\d+)-.*\.md$', re.IGNORECASE)

    for filepath in adr_dir.glob('*.md'):
        match = pattern.match(filepath.name)
        if match:
            number = int(match.group(1))
            max_number = max(max_number, number)

    return max_number + 1


def generate_filename(number: int, title: str, padding: int = 4, with_prefix: bool = False) -> str:
    """Generate ADR filename from number and title."""
    # Convert title to kebab-case
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')

    if with_prefix:
        return f"ADR-{number:0{padding}d}-{slug}.md"
    return f"{number:0{padding}d}-{slug}.md"


def create_adr(
    title: str,
    adr_dir: Path,
    template: str = "minimal",
) -> Path:
    """Create a new ADR file."""
    number = get_next_adr_number(adr_dir)
    padding, has_prefix = detect_numbering_style(adr_dir)
    filename = generate_filename(number, title, padding, has_prefix)
    filepath = adr_dir / filename

    # Select template
    if template == "madr":
        content = MADR_TEMPLATE.format(
            number=number,
            title=title,
            date=date.today().isoformat()
        )
    else:
        content = MINIMAL_TEMPLATE.format(
            number=number,
            title=title,
            date=date.today().isoformat()
        )

    # Write file
    filepath.write_text(content)
    return filepath


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a new Architecture Decision Record"
    )
    parser.add_argument(
        "--title", "-t",
        required=True,
        help="Title of the ADR (e.g., 'Use PostgreSQL for persistence')"
    )
    parser.add_argument(
        "--dir", "-d",
        help="ADR directory path (auto-detected if not specified)"
    )
    parser.add_argument(
        "--template",
        choices=["minimal", "madr"],
        default="minimal",
        help="Template to use (default: minimal)"
    )
    parser.add_argument(
        "--create-dir",
        action="store_true",
        help="Create ADR directory if it doesn't exist"
    )

    args = parser.parse_args()

    # Determine ADR directory
    base_path = Path.cwd()

    if args.dir:
        adr_dir = Path(args.dir)
        if not adr_dir.is_absolute():
            adr_dir = base_path / adr_dir
    else:
        adr_dir = find_adr_directory(base_path)
        if not adr_dir:
            if args.create_dir:
                adr_dir = base_path / "docs" / "adr"
                adr_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created ADR directory: {adr_dir}")
            else:
                print("Error: No ADR directory found.")
                print(f"Searched: {', '.join(ADR_SEARCH_PATHS)}")
                print("Use --dir to specify or --create-dir to create docs/adr/")
                return 1

    if not adr_dir.exists():
        if args.create_dir:
            adr_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created ADR directory: {adr_dir}")
        else:
            print(f"Error: Directory does not exist: {adr_dir}")
            return 1

    # Create ADR
    filepath = create_adr(
        title=args.title,
        adr_dir=adr_dir,
        template=args.template
    )

    number = get_next_adr_number(adr_dir) - 1
    print(f"Created: {filepath}")
    print(f"Number: ADR-{number:04d}")
    print(f"\nNext: Run adr_index.py to update README.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
