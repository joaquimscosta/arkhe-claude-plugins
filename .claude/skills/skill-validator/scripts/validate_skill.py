#!/usr/bin/env python3
"""
Comprehensive skill validator against Anthropic best practices.

Usage:
    validate_skill.py <skill-directory> [options]

Options:
    --min-severity {critical,error,warning,suggestion}
    --format {text,json}
    --ignore RULE1,RULE2
"""

import sys
import re
import os
import stat
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Set, Tuple

# Try to import yaml, fall back to basic parsing if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class Severity(Enum):
    CRITICAL = 4
    ERROR = 3
    WARNING = 2
    SUGGESTION = 1

    def __str__(self):
        return self.name


@dataclass
class Issue:
    rule_id: str
    severity: Severity
    message: str
    location: str
    current_value: Optional[str] = None
    fix_suggestion: str = ""

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.name,
            "message": self.message,
            "location": self.location,
            "current_value": self.current_value,
            "fix_suggestion": self.fix_suggestion
        }


# ============================================================================
# YAML Parsing (fallback if PyYAML not available)
# ============================================================================

def parse_frontmatter(content: str) -> Tuple[Optional[Dict], str, str]:
    """Parse YAML frontmatter from content. Returns (frontmatter_dict, body, error)."""
    if not content.startswith('---'):
        return None, content, "No YAML frontmatter found (must start with ---)"

    match = re.match(r'^---\n(.*?)\n---\n?', content, re.DOTALL)
    if not match:
        return None, content, "Invalid frontmatter format (missing closing ---)"

    frontmatter_text = match.group(1)
    body = content[match.end():]

    if HAS_YAML:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return None, body, "Frontmatter must be a YAML dictionary"
            return frontmatter, body, ""
        except yaml.YAMLError as e:
            return None, body, f"Invalid YAML in frontmatter: {e}"
    else:
        # Basic fallback parsing
        frontmatter = {}
        current_key = None
        current_value = []

        for line in frontmatter_text.split('\n'):
            if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
                if current_key:
                    frontmatter[current_key] = '\n'.join(current_value).strip()
                key, _, value = line.partition(':')
                current_key = key.strip()
                current_value = [value.strip()] if value.strip() else []
            elif current_key:
                current_value.append(line)

        if current_key:
            frontmatter[current_key] = '\n'.join(current_value).strip()

        return frontmatter, body, ""


# ============================================================================
# Frontmatter Validators (FM001-FM012)
# ============================================================================

ALLOWED_FRONTMATTER_KEYS = {
    'name', 'description', 'license', 'allowed-tools', 'metadata',
    'model', 'context', 'agent', 'hooks', 'user-invocable',
    'disable-model-invocation', 'argument-hint'
}

RESERVED_WORDS = {'anthropic', 'claude'}

SECOND_PERSON_PATTERNS = [
    r'\byou\s+should\b',
    r'\byou\s+can\b',
    r'\byou\s+will\b',
    r'\byou\s+need\b',
    r'\byou\'ll\b',
    r'\byour\b',
]

FIRST_PERSON_PATTERNS = [
    r'\bI\s+can\b',
    r'\bI\s+will\b',
    r'\bI\'ll\b',
    r'\bI\s+am\b',
    r'\bI\'m\b',
]


