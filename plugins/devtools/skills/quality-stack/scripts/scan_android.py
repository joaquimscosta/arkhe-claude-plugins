#!/usr/bin/env python3
"""
Android Project Tooling Scanner

Scans Android Gradle build files to detect configured quality, testing, and
build tools specific to Android/KMP projects. Returns JSON for cross-referencing
against research recommendations.

Complements the JVM scanner — detects Android-specific tools (AGP, Compose,
screenshot testing, etc.) while the JVM scanner covers shared Kotlin/Java tools
(detekt, ktlint, kover, mockk, etc.).

Uses only standard library (no external dependencies). Python 3.8+.

Usage (standalone):
    python3 scan_android.py <project_root>
    python3 scan_android.py --recursive <project_root>

Usage (as module):
    from scan_android import scan
    result = scan(Path("/path/to/android/project"), recursive=False)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Sibling import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import SKIP_DIRS, make_detection, read_file_safe, check_files_exist, count_files_by_glob
from scan_jvm import (
    find_gradle_build_files,
    find_build_files_recursive,
    is_commented_out_gradle,
    _detect_tools_with_status,
    scan_version_catalog,
)


# ---------------------------------------------------------------------------
# Detection patterns: Android-specific build plugins
# ---------------------------------------------------------------------------

ANDROID_PLUGIN_PATTERNS: Dict[str, List[str]] = {
    # AGP plugins
    "agp-application": [r"com\.android\.application"],
    "agp-library": [r"com\.android\.library"],
    "agp-kmp-library": [r"com\.android\.kotlin\.multiplatform\.library"],
    # Compose
    "compose-compiler": [
        r"org\.jetbrains\.kotlin\.plugin\.compose",
        r'kotlin\s*\(\s*"compose"\s*\)',
    ],
    # KMP
    "kotlin-multiplatform": [
        r"org\.jetbrains\.kotlin\.multiplatform",
        r'kotlin\s*\(\s*"multiplatform"\s*\)',
    ],
    # Kotlin serialization
    "kotlin-serialization": [
        r"org\.jetbrains\.kotlin\.plugin\.serialization",
        r'kotlin\s*\(\s*"plugin\.serialization"\s*\)',
    ],
    # Android testing
    "android-junit5": [r"de\.mannodermaus\.android-junit5"],
    # DI
    "hilt": [r"com\.google\.dagger\.hilt\.android", r"dagger\.hilt"],
    "ksp": [r"com\.google\.devtools\.ksp"],
    # Database
    "room": [r"androidx\.room"],
    "sqldelight": [r"app\.cash\.sqldelight"],
    # Screenshot testing
    "roborazzi-plugin": [r"io\.github\.takahirom\.roborazzi"],
    "paparazzi-plugin": [r"app\.cash\.paparazzi"],
    # Lint
    "android-lint-custom": [r"lintChecks|lintPublish"],
    # Performance
    "baseline-profile-plugin": [
        r"androidx\.baselineprofile",
        r"com\.android\.test",
    ],
}

ANDROID_TEST_DEPENDENCY_PATTERNS: Dict[str, List[str]] = {
    # Compose UI testing
    "compose-ui-test": [r"ui-test-junit4", r"compose\.ui.*ui-test"],
    "compose-ui-test-manifest": [r"ui-test-manifest"],
    # Screenshot testing
    "roborazzi": [r"roborazzi"],
    "paparazzi": [r"paparazzi"],
    "compose-preview-screenshot": [r"compose-preview-screenshot", r"screenshotTest"],
    # JVM-based Android testing
    "robolectric": [r"robolectric"],
    # Flow/coroutine testing
    "turbine": [r"app\.cash\.turbine", r"\bturbine\b"],
    # Google assertions
    "truth": [r"com\.google\.common\.truth", r"com\.google\.truth"],
    # AndroidX test
    "androidx-test-core": [r"androidx\.test:core", r"androidx\.test\.core"],
    "androidx-test-runner": [r"androidx\.test:runner", r"test-runner"],
    "androidx-test-rules": [r"androidx\.test:rules", r"test-rules"],
    # Espresso
    "espresso": [r"espresso-core", r"espresso-contrib", r"espresso-intents"],
    # Network testing
    "ktor-mock-engine": [r"ktor-client-mock"],
    "mockwebserver": [r"mockwebserver", r"MockWebServer"],
    # Database testing
    "sqldelight-jvm-driver": [r"sqlite-driver", r"sqldelight.*jvm.*driver", r"jdbc-driver"],
    # Macrobenchmark
    "macrobenchmark": [r"benchmark-macro", r"macrobenchmark"],
}

# Android-specific config files
ANDROID_CONFIG_FILE_INDICATORS: Dict[str, str] = {
    "lint.xml": "android-lint",
    "proguard-rules.pro": "r8-proguard",
    "consumer-proguard-rules.pro": "r8-proguard-consumer",
    "compose-stability-config.conf": "compose-stability",
}

# Version catalog keys specific to Android
ANDROID_VERSION_CATALOG_KEY_MAP = {
    "agp": "agp",
    "android-gradle-plugin": "agp",
    "kotlin": "kotlin",
    "compose-bom": "compose-bom",
    "compose": "compose-bom",
    "hilt": "hilt",
    "room": "room",
    "navigation": "navigation",
    "lifecycle": "lifecycle",
    "datastore": "datastore",
    "work": "workmanager",
    "ksp": "ksp",
    "roborazzi": "roborazzi",
    "turbine": "turbine",
    "sqldelight": "sqldelight",
    "ktor": "ktor",
    "koin": "koin",
}


# ---------------------------------------------------------------------------
# Android project detection
# ---------------------------------------------------------------------------


def is_android_project(root: Path) -> bool:
    """Check if directory contains an Android project.

    Looks for Android Gradle plugins in build files or AndroidManifest.xml.
    """
    for name in ["build.gradle.kts", "build.gradle"]:
        build_file = root / name
        if build_file.exists():
            content = read_file_safe(build_file)
            if content and re.search(
                r"com\.android\.(application|library|kotlin\.multiplatform\.library)",
                content,
            ):
                return True

    # Check settings file for included builds with Android plugins
    for name in ["settings.gradle.kts", "settings.gradle"]:
        settings_file = root / name
        if settings_file.exists():
            content = read_file_safe(settings_file)
            if content and re.search(r"com\.android\.", content):
                return True

    # Check for AndroidManifest.xml in standard locations
    manifest_patterns = [
        "src/main/AndroidManifest.xml",
        "*/src/main/AndroidManifest.xml",
        "app/src/main/AndroidManifest.xml",
        "androidApp/src/main/AndroidManifest.xml",
    ]
    for pattern in manifest_patterns:
        if list(root.glob(pattern)):
            return True

    # Check version catalog for AGP
    catalog = root / "gradle" / "libs.versions.toml"
    if catalog.exists():
        content = read_file_safe(catalog)
        if content and re.search(r"com\.android\.(application|library)", content):
            return True

    return False


# ---------------------------------------------------------------------------
# Android-specific version extraction
# ---------------------------------------------------------------------------


def extract_android_versions(content: str) -> Dict[str, str]:
    """Extract Android-specific versions from build file content."""
    versions: Dict[str, str] = {}

    # compileSdk
    match = re.search(r"compileSdk\s*[=:]\s*(\d+)", content)
    if not match:
        match = re.search(r"compileSdkVersion\s*[=(]\s*(\d+)", content)
    if match:
        versions["compile_sdk"] = match.group(1)

    # minSdk
    match = re.search(r"minSdk\s*[=:]\s*(\d+)", content)
    if not match:
        match = re.search(r"minSdkVersion\s*[=(]\s*(\d+)", content)
    if match:
        versions["min_sdk"] = match.group(1)

    # targetSdk
    match = re.search(r"targetSdk\s*[=:]\s*(\d+)", content)
    if not match:
        match = re.search(r"targetSdkVersion\s*[=(]\s*(\d+)", content)
    if match:
        versions["target_sdk"] = match.group(1)

    # AGP version from plugin declaration
    agp_match = re.search(
        r'com\.android\.\w+["\')]\s*version\s*["\']([^"\']+)', content
    )
    if agp_match:
        versions["agp"] = agp_match.group(1)

    # Compose BOM version
    bom_match = re.search(r'compose-bom:([^"\']+)', content)
    if not bom_match:
        bom_match = re.search(r'composeBom\s*=\s*"([^"]+)"', content)
    if bom_match:
        versions["compose-bom"] = bom_match.group(1)

    # Kotlin version
    kt_match = re.search(
        r'kotlin\s*\(\s*"[^"]+"\s*\)\s*version\s*"([^"]+)"', content
    )
    if not kt_match:
        kt_match = re.search(
            r'org\.jetbrains\.kotlin\.\w+["\')]\s*version\s*["\']([^"\']+)',
            content,
        )
    if kt_match:
        versions["kotlin"] = kt_match.group(1)

    return versions


def extract_android_version_catalog(root: Path) -> Dict[str, str]:
    """Extract Android-specific versions from version catalog."""
    versions: Dict[str, str] = {}
    catalog_path = root / "gradle" / "libs.versions.toml"
    if not catalog_path.exists():
        return versions

    content = read_file_safe(catalog_path)
    if not content:
        return versions

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
            tool_name = ANDROID_VERSION_CATALOG_KEY_MAP.get(key.lower())
            if tool_name:
                versions[tool_name] = val

    # Also check for android SDK versions in catalog
    android_sdk_patterns = {
        "androidcompilesdk": "compile_sdk",
        "androidminsdk": "min_sdk",
        "androidtargetsdk": "target_sdk",
        "compilesdk": "compile_sdk",
        "minsdk": "min_sdk",
        "targetsdk": "target_sdk",
    }
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
            key = key.strip().strip('"').strip("'").lower().replace("-", "").replace("_", "")
            sdk_name = android_sdk_patterns.get(key)
            if sdk_name:
                versions[sdk_name] = val.strip().strip('"').strip("'")

    return versions


# ---------------------------------------------------------------------------
# UI toolkit detection
# ---------------------------------------------------------------------------


def detect_ui_toolkit(root: Path, combined_content: str) -> str:
    """Detect whether project uses Compose, Views, or both.

    Returns: 'compose', 'views', 'mixed', or 'unknown'
    """
    has_compose = bool(
        re.search(r"compose|@Composable", combined_content)
        or list(root.glob("**/src/**/composable/**"))
    )

    # Check for Compose dependencies
    if not has_compose:
        has_compose = bool(
            re.search(r"compose-bom|compose\.ui|compose\.material", combined_content)
        )

    has_views = bool(list(root.glob("**/src/main/res/layout/*.xml")))
    if not has_views:
        has_views = bool(list(root.glob("**/src/main/res/layout/**/*.xml")))

    if has_compose and has_views:
        return "mixed"
    elif has_compose:
        return "compose"
    elif has_views:
        return "views"
    return "unknown"


# ---------------------------------------------------------------------------
# Project structure analysis
# ---------------------------------------------------------------------------


def _exclude_build_dirs(paths: List[Path]) -> List[Path]:
    """Filter out paths that pass through build output directories."""
    return [p for p in paths if not (SKIP_DIRS & set(p.parts))]


def analyze_android_structure(root: Path) -> Dict:
    """Analyze Android/KMP project structure."""
    result = {
        "main_file_count": 0,
        "test_file_count": 0,
        "android_test_file_count": 0,
        "common_main_file_count": 0,
        "common_test_file_count": 0,
    }

    # Standard Android source sets
    main_kt = _exclude_build_dirs(list(root.glob("**/src/main/**/*.kt")))
    main_java = _exclude_build_dirs(list(root.glob("**/src/main/**/*.java")))
    test_kt = _exclude_build_dirs(list(root.glob("**/src/test/**/*.kt")))
    test_java = _exclude_build_dirs(list(root.glob("**/src/test/**/*.java")))
    android_test_kt = _exclude_build_dirs(
        list(root.glob("**/src/androidTest/**/*.kt"))
    )
    android_test_java = _exclude_build_dirs(
        list(root.glob("**/src/androidTest/**/*.java"))
    )

    # KMP source sets
    android_main = _exclude_build_dirs(list(root.glob("**/src/androidMain/**/*.kt")))
    common_main = _exclude_build_dirs(list(root.glob("**/src/commonMain/**/*.kt")))
    common_test = _exclude_build_dirs(list(root.glob("**/src/commonTest/**/*.kt")))
    jvm_test = _exclude_build_dirs(list(root.glob("**/src/jvmTest/**/*.kt")))

    result["main_file_count"] = (
        len(main_kt) + len(main_java) + len(android_main) + len(common_main)
    )
    result["test_file_count"] = len(test_kt) + len(test_java) + len(jvm_test)
    result["android_test_file_count"] = len(android_test_kt) + len(android_test_java)
    result["common_main_file_count"] = len(common_main)
    result["common_test_file_count"] = len(common_test)

    return result


# ---------------------------------------------------------------------------
# Android project type detection
# ---------------------------------------------------------------------------


def detect_android_project_type(combined_content: str) -> str:
    """Determine Android project type from build content.

    Returns: 'application', 'library', 'kmp-library', or 'unknown'
    """
    if re.search(r"com\.android\.kotlin\.multiplatform\.library", combined_content):
        return "kmp-library"
    if re.search(r"com\.android\.application", combined_content):
        return "application"
    if re.search(r"com\.android\.library", combined_content):
        return "library"
    return "unknown"


def detect_is_kmp(combined_content: str) -> bool:
    """Check if the project uses Kotlin Multiplatform."""
    return bool(
        re.search(
            r"org\.jetbrains\.kotlin\.multiplatform|"
            r'kotlin\s*\(\s*"multiplatform"\s*\)|'
            r"com\.android\.kotlin\.multiplatform\.library",
            combined_content,
        )
    )


# ---------------------------------------------------------------------------
# Tool classification into Android categories
# ---------------------------------------------------------------------------

ANDROID_PLUGIN_CATEGORY_MAP = {
    "agp-application": "build_config",
    "agp-library": "build_config",
    "agp-kmp-library": "build_config",
    "compose-compiler": "compose",
    "kotlin-multiplatform": "build_config",
    "kotlin-serialization": "build_config",
    "android-junit5": "testing",
    "hilt": "dependency_injection",
    "ksp": "build_config",
    "room": "database",
    "sqldelight": "database",
    "roborazzi-plugin": "screenshot_testing",
    "paparazzi-plugin": "screenshot_testing",
    "android-lint-custom": "static_analysis",
    "baseline-profile-plugin": "performance",
}

ANDROID_DEP_CATEGORY_MAP = {
    "compose-ui-test": "testing",
    "compose-ui-test-manifest": "testing",
    "roborazzi": "screenshot_testing",
    "paparazzi": "screenshot_testing",
    "compose-preview-screenshot": "screenshot_testing",
    "robolectric": "testing",
    "turbine": "testing",
    "truth": "testing",
    "androidx-test-core": "testing",
    "androidx-test-runner": "testing",
    "androidx-test-rules": "testing",
    "espresso": "testing",
    "ktor-mock-engine": "network_testing",
    "mockwebserver": "network_testing",
    "sqldelight-jvm-driver": "database_testing",
    "macrobenchmark": "performance",
}


def classify_android_tools(
    plugins: List[dict],
    deps: List[dict],
    config_files: Dict[str, bool],
) -> Dict[str, List[dict]]:
    """Organize detected Android tools into categories."""
    categories: Dict[str, List[dict]] = {
        "build_config": [],
        "compose": [],
        "static_analysis": [],
        "testing": [],
        "screenshot_testing": [],
        "database": [],
        "database_testing": [],
        "network_testing": [],
        "dependency_injection": [],
        "performance": [],
    }

    classified_names = set()

    for detection in plugins:
        cat = ANDROID_PLUGIN_CATEGORY_MAP.get(detection["name"])
        if cat:
            categories[cat].append(detection)
            classified_names.add(detection["name"])

    for detection in deps:
        cat = ANDROID_DEP_CATEGORY_MAP.get(detection["name"])
        if cat:
            categories[cat].append(detection)
            classified_names.add(detection["name"])

    # Config-only detection
    config_only_map = {
        "lint.xml": ("android-lint", "static_analysis"),
        "compose-stability-config.conf": ("compose-stability", "compose"),
    }
    for config_file, (tool, cat) in config_only_map.items():
        if config_files.get(config_file, False) and tool not in classified_names:
            categories[cat].append(make_detection(tool, "config-only", "config-file"))
            classified_names.add(tool)

    return categories


# ---------------------------------------------------------------------------
# Tool config extraction
# ---------------------------------------------------------------------------


def extract_tool_config(combined_content: str, root: Path) -> Dict[str, object]:
    """Extract Android-specific tool configuration details."""
    config: Dict[str, object] = {}

    # Compose stability config
    stability_path = root / "compose-stability-config.conf"
    config["compose_stability_config"] = stability_path.exists()

    # Android Lint config
    lint_path = root / "lint.xml"
    config["has_lint_config"] = lint_path.exists()

    # Baseline profiles
    baseline_prof = root / "src" / "main" / "baseline-prof.txt"
    if not baseline_prof.exists():
        baseline_prof = root / "app" / "src" / "main" / "baseline-prof.txt"
    config["has_baseline_profile"] = baseline_prof.exists()

    # R8/ProGuard
    config["has_proguard_rules"] = (root / "proguard-rules.pro").exists()

    # Convention plugins
    config["has_convention_plugins"] = (root / "build-logic").is_dir()
    config["has_buildsrc"] = (root / "buildSrc").is_dir()

    # Check for compose features enabled
    config["compose_build_features"] = bool(
        re.search(r"buildFeatures\s*\{[^}]*compose\s*=\s*true", combined_content, re.DOTALL)
    )

    # Check for testOptions configuration
    config["has_include_android_resources"] = bool(
        re.search(
            r"isIncludeAndroidResources\s*=\s*true|includeAndroidResources\s*true",
            combined_content,
        )
    )

    return config


# ---------------------------------------------------------------------------
# Version catalog scanning (Android-specific keys)
# ---------------------------------------------------------------------------


def scan_android_version_catalog(root: Path) -> Tuple[List[dict], List[dict], Dict[str, str]]:
    """Scan version catalog for Android-specific tool references."""
    detected_plugins: List[dict] = []
    detected_deps: List[dict] = []
    versions: Dict[str, str] = {}

    catalog_path = root / "gradle" / "libs.versions.toml"
    if not catalog_path.exists():
        return detected_plugins, detected_deps, versions

    content = read_file_safe(catalog_path)
    if not content:
        return detected_plugins, detected_deps, versions

    seen_plugins = set()
    seen_deps = set()

    for tool, patterns in ANDROID_PLUGIN_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content) and tool not in seen_plugins:
                seen_plugins.add(tool)
                detected_plugins.append(make_detection(tool, "active", "version-catalog"))
                break

    for tool, patterns in ANDROID_TEST_DEPENDENCY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content) and tool not in seen_deps:
                seen_deps.add(tool)
                detected_deps.append(make_detection(tool, "active", "version-catalog"))
                break

    # Extract versions
    versions = extract_android_version_catalog(root)

    return detected_plugins, detected_deps, versions


# ---------------------------------------------------------------------------
# Config file scanning
# ---------------------------------------------------------------------------


def scan_android_config_files(root: Path) -> Dict[str, bool]:
    """Check for existence of Android-specific config files."""
    result = {}
    for file_path in ANDROID_CONFIG_FILE_INDICATORS:
        result[file_path] = (root / file_path).exists()

    # Also check common alternate locations
    result["baseline-prof.txt"] = (
        (root / "src" / "main" / "baseline-prof.txt").exists()
        or (root / "app" / "src" / "main" / "baseline-prof.txt").exists()
    )
    result["build-logic/"] = (root / "build-logic").is_dir()
    result["buildSrc/"] = (root / "buildSrc").is_dir()

    return result


# ---------------------------------------------------------------------------
# Module discovery (for --recursive)
# ---------------------------------------------------------------------------


def discover_android_modules(root: Path) -> List[dict]:
    """Discover Android modules and report tools per module."""
    modules = []
    build_files = find_build_files_recursive(root)

    for bf in build_files:
        if not bf.name.startswith("build.gradle"):
            continue

        content = read_file_safe(bf)
        if not content:
            continue

        # Only include modules with Android plugins
        if not re.search(r"com\.android\.", content):
            continue

        module_dir = bf.parent
        rel_path = str(module_dir.relative_to(root))
        if rel_path == ".":
            rel_path = "(root)"

        tool_names = []
        all_patterns = {}
        all_patterns.update(ANDROID_PLUGIN_PATTERNS)
        all_patterns.update(ANDROID_TEST_DEPENDENCY_PATTERNS)
        for tool, patterns in all_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    tool_names.append(tool)
                    break

        project_type = detect_android_project_type(content)

        modules.append(
            {
                "path": rel_path,
                "project_type": project_type,
                "tools": tool_names,
            }
        )

    return modules


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def scan(root: Path, recursive: bool = False) -> Optional[dict]:
    """Scan an Android project and return structured results.

    This is the main entry point when used as a module by the orchestrator.
    Returns a dict with ecosystem, project, detected_tools, etc.
    Returns None if not an Android project.
    """
    if not is_android_project(root):
        return None

    # Collect all build file content
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
        content = read_file_safe(bf)
        if content:
            combined_content += content + "\n"

    if not combined_content:
        return None

    # Detect tools from build files
    plugins = _detect_tools_with_status(
        combined_content, ANDROID_PLUGIN_PATTERNS, is_commented_out_gradle
    )
    deps = _detect_tools_with_status(
        combined_content, ANDROID_TEST_DEPENDENCY_PATTERNS, is_commented_out_gradle
    )

    # Extract versions from build files
    versions = extract_android_versions(combined_content)

    # Scan version catalog for additional tools and versions
    cat_plugins, cat_deps, cat_versions = scan_android_version_catalog(root)

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

    # Scan config files
    config_files = scan_android_config_files(root)

    # Classify tools into Android categories
    categories = classify_android_tools(plugins, deps, config_files)

    # Analyze project structure
    structure = analyze_android_structure(root)

    # Include version catalog content for project type detection
    catalog_path = root / "gradle" / "libs.versions.toml"
    detection_content = combined_content
    catalog_content = read_file_safe(catalog_path)
    if catalog_content:
        detection_content += "\n" + catalog_content

    # Detect project characteristics
    project_type = detect_android_project_type(detection_content)
    is_kmp = detect_is_kmp(detection_content)
    ui_toolkit = detect_ui_toolkit(root, combined_content)

    # Extract tool config
    tool_config = extract_tool_config(combined_content, root)

    has_version_catalog = (root / "gradle" / "libs.versions.toml").exists()

    result = {
        "ecosystem": "android",
        "project": {
            "agp_version": versions.get("agp"),
            "compose_bom_version": versions.get("compose-bom"),
            "android_project_type": project_type,
            "ui_toolkit": ui_toolkit,
            "is_kmp": is_kmp,
            "kotlin_version": versions.get("kotlin"),
            "compile_sdk": versions.get("compile_sdk"),
            "min_sdk": versions.get("min_sdk"),
            "target_sdk": versions.get("target_sdk"),
            "has_version_catalog": has_version_catalog,
            "has_convention_plugins": tool_config.get("has_convention_plugins", False),
            "main_file_count": structure["main_file_count"],
            "test_file_count": structure["test_file_count"],
            "android_test_file_count": structure["android_test_file_count"],
            "common_main_file_count": structure.get("common_main_file_count", 0),
            "common_test_file_count": structure.get("common_test_file_count", 0),
        },
        "detected_tools": categories,
        "config_files": config_files,
        "versions": versions,
        "tool_config": tool_config,
    }

    if recursive:
        result["modules"] = discover_android_modules(root)

    return result


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------


def main():
    """Main entry point for standalone usage."""
    parser = argparse.ArgumentParser(
        description="Android Project Tooling Scanner — detects quality and testing tools"
    )
    parser.add_argument("project_root", help="Path to the project root directory")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively discover Android modules",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}, indent=2))
        sys.exit(1)

    result = scan(root, recursive=args.recursive)

    if result is None:
        print(
            json.dumps(
                {
                    "error": "not_android_project",
                    "message": f"No Android project detected at: {root}",
                    "hint": "Ensure the project has Android Gradle plugins or AndroidManifest.xml",
                },
                indent=2,
            )
        )
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
