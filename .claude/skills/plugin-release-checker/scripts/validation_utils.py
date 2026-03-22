#!/usr/bin/env python3
"""
Shared utilities for PR validation scripts.

Provides common functions for frontmatter parsing, project root detection,
git date queries, and structured output formatting.
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


def find_project_root() -> Path:
    """Find the arkhe-claude-plugins project root."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".claude-plugin" / "marketplace.json").exists():
            return current
        if (current / "plugins").is_dir() and (current / "CLAUDE.md").exists():
            return current
        current = current.parent

    cwd = Path.cwd()
    if (cwd / "plugins").is_dir():
        return cwd

    print("Error: Cannot find project root.", file=sys.stderr)
    sys.exit(1)


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
            # Convert all values to strings for consistency
            return {k: str(v) if v is not None else "" for k, v in fm.items()}, body
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: simple key-value parsing
    fm = {}
    lines = fm_text.split("\n")
    i = 0
    current_key = None
    current_value_parts = []
    block_scalar = None

    def _store_current():
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


def git_last_modified(filepath: Path) -> Optional[date]:
    """Get the last modification date of a file from git history.

    Returns None if git is not available or the file has no git history.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(filepath)],
            capture_output=True, text=True, timeout=10,
            cwd=filepath.parent,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Parse ISO 8601 date (e.g., 2026-03-19T10:30:00-04:00)
            date_str = result.stdout.strip()[:10]
            return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (subprocess.TimeoutExpired, OSError, ValueError):
        pass
    return None


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
        }
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

    # Text format
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
