#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Update README.md index table for ADRs.

Usage:
    uv run adr_index.py --dir docs/adr
    uv run adr_index.py --dir docs/adr --dry-run
"""

import argparse
import re
import sys
from pathlib import Path

INDEX_HEADER = """# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for this project.

## What is an ADR?

An Architecture Decision Record captures an important architectural decision made along with its context and consequences. ADRs help us:

- Document the "why" behind technical decisions
- Onboard new team members quickly
- Avoid revisiting settled decisions
- Track the evolution of the architecture

## ADR Index

| Number | Title | Status | Date |
|--------|-------|--------|------|
"""

INDEX_FOOTER = """

## ADR Lifecycle

| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion, not yet accepted |
| **Accepted** | Decision has been made and is in effect |
| **Deprecated** | No longer relevant but kept for historical reference |
| **Superseded** | Replaced by a newer ADR (link to replacement) |

## Creating a New ADR

Use the adr_create.py script:

```bash
uv run scripts/adr_create.py --title "Your Decision Title"
uv run scripts/adr_create.py --title "..." --template madr  # Full MADR template
```

## References

- [MADR Template](https://adr.github.io/madr/)
- [ADR GitHub Organization](https://adr.github.io/)
"""


def parse_adr_file(filepath: Path) -> dict | None:
    """Extract metadata from an ADR file."""
    try:
        content = filepath.read_text()
    except Exception:
        return None

    # Extract title from first heading
    title_match = re.search(r'^#\s+(?:ADR-\d+:\s*)?(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filepath.stem

    # Extract number from filename
    num_match = re.match(r'^(?:ADR-)?(\d+)-', filepath.name, re.IGNORECASE)
    number = int(num_match.group(1)) if num_match else 0

    # Extract status
    status_match = re.search(r'^##\s+Status\s*\n+([^\n#]+)', content, re.MULTILINE | re.IGNORECASE)
    status = status_match.group(1).strip() if status_match else "Unknown"

    # Clean up status (remove markdown links if present)
    status = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', status)

    # Extract date
    date_match = re.search(r'^##\s+Date\s*\n+(\d{4}-\d{2}-\d{2})', content, re.MULTILINE | re.IGNORECASE)
    date_str = date_match.group(1) if date_match else ""

    return {
        "number": number,
        "title": title,
        "status": status,
        "date": date_str,
        "filename": filepath.name
    }


def generate_index(adr_dir: Path) -> str:
    """Generate README.md content with ADR index."""
    adrs = []

    # Find all ADR files
    for filepath in adr_dir.glob('*.md'):
        if filepath.name.lower() in ['readme.md', 'template.md']:
            continue

        metadata = parse_adr_file(filepath)
        if metadata and metadata["number"] > 0:
            adrs.append(metadata)

    # Sort by number
    adrs.sort(key=lambda x: x['number'])

    # Build table rows
    rows = []
    for adr in adrs:
        # Detect padding from the ADR with highest number
        padding = 4
        if adrs:
            max_num = max(a['number'] for a in adrs)
            padding = len(str(max_num)) if len(str(max_num)) >= 3 else 4

        num_str = f"{adr['number']:0{padding}d}"
        row = f"| {num_str} | [{adr['title']}]({adr['filename']}) | {adr['status']} | {adr['date']} |"
        rows.append(row)

    return INDEX_HEADER + '\n'.join(rows) + INDEX_FOOTER


def update_readme(adr_dir: Path, dry_run: bool = False) -> bool:
    """Update or create README.md in ADR directory."""
    readme_path = adr_dir / "README.md"
    content = generate_index(adr_dir)

    if dry_run:
        print("=== DRY RUN - Would write to README.md ===\n")
        print(content)
        return True

    readme_path.write_text(content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update README.md index for ADRs"
    )
    parser.add_argument(
        "--dir", "-d",
        required=True,
        help="ADR directory path"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output without writing file"
    )

    args = parser.parse_args()

    adr_dir = Path(args.dir)
    if not adr_dir.is_absolute():
        adr_dir = Path.cwd() / adr_dir

    if not adr_dir.exists():
        print(f"Error: Directory does not exist: {adr_dir}")
        return 1

    success = update_readme(adr_dir, args.dry_run)

    if success and not args.dry_run:
        print(f"Updated: {adr_dir / 'README.md'}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
