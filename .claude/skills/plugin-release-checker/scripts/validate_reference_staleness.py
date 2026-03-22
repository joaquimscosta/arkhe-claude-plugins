#!/usr/bin/env python3
"""
Synced reference document staleness checker.

Validates that synced documentation in docs/reference/ is up-to-date
by checking git modification dates against a configurable threshold.

Checks:
  RS001  Synced doc not updated in >N days (default: 90)
  RS002  File listed in update-claude-docs.sh but missing locally

Usage:
    validate_reference_staleness.py [--max-age-days 90] [--format text|json]
"""

import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validation_utils import (
    ERROR, WARNING, Issue,
    find_project_root, git_last_modified,
    filter_issues, format_output, has_errors, standard_argparse,
)


def parse_url_mappings(script_path: Path) -> List[Tuple[str, str]]:
    """Parse URL_MAPPINGS from update-claude-docs.sh.

    Returns list of (url, filename) tuples.
    """
    if not script_path.exists():
        return []

    content = script_path.read_text(encoding="utf-8")

    mappings = []
    # Match lines like: "https://...url...|FILENAME.md" (skip comment lines)
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        match = re.search(r'"(https?://[^|]+)\|([^"]+)"', stripped)
        if match:
            mappings.append((match.group(1), match.group(2)))

    return mappings


def main():
    parser = standard_argparse("Check staleness of synced reference documentation")
    parser.add_argument("--max-age-days", type=int, default=90,
                        help="Maximum age in days before flagging (default: 90)")
    args = parser.parse_args()

    root = find_project_root()
    reference_dir = root / "docs" / "reference"
    script_path = reference_dir / "update-claude-docs.sh"

    if not script_path.exists():
        print("No update-claude-docs.sh found.", file=sys.stderr)
        sys.exit(0)

    mappings = parse_url_mappings(script_path)
    if not mappings:
        print("No URL mappings found in update-claude-docs.sh.", file=sys.stderr)
        sys.exit(0)

    all_issues: List[Issue] = []
    today = date.today()
    threshold = timedelta(days=args.max_age_days)

    for url, filename in mappings:
        file_path = reference_dir / filename

        # RS002: File missing
        if not file_path.exists():
            all_issues.append(Issue(
                "RS002", ERROR,
                f"File listed in update-claude-docs.sh but missing locally: {filename}",
                f"docs/reference/{filename}",
                suggestion=f"Run: cd docs/reference && ./update-claude-docs.sh",
            ))
            continue

        # RS001: Staleness check
        git_date = git_last_modified(file_path)
        if git_date and (today - git_date) > threshold:
            age_days = (today - git_date).days
            all_issues.append(Issue(
                "RS001", WARNING,
                f"Synced doc '{filename}' last updated {age_days} days ago "
                f"(threshold: {args.max_age_days} days)",
                f"docs/reference/{filename}",
                suggestion=f"Run: cd docs/reference && ./update-claude-docs.sh",
            ))

    # Filter and output
    filtered = filter_issues(all_issues, args.min_severity)
    print(format_output("Reference Documentation Staleness", filtered, args.format))

    if has_errors(filtered):
        sys.exit(1)
    elif filtered:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
