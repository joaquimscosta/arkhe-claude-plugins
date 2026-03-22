#!/usr/bin/env python3
"""
Python Project Tooling Scanner

Scans pyproject.toml, setup.cfg, requirements.txt, and config files to detect
configured quality and testing tools. Returns JSON for cross-referencing
against research recommendations.

Uses only standard library (no external dependencies). Python 3.8+.

Usage (standalone):
    python3 scan_python.py <project_root>

Usage (as module):
    from scan_python import scan
    result = scan(Path("/path/to/project"))
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import SKIP_DIRS, make_detection, read_file_safe, read_json_safe


# ---------------------------------------------------------------------------
# Package detection patterns: tool name -> list of pip package names
# ---------------------------------------------------------------------------

# Linting
LINTER_PACKAGES = {
    "ruff": ["ruff"],
    "flake8": ["flake8"],
    "pylint": ["pylint"],
}

# Formatting
FORMATTER_PACKAGES = {
    "ruff": ["ruff"],  # ruff also does formatting
    "black": ["black"],
    "isort": ["isort"],
    "autopep8": ["autopep8"],
    "yapf": ["yapf"],
}

# Type checking
TYPE_CHECK_PACKAGES = {
    "mypy": ["mypy"],
    "pyright": ["pyright"],
    "pytype": ["pytype"],
}

# Testing
TEST_PACKAGES = {
    "pytest": ["pytest"],
    "nose2": ["nose2"],
    "hypothesis": ["hypothesis"],
}

# Coverage
COVERAGE_PACKAGES = {
    "pytest-cov": ["pytest-cov"],
    "coverage": ["coverage"],
}

# Security
SECURITY_PACKAGES = {
    "bandit": ["bandit"],
    "safety": ["safety"],
    "pip-audit": ["pip-audit"],
}

# Task runners
TASK_RUNNER_PACKAGES = {
    "tox": ["tox"],
    "nox": ["nox"],
    "invoke": ["invoke"],
}

# Documentation
DOC_PACKAGES = {
    "sphinx": ["sphinx"],
    "mkdocs": ["mkdocs", "mkdocs-material"],
    "pdoc": ["pdoc"],
}

# Framework detection
FRAMEWORK_PACKAGES = {
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "starlette": ["starlette"],
    "tornado": ["tornado"],
    "aiohttp": ["aiohttp"],
}

# Config files for tool detection
PYTHON_CONFIG_FILES: Dict[str, str] = {
    # Ruff
    "ruff.toml": "ruff",
    ".ruff.toml": "ruff",
    # Black
    ".black.toml": "black",
    # Flake8
    ".flake8": "flake8",
    # Pylint
    ".pylintrc": "pylint",
    "pylintrc": "pylint",
    # Mypy
    "mypy.ini": "mypy",
    ".mypy.ini": "mypy",
    # Pyright
    "pyrightconfig.json": "pyright",
    # Pytest
    "pytest.ini": "pytest",
    "conftest.py": "pytest",
    # Tox
    "tox.ini": "tox",
    # Nox
    "noxfile.py": "nox",
    # Bandit
    ".bandit": "bandit",
    # Coverage
    ".coveragerc": "coverage",
    # Makefile (task runner)
    "Makefile": "make",
    # pre-commit
    ".pre-commit-config.yaml": "pre-commit",
}


# ---------------------------------------------------------------------------
# Lightweight TOML section extractor (Python 3.8 compat)
# ---------------------------------------------------------------------------


def extract_toml_sections(content: str) -> Dict[str, str]:
    """Extract TOML sections and their raw content.

    Returns a dict mapping section names (e.g., "tool.ruff", "project")
    to their raw text content. This is NOT a full TOML parser — it handles
    the common cases needed for pyproject.toml analysis.
    """
    sections: Dict[str, str] = {}
    current_section = ""
    current_lines: List[str] = []

    for line in content.splitlines():
        stripped = line.strip()
        # Match section header: [section] or [[section]]
        section_match = re.match(r"^\[{1,2}\s*([^\]]+?)\s*\]{1,2}$", stripped)
        if section_match:
            if current_section:
                sections[current_section] = "\n".join(current_lines)
            current_section = section_match.group(1)
            current_lines = []
        else:
            current_lines.append(line)

    # Don't forget the last section
    if current_section:
        sections[current_section] = "\n".join(current_lines)

    return sections


def extract_toml_list(raw_section: str, key: str) -> List[str]:
    """Extract a list value from a TOML section's raw text.

    Handles both inline lists and multi-line lists:
        key = ["a", "b"]
        key = [
            "a",
            "b",
        ]
    """
    # Try inline list first
    match = re.search(
        rf'^{re.escape(key)}\s*=\s*\[([^\]]*)\]',
        raw_section,
        re.MULTILINE,
    )
    if match:
        items_str = match.group(1)
        return [s.strip().strip('"').strip("'") for s in items_str.split(",") if s.strip().strip('"').strip("'")]

    # Try multi-line list
    match = re.search(
        rf'^{re.escape(key)}\s*=\s*\[',
        raw_section,
        re.MULTILINE,
    )
    if match:
        start = match.end()
        # Find closing bracket
        bracket_content = raw_section[start:]
        end = bracket_content.find("]")
        if end != -1:
            items_str = bracket_content[:end]
            return [s.strip().strip('"').strip("'") for s in items_str.split(",") if s.strip().strip('"').strip("'")]

    return []


def extract_toml_value(raw_section: str, key: str) -> Optional[str]:
    """Extract a scalar value from a TOML section's raw text."""
    match = re.search(
        rf'^{re.escape(key)}\s*=\s*["\']?([^"\'#\n]+?)["\']?\s*(?:#.*)?$',
        raw_section,
        re.MULTILINE,
    )
    if match:
        return match.group(1).strip()
    return None


