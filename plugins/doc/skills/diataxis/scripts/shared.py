#!/usr/bin/env python3
"""
Shared utilities for diataxis scripts.

Common helpers for quadrant classification, config loading, doc scanning,
and result formatting. Uses only standard library. Python 3.11+.
"""

import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# The four Diataxis quadrants
QUADRANTS: dict[str, dict[str, str]] = {
    "tutorial": {
        "folder": "tutorials",
        "description": "Learning-oriented, step-by-step lessons",
        "short": "Step-by-step lessons",
    },
    "how-to": {
        "folder": "how-to",
        "description": "Task-oriented, practical problem-solving guides",
        "short": "Practical guides",
    },
    "reference": {
        "folder": "reference",
        "description": "Information-oriented, technical descriptions",
        "short": "Technical descriptions",
    },
    "explanation": {
        "folder": "explanation",
        "description": "Understanding-oriented, conceptual discussions",
        "short": "Conceptual discussions",
    },
}

# Signal tables for classification — each quadrant has four signal types
QUADRANT_SIGNALS: dict[str, dict[str, list[str]]] = {
    "tutorial": {
        "title_keywords": [
            "tutorial", "getting-started", "learn", "beginner", "introduction",
            "first-steps", "walkthrough", "lesson", "workshop", "starter",
            "quickstart", "quick-start", "onboarding", "crash-course",
        ],
        "heading_patterns": [
            r"step\s+\d+", r"prerequisites?", r"what you.ll learn",
            r"by the end", r"let.s\b", r"learning objectives?",
            r"before you begin", r"your first",
        ],
        "content_keywords": [
            "follow along", "in this tutorial", "you will learn",
            "let's create", "let's build", "hands-on", "exercise",
            "we will", "next step", "congratulations", "well done",
            "you have successfully", "what you learned",
            "in this lesson", "let's start",
        ],
        "structural_signals": [
            "numbered_steps", "prerequisite_section", "goal_statement",
            "incremental_code",
        ],
    },
    "how-to": {
        "title_keywords": [
            "how-to", "howto", "guide", "recipe", "cookbook", "setup",
            "configure", "install", "deploy", "migrate", "troubleshoot",
            "fix", "resolve", "upgrade", "integrate",
        ],
        "heading_patterns": [
            r"how to\b", r"steps?:", r"procedure", r"solution",
            r"workaround", r"resolution",
        ],
        "content_keywords": [
            "run the following", "execute", "to do this",
            "use the command", "configure the", "set up",
            "problem:", "workaround", "make sure",
            "you need to", "ensure that", "run this",
            "to fix this", "to resolve",
        ],
        "structural_signals": [
            "task_heading", "short_steps", "no_conceptual_intro",
            "command_blocks",
        ],
    },
    "reference": {
        "title_keywords": [
            "reference", "api", "specification", "spec", "schema",
            "config", "configuration", "options", "parameters",
            "glossary", "changelog", "release-notes", "endpoints",
            "commands", "flags", "env", "environment",
        ],
        "heading_patterns": [
            r"parameters?", r"options?", r"returns?", r"arguments?",
            r"properties", r"fields?", r"methods?", r"endpoints?",
            r"types?", r"syntax", r"flags?", r"commands?",
        ],
        "content_keywords": [
            "default:", "type:", "required", "optional", "deprecated",
            "since version", "returns", "throws", "raises",
            "accepted values", "valid values", "enum:",
            "string | number", "boolean",
        ],
        "structural_signals": [
            "tables", "definition_lists", "code_signatures",
            "parameter_tables",
        ],
    },
    "explanation": {
        "title_keywords": [
            "explanation", "concept", "understanding", "why",
            "background", "overview", "architecture", "design",
            "philosophy", "rationale", "deep-dive", "theory",
            "principles", "fundamentals", "internals",
        ],
        "heading_patterns": [
            r"\bwhy\b", r"background", r"context", r"how .* works",
            r"under the hood", r"design decision", r"trade-?offs?",
            r"motivation", r"rationale",
        ],
        "content_keywords": [
            "the reason", "this is because", "historically",
            "the philosophy", "in contrast", "on the other hand",
            "the tradeoff", "consider", "fundamentally",
            "the key insight", "the approach", "by design",
            "the motivation", "architecturally",
        ],
        "structural_signals": [
            "long_paragraphs", "few_code_blocks", "narrative_flow",
            "diagrams",
        ],
    },
}

