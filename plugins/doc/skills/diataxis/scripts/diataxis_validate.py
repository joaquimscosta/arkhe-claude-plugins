#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Validate Diataxis quadrant purity of markdown documentation.

Checks that documents maintain focus on a single Diataxis quadrant and
follow quadrant-specific best practices.

Usage:
    uv run diataxis_validate.py --dir docs
    uv run diataxis_validate.py --file docs/getting-started.md
    uv run diataxis_validate.py --dir docs --strict
    uv run diataxis_validate.py --dir docs --json
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    ClassificationResult,
    resolve_config,
    scan_markdown_files,
)
from diataxis_classify import classify_file


@dataclass
class ValidationIssue:
    """A single validation finding."""
    rule_id: str
    severity: str       # "error", "warning", "info"
    file_path: Path
    message: str
    line: int = 0       # 0 means whole-file
    suggestion: str = ""


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------

def _count_preamble_words(filepath: Path) -> int:
    """Count words before the first numbered step or code block."""
    word_count = 0
    try:
        with open(filepath) as f:
            for line in f:
                stripped = line.strip()
                # Skip frontmatter
                if stripped == "---":
                    continue
                # Stop at first step or code block
                if re.match(r"^\d+\.\s+", stripped) or stripped.startswith("```"):
                    break
                # Skip headings
                if stripped.startswith("#"):
                    continue
                word_count += len(stripped.split())
    except (OSError, UnicodeDecodeError):
        pass
    return word_count


def _has_section(filepath: Path, patterns: list[str]) -> bool:
    """Check if the document has a heading matching any pattern."""
    try:
        with open(filepath) as f:
            for line in f:
                stripped = line.strip().lower()
                if stripped.startswith("#"):
                    heading_text = re.sub(r"^#+\s*", "", stripped)
                    for pattern in patterns:
                        if re.search(pattern, heading_text):
                            return True
    except (OSError, UnicodeDecodeError):
        pass
    return False


def _count_tables(filepath: Path) -> tuple[int, int]:
    """Count distinct tables and the line of the first table.

    A table is a contiguous block of pipe-delimited lines.
    Returns (number_of_tables, first_table_line).
    """
    count = 0
    first_line = 0
    in_table = False
    try:
        with open(filepath) as f:
            for i, line in enumerate(f, 1):
                is_table_line = line.strip().startswith("|") and "|" in line.strip()[1:]
                if is_table_line and not in_table:
                    # Start of a new table
                    in_table = True
                    count += 1
                    if first_line == 0:
                        first_line = i
                elif not is_table_line:
                    in_table = False
    except (OSError, UnicodeDecodeError):
        pass
    return count, first_line


def _count_step_instructions(filepath: Path) -> tuple[int, int]:
    """Count numbered step lines and the line of the first step."""
    count = 0
    first_line = 0
    try:
        with open(filepath) as f:
            for i, line in enumerate(f, 1):
                if re.match(r"^\d+\.\s+", line.strip()):
                    count += 1
                    if first_line == 0:
                        first_line = i
    except (OSError, UnicodeDecodeError):
        pass
    return count, first_line


def _count_command_blocks(filepath: Path) -> tuple[int, int]:
    """Count code blocks with executable commands and the line of the first."""
    count = 0
    first_line = 0
    in_code = False
    block_start = 0
    block_lines: list[str] = []

    try:
        with open(filepath) as f:
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                if stripped.startswith("```"):
                    if in_code:
                        # Check if block contains commands
                        block_text = " ".join(block_lines).lower()
                        if any(cmd in block_text for cmd in [
                            "run ", "install ", "npm ", "pip ", "docker ",
                            "curl ", "git ", "cd ", "mkdir ", "uv run",
                        ]):
                            count += 1
                            if first_line == 0:
                                first_line = block_start
                        block_lines = []
                    else:
                        block_start = i
                    in_code = not in_code
                elif in_code:
                    block_lines.append(stripped)
    except (OSError, UnicodeDecodeError):
        pass

    return count, first_line