def extract_toml_bool(raw_section: str, key: str) -> Optional[bool]:
    """Extract a boolean value from a TOML section's raw text."""
    val = extract_toml_value(raw_section, key)
    if val is None:
        return None
    return val.lower() == "true"


# ---------------------------------------------------------------------------
# Dependency extraction
# ---------------------------------------------------------------------------


def extract_deps_from_pyproject(content: str) -> List[str]:
    """Extract dependency package names from pyproject.toml."""
    deps: List[str] = []
    sections = extract_toml_sections(content)

    # [project] dependencies
    if "project" in sections:
        project_deps = extract_toml_list(sections["project"], "dependencies")
        deps.extend(project_deps)

    # [project.optional-dependencies] (all groups)
    for section_name, section_content in sections.items():
        if section_name.startswith("project.optional-dependencies"):
            # Extract all list values in this section
            for match in re.finditer(r'^(\w+)\s*=\s*\[', section_content, re.MULTILINE):
                key = match.group(1)
                items = extract_toml_list(section_content, key)
                deps.extend(items)

    # [tool.poetry.dependencies] and [tool.poetry.group.*.dependencies]
    for section_name, section_content in sections.items():
        if "poetry" in section_name and "dependencies" in section_name:
            for line in section_content.splitlines():
                stripped = line.strip()
                if "=" in stripped and not stripped.startswith("["):
                    pkg = stripped.split("=")[0].strip().strip('"').strip("'")
                    if pkg and pkg != "python":
                        deps.append(pkg)

    # [dependency-groups] (PEP 735, uv)
    for section_name, section_content in sections.items():
        if section_name.startswith("dependency-groups"):
            items = extract_toml_list(section_content, section_name.split(".")[-1] if "." in section_name else "dev")
            deps.extend(items)

    return deps


def extract_deps_from_requirements(root: Path) -> List[str]:
    """Extract dependency package names from requirements*.txt files."""
    deps: List[str] = []
    req_files = [
        "requirements.txt", "requirements-dev.txt", "requirements-test.txt",
        "requirements_dev.txt", "requirements_test.txt",
        "dev-requirements.txt", "test-requirements.txt",
    ]
    for rf in req_files:
        content = read_file_safe(root / rf)
        if content is None:
            continue
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("-"):
                continue
            # Extract package name (before version specifier)
            pkg = re.split(r"[>=<!\[;]", stripped)[0].strip()
            if pkg:
                deps.append(pkg)

    return deps


def extract_deps_from_pipfile(root: Path) -> List[str]:
    """Extract dependency package names from Pipfile."""
    deps: List[str] = []
    content = read_file_safe(root / "Pipfile")
    if content is None:
        return deps

    in_deps_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped in ("[packages]", "[dev-packages]"):
            in_deps_section = True
            continue
        if stripped.startswith("["):
            in_deps_section = False
            continue
        if in_deps_section and "=" in stripped:
            pkg = stripped.split("=")[0].strip().strip('"').strip("'")
            if pkg:
                deps.append(pkg)

    return deps