def validate_frontmatter(skill_path: Path, frontmatter: Dict, body: str) -> List[Issue]:
    """Validate YAML frontmatter against best practices."""
    issues = []

    # FM001: name required
    if 'name' not in frontmatter:
        issues.append(Issue(
            rule_id="FM001",
            severity=Severity.CRITICAL,
            message="Required field 'name' missing from frontmatter",
            location="SKILL.md frontmatter",
            fix_suggestion="Add 'name: your-skill-name' to frontmatter"
        ))
        return issues  # Can't continue without name

    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        issues.append(Issue(
            rule_id="FM001",
            severity=Severity.CRITICAL,
            message=f"Name must be a string, got {type(name).__name__}",
            location="SKILL.md frontmatter",
            fix_suggestion="Ensure name is a plain string value"
        ))
        return issues

    name = name.strip()

    # FM002: description required
    if 'description' not in frontmatter:
        issues.append(Issue(
            rule_id="FM002",
            severity=Severity.CRITICAL,
            message="Required field 'description' missing from frontmatter",
            location="SKILL.md frontmatter",
            fix_suggestion="Add 'description: What it does. Use when [triggers].' to frontmatter"
        ))

    # FM003: name format (lowercase-with-hyphens)
    if name and not re.match(r'^[a-z0-9-]+$', name):
        issues.append(Issue(
            rule_id="FM003",
            severity=Severity.ERROR,
            message="Name must be lowercase letters, digits, and hyphens only",
            location="SKILL.md frontmatter",
            current_value=name,
            fix_suggestion=f"Rename to: {re.sub(r'[^a-z0-9-]', '-', name.lower()).strip('-')}"
        ))

    # FM004: name length
    if len(name) > 64:
        issues.append(Issue(
            rule_id="FM004",
            severity=Severity.ERROR,
            message=f"Name exceeds 64 character limit ({len(name)} characters)",
            location="SKILL.md frontmatter",
            current_value=name,
            fix_suggestion="Shorten name to 64 characters or less"
        ))

    # FM005: reserved words
    name_lower = name.lower()
    for reserved in RESERVED_WORDS:
        if reserved in name_lower:
            issues.append(Issue(
                rule_id="FM005",
                severity=Severity.ERROR,
                message=f"Name cannot contain reserved word '{reserved}'",
                location="SKILL.md frontmatter",
                current_value=name,
                fix_suggestion=f"Remove '{reserved}' from the name"
            ))

    # FM006: hyphen placement
    if name.startswith('-') or name.endswith('-') or '--' in name:
        issues.append(Issue(
            rule_id="FM006",
            severity=Severity.ERROR,
            message="Name cannot start/end with hyphen or contain consecutive hyphens",
            location="SKILL.md frontmatter",
            current_value=name,
            fix_suggestion="Fix hyphen placement in the name"
        ))

    # Description validation
    description = frontmatter.get('description', '')
    if isinstance(description, str):
        description = description.strip()

        # FM007: description length
        if len(description) > 1024:
            issues.append(Issue(
                rule_id="FM007",
                severity=Severity.ERROR,
                message=f"Description exceeds 1024 character limit ({len(description)} characters)",
                location="SKILL.md frontmatter",
                fix_suggestion="Shorten description to 1024 characters or less"
            ))

        # FM008: angle brackets
        if '<' in description or '>' in description:
            issues.append(Issue(
                rule_id="FM008",
                severity=Severity.ERROR,
                message="Description cannot contain angle brackets (< or >)",
                location="SKILL.md frontmatter",
                fix_suggestion="Remove angle brackets from description"
            ))

        # FM010: trigger keywords
        trigger_patterns = [
            r'\buse when\b',
            r'\bwhen user\b',
            r'\btrigger',
            r'\bactivate',
            r'\binvoke'
        ]
        has_triggers = any(re.search(p, description, re.IGNORECASE) for p in trigger_patterns)
        if not has_triggers and len(description) > 50:
            issues.append(Issue(
                rule_id="FM010",
                severity=Severity.WARNING,
                message="Description should include trigger scenarios",
                location="SKILL.md frontmatter",
                fix_suggestion="Add 'Use when [scenario]' to description to help Claude know when to invoke"
            ))

        # FM012: first/second person in description
        for pattern in FIRST_PERSON_PATTERNS:
            if re.search(pattern, description, re.IGNORECASE):
                issues.append(Issue(
                    rule_id="FM012",
                    severity=Severity.WARNING,
                    message="Description uses first person",
                    location="SKILL.md frontmatter",
                    current_value=re.search(pattern, description, re.IGNORECASE).group(),
                    fix_suggestion="Use third person: 'This skill extracts...' not 'I can extract...'"
                ))
                break

        for pattern in SECOND_PERSON_PATTERNS[:2]:  # Check common ones
            if re.search(pattern, description, re.IGNORECASE):
                issues.append(Issue(
                    rule_id="FM012",
                    severity=Severity.WARNING,
                    message="Description uses second person",
                    location="SKILL.md frontmatter",
                    current_value=re.search(pattern, description, re.IGNORECASE).group(),
                    fix_suggestion="Use third person: 'Extracts data from...' not 'You can extract...'"
                ))
                break

    # FM009: unknown keys
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected_keys:
        issues.append(Issue(
            rule_id="FM009",
            severity=Severity.WARNING,
            message=f"Unknown frontmatter key(s): {', '.join(sorted(unexpected_keys))}",
            location="SKILL.md frontmatter",
            fix_suggestion=f"Remove or use allowed keys: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}"
        ))

    # FM011: gerund naming (suggestion only)
    if name and not name.endswith('ing') and '-' in name:
        # Check if it could be a gerund
        parts = name.split('-')
        if len(parts) >= 2 and not any(p.endswith('ing') for p in parts):
            issues.append(Issue(
                rule_id="FM011",
                severity=Severity.SUGGESTION,
                message="Consider using gerund naming convention (verb+ing)",
                location="SKILL.md frontmatter",
                current_value=name,
                fix_suggestion=f"Example: 'processing-pdfs' instead of 'pdf-processor'"
            ))

    # FM013: argument-hint format validation
    argument_hint = frontmatter.get('argument-hint', '')
    if argument_hint:
        if isinstance(argument_hint, str):
            # Valid formats: [name], [name] [name], or free text
            # Warn if it looks like it should have brackets but doesn't
            if not re.search(r'\[.+?\]', argument_hint):
                issues.append(Issue(
                    rule_id="FM013",
                    severity=Severity.SUGGESTION,
                    message="argument-hint should use bracket notation",
                    location="SKILL.md frontmatter",
                    current_value=argument_hint,
                    fix_suggestion="Use format like '[issue-number]' or '[filename] [format]'"
                ))
        else:
            issues.append(Issue(
                rule_id="FM013",
                severity=Severity.ERROR,
                message=f"argument-hint must be a string, got {type(argument_hint).__name__}",
                location="SKILL.md frontmatter",
                fix_suggestion="Ensure argument-hint is a plain string value"
            ))

    # FM014: $ARGUMENTS usage validation
    # Only check in actual instruction text, not documentation/examples
    disable_model = frontmatter.get('disable-model-invocation', False)
    # Remove code blocks and table rows before checking
    body_for_args = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    body_for_args = re.sub(r'^\|.*\|$', '', body_for_args, flags=re.MULTILINE)
    body_for_args = re.sub(r'`[^`]+`', '', body_for_args)  # Remove inline code
    has_arguments_var = bool(re.search(r'\$ARGUMENTS|\$\d+|\$\{CLAUDE_SESSION_ID\}', body_for_args))
    if has_arguments_var and not disable_model:
        # Skills using $ARGUMENTS are typically meant for manual invocation
        issues.append(Issue(
            rule_id="FM014",
            severity=Severity.SUGGESTION,
            message="Skill uses $ARGUMENTS but allows model invocation",
            location="SKILL.md",
            fix_suggestion="Consider adding 'disable-model-invocation: true' for skills that require arguments"
        ))

    return issues


