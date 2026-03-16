#!/usr/bin/env python3
"""
Sync official Anthropic documentation and compute diffs for impact analysis.

Downloads updated docs via update-claude-docs.sh, compares before/after state,
extracts hardcoded constants from the skill validator, and identifies discrepancies
between what the docs define and what the validator enforces.

Usage:
    sync_and_diff.py               # Sync docs and output diff analysis as JSON
    sync_and_diff.py --dry-run     # Download to temp, compare, don't overwrite

Output: JSON to stdout with sync results, diffs, and discrepancies.
"""

import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Project discovery
# ---------------------------------------------------------------------------

def find_project_root() -> Path:
    """Find the arkhe-claude-plugins project root."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".claude-plugin" / "marketplace.json").exists():
            return current
        if (current / "plugins").is_dir() and (current / "CLAUDE.md").exists():
            return current
        current = current.parent

    cwd = Path.cwd()
    if (cwd / "plugins").is_dir():
        return cwd

    print("Error: Cannot find project root.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# URL mappings parsing
# ---------------------------------------------------------------------------

def parse_url_mappings(root: Path) -> List[Tuple[str, str]]:
    """Extract URL|FILENAME pairs from update-claude-docs.sh."""
    script_path = root / "docs" / "reference" / "update-claude-docs.sh"
    if not script_path.exists():
        print(f"Error: Sync script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    content = script_path.read_text()
    matches = []
    # Parse only non-comment lines inside the URL_MAPPINGS array
    in_array = False
    for line in content.splitlines():
        stripped = line.strip()
        if "URL_MAPPINGS=(" in stripped:
            in_array = True
            continue
        if in_array and stripped == ")":
            break
        if in_array and not stripped.startswith("#"):
            m = re.match(r'"(https://[^"]+)\|([^"]+)"', stripped)
            if m:
                matches.append((m.group(1), m.group(2)))

    if not matches:
        print("Error: No URL mappings found in sync script.", file=sys.stderr)
        sys.exit(1)

    return matches


# ---------------------------------------------------------------------------
# File snapshotting
# ---------------------------------------------------------------------------

def hash_content(content: str) -> str:
    """SHA-256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def snapshot_files(root: Path, filenames: List[str]) -> Dict[str, str]:
    """Read current content of each synced doc. Returns {filename: content}."""
    ref_dir = root / "docs" / "reference"
    result = {}
    for filename in filenames:
        filepath = ref_dir / filename
        if filepath.exists():
            result[filename] = filepath.read_text()
        else:
            result[filename] = ""
    return result


# ---------------------------------------------------------------------------
# Sync execution
# ---------------------------------------------------------------------------

