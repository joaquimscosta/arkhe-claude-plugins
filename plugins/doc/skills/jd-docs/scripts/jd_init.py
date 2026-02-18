#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Scaffold a Johnny.Decimal documentation structure.

Usage:
    uv run jd_init.py                          # Create docs/ with defaults
    uv run jd_init.py --root docs/skrebe       # Product sub-tree
    uv run jd_init.py --init-config            # Also create .jd-config.json
    uv run jd_init.py --dry-run                # Preview only
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Default area scheme
DEFAULT_AREAS: dict[str, str] = {
    "00": "getting-started",
    "10": "product",
    "20": "architecture",
    "30": "research",
    "90": "archive",
}

# Purpose descriptions for each default area
AREA_DESCRIPTIONS: dict[str, str] = {
    "00": "Onboarding, setup, quick start, MVP, and phase planning",
    "10": "Product specs, features, roadmap, design, and branding",
    "20": "Technical decisions, system design, and integration",
    "30": "Research notes, spikes, investigations, and reference material",
    "90": "Historical and deprecated documentation",
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
            # Merge with defaults for missing keys
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config

        if current == stop_at or current == current.parent:
            break
        current = current.parent

    return dict(DEFAULT_CONFIG)


def generate_root_readme(project_name: str, areas: dict[str, str]) -> str:
    """Generate the docs root README.md content."""
    lines = [
        f"# {project_name} Documentation",
        "",
        "[Brief project description]",
        "",
        "## Quick Start",
        "",
        "- [Getting started guide](./00-getting-started/)" if "00" in areas else None,
        "",
        "## Documentation Index",
        "",
        "<!-- JD:INDEX:START -->",
        "",
        "| Prefix | Area | Purpose |",
        "|--------|------|---------|",
    ]

    for prefix in sorted(areas.keys()):
        name = areas[prefix]
        folder = f"{prefix}-{name}"
        desc = AREA_DESCRIPTIONS.get(prefix, "")
        lines.append(f"| `{prefix}-` | [`{folder}/`](./{folder}/) | {desc} |")

    lines.extend([
        "",
        "<!-- JD:INDEX:END -->",
        "",
        "## Folder Convention",
        "",
        "Documentation uses the [Johnny.Decimal](https://johnnydecimal.com/) numbering system.",
        "Numeric prefixes ensure folders sort in a logical order:",
        "",
        "- `00-09` — Getting started and immediate work",
        "- `10-19` — Product decisions",
        "- `20-29` — Architecture and technical design",
        "- `30-39` — Research and reference material",
        "- `90-99` — Archive",
        "",
        "This convention provides consistent sorting and helps developers",
        "and LLMs quickly locate documentation.",
        "",
    ])

    # Filter empty lines from conditional content
    return "\n".join(line for line in lines if line is not None)


def generate_area_readme(prefix: str, name: str) -> str:
    """Generate a per-area README.md content."""
    title = name.replace("-", " ").title()
    desc = AREA_DESCRIPTIONS.get(prefix, f"Documentation for {title.lower()}")

    return f"""# {prefix} — {title}

{desc}.

## Documents

_No documents yet._
"""


def scaffold_structure(
    root: Path,
    areas: dict[str, str],
    project_name: str,
    dry_run: bool,
) -> list[Path]:
    """Create J.D directory structure with README stubs.

    Returns list of created paths.
    """
    created: list[Path] = []

    # Create root directory
    if not root.exists():
        if dry_run:
            print(f"  Would create: {root}/")
        else:
            root.mkdir(parents=True, exist_ok=True)
        created.append(root)

    # Create root README.md
    readme_path = root / "README.md"
    if not readme_path.exists():
        content = generate_root_readme(project_name, areas)
        if dry_run:
            print(f"  Would create: {readme_path}")
        else:
            readme_path.write_text(content)
        created.append(readme_path)
    else:
        print(f"  Exists (skip): {readme_path}")

    # Create area directories and READMEs
    for prefix in sorted(areas.keys()):
        name = areas[prefix]
        area_dir = root / f"{prefix}-{name}"

        if not area_dir.exists():
            if dry_run:
                print(f"  Would create: {area_dir}/")
            else:
                area_dir.mkdir(parents=True, exist_ok=True)
            created.append(area_dir)

        area_readme = area_dir / "README.md"
        if not area_readme.exists():
            content = generate_area_readme(prefix, name)
            if dry_run:
                print(f"  Would create: {area_readme}")
            else:
                area_readme.write_text(content)
            created.append(area_readme)
        else:
            print(f"  Exists (skip): {area_readme}")

    return created


def create_config(base_path: Path, dry_run: bool) -> Path | None:
    """Write .jd-config.json with defaults."""
    config_path = base_path / ".jd-config.json"

    if config_path.exists():
        print(f"  Exists (skip): {config_path}")
        return None

    if dry_run:
        print(f"  Would create: {config_path}")
        return config_path

    with open(config_path, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
        f.write("\n")

    return config_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a Johnny.Decimal documentation structure"
    )
    parser.add_argument(
        "--root",
        "-r",
        default=None,
        help="Docs root directory (default: from config or 'docs')",
    )
    parser.add_argument(
        "--product",
        "-p",
        default=None,
        help="Product name for sub-tree (e.g., 'skrebe')",
    )
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Path to .jd-config.json (auto-detected if not specified)",
    )
    parser.add_argument(
        "--init-config",
        action="store_true",
        help="Create .jd-config.json with defaults",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing",
    )

    args = parser.parse_args()
    base_path = Path.cwd()

    # Load config
    if args.config:
        config_path = Path(args.config)
        if not config_path.is_absolute():
            config_path = base_path / config_path
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
        else:
            print(f"Error: Config file not found: {config_path}")
            return 1
    else:
        config = load_config(base_path)

    areas = config.get("areas", DEFAULT_AREAS)

    # Determine root directory
    if args.root:
        root = Path(args.root)
        if not root.is_absolute():
            root = base_path / root
    else:
        root = base_path / config.get("root", "docs")

    # Handle product sub-tree
    if args.product:
        root = root / args.product

    # Derive project name from git root or directory
    git_root = find_git_root(base_path)
    project_name = (git_root or base_path).name.replace("-", " ").replace("_", " ").title()

    # Optionally create config file
    if args.init_config:
        config_target = git_root or base_path
        if args.dry_run:
            print("Config:")
        create_config(config_target, args.dry_run)
        if args.dry_run:
            print()

    # Scaffold
    mode = "(dry-run)" if args.dry_run else ""
    print(f"Scaffolding J.D structure at: {root}/ {mode}")
    print()

    created = scaffold_structure(root, areas, project_name, args.dry_run)

    if not created:
        print("\nNothing to create — structure already exists.")
    else:
        print(f"\n{'Would create' if args.dry_run else 'Created'}: {len(created)} items")

    if not args.dry_run and created:
        print(f"\nNext: Run jd_validate.py --dir {root} to verify the structure")

    return 0


if __name__ == "__main__":
    sys.exit(main())
