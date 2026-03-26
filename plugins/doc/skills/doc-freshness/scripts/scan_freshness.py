#!/usr/bin/env python3
"""
Documentation Freshness Scanner (Orchestrator)

Discovers documentation files, runs link checks, version checks,
and git staleness analysis. Outputs a unified JSON report.

Uses only standard library (no external dependencies). Python 3.8+.

Usage:
    python3 scan_freshness.py <project_root>
    python3 scan_freshness.py --links-only <project_root>
    python3 scan_freshness.py --critical-only <project_root>
    python3 scan_freshness.py --config .arkhe.yaml <project_root>

Output:
    JSON with docs inventory, broken links, version mismatches,
    staleness metrics, and summary.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    detect_doc_tier,
    discover_markdown_files,
    extract_headings,
    git_is_available,
    git_last_modified,
    parse_markdown_links,
    read_file_safe,
    read_yaml_section,
    DEFAULT_DOC_PATTERNS,
    DEFAULT_EXCLUDE_PATTERNS,
)
from link_checker import check_all_links
from version_checker import check_all_versions, collect_ground_truth
from claude_md_checker import check_claude_md


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config(root: Path, config_path: Optional[str] = None) -> dict:
    """Load doc-freshness configuration from .arkhe.yaml."""
    if config_path:
        path = Path(config_path)
        if not path.is_absolute():
            path = root / path
    else:
        path = root / ".arkhe.yaml"

    if not path.exists():
        return {}

    section = read_yaml_section(path, "doc-freshness")
    return section or {}


# ---------------------------------------------------------------------------
# Git staleness analysis
# ---------------------------------------------------------------------------

def compute_staleness(
    doc_paths: List[Path], project_root: Path
) -> List[Dict[str, object]]:
    """Compute git-based staleness for each documentation file.

    Compares each doc's last commit date against the most recent
    code commit in the project.

    Returns list of dicts with:
        doc, doc_date, doc_age_days, latest_code_date, code_age_days, drift_score.
    """
    if not git_is_available(str(project_root)):
        return []

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    staleness: List[Dict[str, object]] = []

    # Get latest code commit date (any file that isn't .md)
    import subprocess
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--diff-filter=ACMR",
             "--", "*.py", "*.ts", "*.tsx", "*.js", "*.jsx",
             "*.java", "*.kt", "*.go", "*.rs", "*.rb",
             "*.yaml", "*.yml", "*.json", "*.toml"],
            capture_output=True, text=True, timeout=10,
            cwd=str(project_root),
        )
        latest_code_date_str = result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        latest_code_date_str = None

    latest_code_date = _parse_git_date(latest_code_date_str)

    for doc_path in doc_paths:
        rel_doc = str(doc_path.relative_to(project_root))
        doc_date_str = git_last_modified(rel_doc, str(project_root))
        doc_date = _parse_git_date(doc_date_str)

        doc_age_days = (now - doc_date).days if doc_date else None
        code_age_days = (now - latest_code_date).days if latest_code_date else None

        # Compute drift score
        drift_score = "unknown"
        if doc_age_days is not None and code_age_days is not None:
            gap = doc_age_days - code_age_days
            if gap <= 7:
                drift_score = "fresh"
            elif gap <= 30:
                drift_score = "aging"
            elif gap <= 90:
                drift_score = "stale"
            else:
                drift_score = "very_stale"

        staleness.append({
            "doc": rel_doc,
            "doc_date": doc_date_str,
            "doc_age_days": doc_age_days,
            "latest_code_date": latest_code_date_str,
            "code_age_days": code_age_days,
            "drift_score": drift_score,
        })

    return staleness


def _parse_git_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse a git date string to a UTC-naive datetime for age calculations.

    Accepts both %ai format ('2026-03-15 10:30:00 -0400') and
    %aI format ('2026-03-15T10:30:00-04:00').
    """
    if not date_str:
        return None
    try:
        # Try ISO 8601 with timezone first (%aI format)
        # Python 3.7+ supports %z for ±HH:MM
        cleaned = date_str.strip()
        if "T" in cleaned:
            # %aI format: 2026-03-15T10:30:00-04:00
            dt = datetime.fromisoformat(cleaned)
        else:
            # %ai format: 2026-03-15 10:30:00 -0400
            # Convert -0400 to -04:00 for fromisoformat
            parts = cleaned.rsplit(" ", 1)
            if len(parts) == 2 and (parts[1].startswith("+") or parts[1].startswith("-")):
                tz = parts[1]
                if len(tz) == 5:  # -0400
                    tz = tz[:3] + ":" + tz[3:]
                cleaned = parts[0].replace(" ", "T") + tz
            dt = datetime.fromisoformat(cleaned)

        # Convert to UTC-naive for consistent age calculations
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except (ValueError, IndexError, TypeError):
        # Fallback: parse just date/time, ignore timezone
        try:
            return datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
        except (ValueError, IndexError):
            return None


# ---------------------------------------------------------------------------
# Document inventory
# ---------------------------------------------------------------------------

