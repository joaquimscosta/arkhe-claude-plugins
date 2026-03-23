#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Add a new area to an existing Johnny.Decimal documentation structure.

Usage:
    uv run jd_add_area.py --prefix 40 --name operations
    uv run jd_add_area.py --prefix 40 --name operations --description "Deployment, monitoring, runbooks"
    uv run jd_add_area.py --prefix 40 --name operations --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    AREA_DESCRIPTIONS,
    AREA_NAME_PATTERN,
    DEFAULT_CONFIG,
    find_area_by_prefix,
    find_git_root,
    resolve_config,
)
from jd_index import re_index


def validate_prefix(prefix: str) -> tuple[bool, str | None]:
    """Validate prefix is two digits and a multiple of 10."""
    if not re.match(r"^[0-9]{2}$", prefix):
        return False, f"Prefix must be exactly two digits, got '{prefix}'"
    num = int(prefix)
    if num % 10 != 0:
        return False, f"Prefix '{prefix}' is not a multiple of 10 (convention: 00, 10, 20, ..., 90)"
    return True, None


def validate_name(name: str) -> tuple[bool, str | None]:
    """Validate area name is kebab-case."""
    test_name = f"00-{name}"
    if not AREA_NAME_PATTERN.match(test_name):
        return False, f"Name '{name}' is not valid kebab-case (lowercase letters, numbers, hyphens)"
    return True, None


def check_prefix_available(
    prefix: str,
    docs_dir: Path,
    config: dict,
) -> tuple[bool, str | None]:
    """Check if prefix is not already taken in config or on disk."""
    # Check config
    areas = config.get("areas", {})
    if prefix in areas:
        return False, f"Prefix '{prefix}' already in config as '{prefix}-{areas[prefix]}'"

    # Check on disk
    existing = find_area_by_prefix(docs_dir, prefix)
    if existing:
        return False, f"Prefix '{prefix}' already exists on disk as '{existing.name}'"

    return True, None


def create_area(
    docs_dir: Path,
    prefix: str,
    name: str,
    description: str,
    dry_run: bool,
) -> list[Path]:
    """Create area directory and README stub. Returns created paths."""
    created: list[Path] = []
    area_dir = docs_dir / f"{prefix}-{name}"

    if area_dir.exists():
        print(f"  Exists (skip): {area_dir}/")
        return created

    if dry_run:
        print(f"  Would create: {area_dir}/")
    else:
        area_dir.mkdir(parents=True, exist_ok=True)
    created.append(area_dir)

    # Create README stub
    readme_path = area_dir / "README.md"
    title = name.replace("-", " ").title()
    desc = description or AREA_DESCRIPTIONS.get(prefix, f"Documentation for {title.lower()}")

    content = f"""# {prefix} — {title}

{desc}.

## Documents

_No documents yet._
"""
    if dry_run:
        print(f"  Would create: {readme_path}")
    else:
        readme_path.write_text(content)
    created.append(readme_path)

    return created


def update_config_areas(
    config_path: Path,
    prefix: str,
    name: str,
    dry_run: bool,
) -> bool:
    """Add new area to .jd-config.json. Create config if missing."""
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = dict(DEFAULT_CONFIG)

    areas = config.get("areas", {})
    areas[prefix] = name
    # Sort areas by prefix
    config["areas"] = dict(sorted(areas.items()))

    if dry_run:
        action = "Would update" if config_path.exists() else "Would create"
        print(f"  {action}: {config_path}")
        print(f"    + \"{prefix}\": \"{name}\"")
    else:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
            f.write("\n")
        action = "Updated" if config_path.exists() else "Created"
        print(f"  {action}: {config_path}")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add a new area to a Johnny.Decimal documentation structure"
    )
    parser.add_argument(
        "--prefix",
        "-p",
        required=True,
        help="Two-digit area prefix (e.g., '40')",
    )
    parser.add_argument(
        "--name",
        "-n",
        required=True,
        help="Area name in kebab-case (e.g., 'operations')",
    )
    parser.add_argument(
        "--description",
        "-D",
        default=None,
        help="Purpose description for README stub",
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
        help="Show what would be created without writing",
    )

    args = parser.parse_args()
    base_path = Path.cwd()

    # Validate inputs
    valid, err = validate_prefix(args.prefix)
    if not valid:
        print(f"Error: {err}")
        return 1

    valid, err = validate_name(args.name)
    if not valid:
        print(f"Error: {err}")
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
        print("Run jd_init.py first to create the structure.")
        return 1

    # Check availability
    valid, err = check_prefix_available(args.prefix, docs_dir, config)
    if not valid:
        print(f"Error: {err}")
        return 1

    # Execute
    mode = "(dry-run)" if args.dry_run else ""
    print(f"Adding area {args.prefix}-{args.name} {mode}")
    print()

    # Create directory and README
    created = create_area(
        docs_dir, args.prefix, args.name,
        args.description or "", args.dry_run,
    )

    # Update config
    git_root = find_git_root(base_path)
    config_path = (git_root or base_path) / ".jd-config.json"
    if args.config:
        config_path = Path(args.config)
        if not config_path.is_absolute():
            config_path = base_path / config_path

    print()
    update_config_areas(config_path, args.prefix, args.name, args.dry_run)

    # Re-index
    print()
    print("Re-indexing...")
    # Reload config after update
    if not args.dry_run:
        config = resolve_config(str(config_path) if config_path.exists() else None, base_path)
    re_index(docs_dir, config, args.dry_run)

    if created:
        print(f"\n{'Would create' if args.dry_run else 'Created'}: {len(created)} items")

    return 0


if __name__ == "__main__":
    sys.exit(main())
