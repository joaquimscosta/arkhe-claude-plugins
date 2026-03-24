#!/usr/bin/env python3
"""
Shared utilities for the refresh skill scripts.

Config loading and git helpers. Python 3.8+, stdlib only.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set


# Module directory patterns to discover
MODULE_DIR_PATTERNS: List[str] = [
    "apps/*", "src/*", "packages/*", "libs/*", "modules/*",
    "internal/*", "cmd/*",
]

# Build files that indicate tech stack
BUILD_FILES: Dict[str, str] = {
    "build.gradle.kts": "Java/Kotlin (Gradle)",
    "build.gradle": "Java/Kotlin (Gradle)",
    "pom.xml": "Java/Kotlin (Maven)",
    "package.json": "JavaScript/TypeScript (Node)",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "pyproject.toml": "Python",
    "setup.py": "Python",
    "Gemfile": "Ruby",
    "mix.exs": "Elixir",
}

# Context files expected in the context directory
CONTEXT_FILES: List[str] = ["project.md", "architecture.md", "documents.md"]

# Staleness thresholds (days)
STALENESS_THRESHOLDS = {
    "fresh": 7,
    "aging": 30,
    "stale": 90,
}


def classify_staleness(days: int) -> str:
    """Classify staleness based on days since update."""
    if days <= STALENESS_THRESHOLDS["fresh"]:
        return "fresh"
    elif days <= STALENESS_THRESHOLDS["aging"]:
        return "aging"
    elif days <= STALENESS_THRESHOLDS["stale"]:
        return "stale"
    return "very_stale"


def read_yaml_section(path: Path, section: str) -> Optional[dict]:
    """Read a YAML file and extract a top-level section.

    Simple line-based parser (no PyYAML dependency).
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return None

    lines = content.splitlines()
    in_section = False
    result: dict = {}
    current_key = None
    current_list: List[str] = []
    base_indent = 2

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        if indent == 0 and stripped.endswith(":"):
            if in_section:
                if current_key and current_list:
                    result[current_key] = current_list
                break
            if stripped == f"{section}:":
                in_section = True
            continue

        if not in_section:
            continue

        if indent < base_indent and not stripped.startswith("-"):
            if current_key and current_list:
                result[current_key] = current_list
            break

        if ":" in stripped and not stripped.startswith("-"):
            if current_key and current_list:
                result[current_key] = current_list
                current_list = []
            key, _, value = stripped.partition(":")
            current_key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                result[current_key] = value
                current_key = None
        elif stripped.startswith("- "):
            item = stripped[2:].strip().strip('"').strip("'")
            current_list.append(item)

    if in_section and current_key and current_list:
        result[current_key] = current_list

    return result if result else None


def load_config(project_root: Path) -> dict:
    """Load roadmap configuration from .arkhe.yaml."""
    config_path = project_root / ".arkhe.yaml"
    section = read_yaml_section(config_path, "roadmap")
    defaults = {
        "context_dir": ".arkhe/roadmap",
        "output_dir": "arkhe/roadmap",
        "status_file": "docs/PROJECT-STATUS.md",
    }
    if section:
        defaults.update(section)
    return defaults


def git_is_available(project_root: str) -> bool:
    """Check if git is available and the directory is a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=5,
            cwd=project_root,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def git_last_modified_date(file_path: str, project_root: str) -> Optional[str]:
    """Get the last commit date for a file (ISO 8601)."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", file_path],
            capture_output=True, text=True, timeout=10,
            cwd=project_root,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def git_latest_commit_date(project_root: str) -> Optional[str]:
    """Get the latest commit date in the repo (ISO 8601)."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI"],
            capture_output=True, text=True, timeout=10,
            cwd=project_root,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def git_commits_since(file_path: str, project_root: str) -> int:
    """Count commits since a file was last modified."""
    last_hash = _git_last_hash(file_path, project_root)
    if not last_hash:
        return 0
    try:
        result = subprocess.run(
            ["git", "log", f"{last_hash}..HEAD", "--oneline", "--no-merges"],
            capture_output=True, text=True, timeout=10,
            cwd=project_root,
        )
        if result.returncode == 0:
            lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
            return len(lines)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return 0


def git_feat_fix_commits_since(file_path: str, project_root: str) -> int:
    """Count feat/fix commits since a file was last modified."""
    last_hash = _git_last_hash(file_path, project_root)
    if not last_hash:
        return 0
    try:
        result = subprocess.run(
            ["git", "log", f"{last_hash}..HEAD", "--oneline", "--no-merges"],
            capture_output=True, text=True, timeout=10,
            cwd=project_root,
        )
        if result.returncode == 0:
            count = 0
            for line in result.stdout.strip().splitlines():
                # Match conventional commits: hash feat: or hash fix:
                parts = line.split(" ", 1)
                if len(parts) > 1:
                    msg = parts[1]
                    if msg.startswith("feat") or msg.startswith("fix"):
                        count += 1
            return count
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return 0


def _git_last_hash(file_path: str, project_root: str) -> Optional[str]:
    """Get the last commit hash for a file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", file_path],
            capture_output=True, text=True, timeout=10,
            cwd=project_root,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def discover_modules(project_root: Path) -> List[str]:
    """Discover top-level module directories."""
    modules: Set[str] = set()
    for pattern in MODULE_DIR_PATTERNS:
        for path in project_root.glob(pattern):
            if path.is_dir():
                modules.add(path.name)
    return sorted(modules)


def detect_tech_stack(project_root: Path) -> List[str]:
    """Detect tech stack from build files."""
    found: List[str] = []
    for filename, stack in BUILD_FILES.items():
        if (project_root / filename).exists():
            found.append(stack)
    return found
