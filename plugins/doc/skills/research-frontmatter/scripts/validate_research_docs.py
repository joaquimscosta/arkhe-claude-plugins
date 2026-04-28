#!/usr/bin/env python3
"""
Research document validator.

Validates YAML frontmatter, required sections, index accuracy, and staleness
for research documents. Supports JD-aware path resolution via .jd-config.json.

Checks:
  RD001  Missing YAML frontmatter
  RD002  Missing required field: title
  RD003  Missing required field: version
  RD004  Missing required field: status
  RD005  Missing required field: created
  RD006  Missing required field: last_updated
  RD007  Invalid status value
  RD008  Invalid created date format
  RD009  Invalid last_updated date format
  RD010  Invalid version format (not semver X.Y.Z)
  RD011  Missing ## Executive Summary section
  RD012  Missing ## References section
  RD013  Research doc not in README.md index
  RD014  README index metadata mismatch
  RD015  README index references missing file
  RD016  Stale last_updated (older than git modification date)

Usage:
    validate_research_docs.py [--staleness-only] [--research-dir DIR] [--format text|json]
"""

import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    ERROR, WARNING, SUGGESTION, Issue,
    find_project_root, parse_frontmatter, git_last_modified,
    parse_date, is_valid_date_format, is_valid_semver,
    filter_issues, format_output, has_errors, standard_argparse,
    resolve_research_path,
)

VALID_STATUSES = {"Draft", "Published", "Living Document"}
REQUIRED_FIELDS = ["title", "version", "status", "created", "last_updated"]
SKIP_FILES = {"README.md", "TEMPLATE.md"}

# Staleness thresholds (days)
STALENESS_THRESHOLD_DEFAULT = 7
STALENESS_THRESHOLD_LIVING = 30


def find_research_docs(research_dir: Path) -> List[Path]:
    """Find all research markdown files, recursively."""
    docs = []
    for md_file in sorted(research_dir.rglob("*.md")):
        if md_file.name in SKIP_FILES:
            continue
        docs.append(md_file)
    return docs


def parse_index_table(readme_path: Path) -> List[Dict[str, str]]:
    """Parse the research README.md index table.

    Returns list of dicts with keys: file, version, status, created, last_updated.
    """
    if not readme_path.exists():
        return []

    content = readme_path.read_text(encoding="utf-8")
    entries = []

    # Match table rows: | [Topic](file.md) | version | status | created | last_updated |
    pattern = re.compile(
        r"\|\s*\[.*?\]\(([^)]+)\)\s*\|"  # file path
        r"\s*([^|]*?)\s*\|"               # version
        r"\s*([^|]*?)\s*\|"               # status
        r"\s*([^|]*?)\s*\|"               # created
        r"\s*([^|]*?)\s*\|"               # last_updated
    )

    for match in pattern.finditer(content):
        entries.append({
            "file": match.group(1).strip(),
            "version": match.group(2).strip(),
            "status": match.group(3).strip(),
            "created": match.group(4).strip(),
            "last_updated": match.group(5).strip(),
        })

    return entries


def validate_frontmatter(doc_path: Path, fm: Optional[Dict], research_dir: Path) -> List[Issue]:
    """Validate frontmatter fields (RD001-RD010)."""
    issues = []  # type: List[Issue]
    rel_path = str(doc_path.relative_to(research_dir))

    if fm is None:
        issues.append(Issue("RD001", ERROR, "Missing YAML frontmatter", rel_path))
        return issues

    # Required fields (RD002-RD006)
    rule_map = {
        "title": "RD002",
        "version": "RD003",
        "status": "RD004",
        "created": "RD005",
        "last_updated": "RD006",
    }
    for field_name, rule_id in rule_map.items():
        if field_name not in fm or not fm[field_name]:
            issues.append(Issue(rule_id, ERROR, f"Missing required field: {field_name}", rel_path))

    # Status validation (RD007)
    status = fm.get("status", "")
    if status and status not in VALID_STATUSES:
        issues.append(Issue(
            "RD007", ERROR,
            f"Invalid status '{status}' (expected: {', '.join(sorted(VALID_STATUSES))})",
            rel_path,
        ))

    # Date format validation (RD008-RD009)
    for field_name, rule_id in [("created", "RD008"), ("last_updated", "RD009")]:
        val = fm.get(field_name, "")
        if val and not is_valid_date_format(val):
            issues.append(Issue(rule_id, WARNING, f"'{field_name}' not in YYYY-MM-DD format: {val}", rel_path))

    # Version format (RD010)
    version = fm.get("version", "")
    if version and not is_valid_semver(version):
        issues.append(Issue("RD010", WARNING, f"Version not in X.Y.Z format: {version}", rel_path))

    return issues


def validate_sections(doc_path: Path, body: str, research_dir: Path) -> List[Issue]:
    """Validate required sections (RD011-RD012)."""
    issues = []  # type: List[Issue]
    rel_path = str(doc_path.relative_to(research_dir))

    if not re.search(r"^##\s+Executive\s+Summary", body, re.MULTILINE | re.IGNORECASE):
        issues.append(Issue("RD011", WARNING, "Missing '## Executive Summary' section", rel_path))

    if not re.search(r"^##\s+References", body, re.MULTILINE | re.IGNORECASE):
        issues.append(Issue("RD012", WARNING, "Missing '## References' section", rel_path))

    return issues


