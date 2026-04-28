#!/usr/bin/env python3
"""
Resolve the research documents directory with JD-aware path detection.

Checks for .jd-config.json to find the research area (e.g. docs/30-research/),
falling back to docs/research/ if no JD structure exists.

Usage:
    resolve_research_path.py [--project-root DIR] [--format text|json]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import resolve_research_path, find_project_root


def main():
    parser = argparse.ArgumentParser(
        description="Resolve the research documents directory path"
    )
    parser.add_argument(
        "--project-root", type=str, default=None,
        help="Project root directory (default: auto-detect via git)"
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else None
    result = resolve_research_path(project_root)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        path = result["path"]
        if result["jd_aware"]:
            print(f"{path}  (JD area {result['prefix']}-{result['area_name']})")
        else:
            print(f"{path}  (default, no .jd-config.json)")


if __name__ == "__main__":
    main()
