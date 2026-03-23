#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Scaffold a Diataxis documentation structure.

Creates a folder layout with README templates for each Diataxis quadrant,
or a flat layout with a hub README and config file.

Usage:
    uv run diataxis_scaffold.py --dry-run              # Preview
    uv run diataxis_scaffold.py                         # Folders layout
    uv run diataxis_scaffold.py --layout flat           # Flat layout
    uv run diataxis_scaffold.py --root docs --init-config
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    DEFAULT_CONFIG,
    QUADRANTS,
    find_git_root,
    resolve_config,
)


# ---------------------------------------------------------------------------
# README templates
# ---------------------------------------------------------------------------

def generate_hub_readme(project_name: str, layout: str) -> str:
    """Generate the docs root README.md content."""
    lines = [
        f"# {project_name} Documentation",
        "",
        "Documentation organized using the [Diataxis](https://diataxis.fr/) framework.",
        "",
        "## Documentation Map",
        "",
        "| Quadrant | Purpose | Directory |",
        "|----------|---------|-----------|",
    ]

    for quadrant, meta in QUADRANTS.items():
        folder = meta["folder"]
        desc = meta["description"]
        if layout == "folders":
            lines.append(f"| {quadrant.capitalize()} | {desc} | [`{folder}/`](./{folder}/) |")
        else:
            lines.append(f"| {quadrant.capitalize()} | {desc} | _(flat layout)_ |")

    lines.extend([
        "",
        "## Quick Start",
        "",
        "- **New user?** Start with the [tutorials](./tutorials/)",
        "- **Need to do something?** Check the [how-to guides](./how-to/)",
        "- **Looking up details?** See the [reference](./reference/)",
        "- **Want to understand why?** Read the [explanations](./explanation/)",
        "",
    ])

    return "\n".join(lines)


def generate_quadrant_readme(quadrant: str) -> str:
    """Generate a per-quadrant README.md content."""
    meta = QUADRANTS[quadrant]
    title = quadrant.replace("-", " ").title()

    guidelines: dict[str, str] = {
        "tutorial": (
            "**What makes a good tutorial:**\n"
            "- Has a clear learning goal\n"
            "- Provides a complete, working example\n"
            "- Includes all prerequisites\n"
            "- Takes the reader step-by-step\n"
            "- Avoids unnecessary explanation (link to Explanation docs instead)\n"
            "- Ensures the reader succeeds"
        ),
        "how-to": (
            "**What makes a good how-to guide:**\n"
            "- Addresses a specific, real-world problem\n"
            "- Assumes the reader is competent\n"
            "- Jumps straight to the steps\n"
            "- Provides the solution, not the theory\n"
            "- Has a clear title: 'How to...'"
        ),
        "reference": (
            "**What makes good reference documentation:**\n"
            "- Is complete and accurate\n"
            "- Uses tables for parameters, options, and endpoints\n"
            "- Maintains a neutral, factual tone\n"
            "- Mirrors the structure of the codebase\n"
            "- Is kept up-to-date with code changes"
        ),
        "explanation": (
            "**What makes a good explanation:**\n"
            "- Provides context and background\n"
            "- Explains 'why' decisions were made\n"
            "- Uses narrative prose, not lists\n"
            "- Discusses alternatives and tradeoffs\n"
            "- Can be read during study time (not while coding)"
        ),
    }

    return f"""# {title}s

{meta['description']}.

{guidelines.get(quadrant, '')}

## Documents

_No documents yet._
"""


# ---------------------------------------------------------------------------
# Scaffold logic
# ---------------------------------------------------------------------------

