#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Validate a Johnny.Decimal documentation structure.

Usage:
    uv run jd_validate.py --dir docs
    uv run jd_validate.py --dir docs/skrebe --strict
    uv run jd_validate.py --dir docs --config .jd-config.json
"""

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

# Pattern for valid J.D area directory names: NN-kebab-case
AREA_NAME_PATTERN = re.compile(r"^[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")

# Default area scheme for comparison
DEFAULT_AREAS: dict[str, str] = {
    "00": "getting-started",
    "10": "product",
    "20": "architecture",
    "30": "research",
    "90": "archive",
}

# Files that are expected at the docs root (not orphans)
ROOT_ALLOWED_FILES = {
    "readme.md",
    "glossary.md",
    ".jd-config.json",
    ".ds_store",
}

DEFAULT_CONFIG = {
    "version": 1,
    "root": "docs",
    "areas": DEFAULT_AREAS,
    "products": [],
    "ignore": ["adr", "*.pdf"],
    "readme_format": "table",
}


def find_git_root(start: Path) -> Path | None:
    """Walk up from start to find the git repository root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=start,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except FileNotFoundError:
        pass
    return None


def load_config(base_path: Path) -> dict:
    """Find .jd-config.json walking up to git root, or return defaults."""
    current = base_path.resolve()
    git_root = find_git_root(current)
    stop_at = git_root or current

    while True:
        config_path = current / ".jd-config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config

        if current == stop_at or current == current.parent:
            break
        current = current.parent

    return dict(DEFAULT_CONFIG)


def is_ignored(name: str, ignore_patterns: list[str]) -> bool:
    """Check if a directory or file name matches any ignore pattern."""
    return any(
        fnmatch.fnmatch(name, p) or fnmatch.fnmatch(name.lower(), p.lower())
        for p in ignore_patterns
    )


def find_areas(docs_dir: Path, ignore: list[str]) -> list[Path]:
    """Find all NN-* directories in the docs root."""
    areas = []
    for item in sorted(docs_dir.iterdir()):
        if item.is_dir() and not is_ignored(item.name, ignore):
            if re.match(r"^[0-9]{2}-", item.name):
                areas.append(item)
    return areas


def validate_directory_name(name: str) -> tuple[bool, str | None]:
    """Check if a directory name matches the J.D convention.

    Returns:
        tuple: (is_valid, error_message or None)
    """
    if not AREA_NAME_PATTERN.match(name):
        return False, f"'{name}' does not match NN-kebab-case pattern"
    return True, None


def check_numbering(areas: list[Path]) -> list[str]:
    """Check area prefix numbering conventions.

    Returns list of warning messages.
    """
    warnings = []
    for area in areas:
        prefix = area.name[:2]
        try:
            num = int(prefix)
            if num % 10 != 0 and num < 90:
                warnings.append(
                    f"Area prefix '{prefix}' is not a multiple of 10 "
                    f"(convention: 00, 10, 20, ..., 90)"
                )
        except ValueError:
            pass  # Invalid prefix caught by validate_directory_name
    return warnings


def check_orphan_files(
    docs_dir: Path,
    ignore: list[str],
) -> list[Path]:
    """Find markdown files in docs root that should be in an area."""
    orphans = []
    for item in docs_dir.iterdir():
        if item.is_file() and not is_ignored(item.name, ignore):
            if item.name.lower() not in ROOT_ALLOWED_FILES:
                if item.suffix.lower() == ".md":
                    orphans.append(item)
    return orphans


def check_readme_presence(areas: list[Path]) -> list[Path]:
    """Find area directories missing README.md."""
    missing = []
    for area in areas:
        readme = area / "README.md"
        if not readme.exists():
            missing.append(area)
    return missing


def check_missing_standard_areas(
    areas: list[Path],
    expected_areas: dict[str, str],
) -> list[str]:
    """Report standard areas that are missing."""
    found_prefixes = {a.name[:2] for a in areas}
    missing = []
    for prefix, name in sorted(expected_areas.items()):
        if prefix not in found_prefixes:
            missing.append(f"{prefix}-{name}")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Johnny.Decimal documentation structure"
    )
    parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Docs directory to validate",
    )
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Path to .jd-config.json (auto-detected if not specified)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit code 1)",
    )

    args = parser.parse_args()

    # Resolve directory
    docs_dir = Path(args.dir)
    if not docs_dir.is_absolute():
        docs_dir = Path.cwd() / docs_dir

    if not docs_dir.exists():
        print(f"Error: Directory does not exist: {docs_dir}")
        return 1

    if not docs_dir.is_dir():
        print(f"Error: Not a directory: {docs_dir}")
        return 1

    # Load config
    if args.config:
        config_path = Path(args.config)
        if not config_path.is_absolute():
            config_path = Path.cwd() / config_path
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
        else:
            print(f"Warning: Config not found: {config_path}, using defaults")
            config = dict(DEFAULT_CONFIG)
    else:
        config = load_config(Path.cwd())

    expected_areas = config.get("areas", DEFAULT_AREAS)
    ignore = config.get("ignore", ["adr", "*.pdf"])

    # Run checks
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    # Find areas
    areas = find_areas(docs_dir, ignore)

    # Check root README
    root_readme = docs_dir / "README.md"
    if not root_readme.exists():
        warnings.append("Missing README.md in docs root")

    # Validate area names
    for area in areas:
        valid, msg = validate_directory_name(area.name)
        if not valid:
            errors.append(f"Invalid area name: {msg}")

    # Check numbering conventions
    numbering_warnings = check_numbering(areas)
    warnings.extend(numbering_warnings)

    # Check orphan files
    orphans = check_orphan_files(docs_dir, ignore)
    for orphan in orphans:
        warnings.append(f"Orphan file: {orphan.name}")

    # Check README presence in areas
    missing_readme = check_readme_presence(areas)
    for area in missing_readme:
        warnings.append(f"Missing README.md in {area.name}/")

    # Check missing standard areas
    missing_areas = check_missing_standard_areas(areas, expected_areas)
    for area_name in missing_areas:
        info.append(f"Standard area not present: {area_name}/")

    # Print report
    print("Johnny.Decimal Validation Report")
    print("=" * 40)
    print(f"Directory: {docs_dir}")
    print()

    # Areas found
    print(f"Areas found: {len(areas)}")
    for area in areas:
        valid, _ = validate_directory_name(area.name)
        mark = "+" if valid else "x"
        print(f"  {mark} {area.name}")
    print()

    # Errors
    if errors:
        print(f"Errors: {len(errors)}")
        for err in errors:
            print(f"  x {err}")
        print()

    # Warnings
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for warn in warnings:
            print(f"  ! {warn}")
        print()

    # Info
    if info:
        print(f"Info: {len(info)}")
        for inf in info:
            print(f"  - {inf}")
        print()

    # Result
    if errors:
        result = "FAIL"
    elif warnings and args.strict:
        result = "FAIL (strict mode)"
    else:
        result = "PASS"

    print(f"Result: {result} ({len(areas)} areas, {len(errors)} errors, {len(warnings)} warnings)")

    if errors or (warnings and args.strict):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