DEFAULT_CONFIG: dict = {
    "version": 1,
    "root": "docs",
    "layout": "folders",
    "ignore": ["node_modules", ".git", "adr", "rfcs", "*.pdf", ".DS_Store"],
    "custom_signals": {},
}


@dataclass
class ClassificationResult:
    """Result of classifying a single file into a Diataxis quadrant."""

    file_path: Path
    primary_quadrant: str = ""          # "tutorial", "how-to", "reference", "explanation"
    confidence: str = "low"             # high, medium, low
    score: float = 0.0
    scores: dict[str, float] = field(default_factory=dict)
    signals: dict[str, list[str]] = field(default_factory=dict)
    is_collapsed: bool = False
    collapsed_quadrants: list[str] = field(default_factory=list)
    reason: str = ""


def find_git_root(start: Path) -> Path | None:
    """Walk up from start to find the git repository root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=start,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except FileNotFoundError:
        pass
    return None


def load_config(base_path: Path) -> dict:
    """Find .diataxis-config.json walking up to git root, or return defaults."""
    current = base_path.resolve()
    git_root = find_git_root(current)
    stop_at = git_root or current

    while True:
        config_path = current / ".diataxis-config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config

        if current == stop_at or current == current.parent:
            break
        current = current.parent

    return dict(DEFAULT_CONFIG)


def resolve_config(args_config: str | None, base_path: Path) -> dict:
    """Load config from an explicit path or auto-detect."""
    if args_config:
        config_path = Path(args_config)
        if not config_path.is_absolute():
            config_path = base_path / config_path
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
        else:
            print(f"Warning: Config not found: {config_path}, using defaults",
                  file=sys.stderr)
            return dict(DEFAULT_CONFIG)
    return load_config(base_path)


def is_ignored(name: str, ignore_patterns: list[str]) -> bool:
    """Check if a directory or file name matches any ignore pattern."""
    return any(
        fnmatch.fnmatch(name, p) or fnmatch.fnmatch(name.lower(), p.lower())
        for p in ignore_patterns
    )


def find_docs_dir(base_path: Path, config: dict) -> Path:
    """Locate the docs directory from config or common conventions."""
    root = config.get("root", "docs")
    docs_dir = base_path / root
    if docs_dir.is_dir():
        return docs_dir

    # Try common alternatives
    for candidate in ["doc", "documentation"]:
        alt = base_path / candidate
        if alt.is_dir():
            return alt

    # Fall back to configured root even if it doesn't exist
    return docs_dir


def scan_markdown_files(
    docs_dir: Path,
    ignore_patterns: list[str],
) -> list[Path]:
    """Recursively find all .md files, respecting ignore patterns."""
    files: list[Path] = []
    if not docs_dir.is_dir():
        return files

    for item in sorted(docs_dir.rglob("*.md")):
        # Check if any parent directory is ignored
        skip = False
        for parent in item.relative_to(docs_dir).parents:
            if parent.name and is_ignored(parent.name, ignore_patterns):
                skip = True
                break
        if skip:
            continue
        if is_ignored(item.name, ignore_patterns):
            continue
        if item.is_file():
            files.append(item)

    return files


def read_document(filepath: Path, max_lines: int = 200) -> tuple[str, str, list[str]]:
    """Read a markdown document and extract structured information.

    Returns:
        tuple: (title, body_text, headings)
            - title: first H1 heading text (lowercase)
            - body_text: first max_lines of text (lowercase)
            - headings: list of all heading texts (lowercase)
    """
    title = ""
    body_lines: list[str] = []
    headings: list[str] = []

    try:
        with open(filepath) as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                stripped = line.strip()

                # Extract headings
                heading_match = re.match(r"^(#{1,4})\s+(.+)$", stripped)
                if heading_match:
                    level = len(heading_match.group(1))
                    text = heading_match.group(2).strip().lower()
                    headings.append(text)
                    if level == 1 and not title:
                        title = text

                body_lines.append(line.lower())
    except (OSError, UnicodeDecodeError):
        pass

    return title, " ".join(body_lines), headings


def format_confidence(score: float) -> str:
    """Convert a numeric score to a confidence level."""
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    return "low"


def format_bar(value: int, total: int, width: int = 10) -> str:
    """Format a simple bar chart using Unicode block characters."""
    if total == 0:
        return " " * width
    filled = round(value / total * width)
    return "\u2588" * filled + "\u2591" * (width - filled)
