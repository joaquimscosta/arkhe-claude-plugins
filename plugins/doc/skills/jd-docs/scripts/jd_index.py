#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Generate or update a README.md index for a Johnny.Decimal docs directory.

Usage:
    uv run jd_index.py --dir docs
    uv run jd_index.py --dir docs --format tree
    uv run jd_index.py --dir docs --dry-run
"""

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

START_MARKER = "<!-- JD:INDEX:START -->"
END_MARKER = "<!-- JD:INDEX:END -->"

# Default area descriptions for index
AREA_DESCRIPTIONS: dict[str, str] = {
    "00": "Onboarding, setup, quick start, MVP",
    "10": "Specs, features, roadmap, design",
    "20": "Tech decisions, system design",
    "30": "Research, spikes, investigations",
    "90": "Historical/deprecated docs",
}

DEFAULT_CONFIG = {
    "version": 1,
    "root": "docs",
    "areas": {
        "00": "getting-started",
        "10": "product",
        "20": "architecture",
        "30": "research",
        "90": "archive",
    },
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
    """Check if a name matches any ignore pattern."""
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(name.lower(), pattern.lower()):
            return True
    return False


def parse_doc_title(filepath: Path) -> str:
    """Extract the first heading from a markdown file."""
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    # Remove the # prefix and any leading numbering
                    title = line[2:].strip()
                    # Remove common prefixes like "00 —" or "ADR-0001:"
                    title = re.sub(r"^[0-9]{2,4}\s*[-—:]\s*", "", title)
                    return title
    except (OSError, UnicodeDecodeError):
        pass
    # Fallback: derive from filename
    name = filepath.stem.replace("-", " ").replace("_", " ").title()
    return name


def scan_areas(docs_dir: Path, ignore: list[str]) -> list[dict]:
    """Scan all J.D area directories and their contents."""
    areas = []

    for item in sorted(docs_dir.iterdir()):
        if not item.is_dir():
            continue
        if is_ignored(item.name, ignore):
            continue
        if not re.match(r"^[0-9]{2}-", item.name):
            continue

        prefix = item.name[:2]
        name = item.name[3:]  # After "NN-"

        # Collect documents and subdirectories in a single pass
        entries = list(item.iterdir())
        docs = []
        for doc in sorted(e for e in entries if e.is_file()):
            if doc.suffix.lower() == ".md" and doc.name.lower() != "readme.md":
                if not is_ignored(doc.name, ignore):
                    title = parse_doc_title(doc)
                    docs.append({
                        "path": doc,
                        "name": doc.name,
                        "title": title,
                    })

        subdirs = [d for d in entries if d.is_dir() and not is_ignored(d.name, ignore)]

        desc = AREA_DESCRIPTIONS.get(prefix, "")

        areas.append({
            "prefix": prefix,
            "name": name,
            "folder": item.name,
            "path": item,
            "docs": docs,
            "subdirs": subdirs,
            "description": desc,
            "doc_count": len(docs),
        })

    return areas


def generate_table_index(areas: list[dict], docs_dir: Path) -> str:
    """Generate a table-format index."""
    lines = [
        "| Prefix | Area | Docs | Description |",
        "|--------|------|------|-------------|",
    ]

    for area in areas:
        folder = area["folder"]
        desc = area["description"]
        count = area["doc_count"]
        count_str = f"{count} doc{'s' if count != 1 else ''}" if count > 0 else "—"
        lines.append(f"| `{area['prefix']}-` | [`{folder}/`](./{folder}/) | {count_str} | {desc} |")

    return "\n".join(lines)


def generate_tree_index(areas: list[dict], docs_dir: Path) -> str:
    """Generate a tree-format index with document listings."""
    lines = []

    for area in areas:
        folder = area["folder"]
        desc = area["description"]
        title = area["name"].replace("-", " ").title()
        lines.append(f"- **[`{folder}/`](./{folder}/)** — {desc or title}")

        for doc in area["docs"]:
            rel_path = f"./{folder}/{doc['name']}"
            lines.append(f"  - [{doc['title']}]({rel_path})")

        if area["subdirs"]:
            for subdir in area["subdirs"]:
                lines.append(f"  - `{subdir.name}/` (directory)")

    return "\n".join(lines)


def update_readme(
    docs_dir: Path,
    index_content: str,
    dry_run: bool,
) -> bool:
    """Update README.md with the generated index.

    Uses marker comments to preserve custom content.
    Returns True if changes were made.
    """
    readme_path = docs_dir / "README.md"

    if not readme_path.exists():
        # Generate minimal README with index
        content = f"""# Documentation

## Documentation Index

{START_MARKER}

{index_content}

{END_MARKER}
"""
        if dry_run:
            print(f"Would create: {readme_path}")
            print()
            print(content)
        else:
            readme_path.write_text(content)
            print(f"Created: {readme_path}")
        return True

    # Read existing README
    existing = readme_path.read_text()

    # Check for markers
    if START_MARKER in existing and END_MARKER in existing:
        # Replace content between markers
        pattern = re.compile(
            rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
            re.DOTALL,
        )
        new_content = f"{START_MARKER}\n\n{index_content}\n\n{END_MARKER}"
        updated = pattern.sub(new_content, existing, count=1)

        if updated == existing:
            print("Index is already up to date.")
            return False

        if dry_run:
            print(f"Would update: {readme_path}")
            print()
            print(f"--- Index content ---")
            print(index_content)
            print(f"--- End ---")
        else:
            readme_path.write_text(updated)
            print(f"Updated: {readme_path}")
        return True
    else:
        # No markers found — append index with markers
        section = f"""
{START_MARKER}

{index_content}

{END_MARKER}
"""
        if dry_run:
            print(f"Would append index to: {readme_path}")
            print("(No markers found — adding markers and index)")
            print()
            print(f"--- Index content ---")
            print(index_content)
            print(f"--- End ---")
        else:
            with open(readme_path, "a") as f:
                f.write(section)
            print(f"Appended index to: {readme_path}")
            print("Tip: Move the index markers to the desired position in your README")
        return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or update a README.md index for Johnny.Decimal docs"
    )
    parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Docs directory to index",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["table", "tree"],
        default=None,
        help="Index format (default: from config or 'table')",
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
        help="Print index without writing",
    )

    args = parser.parse_args()

    # Resolve directory
    docs_dir = Path(args.dir)
    if not docs_dir.is_absolute():
        docs_dir = Path.cwd() / docs_dir

    if not docs_dir.exists():
        print(f"Error: Directory does not exist: {docs_dir}")
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
            config = dict(DEFAULT_CONFIG)
    else:
        config = load_config(Path.cwd())

    ignore = config.get("ignore", ["adr", "*.pdf"])
    fmt = args.format or config.get("readme_format", "table")

    # Scan areas
    areas = scan_areas(docs_dir, ignore)

    if not areas:
        print(f"No J.D areas found in: {docs_dir}")
        print("Expected directories matching NN-name pattern (e.g., 00-getting-started/)")
        return 1

    print(f"Scanning: {docs_dir}")
    print(f"Format: {fmt}")
    print(f"Areas found: {len(areas)}")
    total_docs = sum(a["doc_count"] for a in areas)
    print(f"Total documents: {total_docs}")
    print()

    # Generate index
    if fmt == "tree":
        index_content = generate_tree_index(areas, docs_dir)
    else:
        index_content = generate_table_index(areas, docs_dir)

    # Update README
    try:
        update_readme(docs_dir, index_content, args.dry_run)
    except OSError as e:
        print(f"Error writing README: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
