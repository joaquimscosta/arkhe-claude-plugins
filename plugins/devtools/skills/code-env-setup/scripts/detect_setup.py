#!/usr/bin/env python3
"""
Detect existing Claude Code environment configuration.

Outputs JSON report of what is already configured at both the global
(~/.claude/) and project (.claude/) levels. Used by the code-env-setup
skill to determine what needs to be set up.

Usage:
    python3 detect_setup.py [project_root]
"""

import json
import os
import sys
from pathlib import Path


def check_file(path):
    """Check if a file exists and return basic metadata."""
    p = Path(path).expanduser()
    if p.exists() and p.is_file():
        return {"exists": True, "path": str(p), "size_bytes": p.stat().st_size}
    return {"exists": False}


def check_dir(path):
    """Check if a directory exists and count its contents."""
    p = Path(path).expanduser()
    if p.exists() and p.is_dir():
        count = sum(1 for f in p.iterdir() if f.is_file())
        return {"exists": True, "count": count}
    return {"exists": False}


def check_settings_json(path):
    """Check settings.json for hooks and language configuration."""
    p = Path(path).expanduser()
    result = {"exists": False, "has_hooks": False, "has_language": False}
    if p.exists() and p.is_file():
        result["exists"] = True
        try:
            with open(p) as f:
                data = json.load(f)
            result["has_hooks"] = "hooks" in data and bool(data["hooks"])
            result["has_language"] = "language" in data
        except (json.JSONDecodeError, OSError):
            pass
    return result


def check_gitignore_has_env(path):
    """Check if .gitignore contains .env rule."""
    p = Path(path)
    if not p.exists():
        return {"exists": False, "has_env_rule": False}
    try:
        content = p.read_text()
        has_env = any(
            line.strip() in (".env", ".env*", ".env.*", ".env.local")
            for line in content.splitlines()
            if not line.strip().startswith("#")
        )
        return {"exists": True, "has_env_rule": has_env}
    except OSError:
        return {"exists": True, "has_env_rule": False}


def check_claude_dir(path):
    """Check .claude/ directory for skills, agents, commands subdirs."""
    p = Path(path)
    result = {"exists": p.exists() and p.is_dir()}
    if result["exists"]:
        result["has_skills"] = (p / "skills").is_dir()
        result["has_agents"] = (p / "agents").is_dir()
        result["has_commands"] = (p / "commands").is_dir()
    else:
        result["has_skills"] = False
        result["has_agents"] = False
        result["has_commands"] = False
    return result


def detect(project_root):
    """Run all detection checks and return structured results."""
    home = Path.home()
    proj = Path(project_root)

    return {
        "global": {
            "claude_md": check_file(home / ".claude" / "CLAUDE.md"),
            "settings_json": check_settings_json(
                home / ".claude" / "settings.json"
            ),
            "keybindings_json": check_file(
                home / ".claude" / "keybindings.json"
            ),
            "hooks_dir": check_dir(home / ".claude" / "hooks"),
            "agents_dir": check_dir(home / ".claude" / "agents"),
        },
        "project": {
            "claude_md": check_file(proj / "CLAUDE.md"),
            "claude_dir": check_claude_dir(proj / ".claude"),
            "env_example": check_file(proj / ".env.example"),
            "gitignore": check_gitignore_has_env(proj / ".gitignore"),
            "src_dir": {"exists": (proj / "src").is_dir()},
            "tests_dir": {"exists": (proj / "tests").is_dir()},
            "docs_dir": {"exists": (proj / "docs").is_dir()},
            "scripts_dir": {"exists": (proj / "scripts").is_dir()},
        },
    }


def main():
    project_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    if not Path(project_root).is_dir():
        json.dump(
            {"error": "not_a_directory", "path": project_root},
            sys.stdout,
            indent=2,
        )
        sys.exit(1)

    result = detect(project_root)
    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
