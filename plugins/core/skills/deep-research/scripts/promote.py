#!/usr/bin/env python3
"""
Promote research from Tier 1 cache to Tier 2 project docs.

Usage:
    python promote.py <slug> [--output-dir docs/research]
    python promote.py <slug> --refresh  # Update existing promoted file

Environment:
    RESEARCH_CACHE_DIR: Override default cache location (~/.claude/plugins/research)
    RESEARCH_DOCS_DIR: Override default output directory (docs/research)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# Configuration
DEFAULT_CACHE_DIR = Path.home() / ".claude" / "plugins" / "research"
DEFAULT_DOCS_DIR = Path("docs/research")

# Section markers
AUTO_START = "<!-- AUTO-GENERATED: Start -->"
AUTO_END = "<!-- AUTO-GENERATED: End -->"
TEAM_START = "<!-- TEAM-NOTES: Start -->"
TEAM_END = "<!-- TEAM-NOTES: End -->"

TEAM_NOTES_TEMPLATE = """
## Team Context

_Add project-specific notes, implementation references, and team knowledge here._

"""


def get_cache_dir() -> Path:
    """Get cache directory from environment or default."""
    env_dir = os.environ.get("RESEARCH_CACHE_DIR")
    if env_dir:
        return Path(env_dir)
    return DEFAULT_CACHE_DIR


def get_docs_dir(override: Optional[str] = None) -> Path:
    """Get docs directory from argument, environment, or default."""
    if override:
        return Path(override)
    env_dir = os.environ.get("RESEARCH_DOCS_DIR")
    if env_dir:
        return Path(env_dir)
    return DEFAULT_DOCS_DIR


def get_cached_entry(slug: str) -> Optional[dict]:
    """Read cached research entry."""
    cache_dir = get_cache_dir()
    entry_dir = cache_dir / "entries" / slug

    metadata_file = entry_dir / "metadata.json"
    content_file = entry_dir / "content.md"

    if not metadata_file.exists() or not content_file.exists():
        return None

    try:
        metadata = json.loads(metadata_file.read_text())
        content = content_file.read_text()
        return {"metadata": metadata, "content": content}
    except (json.JSONDecodeError, IOError):
        return None


def extract_team_notes(content: str) -> Optional[str]:
    """Extract existing team notes from promoted file."""
    pattern = re.compile(
        rf"{re.escape(TEAM_START)}(.*?){re.escape(TEAM_END)}",
        re.DOTALL
    )
    match = pattern.search(content)
    if match:
        return match.group(1)
    return None


def build_promoted_content(
    metadata: dict,
    auto_content: str,
    team_notes: Optional[str] = None
) -> str:
    """Build the full promoted file content."""
    now = datetime.utcnow().isoformat() + "Z"

    # Build frontmatter
    frontmatter = f"""---
slug: {metadata.get('slug', '')}
title: {metadata.get('title', '')}
aliases: {json.dumps(metadata.get('aliases', []))}
tags: {json.dumps(metadata.get('tags', []))}
promoted_at: {now}
last_refreshed: {metadata.get('researched_at', now)}
sources: {json.dumps(metadata.get('sources', []))}
---

"""

    # Use existing team notes or template
    if team_notes is None:
        team_notes = TEAM_NOTES_TEMPLATE

    # Assemble full content
    content = frontmatter
    content += AUTO_START + "\n"
    content += auto_content.strip() + "\n"
    content += AUTO_END + "\n\n"
    content += TEAM_START
    content += team_notes
    content += TEAM_END + "\n"

    return content


def update_readme_index(docs_dir: Path, slug: str, title: str) -> None:
    """Update the README.md index in the docs directory."""
    readme_path = docs_dir / "README.md"
    now = datetime.utcnow().strftime("%Y-%m-%d")

    # Read existing README or create new
    if readme_path.exists():
        readme_content = readme_path.read_text()
    else:
        readme_content = """# Research Index

Curated technical research for this project.

