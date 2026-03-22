#!/usr/bin/env python3
"""
Shared utilities for quality-stack scanners.

Common helpers used across JVM, Node.js, Python, and cross-cutting scanners.
Uses only standard library (no external dependencies). Python 3.8+.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

# Directories to skip when walking project trees
SKIP_DIRS: Set[str] = {
    "build", ".gradle", "node_modules", ".git", "target", "out", ".idea",
    "__pycache__", ".venv", "venv", "env", ".tox", ".nox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", ".next", ".turbo", "coverage",
}


def make_detection(name: str, status: str = "active", source: str = "build-file") -> dict:
    """Create a tool detection result dict."""
    return {"name": name, "status": status, "source": source}


def read_file_safe(path: Path) -> Optional[str]:
    """Read a file's text content, returning None on any error."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def read_json_safe(path: Path) -> Optional[dict]:
    """Read and parse a JSON file, returning None on any error."""
    content = read_file_safe(path)
    if content is None:
        return None
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return None


def check_files_exist(root: Path, file_paths: Dict[str, str]) -> Dict[str, bool]:
    """Check existence of multiple files relative to root.

    Args:
        root: Project root directory.
        file_paths: Mapping of relative path -> tool name.

    Returns:
        Mapping of relative path -> exists boolean.
    """
    result = {}
    for file_path in file_paths:
        full_path = root / file_path
        if full_path.is_dir():
            # For directories (like .github/workflows), check if they contain files
            has_files = any(full_path.iterdir()) if full_path.exists() else False
            result[file_path] = has_files
        else:
            result[file_path] = full_path.exists()
    return result


def count_files_by_glob(root: Path, pattern: str) -> int:
    """Count files matching a glob pattern, excluding SKIP_DIRS."""
    count = 0
    for p in root.glob(pattern):
        if not (SKIP_DIRS & set(p.parts)):
            count += 1
    return count