def normalize_package_name(name: str) -> str:
    """Normalize a Python package name for comparison."""
    return re.sub(r"[-_.]+", "-", name).lower()


def get_all_deps(root: Path) -> Set[str]:
    """Collect all dependency package names from all sources."""
    all_deps: Set[str] = set()

    # pyproject.toml
    content = read_file_safe(root / "pyproject.toml")
    if content:
        for dep in extract_deps_from_pyproject(content):
            all_deps.add(normalize_package_name(dep))

    # requirements*.txt
    for dep in extract_deps_from_requirements(root):
        all_deps.add(normalize_package_name(dep))

    # Pipfile
    for dep in extract_deps_from_pipfile(root):
        all_deps.add(normalize_package_name(dep))

    return all_deps


# ---------------------------------------------------------------------------
# Dependency manager detection
# ---------------------------------------------------------------------------


def detect_dependency_manager(root: Path) -> str:
    """Detect the dependency/package manager."""
    if (root / "uv.lock").exists():
        return "uv"
    if (root / "poetry.lock").exists():
        return "poetry"
    if (root / "Pipfile.lock").exists():
        return "pipenv"
    if (root / "pdm.lock").exists():
        return "pdm"

    # Check pyproject.toml for build system
    content = read_file_safe(root / "pyproject.toml")
    if content:
        sections = extract_toml_sections(content)
        build_system = sections.get("build-system", "")
        if "poetry" in build_system:
            return "poetry"
        if "pdm" in build_system:
            return "pdm"
        if "hatchling" in build_system or "hatch" in build_system:
            return "hatch"
        if "flit" in build_system:
            return "flit"

    if (root / "requirements.txt").exists():
        return "pip"

    return "unknown"


# ---------------------------------------------------------------------------
# Build system detection
# ---------------------------------------------------------------------------


def detect_build_system(root: Path) -> Optional[str]:
    """Detect the Python build system from pyproject.toml."""
    content = read_file_safe(root / "pyproject.toml")
    if content is None:
        if (root / "setup.py").exists():
            return "setuptools"
        return None

    sections = extract_toml_sections(content)
    build_system = sections.get("build-system", "")

    if "hatchling" in build_system:
        return "hatch"
    if "poetry" in build_system:
        return "poetry"
    if "flit" in build_system:
        return "flit"
    if "pdm" in build_system:
        return "pdm"
    if "maturin" in build_system:
        return "maturin"
    if "setuptools" in build_system:
        return "setuptools"

    return "unknown"


# ---------------------------------------------------------------------------
# Python version detection
# ---------------------------------------------------------------------------


def detect_python_version(root: Path) -> Optional[str]:
    """Detect the Python version requirement."""
    # Check .python-version
    pv = read_file_safe(root / ".python-version")
    if pv:
        return pv.strip()

    # Check pyproject.toml requires-python
    content = read_file_safe(root / "pyproject.toml")
    if content:
        sections = extract_toml_sections(content)
        project = sections.get("project", "")
        requires = extract_toml_value(project, "requires-python")
        if requires:
            return requires

    return None


# ---------------------------------------------------------------------------
# Framework detection
# ---------------------------------------------------------------------------


def detect_framework(all_deps: Set[str]) -> Optional[str]:
    """Detect the primary Python web framework."""
    if "django" in all_deps:
        return "django"
    if "fastapi" in all_deps:
        return "fastapi"
    if "flask" in all_deps:
        return "flask"
    if "starlette" in all_deps:
        return "starlette"
    if "tornado" in all_deps:
        return "tornado"
    if "aiohttp" in all_deps:
        return "aiohttp"
    return None


# ---------------------------------------------------------------------------
# Project structure
# ---------------------------------------------------------------------------


def detect_src_layout(root: Path) -> bool:
    """Check if project uses src layout."""
    return (root / "src").is_dir()


