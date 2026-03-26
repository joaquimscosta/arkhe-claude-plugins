#!/usr/bin/env python3
"""
Frontmatter Onboarding Tool

Discovers markdown files that would benefit from tracking frontmatter
and suggests (or applies) minimal frontmatter using git history.

Uses only standard library (no external dependencies). Python 3.8+.

Usage:
    python3 frontmatter_onboard.py <project_root>           # Suggest mode
    python3 frontmatter_onboard.py --apply <project_root>   # Apply frontmatter

Output:
    JSON with candidates and suggested frontmatter.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import extract_frontmatter, read_file_safe


# ---------------------------------------------------------------------------
# Whitelist: Only these locations contain docs we own and maintain
# ---------------------------------------------------------------------------

CANDIDATE_PATTERNS: List[str] = [
    # Root-level project docs
    "README.md",
    "CLAUDE.md",
    "INSTALLATION.md",
    "CONTRIBUTING.md",
    "RELEASING.md",
    # Plugin READMEs
    "plugins/*/README.md",
    # Custom docs (not synced reference copies)
    "docs/CLAUDE_CODE_GUIDE.md",
    "docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md",
    "docs/PLAYWRIGHT_CLI.md",
    "docs/README.md",
    "docs/research/README.md",
]


# ---------------------------------------------------------------------------
# Candidate discovery
# ---------------------------------------------------------------------------

def _find_candidates(project_root: Path) -> List[Path]:
    """Find markdown files that need frontmatter onboarding.

    Uses whitelist patterns. Skips files that already have frontmatter.
    """
    candidates: List[Path] = []

    for pattern in CANDIDATE_PATTERNS:
        for md in sorted(project_root.glob(pattern)):
            if not md.is_file():
                continue
            content = read_file_safe(md)
            if not content:
                continue
            # Skip files that already have any frontmatter
            if extract_frontmatter(content) is not None:
                continue
            candidates.append(md)

    return candidates


# ---------------------------------------------------------------------------
# Frontmatter generation
# ---------------------------------------------------------------------------

def _extract_title(content: str) -> Optional[str]:
    """Extract the first heading from markdown content.

    Handles both markdown # headings and HTML <h1> tags.
    """
    # Try HTML <h1> first (some READMEs use this)
    html_match = re.search(r"<h1[^>]*>(.+?)</h1>", content, re.IGNORECASE | re.DOTALL)
    if html_match:
        title = html_match.group(1).strip()
        title = re.sub(r"<[^>]+>", "", title)  # Strip nested HTML tags
        return title

    # Fall back to markdown # heading
    md_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if md_match:
        title = md_match.group(1).strip()
        title = re.sub(r"\*\*(.+?)\*\*", r"\1", title)
        title = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", title)
        return title

    return None


def _git_last_date(path: Path, project_root: Path) -> str:
    """Get the last commit date for a file via git log."""
    rel = str(path.relative_to(project_root))
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ai", "--", rel],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_root),
        )
        if result.returncode == 0 and result.stdout.strip():
            # Extract just the date part (YYYY-MM-DD)
            return result.stdout.strip()[:10]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return date.today().isoformat()


def _generate_frontmatter(path: Path, project_root: Path) -> Dict[str, str]:
    """Generate minimal 2-field frontmatter for a doc."""
    content = read_file_safe(path) or ""
    title = _extract_title(content) or path.stem
    last_updated = _git_last_date(path, project_root)

    return {
        "title": title,
        "last_updated": last_updated,
    }


def _format_frontmatter(fm: Dict[str, str]) -> str:
    """Format frontmatter dict as YAML block."""
    lines = ["---"]
    lines.append(f'title: "{fm["title"]}"')
    lines.append(f'last_updated: {fm["last_updated"]}')
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Apply frontmatter
# ---------------------------------------------------------------------------

def _apply_frontmatter(path: Path, fm: Dict[str, str]) -> bool:
    """Prepend frontmatter to a file. Returns True on success."""
    content = read_file_safe(path)
    if content is None:
        return False

    # Double-check: don't add if frontmatter already exists
    if extract_frontmatter(content) is not None:
        return False

    fm_block = _format_frontmatter(fm)
    new_content = fm_block + "\n\n" + content
    try:
        path.write_text(new_content, encoding="utf-8")
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def suggest_onboarding(project_root: Path) -> dict:
    """Find candidates and generate suggested frontmatter.

    Returns dict with candidates list and summary.
    """
    candidates = _find_candidates(project_root)

    results = []
    for path in candidates:
        rel = str(path.relative_to(project_root))
        fm = _generate_frontmatter(path, project_root)
        results.append({
            "path": rel,
            "suggested_frontmatter": fm,
        })

    return {
        "candidates": results,
        "summary": {
            "total_scanned": len(results) + _count_skipped(project_root),
            "already_has_frontmatter": _count_skipped(project_root),
            "candidates": len(results),
        },
    }


def _count_skipped(project_root: Path) -> int:
    """Count files matching whitelist that already have frontmatter."""
    count = 0
    for pattern in CANDIDATE_PATTERNS:
        for md in project_root.glob(pattern):
            if not md.is_file():
                continue
            content = read_file_safe(md)
            if content and extract_frontmatter(content) is not None:
                count += 1
    return count


def apply_onboarding(project_root: Path) -> dict:
    """Apply frontmatter to all candidates.

    Returns dict with results for each file.
    """
    candidates = _find_candidates(project_root)

    results = []
    applied = 0
    for path in candidates:
        rel = str(path.relative_to(project_root))
        fm = _generate_frontmatter(path, project_root)
        success = _apply_frontmatter(path, fm)
        results.append({
            "path": rel,
            "frontmatter": fm,
            "applied": success,
        })
        if success:
            applied += 1

    return {
        "results": results,
        "summary": {
            "candidates": len(candidates),
            "applied": applied,
            "failed": len(candidates) - applied,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Suggest or apply frontmatter to docs that need tracking."
    )
    parser.add_argument(
        "project_root",
        help="Path to the project root directory",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply suggested frontmatter to candidate files",
    )

    args = parser.parse_args()
    root = Path(args.project_root).resolve()

    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    if args.apply:
        result = apply_onboarding(root)
    else:
        result = suggest_onboarding(root)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