def run_sync_script(root: Path) -> Tuple[int, str, str]:
    """Execute update-claude-docs.sh and return (exit_code, stdout, stderr)."""
    script_path = root / "docs" / "reference" / "update-claude-docs.sh"
    result = subprocess.run(
        [str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(root / "docs" / "reference"),
        timeout=300,
    )
    return result.returncode, result.stdout, result.stderr


def dry_run_download(url_mappings: List[Tuple[str, str]], timeout: int = 30) -> Dict[str, str]:
    """Download docs to memory without overwriting. Returns {filename: content}."""
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    result = {}
    for url, filename in url_mappings:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = resp.read().decode("utf-8")
                if len(content.strip()) > 10:
                    result[filename] = content
                else:
                    print(f"Warning: Empty content for {filename}", file=sys.stderr)
                    result[filename] = ""
        except Exception as e:
            print(f"Warning: Failed to download {filename}: {e}", file=sys.stderr)
            result[filename] = ""
    return result


# ---------------------------------------------------------------------------
# Diff computation
# ---------------------------------------------------------------------------

@dataclass
class FileDiff:
    filename: str
    changed: bool
    hash_before: str
    hash_after: str
    added_lines: int = 0
    removed_lines: int = 0
    added_sections: List[str] = field(default_factory=list)
    removed_sections: List[str] = field(default_factory=list)
    diff: str = ""


def extract_sections(content: str) -> List[str]:
    """Extract markdown headings (## and ###) from content."""
    return re.findall(r"^(#{2,3}\s+.+)$", content, re.MULTILINE)


def compute_diffs(before: Dict[str, str], after: Dict[str, str]) -> List[FileDiff]:
    """Compute unified diffs between before and after snapshots."""
    results = []
    all_files = sorted(set(before.keys()) | set(after.keys()))

    for filename in all_files:
        old = before.get(filename, "")
        new = after.get(filename, "")
        h_before = hash_content(old)
        h_after = hash_content(new)
        changed = h_before != h_after

        fd = FileDiff(
            filename=filename,
            changed=changed,
            hash_before=h_before,
            hash_after=h_after,
        )

        if changed:
            old_lines = old.splitlines(keepends=True)
            new_lines = new.splitlines(keepends=True)
            diff_lines = list(difflib.unified_diff(
                old_lines, new_lines,
                fromfile=f"a/{filename}", tofile=f"b/{filename}",
                lineterm="",
            ))

            # Count additions/removals (skip diff header lines)
            for line in diff_lines:
                if line.startswith("+") and not line.startswith("+++"):
                    fd.added_lines += 1
                elif line.startswith("-") and not line.startswith("---"):
                    fd.removed_lines += 1

            # Extract section-level changes
            old_sections = set(extract_sections(old))
            new_sections = set(extract_sections(new))
            fd.added_sections = sorted(new_sections - old_sections)
            fd.removed_sections = sorted(old_sections - new_sections)

            # Truncate diff to ~200 lines
            max_diff_lines = 200
            if len(diff_lines) > max_diff_lines:
                fd.diff = "".join(diff_lines[:max_diff_lines]) + \
                    f"\n... truncated ({len(diff_lines) - max_diff_lines} more lines)\n"
            else:
                fd.diff = "".join(diff_lines)

        results.append(fd)

    return results


# ---------------------------------------------------------------------------
# Validator constant extraction
# ---------------------------------------------------------------------------

@dataclass
class ValidatorConstants:
    allowed_frontmatter_keys: List[str] = field(default_factory=list)
    valid_hook_events: List[str] = field(default_factory=list)
    valid_memory_scopes: List[str] = field(default_factory=list)
    extraction_errors: List[str] = field(default_factory=list)


def extract_validator_constants(root: Path) -> ValidatorConstants:
    """Extract hardcoded constants from validate_skill.py using regex."""
    validator_path = root / ".claude" / "skills" / "skill-validator" / "scripts" / "validate_skill.py"
    constants = ValidatorConstants()

    if not validator_path.exists():
        constants.extraction_errors.append(f"Validator not found: {validator_path}")
        return constants

    content = validator_path.read_text()

    # Extract ALLOWED_FRONTMATTER_KEYS
    match = re.search(
        r"ALLOWED_FRONTMATTER_KEYS\s*=\s*\{([^}]+)\}",
        content, re.DOTALL,
    )
    if match:
        keys = re.findall(r"'([^']+)'", match.group(1))
        constants.allowed_frontmatter_keys = sorted(keys)
    else:
        constants.extraction_errors.append("Could not extract ALLOWED_FRONTMATTER_KEYS")

    # Extract VALID_HOOK_EVENTS
    match = re.search(
        r"VALID_HOOK_EVENTS\s*=\s*\{([^}]+)\}",
        content, re.DOTALL,
    )
    if match:
        events = re.findall(r"'([^']+)'", match.group(1))
        constants.valid_hook_events = sorted(events)
    else:
        constants.extraction_errors.append("Could not extract VALID_HOOK_EVENTS")

    # Extract valid_scopes (local variable in validation function)
    match = re.search(
        r"valid_scopes\s*=\s*\{([^}]+)\}",
        content,
    )
    if match:
        scopes = re.findall(r"'([^']+)'", match.group(1))
        constants.valid_memory_scopes = sorted(scopes)
    else:
        constants.extraction_errors.append("Could not extract valid_scopes")

    return constants


# ---------------------------------------------------------------------------
# Doc field extraction
# ---------------------------------------------------------------------------

@dataclass
class DocFields:
    skills_frontmatter_fields: List[str] = field(default_factory=list)
    subagents_frontmatter_fields: List[str] = field(default_factory=list)
    hook_events: List[str] = field(default_factory=list)
    extraction_errors: List[str] = field(default_factory=list)


def extract_doc_fields(content_map: Dict[str, str]) -> DocFields:
    """Extract structured field definitions from synced documentation."""
    fields = DocFields()

    # --- SKILLS.md: frontmatter fields from the reference table ---
    # The table has: | `field` | Required/No/Recommended | Description |
    skills_content = content_map.get("SKILLS.md", "")
    if skills_content:
        skill_fields = re.findall(
            r"^\|\s*`([a-z][-a-z]*)`\s*\|\s*(?:No|Yes|Recommended)\s*\|",
            skills_content, re.MULTILINE,
        )
        fields.skills_frontmatter_fields = sorted(set(skill_fields))
    else:
        fields.extraction_errors.append("SKILLS.md not available for field extraction")

    # --- SUBAGENTS.md: frontmatter fields table ---
    # The table has: | `field` | Yes/No | Description |
    subagents_content = content_map.get("SUBAGENTS.md", "")
    if subagents_content:
        sub_fields = re.findall(
            r"^\|\s*`([a-zA-Z]+)`\s*\|\s*(?:No|Yes)\s*\|",
            subagents_content, re.MULTILINE,
        )
        fields.subagents_frontmatter_fields = sorted(set(sub_fields))
    else:
        fields.extraction_errors.append("SUBAGENTS.md not available for field extraction")

    # --- HOOKS.md: hook event names from the primary events table ---
    # The events table has: | `EventName` | Description with lowercase start |
    # We only match the first events table (lines ~29-45) by looking for
    # PascalCase names followed by a description starting with "When"
    hooks_content = content_map.get("HOOKS.md", "")
    if hooks_content:
        events = re.findall(
            r"^\|\s*`([A-Z][a-zA-Z]+)`\s*\|\s*[A-Z]",
            hooks_content, re.MULTILINE,
        )
        fields.hook_events = sorted(set(events))
    else:
        fields.extraction_errors.append("HOOKS.md not available for hook event extraction")

    return fields


# ---------------------------------------------------------------------------
# Discrepancy computation
# ---------------------------------------------------------------------------

@dataclass
class SetDiscrepancy:
    in_docs_not_validator: List[str] = field(default_factory=list)
    in_validator_not_docs: List[str] = field(default_factory=list)


@dataclass
class Discrepancies:
    # Skills-only frontmatter: SKILLS.md fields vs validator (CRITICAL)
    skill_frontmatter_keys: SetDiscrepancy = field(default_factory=SetDiscrepancy)
    # Subagent frontmatter: SUBAGENTS.md fields vs validator (INFO context)
    subagent_frontmatter_keys: SetDiscrepancy = field(default_factory=SetDiscrepancy)
    hook_events: SetDiscrepancy = field(default_factory=SetDiscrepancy)
    memory_scopes: SetDiscrepancy = field(default_factory=SetDiscrepancy)


def compute_discrepancies(
    validator: ValidatorConstants,
    doc_fields: DocFields,
) -> Discrepancies:
    """Compute set differences between validator constants and doc-defined fields."""
    disc = Discrepancies()
    validator_fm_keys = set(validator.allowed_frontmatter_keys)

    # Skill frontmatter: only SKILLS.md fields vs validator (CRITICAL)
    # The validator validates SKILL.md frontmatter, so only SKILLS.md is authoritative
    skill_fm_keys = set(doc_fields.skills_frontmatter_fields)
    disc.skill_frontmatter_keys = SetDiscrepancy(
        in_docs_not_validator=sorted(skill_fm_keys - validator_fm_keys),
        in_validator_not_docs=sorted(validator_fm_keys - skill_fm_keys),
    )

    # Subagent frontmatter: SUBAGENTS.md fields vs validator (INFO)
    # Some subagent fields (maxTurns, mcpServers, memory, skills) are valid in
    # skill frontmatter when using context: fork. Others (tools, permissionMode)
    # are agent-only. Report for context, not as CRITICAL.
    subagent_fm_keys = set(doc_fields.subagents_frontmatter_fields)
    disc.subagent_frontmatter_keys = SetDiscrepancy(
        in_docs_not_validator=sorted(subagent_fm_keys - validator_fm_keys),
        in_validator_not_docs=sorted(validator_fm_keys - subagent_fm_keys),
    )

    # Hook events
    doc_events = set(doc_fields.hook_events)
    validator_events = set(validator.valid_hook_events)
    disc.hook_events = SetDiscrepancy(
        in_docs_not_validator=sorted(doc_events - validator_events),
        in_validator_not_docs=sorted(validator_events - doc_events),
    )

    # Memory scopes — extracted from SUBAGENTS.md prose, not a clean table.
    # Manual check area — the script flags it as needing human review.
    disc.memory_scopes = SetDiscrepancy()

    return disc


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def build_output(
    sync_exit_code: Optional[int],
    sync_stdout: str,
    sync_stderr: str,
    file_diffs: List[FileDiff],
    validator_constants: ValidatorConstants,
    doc_fields: DocFields,
    discrepancies: Discrepancies,
    dry_run: bool,
) -> dict:
    """Build the final JSON output."""
    changed_count = sum(1 for f in file_diffs if f.changed)
    unchanged_count = sum(1 for f in file_diffs if not f.changed)

    return {
        "sync_result": {
            "exit_code": sync_exit_code,
            "stdout": sync_stdout,
            "stderr": sync_stderr,
            "summary": f"{changed_count} changed, {unchanged_count} unchanged",
        },
        "files": [asdict(f) for f in file_diffs],
        "validator_constants": asdict(validator_constants),
        "doc_fields": asdict(doc_fields),
        "discrepancies": asdict(discrepancies),
        "dry_run": dry_run,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Sync Anthropic docs and compute diff analysis.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Download to temp, compare, don't overwrite local files.",
    )
    args = parser.parse_args()

    root = find_project_root()
    url_mappings = parse_url_mappings(root)
    filenames = [filename for _, filename in url_mappings]

    # Snapshot before
    before = snapshot_files(root, filenames)

    # Sync or dry-run
    sync_exit_code = None
    sync_stdout = ""
    sync_stderr = ""

    if args.dry_run:
        print("Dry run: downloading to memory without overwriting...", file=sys.stderr)
        after = dry_run_download(url_mappings)
        # Fill in any files that failed to download with their current content
        for filename in filenames:
            if not after.get(filename):
                after[filename] = before.get(filename, "")
    else:
        print("Running sync script...", file=sys.stderr)
        sync_exit_code, sync_stdout, sync_stderr = run_sync_script(root)
        print(f"Sync complete (exit code: {sync_exit_code})", file=sys.stderr)
        # Snapshot after
        after = snapshot_files(root, filenames)

    # Compute diffs
    file_diffs = compute_diffs(before, after)

    # Extract validator constants
    validator_constants = extract_validator_constants(root)

    # Extract doc-defined fields from the AFTER content
    doc_fields = extract_doc_fields(after)

    # Compute discrepancies
    discrepancies = compute_discrepancies(validator_constants, doc_fields)

    # Output JSON
    output = build_output(
        sync_exit_code, sync_stdout, sync_stderr,
        file_diffs, validator_constants, doc_fields,
        discrepancies, args.dry_run,
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