def build_inventory(
    doc_paths: List[Path], project_root: Path
) -> List[Dict[str, object]]:
    """Build an inventory of documentation files with their metadata."""
    inventory: List[Dict[str, object]] = []

    for doc_path in doc_paths:
        rel_doc = str(doc_path.relative_to(project_root))
        content = read_file_safe(doc_path)
        tier = detect_doc_tier(doc_path)
        if content is None:
            inventory.append({
                "path": rel_doc,
                "tier": tier,
                "headings": [],
                "link_count": 0,
                "line_count": 0,
                "error": "Cannot read file",
            })
            continue

        headings = extract_headings(content)
        links = parse_markdown_links(content)

        inventory.append({
            "path": rel_doc,
            "tier": tier,
            "headings": [h["text"] for h in headings],
            "link_count": len(links),
            "line_count": len(content.splitlines()),
        })

    return inventory


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def scan(
    project_root: Path,
    links_only: bool = False,
    config_path: Optional[str] = None,
    critical_only: bool = False,
) -> dict:
    """Run the full freshness scan.

    Args:
        project_root: Path to the project root.
        links_only: If True, only run link checks (fast mode).
        config_path: Optional path to config file.
        critical_only: If True, only scan critical docs (README.md, CLAUDE.md, plugin docs).

    Returns:
        Complete scan results as a dict.
    """
    # Load configuration
    config = load_config(project_root, config_path)
    doc_patterns = config.get("doc_patterns", DEFAULT_DOC_PATTERNS)
    exclude = config.get("exclude", DEFAULT_EXCLUDE_PATTERNS)

    # Ensure patterns are lists
    if isinstance(doc_patterns, str):
        doc_patterns = [doc_patterns]
    if isinstance(exclude, str):
        exclude = [exclude]

    # Discover documentation files
    doc_paths = discover_markdown_files(project_root, doc_patterns, exclude)

    # Filter to critical docs if requested
    if critical_only:
        critical_paths = {
            "README.md",
            "CLAUDE.md",
        }
        doc_paths = [
            p for p in doc_paths
            if str(p.relative_to(project_root)) in critical_paths
        ]

    if not doc_paths:
        return {
            "error": "No documentation files found",
            "config": {
                "doc_patterns": doc_patterns,
                "exclude": exclude,
            },
            "docs": [],
            "broken_links": {"findings": [], "summary": {}},
            "version_mismatches": {"findings": [], "summary": {}},
            "staleness": [],
            "summary": {
                "total_docs": 0,
                "broken_links": 0,
                "version_mismatches": 0,
                "stale_docs": 0,
            },
        }

    # Build inventory
    inventory = build_inventory(doc_paths, project_root)

    # Run link checks (always)
    link_results = check_all_links(doc_paths, project_root)

    # Run additional checks unless links-only mode
    version_results: Dict[str, object] = {"findings": [], "summary": {}}
    staleness: List[Dict[str, object]] = []
    claude_md_results: Dict[str, object] = {"findings": [], "summary": {}}

    if not links_only:
        version_results = check_all_versions(doc_paths, project_root)
        staleness = compute_staleness(doc_paths, project_root)
        # CLAUDE.md structural drift check
        if (project_root / "CLAUDE.md").exists():
            claude_md_results = check_claude_md(project_root)

    # Build summary
    broken_count = link_results["summary"].get("broken", 0)
    version_mismatch_count = version_results.get("summary", {})
    if isinstance(version_mismatch_count, dict):
        version_mismatch_count = version_mismatch_count.get("mismatches", 0)
    else:
        version_mismatch_count = 0

    stale_count = sum(
        1 for s in staleness
        if s.get("drift_score") in ("stale", "very_stale")
    )

    # Count docs per tier
    tier_counts = {"basic": 0, "deep": 0}
    for doc in inventory:
        tier = doc.get("tier", "basic")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    return {
        "scan_date": datetime.now().isoformat(),
        "project_root": str(project_root),
        "config": {
            "doc_patterns": doc_patterns,
            "exclude": exclude,
            "links_only": links_only,
            "critical_only": critical_only,
        },
        "docs": inventory,
        "broken_links": link_results,
        "version_mismatches": version_results,
        "staleness": staleness,
        "claude_md_drift": claude_md_results,
        "summary": {
            "total_docs": len(doc_paths),
            "tier_counts": tier_counts,
            "broken_links": broken_count,
            "version_mismatches": version_mismatch_count,
            "stale_docs": stale_count,
            "claude_md_drift": len([
                f for f in claude_md_results.get("findings", [])
                if f.get("status") != "ok"
            ]),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan project documentation for freshness issues."
    )
    parser.add_argument(
        "project_root",
        help="Path to the project root directory",
    )
    parser.add_argument(
        "--links-only",
        action="store_true",
        help="Only check for broken links (fast mode)",
    )
    parser.add_argument(
        "--critical-only",
        action="store_true",
        help="Only scan critical docs (README.md, CLAUDE.md, plugin docs) — fast mode for SessionStart hook",
    )
    parser.add_argument(
        "--config",
        help="Path to .arkhe.yaml config file (default: <project_root>/.arkhe.yaml)",
    )

    args = parser.parse_args()
    root = Path(args.project_root).resolve()

    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = scan(root, links_only=args.links_only, config_path=args.config, critical_only=args.critical_only)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