# ============================================================================
# Structure & Sizing Validators (SS001-SS006)
# ============================================================================

def validate_structure(skill_path: Path, content: str, body: str) -> List[Issue]:
    """Validate structure and sizing against best practices."""
    issues = []
    lines = content.split('\n')
    line_count = len(lines)

    # SS002: line count error (500 limit)
    if line_count > 500:
        issues.append(Issue(
            rule_id="SS002",
            severity=Severity.ERROR,
            message=f"SKILL.md exceeds 500 line limit ({line_count} lines)",
            location="SKILL.md",
            fix_suggestion="Split content into WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md"
        ))
    # SS003: line count warning (300 threshold)
    elif line_count > 300:
        issues.append(Issue(
            rule_id="SS003",
            severity=Severity.WARNING,
            message=f"SKILL.md approaching line limit ({line_count} lines, max 500)",
            location="SKILL.md",
            fix_suggestion="Consider extracting detailed content to supporting files"
        ))

    # SS004: check for supporting docs if SKILL.md is large
    if line_count > 200:
        supporting_docs = ['WORKFLOW.md', 'EXAMPLES.md', 'TROUBLESHOOTING.md']
        existing_docs = [d for d in supporting_docs if (skill_path / d).exists()]
        if not existing_docs:
            issues.append(Issue(
                rule_id="SS004",
                severity=Severity.WARNING,
                message="Large SKILL.md without supporting documentation files",
                location="SKILL.md",
                fix_suggestion="Create EXAMPLES.md or TROUBLESHOOTING.md to reduce SKILL.md size"
            ))

    # SS005: check reference files for TOC
    refs_dir = skill_path / 'references'
    if refs_dir.exists():
        for ref_file in refs_dir.glob('*.md'):
            ref_content = ref_file.read_text()
            ref_lines = len(ref_content.split('\n'))
            if ref_lines > 100:
                # Check for TOC indicators
                toc_patterns = [
                    r'## table of contents',
                    r'## contents',
                    r'## toc',
                    r'\* \[.*\]\(#',  # Markdown TOC links
                ]
                has_toc = any(re.search(p, ref_content, re.IGNORECASE) for p in toc_patterns)
                if not has_toc:
                    issues.append(Issue(
                        rule_id="SS005",
                        severity=Severity.SUGGESTION,
                        message=f"Reference file >100 lines without table of contents",
                        location=f"references/{ref_file.name}",
                        fix_suggestion="Add table of contents at top for easier navigation"
                    ))

    # SS006: check for deeply nested references
    # Look for links in SKILL.md that go to files that themselves have links
    md_links = re.findall(r'\[.*?\]\(([^)]+\.md)\)', body)
    for link in md_links:
        link_path = skill_path / link
        if link_path.exists():
            linked_content = link_path.read_text()
            nested_links = re.findall(r'\[.*?\]\(([^)]+\.md)\)', linked_content)
            # Filter out self-references and external links
            nested_links = [l for l in nested_links if not l.startswith('http') and l != link]
            if nested_links:
                issues.append(Issue(
                    rule_id="SS006",
                    severity=Severity.WARNING,
                    message=f"Deeply nested reference detected",
                    location=f"{link} -> {nested_links[0]}",
                    fix_suggestion="Keep references one level deep from SKILL.md"
                ))

    return issues


