#!/usr/bin/env python3
"""Discover packages in a repo and detect their release-type and current version.

Stdlib only. Used by release_please_setup.py to build the release-please config
and manifest. Version detection here is file-based and pure (no git); the
orchestrator handles git-tag fallback for migration mode.
"""

import json
import re
from glob import glob
from pathlib import Path

GRADLE_FILES = ("build.gradle", "build.gradle.kts")


def detect_release_type(pkg_dir):
    """Return 'node' | 'python' | 'simple' for a package directory."""
    pkg_dir = Path(pkg_dir)
    if (pkg_dir / "package.json").is_file():
        return "node"
    if (pkg_dir / "pyproject.toml").is_file():
        return "python"
    if any((pkg_dir / g).is_file() for g in GRADLE_FILES):
        return "simple"
    return "simple"


def _version_from_pyproject(text):
    """Extract version from a [project] or [tool.poetry] table."""
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line.strip("[]")
            continue
        if section in ("project", "tool.poetry"):
            m = re.match(r"""version\s*=\s*["']([^"']+)["']""", line)
            if m:
                return m.group(1)
    return None


def detect_version(pkg_dir, release_type):
    """Return the current version string from package files, or None."""
    pkg_dir = Path(pkg_dir)
    if release_type == "node":
        pj = pkg_dir / "package.json"
        if pj.is_file():
            try:
                return json.loads(pj.read_text()).get("version")
            except json.JSONDecodeError:
                return None
    if release_type == "python":
        pp = pkg_dir / "pyproject.toml"
        if pp.is_file():
            return _version_from_pyproject(pp.read_text())
    if release_type == "simple":
        gp = pkg_dir / "gradle.properties"
        if gp.is_file():
            m = re.search(r"^\s*version\s*=\s*(.+?)\s*$", gp.read_text(), re.MULTILINE)
            if m:
                return m.group(1).strip().strip("'\"")
    return None


def _name_for(pkg_dir, release_type):
    pkg_dir = Path(pkg_dir)
    if release_type == "node":
        pj = pkg_dir / "package.json"
        if pj.is_file():
            try:
                name = json.loads(pj.read_text()).get("name") or pkg_dir.name
                return name.split("/")[-1]  # strip @scope/
            except json.JSONDecodeError:
                pass
    return pkg_dir.name


def discover_packages(root, globs):
    """Scan `globs` under `root` and return a sorted list of package dicts."""
    root = Path(root)
    seen = {}
    for pattern in globs:
        for match in glob(str(root / pattern)):
            d = Path(match)
            if not d.is_dir():
                continue
            rel = d.relative_to(root).as_posix()
            if rel in seen:
                continue
            rtype = detect_release_type(d)
            seen[rel] = {
                "path": rel,
                "name": _name_for(d, rtype),
                "release_type": rtype,
                "current_version": detect_version(d, rtype),
            }
    return [seen[k] for k in sorted(seen)]
