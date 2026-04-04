#!/usr/bin/env python3
"""
Detect coding-standards repository and compare project state against templates.

Outputs JSON report of standards repo location, available templates, installed
rules/configs/hooks, comparison results, and compliance score. Used by the
coding-standards skill.

Uses only standard library (no external dependencies).

Usage:
    python3 detect_standards.py [project_root] [--standards-path <path>]
"""

import argparse
import hashlib
import json
import os
import platform
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def detect_os():
    """Detect operating system for install instructions."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    return system


def file_md5(path):
    """Compute MD5 hash of file content. Returns None if file unreadable."""
    try:
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


# ---------------------------------------------------------------------------
# YAML frontmatter parser (stdlib only)
# ---------------------------------------------------------------------------

def parse_frontmatter(filepath):
    """Parse YAML frontmatter from a markdown file.

    Returns dict of key-value pairs (simple types, lists, nested maps).
    Returns None if file doesn't exist or has no frontmatter.
    """
    try:
        content = Path(filepath).read_text()
    except OSError:
        return None

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    # Find closing ---
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break

    if end is None:
        return None

    result = {}
    current_key = None
    current_indent = 0

    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level key
        if indent == 0 and ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if value.startswith("[") and value.endswith("]"):
                # Inline list: [jvm, nodejs]
                items = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
                result[key] = items
            elif value:
                result[key] = value.strip("'\"")
            else:
                # Start of nested map or list
                result[key] = {}
                current_key = key
                current_indent = indent
        elif current_key and indent > 0 and ":" in stripped:
            # Nested key-value
            nk, _, nv = stripped.partition(":")
            nk = nk.strip()
            nv = nv.strip().strip("'\"")
            if isinstance(result.get(current_key), dict):
                result[current_key][nk] = nv

    return result


# ---------------------------------------------------------------------------
# Standards repo discovery
# ---------------------------------------------------------------------------

def find_standards_repo(project_root, override_path=None):
    """Find the coding-standards repository.

    Search order:
    1. override_path argument
    2. .claude/devtools.local.md frontmatter (coding_standards_path)
    3. Walk up from project_root looking for known relative paths
    4. Check sibling directories

    Returns (path_str, source) or (None, None).
    """
    root = Path(project_root)

    # 1. Explicit override
    if override_path:
        p = Path(override_path).expanduser().resolve()
        if _is_standards_repo(p):
            return str(p), "cli_argument"

    # 2. Read from devtools.local.md
    local_md = root / ".claude" / "devtools.local.md"
    fm = parse_frontmatter(str(local_md))
    if fm and fm.get("coding_standards_path"):
        p = Path(fm["coding_standards_path"]).expanduser().resolve()
        if _is_standards_repo(p):
            return str(p), "devtools_local"

    # 3. Walk up looking for common relative paths
    search_paths = [
        "internal-repos/deznode/coding-standards",
        "coding-standards",
        "../coding-standards",
        "../../coding-standards",
    ]

    current = root
    for _ in range(5):  # Max 5 levels up
        for rel in search_paths:
            candidate = (current / rel).resolve()
            if _is_standards_repo(candidate):
                return str(candidate), "auto_discovered"
        parent = current.parent
        if parent == current:
            break
        current = parent

    # 4. Check siblings of project root
    try:
        for entry in root.parent.iterdir():
            if entry.is_dir() and entry.name == "coding-standards":
                if _is_standards_repo(entry):
                    return str(entry.resolve()), "sibling_directory"
    except OSError:
        pass

    return None, None


def _is_standards_repo(path):
    """Check if path looks like a coding-standards repo."""
    p = Path(path)
    return (
        p.is_dir()
        and (p / "templates").is_dir()
        and (p / "templates" / "claude-rules").is_dir()
    )


# ---------------------------------------------------------------------------
# Template listing
# ---------------------------------------------------------------------------

RULE_CATEGORIES = ["backend", "frontend", "infrastructure"]
CONFIG_FILES = [".editorconfig", ".prettierrc", "eslint.config.mjs", "lefthook.yml", "Taskfile.yml"]
HOOK_FILES = ["auto-lint.sh", "settings.json"]


def list_available_templates(standards_root):
    """List all template files available in the coding-standards repo."""
    root = Path(standards_root)
    result = {"claude_rules": {}, "configs": [], "claude_hooks": []}

    # Claude rules by category
    rules_dir = root / "templates" / "claude-rules"
    for category in RULE_CATEGORIES:
        cat_dir = rules_dir / category
        if cat_dir.is_dir():
            files = sorted(f.name for f in cat_dir.iterdir() if f.suffix == ".md")
            result["claude_rules"][category] = files
        else:
            result["claude_rules"][category] = []

    # Config files
    configs_dir = root / "templates" / "configs"
    if configs_dir.is_dir():
        for name in CONFIG_FILES:
            if (configs_dir / name).exists():
                result["configs"].append(name)

    # Hook files
    hooks_dir = root / "templates" / "claude-hooks"
    if hooks_dir.is_dir():
        for name in HOOK_FILES:
            if (hooks_dir / name).exists():
                result["claude_hooks"].append(name)

    return result


# ---------------------------------------------------------------------------
# Installed scanning
# ---------------------------------------------------------------------------

def scan_installed_rules(project_root):
    """Scan .claude/rules/ for installed rule files."""
    rules_dir = Path(project_root) / ".claude" / "rules"
    result = {}

    for category in RULE_CATEGORIES:
        cat_dir = rules_dir / category
        if cat_dir.is_dir():
            files = sorted(f.name for f in cat_dir.iterdir() if f.suffix == ".md")
            result[category] = files
        else:
            result[category] = []

    # Also check for files directly in .claude/rules/ (uncategorized)
    if rules_dir.is_dir():
        uncategorized = sorted(
            f.name for f in rules_dir.iterdir()
            if f.is_file() and f.suffix == ".md"
        )
        if uncategorized:
            result["uncategorized"] = uncategorized

    return result


def scan_installed_configs(project_root):
    """Check project root for known config files."""
    root = Path(project_root)
    result = {}
    for name in CONFIG_FILES:
        p = root / name
        if p.exists():
            try:
                result[name] = {"installed": True, "size_bytes": p.stat().st_size}
            except OSError:
                result[name] = {"installed": True}
        else:
            result[name] = {"installed": False}
    return result


def scan_installed_hooks(project_root):
    """Check .claude/hooks/ for known hook files."""
    hooks_dir = Path(project_root) / ".claude" / "hooks"
    result = {}
    for name in HOOK_FILES:
        p = hooks_dir / name
        if p.exists():
            info = {"installed": True}
            if name.endswith(".sh"):
                info["executable"] = os.access(str(p), os.X_OK)
            result[name] = info
        else:
            result[name] = {"installed": False}
    return result


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_templates(standards_root, project_root):
    """Compare installed files against templates using MD5 hashes.

    Returns list of comparison entries with status:
    - match: identical content
    - modified: file exists but differs
    - missing: template exists, project file doesn't
    - extra: project file exists, no template
    """
    std = Path(standards_root)
    proj = Path(project_root)
    comparisons = {"rules": [], "configs": [], "hooks": []}

    # Rules comparison
    for category in RULE_CATEGORIES:
        template_dir = std / "templates" / "claude-rules" / category
        installed_dir = proj / ".claude" / "rules" / category

        if not template_dir.is_dir():
            continue

        template_files = {f.name for f in template_dir.iterdir() if f.suffix == ".md"}
        installed_files = set()
        if installed_dir.is_dir():
            installed_files = {f.name for f in installed_dir.iterdir() if f.suffix == ".md"}

        # Check templates against installed
        for name in sorted(template_files):
            entry = {"file": f"{category}/{name}"}
            if name in installed_files:
                t_hash = file_md5(template_dir / name)
                i_hash = file_md5(installed_dir / name)
                entry["status"] = "match" if t_hash == i_hash else "modified"
                entry["template_hash"] = t_hash
                entry["installed_hash"] = i_hash
            else:
                entry["status"] = "missing"
            comparisons["rules"].append(entry)

        # Check for extra files (in project but not in template)
        for name in sorted(installed_files - template_files):
            comparisons["rules"].append({
                "file": f"{category}/{name}",
                "status": "extra",
            })

    # Configs comparison
    configs_dir = std / "templates" / "configs"
    for name in CONFIG_FILES:
        entry = {"file": name}
        template_path = configs_dir / name
        installed_path = proj / name

        if not template_path.exists():
            continue

        if installed_path.exists():
            t_hash = file_md5(template_path)
            i_hash = file_md5(installed_path)
            # Configs are expected to be customized (TODO markers replaced)
            entry["status"] = "match" if t_hash == i_hash else "modified"
            entry["template_hash"] = t_hash
            entry["installed_hash"] = i_hash
        else:
            entry["status"] = "missing"
        comparisons["configs"].append(entry)

    # Hooks comparison
    hooks_dir = std / "templates" / "claude-hooks"
    for name in HOOK_FILES:
        entry = {"file": name}
        template_path = hooks_dir / name
        installed_path = proj / ".claude" / "hooks" / name

        if not template_path.exists():
            continue

        if installed_path.exists():
            t_hash = file_md5(template_path)
            i_hash = file_md5(installed_path)
            entry["status"] = "match" if t_hash == i_hash else "modified"
            entry["template_hash"] = t_hash
            entry["installed_hash"] = i_hash
        else:
            entry["status"] = "missing"
        comparisons["hooks"].append(entry)

    return comparisons


def compute_compliance(comparison):
    """Compute compliance score from comparison results."""
    total = 0
    installed = 0
    matching = 0

    for category in ["rules", "configs", "hooks"]:
        for entry in comparison.get(category, []):
            if entry["status"] == "extra":
                continue  # Don't count extras against compliance
            total += 1
            if entry["status"] in ("match", "modified"):
                installed += 1
            if entry["status"] == "match":
                matching += 1

    score = round((installed / total) * 100) if total > 0 else 0

    rules_entries = [e for e in comparison.get("rules", []) if e["status"] != "extra"]
    configs_entries = [e for e in comparison.get("configs", []) if e["status"] != "extra"]
    hooks_entries = [e for e in comparison.get("hooks", []) if e["status"] != "extra"]

    return {
        "rules_installed": sum(1 for e in rules_entries if e["status"] in ("match", "modified")),
        "rules_total": len(rules_entries),
        "rules_matching": sum(1 for e in rules_entries if e["status"] == "match"),
        "configs_installed": sum(1 for e in configs_entries if e["status"] in ("match", "modified")),
        "configs_total": len(configs_entries),
        "configs_matching": sum(1 for e in configs_entries if e["status"] == "match"),
        "hooks_installed": sum(1 for e in hooks_entries if e["status"] in ("match", "modified")),
        "hooks_total": len(hooks_entries),
        "hooks_matching": sum(1 for e in hooks_entries if e["status"] == "match"),
        "total_installed": installed,
        "total": total,
        "total_matching": matching,
        "score_percent": score,
    }


# ---------------------------------------------------------------------------
# Ecosystem detection (simplified from detect_taskfile.py)
# ---------------------------------------------------------------------------

def detect_ecosystems(project_root):
    """Detect project ecosystems from marker files."""
    root = Path(project_root)
    ecosystems = []
    seen = set()

    # Check root and one level deep (apps/, packages/, etc.)
    dirs_to_check = [root]
    monorepo_parents = {"apps", "packages", "libs", "services", "modules"}

    try:
        for entry in sorted(root.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                dirs_to_check.append(entry)
                if entry.name in monorepo_parents:
                    try:
                        for sub in sorted(entry.iterdir()):
                            if sub.is_dir() and not sub.name.startswith("."):
                                dirs_to_check.append(sub)
                    except OSError:
                        pass
    except OSError:
        pass

    for check_dir in dirs_to_check:
        rel = str(check_dir.relative_to(root)) if check_dir != root else "."

        # JVM
        for marker, tool in [
            ("build.gradle.kts", "gradle-kotlin"),
            ("build.gradle", "gradle-groovy"),
            ("pom.xml", "maven"),
        ]:
            if (check_dir / marker).exists() and ("jvm", rel) not in seen:
                ecosystems.append({"ecosystem": "jvm", "build_tool": tool, "root": rel})
                seen.add(("jvm", rel))
                break

        # Node.js
        if (check_dir / "package.json").exists() and ("node", rel) not in seen:
            ecosystems.append({"ecosystem": "node", "root": rel})
            seen.add(("node", rel))

    return ecosystems


# ---------------------------------------------------------------------------
# Main detection
# ---------------------------------------------------------------------------

def detect(project_root, standards_path_override=None):
    """Run all detection checks and return structured results."""
    root = Path(project_root)

    # Find standards repo
    std_path, std_source = find_standards_repo(str(root), standards_path_override)

    standards_repo = {
        "found": std_path is not None,
        "path": std_path,
        "source": std_source,
    }

    if std_path:
        available = list_available_templates(std_path)
        template_count = (
            sum(len(v) for v in available["claude_rules"].values())
            + len(available["configs"])
            + len(available["claude_hooks"])
        )
        standards_repo["template_count"] = template_count
    else:
        available = {"claude_rules": {}, "configs": [], "claude_hooks": []}

    # Read devtools.local.md
    local_md = root / ".claude" / "devtools.local.md"
    devtools_local = parse_frontmatter(str(local_md))

    # Scan installed
    installed = {
        "rules": scan_installed_rules(str(root)),
        "configs": scan_installed_configs(str(root)),
        "hooks": scan_installed_hooks(str(root)),
    }

    # Detect ecosystems
    ecosystems = detect_ecosystems(str(root))

    result = {
        "standards_repo": standards_repo,
        "devtools_local": devtools_local,
        "ecosystems": ecosystems,
        "available_templates": available,
        "installed": installed,
        "os": detect_os(),
    }

    # Comparison (only if standards repo found)
    if std_path:
        comparison = compare_templates(std_path, str(root))
        result["comparison"] = comparison
        result["compliance"] = compute_compliance(comparison)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Detect coding-standards repo and compare against project state"
    )
    parser.add_argument(
        "project_root", nargs="?", default=os.getcwd(),
        help="Path to the project root directory",
    )
    parser.add_argument(
        "--standards-path",
        help="Override path to coding-standards repository",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.is_dir():
        json.dump(
            {"error": "not_a_directory", "path": str(root)},
            sys.stdout, indent=2,
        )
        sys.exit(1)

    result = detect(str(root), standards_path_override=args.standards_path)
    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