# ============================================================================
# Content & Writing Validators (CW001-CW006)
# ============================================================================

def validate_content(skill_path: Path, body: str) -> List[Issue]:
    """Validate content and writing standards."""
    issues = []
    lines = body.split('\n')

    # Track code block state
    in_code_block = False

    # CW001: Second-person language
    for i, line in enumerate(lines, 1):
        # Track code block boundaries
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        # Skip content inside code blocks
        if in_code_block:
            continue
        for pattern in SECOND_PERSON_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                issues.append(Issue(
                    rule_id="CW001",
                    severity=Severity.WARNING,
                    message="Second-person language detected",
                    location=f"SKILL.md:{i}",
                    current_value=match.group(),
                    fix_suggestion="Use imperative form: 'Create...' not 'You should create...'"
                ))
                break  # One per line

    # Reset for next pass
    in_code_block = False

    # CW002: First-person language in body
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        for pattern in FIRST_PERSON_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                issues.append(Issue(
                    rule_id="CW002",
                    severity=Severity.WARNING,
                    message="First-person language detected",
                    location=f"SKILL.md:{i}",
                    current_value=match.group(),
                    fix_suggestion="Use third person or imperative: 'This skill provides' not 'I can help'"
                ))
                break

    # CW003: Multiple options without default (detect lists of alternatives)
    alternatives_pattern = r'(?:use|try|choose)\s+(?:\w+,\s*)+(?:or|and)\s+\w+'
    for i, line in enumerate(lines, 1):
        if re.search(alternatives_pattern, line, re.IGNORECASE):
            # Check if there's a default indicator
            if not re.search(r'\((?:default|recommended|preferred)\)', line, re.IGNORECASE):
                issues.append(Issue(
                    rule_id="CW003",
                    severity=Severity.SUGGESTION,
                    message="Multiple options listed without default",
                    location=f"SKILL.md:{i}",
                    fix_suggestion="Provide one default with escape hatch: 'Use X (or another if preferred)'"
                ))

    # CW004: MCP tool without fully qualified name
    mcp_pattern = r'\b(mcp_\w+)\b'
    for i, line in enumerate(lines, 1):
        match = re.search(mcp_pattern, line)
        if match:
            tool_name = match.group(1)
            if ':' not in line[max(0, match.start()-20):match.end()+20]:
                issues.append(Issue(
                    rule_id="CW004",
                    severity=Severity.WARNING,
                    message="MCP tool may not use fully qualified name",
                    location=f"SKILL.md:{i}",
                    current_value=tool_name,
                    fix_suggestion="Use 'ServerName:tool_name' format for MCP tools"
                ))

    return issues


