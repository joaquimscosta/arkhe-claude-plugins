#!/usr/bin/env python3
"""
Detect drift in .arkhe/roadmap/ context files.

Checks existence, staleness, and codebase changes since last update.
Outputs JSON report to stdout.

Usage:
    python3 detect_context_drift.py [project_root]
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Sibling import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    CONTEXT_FILES,
    classify_staleness,
    detect_tech_stack,
    discover_modules,
    git_commits_since,
    git_feat_fix_commits_since,
    git_is_available,
    git_last_modified_date,
    git_latest_commit_date,
    load_config,
)


def parse_iso_date(iso_str: str) -> datetime:
    """Parse an ISO 8601 date string to datetime."""
    # Handle timezone offset format from git
    # Python 3.8 doesn't have datetime.fromisoformat for all formats
    clean = iso_str.strip()
    # Replace timezone offset like +00:00 or -04:00 for Python 3.8 compat
    if "+" in clean[10:] or clean.endswith("Z"):
        if clean.endswith("Z"):
            clean = clean[:-1] + "+00:00"
    try:
        # Python 3.10+ handles this natively
        return datetime.fromisoformat(clean)
    except ValueError:
        # Fallback: strip timezone for date-only comparison
        date_part = clean[:10]
        return datetime.strptime(date_part, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def days_between(date_str: str) -> int:
    """Calculate days between a date string and now."""
    dt = parse_iso_date(date_str)
    now = datetime.now(timezone.utc)
    # Make both timezone-aware for comparison
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (now - dt).days)


def check_file(file_name: str, context_dir: Path, project_root: str) -> dict:
    """Check a single context file for existence and staleness."""
    file_path = context_dir / file_name
    rel_path = str(file_path.relative_to(Path(project_root)))

    if not file_path.exists():
        return {"exists": False}

    result: dict = {"exists": True}

    last_mod = git_last_modified_date(rel_path, project_root)
    if last_mod:
        days = days_between(last_mod)
        result["last_modified"] = last_mod[:10]  # Date only
        result["staleness"] = classify_staleness(days)
        result["days_since_update"] = days
        result["commits_since"] = git_commits_since(rel_path, project_root)
        result["feat_fix_commits_since"] = git_feat_fix_commits_since(
            rel_path, project_root
        )
    else:
        # File exists but not in git (uncommitted)
        result["last_modified"] = None
        result["staleness"] = "uncommitted"
        result["days_since_update"] = 0
        result["commits_since"] = 0
        result["feat_fix_commits_since"] = 0

    return result


def detect_new_modules(
    context_dir: Path, project_root: Path, modules: list
) -> list:
    """Find modules not mentioned in architecture.md."""
    arch_file = context_dir / "architecture.md"
    if not arch_file.exists():
        return modules  # All modules are "new" if no architecture.md

    try:
        content = arch_file.read_text(encoding="utf-8").lower()
    except Exception:
        return modules

    new = []
    for mod in modules:
        if mod.lower() not in content:
            new.append(mod)
    return new


def main():
    """Main entry point."""
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    project_root_path = Path(project_root).resolve()

    # Load config
    config = load_config(project_root_path)
    context_dir = project_root_path / config["context_dir"]

    # Check git availability
    has_git = git_is_available(str(project_root_path))

    # Build report
    report: dict = {
        "context_dir": config["context_dir"],
        "exists": context_dir.is_dir(),
        "git_available": has_git,
        "files": {},
        "new_modules": [],
        "tech_stack": detect_tech_stack(project_root_path),
        "config": config,
    }

    # Check each context file
    if has_git:
        for file_name in CONTEXT_FILES:
            report["files"][file_name] = check_file(
                file_name, context_dir, str(project_root_path)
            )

        # Detect new modules
        modules = discover_modules(project_root_path)
        report["discovered_modules"] = modules
        report["new_modules"] = detect_new_modules(
            context_dir, project_root_path, modules
        )
    else:
        # Without git, just check existence
        for file_name in CONTEXT_FILES:
            file_path = context_dir / file_name
            report["files"][file_name] = {"exists": file_path.exists()}
        report["discovered_modules"] = discover_modules(project_root_path)
        report["new_modules"] = report["discovered_modules"]

    # Latest codebase commit
    if has_git:
        latest = git_latest_commit_date(str(project_root_path))
        if latest:
            report["latest_commit"] = latest[:10]

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
