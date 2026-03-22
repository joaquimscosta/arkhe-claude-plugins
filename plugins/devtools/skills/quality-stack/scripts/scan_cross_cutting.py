#!/usr/bin/env python3
"""
Cross-Cutting Tools Scanner

Detects ecosystem-agnostic quality tools: git hooks, CI/CD systems,
commit conventions, EditorConfig, dependency automation, security scanning,
and frontend tools (for Lefthook wiring).

Uses only standard library (no external dependencies). Python 3.8+.

Usage (standalone):
    python3 scan_cross_cutting.py <project_root>

Usage (as module):
    from scan_cross_cutting import scan
    result = scan(Path("/path/to/project"))
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import SKIP_DIRS, make_detection, read_file_safe, read_json_safe


# ---------------------------------------------------------------------------
# CI/CD detection
# ---------------------------------------------------------------------------

CI_FILE_INDICATORS: Dict[str, str] = {
    ".github/workflows": "github-actions",
    "Jenkinsfile": "jenkins",
    ".gitlab-ci.yml": "gitlab-ci",
    ".circleci/config.yml": "circleci",
    "bitbucket-pipelines.yml": "bitbucket-pipelines",
    "azure-pipelines.yml": "azure-devops",
}


def scan_ci_files(root: Path) -> List[dict]:
    """Detect CI/CD systems in use."""
    detected = []
    for path, ci_system in CI_FILE_INDICATORS.items():
        full_path = root / path
        if full_path.is_dir():
            has_workflows = list(full_path.glob("*.yml")) or list(full_path.glob("*.yaml"))
            if has_workflows:
                detected.append(make_detection(ci_system, "active", "ci-file"))
        elif full_path.exists():
            detected.append(make_detection(ci_system, "active", "ci-file"))
    return detected


# ---------------------------------------------------------------------------
# Git hooks detection
# ---------------------------------------------------------------------------

GIT_HOOK_CONFIG_FILES = {
    "lefthook.yml": "lefthook",
    "lefthook-local.yml": "lefthook",
    ".husky/_/husky.sh": "husky",
    ".pre-commit-config.yaml": "pre-commit",
}


def scan_git_hooks(root: Path) -> List[dict]:
    """Detect git hook managers from config files and package.json."""
    detected = []
    seen = set()

    # Config file detection
    for config_file, tool in GIT_HOOK_CONFIG_FILES.items():
        if (root / config_file).exists() and tool not in seen:
            seen.add(tool)
            detected.append(make_detection(tool, "active", "config-file"))

    # Package.json detection
    pkg = read_json_safe(root / "package.json")
    if pkg:
        all_deps = {}
        for key in ("devDependencies", "dependencies"):
            if key in pkg and isinstance(pkg[key], dict):
                all_deps.update(pkg[key])
        for tool in ["lefthook", "husky"]:
            if tool in all_deps and tool not in seen:
                seen.add(tool)
                detected.append(make_detection(tool, "active", "package-json"))

    return detected


def extract_lefthook_config(root: Path) -> Dict[str, object]:
    """Extract lefthook configuration details from lefthook.yml."""
    content = read_file_safe(root / "lefthook.yml")
    if content is None:
        return {}

    config: Dict[str, object] = {}

    # Extract configured hook command names from all hook sections
    hooks: List[str] = []
    in_commands = False
    commands_indent = -1
    child_indent = -1
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "commands:":
            in_commands = True
            commands_indent = len(line) - len(line.lstrip())
            child_indent = -1
            continue
        if in_commands:
            if not stripped:
                continue
            line_indent = len(line) - len(line.lstrip())
            if line_indent <= commands_indent:
                in_commands = False
                # Don't continue — this line may start a new section or commands block
                if stripped == "commands:":
                    in_commands = True
                    commands_indent = len(line) - len(line.lstrip())
                    child_indent = -1
                continue
            match = re.match(r"^\s+(\w[\w-]*):", line)
            if match:
                if child_indent == -1:
                    child_indent = line_indent
                if line_indent == child_indent:
                    hooks.append(match.group(1))
    config["lefthook_hooks"] = hooks

    # Check for stage_fixed usage (lefthook v2 best practice)
    config["lefthook_has_stage_fixed"] = bool(
        re.search(r"stage_fixed:\s*true", content)
    )

    return config


# ---------------------------------------------------------------------------
# Commit conventions detection
# ---------------------------------------------------------------------------

COMMITLINT_CONFIG_FILES = [
    "commitlint.config.js",
    "commitlint.config.cjs",
    "commitlint.config.mjs",
    "commitlint.config.ts",
    ".commitlintrc",
    ".commitlintrc.json",
    ".commitlintrc.yml",
    ".commitlintrc.yaml",
    ".commitlintrc.js",
    ".commitlintrc.cjs",
    ".commitlintrc.ts",
]


def scan_commit_conventions(root: Path) -> List[dict]:
    """Detect commit convention tools."""
    detected = []
    seen = set()

    # commitlint config files
    for config_file in COMMITLINT_CONFIG_FILES:
        if (root / config_file).exists() and "commitlint" not in seen:
            seen.add("commitlint")
            detected.append(make_detection("commitlint", "active", "config-file"))
            break

    # commitlint in package.json
    pkg = read_json_safe(root / "package.json")
    if pkg:
        all_deps = {}
        for key in ("devDependencies", "dependencies"):
            if key in pkg and isinstance(pkg[key], dict):
                all_deps.update(pkg[key])

        if "@commitlint/cli" in all_deps and "commitlint" not in seen:
            seen.add("commitlint")
            detected.append(make_detection("commitlint", "active", "package-json"))

        # commitizen
        if "commitizen" in all_deps and "commitizen" not in seen:
            seen.add("commitizen")
            detected.append(make_detection("commitizen", "active", "package-json"))
        elif "cz-conventional-changelog" in all_deps and "commitizen" not in seen:
            seen.add("commitizen")
            detected.append(make_detection("commitizen", "active", "package-json"))

    return detected


# ---------------------------------------------------------------------------
# EditorConfig detection
# ---------------------------------------------------------------------------


def scan_editor_config(root: Path) -> dict:
    """Detect and audit EditorConfig setup."""
    result = {
        "detected": False,
        "settings": {},
    }

    content = read_file_safe(root / ".editorconfig")
    if content is None:
        return result

    result["detected"] = True

    # Extract key settings
    settings = {}
    if re.search(r"indent_style\s*=\s*(\w+)", content):
        match = re.search(r"indent_style\s*=\s*(\w+)", content)
        settings["indent_style"] = match.group(1)
    if re.search(r"indent_size\s*=\s*(\w+)", content):
        match = re.search(r"indent_size\s*=\s*(\w+)", content)
        settings["indent_size"] = match.group(1)
    if re.search(r"end_of_line\s*=\s*(\w+)", content):
        match = re.search(r"end_of_line\s*=\s*(\w+)", content)
        settings["end_of_line"] = match.group(1)
    settings["trim_trailing_whitespace"] = bool(
        re.search(r"trim_trailing_whitespace\s*=\s*true", content, re.IGNORECASE)
    )
    settings["insert_final_newline"] = bool(
        re.search(r"insert_final_newline\s*=\s*true", content, re.IGNORECASE)
    )
    settings["is_root"] = bool(
        re.search(r"root\s*=\s*true", content, re.IGNORECASE)
    )

    result["settings"] = settings
    return result


# ---------------------------------------------------------------------------
# Dependency automation detection
# ---------------------------------------------------------------------------


def scan_dependency_automation(root: Path) -> List[dict]:
    """Detect dependency automation tools (Renovate, Dependabot)."""
    detected = []
    seen = set()

    # Renovate
    renovate_files = [
        "renovate.json", "renovate.json5", ".renovaterc", ".renovaterc.json",
    ]
    for rf in renovate_files:
        if (root / rf).exists() and "renovate" not in seen:
            seen.add("renovate")
            detected.append(make_detection("renovate", "active", "config-file"))
            break

    # Dependabot
    if (root / ".github" / "dependabot.yml").exists() and "dependabot" not in seen:
        seen.add("dependabot")
        detected.append(make_detection("dependabot", "active", "config-file"))

    return detected


# ---------------------------------------------------------------------------
# Security scanning detection
# ---------------------------------------------------------------------------


def scan_security_tools(root: Path) -> List[dict]:
    """Detect security scanning tools (Trivy, gitleaks, Snyk)."""
    detected = []

    # Trivy
    if (root / ".trivyignore").exists():
        detected.append(make_detection("trivy", "active", "config-file"))

    # gitleaks
    if (root / ".gitleaks.toml").exists():
        detected.append(make_detection("gitleaks", "active", "config-file"))

    # Snyk
    if (root / ".snyk").exists():
        detected.append(make_detection("snyk", "active", "config-file"))

    # Also check CI workflows for security tool mentions
    workflows_dir = root / ".github" / "workflows"
    if workflows_dir.is_dir():
        for wf in list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml")):
            content = read_file_safe(wf)
            if content is None:
                continue
            tool_seen = {d["name"] for d in detected}
            if "trivy" not in tool_seen and re.search(r"trivy", content, re.IGNORECASE):
                detected.append(make_detection("trivy", "active", "ci-workflow"))
            if "gitleaks" not in tool_seen and re.search(r"gitleaks", content, re.IGNORECASE):
                detected.append(make_detection("gitleaks", "active", "ci-workflow"))
            if "snyk" not in tool_seen and re.search(r"snyk", content, re.IGNORECASE):
                detected.append(make_detection("snyk", "active", "ci-workflow"))

    return detected


# ---------------------------------------------------------------------------
# Frontend tool detection (for Lefthook wiring)
# ---------------------------------------------------------------------------

FRONTEND_CONFIG_FILES: Dict[str, str] = {
    "eslint.config.mjs": "eslint",
    "eslint.config.js": "eslint",
    "eslint.config.cjs": "eslint",
    ".eslintrc.js": "eslint",
    ".eslintrc.cjs": "eslint",
    ".eslintrc.json": "eslint",
    ".eslintrc.yml": "eslint",
    ".eslintrc.yaml": "eslint",
    ".prettierrc": "prettier",
    ".prettierrc.json": "prettier",
    ".prettierrc.yml": "prettier",
    ".prettierrc.yaml": "prettier",
    ".prettierrc.js": "prettier",
    ".prettierrc.cjs": "prettier",
    "prettier.config.js": "prettier",
    "prettier.config.cjs": "prettier",
    "prettier.config.mjs": "prettier",
    "tailwind.config.js": "tailwindcss",
    "tailwind.config.ts": "tailwindcss",
    "tailwind.config.cjs": "tailwindcss",
    "tailwind.config.mjs": "tailwindcss",
    "biome.json": "biome",
    "biome.jsonc": "biome",
}

FRONTEND_PACKAGE_NAMES: Dict[str, str] = {
    "eslint": "eslint",
    "prettier": "prettier",
    "tailwindcss": "tailwindcss",
    "prettier-plugin-tailwindcss": "prettier-plugin-tailwindcss",
    "@biomejs/biome": "biome",
}


def scan_frontend_tools(directory: Path, root: Path) -> Optional[dict]:
    """Scan a directory for frontend tools (ESLint, Prettier, Tailwind CSS, Biome).

    Used for Lefthook wiring and Node.js scanner integration.
    Returns None if no frontend tools are detected.
    """
    tools: Dict[str, dict] = {}

    for pkg_name in FRONTEND_PACKAGE_NAMES:
        tool_name = FRONTEND_PACKAGE_NAMES[pkg_name]
        if tool_name not in tools:
            tools[tool_name] = {
                "detected": False,
                "version": None,
                "source": None,
                "config_file": None,
            }

    # Scan package.json for dependencies
    pkg = read_json_safe(directory / "package.json")
    if pkg:
        all_deps: Dict[str, str] = {}
        for key in ("devDependencies", "dependencies"):
            if key in pkg and isinstance(pkg[key], dict):
                all_deps.update(pkg[key])

        for pkg_name, tool_name in FRONTEND_PACKAGE_NAMES.items():
            if pkg_name in all_deps:
                tools[tool_name]["detected"] = True
                tools[tool_name]["version"] = all_deps[pkg_name]
                tools[tool_name]["source"] = "package-json"

    # Scan for config files
    for config_file, tool_name in FRONTEND_CONFIG_FILES.items():
        if (directory / config_file).exists():
            if tool_name in tools:
                tools[tool_name]["config_file"] = config_file
                if not tools[tool_name]["detected"]:
                    tools[tool_name]["detected"] = True
                    tools[tool_name]["source"] = "config-file"

    if not any(t["detected"] for t in tools.values()):
        return None

    rel_path = str(directory.relative_to(root)) if directory != root else "(root)"
    return {"path": rel_path, "tools": tools}


def discover_frontend_directories(root: Path) -> List[Path]:
    """Find directories containing package.json for frontend tool scanning."""
    dirs: List[Path] = []
    seen: set = set()

    def _add(d: Path) -> None:
        resolved = d.resolve()
        if resolved not in seen and (d / "package.json").exists():
            seen.add(resolved)
            dirs.append(d)

    _add(root)

    try:
        for entry in root.iterdir():
            if entry.is_dir() and entry.name not in SKIP_DIRS:
                _add(entry)
    except Exception:
        pass

    monorepo_prefixes = ["apps", "packages", "frontend", "web", "client"]
    for prefix in monorepo_prefixes:
        prefix_dir = root / prefix
        if prefix_dir.is_dir():
            try:
                for entry in prefix_dir.iterdir():
                    if entry.is_dir() and entry.name not in SKIP_DIRS:
                        _add(entry)
            except Exception:
                pass

    return dirs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def scan(root: Path) -> dict:
    """Scan for cross-cutting tools and return structured results.

    This is the main entry point when used as a module by the orchestrator.
    """
    ci_cd = scan_ci_files(root)
    git_hooks = scan_git_hooks(root)
    lefthook_config = extract_lefthook_config(root)
    commit_conventions = scan_commit_conventions(root)
    editor_config = scan_editor_config(root)
    dependency_automation = scan_dependency_automation(root)
    security_scanning = scan_security_tools(root)

    # Frontend tools for Lefthook wiring
    frontend_dirs = discover_frontend_directories(root)
    frontend_tools = []
    for fdir in frontend_dirs:
        result = scan_frontend_tools(fdir, root)
        if result is not None:
            frontend_tools.append(result)

    output = {
        "ci_cd": ci_cd,
        "git_hooks": git_hooks,
        "commit_conventions": commit_conventions,
        "editor_config": editor_config,
        "dependency_automation": dependency_automation,
        "security_scanning": security_scanning,
    }

    if lefthook_config:
        output["lefthook_config"] = lefthook_config

    if frontend_tools:
        output["frontend_tools"] = frontend_tools

    return output


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------


def main():
    """Main entry point for standalone usage."""
    parser = argparse.ArgumentParser(
        description="Cross-Cutting Tools Scanner — detects CI/CD, git hooks, security tools"
    )
    parser.add_argument("project_root", help="Path to the project root directory")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}, indent=2))
        sys.exit(1)

    result = scan(root)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
