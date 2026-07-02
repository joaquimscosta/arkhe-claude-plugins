#!/usr/bin/env python3
"""Build a release-please-config.json dict from a list of package dicts.

Monorepos get include-component-in-tag, tag-separator '-', pre-major bump
flags, and a mutual exclude-paths matrix (each package excludes every other
package's path). Single-package repos get a minimal release-type-only entry.
Stdlib only.
"""

CONFIG_SCHEMA = "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json"

DEFAULT_CHANGELOG_SECTIONS = [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
    {"type": "perf", "section": "Performance Improvements"},
    {"type": "refactor", "section": "Code Refactoring"},
    {"type": "docs", "section": "Documentation"},
    {"type": "test", "section": "Tests"},
    {"type": "ci", "section": "CI/CD"},
    {"type": "security", "section": "Security"},
    {"type": "chore", "section": "Miscellaneous", "hidden": True},
]


def generate_config(packages, *, single, tag_separator="-",
                    changelog_sections=None):
    """Return a release-please-config.json dict.

    packages: list of dicts with keys path, name, release_type, current_version.
    single:   True for a single-package repo (minimal entry, no component tags).
    """
    if changelog_sections is None:
        changelog_sections = DEFAULT_CHANGELOG_SECTIONS

    all_paths = [p["path"] for p in packages]
    out_packages = {}
    for p in packages:
        entry = {
            "release-type": p["release_type"],
            "package-name": p["name"],
        }
        if not single:
            entry["bump-minor-pre-major"] = True
            entry["bump-patch-for-minor-pre-major"] = True
            entry["include-component-in-tag"] = True
            entry["tag-separator"] = tag_separator
            others = [path for path in all_paths if path != p["path"]]
            if others:
                entry["exclude-paths"] = others
        out_packages[p["path"]] = entry

    return {
        "$schema": CONFIG_SCHEMA,
        "packages": out_packages,
        "changelog-sections": changelog_sections,
    }
