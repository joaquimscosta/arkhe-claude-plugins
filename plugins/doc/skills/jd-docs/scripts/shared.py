#!/usr/bin/env python3
"""
Shared utilities for jd-docs scripts.

Common helpers for config loading, git root detection, file naming,
and area management. Uses only standard library. Python 3.11+.
"""

import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

# Pattern for valid J.D area directory names: NN-kebab-case
AREA_NAME_PATTERN = re.compile(r"^[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")

# Default area scheme
DEFAULT_AREAS: dict[str, str] = {
    "00": "getting-started",
    "10": "product",
    "20": "architecture",
    "30": "research",
    "90": "archive",
}

# Purpose descriptions for each default area
AREA_DESCRIPTIONS: dict[str, str] = {
    "00": "Onboarding, setup, quick start, MVP, and phase planning",
    "10": "Product specs, features, roadmap, design, and branding",
    "20": "Technical decisions, system design, and integration",
    "30": "Research notes, spikes, investigations, and reference material",
    "90": "Historical and deprecated documentation",
    "41": "Learning-oriented, step-by-step lessons (Diataxis: Tutorial)",
    "42": "Task-oriented, practical problem-solving guides (Diataxis: How-to)",
    "43": "Information-oriented, technical descriptions (Diataxis: Reference)",
    "44": "Understanding-oriented, conceptual discussions (Diataxis: Explanation)",
}

# Short descriptions for index tables
AREA_DESCRIPTIONS_SHORT: dict[str, str] = {
    "00": "Onboarding, setup, quick start, MVP",
    "10": "Specs, features, roadmap, design",
    "20": "Tech decisions, system design",
    "30": "Research, spikes, investigations",
    "90": "Historical/deprecated docs",
    "41": "Tutorials (Diataxis)",
    "42": "How-to guides (Diataxis)",
    "43": "Reference docs (Diataxis)",
    "44": "Explanation docs (Diataxis)",
}

# Diataxis quadrant areas (range 41-44, within the 40-49 custom zone)
DIATAXIS_AREAS: dict[str, str] = {
    "41": "tutorials",
    "42": "how-to",
    "43": "reference",
    "44": "explanation",
}

# Mapping from Diataxis quadrant name to JD prefix
DIATAXIS_QUADRANT_TO_PREFIX: dict[str, str] = {
    "tutorial": "41",
    "how-to": "42",
    "reference": "43",
    "explanation": "44",
}

DEFAULT_CONFIG: dict = {
    "version": 1,
    "root": "docs",
    "areas": DEFAULT_AREAS,
    "products": [],
    "ignore": ["adr", "*.pdf"],
    "readme_format": "table",
}

# Files that are expected at the docs root (not orphans)
ROOT_ALLOWED_FILES: set[str] = {
    "readme.md",
    "glossary.md",
    ".jd-config.json",
    ".ds_store",
}


def find_git_root(start: Path) -> Path | None:
    """Walk up from start to find the git repository root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=start,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except FileNotFoundError:
        pass
    return None


def load_config(base_path: Path) -> dict:
    """Find .jd-config.json walking up to git root, or return defaults."""
    current = base_path.resolve()
    git_root = find_git_root(current)
    stop_at = git_root or current

    while True:
        config_path = current / ".jd-config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            # Merge with defaults for missing keys
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config

        if current == stop_at or current == current.parent:
            break
        current = current.parent

    return dict(DEFAULT_CONFIG)


def resolve_config(args_config: str | None, base_path: Path) -> dict:
    """Load config from an explicit path or auto-detect."""
    if args_config:
        config_path = Path(args_config)
        if not config_path.is_absolute():
            config_path = base_path / config_path
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
        else:
            print(f"Warning: Config not found: {config_path}, using defaults",
                  file=sys.stderr)
            return dict(DEFAULT_CONFIG)
    return load_config(base_path)


def is_ignored(name: str, ignore_patterns: list[str]) -> bool:
    """Check if a directory or file name matches any ignore pattern."""
    return any(
        fnmatch.fnmatch(name, p) or fnmatch.fnmatch(name.lower(), p.lower())
        for p in ignore_patterns
    )


def find_area_by_prefix(docs_dir: Path, prefix: str) -> Path | None:
    """Find an area directory by its two-digit prefix."""
    for item in docs_dir.iterdir():
        if item.is_dir() and item.name.startswith(f"{prefix}-"):
            return item
    return None


def normalize_filename(name: str) -> str:
    """Normalize a filename to kebab-case, preserving the extension.

    Examples:
        "My Design Doc.md"   -> "my-design-doc.md"
        "Tech_Stack_v2.md"   -> "tech-stack-v2.md"
        "SETUP Guide!.md"    -> "setup-guide.md"
        "a--b---c.md"        -> "a-b-c.md"
        ".gitkeep"           -> ".gitkeep" (hidden files unchanged)
    """
    # Skip hidden files
    if name.startswith("."):
        return name

    # Split name and extension
    path = Path(name)
    stem = path.stem
    suffix = path.suffix.lower()

    # Lowercase
    stem = stem.lower()
    # Replace underscores and spaces with hyphens
    stem = re.sub(r"[_ ]+", "-", stem)
    # Strip characters that aren't alphanumeric, hyphen, or dot
    stem = re.sub(r"[^a-z0-9\-.]", "", stem)
    # Collapse multiple hyphens
    stem = re.sub(r"-{2,}", "-", stem)
    # Strip leading/trailing hyphens
    stem = stem.strip("-")

    if not stem:
        stem = "untitled"

    return f"{stem}{suffix}"