def validate_file(
    filepath: Path,
    classification: ClassificationResult,
) -> list[ValidationIssue]:
    """Run all validation rules against a single file."""
    issues: list[ValidationIssue] = []
    quadrant = classification.primary_quadrant

    if not quadrant:
        # DX005: No clear quadrant signal
        issues.append(ValidationIssue(
            rule_id="DX005",
            severity="info",
            file_path=filepath,
            message="No clear quadrant signal detected",
            suggestion="Add a clear purpose heading or rename the file to indicate its type",
        ))
        return issues

    # DX006: Collapsed document
    if classification.is_collapsed:
        mixed = " + ".join(q.capitalize() for q in classification.collapsed_quadrants)
        issues.append(ValidationIssue(
            rule_id="DX006",
            severity="warning",
            file_path=filepath,
            message=f"Collapsed document: mixes {mixed}",
            suggestion=f"Consider splitting into separate {' and '.join(classification.collapsed_quadrants)} documents",
        ))

    # Quadrant-specific rules
    if quadrant == "tutorial":
        # DX001: Tutorial contains reference tables
        table_count, table_line = _count_tables(filepath)
        if table_count >= 3:
            issues.append(ValidationIssue(
                rule_id="DX001",
                severity="warning",
                file_path=filepath,
                message=f"Tutorial contains {table_count} tables (reference-style content)",
                line=table_line,
                suggestion="Move parameter/option tables to a separate Reference document",
            ))

        # DX007: Tutorial missing prerequisites
        if not _has_section(filepath, [r"prerequisites?", r"before you begin", r"requirements?"]):
            issues.append(ValidationIssue(
                rule_id="DX007",
                severity="info",
                file_path=filepath,
                message="Tutorial missing prerequisites section",
                suggestion="Add a 'Prerequisites' or 'Before You Begin' heading",
            ))

        # DX008: Tutorial missing learning objectives
        if not _has_section(filepath, [r"what you.ll learn", r"learning objectives?", r"goals?"]):
            issues.append(ValidationIssue(
                rule_id="DX008",
                severity="info",
                file_path=filepath,
                message="Tutorial missing 'What You'll Learn' section",
                suggestion="Add a brief section describing what the reader will learn",
            ))

    elif quadrant == "how-to":
        # DX002: How-to with long conceptual preamble
        preamble_words = _count_preamble_words(filepath)
        if preamble_words > 100:
            issues.append(ValidationIssue(
                rule_id="DX002",
                severity="warning",
                file_path=filepath,
                message=f"How-to guide has {preamble_words}-word preamble before first action step",
                suggestion="Move conceptual content to an Explanation document; start with the task",
            ))

        # DX009: How-to missing problem statement
        if not _has_section(filepath, [r"problem", r"scenario", r"when to use", r"use case"]):
            issues.append(ValidationIssue(
                rule_id="DX009",
                severity="info",
                file_path=filepath,
                message="How-to guide missing problem statement",
                suggestion="Add a brief description of the problem this guide solves",
            ))

    elif quadrant == "reference":
        # DX003: Reference contains step-by-step instructions
        step_count, step_line = _count_step_instructions(filepath)
        if step_count >= 3:
            issues.append(ValidationIssue(
                rule_id="DX003",
                severity="warning",
                file_path=filepath,
                message=f"Reference document contains {step_count} numbered steps (how-to content)",
                line=step_line,
                suggestion="Move step-by-step instructions to a How-to guide",
            ))

        # DX010: Reference missing parameter/option tables
        table_count, _ = _count_tables(filepath)
        if table_count == 0:
            issues.append(ValidationIssue(
                rule_id="DX010",
                severity="info",
                file_path=filepath,
                message="Reference document has no tables",
                suggestion="Consider adding tables for parameters, options, or API endpoints",
            ))

    elif quadrant == "explanation":
        # DX004: Explanation contains execution commands
        cmd_count, cmd_line = _count_command_blocks(filepath)
        if cmd_count >= 2:
            issues.append(ValidationIssue(
                rule_id="DX004",
                severity="warning",
                file_path=filepath,
                message=f"Explanation document contains {cmd_count} command blocks (how-to content)",
                line=cmd_line,
                suggestion="Move executable commands to a How-to guide; keep concepts here",
            ))

    return issues


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_report(
    issues: list[ValidationIssue],
    docs_dir: Path,
    file_count: int,
) -> str:
    """Format validation results as a human-readable report."""
    lines = [
        "Diataxis Purity Validation Report",
        "=" * 40,
        f"Directory: {docs_dir}",
        f"Files validated: {file_count}",
        "",
    ]

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    if errors:
        lines.append(f"Errors: {len(errors)}")
        for issue in errors:
            loc = f" (line {issue.line})" if issue.line else ""
            lines.append(f"  x {issue.rule_id} {issue.file_path.name}{loc} — {issue.message}")
            if issue.suggestion:
                lines.append(f"    Suggestion: {issue.suggestion}")
        lines.append("")

    if warnings:
        lines.append(f"Warnings: {len(warnings)}")
        for issue in warnings:
            loc = f" (line {issue.line})" if issue.line else ""
            lines.append(f"  ! {issue.rule_id} {issue.file_path.name}{loc} — {issue.message}")
            if issue.suggestion:
                lines.append(f"    Suggestion: {issue.suggestion}")
        lines.append("")

    if infos:
        lines.append(f"Info: {len(infos)}")
        for issue in infos:
            lines.append(f"  - {issue.rule_id} {issue.file_path.name} — {issue.message}")
        lines.append("")

    if not issues:
        lines.append("No issues found.")
        lines.append("")

    # Result
    if errors:
        result = "FAIL"
    elif warnings:
        result = "WARN"
    else:
        result = "PASS"

    lines.append(
        f"Result: {result} ({file_count} files, "
        f"{len(errors)} errors, {len(warnings)} warnings, {len(infos)} info)"
    )

    return "\n".join(lines)


