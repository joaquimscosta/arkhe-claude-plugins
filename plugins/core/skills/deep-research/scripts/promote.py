#!/usr/bin/env python3
"""
Promote research from Tier 1 cache to Tier 2 project docs.

Usage:
    python promote.py <slug> [--output-dir docs/research]
    python promote.py <slug> --refresh  # Update existing promoted file
    python promote.py check <slug>      # Check if promoted

Environment:
    RESEARCH_CACHE_DIR: Override default cache location (~/.claude/plugins/research)
    RESEARCH_DOCS_DIR: Override default output directory (docs/research)
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

# Ensure sibling imports work from any working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from research_utils import (
    AUTO_END,
    AUTO_START,
    TEAM_END,
    TEAM_NOTES_TEMPLATE,
    TEAM_START,
    extract_team_notes,
    get_docs_dir,
    get_entry,
)


def build_promoted_content(
    metadata: dict,
    auto_content: str,
    team_notes: Optional[str] = None,
) -> str:
    """Build the full promoted file content."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

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

    if team_notes is None:
        team_notes = TEAM_NOTES_TEMPLATE

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
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if readme_path.exists():
        readme_content = readme_path.read_text()
    else:
        readme_content = """# Research Index

Curated technical research for this project.

| Topic | Promoted | Last Refreshed | Team Notes |
|-------|----------|----------------|------------|
"""

    slug_pattern = re.compile(rf"\|\s*\[.*?\]\({re.escape(slug)}\.md\)")

    if slug_pattern.search(readme_content):
        entry_pattern = re.compile(
            rf"\|\s*\[.*?\]\({re.escape(slug)}\.md\)\s*\|[^|]*\|[^|]*\|[^|]*\|"
        )
        new_entry = f"| [{title}]({slug}.md) | {now} | {now} | No |"
        readme_content = entry_pattern.sub(new_entry, readme_content)
    else:
        table_end = readme_content.rfind("|")
        if table_end > 0:
            line_end = readme_content.find("\n", table_end)
            if line_end == -1:
                line_end = len(readme_content)

            new_entry = f"\n| [{title}]({slug}.md) | {now} | {now} | No |"
            readme_content = (
                readme_content[:line_end]
                + new_entry
                + readme_content[line_end:]
            )

    readme_path.write_text(readme_content)


def promote(
    slug: str,
    output_dir: Optional[str] = None,
    refresh: bool = False,
) -> Tuple[bool, str]:
    """
    Promote cached research to project docs.

    Returns:
        Tuple of (success, message)
    """
    entry = get_entry(slug)
    if not entry:
        return False, f"Cache entry not found: {slug}"

    docs_dir = get_docs_dir(output_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    output_file = docs_dir / f"{slug}.md"

    team_notes = None
    if output_file.exists() and refresh:
        existing_content = output_file.read_text()
        team_notes = extract_team_notes(existing_content)

    content = build_promoted_content(
        metadata=entry["metadata"],
        auto_content=entry["content"],
        team_notes=team_notes,
    )

    output_file.write_text(content)

    update_readme_index(
        docs_dir,
        slug,
        entry["metadata"].get("title", slug),
    )

    action = "Updated" if refresh else "Promoted"
    preserved = " (team notes preserved)" if team_notes else ""

    return True, f"{action} to {output_file}{preserved}"


def cmd_promote(args) -> int:
    """Handle promote command."""
    success, message = promote(
        slug=args.slug,
        output_dir=args.output_dir,
        refresh=args.refresh,
    )

    result = {
        "success": success,
        "message": message,
        "slug": args.slug,
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
        "promoted": promoted_file.exists(),
    }

    if promoted_file.exists():
        content = promoted_file.read_text()
        result["has_team_notes"] = bool(extract_team_notes(content))
        result["path"] = str(promoted_file)

    print(json.dumps(result, indent=2))
    return 0


def main() -> int:
    # Handle backwards-compat: `promote.py <slug>` without subcommand
    # Detect if first arg looks like a slug (not a subcommand)
    if len(sys.argv) > 1 and sys.argv[1] not in ("promote", "check", "-h", "--help"):
        promote_parser = argparse.ArgumentParser(description="Promote research from cache to project docs")
        promote_parser.add_argument("slug", help="Topic slug to promote")
        promote_parser.add_argument("--output-dir", "-o", help="Output directory (default: docs/research)")
        promote_parser.add_argument("--refresh", "-r", action="store_true", help="Refresh existing promoted file, preserving team notes")
        args = promote_parser.parse_args()
        return cmd_promote(args)

    parser = argparse.ArgumentParser(
        description="Promote research from cache to project docs"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # promote subcommand
    promote_parser = subparsers.add_parser("promote", help="Promote cached research")
    promote_parser.add_argument("slug", help="Topic slug to promote")
    promote_parser.add_argument("--output-dir", "-o", help="Output directory (default: docs/research)")
    promote_parser.add_argument("--refresh", "-r", action="store_true", help="Refresh existing promoted file, preserving team notes")
    promote_parser.set_defaults(func=cmd_promote)

    # check subcommand
    check_parser = subparsers.add_parser("check", help="Check promotion status")
    check_parser.add_argument("slug", help="Topic slug")
    check_parser.add_argument("--output-dir", "-o", help="Docs directory to check")
    check_parser.set_defaults(func=cmd_check_promoted)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