def count_source_files(root: Path) -> Tuple[int, int]:
    """Count Python source and test files."""
    src_count = 0
    test_count = 0

    test_dirs = {"test", "tests", "test_", "testing"}
    test_prefixes = ("test_",)
    test_suffixes = ("_test.py",)

    for dirpath, dirs, files in os.walk(str(root), topdown=True):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for f in files:
            if not f.endswith(".py"):
                continue

            is_test = False
            dir_parts = set(Path(dirpath).relative_to(root).parts)
            if dir_parts & test_dirs:
                is_test = True
            elif f.startswith(test_prefixes) or f.endswith(test_suffixes):
                is_test = True
            elif f == "conftest.py":
                is_test = True

            if is_test:
                test_count += 1
            else:
                src_count += 1

    return src_count, test_count


# ---------------------------------------------------------------------------
# Tool classification
# ---------------------------------------------------------------------------


def classify_python_tools(
    all_deps: Set[str],
    root: Path,
) -> Dict[str, List[dict]]:
    """Detect and classify all Python tools into categories."""
    categories: Dict[str, List[dict]] = {
        "linting": [],
        "formatting": [],
        "type_checking": [],
        "testing": [],
        "coverage": [],
        "security": [],
        "task_runner": [],
        "documentation": [],
        "framework": [],
    }

    seen_tools: Set[str] = set()

    def _add(cat: str, name: str, source: str) -> None:
        if name not in seen_tools:
            seen_tools.add(name)
            categories[cat].append(make_detection(name, "active", source))

    # Package-based detection
    for tool, packages in LINTER_PACKAGES.items():
        for pkg in packages:
            if normalize_package_name(pkg) in all_deps and tool not in seen_tools:
                _add("linting", tool, "dependency")
                break

    for tool, packages in FORMATTER_PACKAGES.items():
        for pkg in packages:
            if normalize_package_name(pkg) in all_deps and tool not in seen_tools:
                _add("formatting", tool, "dependency")
                break

    for tool, packages in TYPE_CHECK_PACKAGES.items():
        for pkg in packages:
            if normalize_package_name(pkg) in all_deps and tool not in seen_tools:
                _add("type_checking", tool, "dependency")
                break

    for tool, packages in TEST_PACKAGES.items():
        for pkg in packages:
            if normalize_package_name(pkg) in all_deps and tool not in seen_tools:
                _add("testing", tool, "dependency")
                break

    for tool, packages in COVERAGE_PACKAGES.items():
        for pkg in packages:
            if normalize_package_name(pkg) in all_deps and tool not in seen_tools:
                _add("coverage", tool, "dependency")
                break

    for tool, packages in SECURITY_PACKAGES.items():
        for pkg in packages:
            if normalize_package_name(pkg) in all_deps and tool not in seen_tools:
                _add("security", tool, "dependency")
                break

    for tool, packages in TASK_RUNNER_PACKAGES.items():
        for pkg in packages:
            if normalize_package_name(pkg) in all_deps and tool not in seen_tools:
                _add("task_runner", tool, "dependency")
                break

    for tool, packages in DOC_PACKAGES.items():
        for pkg in packages:
            if normalize_package_name(pkg) in all_deps and tool not in seen_tools:
                _add("documentation", tool, "dependency")
                break

    for tool, packages in FRAMEWORK_PACKAGES.items():
        for pkg in packages:
            if normalize_package_name(pkg) in all_deps and tool not in seen_tools:
                _add("framework", tool, "dependency")
                break

    # Config-file-only detection
    config_to_category = {
        "ruff": "linting",
        "black": "formatting",
        "flake8": "linting",
        "pylint": "linting",
        "mypy": "type_checking",
        "pyright": "type_checking",
        "pytest": "testing",
        "tox": "task_runner",
        "nox": "task_runner",
        "bandit": "security",
        "coverage": "coverage",
        "make": "task_runner",
    }
    for config_file, tool in PYTHON_CONFIG_FILES.items():
        if (root / config_file).exists() and tool not in seen_tools:
            cat = config_to_category.get(tool)
            if cat:
                _add(cat, tool, "config-file")

    # Also check pyproject.toml [tool.*] sections
    content = read_file_safe(root / "pyproject.toml")
    if content:
        sections = extract_toml_sections(content)
        tool_section_map = {
            "tool.ruff": ("ruff", "linting"),
            "tool.ruff.format": ("ruff", "formatting"),
            "tool.black": ("black", "formatting"),
            "tool.isort": ("isort", "formatting"),
            "tool.mypy": ("mypy", "type_checking"),
            "tool.pylint": ("pylint", "linting"),
            "tool.pytest": ("pytest", "testing"),
            "tool.pytest.ini_options": ("pytest", "testing"),
            "tool.coverage": ("coverage", "coverage"),
            "tool.coverage.run": ("coverage", "coverage"),
            "tool.bandit": ("bandit", "security"),
        }
        for section_name, (tool, cat) in tool_section_map.items():
            if section_name in sections and tool not in seen_tools:
                _add(cat, tool, "pyproject-toml")

    return categories


