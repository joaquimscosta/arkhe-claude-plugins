#!/usr/bin/env python3
"""
Detect Taskfile installation and audit Taskfile.yml configurations.

Outputs JSON report of installed tools, existing Taskfile, detected
ecosystems, and audit violations. Used by taskfile-setup skill.

Uses only standard library (no external dependencies).

Usage:
    python3 detect_taskfile.py [project_root] [--no-audit]
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers (same pattern as detect_sops.py)
# ---------------------------------------------------------------------------

def run_cmd(cmd):
    """Run a command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def detect_os():
    """Detect operating system for install instructions."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    return system


# ---------------------------------------------------------------------------
# Tool detection
# ---------------------------------------------------------------------------

def detect_tool(name):
    """Check if a tool is installed and get its version."""
    path = shutil.which(name)
    if not path:
        return {"installed": False}

    info = {"installed": True, "path": path}

    version_output = run_cmd([name, "--version"])
    if version_output:
        match = re.search(r"(\d+\.\d+\.\d+)", version_output)
        if match:
            info["version"] = match.group(1)
        else:
            info["version_raw"] = version_output.splitlines()[0]

    return info


# ---------------------------------------------------------------------------
# Taskfile detection + parsing
# ---------------------------------------------------------------------------

TASKFILE_VARIANTS = [
    "Taskfile.yml", "taskfile.yml",
    "Taskfile.yaml", "taskfile.yaml",
    "Taskfile.dist.yml", "Taskfile.dist.yaml",
]


def _parse_taskfile(content):
    """Best-effort line-level YAML parser for Taskfile.yml.

    Returns a dict with top-level keys and parsed task metadata.
    No PyYAML required — uses indentation tracking.
    """
    result = {
        "version": None,
        "has_includes": False,
        "include_count": 0,
        "has_dotenv": False,
        "tasks": [],
    }

    lines = content.splitlines()

    # Top-level key detection
    current_section = None
    current_task = None
    task_indent = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Detect indentation level
        indent = len(line) - len(line.lstrip())

        # Top-level keys (indent == 0)
        if indent == 0 and ":" in stripped:
            key = stripped.split(":")[0].strip()
            value = stripped.split(":", 1)[1].strip() if ":" in stripped else ""

            if key == "version":
                # Extract version string (remove quotes)
                result["version"] = value.strip("'\"")
                current_section = None
            elif key == "includes":
                result["has_includes"] = True
                current_section = "includes"
            elif key == "dotenv":
                result["has_dotenv"] = True
                current_section = None
            elif key == "tasks":
                current_section = "tasks"
            else:
                current_section = key

            # Reset task context when changing sections
            if key != "tasks" and current_section != "tasks":
                current_task = None
                task_indent = None
            continue

        # Count includes entries (indent == 2 under includes)
        # Handles both expanded form (key:) and short form (key: ./path)
        if current_section == "includes" and indent == 2 and ":" in stripped:
            result["include_count"] += 1
            continue

        # Parse tasks section
        if current_section == "tasks":
            # Task name detection: indent == 2, ends with ':'
            if indent == 2 and stripped.endswith(":") and not stripped.startswith("-"):
                task_name = stripped[:-1].strip()
                current_task = {
                    "name": task_name,
                    "has_desc": False,
                    "has_preconditions": False,
                    "has_sources": False,
                    "has_generates": False,
                    "has_deps": False,
                    "has_status": False,
                    "line": i + 1,
                }
                task_indent = 2
                result["tasks"].append(current_task)
                continue

            # Task properties (indent == 4 under task)
            if current_task and indent == 4 and ":" in stripped:
                prop = stripped.split(":")[0].strip()
                if prop == "desc":
                    current_task["has_desc"] = True
                elif prop == "preconditions":
                    current_task["has_preconditions"] = True
                elif prop == "sources":
                    current_task["has_sources"] = True
                elif prop == "generates":
                    current_task["has_generates"] = True
                elif prop == "deps":
                    current_task["has_deps"] = True
                elif prop == "status":
                    current_task["has_status"] = True

    return result


def detect_taskfile(project_root):
    """Check for Taskfile.yml (or variants) and parse it."""
    root = Path(project_root)

    for variant in TASKFILE_VARIANTS:
        taskfile_path = root / variant
        if taskfile_path.exists():
            result = {"exists": True, "path": variant}
            try:
                content = taskfile_path.read_text()
                parsed = _parse_taskfile(content)
                result["version"] = parsed["version"]
                result["task_count"] = len(parsed["tasks"])
                result["has_includes"] = parsed["has_includes"]
                result["include_count"] = parsed["include_count"]
                result["has_dotenv"] = parsed["has_dotenv"]
                result["tasks"] = parsed["tasks"]
            except OSError:
                result["read_error"] = True
            return result

    return {"exists": False}


# ---------------------------------------------------------------------------
# Ecosystem detection
# ---------------------------------------------------------------------------

def detect_ecosystems(project_root):
    """Detect project ecosystems from marker files."""
    root = Path(project_root)
    ecosystems = []

    # Check root, one level deep, and two levels deep for monorepo patterns
    dirs_to_check = [root]
    monorepo_parents = {"apps", "packages", "libs", "services", "modules"}
    try:
        for entry in sorted(root.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                dirs_to_check.append(entry)
                # Two levels deep for known monorepo container dirs
                if entry.name in monorepo_parents:
                    try:
                        for sub in sorted(entry.iterdir()):
                            if sub.is_dir() and not sub.name.startswith("."):
                                dirs_to_check.append(sub)
                    except OSError:
                        pass
    except OSError:
        pass

    seen = set()

    for check_dir in dirs_to_check:
        rel = str(check_dir.relative_to(root)) if check_dir != root else "."

        # Node.js
        if (check_dir / "package.json").exists() and ("node", rel) not in seen:
            eco = {"ecosystem": "node", "root": rel}
            if (check_dir / "pnpm-lock.yaml").exists():
                eco["package_manager"] = "pnpm"
            elif (check_dir / "yarn.lock").exists():
                eco["package_manager"] = "yarn"
            elif (check_dir / "package-lock.json").exists():
                eco["package_manager"] = "npm"
            else:
                eco["package_manager"] = "unknown"
            ecosystems.append(eco)
            seen.add(("node", rel))

        # JVM
        if (check_dir / "build.gradle.kts").exists() and ("jvm", rel) not in seen:
            ecosystems.append({
                "ecosystem": "jvm", "build_tool": "gradle-kotlin", "root": rel
            })
            seen.add(("jvm", rel))
        elif (check_dir / "build.gradle").exists() and ("jvm", rel) not in seen:
            ecosystems.append({
                "ecosystem": "jvm", "build_tool": "gradle-groovy", "root": rel
            })
            seen.add(("jvm", rel))
        elif (check_dir / "pom.xml").exists() and ("jvm", rel) not in seen:
            ecosystems.append({
                "ecosystem": "jvm", "build_tool": "maven", "root": rel
            })
            seen.add(("jvm", rel))

        # Python
        if (check_dir / "pyproject.toml").exists() and ("python", rel) not in seen:
            eco = {"ecosystem": "python", "root": rel}
            if (check_dir / "uv.lock").exists():
                eco["package_manager"] = "uv"
            elif (check_dir / "Pipfile.lock").exists():
                eco["package_manager"] = "pipenv"
            elif (check_dir / "poetry.lock").exists():
                eco["package_manager"] = "poetry"
            else:
                eco["package_manager"] = "pip"
            ecosystems.append(eco)
            seen.add(("python", rel))
        elif (check_dir / "requirements.txt").exists() and ("python", rel) not in seen:
            ecosystems.append({
                "ecosystem": "python", "package_manager": "pip", "root": rel
            })
            seen.add(("python", rel))

    # Docker (check root only)
    compose_files = [
        "docker-compose.yml", "docker-compose.yaml",
        "compose.yml", "compose.yaml",
    ]
    has_dockerfile = (root / "Dockerfile").exists()
    has_compose = any((root / f).exists() for f in compose_files)

    # Also check infrastructure/ and docker/ subdirs for compose files
    for subdir in ["infrastructure", "infrastructure/docker", "docker"]:
        sub = root / subdir
        if sub.is_dir():
            if any((sub / f).exists() for f in compose_files):
                has_compose = True
            if (sub / "Dockerfile").exists():
                has_dockerfile = True

    if has_dockerfile or has_compose:
        ecosystems.append({
            "ecosystem": "docker",
            "has_dockerfile": has_dockerfile,
            "has_compose": has_compose,
            "root": ".",
        })

    return ecosystems


# ---------------------------------------------------------------------------
# Environment & runner detection
# ---------------------------------------------------------------------------

def detect_env_files(project_root):
    """Find .env* files in the project root."""
    root = Path(project_root)
    env_files = []
    try:
        for f in sorted(root.iterdir()):
            if f.is_file() and f.name.startswith(".env") and f.name != ".env.example":
                env_files.append(f.name)
    except OSError:
        pass
    return env_files


def detect_existing_runners(project_root):
    """Check for existing task runner tools."""
    root = Path(project_root)

    has_scripts = False
    pkg = root / "package.json"
    if pkg.exists():
        try:
            content = pkg.read_text()
            has_scripts = '"scripts"' in content
        except OSError:
            pass

    return {
        "makefile": (root / "Makefile").exists(),
        "justfile": (root / "justfile").exists() or (root / "Justfile").exists(),
        "package_json_scripts": has_scripts,
        "gradlew": (root / "gradlew").exists(),
    }


# ---------------------------------------------------------------------------
# Audit rules
# ---------------------------------------------------------------------------

DEPLOY_TASK_PATTERNS = re.compile(
    r"^(deploy|publish|release|push|promote)", re.IGNORECASE
)
BUILD_TASK_PATTERNS = re.compile(
    r"^(build|compile|package|assemble)", re.IGNORECASE
)
SEQUENTIAL_TASK_PATTERNS = re.compile(
    r"^(ci|pipeline|all|full|release|deploy)", re.IGNORECASE
)
ABSOLUTE_PATH_PATTERN = re.compile(r"(?:^|\s)/(?:usr|home|opt|var|etc|Users)/")


def audit_taskfile(project_root, taskfile_info, env_files):
    """Run audit rules against parsed Taskfile data.

    Returns a list of violation dicts.
    """
    violations = []

    if not taskfile_info.get("exists"):
        return violations

    # TF001: Missing version: '3'
    version = taskfile_info.get("version")
    if not version or not version.startswith("3"):
        violations.append({
            "rule": "TF001",
            "severity": "ERROR",
            "message": "Missing or non-'3' version declaration",
            "fix_hint": "Add 'version: \"3\"' at the top of your Taskfile",
        })

    tasks = taskfile_info.get("tasks", [])

    for task in tasks:
        name = task["name"]
        line = task["line"]

        # TF002: No preconditions on deploy/publish tasks
        if DEPLOY_TASK_PATTERNS.match(name) and not task["has_preconditions"]:
            violations.append({
                "rule": "TF002",
                "severity": "WARNING",
                "message": f"Task '{name}' has no preconditions (safety-critical task)",
                "task": name,
                "line": line,
                "fix_hint": "Add preconditions to validate environment, credentials, or branch",
            })

        # TF003: No sources/generates on build tasks
        if BUILD_TASK_PATTERNS.match(name) and not task["has_sources"] and not task["has_generates"]:
            violations.append({
                "rule": "TF003",
                "severity": "WARNING",
                "message": f"Task '{name}' has no sources/generates (no up-to-date checks)",
                "task": name,
                "line": line,
                "fix_hint": "Add sources/generates for incremental build caching",
            })

        # TF005: Missing desc
        if not task["has_desc"]:
            violations.append({
                "rule": "TF005",
                "severity": "WARNING",
                "message": f"Task '{name}' is missing a 'desc:' field",
                "task": name,
                "line": line,
                "fix_hint": f"Add 'desc: ...' to improve 'task --list' discoverability",
            })

        # TF008: deps used where sequential ordering is likely intended
        if task["has_deps"] and SEQUENTIAL_TASK_PATTERNS.match(name):
            violations.append({
                "rule": "TF008",
                "severity": "INFO",
                "message": f"Task '{name}' uses deps (parallel) — consider cmds with task: for sequential ordering",
                "task": name,
                "line": line,
                "fix_hint": "Replace deps: [...] with cmds: [{task: x}, {task: y}] if order matters",
            })

    # TF004: Too many tasks in single file
    task_count = taskfile_info.get("task_count", 0)
    has_includes = taskfile_info.get("has_includes", False)
    if task_count > 20 and not has_includes:
        violations.append({
            "rule": "TF004",
            "severity": "INFO",
            "message": f"Single file with {task_count} tasks (consider splitting via includes)",
            "fix_hint": "Split into taskfiles/ directory with per-concern Taskfile includes",
        })

    # TF006: No dotenv when .env files exist
    has_dotenv = taskfile_info.get("has_dotenv", False)
    if env_files and not has_dotenv:
        violations.append({
            "rule": "TF006",
            "severity": "INFO",
            "message": f"No 'dotenv:' config but {len(env_files)} .env file(s) found",
            "fix_hint": "Add 'dotenv: [\".env.local\", \".env\"]' for automatic env loading",
        })

    # TF007: Requires reading raw file content
    taskfile_path = Path(project_root) / taskfile_info["path"]
    try:
        content = taskfile_path.read_text()
        _audit_file_content(content, violations)
    except OSError:
        pass

    # Build summary
    summary = {"total": len(violations), "errors": 0, "warnings": 0, "info": 0}
    for v in violations:
        sev = v["severity"].lower()
        if sev in summary:
            summary[sev] += 1

    return {"violations": violations, "summary": summary}


def _audit_file_content(content, violations):
    """Audit rules that require raw file content."""
    lines = content.splitlines()

    for i, line in enumerate(lines):
        # TF007: Hard-coded absolute paths
        if ABSOLUTE_PATH_PATTERN.search(line) and not line.strip().startswith("#"):
            violations.append({
                "rule": "TF007",
                "severity": "WARNING",
                "message": f"Hard-coded absolute path on line {i + 1}",
                "line": i + 1,
                "fix_hint": "Use variables ({{.ROOT_DIR}}) or relative paths instead",
            })


# ---------------------------------------------------------------------------
# Main detection
# ---------------------------------------------------------------------------

def detect(project_root, audit=True):
    """Run all detection checks and return structured results."""
    taskfile_info = detect_taskfile(project_root)
    env_files = detect_env_files(project_root)

    result = {
        "task_binary": detect_tool("task"),
        "taskfile": taskfile_info,
        "ecosystems": detect_ecosystems(project_root),
        "env_files": env_files,
        "existing_runners": detect_existing_runners(project_root),
        "os": detect_os(),
    }

    if audit and taskfile_info.get("exists"):
        result["audit"] = audit_taskfile(project_root, taskfile_info, env_files)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Detect Taskfile installation and audit Taskfile.yml configurations"
    )
    parser.add_argument(
        "project_root", nargs="?", default=os.getcwd(),
        help="Path to the project root directory"
    )
    parser.add_argument(
        "--no-audit", action="store_true",
        help="Skip audit checks (detection only)"
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.is_dir():
        json.dump(
            {"error": "not_a_directory", "path": str(root)},
            sys.stdout, indent=2,
        )
        sys.exit(1)

    result = detect(str(root), audit=not args.no_audit)
    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
