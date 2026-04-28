#!/usr/bin/env python3
"""
Shared utilities for research frontmatter validation and path resolution.

Provides common functions for frontmatter parsing, project root detection,
git date queries, structured output formatting, and JD-aware path resolution.
"""

import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Severity levels (ordered by importance)
CRITICAL = "CRITICAL"
ERROR = "ERROR"
WARNING = "WARNING"
SUGGESTION = "SUGGESTION"

SEVERITY_ORDER = {CRITICAL: 0, ERROR: 1, WARNING: 2, SUGGESTION: 3}


# ---------------------------------------------------------------------------
# Project root detection
# ---------------------------------------------------------------------------

def find_project_root(start: Optional[Path] = None) -> Path:
    """Find project root via git, falling back to directory heuristics.

    Walks up from *start* (default: script location) looking for a git root.
    Falls back to looking for common project markers (CLAUDE.md, plugins/).
    """
    if start is None:
        start = Path(__file__).resolve().parent

    # Try git first
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
            cwd=str(start),
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, OSError):
        pass

    # Fallback: walk up looking for markers
    current = start.resolve()
    for _ in range(10):
        if (current / ".claude-plugin" / "marketplace.json").exists():
            return current
        if (current / "plugins").is_dir() and (current / "CLAUDE.md").exists():
            return current
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent

    # Last resort: cwd
    cwd = Path.cwd()
    if (cwd / "CLAUDE.md").exists():
        return cwd

    print("Error: Cannot find project root.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# YAML frontmatter parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> Tuple[Optional[Dict[str, str]], str]:
    """Parse YAML frontmatter from markdown content.

    Returns (frontmatter_dict, body_text). If no frontmatter found,
    returns (None, original_content).
    """
    if not content.startswith("---"):
        return None, content

    match = re.match(r"^---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        return None, content

    fm_text = match.group(1)
    body = content[match.end():]

    # Try PyYAML first for better parsing
    try:
        import yaml
        fm = yaml.safe_load(fm_text)
        if isinstance(fm, dict):
            return {k: str(v) if v is not None else "" for k, v in fm.items()}, body
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: simple key-value parsing
    fm = {}  # type: Dict[str, str]
    lines = fm_text.split("\n")
    i = 0
    current_key = None  # type: Optional[str]
    current_value_parts = []  # type: List[str]
    block_scalar = None  # type: Optional[str]

    def _store_current():
        # type: () -> None
        nonlocal current_key, current_value_parts, block_scalar
        if current_key is not None:
            if block_scalar == ">":
                val = " ".join(p.strip() for p in current_value_parts if p.strip())
            elif block_scalar == "|":
                val = "\n".join(current_value_parts)
            else:
                val = " ".join(p.strip() for p in current_value_parts if p.strip())
            val = val.strip().strip("'\"")
            if val:
                fm[current_key] = val
        current_key = None
        current_value_parts = []
        block_scalar = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if current_key is not None and line and line[0] in (" ", "\t"):
            current_value_parts.append(stripped)
            i += 1
            continue
        if ":" in stripped and line and not line[0].isspace():
            _store_current()
            key, _, value = stripped.partition(":")
            current_key = key.strip()
            value = value.strip()
            if value in (">", "|", ">-", "|-"):
                block_scalar = value[0]
                current_value_parts = []
            else:
                current_value_parts = [value.strip("'\"")]
        i += 1

    _store_current()
    return fm, body


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git_last_modified(filepath: Path) -> Optional[date]:
    """Get the last modification date of a file from git history."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(filepath)],
            capture_output=True, text=True, timeout=10,
            cwd=filepath.parent,
        )
        if result.returncode == 0 and result.stdout.strip():
            date_str = result.stdout.strip()[:10]
            return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (subprocess.TimeoutExpired, OSError, ValueError):
        pass
    return None


# ---------------------------------------------------------------------------
# Date / version helpers
# ---------------------------------------------------------------------------

def parse_date(date_str: str) -> Optional[date]:
    """Parse a YYYY-MM-DD date string."""
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def is_valid_date_format(date_str: str) -> bool:
    """Check if a string is in YYYY-MM-DD format."""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_str.strip()))


def is_valid_semver(version_str: str) -> bool:
    """Check if a string is in basic semver X.Y.Z format."""
    return bool(re.match(r"^\d+\.\d+\.\d+$", version_str.strip()))


# ---------------------------------------------------------------------------
# Issue reporting
# ---------------------------------------------------------------------------

class Issue:
    """A validation issue."""

    def __init__(self, rule_id: str, severity: str, message: str,
                 location: str = "", suggestion: str = ""):
        self.rule_id = rule_id
        self.severity = severity
        self.message = message
        self.location = location
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
        }  # type: Dict[str, Any]
        if self.location:
            d["location"] = self.location
        if self.suggestion:
            d["suggestion"] = self.suggestion
        return d

    def to_text(self) -> str:
        parts = [f"[{self.severity}] {self.rule_id}: {self.message}"]
        if self.location:
            parts[0] += f"  ({self.location})"
        if self.suggestion:
            parts.append(f"  -> {self.suggestion}")
        return "\n".join(parts)


def filter_issues(issues: List[Issue], min_severity: str) -> List[Issue]:
    """Filter issues by minimum severity level."""
    min_level = SEVERITY_ORDER.get(min_severity.upper(), 2)
    return [i for i in issues if SEVERITY_ORDER.get(i.severity, 3) <= min_level]


def format_output(title: str, issues: List[Issue], fmt: str = "text") -> str:
    """Format issues for output."""
    if fmt == "json":
        return json.dumps({
            "title": title,
            "total_issues": len(issues),
            "issues": [i.to_dict() for i in issues],
            "summary": {
                sev: len([i for i in issues if i.severity == sev])
                for sev in [CRITICAL, ERROR, WARNING, SUGGESTION]
                if any(i.severity == sev for i in issues)
            },
        }, indent=2)

    lines = [f"{'=' * 60}", f"  {title}", f"{'=' * 60}", ""]
    if not issues:
        lines.append("  All checks passed!")
    else:
        for issue in issues:
            lines.append(issue.to_text())
        lines.append("")
        summary_parts = []
        for sev in [CRITICAL, ERROR, WARNING, SUGGESTION]:
            count = len([i for i in issues if i.severity == sev])
            if count > 0:
                summary_parts.append(f"{count} {sev.lower()}")
        lines.append(f"Summary: {', '.join(summary_parts)}")
    lines.append("")
    return "\n".join(lines)


def has_errors(issues: List[Issue]) -> bool:
    """Check if any issues are CRITICAL or ERROR severity."""
    return any(i.severity in (CRITICAL, ERROR) for i in issues)


def standard_argparse(description: str):
    """Create a standard argparse parser with --format and --min-severity."""
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--min-severity", choices=["critical", "error", "warning", "suggestion"],
                        default="warning", help="Minimum severity to report (default: warning)")
    return parser


# ---------------------------------------------------------------------------
# JD-aware research path resolution
# ---------------------------------------------------------------------------

def _load_jd_config(project_root: Path) -> Optional[Dict[str, Any]]:
    """Load .jd-config.json from project root if it exists."""
    config_path = project_root / ".jd-config.json"
    if not config_path.exists():
        return None
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return None


def resolve_research_path(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Resolve the research documents directory, JD-aware.

    Algorithm:
      1. Find project root (git root)
      2. Try loading .jd-config.json
      3. Search areas dict for value containing "research"
      4. Construct {root}/{prefix}-{name}/ path
      5. Fall back to docs/research/ if no JD config

    Returns dict with keys:
      - path: str (relative path from project root, e.g. "docs/30-research")
      - jd_aware: bool
      - prefix: Optional[str] (e.g. "30")
      - area_name: Optional[str] (e.g. "research")
      - root: str (docs root, e.g. "docs")
    """
    if project_root is None:
        project_root = find_project_root()

    config = _load_jd_config(project_root)
    if config is not None:
        docs_root = config.get("root", "docs")
        areas = config.get("areas", {})

        for prefix, name in areas.items():
            if "research" in name.lower():
                path = f"{docs_root}/{prefix}-{name}"
                return {
                    "path": path,
                    "jd_aware": True,
                    "prefix": str(prefix),
                    "area_name": name,
                    "root": docs_root,
                }

    return {
        "path": "docs/research",
        "jd_aware": False,
        "prefix": None,
        "area_name": None,
        "root": "docs",
    }
