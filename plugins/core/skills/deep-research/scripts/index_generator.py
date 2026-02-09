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
import sys
from pathlib import Path
from typing import Optional

# Ensure sibling imports work from any working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from research_utils import (
    check_expiration,
    extract_frontmatter,
    format_date,
    get_cache_dir,
    get_docs_dir,
    get_index,
    has_team_notes,
)


def generate_cache_readme() -> str:
    """Generate README.md content for Tier 1 cache."""
    cache_dir = get_cache_dir()
    index = get_index()

    if not index:
        return "# Research Cache\n\nNo cached research yet.\n"

    entries = sorted(
        index.values(),
        key=lambda x: x.get("researched_at", ""),
        reverse=True,
    )

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
        "|------|-------|------------|---------|--------|",
    ]

    valid_count = 0
    expired_count = 0

    for entry in entries:
        slug = entry.get("slug", "")
        title = entry.get("title", slug)
        researched = format_date(entry.get("researched_at", ""))
        expires = format_date(entry.get("expires_at", ""))
        expired = check_expiration(entry.get("expires_at", ""))["expired"]

        status = "Expired" if expired else "Valid"
        status_icon = "⚠️" if expired else "✅"

        if expired:
            expired_count += 1
        else:
            valid_count += 1

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
        "",
    ])

    return "\n".join(lines)


def generate_docs_readme(docs_dir: Optional[str] = None) -> str:
    """Generate README.md content for Tier 2 docs."""
    docs_path = get_docs_dir(docs_dir)

    if not docs_path.exists():
        return "# Research Index\n\nNo promoted research yet.\n"

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
        notes = has_team_notes(content)

        entries.append({
            "slug": slug,
            "title": title,
            "promoted_at": promoted,
            "last_refreshed": refreshed,
            "has_team_notes": notes,
        })

    entries.sort(key=lambda x: x.get("promoted_at", ""), reverse=True)

    lines = [
        "# Research Index",
        "",
        "Curated technical research for this project.",
        "",
        "## Topics",
        "",
        "| Topic | Promoted | Last Refreshed | Team Notes |",
        "|-------|----------|----------------|------------|",
    ]

    with_notes = 0
    without_notes = 0

    for entry in entries:
        slug = entry["slug"]
        title = entry["title"]
        promoted = entry["promoted_at"]
        refreshed = entry["last_refreshed"]
        notes = entry["has_team_notes"]

        notes_icon = "✅ Yes" if notes else "—"

        if notes:
            with_notes += 1
        else:
            without_notes += 1

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
        "",
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

    parser.add_argument("--cache", "-c", action="store_true", help="Generate README for Tier 1 cache")
    parser.add_argument("--docs", "-d", action="store_true", help="Generate README for Tier 2 docs")
    parser.add_argument("--both", "-b", action="store_true", help="Generate README for both tiers")
    parser.add_argument("--docs-dir", help="Override docs directory path")
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing files")

    args = parser.parse_args()

    if not (args.cache or args.docs or args.both):
        args.both = True

    return cmd_generate(args)


if __name__ == "__main__":
    sys.exit(main())
