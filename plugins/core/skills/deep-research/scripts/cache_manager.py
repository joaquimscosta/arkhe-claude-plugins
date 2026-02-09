#!/usr/bin/env python3
"""
Cache management for deep research results.

Usage:
    python cache_manager.py get <slug>
    python cache_manager.py put <slug> --title "Title" --content-file content.md
    python cache_manager.py check <slug>
    python cache_manager.py list
    python cache_manager.py delete <slug>

Environment:
    RESEARCH_CACHE_DIR: Override default cache location (~/.claude/plugins/research)
    RESEARCH_TTL_DAYS: Override default TTL (30 days)
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# Ensure sibling imports work from any working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from research_utils import (
    check_expiration,
    ensure_cache_dir,
    find_by_alias,
    get_cache_dir,
    get_entry,
    get_index,
    get_ttl_days,
    normalize_slug,
    save_index,
)


def put_entry(
    slug: str,
    title: str,
    content: str,
    aliases: Optional[list] = None,
    tags: Optional[list] = None,
    sources: Optional[list] = None,
) -> dict:
    """
    Store a research entry in the cache.

    Returns the metadata dict.
    """
    cache_dir = ensure_cache_dir()
    entry_dir = cache_dir / "entries" / slug
    entry_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    ttl_days = get_ttl_days()
    expires_at = now + timedelta(days=ttl_days)

    metadata = {
        "slug": slug,
        "title": title,
        "aliases": aliases or [],
        "tags": tags or [],
        "sources": sources or [],
        "researched_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    # Write metadata
    metadata_file = entry_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))

    # Write content
    content_file = entry_dir / "content.md"
    content_file.write_text(content)

    # Update index
    index = get_index()
    index[slug] = {
        "slug": slug,
        "title": title,
        "aliases": aliases or [],
        "researched_at": metadata["researched_at"],
        "expires_at": metadata["expires_at"],
    }
    save_index(index)

    return metadata


def delete_entry(slug: str) -> bool:
    """
    Delete a cache entry.

    Returns True if deleted, False if not found.
    """
    cache_dir = get_cache_dir()
    entry_dir = cache_dir / "entries" / slug

    if not entry_dir.exists():
        return False

    for f in entry_dir.iterdir():
        f.unlink()
    entry_dir.rmdir()

    index = get_index()
    if slug in index:
        del index[slug]
        save_index(index)

    return True


def list_entries() -> list:
    """
    List all cache entries with their status.

    Returns list of dicts with slug, title, researched_at, expires_at, expired.
    """
    index = get_index()
    entries = []

    for slug, meta in index.items():
        expiration = check_expiration(meta)
        entries.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "aliases": meta.get("aliases", []),
            "researched_at": meta.get("researched_at", ""),
            "expires_at": expiration["expires_at"],
            "expired": expiration["expired"],
        })

    entries.sort(key=lambda x: x.get("researched_at", ""), reverse=True)
    return entries


# ---------------------------------------------------------------------------
# CLI command handlers
# ---------------------------------------------------------------------------

def cmd_get(args) -> int:
    """Handle 'get' command."""
    slug = find_by_alias(args.slug) or normalize_slug(args.slug)
    entry = get_entry(slug)

    if not entry:
        print(json.dumps({"error": "not_found", "slug": slug}))
        return 1

    expiration = check_expiration(entry["metadata"])

    result = {
        "slug": slug,
        "metadata": entry["metadata"],
        "content": entry["content"],
        "cache_status": "expired" if expiration["expired"] else "valid",
    }

    print(json.dumps(result, indent=2))
    return 0


def cmd_put(args) -> int:
    """Handle 'put' command."""
    slug = normalize_slug(args.slug)

    if args.content_file:
        content_path = Path(args.content_file)
        try:
            content = content_path.read_text()
        except FileNotFoundError:
            print(f"Error: File not found: {args.content_file}", file=sys.stderr)
            return 1
        except PermissionError:
            print(f"Error: Permission denied: {args.content_file}", file=sys.stderr)
            return 1
    else:
        content = sys.stdin.read()

    aliases = args.aliases.split(",") if args.aliases else []
    tags = args.tags.split(",") if args.tags else []

    metadata = put_entry(
        slug=slug,
        title=args.title or slug,
        content=content,
        aliases=[a.strip() for a in aliases if a.strip()],
        tags=[t.strip() for t in tags if t.strip()],
    )

    print(json.dumps({
        "status": "cached",
        "slug": slug,
        "path": str(get_cache_dir() / "entries" / slug),
        "expires_at": metadata["expires_at"],
    }, indent=2))

    return 0


def cmd_check(args) -> int:
    """Handle 'check' command."""
    slug = find_by_alias(args.slug) or normalize_slug(args.slug)
    entry = get_entry(slug)

    if not entry:
        print(json.dumps({"exists": False, "slug": slug}))
        return 0

    expiration = check_expiration(entry["metadata"])

    print(json.dumps({
        "exists": True,
        "slug": slug,
        "title": entry["metadata"].get("title", slug),
        "expired": expiration["expired"],
        "expires_at": expiration["expires_at"],
        "researched_at": entry["metadata"].get("researched_at", ""),
    }, indent=2))

    return 0


def cmd_list(args) -> int:
    """Handle 'list' command."""
    entries = list_entries()

    if args.format == "json":
        print(json.dumps(entries, indent=2))
    else:
        print(f"{'Slug':<30} {'Title':<30} {'Status':<10} {'Expires':<12}")
        print("-" * 85)
        for e in entries:
            status = "Expired" if e["expired"] else "Valid"
            expires = e["expires_at"][:10] if e["expires_at"] else "N/A"
            title = e["title"][:28] + ".." if len(e["title"]) > 30 else e["title"]
            print(f"{e['slug']:<30} {title:<30} {status:<10} {expires:<12}")

    return 0


def cmd_delete(args) -> int:
    """Handle 'delete' command."""
    slug = normalize_slug(args.slug)

    if delete_entry(slug):
        print(json.dumps({"status": "deleted", "slug": slug}))
        return 0
    else:
        print(json.dumps({"error": "not_found", "slug": slug}))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cache management for deep research results"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get
    get_parser = subparsers.add_parser("get", help="Get cached research")
    get_parser.add_argument("slug", help="Topic slug or alias")
    get_parser.set_defaults(func=cmd_get)

    # put
    put_parser = subparsers.add_parser("put", help="Cache research result")
    put_parser.add_argument("slug", help="Topic slug")
    put_parser.add_argument("--title", "-t", help="Human-readable title")
    put_parser.add_argument("--content-file", "-f", help="Path to content file")
    put_parser.add_argument("--aliases", "-a", help="Comma-separated aliases")
    put_parser.add_argument("--tags", help="Comma-separated tags")
    put_parser.set_defaults(func=cmd_put)

    # check
    check_parser = subparsers.add_parser("check", help="Check if topic is cached")
    check_parser.add_argument("slug", help="Topic slug or alias")
    check_parser.set_defaults(func=cmd_check)

    # list
    list_parser = subparsers.add_parser("list", help="List all cached research")
    list_parser.add_argument(
        "--format", "-f",
        choices=["table", "json"],
        default="table",
        help="Output format",
    )
    list_parser.set_defaults(func=cmd_list)

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete cached research")
    delete_parser.add_argument("slug", help="Topic slug")
    delete_parser.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
