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
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Configuration
DEFAULT_CACHE_DIR = Path.home() / ".claude" / "plugins" / "research"
DEFAULT_TTL_DAYS = 30


def get_cache_dir() -> Path:
    """Get cache directory from environment or default."""
    env_dir = os.environ.get("RESEARCH_CACHE_DIR")
    if env_dir:
        return Path(env_dir)
    return DEFAULT_CACHE_DIR


def get_ttl_days() -> int:
    """Get TTL days from environment or default."""
    env_ttl = os.environ.get("RESEARCH_TTL_DAYS")
    if env_ttl:
        try:
            return int(env_ttl)
        except ValueError:
            pass
    return DEFAULT_TTL_DAYS


def normalize_slug(topic: str) -> str:
    """
    Convert a topic to a normalized slug.

    Examples:
        "Domain-Driven Design" -> "domain-driven-design"
        "React Hooks" -> "react-hooks"
        "C# async/await" -> "csharp-async-await"
    """
    # Lowercase
    slug = topic.lower()

    # Replace C# with csharp, C++ with cpp, etc.
    slug = slug.replace("c#", "csharp").replace("c++", "cpp")

    # Replace special characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)

    return slug


def ensure_cache_dir() -> Path:
    """Ensure cache directory structure exists."""
    cache_dir = get_cache_dir()
    entries_dir = cache_dir / "entries"
    entries_dir.mkdir(parents=True, exist_ok=True)

    # Ensure index.json exists
    index_file = cache_dir / "index.json"
    if not index_file.exists():
        index_file.write_text("{}")

    return cache_dir


def get_index() -> dict:
    """Read the cache index."""
    cache_dir = get_cache_dir()
    index_file = cache_dir / "index.json"

    if not index_file.exists():
        return {}

    try:
        return json.loads(index_file.read_text())
    except json.JSONDecodeError:
        return {}


def save_index(index: dict) -> None:
    """Write the cache index."""
    cache_dir = ensure_cache_dir()
    index_file = cache_dir / "index.json"
    index_file.write_text(json.dumps(index, indent=2, sort_keys=True))


def find_by_alias(topic: str) -> Optional[str]:
    """
    Find a slug by alias lookup.

    Returns the canonical slug if found, None otherwise.
    """
    normalized = normalize_slug(topic)
    index = get_index()

    # Direct match
    if normalized in index:
        return normalized

    # Search aliases
    for slug, metadata in index.items():
        aliases = metadata.get("aliases", [])
        normalized_aliases = [normalize_slug(a) for a in aliases]
        if normalized in normalized_aliases:
            return slug

    return None


def get_entry(slug: str) -> Optional[dict]:
    """
    Get a cache entry by slug.

    Returns dict with 'metadata' and 'content' keys, or None if not found.
    """
    cache_dir = get_cache_dir()
    entry_dir = cache_dir / "entries" / slug

    metadata_file = entry_dir / "metadata.json"
    content_file = entry_dir / "content.md"

    if not metadata_file.exists() or not content_file.exists():
        return None

    try:
        metadata = json.loads(metadata_file.read_text())
        content = content_file.read_text()

        return {
            "metadata": metadata,
            "content": content
        }
    except (json.JSONDecodeError, IOError):
        return None


def check_expiration(metadata: dict) -> dict:
    """
    Check if a cache entry is expired.

    Returns dict with 'expired' (bool) and 'expires_at' (str).
    """
    expires_at_str = metadata.get("expires_at", "")

    if not expires_at_str:
        return {"expired": True, "expires_at": None}

    try:
        expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        now = datetime.now(expires_at.tzinfo) if expires_at.tzinfo else datetime.now()

        return {
            "expired": now > expires_at,
            "expires_at": expires_at_str
        }
    except ValueError:
        return {"expired": True, "expires_at": expires_at_str}


def put_entry(
    slug: str,
    title: str,
    content: str,
    aliases: Optional[list] = None,
    tags: Optional[list] = None,
    sources: Optional[list] = None
) -> dict:
    """
    Store a research entry in the cache.

    Returns the metadata dict.
    """
    cache_dir = ensure_cache_dir()
    entry_dir = cache_dir / "entries" / slug
    entry_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.utcnow()
    ttl_days = get_ttl_days()
    expires_at = now + timedelta(days=ttl_days)

    metadata = {
        "slug": slug,
        "title": title,
        "aliases": aliases or [],
        "tags": tags or [],
        "sources": sources or [],
        "researched_at": now.isoformat() + "Z",
        "expires_at": expires_at.isoformat() + "Z"
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
        "expires_at": metadata["expires_at"]
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

    # Remove files
    for f in entry_dir.iterdir():
        f.unlink()
    entry_dir.rmdir()

    # Update index
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
            "expired": expiration["expired"]
        })

    # Sort by researched_at descending
    entries.sort(key=lambda x: x.get("researched_at", ""), reverse=True)

    return entries


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
        "cache_status": "expired" if expiration["expired"] else "valid"
    }

    print(json.dumps(result, indent=2))
    return 0


def cmd_put(args) -> int:
    """Handle 'put' command."""
    slug = normalize_slug(args.slug)

    # Read content from file or stdin
    if args.content_file:
        content = Path(args.content_file).read_text()
    else:
        content = sys.stdin.read()

    # Parse aliases and tags
    aliases = args.aliases.split(",") if args.aliases else []
    tags = args.tags.split(",") if args.tags else []

    metadata = put_entry(
        slug=slug,
        title=args.title or slug,
        content=content,
        aliases=[a.strip() for a in aliases if a.strip()],
        tags=[t.strip() for t in tags if t.strip()]
    )

    print(json.dumps({
        "status": "cached",
        "slug": slug,
        "path": str(get_cache_dir() / "entries" / slug),
        "expires_at": metadata["expires_at"]
    }, indent=2))

    return 0


def cmd_check(args) -> int:
    """Handle 'check' command."""
    slug = find_by_alias(args.slug) or normalize_slug(args.slug)
    entry = get_entry(slug)

    if not entry:
        print(json.dumps({
            "exists": False,
            "slug": slug
        }))
        return 0

    expiration = check_expiration(entry["metadata"])

    print(json.dumps({
        "exists": True,
        "slug": slug,
        "title": entry["metadata"].get("title", slug),
        "expired": expiration["expired"],
        "expires_at": expiration["expires_at"],
        "researched_at": entry["metadata"].get("researched_at", "")
    }, indent=2))

    return 0


def cmd_list(args) -> int:
    """Handle 'list' command."""
    entries = list_entries()

    if args.format == "json":
        print(json.dumps(entries, indent=2))
    else:
        # Table format
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
        help="Output format"
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
