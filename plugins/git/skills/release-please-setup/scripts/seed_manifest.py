#!/usr/bin/env python3
"""Build a .release-please-manifest.json dict from package dicts.

greenfield: every package starts at `initial` (default 0.0.0).
migration:  use each package's detected current_version, falling back to
            `initial` when none was found. This is what lets an existing
            manual-tag repo (e.g. papia-studio) adopt release-please without
            resetting versions. Stdlib only.
"""


def seed_manifest(packages, *, mode, initial="0.0.0"):
    """Return { "<path>": "<version>" } for all packages."""
    if mode not in ("greenfield", "migration"):
        raise ValueError(f"mode must be 'greenfield' or 'migration', got {mode!r}")
    manifest = {}
    for p in packages:
        if mode == "migration" and p.get("current_version"):
            manifest[p["path"]] = p["current_version"]
        else:
            manifest[p["path"]] = initial
    return manifest
