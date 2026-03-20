#!/usr/bin/env python3
"""
Detect SOPS + age environment configuration.

Outputs JSON report of installed tools, age keys, project config,
and .env files. Used by sops-setup skill to determine current state.

Uses only standard library (no external dependencies).

Usage:
    python3 detect_sops.py [project_root]
"""

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd):
    """Run a command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def detect_tool(name):
    """Check if a tool is installed and get its version."""
    path = shutil.which(name)
    if not path:
        return {"installed": False}

    info = {"installed": True, "path": path}

    version_output = run_cmd([name, "--version"])
    if version_output:
        # Extract version number from output
        match = re.search(r"(\d+\.\d+\.\d+)", version_output)
        if match:
            info["version"] = match.group(1)
        else:
            info["version_raw"] = version_output.splitlines()[0]

    return info


def detect_age_key():
    """Check for age key file and extract public key."""
    # age uses XDG_CONFIG_HOME or platform default
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if not config_home:
        if platform.system() == "Darwin":
            config_home = str(Path.home() / "Library" / "Application Support")
        else:
            config_home = str(Path.home() / ".config")

    key_path = Path(config_home) / "sops" / "age" / "keys.txt"

    # Also check SOPS_AGE_KEY_FILE env var
    env_key_path = os.environ.get("SOPS_AGE_KEY_FILE")
    if env_key_path:
        key_path = Path(env_key_path)

    if not key_path.exists():
        return {"exists": False, "expected_path": str(key_path)}

    result = {
        "exists": True,
        "path": str(key_path),
    }

    try:
        content = key_path.read_text()
        # Extract public key from comment line: # public key: age1...
        for line in content.splitlines():
            match = re.match(r"#\s*public key:\s*(age1\S+)", line)
            if match:
                result["public_key"] = match.group(1)
                break
    except OSError:
        result["read_error"] = True

    return result


def detect_sops_yaml(project_root):
    """Check for .sops.yaml and parse its age recipients."""
    sops_path = Path(project_root) / ".sops.yaml"
    if not sops_path.exists():
        return {"exists": False}

    result = {"exists": True, "path": str(sops_path)}

    try:
        content = sops_path.read_text()
        # Extract age public keys from the file
        keys = re.findall(r"(age1[a-z0-9]+)", content)
        if keys:
            result["authorized_keys"] = list(set(keys))
            result["key_count"] = len(set(keys))
    except OSError:
        result["read_error"] = True

    return result


def detect_env_files(project_root):
    """Find .env* files and encrypted YAML files in the project root."""
    root = Path(project_root)
    env_files = []
    encrypted_files = []

    for f in sorted(root.iterdir()):
        if not f.is_file():
            continue
        name = f.name
        if name.endswith(".enc.yaml"):
            encrypted_files.append(name)
        elif name.startswith(".env") and name != ".env.example":
            env_files.append(name)

    return env_files, encrypted_files


def detect_gitignore(project_root):
    """Check .gitignore for .env and .encrypted rules."""
    gitignore_path = Path(project_root) / ".gitignore"
    if not gitignore_path.exists():
        return {"exists": False, "ignores_env": False, "ignores_encrypted": False}

    try:
        content = gitignore_path.read_text()
        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        ignores_env = any(
            pattern in lines
            for pattern in (".env", ".env*", ".env.*", ".env.local")
        )

        ignores_encrypted = any(
            "enc.yaml" in line or "encrypted" in line for line in lines
        )

        return {
            "exists": True,
            "ignores_env": ignores_env,
            "ignores_encrypted": ignores_encrypted,
        }
    except OSError:
        return {"exists": True, "ignores_env": False, "ignores_encrypted": False}


def detect_os():
    """Detect operating system for install instructions."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    return system


def detect(project_root):
    """Run all detection checks and return structured results."""
    env_files, encrypted_files = detect_env_files(project_root)

    return {
        "tools": {
            "sops": detect_tool("sops"),
            "age": detect_tool("age"),
        },
        "age_key": detect_age_key(),
        "project": {
            "sops_yaml": detect_sops_yaml(project_root),
            "env_files": env_files,
            "encrypted_files": encrypted_files,
            "gitignore": detect_gitignore(project_root),
        },
        "os": detect_os(),
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