| Topic | Promoted | Last Refreshed | Team Notes |
|-------|----------|----------------|------------|
"""

    # Check if slug already exists in table
    slug_pattern = re.compile(rf"\|\s*\[.*?\]\({re.escape(slug)}\.md\)")

    if slug_pattern.search(readme_content):
        # Update existing entry
        entry_pattern = re.compile(
            rf"\|\s*\[.*?\]\({re.escape(slug)}\.md\)\s*\|[^|]*\|[^|]*\|[^|]*\|"
        )
        new_entry = f"| [{title}]({slug}.md) | {now} | {now} | No |"
        readme_content = entry_pattern.sub(new_entry, readme_content)
    else:
        # Add new entry before the last line (or at end of table)
        table_end = readme_content.rfind("|")
        if table_end > 0:
            # Find end of the line
            line_end = readme_content.find("\n", table_end)
            if line_end == -1:
                line_end = len(readme_content)

            new_entry = f"\n| [{title}]({slug}.md) | {now} | {now} | No |"
            readme_content = (
                readme_content[:line_end] +
                new_entry +
                readme_content[line_end:]
            )

    readme_path.write_text(readme_content)


def promote(
    slug: str,
    output_dir: Optional[str] = None,
    refresh: bool = False
) -> Tuple[bool, str]:
    """
    Promote cached research to project docs.

    Args:
        slug: The cache entry slug
        output_dir: Override output directory
        refresh: If True, preserve existing team notes

    Returns:
        Tuple of (success, message)
    """
    # Get cached entry
    entry = get_cached_entry(slug)
    if not entry:
        return False, f"Cache entry not found: {slug}"

    docs_dir = get_docs_dir(output_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    output_file = docs_dir / f"{slug}.md"

    # Check for existing promoted file
    team_notes = None
    if output_file.exists() and refresh:
        existing_content = output_file.read_text()
        team_notes = extract_team_notes(existing_content)

    # Build promoted content
    content = build_promoted_content(
        metadata=entry["metadata"],
        auto_content=entry["content"],
        team_notes=team_notes
    )

    # Write promoted file
    output_file.write_text(content)

    # Update README index
    update_readme_index(
        docs_dir,
        slug,
        entry["metadata"].get("title", slug)
    )

    action = "Updated" if refresh else "Promoted"
    preserved = " (team notes preserved)" if team_notes else ""

    return True, f"{action} to {output_file}{preserved}"


def cmd_promote(args) -> int:
    """Handle promote command."""
    success, message = promote(
        slug=args.slug,
        output_dir=args.output_dir,
        refresh=args.refresh
    )

    result = {
        "success": success,
        "message": message,
        "slug": args.slug
    }

    if success:
        result["path"] = str(get_docs_dir(args.output_dir) / f"{args.slug}.md")

    print(json.dumps(result, indent=2))
    return 0 if success else 1


def cmd_check_promoted(args) -> int:
    """Check if a slug has been promoted."""
    docs_dir = get_docs_dir(args.output_dir)
    promoted_file = docs_dir / f"{args.slug}.md"

    result = {
        "slug": args.slug,
        "promoted": promoted_file.exists()
    }

    if promoted_file.exists():
        content = promoted_file.read_text()
        result["has_team_notes"] = bool(extract_team_notes(content))
        result["path"] = str(promoted_file)

    print(json.dumps(result, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote research from cache to project docs"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Default is promote
    parser.add_argument("slug", nargs="?", help="Topic slug to promote")
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory (default: docs/research)"
    )
    parser.add_argument(
        "--refresh", "-r",
        action="store_true",
        help="Refresh existing promoted file, preserving team notes"
    )

    # check subcommand
    check_parser = subparsers.add_parser("check", help="Check promotion status")
    check_parser.add_argument("slug", help="Topic slug")
    check_parser.add_argument("--output-dir", "-o", help="Docs directory to check")
    check_parser.set_defaults(func=cmd_check_promoted)

    args = parser.parse_args()

    if args.command == "check":
        return args.func(args)
    elif args.slug:
        return cmd_promote(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