# ---------------------------------------------------------------------------
# Tool config extraction
# ---------------------------------------------------------------------------


def extract_tool_config(root: Path) -> Dict[str, object]:
    """Extract specific tool configuration details."""
    config: Dict[str, object] = {}

    content = read_file_safe(root / "pyproject.toml")
    if content is None:
        return config

    sections = extract_toml_sections(content)

    # Ruff config
    ruff_section = sections.get("tool.ruff", "")
    if ruff_section:
        target = extract_toml_value(ruff_section, "target-version")
        if target:
            config["ruff_target_version"] = target
        line_length = extract_toml_value(ruff_section, "line-length")
        if line_length:
            config["ruff_line_length"] = line_length

    ruff_lint = sections.get("tool.ruff.lint", "")
    if ruff_lint:
        select = extract_toml_list(ruff_lint, "select")
        if select:
            config["ruff_select_rules"] = select

    # Ruff formatter check
    if "tool.ruff.format" in sections:
        config["ruff_formatter_enabled"] = True

    # Mypy config
    mypy_section = sections.get("tool.mypy", "")
    if mypy_section:
        strict = extract_toml_bool(mypy_section, "strict")
        if strict is not None:
            config["mypy_strict"] = strict
        disallow_untyped = extract_toml_bool(mypy_section, "disallow_untyped_defs")
        if disallow_untyped is not None:
            config["mypy_disallow_untyped_defs"] = disallow_untyped

    # Black config
    black_section = sections.get("tool.black", "")
    if black_section:
        line_length = extract_toml_value(black_section, "line-length")
        if line_length:
            config["black_line_length"] = line_length

    # Pytest config
    pytest_section = sections.get("tool.pytest.ini_options", "")
    if pytest_section:
        addopts = extract_toml_value(pytest_section, "addopts")
        if addopts:
            config["pytest_addopts"] = addopts

    return config


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_python_project(root: Path) -> bool:
    """Check if directory contains a Python project."""
    markers = ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"]
    return any((root / m).exists() for m in markers)


def scan(root: Path) -> Optional[dict]:
    """Scan a Python project and return structured results.

    Returns None if not a Python project.
    """
    if not is_python_project(root):
        return None

    all_deps = get_all_deps(root)
    dep_manager = detect_dependency_manager(root)
    build_system = detect_build_system(root)
    python_version = detect_python_version(root)
    framework = detect_framework(all_deps)
    has_src_layout = detect_src_layout(root)
    src_count, test_count = count_source_files(root)

    # Classify tools
    categories = classify_python_tools(all_deps, root)

    # Extract tool config
    tool_config = extract_tool_config(root)

    # Config file existence map
    config_files = {}
    for file_path in PYTHON_CONFIG_FILES:
        config_files[file_path] = (root / file_path).exists()

    result = {
        "ecosystem": "python",
        "project": {
            "dependency_manager": dep_manager,
            "build_system": build_system,
            "python_version": python_version,
            "framework": framework,
            "has_pyproject_toml": (root / "pyproject.toml").exists(),
            "has_src_layout": has_src_layout,
            "test_file_count": test_count,
            "src_file_count": src_count,
        },
        "detected_tools": categories,
        "config_files": config_files,
        "tool_config": tool_config,
    }

    return result


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------


def main():
    """Main entry point for standalone usage."""
    parser = argparse.ArgumentParser(
        description="Python Project Tooling Scanner"
    )
    parser.add_argument("project_root", help="Path to the project root directory")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}, indent=2))
        sys.exit(1)

    result = scan(root)
    if result is None:
        print(json.dumps({
            "error": "no_python_project",
            "message": f"No Python project markers found at: {root}",
        }, indent=2))
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
