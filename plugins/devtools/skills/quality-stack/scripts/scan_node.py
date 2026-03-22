#!/usr/bin/env python3
"""
Node.js / TypeScript Project Tooling Scanner

Scans package.json, tsconfig.json, and config files to detect configured
quality and testing tools. Returns JSON for cross-referencing against
research recommendations.

Uses only standard library (no external dependencies). Python 3.8+.

Usage (standalone):
    python3 scan_node.py <project_root>

Usage (as module):
    from scan_node import scan
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
# Package detection patterns: tool name -> list of npm package names
# ---------------------------------------------------------------------------

# Static analysis
LINTER_PACKAGES = {
    "eslint": ["eslint"],
    "biome": ["@biomejs/biome"],
}

# Formatting
FORMATTER_PACKAGES = {
    "prettier": ["prettier"],
    "biome": ["@biomejs/biome"],  # biome also does formatting
}

# Testing frameworks
TEST_PACKAGES = {
    "vitest": ["vitest"],
    "jest": ["jest", "ts-jest", "@jest/core"],
    "playwright": ["@playwright/test"],
    "cypress": ["cypress"],
    "testing-library-react": ["@testing-library/react"],
    "testing-library-vue": ["@testing-library/vue"],
    "testing-library-dom": ["@testing-library/dom"],
}

# Coverage
COVERAGE_PACKAGES = {
    "c8": ["c8"],
    "istanbul-nyc": ["nyc"],
    "vitest-coverage": ["@vitest/coverage-v8", "@vitest/coverage-istanbul"],
}

# Bundle analysis
BUNDLE_PACKAGES = {
    "size-limit": ["size-limit", "@size-limit/preset-small-lib", "@size-limit/preset-app"],
    "bundlemon": ["bundlemon"],
    "next-bundle-analyzer": ["@next/bundle-analyzer"],
    "webpack-bundle-analyzer": ["webpack-bundle-analyzer"],
}

# Security
SECURITY_PACKAGES = {
    "snyk": ["snyk"],
}

# Build tools
BUILD_PACKAGES = {
    "turbo": ["turbo"],
    "nx": ["nx", "@nx/workspace"],
    "tsup": ["tsup"],
    "vite": ["vite"],
    "esbuild": ["esbuild"],
    "webpack": ["webpack"],
    "rollup": ["rollup"],
}

# API testing
API_TEST_PACKAGES = {
    "supertest": ["supertest"],
    "msw": ["msw"],
    "nock": ["nock"],
}

# Framework detection
FRAMEWORK_PACKAGES = {
    "next": ["next"],
    "react": ["react"],
    "vue": ["vue"],
    "angular": ["@angular/core"],
    "svelte": ["svelte"],
    "nuxt": ["nuxt"],
    "remix": ["@remix-run/react"],
    "astro": ["astro"],
}

# Config files for tool detection
NODE_CONFIG_FILES: Dict[str, str] = {
    # ESLint
    "eslint.config.mjs": "eslint",
    "eslint.config.js": "eslint",
    "eslint.config.cjs": "eslint",
    "eslint.config.ts": "eslint",
    ".eslintrc.js": "eslint",
    ".eslintrc.cjs": "eslint",
    ".eslintrc.json": "eslint",
    ".eslintrc.yml": "eslint",
    ".eslintrc.yaml": "eslint",
    # Prettier
    ".prettierrc": "prettier",
    ".prettierrc.json": "prettier",
    ".prettierrc.yml": "prettier",
    ".prettierrc.yaml": "prettier",
    ".prettierrc.js": "prettier",
    ".prettierrc.cjs": "prettier",
    "prettier.config.js": "prettier",
    "prettier.config.cjs": "prettier",
    "prettier.config.mjs": "prettier",
    # Biome
    "biome.json": "biome",
    "biome.jsonc": "biome",
    # Tailwind CSS
    "tailwind.config.js": "tailwindcss",
    "tailwind.config.ts": "tailwindcss",
    "tailwind.config.cjs": "tailwindcss",
    "tailwind.config.mjs": "tailwindcss",
    # Vitest
    "vitest.config.ts": "vitest",
    "vitest.config.js": "vitest",
    "vitest.config.mts": "vitest",
    "vitest.workspace.ts": "vitest",
    # Jest
    "jest.config.js": "jest",
    "jest.config.ts": "jest",
    "jest.config.cjs": "jest",
    "jest.config.mjs": "jest",
    # Playwright
    "playwright.config.ts": "playwright",
    "playwright.config.js": "playwright",
    # Cypress
    "cypress.config.ts": "cypress",
    "cypress.config.js": "cypress",
    "cypress.config.cjs": "cypress",
    "cypress.config.mjs": "cypress",
}


# ---------------------------------------------------------------------------
# Package.json parsing
# ---------------------------------------------------------------------------


def get_all_deps(pkg: dict) -> Dict[str, str]:
    """Extract all dependencies from package.json."""
    all_deps: Dict[str, str] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        if key in pkg and isinstance(pkg[key], dict):
            all_deps.update(pkg[key])
    return all_deps


def detect_packages(
    all_deps: Dict[str, str],
    package_map: Dict[str, List[str]],
) -> List[Tuple[str, str]]:
    """Detect tools by checking for their npm packages.

    Returns list of (tool_name, matched_package) tuples.
    """
    found = []
    seen = set()
    for tool, packages in package_map.items():
        for pkg in packages:
            if pkg in all_deps and tool not in seen:
                seen.add(tool)
                found.append((tool, all_deps[pkg]))
                break
    return found


# ---------------------------------------------------------------------------
# TypeScript analysis
# ---------------------------------------------------------------------------


def analyze_tsconfig(root: Path) -> Dict[str, object]:
    """Analyze tsconfig.json for strict mode and other settings."""
    result = {
        "detected": False,
        "strict": False,
        "strict_flags": {},
        "target": None,
        "module": None,
    }

    tsconfig = read_json_safe(root / "tsconfig.json")
    if tsconfig is None:
        return result

    result["detected"] = True
    compiler_opts = tsconfig.get("compilerOptions", {})

    result["strict"] = compiler_opts.get("strict", False)
    result["target"] = compiler_opts.get("target")
    result["module"] = compiler_opts.get("module")

    # Track individual strict flags
    strict_flags = {}
    flag_names = [
        "noImplicitAny", "strictNullChecks", "strictFunctionTypes",
        "strictBindCallApply", "strictPropertyInitialization",
        "noImplicitThis", "alwaysStrict",
        "noUncheckedIndexedAccess", "exactOptionalPropertyTypes",
        "noImplicitReturns", "noFallthroughCasesInSwitch",
        "noUnusedLocals", "noUnusedParameters",
    ]
    for flag in flag_names:
        if flag in compiler_opts:
            strict_flags[flag] = compiler_opts[flag]

    result["strict_flags"] = strict_flags
    return result


# ---------------------------------------------------------------------------
# ESLint config analysis
# ---------------------------------------------------------------------------


def detect_eslint_config_type(root: Path) -> Optional[str]:
    """Detect ESLint config type: 'flat' or 'legacy'."""
    flat_configs = [
        "eslint.config.mjs", "eslint.config.js", "eslint.config.cjs", "eslint.config.ts",
    ]
    legacy_configs = [
        ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json", ".eslintrc.yml", ".eslintrc.yaml",
    ]

    for config in flat_configs:
        if (root / config).exists():
            return "flat"
    for config in legacy_configs:
        if (root / config).exists():
            return "legacy"
    return None


# ---------------------------------------------------------------------------
# Package manager detection
# ---------------------------------------------------------------------------


def detect_package_manager(root: Path) -> str:
    """Detect which package manager is used."""
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (root / "yarn.lock").exists():
        return "yarn"
    if (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        return "bun"
    if (root / "package-lock.json").exists():
        return "npm"

    # Check packageManager field in package.json
    pkg = read_json_safe(root / "package.json")
    if pkg and "packageManager" in pkg:
        pm = pkg["packageManager"]
        if pm.startswith("pnpm"):
            return "pnpm"
        if pm.startswith("yarn"):
            return "yarn"
        if pm.startswith("bun"):
            return "bun"

    return "npm"  # default


# ---------------------------------------------------------------------------
# Monorepo tool detection
# ---------------------------------------------------------------------------


def detect_monorepo_tool(root: Path, all_deps: Dict[str, str]) -> Optional[str]:
    """Detect monorepo management tool."""
    if (root / "turbo.json").exists() or "turbo" in all_deps:
        return "turbo"
    if (root / "nx.json").exists() or "nx" in all_deps or "@nx/workspace" in all_deps:
        return "nx"
    if (root / "lerna.json").exists():
        return "lerna"
    if (root / "pnpm-workspace.yaml").exists():
        return "pnpm-workspaces"
    # Check package.json workspaces
    pkg = read_json_safe(root / "package.json")
    if pkg and "workspaces" in pkg:
        return "workspaces"
    return None


# ---------------------------------------------------------------------------
# Framework detection
# ---------------------------------------------------------------------------


def detect_framework(all_deps: Dict[str, str]) -> Optional[str]:
    """Detect the primary framework."""
    # Order matters: check more specific frameworks first
    if "next" in all_deps:
        return "next"
    if "nuxt" in all_deps:
        return "nuxt"
    if "@remix-run/react" in all_deps:
        return "remix"
    if "astro" in all_deps:
        return "astro"
    if "@angular/core" in all_deps:
        return "angular"
    if "svelte" in all_deps:
        return "svelte"
    if "vue" in all_deps:
        return "vue"
    if "react" in all_deps:
        return "react"
    return None


# ---------------------------------------------------------------------------
# Node version detection
# ---------------------------------------------------------------------------


def detect_node_version(root: Path, pkg: dict) -> Optional[str]:
    """Detect the Node.js version requirement."""
    # Check .nvmrc
    nvmrc = read_file_safe(root / ".nvmrc")
    if nvmrc:
        return nvmrc.strip()

    # Check .node-version
    node_version = read_file_safe(root / ".node-version")
    if node_version:
        return node_version.strip()

    # Check engines in package.json
    engines = pkg.get("engines", {})
    if "node" in engines:
        return engines["node"]

    return None


# ---------------------------------------------------------------------------
# File counting
# ---------------------------------------------------------------------------


def count_source_files(root: Path) -> Tuple[int, int]:
    """Count source and test files in a Node.js project."""
    src_count = 0
    test_count = 0

    test_patterns = {"test", "tests", "__tests__", "spec", "specs", "__mocks__"}
    test_suffixes = {".test.", ".spec.", ".e2e."}

    for dirpath, dirs, files in os.walk(str(root), topdown=True):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for f in files:
            if not any(f.endswith(ext) for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")):
                continue

            # Determine if test file
            is_test = False
            dir_parts = set(Path(dirpath).relative_to(root).parts)
            if dir_parts & test_patterns:
                is_test = True
            elif any(suffix in f for suffix in test_suffixes):
                is_test = True

            if is_test:
                test_count += 1
            else:
                src_count += 1

    return src_count, test_count


# ---------------------------------------------------------------------------
# Tool classification
# ---------------------------------------------------------------------------


def classify_node_tools(
    all_deps: Dict[str, str],
    root: Path,
) -> Dict[str, List[dict]]:
    """Detect and classify all Node.js tools into categories."""
    categories: Dict[str, List[dict]] = {
        "static_analysis": [],
        "formatting": [],
        "testing": [],
        "type_checking": [],
        "coverage": [],
        "bundle_analysis": [],
        "security": [],
        "build_tools": [],
        "framework": [],
        "api_testing": [],
    }

    seen_tools: Set[str] = set()

    def _add(cat: str, name: str, version: Optional[str], source: str) -> None:
        if name not in seen_tools:
            seen_tools.add(name)
            det = make_detection(name, "active", source)
            if version:
                det["version"] = version
            categories[cat].append(det)

    # Package-based detection
    for tool, version in detect_packages(all_deps, LINTER_PACKAGES):
        _add("static_analysis", tool, version, "package-json")
    for tool, version in detect_packages(all_deps, FORMATTER_PACKAGES):
        if tool not in seen_tools:  # biome may already be in static_analysis
            _add("formatting", tool, version, "package-json")
    for tool, version in detect_packages(all_deps, TEST_PACKAGES):
        _add("testing", tool, version, "package-json")
    for tool, version in detect_packages(all_deps, COVERAGE_PACKAGES):
        _add("coverage", tool, version, "package-json")
    for tool, version in detect_packages(all_deps, BUNDLE_PACKAGES):
        _add("bundle_analysis", tool, version, "package-json")
    for tool, version in detect_packages(all_deps, SECURITY_PACKAGES):
        _add("security", tool, version, "package-json")
    for tool, version in detect_packages(all_deps, BUILD_PACKAGES):
        _add("build_tools", tool, version, "package-json")
    for tool, version in detect_packages(all_deps, API_TEST_PACKAGES):
        _add("api_testing", tool, version, "package-json")

    # Framework detection (informational)
    for tool, version in detect_packages(all_deps, FRAMEWORK_PACKAGES):
        _add("framework", tool, version, "package-json")

    # Config-file-only detection (tool not in deps but config exists)
    config_to_category = {
        "eslint": "static_analysis",
        "biome": "static_analysis",
        "prettier": "formatting",
        "vitest": "testing",
        "jest": "testing",
        "playwright": "testing",
        "cypress": "testing",
    }
    for config_file, tool in NODE_CONFIG_FILES.items():
        if (root / config_file).exists() and tool not in seen_tools:
            cat = config_to_category.get(tool)
            if cat:
                _add(cat, tool, None, "config-file")

    # TypeScript as type checking tool
    if "typescript" in all_deps:
        _add("type_checking", "typescript", all_deps["typescript"], "package-json")

    return categories


# ---------------------------------------------------------------------------
# Tool config extraction
# ---------------------------------------------------------------------------


def extract_tool_config(root: Path, all_deps: Dict[str, str]) -> Dict[str, object]:
    """Extract specific tool configuration details."""
    config: Dict[str, object] = {}

    # ESLint config type
    eslint_type = detect_eslint_config_type(root)
    if eslint_type:
        config["eslint_config_type"] = eslint_type

    # Check for npm audit in scripts
    pkg = read_json_safe(root / "package.json")
    if pkg:
        scripts = pkg.get("scripts", {})
        has_audit = any("audit" in v for v in scripts.values()) if scripts else False
        config["has_audit_script"] = has_audit

        # Check for test script
        config["has_test_script"] = "test" in scripts if scripts else False

        # Check for lint script
        config["has_lint_script"] = any(
            k in scripts for k in ["lint", "lint:fix", "eslint", "check"]
        ) if scripts else False

    # Tailwind CSS version (v4 needs special attention)
    if "tailwindcss" in all_deps:
        version = all_deps["tailwindcss"]
        config["tailwindcss_version"] = version
        if version.startswith("^4") or version.startswith("~4") or version.startswith("4"):
            config["tailwindcss_v4"] = True

    # Next.js specific
    if "next" in all_deps:
        config["next_version"] = all_deps["next"]

    return config


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_node_project(root: Path) -> bool:
    """Check if directory contains a Node.js project."""
    return (root / "package.json").exists()


def scan(root: Path) -> Optional[dict]:
    """Scan a Node.js/TypeScript project and return structured results.

    Returns None if not a Node.js project.
    """
    pkg = read_json_safe(root / "package.json")
    if pkg is None:
        return None

    all_deps = get_all_deps(pkg)

    # Detect project metadata
    package_manager = detect_package_manager(root)
    framework = detect_framework(all_deps)
    monorepo_tool = detect_monorepo_tool(root, all_deps)
    typescript_config = analyze_tsconfig(root)
    node_version = detect_node_version(root, pkg)
    src_count, test_count = count_source_files(root)

    # Classify tools
    categories = classify_node_tools(all_deps, root)

    # Extract tool config
    tool_config = extract_tool_config(root, all_deps)

    # Config file existence map
    config_files = {}
    for file_path in NODE_CONFIG_FILES:
        config_files[file_path] = (root / file_path).exists()

    result = {
        "ecosystem": "node",
        "project": {
            "package_manager": package_manager,
            "framework": framework,
            "typescript": typescript_config["detected"],
            "typescript_strict": typescript_config["strict"],
            "monorepo_tool": monorepo_tool,
            "node_version": node_version,
            "test_file_count": test_count,
            "src_file_count": src_count,
        },
        "detected_tools": categories,
        "config_files": config_files,
        "versions": {
            k: all_deps[k] for k in ["typescript", "next", "react", "vue"]
            if k in all_deps
        },
        "tool_config": tool_config,
    }

    if typescript_config["detected"]:
        result["typescript_analysis"] = typescript_config

    return result


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------


def main():
    """Main entry point for standalone usage."""
    parser = argparse.ArgumentParser(
        description="Node.js/TypeScript Project Tooling Scanner"
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
            "error": "no_package_json",
            "message": f"No package.json found at: {root}",
        }, indent=2))
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