def scaffold_folders(
    root: Path,
    project_name: str,
    dry_run: bool,
) -> list[Path]:
    """Create Diataxis folder structure with README templates."""
    created: list[Path] = []

    # Create root directory
    if not root.exists():
        if dry_run:
            print(f"  Would create: {root}/")
        else:
            root.mkdir(parents=True, exist_ok=True)
        created.append(root)

    # Create hub README
    readme_path = root / "README.md"
    if not readme_path.exists():
        content = generate_hub_readme(project_name, "folders")
        if dry_run:
            print(f"  Would create: {readme_path}")
        else:
            readme_path.write_text(content)
        created.append(readme_path)
    else:
        print(f"  Exists (skip): {readme_path}")

    # Create quadrant directories
    for quadrant, meta in QUADRANTS.items():
        folder = meta["folder"]
        quad_dir = root / folder

        if not quad_dir.exists():
            if dry_run:
                print(f"  Would create: {quad_dir}/")
            else:
                quad_dir.mkdir(parents=True, exist_ok=True)
            created.append(quad_dir)

        quad_readme = quad_dir / "README.md"
        if not quad_readme.exists():
            content = generate_quadrant_readme(quadrant)
            if dry_run:
                print(f"  Would create: {quad_readme}")
            else:
                quad_readme.write_text(content)
            created.append(quad_readme)
        else:
            print(f"  Exists (skip): {quad_readme}")

    return created


def scaffold_flat(
    root: Path,
    project_name: str,
    dry_run: bool,
) -> list[Path]:
    """Create flat Diataxis layout with hub README only."""
    created: list[Path] = []

    # Create root directory
    if not root.exists():
        if dry_run:
            print(f"  Would create: {root}/")
        else:
            root.mkdir(parents=True, exist_ok=True)
        created.append(root)

    # Create hub README
    readme_path = root / "README.md"
    if not readme_path.exists():
        content = generate_hub_readme(project_name, "flat")
        if dry_run:
            print(f"  Would create: {readme_path}")
        else:
            readme_path.write_text(content)
        created.append(readme_path)
    else:
        print(f"  Exists (skip): {readme_path}")

    return created


def create_config(base_path: Path, layout: str, root: str, dry_run: bool) -> Path | None:
    """Write .diataxis-config.json with defaults."""
    config_path = base_path / ".diataxis-config.json"

    if config_path.exists():
        print(f"  Exists (skip): {config_path}")
        return None

    config = dict(DEFAULT_CONFIG)
    config["layout"] = layout
    config["root"] = root

    if dry_run:
        print(f"  Would create: {config_path}")
        return config_path

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    return config_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a Diataxis documentation structure"
    )
    parser.add_argument(
        "--root",
        "-r",
        default=None,
        help="Docs root directory (default: from config or 'docs')",
    )
    parser.add_argument(
        "--layout",
        "-l",
        choices=["folders", "flat"],
        default=None,
        help="Layout type (default: from config or 'folders')",
    )
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Path to .diataxis-config.json",
    )
    parser.add_argument(
        "--init-config",
        action="store_true",
        help="Create .diataxis-config.json with defaults",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing",
    )

    args = parser.parse_args()
    base_path = Path.cwd()
    config = resolve_config(args.config, base_path)

    # Determine layout
    layout = args.layout or config.get("layout", "folders")

    # Determine root directory
    if args.root:
        root = Path(args.root)
        if not root.is_absolute():
            root = base_path / root
        root_rel = args.root
    else:
        root_rel = config.get("root", "docs")
        root = base_path / root_rel

    # Derive project name
    git_root = find_git_root(base_path)
    project_name = (git_root or base_path).name.replace("-", " ").replace("_", " ").title()

    # Optionally create config file
    if args.init_config:
        config_target = git_root or base_path
        if args.dry_run:
            print("Config:")
        create_config(config_target, layout, root_rel, args.dry_run)
        if args.dry_run:
            print()

    # Scaffold
    mode = "(dry-run)" if args.dry_run else ""
    print(f"Scaffolding Diataxis structure at: {root}/ [{layout}] {mode}")
    print()

    if layout == "folders":
        created = scaffold_folders(root, project_name, args.dry_run)
    else:
        created = scaffold_flat(root, project_name, args.dry_run)

    if not created:
        print("\nNothing to create — structure already exists.")
    else:
        print(f"\n{'Would create' if args.dry_run else 'Created'}: {len(created)} items")

    if not args.dry_run and created:
        print(f"\nNext steps:")
        print(f"  1. Add documentation to each quadrant directory")
        print(f"  2. Run: uv run diataxis_audit.py --dir {root} to check coverage")
        print(f"  3. Run: uv run diataxis_validate.py --dir {root} to check purity")

    return 0


if __name__ == "__main__":
    sys.exit(main())
