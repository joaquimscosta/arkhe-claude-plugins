#!/usr/bin/env python3
"""
JVM Project Tooling Scanner

Scans build files, config files, and project structure to detect configured
quality and testing tools. Returns JSON for cross-referencing against research
recommendations.

Uses only standard library (no external dependencies).

Usage:
    python3 scan_tooling.py <project_root>

Output:
    JSON with project profile, detected tools, config files, and versions.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Detection patterns: tool name → list of regex patterns to search in build files
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

# Config files → what they indicate
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
}

CI_FILE_INDICATORS: Dict[str, str] = {
    ".github/workflows": "github-actions",
    "Jenkinsfile": "jenkins",
    ".gitlab-ci.yml": "gitlab-ci",
    ".circleci/config.yml": "circleci",
    "bitbucket-pipelines.yml": "bitbucket-pipelines",
    "azure-pipelines.yml": "azure-devops",
}


# ---------------------------------------------------------------------------
# Build tool detection
# ---------------------------------------------------------------------------


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
# Gradle scanning
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


def scan_gradle_builds(root: Path) -> Tuple[List[str], List[str], Dict[str, str]]:
    """Scan Gradle build files for plugins, dependencies, and versions."""
    detected_plugins = []
    detected_deps = []
    versions: Dict[str, str] = {}

    build_files = find_gradle_build_files(root)
    combined_content = ""
    for bf in build_files:
        try:
            combined_content += bf.read_text(encoding="utf-8") + "\n"
        except Exception:
            pass

    if not combined_content:
        return detected_plugins, detected_deps, versions

    # Detect plugins
    for tool, patterns in GRADLE_PLUGIN_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, combined_content):
                if tool not in detected_plugins:
                    detected_plugins.append(tool)
                break

    # Detect test dependencies
    for lib, patterns in TEST_DEPENDENCY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, combined_content):
                if lib not in detected_deps:
                    detected_deps.append(lib)
                break

    # Extract Spring Boot version
    sb_match = re.search(
        r'org\.springframework\.boot["\')]\s*version\s*["\']([^"\']+)', combined_content
    )
    if not sb_match:
        sb_match = re.search(
            r'id\s*\(\s*"org\.springframework\.boot"\s*\)\s*version\s*"([^"]+)"',
            combined_content,
        )
    if sb_match:
        versions["spring-boot"] = sb_match.group(1)

    # Extract Kotlin version
    kt_match = re.search(r'kotlin\s*\(\s*"jvm"\s*\)\s*version\s*"([^"]+)"', combined_content)
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
            r'sourceCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)', combined_content
        )
    if not java_match:
        java_match = re.search(r"java\.sourceCompatibility\s*=\s*.*?(\d+)", combined_content)
    if java_match:
        versions["java"] = java_match.group(1)

    # Extract tool versions where visible
    version_extractions = {
        "detekt": [r'detekt["\')]\s*version\s*["\']([^"\']+)'],
        "ktlint": [r'ktlint["\')]\s*version\s*["\']([^"\']+)', r'version\.set\s*\(\s*"([^"]+)"'],
        "kover": [r'kover["\')]\s*version\s*["\']([^"\']+)'],
        "pitest": [r'pitest["\')]\s*version\s*["\']([^"\']+)', r'pitestVersion\.set\s*\(\s*"([^"]+)"'],
        "jacoco": [r'toolVersion\s*=\s*"([^"]+)"'],
    }
    for tool, regexes in version_extractions.items():
        if tool in detected_plugins:
            for regex in regexes:
                match = re.search(regex, combined_content)
                if match:
                    versions[tool] = match.group(1)
                    break

    return detected_plugins, detected_deps, versions


# ---------------------------------------------------------------------------
# Maven scanning
# ---------------------------------------------------------------------------


def scan_maven_build(root: Path) -> Tuple[List[str], List[str], Dict[str, str]]:
    """Scan pom.xml for plugins, dependencies, and versions."""
    detected_plugins = []
    detected_deps = []
    versions: Dict[str, str] = {}

    pom_file = root / "pom.xml"
    if not pom_file.exists():
        return detected_plugins, detected_deps, versions

    try:
        content = pom_file.read_text(encoding="utf-8")
    except Exception:
        return detected_plugins, detected_deps, versions

    # Detect plugins
    for tool, patterns in MAVEN_PLUGIN_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content):
                if tool not in detected_plugins:
                    detected_plugins.append(tool)
                break

    # Detect test dependencies
    for lib, patterns in TEST_DEPENDENCY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content):
                if lib not in detected_deps:
                    detected_deps.append(lib)
                break

    # Extract Spring Boot version
    sb_match = re.search(
        r"<artifactId>spring-boot-starter-parent</artifactId>\s*<version>([^<]+)</version>",
        content,
    )
    if sb_match:
        versions["spring-boot"] = sb_match.group(1)

    # Extract Java version
    java_match = re.search(r"<java\.version>(\d+)</java\.version>", content)
    if not java_match:
        java_match = re.search(r"<maven\.compiler\.source>(\d+)</maven\.compiler\.source>", content)
    if java_match:
        versions["java"] = java_match.group(1)

    # Extract Kotlin version
    kt_match = re.search(r"<kotlin\.version>([^<]+)</kotlin\.version>", content)
    if kt_match:
        versions["kotlin"] = kt_match.group(1)

    return detected_plugins, detected_deps, versions


# ---------------------------------------------------------------------------
# Version catalog scanning (Gradle)
# ---------------------------------------------------------------------------


def scan_version_catalog(root: Path) -> Tuple[List[str], List[str], Dict[str, str]]:
    """Scan gradle/libs.versions.toml for tool references and versions."""
    detected_plugins = []
    detected_deps = []
    versions: Dict[str, str] = {}

    catalog_path = root / "gradle" / "libs.versions.toml"
    if not catalog_path.exists():
        return detected_plugins, detected_deps, versions

    try:
        content = catalog_path.read_text(encoding="utf-8")
    except Exception:
        return detected_plugins, detected_deps, versions

    # Check for plugin/library references
    all_patterns = {}
    all_patterns.update(GRADLE_PLUGIN_PATTERNS)
    all_patterns.update(TEST_DEPENDENCY_PATTERNS)

    for tool, patterns in all_patterns.items():
        for pattern in patterns:
            if re.search(pattern, content):
                if tool in GRADLE_PLUGIN_PATTERNS and tool not in detected_plugins:
                    detected_plugins.append(tool)
                elif tool in TEST_DEPENDENCY_PATTERNS and tool not in detected_deps:
                    detected_deps.append(tool)
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
            # Map common version catalog keys to tool names
            version_key_map = {
                "spring-boot": "spring-boot",
                "springBoot": "spring-boot",
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
            for catalog_key, tool_name in version_key_map.items():
                if key.lower() == catalog_key.lower():
                    versions[tool_name] = val
                    break

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
        if full_path.exists() or full_path.is_dir():
            # For directories like .github/workflows, check if it has files
            if full_path.is_dir():
                yml_files = list(full_path.glob("*.yml")) + list(full_path.glob("*.yaml"))
                if yml_files:
                    detected.append(ci_system)
            else:
                detected.append(ci_system)
    return detected


# ---------------------------------------------------------------------------
# Project structure analysis
# ---------------------------------------------------------------------------


def analyze_project_structure(root: Path) -> Dict:
    """Analyze project structure for language, test count, etc."""
    result = {
        "language": "unknown",
        "test_file_count": 0,
        "main_file_count": 0,
        "has_test_dir": False,
        "has_jmh_dir": False,
    }

    # Count source files
    java_main = list(root.glob("**/src/main/**/*.java"))
    kotlin_main = list(root.glob("**/src/main/**/*.kt"))
    java_test = list(root.glob("**/src/test/**/*.java"))
    kotlin_test = list(root.glob("**/src/test/**/*.kt"))

    result["main_file_count"] = len(java_main) + len(kotlin_main)
    result["test_file_count"] = len(java_test) + len(kotlin_test)
    result["has_test_dir"] = (root / "src" / "test").exists()
    result["has_jmh_dir"] = (root / "src" / "jmh").exists()

    # Determine language
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


def classify_tools(
    plugins: List[str], deps: List[str], ci: List[str], config: Dict[str, bool]
) -> Dict[str, List[str]]:
    """Organize detected tools into categories."""
    categories: Dict[str, List[str]] = {
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
    }

    # Plugins → categories
    plugin_category_map = {
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

    for plugin in plugins:
        cat = plugin_category_map.get(plugin)
        if cat and plugin not in categories[cat]:
            categories[cat].append(plugin)

    # Dependencies → categories
    dep_category_map = {
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

    for dep in deps:
        cat = dep_category_map.get(dep)
        if cat and dep not in categories[cat]:
            categories[cat].append(dep)

    # CI systems
    categories["ci_cd"] = ci

    # Config-based detections (tools detected only via config files)
    config_tool_map = {
        ".trivyignore": ("trivy", "security"),
        "renovate.json": ("renovate", "dependency_management"),
        "renovate.json5": ("renovate", "dependency_management"),
        ".renovaterc": ("renovate", "dependency_management"),
        ".renovaterc.json": ("renovate", "dependency_management"),
        ".github/dependabot.yml": ("dependabot", "dependency_management"),
    }

    for config_file, (tool, cat) in config_tool_map.items():
        if config.get(config_file, False) and tool not in categories[cat]:
            categories[cat].append(tool)

    return categories


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {"error": "Usage: python3 scan_tooling.py <project_root>"},
                indent=2,
            )
        )
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}, indent=2))
        sys.exit(1)

    # Detect build tool
    build_tool = detect_build_tool(root)

    # Scan build files
    if build_tool.startswith("gradle"):
        plugins, deps, versions = scan_gradle_builds(root)
    elif build_tool == "maven":
        plugins, deps, versions = scan_maven_build(root)
    else:
        plugins, deps, versions = [], [], {}

    # Scan version catalog (Gradle only)
    if build_tool.startswith("gradle"):
        cat_plugins, cat_deps, cat_versions = scan_version_catalog(root)
        for p in cat_plugins:
            if p not in plugins:
                plugins.append(p)
        for d in cat_deps:
            if d not in deps:
                deps.append(d)
        for k, v in cat_versions.items():
            if k not in versions:
                versions[k] = v

    # Scan config and CI files
    config_files = scan_config_files(root)
    ci_systems = scan_ci_files(root)

    # Analyze project structure
    structure = analyze_project_structure(root)

    # Classify tools into categories
    categories = classify_tools(plugins, deps, ci_systems, config_files)

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
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
