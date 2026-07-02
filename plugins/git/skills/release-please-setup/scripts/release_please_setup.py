#!/usr/bin/env python3
"""Orchestrate release-please setup: discover -> generate config -> seed manifest.

Usage:
  release_please_setup.py --root . [--globs packages/*,backend/*] \
      [--migrate] [--single] [--initial 0.0.0] [--dry-run] [--out-dir .]

Writes release-please-config.json and .release-please-manifest.json (or prints
them with --dry-run). Deploy/publish workflow templates are copied separately
per WORKFLOW.md, not by this script. Stdlib only.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover_packages import discover_packages
from generate_config import generate_config
from seed_manifest import seed_manifest

DEFAULT_GLOBS = ["packages/*", "backend/*", "frontend/*"]
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def version_from_git_tag(root, name):
    """Best-effort: highest semver from git tags like '<name>-v1.2.3'. None on failure."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "tag", "--list", f"{name}-v*"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    best = None
    for tag in out.split():
        ver = tag[len(name) + 2:] if tag.startswith(f"{name}-v") else None
        if ver and SEMVER_RE.match(ver):
            key = tuple(int(x) for x in ver.split("."))
            if best is None or key > best[0]:
                best = (key, ver)
    return best[1] if best else None


def build_artifacts(root, *, globs, single, mode, initial="0.0.0"):
    """Return (config_dict, manifest_dict). In migration mode, fill missing
    versions from git tags before seeding."""
    packages = discover_packages(root, globs)
    if mode == "migration":
        for p in packages:
            if not p["current_version"]:
                p["current_version"] = version_from_git_tag(root, p["name"])
    single = single or len(packages) <= 1
    config = generate_config(packages, single=single)
    manifest = seed_manifest(packages, mode=mode, initial=initial)
    return config, manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description="Set up release-please for a repo.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--globs", default=",".join(DEFAULT_GLOBS))
    ap.add_argument("--migrate", action="store_true")
    ap.add_argument("--single", action="store_true")
    ap.add_argument("--initial", default="0.0.0")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)

    globs = [g.strip() for g in args.globs.split(",") if g.strip()]
    mode = "migration" if args.migrate else "greenfield"
    config, manifest = build_artifacts(
        args.root, globs=globs, single=args.single, mode=mode, initial=args.initial
    )

    config_text = json.dumps(config, indent=2) + "\n"
    manifest_text = json.dumps(manifest, indent=2) + "\n"

    if args.dry_run:
        print("=== release-please-config.json ===")
        print(config_text)
        print("=== .release-please-manifest.json ===")
        print(manifest_text)
        return 0

    out = Path(args.out_dir or args.root)
    (out / "release-please-config.json").write_text(config_text)
    (out / ".release-please-manifest.json").write_text(manifest_text)
    print(f"Wrote release-please-config.json and .release-please-manifest.json to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
