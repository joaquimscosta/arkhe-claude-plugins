#!/usr/bin/env python3
"""Transpile Claude .md commands to Gemini .toml commands.

Walks every plugins/<plugin>/commands/*.md and emits
.gemini-extensions/<plugin>/commands/<name>.toml.

Frontmatter description becomes a TOML description field; the markdown body
becomes the TOML prompt field as a multi-line basic string. Placeholders
$ARGUMENTS and {{name}} are converted to {{args}}.

Subagent-heavy commands (the six identified in spec 004) emit a banner at
the top of the prompt body and inline the agent's prompt verbatim from
plugins/<source-plugin>/agents/<agent-name>.md.

Idempotent: re-running produces no diff. Stdlib only, Python 3.8+.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
OUTPUT_ROOT = REPO_ROOT / ".gemini-extensions"

BANNER = (
    "On Gemini, this command runs inline; the agent it would invoke on "
    "Claude has been collapsed into the prompt body. Behavior is degraded "
    "— no parallel sub-execution."
)

# Commands that dispatch subagents on Claude. Maps a command path
# (relative to repo root) to the source plugin and agent file name.
SUBAGENT_HEAVY: Dict[str, Tuple[str, str]] = {
    "plugins/core/commands/debug.md":               ("core", "systematic-debugger"),
    "plugins/core/commands/think.md":               ("core", "deep-think-partner"),
    "plugins/core/commands/research.md":            ("core", "deep-researcher"),
    "plugins/core/commands/double-check.md":        ("core", "code-reviewer"),
    "plugins/spring-boot/commands/spring-review.md":   ("spring-boot", "spring-boot-reviewer"),
    "plugins/spring-boot/commands/verify-upgrade.md":  ("spring-boot", "spring-boot-upgrade-verifier"),
}


# ---------------------------------------------------------------------------
# YAML frontmatter parsing (manual; stdlib only).
# Mirrors the fallback approach in skill-validator/scripts/validate_skill.py.
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """Parse YAML frontmatter and return (fields, body).

    Returns ({}, content) if no frontmatter is found.
    """
    if not content.startswith("---"):
        return {}, content

    match = re.match(r"^---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        return {}, content

    frontmatter_text = match.group(1)
    body = content[match.end():]

    fields: Dict[str, str] = {}
    current_key: Optional[str] = None
    current_value: list = []
    block_scalar: Optional[str] = None  # '>' folded, '|' literal

    def store() -> None:
        if current_key is None:
            return
        if block_scalar == ">":
            text = " ".join(line.strip() for line in current_value if line.strip())
        elif block_scalar == "|":
            text = "\n".join(current_value)
        else:
            text = "\n".join(current_value)
        fields[current_key] = text.strip()

    for line in frontmatter_text.split("\n"):
        if ":" in line and not line.startswith((" ", "\t")):
            store()
            key, _, value = line.partition(":")
            current_key = key.strip()
            value = value.strip()
            if value in (">", "|", ">-", "|-"):
                block_scalar = value[0]
                current_value = []
            else:
                block_scalar = None
                current_value = [value] if value else []
        elif current_key is not None:
            current_value.append(line)

    store()
    return fields, body


# ---------------------------------------------------------------------------
# Transformations
# ---------------------------------------------------------------------------

def convert_placeholders(body: str) -> str:
    """Convert Claude command placeholders to Gemini's `{{args}}`."""
    body = body.replace("$ARGUMENTS", "{{args}}")
    # `{{name}}` (any unquoted identifier inside double-braces) -> `{{args}}`.
    # Only convert single-token names; leave handlebars-style helpers alone.
    body = re.sub(r"\{\{\s*([a-zA-Z_][\w-]*)\s*\}\}", "{{args}}", body)
    return body


def load_agent_body(source_plugin: str, agent_name: str) -> Optional[str]:
    """Load and return the body of an agent file, frontmatter stripped."""
    agent_path = PLUGINS_DIR / source_plugin / "agents" / f"{agent_name}.md"
    if not agent_path.exists():
        return None
    _frontmatter, agent_body = parse_frontmatter(agent_path.read_text(encoding="utf-8"))
    return agent_body.strip()


def build_prompt(rel_path: str, body: str) -> str:
    """Apply banner-and-inline treatment for subagent-heavy commands."""
    body = body.strip()
    if rel_path in SUBAGENT_HEAVY:
        source_plugin, agent_name = SUBAGENT_HEAVY[rel_path]
        agent_body = load_agent_body(source_plugin, agent_name)
        if agent_body is None:
            sys.stderr.write(
                f"warning: subagent-heavy command {rel_path} references "
                f"agent {source_plugin}:{agent_name} that does not exist\n"
            )
        else:
            body = (
                f"> **Note:** {BANNER}\n\n"
                f"{body}\n\n"
                f"---\n\n"
                f"## Inlined agent: `{source_plugin}:{agent_name}`\n\n"
                f"{agent_body}\n"
            )
    return convert_placeholders(body)


# ---------------------------------------------------------------------------
# TOML emission (manual; no third-party tomli_w)
# ---------------------------------------------------------------------------

def escape_basic_string(value: str) -> str:
    """Escape a string for use in a TOML basic single-quoted string literal."""
    # TOML basic strings: backslash-escape control chars and double quotes.
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def render_toml(description: str, prompt: str) -> str:
    """Render the two-key TOML output."""
    desc_line = f'description = "{escape_basic_string(description)}"\n'
    # Use multi-line basic string for prompt; close marker on its own line.
    # Escape any triple-quote sequences in the body to avoid premature close.
    safe_prompt = prompt.replace('"""', '\\"""')
    prompt_block = f'prompt = """\n{safe_prompt}\n"""\n'
    return desc_line + prompt_block


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def transpile_command(md_path: Path) -> Tuple[Path, bool]:
    """Transpile one command file. Returns (output_path, wrote_changes)."""
    rel_path = md_path.relative_to(REPO_ROOT).as_posix()
    parts = md_path.relative_to(PLUGINS_DIR).parts
    plugin_name = parts[0]
    command_name = md_path.stem

    content = md_path.read_text(encoding="utf-8")
    fields, body = parse_frontmatter(content)
    description = fields.get("description", "").strip()
    prompt = build_prompt(rel_path, body)

    output_dir = OUTPUT_ROOT / plugin_name / "commands"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{command_name}.toml"

    new_content = render_toml(description, prompt)
    if output_path.exists() and output_path.read_text(encoding="utf-8") == new_content:
        return output_path, False
    output_path.write_text(new_content, encoding="utf-8")
    return output_path, True


def main() -> int:
    if not PLUGINS_DIR.is_dir():
        sys.stderr.write(f"error: {PLUGINS_DIR} not found\n")
        return 1

    counts: Dict[str, int] = {}
    changed_total = 0
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue
        commands_dir = plugin_dir / "commands"
        if not commands_dir.is_dir():
            counts[plugin_dir.name] = 0
            continue
        n = 0
        for md_path in sorted(commands_dir.glob("*.md")):
            _output, wrote = transpile_command(md_path)
            if wrote:
                changed_total += 1
            n += 1
        counts[plugin_dir.name] = n

    for plugin, n in counts.items():
        print(f"[{plugin}] {n} commands transpiled")
    print(f"total: {sum(counts.values())} commands; {changed_total} files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