# ============================================================================
# File Organization Validators (FO001-FO007)
# ============================================================================

FORBIDDEN_FILES = {
    'README.md', 'readme.md',
    'INSTALLATION_GUIDE.md', 'INSTALL.md',
    'CHANGELOG.md', 'HISTORY.md',
    'QUICK_REFERENCE.md',
    'CONTRIBUTING.md',
    'LICENSE.md',  # LICENSE.txt is OK
}

UPPERCASE_DOC_PATTERN = re.compile(r'^[A-Z][A-Z0-9_-]*\.md$')
LOWERCASE_SCRIPT_PATTERN = re.compile(r'^[a-z][a-z0-9_]*\.py$')


def validate_files(skill_path: Path) -> List[Issue]:
    """Validate file organization against best practices."""
    issues = []

    # FO001: Forbidden files
    for forbidden in FORBIDDEN_FILES:
        if (skill_path / forbidden).exists():
            issues.append(Issue(
                rule_id="FO001",
                severity=Severity.WARNING,
                message=f"Forbidden file detected: {forbidden}",
                location=forbidden,
                fix_suggestion="Remove this file - skills should not include auxiliary documentation"
            ))

    # Check all files
    for file_path in skill_path.rglob('*'):
        if not file_path.is_file():
            continue

        relative = file_path.relative_to(skill_path)
        filename = file_path.name

        # FO002: Documentation files should be UPPERCASE
        if filename.endswith('.md') and str(relative.parent) in ['.', 'references']:
            if not UPPERCASE_DOC_PATTERN.match(filename) and filename != 'SKILL.md':
                issues.append(Issue(
                    rule_id="FO002",
                    severity=Severity.WARNING,
                    message=f"Documentation file not UPPERCASE",
                    location=str(relative),
                    fix_suggestion=f"Rename to {filename.upper()}"
                ))

        # FO003, FO004, FO005: Script validation
        if str(relative).startswith('scripts/') and filename.endswith('.py'):
            # FO003: Script naming
            if not LOWERCASE_SCRIPT_PATTERN.match(filename):
                issues.append(Issue(
                    rule_id="FO003",
                    severity=Severity.WARNING,
                    message="Script file not lowercase_with_underscores",
                    location=str(relative),
                    fix_suggestion=f"Rename to {re.sub(r'[^a-z0-9_.]', '_', filename.lower())}"
                ))

            # FO004: Script executable
            if not os.access(file_path, os.X_OK):
                issues.append(Issue(
                    rule_id="FO004",
                    severity=Severity.ERROR,
                    message="Script not executable",
                    location=str(relative),
                    fix_suggestion=f"Run: chmod +x {relative}"
                ))

            # FO005: Shebang
            try:
                first_line = file_path.read_text().split('\n')[0]
                if not first_line.startswith('#!'):
                    issues.append(Issue(
                        rule_id="FO005",
                        severity=Severity.ERROR,
                        message="Python script missing shebang",
                        location=str(relative),
                        fix_suggestion="Add '#!/usr/bin/env python3' as first line"
                    ))
            except Exception:
                pass

    # FO006: Empty resource directories
    for dir_name in ['scripts', 'references', 'assets']:
        dir_path = skill_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            files = list(dir_path.rglob('*'))
            files = [f for f in files if f.is_file()]
            if not files:
                issues.append(Issue(
                    rule_id="FO006",
                    severity=Severity.SUGGESTION,
                    message=f"Empty resource directory",
                    location=f"{dir_name}/",
                    fix_suggestion=f"Remove unused {dir_name}/ directory"
                ))

    # FO007: Windows-style paths in content
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text()
        if '\\' in content and re.search(r'[a-zA-Z]:\\', content):
            issues.append(Issue(
                rule_id="FO007",
                severity=Severity.WARNING,
                message="Windows-style path separator detected",
                location="SKILL.md",
                fix_suggestion="Use Unix-style '/' in all paths"
            ))

    return issues


