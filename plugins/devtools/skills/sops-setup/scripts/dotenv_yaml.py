#!/usr/bin/env python3
"""
Convert between dotenv and YAML formats for SOPS encryption.

SOPS dotenv store has a known bug (#1435) that corrupts backslash and
newline sequences. This script converts .env files to YAML for safe
encryption, and converts decrypted YAML back to dotenv format.

Uses only standard library (no external dependencies).

Usage:
    # dotenv → yaml (for encryption)
    python3 dotenv_yaml.py to-yaml .env.local > .env.local.yaml

    # yaml → dotenv (after decryption)
    python3 dotenv_yaml.py to-dotenv .env.local.yaml > .env.local

    # Round-trip test
    python3 dotenv_yaml.py test .env.local
"""

import re
import sys
from pathlib import Path


def dotenv_to_yaml(content: str) -> str:
    """Convert dotenv format to YAML key-value pairs.

    Handles:
    - KEY=value (unquoted)
    - KEY="value" (double-quoted, preserves escapes)
    - KEY='value' (single-quoted, literal)
    - Comments (# ...) — preserved as YAML comments
    - Empty lines — preserved
    - export KEY=value — strips export prefix
    """
    lines = []
    for line in content.splitlines():
        stripped = line.strip()

        # Empty lines and comments pass through
        if not stripped or stripped.startswith("#"):
            lines.append(line)
            continue

        # Strip optional 'export ' prefix
        if stripped.startswith("export "):
            stripped = stripped[7:].strip()

        # Parse KEY=VALUE
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)", stripped)
        if not match:
            # Not a valid env line, keep as comment
            lines.append(f"# {line}")
            continue

        key = match.group(1)
        raw_value = match.group(2)

        # Remove surrounding quotes if present
        if len(raw_value) >= 2:
            if raw_value[0] == '"' and raw_value[-1] == '"':
                raw_value = raw_value[1:-1]
            elif raw_value[0] == "'" and raw_value[-1] == "'":
                raw_value = raw_value[1:-1]

        # YAML quoting: always double-quote to preserve special chars
        # Escape backslashes and double quotes for YAML
        yaml_value = raw_value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{key}: "{yaml_value}"')

    return "\n".join(lines) + "\n"


def yaml_to_dotenv(content: str) -> str:
    """Convert simple YAML key-value pairs back to dotenv format.

    Handles the subset of YAML produced by dotenv_to_yaml:
    - KEY: "value" (quoted string)
    - KEY: value (unquoted)
    - Comments and empty lines preserved
    - Ignores sops metadata block
    """
    lines = []
    in_sops_block = False

    for line in content.splitlines():
        stripped = line.strip()

        # Skip sops metadata block
        if stripped == "sops:":
            in_sops_block = True
            continue
        if in_sops_block:
            if stripped and not stripped.startswith("#") and not line.startswith(" ") and not line.startswith("\t"):
                in_sops_block = False
            else:
                continue

        # Empty lines and comments pass through
        if not stripped or stripped.startswith("#"):
            lines.append(line)
            continue

        # Parse YAML KEY: VALUE
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)', stripped)
        if not match:
            continue

        key = match.group(1)
        raw_value = match.group(2).strip()

        # Remove YAML quotes
        if len(raw_value) >= 2:
            if raw_value[0] == '"' and raw_value[-1] == '"':
                raw_value = raw_value[1:-1]
                # Unescape YAML double-quote escapes
                raw_value = raw_value.replace('\\"', '"').replace("\\\\", "\\")
            elif raw_value[0] == "'" and raw_value[-1] == "'":
                raw_value = raw_value[1:-1]

        # Quote in dotenv if value contains special chars
        needs_quoting = any(c in raw_value for c in ' "\'\\$`!#&|;')
        if needs_quoting:
            escaped = raw_value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={raw_value}")

    return "\n".join(lines) + "\n"


def round_trip_test(filepath: str) -> bool:
    """Test that a dotenv file survives round-trip conversion."""
    original = Path(filepath).read_text()
    yaml_content = dotenv_to_yaml(original)
    restored = yaml_to_dotenv(yaml_content)

    # Compare key=value pairs (ignoring whitespace differences)
    def parse_env(text):
        pairs = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)", line)
            if match:
                pairs[match.group(1)] = match.group(2)
        return pairs

    original_pairs = parse_env(original)
    restored_pairs = parse_env(restored)

    if original_pairs == restored_pairs:
        print(f"PASS: {len(original_pairs)} key-value pairs preserved", file=sys.stderr)
        return True
    else:
        missing = set(original_pairs) - set(restored_pairs)
        added = set(restored_pairs) - set(original_pairs)
        changed = {
            k for k in original_pairs.keys() & restored_pairs.keys()
            if original_pairs[k] != restored_pairs[k]
        }
        if missing:
            print(f"FAIL: Missing keys: {missing}", file=sys.stderr)
        if added:
            print(f"FAIL: Extra keys: {added}", file=sys.stderr)
        if changed:
            print(f"FAIL: Changed values: {changed}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 3:
        print(
            "Usage:\n"
            "  dotenv_yaml.py to-yaml <file>    # Convert .env to YAML (stdout)\n"
            "  dotenv_yaml.py to-dotenv <file>   # Convert YAML to .env (stdout)\n"
            "  dotenv_yaml.py test <file>         # Round-trip test a .env file",
            file=sys.stderr,
        )
        sys.exit(1)

    command = sys.argv[1]
    filepath = sys.argv[2]
    content = Path(filepath).read_text()

    if command == "to-yaml":
        print(dotenv_to_yaml(content), end="")
    elif command == "to-dotenv":
        print(yaml_to_dotenv(content), end="")
    elif command == "test":
        success = round_trip_test(filepath)
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
