#!/usr/bin/env python3
"""
Generate README.md index for research directories.

Usage:
    python index_generator.py --cache          # Generate for Tier 1 cache
    python index_generator.py --docs [DIR]     # Generate for Tier 2 docs
    python index_generator.py --both           # Generate both

Environment:
    RESEARCH_CACHE_DIR: Override default cache location (~/.claude/plugins/research)
    RESEARCH_DOCS_DIR: Override default docs directory (docs/research)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuration
DEFAULT_CACHE_DIR = Path.home() / ".claude" / "plugins" / "research"
DEFAULT_DOCS_DIR = Path("docs/research")


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


def check_expiration(expires_at: str) -> bool:
    """Check if a timestamp is expired."""
    if not expires_at:
        return True

    try:
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        now = datetime.now(expires.tzinfo) if expires.tzinfo else datetime.now()
        return now > expires
    except ValueError:
        return True


def format_date(iso_string: str) -> str:
    """Format ISO date string to YYYY-MM-DD."""
    if not iso_string:
        return "N/A"
    try:
        return iso_string[:10]
    except (ValueError, IndexError):
        return "N/A"


def generate_cache_readme() -> str:
    """Generate README.md content for Tier 1 cache."""
    cache_dir = get_cache_dir()
    index_file = cache_dir / "index.json"

    if not index_file.exists():
        return "# Research Cache\n\nNo cached research yet.\n"

    try:
        index = json.loads(index_file.read_text())
    except json.JSONDecodeError:
        return "# Research Cache\n\nError reading cache index.\n"

    # Sort by researched_at descending
    entries = sorted(
        index.values(),
        key=lambda x: x.get("researched_at", ""),
        reverse=True
    )

    # Build README
    lines = [
        "# Research Cache",
        "",
        "User-level cache for cross-project research reuse.",
        "",
        f"**Location:** `{cache_dir}`",
        f"**Entries:** {len(entries)}",
        "",
        "## Index",
        "",
        "| Slug | Title | Researched | Expires | Status |",
        "|------|-------|------------|---------|--------|"
    ]

    valid_count = 0
    expired_count = 0

    for entry in entries:
        slug = entry.get("slug", "")
        title = entry.get("title", slug)
        researched = format_date(entry.get("researched_at", ""))
        expires = format_date(entry.get("expires_at", ""))
        expired = check_expiration(entry.get("expires_at", ""))

        status = "Expired" if expired else "Valid"
        status_icon = "⚠️" if expired else "✅"

        if expired:
            expired_count += 1
        else:
            valid_count += 1

        # Truncate long titles
        if len(title) > 35:
            title = title[:32] + "..."

        lines.append(f"| {slug} | {title} | {researched} | {expires} | {status_icon} {status} |")

    lines.extend([
        "",
        "## Summary",
        "",
        f"- **Valid:** {valid_count}",
        f"- **Expired:** {expired_count}",
        "",
        "## Commands",
        "",
        "```bash",
        "# Research a topic",
        "/research <topic>",
        "",
        "# Promote to project docs",
        "/research promote <slug>",
        "",
        "# Refresh expired research",
        "/research refresh <slug>",
        "```",
        ""
    ])

    return "\n".join(lines)


def has_team_notes(content: str) -> bool:
    """Check if promoted file has non-empty team notes."""
    pattern = re.compile(
        r"<!-- TEAM-NOTES: Start -->(.*?)<!-- TEAM-NOTES: End -->",
        re.DOTALL
    )
    match = pattern.search(content)
    if not match:
        return False

    notes = match.group(1).strip()
    # Check if it's more than just the template
    if "_Add project-specific notes" in notes:
        return False
    return bool(notes)


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown."""
    if not content.startswith("---"):
        return {}

    end = content.find("---", 3)
    if end == -1:
        return {}

    frontmatter = content[3:end].strip()
    result = {}

    for line in frontmatter.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            # Handle JSON arrays
            if value.startswith("["):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass

            result[key] = value

    return result