# ============================================================================
# Reference Integrity Validators (RI001-RI003)
# ============================================================================

def validate_references(skill_path: Path, body: str) -> List[Issue]:
    """Validate reference integrity."""
    issues = []

    # Remove code blocks from body before checking references
    # This prevents flagging example links in code blocks
    body_without_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL)

    # Find all markdown links in body (excluding code blocks)
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', body_without_code)

    referenced_files: Set[str] = set()

    for link_text, link_target in md_links:
        # Skip external links
        if link_target.startswith('http://') or link_target.startswith('https://'):
            continue

        # Handle anchor links
        if '#' in link_target:
            file_part, anchor = link_target.split('#', 1)
            if not file_part:  # Same-file anchor
                continue
            link_target = file_part

        referenced_files.add(link_target)

        # RI001: Broken reference
        target_path = skill_path / link_target
        if not target_path.exists():
            issues.append(Issue(
                rule_id="RI001",
                severity=Severity.ERROR,
                message=f"Broken reference: file not found",
                location=f"SKILL.md -> {link_target}",
                fix_suggestion=f"Fix path or create missing file: {link_target}"
            ))

    # Also check for backtick mentions (e.g., `WORKFLOW.md`)
    backtick_mentions = re.findall(r'`([^`]+\.md)`', body_without_code)
    for mention in backtick_mentions:
        referenced_files.add(mention)

    # RI002: Orphan files (not referenced from SKILL.md)
    for file_path in skill_path.rglob('*.md'):
        if file_path.name == 'SKILL.md':
            continue
        relative = str(file_path.relative_to(skill_path))
        filename = file_path.name
        if relative not in referenced_files and filename not in referenced_files:
            # Also check without leading ./
            if relative.lstrip('./') not in referenced_files:
                issues.append(Issue(
                    rule_id="RI002",
                    severity=Severity.WARNING,
                    message="File not referenced from SKILL.md",
                    location=relative,
                    fix_suggestion="Add reference in SKILL.md or remove if unused"
                ))

    return issues


# ============================================================================
# Security Validators (SC001-SC005)
# ============================================================================

