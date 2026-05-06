#!/usr/bin/env python3
"""Generate per-plugin AGENTS.md for Codex CLI.

For each plugin under plugins/<plugin>/, walk:
  - skills/<skill>/SKILL.md   -> emit one line per skill (name + description)
  - commands/*.md             -> emit a "Commands as Trigger Phrases" section

The six subagent-heavy commands (spec 004) emit a banner and inline the
agent's prompt verbatim from plugins/<source-plugin>/agents/<agent>.md.

Each generated AGENTS.md is asserted <= 32 KiB (Codex project_doc_max_bytes).
Output: .codex-marketplace/<plugin>/AGENTS.md.

Idempotent. Stdlib only. Python 3.8+.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
OUTPUT_ROOT = REPO_ROOT / ".codex-marketplace"
SIZE_LIMIT_BYTES = 32 * 1024  # 32 KiB
# Cap each inlined agent body for Codex output. Gemini's TOML transpiler keeps
# the full body — Codex's 32 KiB doc limit forces a condensed inline here.
INLINED_AGENT_CHAR_CAP = 1500

BANNER = (
    "On Codex, this command runs inline; the agent it would invoke on "
    "Claude has been collapsed into the prompt body. Behavior is degraded "
    "— no parallel sub-execution."
)

BOOTSTRAP_POINTER = (
    "> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only "
    "tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, "
    "`Agent`) to Codex equivalents.\n"
)

SUBAGENT_HEAVY: Dict[str, Tuple[str, str]] = {
    "plugins/core/commands/debug.md":               ("core", "systematic-debugger"),
    "plugins/core/commands/think.md":               ("core", "deep-think-partner"),
    "plugins/core/commands/research.md":            ("core", "deep-researcher"),
    "plugins/core/commands/double-check.md":        ("core", "code-reviewer"),
    "plugins/spring-boot/commands/spring-review.md":   ("spring-boot", "spring-boot-reviewer"),
    "plugins/spring-boot/commands/verify-upgrade.md":  ("spring-boot", "spring-boot-upgrade-verifier"),
}


# ---------------------------------------------------------------------------
# YAML frontmatter parsing (manual; mirrors validate_skill.py fallback).
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
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
    block_scalar: Optional[str] = None

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


def first_sentence(text: str, max_chars: int = 200) -> str:
    """Return a one-line description trimmed for the skill index."""
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def load_agent_body(source_plugin: str, agent_name: str) -> Optional[str]:
    agent_path = PLUGINS_DIR / source_plugin / "agents" / f"{agent_name}.md"
    if not agent_path.exists():
        return None
    _fm, body = parse_frontmatter(agent_path.read_text(encoding="utf-8"))
    return body.strip()


def condense_agent_body(body: str, source_plugin: str, agent_name: str) -> str:
    """Truncate at INLINED_AGENT_CHAR_CAP at a paragraph boundary.

    Codex enforces 32 KiB per AGENTS.md. Multiple full agent bodies do not
    fit, so include the role-defining intro and point at the canonical file
    for the rest.
    """
    if len(body) <= INLINED_AGENT_CHAR_CAP:
        return body
    cutoff = body.rfind("\n\n", 0, INLINED_AGENT_CHAR_CAP)
    if cutoff < INLINED_AGENT_CHAR_CAP // 2:
        cutoff = INLINED_AGENT_CHAR_CAP
    truncated = body[:cutoff].rstrip()
    pointer = (
        f"\n\n_…full agent body at "
        f"`plugins/{source_plugin}/agents/{agent_name}.md` "
        f"(symlinked into `skills/` for Codex)._"
    )
    return truncated + pointer


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def build_skills_section(plugin_dir: Path) -> str:
    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        return ""
    entries: List[str] = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        fm, _body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        name = fm.get("name", skill_dir.name).strip()
        desc = first_sentence(fm.get("description", ""))
        entries.append(f"- **{name}** — {desc}" if desc else f"- **{name}**")
    if not entries:
        return ""
    body = ["## Skills", ""] + entries + [""]
    return "\n".join(body)


def build_commands_section(plugin_dir: Path) -> str:
    commands_dir = plugin_dir / "commands"
    if not commands_dir.is_dir():
        return ""
    chunks: List[str] = ["## Commands as Trigger Phrases", ""]
    plugin_name = plugin_dir.name
    for md_path in sorted(commands_dir.glob("*.md")):
        rel_path = md_path.relative_to(REPO_ROOT).as_posix()
        name = md_path.stem
        fm, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
        desc = first_sentence(fm.get("description", ""))
        argument_hint = fm.get("argument-hint", "").strip()
        trigger_phrase = f'/{plugin_name}:{name}'
        header = f'### When the user says "{trigger_phrase}"'
        if argument_hint:
            header += f' (args: {argument_hint})'
        chunks.append(header)
        chunks.append("")
        if desc:
            chunks.append(desc)
            chunks.append("")
        body = body.strip()
        if rel_path in SUBAGENT_HEAVY:
            source_plugin, agent_name = SUBAGENT_HEAVY[rel_path]
            agent_body = load_agent_body(source_plugin, agent_name)
            chunks.append(f"> **Note:** {BANNER}")
            chunks.append("")
            chunks.append(body)
            chunks.append("")
            if agent_body is not None:
                condensed = condense_agent_body(agent_body, source_plugin, agent_name)
                chunks.append(f"#### Inlined agent: `{source_plugin}:{agent_name}`")
                chunks.append("")
                chunks.append(condensed)
                chunks.append("")
            else:
                sys.stderr.write(
                    f"warning: agent {source_plugin}:{agent_name} not found "
                    f"for {rel_path}\n"
                )
        else:
            chunks.append(body)
            chunks.append("")
    return "\n".join(chunks)


def build_agents_md(plugin_dir: Path, plugin_meta: Dict[str, str]) -> Tuple[str, Optional[str]]:
    """Build AGENTS.md content. If size exceeds the limit, return a split:
    (skills-only AGENTS.md, commands-only AGENTS.override.md). Otherwise the
    second element is None.
    """
    name = plugin_meta.get("name", plugin_dir.name)
    description = plugin_meta.get("description", "").strip()
    header_parts: List[str] = [
        f"# {name} — Codex AGENTS",
        "",
        BOOTSTRAP_POINTER,
    ]
    if description:
        header_parts.append(description)
        header_parts.append("")
    skills_section = build_skills_section(plugin_dir)
    commands_section = build_commands_section(plugin_dir)

    combined_parts = list(header_parts)
    if skills_section:
        combined_parts.append(skills_section)
    if commands_section:
        combined_parts.append(commands_section)
    combined = "\n".join(combined_parts).rstrip() + "\n"

    if len(combined.encode("utf-8")) <= SIZE_LIMIT_BYTES:
        return combined, None

    # Split: AGENTS.md keeps skills, AGENTS.override.md holds commands.
    primary_parts = list(header_parts)
    primary_parts.append(
        "> **Note:** Commands for this plugin are in `AGENTS.override.md` "
        "(Codex reads both; override takes precedence)."
    )
    primary_parts.append("")
    if skills_section:
        primary_parts.append(skills_section)
    primary = "\n".join(primary_parts).rstrip() + "\n"

    override_parts = [
        f"# {name} — Codex AGENTS (commands override)",
        "",
        BOOTSTRAP_POINTER,
    ]
    if commands_section:
        override_parts.append(commands_section)
    override = "\n".join(override_parts).rstrip() + "\n"

    return primary, override


# ---------------------------------------------------------------------------
# Plugin metadata
# ---------------------------------------------------------------------------

def load_plugin_meta(plugin_dir: Path) -> Dict[str, str]:
    """Read .claude-plugin/plugin.json without importing json's risk surface."""
    import json
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        return {"name": plugin_dir.name, "description": ""}
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"warning: invalid plugin.json at {manifest}: {exc}\n")
        return {"name": plugin_dir.name, "description": ""}
    return {
        "name": data.get("name", plugin_dir.name),
        "description": data.get("description", ""),
        "version": data.get("version", ""),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _write_if_changed(path: Path, encoded: bytes) -> bool:
    if path.exists() and path.read_bytes() == encoded:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return True


def generate_for_plugin(plugin_dir: Path) -> Tuple[Path, int, bool, bool]:
    """Returns (primary_path, primary_size, wrote_any, was_split)."""
    meta = load_plugin_meta(plugin_dir)
    primary, override = build_agents_md(plugin_dir, meta)
    primary_bytes = primary.encode("utf-8")
    primary_size = len(primary_bytes)
    if primary_size > SIZE_LIMIT_BYTES:
        raise SystemExit(
            f"error: {plugin_dir.name}/AGENTS.md is {primary_size} bytes "
            f"(> {SIZE_LIMIT_BYTES} bytes Codex limit) even after splitting "
            f"commands into AGENTS.override.md. Trim skills or split further."
        )
    output_dir = OUTPUT_ROOT / plugin_dir.name
    primary_path = output_dir / "AGENTS.md"
    wrote_primary = _write_if_changed(primary_path, primary_bytes)

    wrote_override = False
    if override is not None:
        override_bytes = override.encode("utf-8")
        override_size = len(override_bytes)
        if override_size > SIZE_LIMIT_BYTES:
            raise SystemExit(
                f"error: {plugin_dir.name}/AGENTS.override.md is "
                f"{override_size} bytes (> {SIZE_LIMIT_BYTES} bytes). "
                f"Trim command bodies or split commands further."
            )
        override_path = output_dir / "AGENTS.override.md"
        wrote_override = _write_if_changed(override_path, override_bytes)
    else:
        # Clean up any stale override file from a prior run.
        stale = output_dir / "AGENTS.override.md"
        if stale.exists():
            stale.unlink()
            wrote_override = True

    return primary_path, primary_size, (wrote_primary or wrote_override), override is not None


def main() -> int:
    if not PLUGINS_DIR.is_dir():
        sys.stderr.write(f"error: {PLUGINS_DIR} not found\n")
        return 1

    total_changed = 0
    total_split = 0
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue
        if not (plugin_dir / ".claude-plugin").is_dir():
            continue
        output_path, size, wrote, was_split = generate_for_plugin(plugin_dir)
        marker = "wrote" if wrote else "unchanged"
        split_marker = " [split commands→AGENTS.override.md]" if was_split else ""
        rel = output_path.relative_to(REPO_ROOT).as_posix()
        print(f"[{plugin_dir.name}] {rel} ({size} bytes, {marker}){split_marker}")
        if wrote:
            total_changed += 1
        if was_split:
            total_split += 1
    print(f"total: {total_changed} plugins changed; {total_split} split")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
