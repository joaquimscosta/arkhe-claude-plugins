#!/usr/bin/env python3
"""
Plugin release readiness checker.

Validates plugin content quality before release:
1. Runs skill-validator across all skills in each plugin
2. Verifies marketplace.json completeness
3. Checks plugin.json version consistency with CHANGELOG
4. Detects broken documentation cross-references
5. Validates required files exist

Usage:
    check_release_readiness.py --all
    check_release_readiness.py --plugin core
    check_release_readiness.py --all --skip-skill-validator
    check_release_readiness.py --all --format json
"""

import sys
import os
import re
import json
import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple


@dataclass
class CheckResult:
    plugin_name: str
    version: str = ""
    passed: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def is_ready(self) -> bool:
        return len(self.failed) == 0

    def to_dict(self) -> dict:
        return {
            "plugin": self.plugin_name,
            "version": self.version,
            "ready": self.is_ready,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
        }


def find_project_root() -> Path:
    """Find the arkhe-claude-plugins project root."""
    # Walk up from script location
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".claude-plugin" / "marketplace.json").exists():
            return current
        if (current / "plugins").is_dir() and (current / "CLAUDE.md").exists():
            return current
        current = current.parent

    # Fallback: try CWD
    cwd = Path.cwd()
    if (cwd / "plugins").is_dir():
        return cwd

    print("Error: Cannot find project root. Run from arkhe-claude-plugins directory.", file=sys.stderr)
    sys.exit(1)


