#!/usr/bin/env python3
"""
CLAUDE.md Drift Checker

Parses CLAUDE.md structural claims (plugin counts, component inventories,
versions, file paths) and compares them against filesystem ground truth.

Uses only standard library (no external dependencies). Python 3.8+.

Usage:
    python3 claude_md_checker.py <project_root>

Output:
    JSON with findings grouped by category and summary.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import extract_frontmatter, read_file_safe, read_json_safe


# ---------------------------------------------------------------------------
# Plugin name normalization
# ---------------------------------------------------------------------------

# Edge cases where lower().replace(" ", "-") doesn't match directory name
_NAME_OVERRIDES: Dict[str, str] = {
    "google stitch": "google-stitch",
    "design intent": "design-intent",
    "spring boot": "spring-boot",
}


def _normalize_plugin_name(heading: str) -> str:
    """Convert heading text to plugin directory name.

    'Core' -> 'core', 'Design Intent' -> 'design-intent'.
    """
    lower = heading.strip().lower()
    return _NAME_OVERRIDES.get(lower, lower.replace(" ", "-"))


# ---------------------------------------------------------------------------
# Ground truth collection
# ---------------------------------------------------------------------------

def _scan_marketplace(project_root: Path) -> List[str]:
    """Get plugin names from marketplace.json."""
    mp = read_json_safe(project_root / ".claude-plugin" / "marketplace.json")
    if not mp or "plugins" not in mp:
        return []
    return [p.get("name", "") for p in mp["plugins"] if p.get("name")]


def _scan_plugin_versions(project_root: Path) -> Dict[str, str]:
    """Get actual versions from each plugin's plugin.json."""
    versions: Dict[str, str] = {}
    plugins_dir = project_root / "plugins"
    if not plugins_dir.is_dir():
        return versions

    for entry in sorted(plugins_dir.iterdir()):
        pj = entry / ".claude-plugin" / "plugin.json"
        data = read_json_safe(pj)
        if data and "version" in data:
            versions[entry.name] = data["version"]
    return versions


def _scan_plugin_agents(project_root: Path) -> Dict[str, List[str]]:
    """Get agent names from each plugin's agents/ directory."""
    result: Dict[str, List[str]] = {}
    plugins_dir = project_root / "plugins"
    if not plugins_dir.is_dir():
        return result

    for entry in sorted(plugins_dir.iterdir()):
        agents_dir = entry / "agents"
        if not agents_dir.is_dir():
            continue
        names = []
        for md in sorted(agents_dir.glob("*.md")):
            content = read_file_safe(md)
            if content:
                fm = extract_frontmatter(content)
                name = fm.get("name") if fm else None
                names.append(name or md.stem)
            else:
                names.append(md.stem)
        if names:
            result[entry.name] = names
    return result


def _scan_plugin_commands(project_root: Path) -> Dict[str, List[str]]:
    """Get command names from each plugin's commands/ directory."""
    result: Dict[str, List[str]] = {}
    plugins_dir = project_root / "plugins"
    if not plugins_dir.is_dir():
        return result

    for entry in sorted(plugins_dir.iterdir()):
        cmds_dir = entry / "commands"
        if not cmds_dir.is_dir():
            continue
        names = [md.stem for md in sorted(cmds_dir.glob("*.md"))]
        if names:
            result[entry.name] = names
    return result


def _scan_plugin_skills(project_root: Path) -> Dict[str, List[str]]:
    """Get skill names from each plugin's skills/ directory."""
    result: Dict[str, List[str]] = {}
    plugins_dir = project_root / "plugins"
    if not plugins_dir.is_dir():
        return result

    for entry in sorted(plugins_dir.iterdir()):
        skills_dir = entry / "skills"
        if not skills_dir.is_dir():
            continue
        names = []
        for skill_subdir in sorted(skills_dir.iterdir()):
            if not skill_subdir.is_dir():
                continue
            skill_md = skill_subdir / "SKILL.md"
            content = read_file_safe(skill_md)
            if content:
                fm = extract_frontmatter(content)
                name = fm.get("name") if fm else None
                names.append(name or skill_subdir.name)
            else:
                names.append(skill_subdir.name)
        if names:
            result[entry.name] = names
    return result