def validate_index(
    docs: List[Path],
    index_entries: List[Dict[str, str]],
    doc_frontmatters: Dict[str, Dict],
    research_dir: Path,
) -> List[Issue]:
    """Validate index accuracy (RD013-RD015)."""
    issues = []  # type: List[Issue]

    # Build set of indexed file paths
    indexed_files = {entry["file"] for entry in index_entries}

    # RD013: Research doc not in index
    for doc_path in docs:
        rel_path = str(doc_path.relative_to(research_dir))
        if rel_path not in indexed_files:
            issues.append(Issue("RD013", ERROR, "Not listed in README.md index", rel_path))

    # RD014: Index metadata mismatch
    for entry in index_entries:
        rel_path = entry["file"]
        fm = doc_frontmatters.get(rel_path)
        if fm is None:
            continue

        mismatches = []
        for key in ["version", "status", "created", "last_updated"]:
            index_val = entry.get(key, "").strip()
            fm_val = fm.get(key, "").strip()
            if index_val and fm_val and index_val != fm_val:
                mismatches.append(f"{key}: index='{index_val}' vs frontmatter='{fm_val}'")

        if mismatches:
            issues.append(Issue(
                "RD014", WARNING,
                f"Index metadata mismatch: {'; '.join(mismatches)}",
                rel_path,
            ))

    # RD015: Index references missing file
    for entry in index_entries:
        file_path = research_dir / entry["file"]
        if not file_path.exists():
            issues.append(Issue("RD015", WARNING, "Index references missing file", entry["file"]))

    return issues


def validate_staleness(
    doc_path: Path,
    fm: Optional[Dict],
    research_dir: Path,
) -> List[Issue]:
    """Check if last_updated is stale compared to git (RD016)."""
    issues = []  # type: List[Issue]
    rel_path = str(doc_path.relative_to(research_dir))

    if fm is None:
        return issues

    last_updated_str = fm.get("last_updated", "")
    if not last_updated_str:
        return issues

    fm_date = parse_date(last_updated_str)
    if fm_date is None:
        return issues

    git_date = git_last_modified(doc_path)
    if git_date is None:
        return issues

    status = fm.get("status", "")
    threshold = STALENESS_THRESHOLD_LIVING if status == "Living Document" else STALENESS_THRESHOLD_DEFAULT

    if git_date > fm_date + timedelta(days=threshold):
        issues.append(Issue(
            "RD016", WARNING,
            f"Stale: last_updated={last_updated_str} but git shows {git_date.isoformat()} "
            f"(>{threshold} day threshold)",
            rel_path,
            suggestion=f"Update last_updated to {git_date.isoformat()}",
        ))

    return issues


def main():
    parser = standard_argparse("Validate research documents")
    parser.add_argument("--staleness-only", action="store_true",
                        help="Only check staleness (RD016)")
    parser.add_argument("--research-dir", type=str, default=None,
                        help="Explicit research directory path (overrides JD resolution)")
    parser.add_argument("--project-root", type=str, default=None,
                        help="Project root directory (default: auto-detect)")
    args = parser.parse_args()

    root = find_project_root(
        Path(args.project_root) if args.project_root else None
    )

    if args.research_dir:
        research_dir = Path(args.research_dir)
        if not research_dir.is_absolute():
            research_dir = root / research_dir
    else:
        resolved = resolve_research_path(root)
        research_dir = root / resolved["path"]

    if not research_dir.is_dir():
        print(f"No research directory found at {research_dir}", file=sys.stderr)
        sys.exit(0)

    docs = find_research_docs(research_dir)
    if not docs:
        print("No research documents found.", file=sys.stderr)
        sys.exit(0)

    all_issues = []  # type: List[Issue]
    doc_frontmatters = {}  # type: Dict[str, Dict]

    # Parse all documents
    for doc_path in docs:
        content = doc_path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(content)
        rel_path = str(doc_path.relative_to(research_dir))
        if fm:
            doc_frontmatters[rel_path] = fm

        if args.staleness_only:
            all_issues.extend(validate_staleness(doc_path, fm, research_dir))
        else:
            all_issues.extend(validate_frontmatter(doc_path, fm, research_dir))
            all_issues.extend(validate_sections(doc_path, body, research_dir))
            all_issues.extend(validate_staleness(doc_path, fm, research_dir))

    # Index validation (skip in staleness-only mode)
    if not args.staleness_only:
        readme_path = research_dir / "README.md"
        index_entries = parse_index_table(readme_path)
        all_issues.extend(validate_index(docs, index_entries, doc_frontmatters, research_dir))

    # Filter and output
    filtered = filter_issues(all_issues, args.min_severity)
    title = "Research Document Staleness" if args.staleness_only else "Research Document Validation"
    print(format_output(title, filtered, args.format))

    if has_errors(filtered):
        sys.exit(1)
    elif filtered:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