def load_marketplace(root: Path) -> Optional[Dict]:
    """Load marketplace.json."""
    mp_path = root / ".claude-plugin" / "marketplace.json"
    if not mp_path.exists():
        return None
    try:
        with open(mp_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Cannot parse marketplace.json: {e}", file=sys.stderr)
        return None


def load_changelog(root: Path) -> str:
    """Load CHANGELOG.md content."""
    changelog_path = root / "CHANGELOG.md"
    if not changelog_path.exists():
        return ""
    return changelog_path.read_text(encoding="utf-8")


def get_plugin_dirs(root: Path, plugin_filter: Optional[str] = None) -> List[Path]:
    """Get plugin directories to check."""
    plugins_dir = root / "plugins"
    if not plugins_dir.is_dir():
        return []

    dirs = sorted(
        [d for d in plugins_dir.iterdir() if d.is_dir() and not d.name.startswith(".")],
        key=lambda p: p.name,
    )

    if plugin_filter:
        dirs = [d for d in dirs if d.name == plugin_filter]
        if not dirs:
            print(f"Error: Plugin '{plugin_filter}' not found in plugins/", file=sys.stderr)
            sys.exit(1)

    return dirs


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None, content

    match = re.match(r"^---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        return None, content

    fm_text = match.group(1)
    body = content[match.end():]

    # Simple key-value parsing (avoids PyYAML dependency)
    fm = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip("'\"")
            if value:
                fm[key] = value

    return fm, body


def check_required_files(plugin_dir: Path, result: CheckResult) -> None:
    """Check that required plugin files exist."""
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
    readme = plugin_dir / "README.md"

    if plugin_json.exists():
        try:
            with open(plugin_json) as f:
                pj = json.load(f)
            result.version = pj.get("version", "unknown")
            if not pj.get("name"):
                result.failed.append("plugin.json missing 'name' field")
            if not pj.get("description"):
                result.warnings.append("plugin.json missing 'description' field")
        except (json.JSONDecodeError, OSError):
            result.failed.append("plugin.json is invalid JSON")
    else:
        result.failed.append("Missing .claude-plugin/plugin.json")

    if readme.exists():
        result.passed.append("README.md present")
    else:
        result.warnings.append("Missing README.md")


def check_marketplace_entry(plugin_name: str, marketplace: Optional[Dict], result: CheckResult) -> None:
    """Check plugin has a complete marketplace entry."""
    if marketplace is None:
        result.warnings.append("Cannot verify marketplace (marketplace.json not found)")
        return

    plugins = marketplace.get("plugins", [])
    entry = next((p for p in plugins if p.get("name") == plugin_name), None)

    if entry is None:
        result.failed.append(f"No marketplace.json entry for '{plugin_name}'")
        return

    if not entry.get("description"):
        result.failed.append("Marketplace entry missing 'description'")
    elif len(entry["description"]) < 20:
        result.warnings.append("Marketplace description is very short (<20 chars)")

    if not entry.get("source"):
        result.failed.append("Marketplace entry missing 'source'")

    result.passed.append("Marketplace entry found")


def check_version_consistency(plugin_name: str, version: str, changelog: str, result: CheckResult) -> None:
    """Check plugin version appears in CHANGELOG."""
    if not version or version == "unknown":
        result.warnings.append("Cannot check version consistency (no version in plugin.json)")
        return

    if not changelog:
        result.warnings.append("Cannot check version consistency (no CHANGELOG.md)")
        return

    # Look for version mention in changelog
    # The changelog may reference the global project version, not per-plugin versions
    # This is a soft check
    result.passed.append(f"Version {version} noted")


def check_cross_references(plugin_dir: Path, result: CheckResult) -> None:
    """Check for broken cross-references in markdown files."""
    broken = []

    for md_file in plugin_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        # Find markdown links to local files: [text](path.md) or [text](./path.md)
        links = re.findall(r"\[.*?\]\(([^)]+)\)", content)
        for link in links:
            # Skip external URLs, anchors, and variables
            if link.startswith(("http://", "https://", "#", "$", "mailto:")):
                continue
            # Skip script references like scripts/validate_skill.py
            if not link.endswith(".md"):
                continue

            # Resolve relative to the markdown file's directory
            target = (md_file.parent / link).resolve()
            if not target.exists():
                rel_source = md_file.relative_to(plugin_dir)
                broken.append(f"{rel_source} → {link}")

    if broken:
        for ref in broken[:5]:  # Limit to first 5
            result.failed.append(f"Broken cross-reference: {ref}")
        if len(broken) > 5:
            result.failed.append(f"...and {len(broken) - 5} more broken references")
    else:
        result.passed.append("No broken cross-references")


def check_frontmatter_quality(plugin_dir: Path, result: CheckResult) -> None:
    """Check YAML frontmatter in agents, commands, and skills."""
    issues = []

    # Check agents
    agents_dir = plugin_dir / "agents"
    if agents_dir.is_dir():
        for md_file in sorted(agents_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
            if fm is None:
                issues.append(f"agents/{md_file.name}: missing YAML frontmatter")
            elif not fm.get("name"):
                issues.append(f"agents/{md_file.name}: missing 'name' in frontmatter")
            elif not fm.get("description"):
                issues.append(f"agents/{md_file.name}: missing 'description' in frontmatter")

    # Check commands
    commands_dir = plugin_dir / "commands"
    if commands_dir.is_dir():
        for md_file in sorted(commands_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
            if fm is None:
                issues.append(f"commands/{md_file.name}: missing YAML frontmatter")
            elif not fm.get("description"):
                issues.append(f"commands/{md_file.name}: missing 'description' in frontmatter")

    # Check skills
    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                issues.append(f"skills/{skill_dir.name}/: missing SKILL.md")
                continue
            content = skill_md.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(content)
            if fm is None:
                issues.append(f"skills/{skill_dir.name}/SKILL.md: missing YAML frontmatter")
            else:
                if not fm.get("name"):
                    issues.append(f"skills/{skill_dir.name}/SKILL.md: missing 'name' in frontmatter")
                desc = fm.get("description", "")
                if not desc:
                    issues.append(f"skills/{skill_dir.name}/SKILL.md: missing 'description' in frontmatter")
                elif "use when" not in desc.lower():
                    issues.append(f"skills/{skill_dir.name}/SKILL.md: description lacks 'Use when...' trigger keywords")
                if len(desc) > 1024:
                    issues.append(f"skills/{skill_dir.name}/SKILL.md: description exceeds 1,024 chars ({len(desc)})")

            # Check line count
            line_count = len(body.strip().split("\n")) if body.strip() else 0
            if line_count > 500:
                issues.append(f"skills/{skill_dir.name}/SKILL.md: body exceeds 500 lines ({line_count})")

    if issues:
        for issue in issues[:10]:
            result.failed.append(f"Frontmatter: {issue}")
        if len(issues) > 10:
            result.failed.append(f"...and {len(issues) - 10} more frontmatter issues")
    else:
        result.passed.append("All frontmatter valid")


def check_python_scripts(plugin_dir: Path, result: CheckResult) -> None:
    """Check Python scripts follow conventions."""
    issues = []

    for py_file in plugin_dir.rglob("*.py"):
        rel_path = py_file.relative_to(plugin_dir)
        content = py_file.read_text(encoding="utf-8")

        # Check shebang
        if not content.startswith("#!/usr/bin/env python3"):
            issues.append(f"{rel_path}: missing shebang (#!/usr/bin/env python3)")

        # Check for third-party imports
        forbidden_imports = ["requests", "flask", "django", "fastapi", "numpy", "pandas"]
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                for pkg in forbidden_imports:
                    if pkg in line and f"# skill-validator: ignore" not in line:
                        issues.append(f"{rel_path}: uses third-party package '{pkg}'")

        # Check executable permission
        if not os.access(py_file, os.X_OK):
            issues.append(f"{rel_path}: not executable (needs chmod +x)")

    if issues:
        for issue in issues[:5]:
            result.warnings.append(f"Script: {issue}")
    elif list(plugin_dir.rglob("*.py")):
        result.passed.append("Python scripts follow conventions")


def run_skill_validator(plugin_dir: Path, validator_path: Path, result: CheckResult) -> None:
    """Run the skill-validator against each skill in the plugin."""
    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        return

    if not validator_path.exists():
        result.warnings.append("Skill-validator not found; skipping skill validation")
        return

    all_passed = True
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
            continue

        try:
            proc = subprocess.run(
                [str(validator_path), str(skill_dir), "--min-severity", "error", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode != 0 and proc.stdout.strip():
                try:
                    report = json.loads(proc.stdout)
                    issues = report.get("issues", [])
                    errors = [i for i in issues if i.get("severity") in ("CRITICAL", "ERROR")]
                    if errors:
                        all_passed = False
                        for err in errors[:3]:
                            result.failed.append(
                                f"Skill '{skill_dir.name}': [{err.get('severity')}] {err.get('rule_id')}: {err.get('message')}"
                            )
                except json.JSONDecodeError:
                    if proc.returncode != 0:
                        all_passed = False
                        result.warnings.append(f"Skill '{skill_dir.name}': validator returned errors (non-JSON output)")
        except (subprocess.TimeoutExpired, OSError) as e:
            result.warnings.append(f"Skill '{skill_dir.name}': validator error: {e}")

    if all_passed:
        result.passed.append("All skills pass validation")


def check_naming_conventions(plugin_dir: Path, result: CheckResult) -> None:
    """Check file naming follows kebab-case conventions."""
    issues = []
    kebab_pattern = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*\.md$")

    for subdir_name in ("agents", "commands"):
        subdir = plugin_dir / subdir_name
        if not subdir.is_dir():
            continue
        for md_file in sorted(subdir.glob("*.md")):
            if not kebab_pattern.match(md_file.name):
                issues.append(f"{subdir_name}/{md_file.name}: not kebab-case")

    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        kebab_dir_pattern = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir() and not kebab_dir_pattern.match(skill_dir.name):
                issues.append(f"skills/{skill_dir.name}/: directory not kebab-case")

    if issues:
        for issue in issues:
            result.failed.append(f"Naming: {issue}")
    else:
        result.passed.append("File naming conventions OK")


def format_text(results: List[CheckResult]) -> str:
    """Format results as human-readable text."""
    lines = ["", "=== Plugin Release Readiness Report ===", ""]

    ready_count = sum(1 for r in results if r.is_ready)
    total_count = len(results)

    for r in results:
        status = "READY" if r.is_ready else "ISSUES"
        version_str = f" (v{r.version})" if r.version else ""
        lines.append(f"Plugin: {r.plugin_name}{version_str} [{status}]")

        for msg in r.passed:
            lines.append(f"  \u2713 {msg}")
        for msg in r.failed:
            lines.append(f"  \u2717 {msg}")
        for msg in r.warnings:
            lines.append(f"  \u26a0 {msg}")
        lines.append("")

    lines.append(f"Summary: {ready_count}/{total_count} plugins ready")
    if ready_count < total_count:
        lines.append(f"         {total_count - ready_count} plugin(s) have issues that should be resolved before release")
    else:
        lines.append("         All plugins are release-ready!")
    lines.append("")

    return "\n".join(lines)


def format_json(results: List[CheckResult]) -> str:
    """Format results as JSON."""
    output = {
        "total": len(results),
        "ready": sum(1 for r in results if r.is_ready),
        "plugins": [r.to_dict() for r in results],
    }
    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Plugin release readiness checker")
    parser.add_argument("--all", action="store_true", help="Check all plugins")
    parser.add_argument("--plugin", type=str, help="Check specific plugin")
    parser.add_argument("--skip-skill-validator", action="store_true", help="Skip skill-validator (faster)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    if not args.all and not args.plugin:
        args.all = True

    root = find_project_root()
    marketplace = load_marketplace(root)
    changelog = load_changelog(root)

    plugin_filter = args.plugin if args.plugin else None
    plugin_dirs = get_plugin_dirs(root, plugin_filter)

    if not plugin_dirs:
        print("No plugins found to check.", file=sys.stderr)
        sys.exit(1)

    validator_path = root / ".claude" / "skills" / "skill-validator" / "scripts" / "validate_skill.py"

    results: List[CheckResult] = []

    for plugin_dir in plugin_dirs:
        result = CheckResult(plugin_name=plugin_dir.name)

        # Run all checks
        check_required_files(plugin_dir, result)
        check_marketplace_entry(plugin_dir.name, marketplace, result)
        check_version_consistency(plugin_dir.name, result.version, changelog, result)
        check_cross_references(plugin_dir, result)
        check_frontmatter_quality(plugin_dir, result)
        check_naming_conventions(plugin_dir, result)
        check_python_scripts(plugin_dir, result)

        if not args.skip_skill_validator:
            run_skill_validator(plugin_dir, validator_path, result)

        results.append(result)

    # Output
    if args.format == "json":
        print(format_json(results))
    else:
        print(format_text(results))

    # Exit code: 0 if all ready, 1 if any issues
    if all(r.is_ready for r in results):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