def _collect_ground_truth(project_root: Path) -> dict:
    """Collect all filesystem ground truth."""
    return {
        "marketplace_plugins": _scan_marketplace(project_root),
        "versions": _scan_plugin_versions(project_root),
        "agents": _scan_plugin_agents(project_root),
        "commands": _scan_plugin_commands(project_root),
        "skills": _scan_plugin_skills(project_root),
    }


# ---------------------------------------------------------------------------
# CLAUDE.md claim parsing
# ---------------------------------------------------------------------------

_PLUGIN_HEADING_RE = re.compile(r"^###\s+(.+?)\s+Plugin\s*$", re.MULTILINE)
_AGENTS_LINE_RE = re.compile(
    r"^\s*-\s+\*\*Agents\*\*:\s*(.+)$", re.MULTILINE
)
_COMMANDS_LINE_RE = re.compile(
    r"^\s*-\s+\*\*Commands\*\*:\s*(.+)$", re.MULTILINE
)
_SKILLS_LINE_RE = re.compile(
    r"^\s*-\s+\*\*Skills\*\*:\s*(.+)$", re.MULTILINE
)
_BACKTICK_NAME_RE = re.compile(r"`([^`]+)`")
_SLASH_CMD_RE = re.compile(r"`/([a-z][-a-z0-9]*)`")
_VERSION_LINE_RE = re.compile(
    r"Plugin versions?:\s*(.+)", re.IGNORECASE
)
_VERSION_ENTRY_RE = re.compile(r"([a-z][-a-z0-9]*)\s+(\d+\.\d+\.\d+)")


def _extract_names_from_line(line: str) -> List[str]:
    """Extract backtick-quoted names from a component line.

    Filters out flags (--deep), paths (docs/foo.md), and parenthetical hints.
    """
    names = _BACKTICK_NAME_RE.findall(line)
    return [
        n for n in names
        if not n.startswith("-") and "/" not in n and "." not in n
    ]


def _extract_commands_from_line(line: str) -> List[str]:
    """Extract /command names from a component line."""
    return _SLASH_CMD_RE.findall(line)


def _parse_plugin_sections(content: str) -> Dict[str, dict]:
    """Parse all ### {Name} Plugin sections from CLAUDE.md.

    Only parses sections within the '## Available Plugins' area to avoid
    matching headings like '### Creating a New Plugin' in other sections.

    Returns dict mapping normalized plugin name to claimed components.
    """
    # Restrict to "Available Plugins" section
    avail_start = content.find("## Available Plugins")
    if avail_start == -1:
        return {}
    # Find the next ## heading after Available Plugins
    next_section = re.search(r"^## (?!Available Plugins)", content[avail_start + 1:], re.MULTILINE)
    avail_end = (avail_start + 1 + next_section.start()) if next_section else len(content)
    avail_content = content[avail_start:avail_end]

    sections: Dict[str, dict] = {}
    headings = list(_PLUGIN_HEADING_RE.finditer(avail_content))

    for i, match in enumerate(headings):
        heading_text = match.group(1)
        plugin_name = _normalize_plugin_name(heading_text)

        # Extract section text up to next heading or end
        start = match.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(avail_content)
        section_text = avail_content[start:end]

        section: dict = {"heading": heading_text, "agents": [], "commands": [], "skills": []}

        # Parse agents
        agents_match = _AGENTS_LINE_RE.search(section_text)
        if agents_match:
            section["agents"] = _extract_names_from_line(agents_match.group(1))

        # Parse commands
        cmds_match = _COMMANDS_LINE_RE.search(section_text)
        if cmds_match:
            section["commands"] = _extract_commands_from_line(cmds_match.group(1))

        # Parse skills
        skills_match = _SKILLS_LINE_RE.search(section_text)
        if skills_match:
            section["skills"] = _extract_names_from_line(skills_match.group(1))

        sections[plugin_name] = section

    return sections


