#!/usr/bin/env python3
"""
Spring Boot Skill Freshness Scanner

Scans Spring Boot plugin skills and research docs, computes content drift,
and outputs a JSON freshness report.

Usage:
    python3 scan_skill_freshness.py <plugin_root>
    python3 scan_skill_freshness.py --format json <plugin_root>
    python3 scan_skill_freshness.py --format text <plugin_root>

Output:
    JSON or text report with per-skill freshness status and drift analysis.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Research doc → skills mapping
RESEARCH_TO_SKILLS: Dict[str, List[str]] = {
    "spring-boot-ecosystem-research.md": [
        "spring-boot-scanner",
        "spring-boot-verify",
        "spring-boot-web-api",
        "spring-boot-data-ddd",
        "spring-boot-modulith",
        "domain-driven-design",
    ],
    "spring-boot-ddd-implementation.md": [
        "domain-driven-design",
        "spring-boot-data-ddd",
        "spring-boot-web-api",
        "spring-boot-modulith",
    ],
    "spring-boot-security-observability-testing.md": [
        "spring-boot-security",
        "spring-boot-observability",
        "spring-boot-testing",
    ],
}

# Staleness thresholds (days)
FRESH_THRESHOLD = 7
AGING_THRESHOLD = 30
STALE_THRESHOLD = 60


def parse_frontmatter(filepath: Path) -> Dict[str, str]:
    """Parse YAML frontmatter from a markdown file using regex."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    result = {}
    for line in match.group(1).splitlines():
        # Handle simple key: value pairs (including quoted values)
        kv = re.match(r'^(\S+)\s*:\s*"?([^"]*)"?\s*$', line)
        if kv:
            result[kv.group(1)] = kv.group(2).strip()
    return result


def git_last_modified(filepath: Path) -> Optional[str]:
    """Get the last git modification date for a file as ISO string."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(filepath)],
            capture_output=True,
            text=True,
            cwd=filepath.parent,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse a date string (ISO or YYYY-MM-DD) to datetime."""
    if not date_str:
        return None
    try:
        # Try ISO format first (from git log)
        if "T" in date_str:
            # Handle timezone offset
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        # Simple date format (from frontmatter)
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def days_since(date: Optional[datetime], now: datetime) -> Optional[int]:
    """Calculate days between a date and now."""
    if not date:
        return None
    delta = now - date
    return delta.days


def classify_staleness(days: Optional[int]) -> str:
    """Classify staleness based on day thresholds."""
    if days is None:
        return "UNKNOWN"
    if days <= FRESH_THRESHOLD:
        return "FRESH"
    if days <= AGING_THRESHOLD:
        return "AGING"
    if days <= STALE_THRESHOLD:
        return "STALE"
    return "VERY_STALE"


def classify_drift(drift_days: Optional[int]) -> str:
    """Classify skill drift (research newer than skill)."""
    if drift_days is None:
        return "UNKNOWN"
    if drift_days <= 0:
        return "UP_TO_DATE"
    if drift_days <= FRESH_THRESHOLD:
        return "FRESH"
    if drift_days <= AGING_THRESHOLD:
        return "NEEDS_REVIEW"
    return "NEEDS_UPDATE"


def build_skill_to_research() -> Dict[str, List[str]]:
    """Build inverse mapping: skill → research docs."""
    result: Dict[str, List[str]] = {}
    for doc, skills in RESEARCH_TO_SKILLS.items():
        for skill in skills:
            result.setdefault(skill, []).append(doc)
    return result