def format_issues_json(issues: list[ValidationIssue]) -> str:
    """Format validation issues as JSON."""
    data = []
    for issue in issues:
        data.append({
            "rule_id": issue.rule_id,
            "severity": issue.severity,
            "file": str(issue.file_path),
            "message": issue.message,
            "line": issue.line,
            "suggestion": issue.suggestion,
        })
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Diataxis quadrant purity of documentation"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--dir",
        "-d",
        default=None,
        help="Docs directory to validate",
    )
    group.add_argument(
        "--file",
        "-f",
        default=None,
        help="Single file to validate",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit code 1 on any warnings (for CI)",
    )
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Path to .diataxis-config.json",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )

    args = parser.parse_args()
    base_path = Path.cwd()
    config = resolve_config(args.config, base_path)

    # Collect files
    if args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = base_path / filepath
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            return 1
        files = [filepath]
        docs_dir = filepath.parent
    else:
        docs_dir = Path(args.dir)
        if not docs_dir.is_absolute():
            docs_dir = base_path / docs_dir
        if not docs_dir.exists():
            print(f"Error: Directory does not exist: {docs_dir}")
            return 1
        ignore = config.get("ignore", [])
        files = scan_markdown_files(docs_dir, ignore)

    if not files:
        print("No markdown files found.")
        return 0

    # Classify and validate
    all_issues: list[ValidationIssue] = []
    for filepath in files:
        classification = classify_file(filepath, config)
        issues = validate_file(filepath, classification)
        all_issues.extend(issues)

    # Output
    if args.json_output:
        print(format_issues_json(all_issues))
    else:
        print(format_report(all_issues, docs_dir, len(files)))

    # Exit code
    errors = [i for i in all_issues if i.severity == "error"]
    warnings = [i for i in all_issues if i.severity == "warning"]

    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
