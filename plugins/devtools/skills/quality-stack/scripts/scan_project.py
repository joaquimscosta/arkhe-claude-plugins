#!/usr/bin/env python3
"""
Multi-Ecosystem Project Scanner (Orchestrator)

Auto-detects project ecosystems (JVM, Node.js, Python) and runs the
appropriate scanners. Merges results into a unified JSON output.

Uses only standard library (no external dependencies). Python 3.8+.

Usage:
    python3 scan_project.py <project_root>
    python3 scan_project.py --recursive <project_root>
    python3 scan_project.py --ecosystem jvm <project_root>
    python3 scan_project.py --ecosystem node <project_root>
    python3 scan_project.py --ecosystem python <project_root>

Output:
    JSON with ecosystems array, cross_cutting section, and optional modules.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import SKIP_DIRS


# ---------------------------------------------------------------------------
# Ecosystem detection
# ---------------------------------------------------------------------------

# Marker files for each ecosystem
JVM_MARKERS = {"build.gradle.kts", "build.gradle", "pom.xml"}
NODE_MARKERS = {"package.json"}
PYTHON_MARKERS = {"pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"}

# Android plugin patterns to detect in Gradle build files
ANDROID_BUILD_PATTERNS = [
    r"com\.android\.application",
    r"com\.android\.library",
    r"com\.android\.kotlin\.multiplatform\.library",
]


def detect_ecosystems(root: Path) -> List[Dict[str, str]]:
    """Auto-detect project ecosystems at the root and in subdirectories.

    Returns a list of dicts with 'ecosystem' and 'root' keys.
    For monorepos, may detect multiple ecosystems in different directories.
    """
    found = []
    seen_roots: Set[str] = set()

    def _check_dir(directory: Path) -> None:
        dir_str = str(directory.resolve())
        if dir_str in seen_roots:
            return
        seen_roots.add(dir_str)  # Mark visited before processing to prevent duplicates

        entries = set()
        try:
            entries = {e.name for e in directory.iterdir() if e.is_file()}
        except Exception:
            return

        rel_path = str(directory.relative_to(root)) if directory != root else "."

        if entries & JVM_MARKERS:
            found.append({"ecosystem": "jvm", "root": rel_path})

            # Check if this JVM project is also an Android project
            _android_detected = False
            for gradle_name in ["build.gradle.kts", "build.gradle"]:
                gradle_file = directory / gradle_name
                if gradle_file.exists():
                    try:
                        gradle_content = gradle_file.read_text(encoding="utf-8")
                        for pattern in ANDROID_BUILD_PATTERNS:
                            if re.search(pattern, gradle_content):
                                _android_detected = True
                                break
                    except Exception:
                        pass
                if _android_detected:
                    break

            # Also check version catalog for AGP plugins
            if not _android_detected:
                catalog = directory / "gradle" / "libs.versions.toml"
                if catalog.exists():
                    try:
                        cat_content = catalog.read_text(encoding="utf-8")
                        for pattern in ANDROID_BUILD_PATTERNS:
                            if re.search(pattern, cat_content):
                                _android_detected = True
                                break
                    except Exception:
                        pass

            # Check for AndroidManifest.xml as fallback
            if not _android_detected:
                manifest_globs = [
                    "src/main/AndroidManifest.xml",
                    "*/src/main/AndroidManifest.xml",
                    "app/src/main/AndroidManifest.xml",
                    "androidApp/src/main/AndroidManifest.xml",
                ]
                for glob_pat in manifest_globs:
                    if list(directory.glob(glob_pat)):
                        _android_detected = True
                        break

            if _android_detected:
                found.append({"ecosystem": "android", "root": rel_path})

        if entries & NODE_MARKERS:
            # Only count as Node ecosystem if it has actual source files
            # (not just a package.json for tooling like lefthook)
            pkg_path = directory / "package.json"
            is_real_node_project = False
            try:
                content = pkg_path.read_text(encoding="utf-8")
                data = json.loads(content)
                # Has dependencies, scripts, or workspaces -> real project
                has_deps = bool(data.get("dependencies") or data.get("devDependencies"))
                has_scripts = bool(data.get("scripts"))
                has_workspaces = bool(data.get("workspaces"))
                # Has a tsconfig or src directory -> real project
                has_ts = (directory / "tsconfig.json").exists()
                has_src = (directory / "src").is_dir() or (directory / "app").is_dir()
                is_real_node_project = has_deps and (has_scripts or has_workspaces or has_ts or has_src)
            except Exception:
                pass

            if is_real_node_project:
                found.append({"ecosystem": "node", "root": rel_path})

        if entries & PYTHON_MARKERS:
            found.append({"ecosystem": "python", "root": rel_path})

    # Check root
    _check_dir(root)

    # Check immediate subdirectories
    try:
        for entry in root.iterdir():
            if entry.is_dir() and entry.name not in SKIP_DIRS:
                _check_dir(entry)
    except Exception:
        pass

    # Check common monorepo patterns (two levels deep)
    monorepo_prefixes = [
        "apps", "packages", "services", "modules", "libs",
        "frontend", "backend", "web", "api", "server", "client",
    ]
    for prefix in monorepo_prefixes:
        prefix_dir = root / prefix
        if prefix_dir.is_dir():
            try:
                for entry in prefix_dir.iterdir():
                    if entry.is_dir() and entry.name not in SKIP_DIRS:
                        _check_dir(entry)
            except Exception:
                pass

    return found


# ---------------------------------------------------------------------------
# Scanner dispatch
# ---------------------------------------------------------------------------


def run_jvm_scanner(root: Path, project_root: str, recursive: bool) -> Optional[dict]:
    """Run the JVM scanner on a directory."""
    try:
        from scan_jvm import scan
        result = scan(root, recursive=recursive)
        if result is not None:
            result["root"] = project_root
        return result
    except Exception as e:
        return {"ecosystem": "jvm", "root": project_root, "error": str(e)}


def run_node_scanner(root: Path, project_root: str) -> Optional[dict]:
    """Run the Node.js scanner on a directory."""
    try:
        from scan_node import scan
        result = scan(root)
        if result is not None:
            result["root"] = project_root
        return result
    except ImportError:
        # Node scanner not yet implemented
        return {
            "ecosystem": "node",
            "root": project_root,
            "error": "Node.js scanner not yet available (scan_node.py)",
        }
    except Exception as e:
        return {"ecosystem": "node", "root": project_root, "error": str(e)}


def run_python_scanner(root: Path, project_root: str) -> Optional[dict]:
    """Run the Python scanner on a directory."""
    try:
        from scan_python import scan
        result = scan(root)
        if result is not None:
            result["root"] = project_root
        return result
    except ImportError:
        # Python scanner not yet implemented
        return {
            "ecosystem": "python",
            "root": project_root,
            "error": "Python scanner not yet available (scan_python.py)",
        }
    except Exception as e:
        return {"ecosystem": "python", "root": project_root, "error": str(e)}


def run_android_scanner(root: Path, project_root: str, recursive: bool) -> Optional[dict]:
    """Run the Android scanner on a directory."""
    try:
        from scan_android import scan
        result = scan(root, recursive=recursive)
        if result is not None:
            result["root"] = project_root
        return result
    except ImportError:
        return {
            "ecosystem": "android",
            "root": project_root,
            "error": "Android scanner not yet available (scan_android.py)",
        }
    except Exception as e:
        return {"ecosystem": "android", "root": project_root, "error": str(e)}


def run_cross_cutting_scanner(root: Path) -> dict:
    """Run the cross-cutting scanner."""
    try:
        from scan_cross_cutting import scan
        return scan(root)
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def scan_project(
    root: Path,
    recursive: bool = False,
    ecosystem_filter: Optional[str] = None,
) -> dict:
    """Orchestrate scanning across all detected ecosystems.

    Args:
        root: Project root directory.
        recursive: Enable recursive scanning for monorepos.
        ecosystem_filter: If set, only scan this ecosystem ('jvm', 'node', 'python').

    Returns:
        Unified JSON output with ecosystems array and cross_cutting section.
    """
    # Detect ecosystems
    if ecosystem_filter:
        # User explicitly specified an ecosystem
        ecosystems_found = [{"ecosystem": ecosystem_filter, "root": "."}]
    else:
        ecosystems_found = detect_ecosystems(root)

    if not ecosystems_found:
        # No ecosystem detected — provide hints
        hint_files = []
        for pattern in ["*/build.gradle.kts", "*/build.gradle", "*/pom.xml",
                        "*/package.json", "*/pyproject.toml"]:
            found = list(root.glob(pattern))[:3]
            hint_files.extend(str(f.relative_to(root)) for f in found)

        return {
            "error": "no_ecosystem_detected",
            "message": f"No JVM, Android, Node.js, or Python project detected at: {root}",
            "hint": "Try --recursive flag or pass a subproject path directly",
            "nearby_project_files": hint_files,
        }

    # Run ecosystem-specific scanners
    ecosystem_results = []
    for eco in ecosystems_found:
        eco_type = eco["ecosystem"]
        eco_root_str = eco["root"]
        eco_root = root / eco_root_str if eco_root_str != "." else root

        if eco_type == "jvm":
            result = run_jvm_scanner(eco_root, eco_root_str, recursive)
        elif eco_type == "android":
            result = run_android_scanner(eco_root, eco_root_str, recursive)
        elif eco_type == "node":
            result = run_node_scanner(eco_root, eco_root_str)
        elif eco_type == "python":
            result = run_python_scanner(eco_root, eco_root_str)
        else:
            continue

        if result is not None:
            ecosystem_results.append(result)

    # Run cross-cutting scanner (always at project root)
    cross_cutting = run_cross_cutting_scanner(root)

    # Build unified output
    output = {
        "ecosystems": ecosystem_results,
        "cross_cutting": cross_cutting,
    }

    # Summary of detected ecosystems
    output["summary"] = {
        "ecosystems_detected": [e["ecosystem"] for e in ecosystems_found],
        "ecosystem_count": len(ecosystems_found),
    }

    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Ecosystem Project Scanner — auto-detects and scans JVM, Android, Node.js, Python"
    )
    parser.add_argument("project_root", help="Path to the project root directory")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively discover projects in subdirectories (for monorepos)",
    )
    parser.add_argument(
        "--ecosystem",
        choices=["jvm", "android", "node", "python"],
        help="Force scanning a specific ecosystem (skip auto-detection)",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}, indent=2))
        sys.exit(1)

    result = scan_project(root, recursive=args.recursive, ecosystem_filter=args.ecosystem)

    # Exit with error code if no ecosystems found
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
