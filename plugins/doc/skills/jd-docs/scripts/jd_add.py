#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Move or add a file to a Johnny.Decimal area directory.

Usage:
    uv run jd_add.py docs/roadmap.md 00
    uv run jd_add.py docs/roadmap.md 00-getting-started
    uv run jd_add.py "docs/My Design Doc.md" 20 --name design-doc.md
    uv run jd_add.py docs/roadmap.md 00 --dry-run
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    find_area_by_prefix,
    normalize_filename,
    resolve_config,
)
from jd_index import re_index


def resolve_target_area(
    target: str,
    docs_dir: Path,
) -> tuple[Path | None, str | None]:
    """Resolve target to an area directory path.

    Accepts prefix ("20") or full name ("20-architecture").
    Returns (area_path, error_message).
    """
    # Try as a prefix (two digits)
    if re.match(r"^[0-9]{2}$", target):
        area = find_area_by_prefix(docs_dir, target)
        if area:
            return area, None
        return None, f"No area with prefix '{target}' found in {docs_dir}"

    # Try as a full directory name
    area_path = docs_dir / target
    if area_path.is_dir():
        return area_path, None

    # Try as prefix-name pattern
    if re.match(r"^[0-9]{2}-", target):
        area_path = docs_dir / target
        if not area_path.exists():
            return None, f"Area directory '{target}' does not exist in {docs_dir}"

    return None, f"Cannot resolve target '{target}' to an area directory"


def find_cross_references(
    old_path: Path,
    docs_dir: Path,
) -> list[tuple[Path, int, str]]:
    """Search docs for markdown references to old_path.

    Returns list of (file, line_number, line_content).
    """
    refs: list[tuple[Path, int, str]] = []

    # Build patterns to search for
    old_name = old_path.name
    # Relative path from docs root
    try:
        old_relative = old_path.relative_to(docs_dir)
    except ValueError:
        old_relative = None

    patterns = [old_name]
    if old_relative:
        patterns.append(str(old_relative))
        patterns.append(f"./{old_relative}")

    for md_file in docs_dir.rglob("*.md"):
        if md_file == old_path:
            continue
        try:
            with open(md_file) as f:
                for lineno, line in enumerate(f, 1):
                    for pattern in patterns:
                        if pattern in line:
                            refs.append((md_file, lineno, line.rstrip()))
                            break  # Only report each line once
        except (OSError, UnicodeDecodeError):
            continue

    return refs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Move or add a file to a Johnny.Decimal area directory"
    )
    parser.add_argument(
        "file",
        help="Path to the file to move",
    )
    parser.add_argument(
        "target",
        help="Target area by prefix ('20') or full name ('20-architecture')",
    )
    parser.add_argument(
        "--name",
        "-n",
        default=None,
        help="Override the output filename (auto-normalized if not provided)",
    )
    parser.add_argument(
        "--dir",
        "-d",
        default=None,
        help="Docs directory (default: from config or 'docs')",
    )
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Path to .jd-config.json (auto-detected if not specified)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing",
    )

    args = parser.parse_args()
    base_path = Path.cwd()

    # Resolve source file
    src = Path(args.file)
    if not src.is_absolute():
        src = base_path / src

    if not src.exists():
        print(f"Error: File not found: {src}")
        return 1

    if not src.is_file():
        print(f"Error: Not a file: {src}")
        return 1

    # Load config
    config = resolve_config(args.config, base_path)

    # Resolve docs directory
    if args.dir:
        docs_dir = Path(args.dir)
        if not docs_dir.is_absolute():
            docs_dir = base_path / docs_dir
    else:
        docs_dir = base_path / config.get("root", "docs")

    if not docs_dir.exists():
        print(f"Error: Docs directory does not exist: {docs_dir}")
        return 1

    # Resolve target area
    area_dir, err = resolve_target_area(args.target, docs_dir)
    if err:
        print(f"Error: {err}")
        return 1

    # Determine output filename
    if args.name:
        out_name = normalize_filename(args.name)
    else:
        out_name = normalize_filename(src.name)

    dst = area_dir / out_name

    # Check for conflicts
    if dst.exists():
        print(f"Error: File already exists: {dst}")
        print(f"Use --name to specify a different filename.")
        return 1

    # Execute
    mode = "(dry-run)" if args.dry_run else ""
    print(f"Moving file to {area_dir.name}/ {mode}")
    print()
    print(f"  Source:      {src}")
    print(f"  Destination: {dst}")
    if src.name != out_name:
        print(f"  Renamed:     {src.name} -> {out_name}")

    if not args.dry_run:
        shutil.move(str(src), str(dst))
        print(f"\n  Moved successfully.")

    # Check for cross-references
    refs = find_cross_references(src, docs_dir)
    if refs:
        print(f"\nCross-references found ({len(refs)} occurrence(s)):")
        print("These files reference the old path and may need updating:")
        print()
        for ref_file, lineno, line in refs[:10]:
            try:
                rel = ref_file.relative_to(docs_dir)
            except ValueError:
                rel = ref_file
            print(f"  {rel}:{lineno}: {line.strip()[:100]}")
        if len(refs) > 10:
            print(f"  ... and {len(refs) - 10} more")

        # Suggest the new relative path
        try:
            new_rel = dst.relative_to(docs_dir)
            old_rel = src.relative_to(docs_dir)
            print(f"\nSuggested replacement: '{old_rel}' -> '{new_rel}'")
        except ValueError:
            pass
    else:
        print("\nNo cross-references found.")

    # Re-index
    if not args.dry_run:
        print("\nRe-indexing...")
        re_index(docs_dir, config, dry_run=False)
    elif args.dry_run:
        print("\nWould re-index after move.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