def _parse_version_line(content: str) -> Dict[str, str]:
    """Parse the 'Plugin versions: core 2.1.0, ...' line."""
    match = _VERSION_LINE_RE.search(content)
    if not match:
        return {}
    return dict(_VERSION_ENTRY_RE.findall(match.group(1)))


# ---------------------------------------------------------------------------
# Drift checks
# ---------------------------------------------------------------------------

def _finding(
    category: str,
    status: str,
    severity: str,
    detail: str,
    plugin: str = "",
    claimed: str = "",
    actual: str = "",
) -> dict:
    """Create a finding dict."""
    f = {
        "category": category,
        "status": status,
        "severity": severity,
        "detail": detail,
    }
    if plugin:
        f["plugin"] = plugin
    if claimed:
        f["claimed"] = claimed
    if actual:
        f["actual"] = actual
    return f


def _check_plugin_count(
    sections: Dict[str, dict], ground_truth: dict
) -> List[dict]:
    """Check if documented plugin count matches marketplace."""
    findings = []
    claimed_count = len(sections)
    actual_count = len(ground_truth["marketplace_plugins"])

    if claimed_count != actual_count:
        findings.append(_finding(
            category="plugin_count",
            status="drift",
            severity="WARNING",
            detail=f"CLAUDE.md documents {claimed_count} plugins, marketplace has {actual_count}",
            claimed=str(claimed_count),
            actual=str(actual_count),
        ))
    else:
        findings.append(_finding(
            category="plugin_count",
            status="ok",
            severity="INFO",
            detail=f"Plugin count matches: {actual_count}",
            claimed=str(claimed_count),
            actual=str(actual_count),
        ))
    return findings


def _check_component_inventories(
    sections: Dict[str, dict], ground_truth: dict
) -> List[dict]:
    """Check agents, commands, skills per plugin."""
    findings = []

    for component_type in ("agents", "commands", "skills"):
        actual_all = ground_truth[component_type]

        for plugin_name, section in sections.items():
            claimed_names = set(section.get(component_type, []))
            actual_names = set(actual_all.get(plugin_name, []))

            # Names in CLAUDE.md but not on disk
            for name in sorted(claimed_names - actual_names):
                findings.append(_finding(
                    category=component_type,
                    status="phantom",
                    severity="CRITICAL",
                    detail=f"{component_type[:-1]} '{name}' documented but not found on disk",
                    plugin=plugin_name,
                    claimed=name,
                ))

            # Names on disk but not in CLAUDE.md
            for name in sorted(actual_names - claimed_names):
                findings.append(_finding(
                    category=component_type,
                    status="undocumented",
                    severity="CRITICAL",
                    detail=f"{component_type[:-1]} '{name}' exists on disk but not in CLAUDE.md",
                    plugin=plugin_name,
                    actual=name,
                ))

            # Matching names
            for name in sorted(claimed_names & actual_names):
                findings.append(_finding(
                    category=component_type,
                    status="ok",
                    severity="INFO",
                    detail=f"{component_type[:-1]} '{name}' matches",
                    plugin=plugin_name,
                ))

    return findings


