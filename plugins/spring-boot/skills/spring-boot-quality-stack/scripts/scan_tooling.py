#!/usr/bin/env python3
"""
JVM Project Tooling Scanner

Scans build files, config files, and project structure to detect configured
quality and testing tools. Returns JSON for cross-referencing against research
recommendations.

Uses only standard library (no external dependencies).

Usage:
    python3 scan_tooling.py <project_root>
    python3 scan_tooling.py --recursive <project_root>

Output:
    JSON with project profile, detected tools (with status), config files,
    versions, and tool configuration details.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Detection patterns: tool name -> list of regex patterns to search in build files
# ---------------------------------------------------------------------------

GRADLE_PLUGIN_PATTERNS: Dict[str, List[str]] = {
    # Static analysis
    "error-prone": [r"net\.ltgt\.errorprone", r"error_prone_core"],
    "spotbugs": [r"com\.github\.spotbugs", r"spotbugs"],
    "detekt": [r"io\.gitlab\.arturbosch\.detekt", r"detekt"],
    "ktlint": [r"org\.jlleitschuh\.gradle\.ktlint", r"ktlint"],
    "sonarqube": [r"org\.sonarqube", r"sonarqube"],
    # Coverage
    "jacoco": [r"\bjacoco\b"],
    "kover": [r"org\.jetbrains\.kotlinx\.kover", r"kotlinx\.kover"],
    # Mutation testing
    "pitest": [r"info\.solidsoft\.pitest", r"pitest"],
    # Security
    "owasp-dependency-check": [r"org\.owasp\.dependencycheck", r"owasp"],
    # Migrations
    "openrewrite": [r"org\.openrewrite\.rewrite", r"openrewrite"],
}

MAVEN_PLUGIN_PATTERNS: Dict[str, List[str]] = {
    "error-prone": [r"error_prone_core", r"error-prone"],
    "spotbugs": [r"spotbugs-maven-plugin", r"spotbugs"],
    "detekt": [r"detekt-maven-plugin"],
    "ktlint": [r"ktlint-maven-plugin"],
    "sonarqube": [r"sonar-maven-plugin", r"sonarqube"],
    "jacoco": [r"jacoco-maven-plugin", r"org\.jacoco"],
    "pitest": [r"pitest-maven", r"pitest"],
    "owasp-dependency-check": [r"dependency-check-maven"],
    "openrewrite": [r"rewrite-maven-plugin"],
}

TEST_DEPENDENCY_PATTERNS: Dict[str, List[str]] = {
    # Assertions
    "assertj": [r"assertj-core", r"assertj"],
    "kotest-assertions": [r"kotest-assertions-core"],
    "kotest-runner": [r"kotest-runner-junit5"],
    "strikt": [r"strikt-core"],
    "hamcrest": [r"org\.hamcrest", r"hamcrest"],
    # Mocking
    "mockk": [r"io\.mockk", r"\bmockk\b"],
    "mockito": [r"mockito-core", r"mockito-kotlin"],
    # Test data
    "instancio": [r"instancio-junit", r"instancio-core", r"instancio"],
    "kotlin-faker": [r"kotlin-faker"],
    "fixture-monkey": [r"fixture-monkey"],
    # Integration testing
    "testcontainers": [r"testcontainers"],
    # Architecture
    "archunit": [r"archunit"],
    # Contract testing
    "pact": [r"pact-jvm", r"au\.com\.dius\.pact", r"pact"],
    "spring-cloud-contract": [r"spring-cloud-contract", r"spring-cloud-starter-contract"],
    # Property-based testing
    "jqwik": [r"jqwik"],
    # API testing
    "rest-assured": [r"rest-assured"],
    # Benchmarking
    "jmh": [r"jmh-core", r"jmh-generator", r"me\.champeau\.jmh"],
    # Spring Modulith testing
    "spring-modulith-test": [r"spring-modulith-starter-test", r"spring-modulith-test"],
}

# Config files -> what they indicate
CONFIG_FILE_INDICATORS: Dict[str, str] = {
    "detekt.yml": "detekt",
    "detekt-config.yml": "detekt",
    "config/detekt.yml": "detekt",
    ".editorconfig": "editorconfig",
    "spotbugs-exclude.xml": "spotbugs",
    ".trivyignore": "trivy",
    "renovate.json": "renovate",
    "renovate.json5": "renovate",
    ".renovaterc": "renovate",
    ".renovaterc.json": "renovate",
    ".github/dependabot.yml": "dependabot",
    "sonar-project.properties": "sonarqube",
    "dependency-suppression.xml": "owasp-dependency-check",
    "config/dependency-suppression.xml": "owasp-dependency-check",
    # Git hooks
    "lefthook.yml": "lefthook",
    "lefthook-local.yml": "lefthook-local",
    ".husky/_/husky.sh": "husky",
    ".pre-commit-config.yaml": "pre-commit",
}

CI_FILE_INDICATORS: Dict[str, str] = {
    ".github/workflows": "github-actions",
    "Jenkinsfile": "jenkins",
    ".gitlab-ci.yml": "gitlab-ci",
    ".circleci/config.yml": "circleci",
    "bitbucket-pipelines.yml": "bitbucket-pipelines",
    "azure-pipelines.yml": "azure-devops",
}

SKIP_DIRS = {"build", ".gradle", "node_modules", ".git", "target", "out", ".idea"}

# Maps version catalog keys to normalized tool names
VERSION_CATALOG_KEY_MAP = {
    "spring-boot": "spring-boot",
    "springboot": "spring-boot",
    "kotlin": "kotlin",
    "detekt": "detekt",
    "ktlint": "ktlint",
    "kover": "kover",
    "jacoco": "jacoco",
    "pitest": "pitest",
    "kotest": "kotest",
    "mockk": "mockk",
    "assertj": "assertj",
    "testcontainers": "testcontainers",
    "archunit": "archunit",
    "jqwik": "jqwik",
    "instancio": "instancio",
    "java": "java",
}


# ---------------------------------------------------------------------------
# Detection result helpers
# ---------------------------------------------------------------------------


def make_detection(name: str, status: str = "active", source: str = "build-file") -> dict:
    """Create a tool detection result dict."""
    return {"name": name, "status": status, "source": source}


# ---------------------------------------------------------------------------
# Comment detection
# ---------------------------------------------------------------------------


def is_commented_out_gradle(content: str, match_pos: int) -> bool:
    """Check if a match position in Gradle content is inside a comment."""
    # Check single-line comment
    line_start = content.rfind("\n", 0, match_pos) + 1
    line_prefix = content[line_start:match_pos].lstrip()
    if line_prefix.startswith("//"):
        return True
    # Check block comment balance
    opens = len(re.findall(r"/\*", content[:match_pos]))
    closes = len(re.findall(r"\*/", content[:match_pos]))
    return opens > closes


def is_commented_out_maven(content: str, match_pos: int) -> bool:
    """Check if a match position in Maven POM is inside an XML comment."""
    last_open = content.rfind("<!--", 0, match_pos)
    if last_open == -1:
        return False
    last_close = content.rfind("-->", 0, match_pos)
    return last_close < last_open


# ---------------------------------------------------------------------------
# Tool config extraction
# ---------------------------------------------------------------------------


def extract_jacoco_threshold(content: str) -> Optional[str]:
    """Extract JaCoCo minimum coverage threshold from violationRules block."""
    match = re.search(
        r"violationRules\s*\{[^}]*minimum\.set\s*\(\s*([0-9.]+)\s*\)",
        content,
        re.DOTALL,
    )
    if not match:
        match = re.search(
            r"violationRules\s*\{[^}]*minimum\s*=\s*([0-9.]+)",
            content,
            re.DOTALL,
        )
    if not match:
        # Maven style
        match = re.search(
            r"<minimum>([0-9.]+)</minimum>",
            content,
        )
    return match.group(1) if match else None


def detect_ktlint_sarif(content: str) -> bool:
    """Check if ktlint is configured with SARIF reporter."""
    return bool(
        re.search(r"reporter.*sarif|sarif.*reporter|outputToSarif", content, re.IGNORECASE)
    )


def extract_lefthook_config(root: Path) -> Dict[str, object]:
    """Extract lefthook configuration details from lefthook.yml."""
    lefthook_file = root / "lefthook.yml"
    if not lefthook_file.exists():
        return {}

    try:
        content = lefthook_file.read_text(encoding="utf-8")
    except Exception:
        return {}

    config: Dict[str, object] = {}

    # Extract configured hook command names (under pre-commit.commands)
    hooks: List[str] = []
    in_commands = False
    commands_indent = -1
    child_indent = -1  # set by first child key encountered
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
                continue
            match = re.match(r"^\s+(\w[\w-]*):", line)
            if match:
                if child_indent == -1:
                    child_indent = line_indent  # first key sets the level
                if line_indent == child_indent:
                    hooks.append(match.group(1))
    config["lefthook_hooks"] = hooks

    # Check for stage_fixed usage (lefthook v2 best practice)
    config["lefthook_has_stage_fixed"] = bool(
        re.search(r"stage_fixed:\s*true", content)
    )

    return config


# ---------------------------------------------------------------------------
# Build tool detection
# ---------------------------------------------------------------------------


def scan_package_json_hooks(root: Path) -> List[str]:
    """Check package.json for git hook manager dependencies (lefthook, husky)."""
    pkg_path = root / "package.json"
    if not pkg_path.exists():
        return []

    try:
        content = pkg_path.read_text(encoding="utf-8")
        data = json.loads(content)
    except Exception:
        return []

    detected = []
    all_deps = {}
    for key in ("devDependencies", "dependencies"):
        if key in data and isinstance(data[key], dict):
            all_deps.update(data[key])

    if "lefthook" in all_deps:
        detected.append("lefthook")
    if "husky" in all_deps:
        detected.append("husky")

    return detected


def detect_build_tool(root: Path) -> str:
    """Determine the build tool used by the project."""
    if (root / "build.gradle.kts").exists():
        return "gradle-kotlin"
    if (root / "build.gradle").exists():
        return "gradle-groovy"
    if (root / "pom.xml").exists():
        return "maven"
    return "unknown"


# ---------------------------------------------------------------------------
# Build file discovery
# ---------------------------------------------------------------------------


def find_gradle_build_files(root: Path) -> List[Path]:
    """Find all Gradle build files (root + submodules)."""
    files = []
    for name in ["build.gradle.kts", "build.gradle"]:
        root_file = root / name
        if root_file.exists():
            files.append(root_file)
    # Also check settings for included builds
    settings = root / "settings.gradle.kts"
    if not settings.exists():
        settings = root / "settings.gradle"
    if settings.exists():
        try:
            content = settings.read_text(encoding="utf-8")
            # Find include(":module") patterns
            includes = re.findall(r'include\s*\(\s*"([^"]+)"\s*\)', content)
            includes += re.findall(r"include\s*\(\s*'([^']+)'\s*\)", content)
            includes += re.findall(r'include\s+"([^"]+)"', content)
            includes += re.findall(r"include\s+'([^']+)'", content)
            for module in includes:
                module_dir = root / module.replace(":", "/").lstrip("/")
                for name in ["build.gradle.kts", "build.gradle"]:
                    module_file = module_dir / name
                    if module_file.exists():
                        files.append(module_file)
        except Exception:
            pass
    return files


def find_build_files_recursive(root: Path) -> List[Path]:
    """Walk directories to find all build files, skipping build output dirs."""
    build_files = []
    for dirpath, dirs, files in os.walk(str(root), topdown=True):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in ["build.gradle.kts", "build.gradle", "pom.xml"]:
            if name in files:
                build_files.append(Path(dirpath) / name)
    return build_files


# ---------------------------------------------------------------------------
# Gradle scanning
# ---------------------------------------------------------------------------


def _detect_tools_with_status(
    content: str,
    patterns: Dict[str, List[str]],
    comment_checker,
) -> List[dict]:
    """Detect tools in content with comment-aware status."""
    detected = []
    seen = set()
    for tool, tool_patterns in patterns.items():
        for pattern in tool_patterns:
            match = re.search(pattern, content)
            if match and tool not in seen:
                seen.add(tool)
                commented = comment_checker(content, match.start())
                status = "disabled" if commented else "active"
                detected.append(make_detection(tool, status, "build-file"))
                break
    return detected


def scan_gradle_builds(
    root: Path, recursive: bool = False
) -> Tuple[List[dict], List[dict], Dict[str, str], Dict[str, object]]:
    """Scan Gradle build files for plugins, dependencies, versions, and config."""
    detected_plugins: List[dict] = []
    detected_deps: List[dict] = []
    versions: Dict[str, str] = {}
    tool_config: Dict[str, object] = {}

    if recursive:
        build_files = [
            f
            for f in find_build_files_recursive(root)
            if f.name.startswith("build.gradle")
        ]
    else:
        build_files = find_gradle_build_files(root)

    combined_content = ""
    for bf in build_files:
        try:
            combined_content += bf.read_text(encoding="utf-8") + "\n"
        except Exception:
            pass

    if not combined_content:
        return detected_plugins, detected_deps, versions, tool_config

    # Detect plugins with status
    detected_plugins = _detect_tools_with_status(
        combined_content, GRADLE_PLUGIN_PATTERNS, is_commented_out_gradle
    )

    # Detect test dependencies with status
    detected_deps = _detect_tools_with_status(
        combined_content, TEST_DEPENDENCY_PATTERNS, is_commented_out_gradle
    )

    # Extract Spring Boot version
    sb_match = re.search(
        r'org\.springframework\.boot["\')]\s*version\s*["\']([^"\']+)',
        combined_content,
    )
    if not sb_match:
        sb_match = re.search(
            r'id\s*\(\s*"org\.springframework\.boot"\s*\)\s*version\s*"([^"]+)"',
            combined_content,
        )
    if sb_match:
        versions["spring-boot"] = sb_match.group(1)

    # Extract Kotlin version
    kt_match = re.search(
        r'kotlin\s*\(\s*"jvm"\s*\)\s*version\s*"([^"]+)"', combined_content
    )
    if not kt_match:
        kt_match = re.search(
            r'org\.jetbrains\.kotlin\.jvm["\')]\s*version\s*["\']([^"\']+)',
            combined_content,
        )
    if kt_match:
        versions["kotlin"] = kt_match.group(1)

    # Extract Java version
    java_match = re.search(r"jvmToolchain\s*\(\s*(\d+)\s*\)", combined_content)
    if not java_match:
        java_match = re.search(
            r"sourceCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)",
            combined_content,
        )
    if not java_match:
        java_match = re.search(
            r"java\.sourceCompatibility\s*=\s*.*?(\d+)", combined_content
        )
    if java_match:
        versions["java"] = java_match.group(1)

    # Extract tool versions where visible
    plugin_names = {d["name"] for d in detected_plugins}
    version_extractions = {
        "detekt": [r'detekt["\')]\s*version\s*["\']([^"\']+)'],
        "ktlint": [
            r'ktlint["\')]\s*version\s*["\']([^"\']+)',
            r'version\.set\s*\(\s*"([^"]+)"',
        ],
        "kover": [r'kover["\')]\s*version\s*["\']([^"\']+)'],
        "pitest": [
            r'pitest["\')]\s*version\s*["\']([^"\']+)',
            r'pitestVersion\.set\s*\(\s*"([^"]+)"',
        ],
        "jacoco": [r'toolVersion\s*=\s*"([^"]+)"'],
    }
    for tool, regexes in version_extractions.items():
        if tool in plugin_names:
            for regex in regexes:
                match = re.search(regex, combined_content)
                if match:
                    versions[tool] = match.group(1)
                    break

    # Extract tool config details
    threshold = extract_jacoco_threshold(combined_content)
    if threshold is not None:
        tool_config["jacoco_threshold"] = threshold

    if "ktlint" in plugin_names:
        tool_config["ktlint_sarif_enabled"] = detect_ktlint_sarif(combined_content)

    return detected_plugins, detected_deps, versions, tool_config


# ---------------------------------------------------------------------------
# Maven scanning
# ---------------------------------------------------------------------------


def scan_maven_build(
    root: Path, recursive: bool = False
) -> Tuple[List[dict], List[dict], Dict[str, str], Dict[str, object]]:
    """Scan pom.xml for plugins, dependencies, versions, and config."""
    detected_plugins: List[dict] = []
    detected_deps: List[dict] = []
    versions: Dict[str, str] = {}
    tool_config: Dict[str, object] = {}

    if recursive:
        pom_files = [
            f for f in find_build_files_recursive(root) if f.name == "pom.xml"
        ]
    else:
        pom_file = root / "pom.xml"
        pom_files = [pom_file] if pom_file.exists() else []

    combined_content = ""
    for pf in pom_files:
        try:
            combined_content += pf.read_text(encoding="utf-8") + "\n"
        except Exception:
            pass

    if not combined_content:
        return detected_plugins, detected_deps, versions, tool_config

    # Detect plugins with status
    detected_plugins = _detect_tools_with_status(
        combined_content, MAVEN_PLUGIN_PATTERNS, is_commented_out_maven
    )

    # Detect test dependencies with status
    detected_deps = _detect_tools_with_status(
        combined_content, TEST_DEPENDENCY_PATTERNS, is_commented_out_maven
    )

    # Extract Spring Boot version
    sb_match = re.search(
        r"<artifactId>spring-boot-starter-parent</artifactId>\s*<version>([^<]+)</version>",
        combined_content,
    )
    if sb_match:
        versions["spring-boot"] = sb_match.group(1)

    # Extract Java version
    java_match = re.search(r"<java\.version>(\d+)</java\.version>", combined_content)
    if not java_match:
        java_match = re.search(
            r"<maven\.compiler\.source>(\d+)</maven\.compiler\.source>",
            combined_content,
        )
    if java_match:
        versions["java"] = java_match.group(1)

    # Extract Kotlin version
    kt_match = re.search(
        r"<kotlin\.version>([^<]+)</kotlin\.version>", combined_content
    )
    if kt_match:
        versions["kotlin"] = kt_match.group(1)

    # Extract tool config details
    threshold = extract_jacoco_threshold(combined_content)
    if threshold is not None:
        tool_config["jacoco_threshold"] = threshold

    plugin_names = {d["name"] for d in detected_plugins}
    if "ktlint" in plugin_names:
        tool_config["ktlint_sarif_enabled"] = detect_ktlint_sarif(combined_content)

    return detected_plugins, detected_deps, versions, tool_config


# ---------------------------------------------------------------------------
# Version catalog scanning (Gradle)
# ---------------------------------------------------------------------------


def scan_version_catalog(root: Path) -> Tuple[List[dict], List[dict], Dict[str, str]]:
    """Scan gradle/libs.versions.toml for tool references and versions."""
    detected_plugins: List[dict] = []
    detected_deps: List[dict] = []
    versions: Dict[str, str] = {}

    catalog_path = root / "gradle" / "libs.versions.toml"
    if not catalog_path.exists():
        return detected_plugins, detected_deps, versions

    try:
        content = catalog_path.read_text(encoding="utf-8")
    except Exception:
        return detected_plugins, detected_deps, versions

    # Check for plugin/library references (version catalogs don't have comments
    # in the same way, so we treat all as active)
    seen_plugins = set()
    seen_deps = set()

    for tool, patterns in GRADLE_PLUGIN_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content) and tool not in seen_plugins:
                seen_plugins.add(tool)
                detected_plugins.append(make_detection(tool, "active", "version-catalog"))
                break

    for tool, patterns in TEST_DEPENDENCY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content) and tool not in seen_deps:
                seen_deps.add(tool)
                detected_deps.append(make_detection(tool, "active", "version-catalog"))
                break

    # Extract versions from [versions] section
    in_versions = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[versions]":
            in_versions = True
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            in_versions = False
            continue
        if in_versions and "=" in stripped:
            key, _, val = stripped.partition("=")
            key = key.strip().strip('"').strip("'")
            val = val.strip().strip('"').strip("'")
            tool_name = VERSION_CATALOG_KEY_MAP.get(key.lower())
            if tool_name:
                versions[tool_name] = val

    return detected_plugins, detected_deps, versions


# ---------------------------------------------------------------------------
# Config & CI file scanning
# ---------------------------------------------------------------------------


def scan_config_files(root: Path) -> Dict[str, bool]:
    """Check for existence of tool config files."""
    result = {}
    for file_path, tool in CONFIG_FILE_INDICATORS.items():
        full_path = root / file_path
        result[file_path] = full_path.exists()
    return result


def scan_ci_files(root: Path) -> List[str]:
    """Detect CI/CD systems in use."""
    detected = []
    for path, ci_system in CI_FILE_INDICATORS.items():
        full_path = root / path
        if full_path.is_dir():
            has_workflows = list(full_path.glob("*.yml")) or list(full_path.glob("*.yaml"))
            if has_workflows:
                detected.append(ci_system)
        elif full_path.exists():
            detected.append(ci_system)
    return detected


# ---------------------------------------------------------------------------
# Project structure analysis
# ---------------------------------------------------------------------------


def _exclude_build_dirs(paths: List[Path]) -> List[Path]:
    """Filter out paths that pass through build output directories."""
    return [p for p in paths if not (SKIP_DIRS & set(p.parts))]


def analyze_project_structure(root: Path) -> Dict:
    """Analyze project structure for language, test count, etc."""
    result = {
        "language": "unknown",
        "test_file_count": 0,
        "main_file_count": 0,
        "has_test_dir": False,
        "has_jmh_dir": False,
    }

    java_main = _exclude_build_dirs(list(root.glob("**/src/main/**/*.java")))
    kotlin_main = _exclude_build_dirs(list(root.glob("**/src/main/**/*.kt")))
    java_test = _exclude_build_dirs(list(root.glob("**/src/test/**/*.java")))
    kotlin_test = _exclude_build_dirs(list(root.glob("**/src/test/**/*.kt")))

    result["main_file_count"] = len(java_main) + len(kotlin_main)
    result["test_file_count"] = len(java_test) + len(kotlin_test)
    result["has_test_dir"] = (root / "src" / "test").exists()
    result["has_jmh_dir"] = (root / "src" / "jmh").exists()

    java_count = len(java_main) + len(java_test)
    kotlin_count = len(kotlin_main) + len(kotlin_test)

    if kotlin_count > 0 and java_count > 0:
        result["language"] = "mixed"
    elif kotlin_count > 0:
        result["language"] = "kotlin"
    elif java_count > 0:
        result["language"] = "java"

    return result


# ---------------------------------------------------------------------------
# Tool classification into categories
# ---------------------------------------------------------------------------

PLUGIN_CATEGORY_MAP = {
    "error-prone": "static_analysis",
    "spotbugs": "static_analysis",
    "detekt": "static_analysis",
    "ktlint": "static_analysis",
    "sonarqube": "static_analysis",
    "jacoco": "coverage",
    "kover": "coverage",
    "pitest": "mutation_testing",
    "owasp-dependency-check": "security",
    "openrewrite": "migrations",
}

DEP_CATEGORY_MAP = {
    "assertj": "testing_libraries",
    "kotest-assertions": "testing_libraries",
    "kotest-runner": "testing_libraries",
    "strikt": "testing_libraries",
    "hamcrest": "testing_libraries",
    "mockk": "testing_libraries",
    "mockito": "testing_libraries",
    "instancio": "testing_libraries",
    "kotlin-faker": "testing_libraries",
    "fixture-monkey": "testing_libraries",
    "testcontainers": "testing_libraries",
    "spring-modulith-test": "testing_libraries",
    "archunit": "architecture",
    "pact": "contract_testing",
    "spring-cloud-contract": "contract_testing",
    "jqwik": "property_testing",
    "rest-assured": "api_testing",
    "jmh": "benchmarking",
}

# Config files that indicate a tool when no build-file reference exists
CONFIG_ONLY_MAP = {
    "detekt.yml": ("detekt", "static_analysis"),
    "detekt-config.yml": ("detekt", "static_analysis"),
    "config/detekt.yml": ("detekt", "static_analysis"),
    "spotbugs-exclude.xml": ("spotbugs", "static_analysis"),
    "sonar-project.properties": ("sonarqube", "static_analysis"),
}

# Config files that always indicate a standalone tool
CONFIG_TOOL_MAP = {
    ".trivyignore": ("trivy", "security"),
    "renovate.json": ("renovate", "dependency_management"),
    "renovate.json5": ("renovate", "dependency_management"),
    ".renovaterc": ("renovate", "dependency_management"),
    ".renovaterc.json": ("renovate", "dependency_management"),
    ".github/dependabot.yml": ("dependabot", "dependency_management"),
    "lefthook.yml": ("lefthook", "git_hooks"),
    ".husky/_/husky.sh": ("husky", "git_hooks"),
    ".pre-commit-config.yaml": ("pre-commit", "git_hooks"),
}


def classify_tools(
    plugins: List[dict],
    deps: List[dict],
    ci: List[str],
    config: Dict[str, bool],
) -> Dict[str, List[dict]]:
    """Organize detected tools into categories with status info."""
    categories: Dict[str, List[dict]] = {
        "static_analysis": [],
        "testing_libraries": [],
        "coverage": [],
        "mutation_testing": [],
        "architecture": [],
        "contract_testing": [],
        "property_testing": [],
        "api_testing": [],
        "benchmarking": [],
        "ci_cd": [],
        "dependency_management": [],
        "security": [],
        "migrations": [],
        "git_hooks": [],
    }

    # Track tool names already classified (for config-only detection)
    classified_names = set()

    # Plugins -> categories
    for detection in plugins:
        cat = PLUGIN_CATEGORY_MAP.get(detection["name"])
        if cat:
            categories[cat].append(detection)
            classified_names.add(detection["name"])

    # Dependencies -> categories
    for detection in deps:
        cat = DEP_CATEGORY_MAP.get(detection["name"])
        if cat:
            categories[cat].append(detection)
            classified_names.add(detection["name"])

    # CI systems
    categories["ci_cd"] = [make_detection(ci_sys, "active", "ci-file") for ci_sys in ci]

    # Standalone config-based tools (trivy, renovate, dependabot)
    for config_file, (tool, cat) in CONFIG_TOOL_MAP.items():
        if config.get(config_file, False) and tool not in classified_names:
            categories[cat].append(make_detection(tool, "active", "config-file"))
            classified_names.add(tool)

    # Config-only detection: config file exists but no build-file reference
    for config_file, (tool, cat) in CONFIG_ONLY_MAP.items():
        if config.get(config_file, False) and tool not in classified_names:
            categories[cat].append(make_detection(tool, "config-only", "config-file"))
            classified_names.add(tool)

    return categories


# ---------------------------------------------------------------------------
# Module discovery (for --recursive)
# ---------------------------------------------------------------------------


def discover_modules(root: Path) -> List[dict]:
    """Discover modules in a monorepo and report tools per module."""
    modules = []
    build_files = find_build_files_recursive(root)

    for bf in build_files:
        module_dir = bf.parent
        rel_path = str(module_dir.relative_to(root))
        if rel_path == ".":
            rel_path = "(root)"

        build_tool = detect_build_tool(module_dir)
        # Quick tool scan for this module
        content = ""
        try:
            content = bf.read_text(encoding="utf-8")
        except Exception:
            pass

        tool_names = []
        all_patterns = {}
        all_patterns.update(GRADLE_PLUGIN_PATTERNS)
        all_patterns.update(MAVEN_PLUGIN_PATTERNS)
        all_patterns.update(TEST_DEPENDENCY_PATTERNS)
        for tool, patterns in all_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    tool_names.append(tool)
                    break

        modules.append(
            {
                "path": rel_path,
                "build_tool": build_tool,
                "tools": tool_names,
            }
        )

    return modules


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="JVM Project Tooling Scanner — detects quality and testing tools"
    )
    parser.add_argument("project_root", help="Path to the project root directory")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively discover build files (for monorepos)",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}, indent=2))
        sys.exit(1)

    # Detect build tool
    build_tool = detect_build_tool(root)

    # Pre-flight check: no build file found
    if build_tool == "unknown":
        hint_files = []
        for name in ["build.gradle.kts", "build.gradle", "pom.xml"]:
            found = list(root.glob(f"*/{name}"))[:5]
            hint_files.extend(str(f.relative_to(root)) for f in found)

        output = {
            "error": "no_build_file",
            "message": f"No build file found at project root: {root}",
            "hint": "Try --recursive flag or pass a subproject path directly",
            "nearby_build_files": hint_files,
        }
        print(json.dumps(output, indent=2))
        sys.exit(1)

    # Scan build files
    if build_tool.startswith("gradle"):
        plugins, deps, versions, tool_config = scan_gradle_builds(
            root, recursive=args.recursive
        )
    elif build_tool == "maven":
        plugins, deps, versions, tool_config = scan_maven_build(
            root, recursive=args.recursive
        )
    else:
        plugins, deps, versions, tool_config = [], [], {}, {}

    # Scan version catalog (Gradle only)
    if build_tool.startswith("gradle"):
        cat_plugins, cat_deps, cat_versions = scan_version_catalog(root)
        existing_plugin_names = {d["name"] for d in plugins}
        existing_dep_names = {d["name"] for d in deps}
        for p in cat_plugins:
            if p["name"] not in existing_plugin_names:
                plugins.append(p)
        for d in cat_deps:
            if d["name"] not in existing_dep_names:
                deps.append(d)
        for k, v in cat_versions.items():
            if k not in versions:
                versions[k] = v

    # Scan config and CI files
    config_files = scan_config_files(root)
    ci_systems = scan_ci_files(root)

    # Extract lefthook config details (if lefthook.yml exists)
    lefthook_config = extract_lefthook_config(root)
    tool_config.update(lefthook_config)

    # Analyze project structure
    structure = analyze_project_structure(root)

    # Classify tools into categories
    categories = classify_tools(plugins, deps, ci_systems, config_files)

    # Detect git hook managers from package.json (supplements config-file detection)
    npm_hooks = scan_package_json_hooks(root)
    existing_hook_names = {d["name"] for d in categories["git_hooks"]}
    for hook_tool in npm_hooks:
        if hook_tool not in existing_hook_names:
            categories["git_hooks"].append(
                make_detection(hook_tool, "active", "package-json")
            )

    # Check version catalog existence
    has_version_catalog = (root / "gradle" / "libs.versions.toml").exists()

    # Build output
    output = {
        "project": {
            "build_tool": build_tool,
            "spring_boot_version": versions.get("spring-boot"),
            "language": structure["language"],
            "java_version": versions.get("java"),
            "kotlin_version": versions.get("kotlin"),
            "has_version_catalog": has_version_catalog,
            "test_file_count": structure["test_file_count"],
            "main_file_count": structure["main_file_count"],
        },
        "detected_tools": categories,
        "config_files": config_files,
        "versions": versions,
        "tool_config": tool_config,
    }

    # Add modules info for recursive mode
    if args.recursive:
        output["modules"] = discover_modules(root)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
