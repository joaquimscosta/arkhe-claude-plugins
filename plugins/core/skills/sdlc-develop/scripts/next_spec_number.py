#!/usr/bin/env python3
"""
Compute the next spec sequence number for the sdlc-develop skill.

Scans {specs_dir}/ for directories matching NNN-* or NN-* patterns,
finds the highest numeric prefix, and returns the next number
zero-padded to 3 digits.

Usage:
    python3 next_spec_number.py --specs-dir arkhe/specs
    python3 next_spec_number.py --specs-dir arkhe/specs --format plain
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Matches directories starting with one or more digits followed by a hyphen
PREFIX_PATTERN = re.compile(r'^(\d+)-')


def get_next_spec_number(specs_dir: Path) -> dict:
    """Scan existing spec directories and return next available number."""
    max_number = 0
    total_dirs = 0

    if specs_dir.is_dir():
        for entry in specs_dir.iterdir():
            if entry.is_dir():
                match = PREFIX_PATTERN.match(entry.name)
                if match:
                    number = int(match.group(1))
                    max_number = max(max_number, number)
                    total_dirs += 1

    next_number = max_number + 1
    return {
        "next_number": next_number,
        "prefix": f"{next_number:03d}",
        "highest_existing": max_number,
        "total_dirs": total_dirs,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compute next spec sequence number"
    )
    parser.add_argument(
        "--specs-dir",
        required=True,
        help="Path to the specs directory (e.g., arkhe/specs)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "plain"],
        default="json",
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    specs_dir = Path(args.specs_dir).resolve()

    if specs_dir.exists() and not specs_dir.is_dir():
        print(
            json.dumps({"error": f"Path exists but is not a directory: {specs_dir}"}),
            file=sys.stderr,
        )
        sys.exit(1)

    result = get_next_spec_number(specs_dir)

    if args.format == "plain":
        print(result["prefix"])
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