def generate_docs_readme(docs_dir: Optional[str] = None) -> str:
    """Generate README.md content for Tier 2 docs."""
    docs_path = get_docs_dir(docs_dir)

    if not docs_path.exists():
        return "# Research Index\n\nNo promoted research yet.\n"

    # Find all markdown files except README
    entries = []
    for md_file in docs_path.glob("*.md"):
        if md_file.name.lower() == "readme.md":
            continue

        content = md_file.read_text()
        frontmatter = extract_frontmatter(content)

        slug = md_file.stem
        title = frontmatter.get("title", slug)
        promoted = format_date(frontmatter.get("promoted_at", ""))
        refreshed = format_date(frontmatter.get("last_refreshed", ""))
        has_notes = has_team_notes(content)

        entries.append({
            "slug": slug,
            "title": title,
            "promoted_at": promoted,
            "last_refreshed": refreshed,
            "has_team_notes": has_notes
        })

    # Sort by promoted_at descending
    entries.sort(key=lambda x: x.get("promoted_at", ""), reverse=True)

    # Build README
    lines = [
        "# Research Index",
        "",
        "Curated technical research for this project.",
        "",
        "## Topics",
        "",
        "| Topic | Promoted | Last Refreshed | Team Notes |",
        "|-------|----------|----------------|------------|"
    ]

    with_notes = 0
    without_notes = 0

    for entry in entries:
        slug = entry["slug"]
        title = entry["title"]
        promoted = entry["promoted_at"]
        refreshed = entry["last_refreshed"]
        has_notes = entry["has_team_notes"]

        notes_icon = "✅ Yes" if has_notes else "—"

        if has_notes:
            with_notes += 1
        else:
            without_notes += 1

        # Truncate long titles
        if len(title) > 35:
            title = title[:32] + "..."

        lines.append(f"| [{title}]({slug}.md) | {promoted} | {refreshed} | {notes_icon} |")

    lines.extend([
        "",
        "## Summary",
        "",
        f"- **Total:** {len(entries)}",
        f"- **With team notes:** {with_notes}",
        f"- **Without team notes:** {without_notes}",
        "",
        "## Contributing",
        "",
        "1. Research new topics: `/research <topic>`",
        "2. Promote valuable research: `/research promote <slug>`",
        "3. Add team context in the TEAM-NOTES section",
        "4. Refresh when needed: `/research refresh <slug>`",
        ""
    ])

    return "\n".join(lines)


def cmd_generate(args) -> int:
    """Handle generate command."""
    results = []

    if args.cache or args.both:
        cache_dir = get_cache_dir()
        readme_content = generate_cache_readme()

        if not args.dry_run:
            cache_dir.mkdir(parents=True, exist_ok=True)
            readme_path = cache_dir / "README.md"
            readme_path.write_text(readme_content)
            results.append({"tier": "cache", "path": str(readme_path), "status": "updated"})
        else:
            print("=== CACHE README ===")
            print(readme_content)
            results.append({"tier": "cache", "status": "dry_run"})

    if args.docs or args.both:
        docs_dir = get_docs_dir(args.docs_dir)
        readme_content = generate_docs_readme(args.docs_dir)

        if not args.dry_run:
            docs_dir.mkdir(parents=True, exist_ok=True)
            readme_path = docs_dir / "README.md"
            readme_path.write_text(readme_content)
            results.append({"tier": "docs", "path": str(readme_path), "status": "updated"})
        else:
            print("=== DOCS README ===")
            print(readme_content)
            results.append({"tier": "docs", "status": "dry_run"})

    if not args.dry_run:
        print(json.dumps({"results": results}, indent=2))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate README.md index for research directories"
    )

    parser.add_argument(
        "--cache", "-c",
        action="store_true",
        help="Generate README for Tier 1 cache"
    )
    parser.add_argument(
        "--docs", "-d",
        action="store_true",
        help="Generate README for Tier 2 docs"
    )
    parser.add_argument(
        "--both", "-b",
        action="store_true",
        help="Generate README for both tiers"
    )
    parser.add_argument(
        "--docs-dir",
        help="Override docs directory path"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output without writing files"
    )

    args = parser.parse_args()

    # Default to both if nothing specified
    if not (args.cache or args.docs or args.both):
        args.both = True

    return cmd_generate(args)


if __name__ == "__main__":
    sys.exit(main())