def validate_security(skill_path: Path) -> List[Issue]:
    """Validate scripts for security issues."""
    issues = []

    scripts_dir = skill_path / 'scripts'
    if not scripts_dir.exists():
        return issues

    for script_path in scripts_dir.rglob('*.py'):
        try:
            content = script_path.read_text()
            lines = content.split('\n')
            relative = script_path.relative_to(skill_path)

            # Check for ignore comments
            ignored_rules: Set[str] = set()
            for line in lines:
                ignore_match = re.search(r'#\s*skill-validator:\s*ignore\s+(\w+)', line)
                if ignore_match:
                    ignored_rules.add(ignore_match.group(1))

            # SC001: eval/exec detection
            if 'SC001' not in ignored_rules:
                for i, line in enumerate(lines, 1):
                    if re.search(r'\b(eval|exec)\s*\(', line):
                        issues.append(Issue(
                            rule_id="SC001",
                            severity=Severity.CRITICAL,
                            message="Dynamic code execution detected (eval/exec)",
                            location=f"{relative}:{i}",
                            fix_suggestion="Remove eval/exec or add '# skill-validator: ignore SC001' with justification"
                        ))

            # SC002: Undocumented magic numbers
            if 'SC002' not in ignored_rules:
                for i, line in enumerate(lines, 1):
                    # Look for numeric assignments
                    number_match = re.search(r'=\s*(\d{2,})\s*$', line)
                    if number_match:
                        # Check if there's a comment on this line or the line above
                        has_comment = '#' in line
                        if i > 1:
                            prev_line = lines[i-2]
                            has_comment = has_comment or prev_line.strip().startswith('#')
                        if not has_comment:
                            issues.append(Issue(
                                rule_id="SC002",
                                severity=Severity.WARNING,
                                message=f"Undocumented numeric constant: {number_match.group(1)}",
                                location=f"{relative}:{i}",
                                fix_suggestion="Add comment explaining the constant's purpose"
                            ))

            # SC004: Base64/hex encoded strings (potential obfuscation)
            if 'SC004' not in ignored_rules:
                for i, line in enumerate(lines, 1):
                    # Long hex strings
                    if re.search(r'["\'][0-9a-fA-F]{32,}["\']', line):
                        issues.append(Issue(
                            rule_id="SC004",
                            severity=Severity.WARNING,
                            message="Long hex-encoded string detected",
                            location=f"{relative}:{i}",
                            fix_suggestion="Explain purpose or remove obfuscated code"
                        ))
                    # Base64 patterns
                    if re.search(r'base64\.(b64decode|decode)', line):
                        issues.append(Issue(
                            rule_id="SC004",
                            severity=Severity.WARNING,
                            message="Base64 decoding detected",
                            location=f"{relative}:{i}",
                            fix_suggestion="Document the purpose of encoded content"
                        ))

        except Exception as e:
            issues.append(Issue(
                rule_id="SC000",
                severity=Severity.ERROR,
                message=f"Failed to analyze script: {e}",
                location=str(script_path.relative_to(skill_path)),
                fix_suggestion="Check file encoding and syntax"
            ))

    return issues


# ============================================================================
# Main Validation Function
# ============================================================================

def validate_skill(skill_path: Path, ignored_rules: Set[str] = None) -> List[Issue]:
    """Run all validators on a skill directory."""
    if ignored_rules is None:
        ignored_rules = set()

    issues: List[Issue] = []

    # SS001: Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        issues.append(Issue(
            rule_id="SS001",
            severity=Severity.CRITICAL,
            message="SKILL.md not found",
            location=str(skill_path),
            fix_suggestion="Create SKILL.md with YAML frontmatter"
        ))
        return issues

    # Read and parse SKILL.md
    content = skill_md.read_text()
    frontmatter, body, error = parse_frontmatter(content)

    if error:
        issues.append(Issue(
            rule_id="FM000",
            severity=Severity.CRITICAL,
            message=error,
            location="SKILL.md",
            fix_suggestion="Fix YAML frontmatter syntax"
        ))
        return issues

    # Run validators
    if frontmatter:
        issues.extend(validate_frontmatter(skill_path, frontmatter, body))
    issues.extend(validate_structure(skill_path, content, body))
    issues.extend(validate_content(skill_path, body))
    issues.extend(validate_files(skill_path))
    issues.extend(validate_references(skill_path, body))
    issues.extend(validate_security(skill_path))

    # Filter ignored rules
    issues = [i for i in issues if i.rule_id not in ignored_rules]

    # Sort by severity (most severe first)
    issues.sort(key=lambda i: -i.severity.value)

    return issues