def find_project_root(plugin_root: Path) -> Optional[Path]:
    """Find the git project root from plugin_root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=plugin_root,
            timeout=10,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    # Fallback: walk up looking for .git
    current = plugin_root
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return None


def scan_skills(plugin_root: Path, now: datetime) -> List[Dict[str, Any]]:
    """Scan all Spring Boot skill SKILL.md files."""
    skills_dir = plugin_root / "skills"
    results = []

    if not skills_dir.is_dir():
        return results

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue

        fm = parse_frontmatter(skill_md)
        git_date = git_last_modified(skill_md)
        git_dt = parse_date(git_date)

        results.append({
            "name": fm.get("name", skill_dir.name),
            "spring_boot_version": fm.get("spring-boot-version", "unknown"),
            "skill_path": str(skill_dir.relative_to(plugin_root)),
            "git_modified": git_date,
            "days_since_modified": days_since(git_dt, now),
        })

    return results


def scan_research_docs(
    project_root: Path, now: datetime
) -> List[Dict[str, Any]]:
    """Scan Spring Boot research documents."""
    research_dir = project_root / "docs" / "research"
    results = []

    if not research_dir.is_dir():
        return results

    for doc in sorted(research_dir.iterdir()):
        if not doc.name.startswith("spring-boot-") or not doc.name.endswith(".md"):
            continue

        fm = parse_frontmatter(doc)
        last_updated = fm.get("last_updated")
        git_date = git_last_modified(doc)

        # Use the more recent of frontmatter date and git date
        fm_dt = parse_date(last_updated)
        git_dt = parse_date(git_date)
        effective_dt = max(filter(None, [fm_dt, git_dt]), default=None)
        effective_date = (
            effective_dt.strftime("%Y-%m-%d") if effective_dt else last_updated
        )
        age = days_since(effective_dt, now)

        results.append({
            "file": doc.name,
            "title": fm.get("title", doc.stem),
            "version": fm.get("version", "unknown"),
            "status": fm.get("status", "unknown"),
            "last_updated": last_updated,
            "git_modified": git_date,
            "effective_date": effective_date,
            "days_since_update": age,
            "staleness": classify_staleness(age),
            "skills_affected": RESEARCH_TO_SKILLS.get(doc.name, []),
        })

    return results


def compute_drift(
    skills: List[Dict[str, Any]],
    research_docs: List[Dict[str, Any]],
    now: datetime,
) -> List[Dict[str, Any]]:
    """Compute drift between skills and their research docs."""
    skill_to_research = build_skill_to_research()

    # Build lookup: research doc name → effective datetime
    research_dates: Dict[str, Optional[datetime]] = {}
    for doc in research_docs:
        dt = parse_date(doc.get("effective_date"))
        research_dates[doc["file"]] = dt

    results = []
    for skill in skills:
        name = skill["name"]
        mapped_docs = skill_to_research.get(name, [])
        skill_git_dt = parse_date(skill.get("git_modified"))

        # Find the most recent research doc date for this skill
        latest_research_dt = None
        latest_research_doc = None
        for doc_name in mapped_docs:
            dt = research_dates.get(doc_name)
            if dt and (latest_research_dt is None or dt > latest_research_dt):
                latest_research_dt = dt
                latest_research_doc = doc_name

        # Compute drift: positive = research is newer than skill
        drift_days = None
        if latest_research_dt and skill_git_dt:
            drift_days = (latest_research_dt - skill_git_dt).days

        results.append({
            **skill,
            "research_docs": mapped_docs,
            "latest_research_date": (
                latest_research_dt.strftime("%Y-%m-%d")
                if latest_research_dt
                else None
            ),
            "latest_research_doc": latest_research_doc,
            "drift_days": drift_days,
            "status": classify_drift(drift_days) if mapped_docs else "NO_RESEARCH",
        })

    return results


def build_summary(skills_with_drift: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build drift summary statistics."""
    statuses = [s["status"] for s in skills_with_drift]
    return {
        "total_skills": len(skills_with_drift),
        "up_to_date": statuses.count("UP_TO_DATE"),
        "fresh": statuses.count("FRESH"),
        "needs_review": statuses.count("NEEDS_REVIEW"),
        "needs_update": statuses.count("NEEDS_UPDATE"),
        "no_research": statuses.count("NO_RESEARCH"),
        "unknown": statuses.count("UNKNOWN"),
    }


def format_text(report: Dict[str, Any]) -> str:
    """Format the report as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("SPRING BOOT SKILL FRESHNESS REPORT")
    lines.append(f"Scan date: {report['scan_date']}")
    lines.append("=" * 70)

    # Research docs
    lines.append("\n## Research Documents\n")
    lines.append(
        f"{'Document':<45} {'Version':<8} {'Updated':<12} {'Age':>5} {'Status':<12}"
    )
    lines.append("-" * 85)
    for doc in report["research_docs"]:
        age = doc["days_since_update"]
        age_str = f"{age}d" if age is not None else "?"
        lines.append(
            f"{doc['file']:<45} {doc['version']:<8} "
            f"{doc.get('effective_date', '?'):<12} {age_str:>5} {doc['staleness']:<12}"
        )

    # Skills
    lines.append("\n## Skills\n")
    lines.append(
        f"{'Skill':<30} {'Version':<8} {'Modified':<12} "
        f"{'Research':<12} {'Drift':>6} {'Status':<14}"
    )
    lines.append("-" * 85)
    for skill in report["skills"]:
        git_date = skill.get("git_modified") or "?"
        if git_date != "?" and "T" in str(git_date):
            git_date = git_date[:10]
        research_date = skill.get("latest_research_date") or "-"
        drift = skill.get("drift_days")
        drift_str = f"{drift:+d}d" if drift is not None else "-"
        lines.append(
            f"{skill['name']:<30} {skill['spring_boot_version']:<8} "
            f"{git_date:<12} {research_date:<12} {drift_str:>6} {skill['status']:<14}"
        )

    # Summary
    summary = report["drift_summary"]
    lines.append(f"\n## Summary\n")
    lines.append(f"Total skills: {summary['total_skills']}")
    lines.append(f"  Up to date: {summary['up_to_date']}")
    lines.append(f"  Fresh:      {summary['fresh']}")
    lines.append(f"  Needs review: {summary['needs_review']}")
    lines.append(f"  Needs update: {summary['needs_update']}")
    lines.append(f"  No research:  {summary['no_research']}")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    args = sys.argv[1:]
    fmt = "json"

    # Parse --format flag
    if "--format" in args:
        idx = args.index("--format")
        if idx + 1 < len(args):
            fmt = args[idx + 1]
            args = args[:idx] + args[idx + 2:]

    if not args:
        print("Usage: scan_skill_freshness.py [--format json|text] <plugin_root>")
        sys.exit(1)

    plugin_root = Path(args[0]).resolve()
    if not plugin_root.is_dir():
        print(f"Error: {plugin_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    project_root = find_project_root(plugin_root)
    if not project_root:
        print("Error: could not find git project root", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc)

    # Scan
    skills = scan_skills(plugin_root, now)
    research_docs = scan_research_docs(project_root, now)
    skills_with_drift = compute_drift(skills, research_docs, now)
    summary = build_summary(skills_with_drift)

    report = {
        "scan_date": now.strftime("%Y-%m-%d"),
        "plugin_root": str(plugin_root),
        "project_root": str(project_root),
        "research_docs": research_docs,
        "skills": skills_with_drift,
        "drift_summary": summary,
    }

    if fmt == "text":
        print(format_text(report))
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