def _check_plugin_versions(
    content: str, ground_truth: dict
) -> List[dict]:
    """Check plugin version claims against plugin.json files."""
    findings = []
    claimed_versions = _parse_version_line(content)
    actual_versions = ground_truth["versions"]

    all_plugins = set(claimed_versions) | set(actual_versions)
    for plugin in sorted(all_plugins):
        claimed = claimed_versions.get(plugin)
        actual = actual_versions.get(plugin)

        if claimed and actual:
            if claimed == actual:
                findings.append(_finding(
                    category="version",
                    status="ok",
                    severity="INFO",
                    detail=f"{plugin} version matches: {actual}",
                    plugin=plugin,
                    claimed=claimed,
                    actual=actual,
                ))
            else:
                findings.append(_finding(
                    category="version",
                    status="drift",
                    severity="WARNING",
                    detail=f"{plugin} version mismatch: CLAUDE.md says {claimed}, plugin.json says {actual}",
                    plugin=plugin,
                    claimed=claimed,
                    actual=actual,
                ))
        elif claimed and not actual:
            findings.append(_finding(
                category="version",
                status="phantom",
                severity="WARNING",
                detail=f"{plugin} version in CLAUDE.md but plugin not found",
                plugin=plugin,
                claimed=claimed,
            ))
        elif actual and not claimed:
            findings.append(_finding(
                category="version",
                status="undocumented",
                severity="WARNING",
                detail=f"{plugin} has version {actual} but not listed in CLAUDE.md versions line",
                plugin=plugin,
                actual=actual,
            ))

    return findings


def _check_file_claims(content: str, project_root: Path) -> List[dict]:
    """Check backtick-quoted file paths in CLAUDE.md exist on disk."""
    findings = []
    # Match paths that contain / and have an extension (relative file references)
    path_re = re.compile(r"`([a-zA-Z0-9_./-]+/[a-zA-Z0-9_./-]+\.\w+)`")

    for match in path_re.finditer(content):
        path_str = match.group(1)
        # Skip URLs, anchors, glob patterns
        if path_str.startswith("http") or "#" in path_str or "*" in path_str:
            continue
        # Skip slash commands and skill references
        if path_str.startswith("/plugin") or path_str.startswith("/doc:"):
            continue
        # Skip paths starting with ./ (context-dependent)
        if path_str.startswith("./"):
            continue

        target = project_root / path_str
        if target.exists():
            findings.append(_finding(
                category="file_path",
                status="ok",
                severity="INFO",
                detail=f"Path exists: {path_str}",
                claimed=path_str,
            ))
        else:
            findings.append(_finding(
                category="file_path",
                status="missing",
                severity="WARNING",
                detail=f"Path referenced in CLAUDE.md does not exist: {path_str}",
                claimed=path_str,
            ))

    return findings


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def check_claude_md(project_root: Path) -> dict:
    """Run all CLAUDE.md drift checks.

    Args:
        project_root: Path to the project root.

    Returns:
        Complete check results as a dict.
    """
    claude_md = project_root / "CLAUDE.md"
    content = read_file_safe(claude_md)

    if not content:
        return {
            "claude_md_path": "CLAUDE.md",
            "error": "CLAUDE.md not found or empty",
            "findings": [],
            "summary": {"total_checks": 0},
        }

    # Collect ground truth
    truth = _collect_ground_truth(project_root)

    # Parse CLAUDE.md claims
    sections = _parse_plugin_sections(content)

    # Run all checks
    findings: List[dict] = []
    findings.extend(_check_plugin_count(sections, truth))
    findings.extend(_check_component_inventories(sections, truth))
    findings.extend(_check_plugin_versions(content, truth))
    findings.extend(_check_file_claims(content, project_root))

    # Build summary
    status_counts: Dict[str, int] = {}
    category_counts: Dict[str, Dict[str, int]] = {}
    for f in findings:
        st = f["status"]
        cat = f["category"]
        status_counts[st] = status_counts.get(st, 0) + 1
        if cat not in category_counts:
            category_counts[cat] = {}
        category_counts[cat][st] = category_counts[cat].get(st, 0) + 1

    return {
        "claude_md_path": "CLAUDE.md",
        "findings": findings,
        "summary": {
            "total_checks": len(findings),
            **status_counts,
            "by_category": category_counts,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check CLAUDE.md claims against filesystem ground truth."
    )
    parser.add_argument(
        "project_root",
        help="Path to the project root directory",
    )

    args = parser.parse_args()
    root = Path(args.project_root).resolve()

    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = check_claude_md(root)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