# ============================================================================
# Report Generation
# ============================================================================

def format_text_report(skill_name: str, skill_path: Path, issues: List[Issue]) -> str:
    """Generate text format report."""
    lines = []

    # Header
    lines.append(f"=== Skill Validation Report: {skill_name} ===")
    lines.append(f"Path: {skill_path}")
    lines.append("")

    # Summary
    counts = {s: 0 for s in Severity}
    for issue in issues:
        counts[issue.severity] += 1

    summary_parts = []
    for severity in [Severity.CRITICAL, Severity.ERROR, Severity.WARNING, Severity.SUGGESTION]:
        if counts[severity] > 0:
            summary_parts.append(f"{counts[severity]} {severity.name.lower()}")

    if summary_parts:
        lines.append(f"Summary: {', '.join(summary_parts)}")
    else:
        lines.append("Summary: No issues found!")
    lines.append("")
    lines.append("─" * 70)

    # Issues
    for issue in issues:
        lines.append("")
        severity_label = f"[{issue.severity.name}]"
        lines.append(f"{severity_label} {issue.rule_id}: {issue.message}")
        lines.append(f"  Location: {issue.location}")
        if issue.current_value:
            lines.append(f"  Found: {issue.current_value}")
        if issue.fix_suggestion:
            lines.append(f"  Fix: {issue.fix_suggestion}")
        lines.append("")
        lines.append("─" * 70)

    # Footer
    if issues:
        lines.append("")
        lines.append("Use --ignore RULE1,RULE2 to suppress specific rules.")

    return '\n'.join(lines)


def format_json_report(skill_name: str, skill_path: Path, issues: List[Issue]) -> str:
    """Generate JSON format report."""
    counts = {s.name.lower(): 0 for s in Severity}
    for issue in issues:
        counts[issue.severity.name.lower()] += 1

    report = {
        "skill_name": skill_name,
        "skill_path": str(skill_path),
        "summary": {
            **counts,
            "total": len(issues)
        },
        "issues": [issue.to_dict() for issue in issues],
        "passed": counts["critical"] == 0 and counts["error"] == 0
    }

    return json.dumps(report, indent=2)


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Validate skills against Anthropic best practices"
    )
    parser.add_argument(
        "skill_path",
        type=Path,
        help="Path to skill directory"
    )
    parser.add_argument(
        "--min-severity",
        choices=["critical", "error", "warning", "suggestion"],
        default="suggestion",
        help="Minimum severity to report (default: suggestion)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--ignore",
        type=str,
        default="",
        help="Comma-separated list of rules to ignore"
    )

    args = parser.parse_args()

    skill_path = args.skill_path.resolve()

    if not skill_path.exists():
        print(f"Error: Path does not exist: {skill_path}", file=sys.stderr)
        sys.exit(1)

    if not skill_path.is_dir():
        print(f"Error: Path is not a directory: {skill_path}", file=sys.stderr)
        sys.exit(1)

    # Parse ignored rules
    ignored_rules = set(r.strip() for r in args.ignore.split(',') if r.strip())

    # Run validation
    issues = validate_skill(skill_path, ignored_rules)

    # Filter by severity
    severity_map = {
        "critical": Severity.CRITICAL,
        "error": Severity.ERROR,
        "warning": Severity.WARNING,
        "suggestion": Severity.SUGGESTION
    }
    min_severity = severity_map[args.min_severity]
    issues = [i for i in issues if i.severity.value >= min_severity.value]

    # Generate report
    skill_name = skill_path.name
    if args.format == "json":
        print(format_json_report(skill_name, skill_path, issues))
    else:
        print(format_text_report(skill_name, skill_path, issues))

    # Exit code: 1 if critical or error, 0 otherwise
    has_critical = any(i.severity == Severity.CRITICAL for i in issues)
    has_error = any(i.severity == Severity.ERROR for i in issues)

    sys.exit(1 if has_critical or has_error else 0)


if __name__ == "__main__":
    main()
