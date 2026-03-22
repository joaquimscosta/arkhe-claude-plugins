#!/usr/bin/env python3
"""
Cross-reference integrity checker.

Validates all markdown links across docs/, plugins/, .claude/skills/, and root
to ensure targets exist.

Checks:
  XR001  Markdown link target file does not exist
  XR002  Anchor #section not found in target file headings
  XR003  Image reference target does not exist

Usage:
    validate_cross_references.py [--format text|json] [--min-severity ...]
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validation_utils import (
    ERROR, WARNING, Issue,
    find_project_root, filter_issues, format_output, has_errors,
    standard_argparse,
)

# Directories to scan for markdown files
SCAN_DIRS = ["docs", "plugins", ".claude/skills"]

# Patterns to skip
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "ftp://", "tel:")
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp"}


def heading_to_anchor(heading: str) -> str:
    """Convert a markdown heading to GitHub-style anchor slug."""
    # Strip leading # and whitespace
    text = re.sub(r"^#+\s*", "", heading)
    # Strip inline formatting
    text = re.sub(r"[*_`~]", "", text)
    # Strip links but keep text: [text](url) -> text
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Convert to lowercase
    text = text.lower().strip()
    # Replace spaces and non-alphanumeric with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    # Strip leading/trailing hyphens
    text = text.strip("-")
    return text


def extract_headings(content: str) -> Set[str]:
    """Extract heading anchors from markdown content."""
    anchors = set()
    in_code_block = False
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped.startswith("#"):
            anchor = heading_to_anchor(stripped)
            if anchor:
                anchors.add(anchor)
    return anchors


def extract_links(content: str) -> List[Tuple[str, bool, int]]:
    """Extract markdown links from content, skipping code blocks.

    Returns list of (target, is_image, line_number).
    """
    links = []
    in_code_block = False

    for line_num, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Also skip inline code
        # Remove inline code spans to avoid matching links inside them
        cleaned = re.sub(r"`[^`]+`", "", line)

        # Image links: ![alt](target)
        for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", cleaned):
            links.append((match.group(1).strip(), True, line_num))

        # Regular links: [text](target) — exclude image links already captured
        for match in re.finditer(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", cleaned):
            links.append((match.group(1).strip(), False, line_num))

    return links


def find_markdown_files(root: Path) -> List[Path]:
    """Find all markdown files to check."""
    files = []

    # Root-level markdown files
    for md in sorted(root.glob("*.md")):
        files.append(md)

    # Scan directories
    for dir_name in SCAN_DIRS:
        scan_dir = root / dir_name
        if scan_dir.is_dir():
            for md in sorted(scan_dir.rglob("*.md")):
                files.append(md)

    return files


def validate_link(
    source_path: Path,
    target_raw: str,
    is_image: bool,
    line_num: int,
    root: Path,
    heading_cache: Dict[str, Set[str]],
) -> Optional[Issue]:
    """Validate a single link target."""
    # Skip external URLs
    if any(target_raw.startswith(prefix) for prefix in EXTERNAL_PREFIXES):
        return None

    # Skip pure anchors (same-file references)
    if target_raw.startswith("#"):
        return None

    # Skip template variables
    if target_raw.startswith("$") or target_raw.startswith("{"):
        return None

    # Skip absolute-path links (site-internal references from synced docs)
    if target_raw.startswith("/"):
        return None

    # Separate path and anchor
    if "#" in target_raw:
        path_part, anchor = target_raw.split("#", 1)
    else:
        path_part, anchor = target_raw, None

    # Strip query strings
    if "?" in path_part:
        path_part = path_part.split("?", 1)[0]

    # Skip empty paths (pure anchor after stripping)
    if not path_part:
        return None

    # Resolve relative path
    source_dir = source_path.parent
    target_path = (source_dir / path_part).resolve()

    # Compute relative location for reporting
    try:
        rel_source = str(source_path.relative_to(root))
    except ValueError:
        rel_source = str(source_path)

    location = f"{rel_source}:{line_num}"

    # Check file existence
    if not target_path.exists():
        if is_image:
            return Issue("XR003", WARNING, f"Image target not found: {target_raw}", location)
        else:
            return Issue("XR001", ERROR, f"Link target not found: {path_part}", location)

    # Check anchor (only for markdown files)
    if anchor and target_path.suffix == ".md":
        cache_key = str(target_path)
        if cache_key not in heading_cache:
            try:
                target_content = target_path.read_text(encoding="utf-8")
                heading_cache[cache_key] = extract_headings(target_content)
            except (OSError, UnicodeDecodeError):
                heading_cache[cache_key] = set()

        expected_anchor = anchor.lower()
        if expected_anchor not in heading_cache[cache_key]:
            return Issue(
                "XR002", WARNING,
                f"Anchor '#{anchor}' not found in {path_part}",
                location,
            )

    return None


def main():
    parser = standard_argparse("Validate markdown cross-references across the repository")
    args = parser.parse_args()

    root = find_project_root()
    md_files = find_markdown_files(root)

    if not md_files:
        print("No markdown files found.", file=sys.stderr)
        sys.exit(0)

    all_issues: List[Issue] = []
    heading_cache: Dict[str, Set[str]] = {}

    for md_path in md_files:
        try:
            content = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        links = extract_links(content)
        for target_raw, is_image, line_num in links:
            issue = validate_link(md_path, target_raw, is_image, line_num, root, heading_cache)
            if issue:
                all_issues.append(issue)

    # Filter and output
    filtered = filter_issues(all_issues, args.min_severity)
    print(format_output("Cross-Reference Integrity", filtered, args.format))

    if has_errors(filtered):
        sys.exit(1)
    elif filtered:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
