#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Handle ADR supersession workflow.

Usage:
    uv run adr_supersede.py --old 5 --new 12 --dir docs/adr
"""

import argparse
import re
import sys
from pathlib import Path


def find_adr_by_number(adr_dir: Path, number: int) -> Path | None:
    """Find ADR file by number."""
    # Match patterns with flexible padding
    pattern = re.compile(rf'^(?:ADR-)?0*{number}-.*\.md$', re.IGNORECASE)

    for filepath in adr_dir.glob('*.md'):
        if pattern.match(filepath.name):
            return filepath

    return None


def get_adr_reference(filepath: Path) -> str:
    """Get ADR reference string (e.g., 'ADR-0005')."""
    match = re.match(r'^(?:ADR-)?(\d+)-', filepath.name, re.IGNORECASE)
    if match:
        num = int(match.group(1))
        padding = len(match.group(1))
        return f"ADR-{num:0{padding}d}"
    return filepath.stem


def update_adr_status(filepath: Path, new_status: str, link_ref: str, link_file: str) -> bool:
    """Update the status section of an ADR."""
    content = filepath.read_text()

    # Find and replace status section
    # Match: ## Status\n<content until next ## or end>
    status_pattern = r'(^##\s+Status\s*\n+)([^\n#]+)'

    # Build new status with link
    new_status_text = f"{new_status} by [{link_ref}]({link_file})"
    replacement = rf'\g<1>{new_status_text}'

    new_content, count = re.subn(
        status_pattern,
        replacement,
        content,
        count=1,
        flags=re.MULTILINE | re.IGNORECASE
    )

    if count == 0:
        return False

    filepath.write_text(new_content)
    return True


def add_supersedes_reference(filepath: Path, old_adr_ref: str, old_adr_file: str) -> bool:
    """Add 'Supersedes' reference to new ADR after status section."""
    content = filepath.read_text()

    # Find status section and add reference after it
    # Match the entire status section including the status value
    status_pattern = r'(^##\s+Status\s*\n+[^\n#]+\n)'

    replacement = rf'\g<1>\nSupersedes: [{old_adr_ref}]({old_adr_file})\n'

    new_content, count = re.subn(
        status_pattern,
        replacement,
        content,
        count=1,
        flags=re.MULTILINE | re.IGNORECASE
    )

    if count == 0:
        return False

    filepath.write_text(new_content)
    return True


def supersede_adr(adr_dir: Path, old_number: int, new_number: int) -> bool:
    """Execute supersession workflow."""
    old_adr = find_adr_by_number(adr_dir, old_number)
    new_adr = find_adr_by_number(adr_dir, new_number)

    if not old_adr:
        print(f"Error: Old ADR not found: ADR-{old_number:04d}")
        print(f"Searched in: {adr_dir}")
        return False

    if not new_adr:
        print(f"Error: New ADR not found: ADR-{new_number:04d}")
        print(f"Searched in: {adr_dir}")
        return False

    # Get reference strings
    old_ref = get_adr_reference(old_adr)
    new_ref = get_adr_reference(new_adr)

    print(f"Superseding {old_ref} with {new_ref}...")
    print()

    # Update old ADR status
    if not update_adr_status(old_adr, "Superseded", new_ref, new_adr.name):
        print(f"Error: Could not update status in {old_adr.name}")
        print("The file may have a non-standard format.")
        return False

    print(f"  Updated: {old_adr.name}")
    print(f"    Status: Superseded by [{new_ref}]({new_adr.name})")

    # Add supersedes reference to new ADR
    if not add_supersedes_reference(new_adr, old_ref, old_adr.name):
        print(f"  Warning: Could not add Supersedes reference to {new_adr.name}")
        print("  You may need to add it manually.")
    else:
        print(f"  Updated: {new_adr.name}")
        print(f"    Added: Supersedes: [{old_ref}]({old_adr.name})")

    print()
    print("Supersession complete.")
    print(f"\nNext: Run adr_index.py to update README.md:")
    print(f"  uv run adr_index.py --dir {adr_dir}")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Handle ADR supersession workflow"
    )
    parser.add_argument(
        "--old",
        type=int,
        required=True,
        help="Number of ADR being superseded (e.g., 5)"
    )
    parser.add_argument(
        "--new",
        type=int,
        required=True,
        help="Number of new ADR (e.g., 12)"
    )
    parser.add_argument(
        "--dir", "-d",
        required=True,
        help="ADR directory path"
    )

    args = parser.parse_args()

    adr_dir = Path(args.dir)
    if not adr_dir.is_absolute():
        adr_dir = Path.cwd() / adr_dir

    if not adr_dir.exists():
        print(f"Error: Directory does not exist: {adr_dir}")
        return 1

    success = supersede_adr(adr_dir, args.old, args.new)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
