#!/usr/bin/env python3
"""
Shared utilities for deep research cache management.

Provides common functions used by cache_manager.py, index_generator.py,
and promote.py to avoid duplication.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuration defaults
DEFAULT_CACHE_DIR = Path.home() / ".claude" / "plugins" / "research"
DEFAULT_DOCS_DIR = Path("docs/research")
DEFAULT_TTL_DAYS = 30

# Section markers for promoted files
AUTO_START = "<!-- AUTO-GENERATED: Start -->"
AUTO_END = "<!-- AUTO-GENERATED: End -->"
TEAM_START = "<!-- TEAM-NOTES: Start -->"
TEAM_END = "<!-- TEAM-NOTES: End -->"

TEAM_NOTES_TEMPLATE = """
## Team Context

_Add project-specific notes, implementation references, and team knowledge here._

"""


# ---------------------------------------------------------------------------
# Directory / config helpers
# ---------------------------------------------------------------------------

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


def get_ttl_days() -> int:
    """Get TTL days from environment or default."""
    env_ttl = os.environ.get("RESEARCH_TTL_DAYS")
    if env_ttl:
        try:
            return int(env_ttl)
        except ValueError:
            pass
    return DEFAULT_TTL_DAYS


# ---------------------------------------------------------------------------
# Slug helpers
# ---------------------------------------------------------------------------

def normalize_slug(topic: str) -> str:
    """
    Convert a topic to a normalized slug.

    Examples:
        "Domain-Driven Design" -> "domain-driven-design"
        "React Hooks" -> "react-hooks"
        "C# async/await" -> "csharp-async-await"
    """
    slug = topic.lower()
    slug = slug.replace("c#", "csharp").replace("c++", "cpp")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug


# ---------------------------------------------------------------------------
# Cache directory management
# ---------------------------------------------------------------------------

def ensure_cache_dir() -> Path:
    """Ensure cache directory structure exists."""
    cache_dir = get_cache_dir()
    entries_dir = cache_dir / "entries"
    entries_dir.mkdir(parents=True, exist_ok=True)

    index_file = cache_dir / "index.json"
    if not index_file.exists():
        index_file.write_text("{}")

    return cache_dir


# ---------------------------------------------------------------------------
# Index operations
# ---------------------------------------------------------------------------

def get_index() -> dict:
    """
    Read the cache index.

    Handles two formats:
    - Legacy: {"version": "...", "entries": [{slug, title, ...}, ...]}
    - Current: {"slug-key": {slug, title, ...}, ...}

    Always returns the current dict-keyed-by-slug format.
    """
    cache_dir = get_cache_dir()
    index_file = cache_dir / "index.json"

    if not index_file.exists():
        return {}

    try:
        data = json.loads(index_file.read_text())
    except json.JSONDecodeError:
        return {}

    # Handle legacy array format
    if isinstance(data, dict) and "entries" in data and isinstance(data["entries"], list):
        converted = {}
        for entry in data["entries"]:
            slug = entry.get("slug", "")
            if slug:
                converted[slug] = entry
        return converted

    return data


def save_index(index: dict) -> None:
    """Write the cache index."""
    cache_dir = ensure_cache_dir()
    index_file = cache_dir / "index.json"
    index_file.write_text(json.dumps(index, indent=2, sort_keys=True))


# ---------------------------------------------------------------------------
# Alias lookup
# ---------------------------------------------------------------------------

def find_by_alias(topic: str) -> Optional[str]:
    """
    Find a slug by alias lookup.

    Returns the canonical slug if found, None otherwise.
    """
    normalized = normalize_slug(topic)
    index = get_index()

    if normalized in index:
        return normalized

    for slug, metadata in index.items():
        aliases = metadata.get("aliases", [])
        normalized_aliases = [normalize_slug(a) for a in aliases]
        if normalized in normalized_aliases:
            return slug

    return None


# ---------------------------------------------------------------------------
# Cache entry read
# ---------------------------------------------------------------------------

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
        return {"metadata": metadata, "content": content}
    except (json.JSONDecodeError, IOError):
        return None


# ---------------------------------------------------------------------------
# Expiration / date helpers
# ---------------------------------------------------------------------------

def check_expiration(metadata_or_str) -> dict:
    """
    Check if a cache entry is expired.

    Accepts either a metadata dict (with 'expires_at' key) or a raw
    ISO timestamp string.

    Returns dict with 'expired' (bool) and 'expires_at' (str).
    """
    if isinstance(metadata_or_str, dict):
        expires_at_str = metadata_or_str.get("expires_at", "")
    else:
        expires_at_str = metadata_or_str or ""

    if not expires_at_str:
        return {"expired": True, "expires_at": None}

    try:
        expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        now = datetime.now(expires_at.tzinfo) if expires_at.tzinfo else datetime.now()
        return {
            "expired": now > expires_at,
            "expires_at": expires_at_str,
        }
    except ValueError:
        return {"expired": True, "expires_at": expires_at_str}


def format_date(iso_string: str) -> str:
    """Format ISO date string to YYYY-MM-DD."""
    if not iso_string:
        return "N/A"
    try:
        return iso_string[:10]
    except (ValueError, IndexError):
        return "N/A"


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

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

            if value.startswith("["):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass

            result[key] = value

    return result


def extract_team_notes(content: str) -> Optional[str]:
    """Extract existing team notes from promoted file."""
    pattern = re.compile(
        rf"{re.escape(TEAM_START)}(.*?){re.escape(TEAM_END)}",
        re.DOTALL,
    )
    match = pattern.search(content)
    if match:
        return match.group(1)
    return None


def has_team_notes(content: str) -> bool:
    """Check if promoted file has non-empty team notes."""
    notes = extract_team_notes(content)
    if not notes:
        return False
    notes = notes.strip()
    if "_Add project-specific notes" in notes:
        return False
    return bool(notes)
