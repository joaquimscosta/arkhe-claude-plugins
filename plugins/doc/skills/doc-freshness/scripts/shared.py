#!/usr/bin/env python3
"""
Shared utilities for doc-freshness scanners.

Common helpers for markdown parsing, git operations, and file handling.
Uses only standard library (no external dependencies). Python 3.8+.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Directories to skip when walking project trees
SKIP_DIRS: Set[str] = {
    "build", ".gradle", "node_modules", ".git", "target", "out", ".idea",
    "__pycache__", ".venv", "venv", "env", ".tox", ".nox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", ".next", ".turbo", "coverage",
    "vendor", ".bundle", "_site", ".docusaurus",
}

# Default glob patterns for discovering documentation files
DEFAULT_DOC_PATTERNS: List[str] = [
    "README.md", "CLAUDE.md", "CONTRIBUTING.md", "CHANGELOG.md",
    "INSTALL.md", "INSTALLATION.md", "SETUP.md", "LICENSE.md",
    "docs/**/*.md", "wiki/**/*.md", "plan/**/*.md",
    ".github/**/*.md",
]

# Default patterns to exclude
DEFAULT_EXCLUDE_PATTERNS: List[str] = [
    "node_modules/**", ".git/**", "vendor/**", ".venv/**", "venv/**",
    "dist/**", "build/**", "target/**", "coverage/**",
]


def extract_frontmatter(content: str) -> Optional[Dict[str, str]]:
    """Extract YAML frontmatter from markdown content.

    Parses the block between opening and closing '---' delimiters.
    Returns flat key-value dict, or None if no frontmatter found.
    """
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for i, line in enumerate(lines[1:50], start=1):
        if line.strip() == "---":
            result: Dict[str, str] = {}
            for fm_line in lines[1:i]:
                fm_stripped = fm_line.strip()
                if not fm_stripped or fm_stripped.startswith("#"):
                    continue
                if ":" in fm_stripped:
                    key, _, value = fm_stripped.partition(":")
                    value = value.strip().strip('"').strip("'")
                    if value:
                        result[key.strip()] = value
            return result if result else None

    return None


def detect_doc_tier(path: Path) -> str:
    """Detect whether a doc qualifies for deep or basic scanning.

    Deep tier: has YAML frontmatter with last_updated or version fields.
    Basic tier: everything else.
    """
    content = read_file_safe(path)
    if not content:
        return "basic"

    fm = extract_frontmatter(content)
    if fm and ("last_updated" in fm or "version" in fm):
        return "deep"
    return "basic"


def read_file_safe(path: Path) -> Optional[str]:
    """Read a file's text content, returning None on any error."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def read_json_safe(path: Path) -> Optional[dict]:
    """Read and parse a JSON file, returning None on any error."""
    import json
    content = read_file_safe(path)
    if content is None:
        return None
    try:
        return json.loads(content)
    except (ValueError, TypeError):
        return None


def read_yaml_section(path: Path, section: str) -> Optional[dict]:
    """Read a YAML file and extract a top-level section.

    Uses a simple line-based parser (no PyYAML dependency).
    Only handles flat key-value and simple list structures.
    """
    content = read_file_safe(path)
    if content is None:
        return None

    lines = content.splitlines()
    in_section = False
    result: dict = {}
    current_key = None
    current_list: List[str] = []
    base_indent = 0

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        if indent == 0 and stripped.endswith(":"):
            if in_section:
                if current_key and current_list:
                    result[current_key] = current_list
                break
            if stripped == f"{section}:":
                in_section = True
                base_indent = 2
            continue

        if not in_section:
            continue

        if indent < base_indent and not stripped.startswith("-"):
            if current_key and current_list:
                result[current_key] = current_list
            break

        if ":" in stripped and not stripped.startswith("-"):
            if current_key and current_list:
                result[current_key] = current_list
                current_list = []
            key, _, value = stripped.partition(":")
            current_key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                result[current_key] = value
                current_key = None
        elif stripped.startswith("- "):
            item = stripped[2:].strip().strip('"').strip("'")
            current_list.append(item)

    if in_section and current_key and current_list:
        result[current_key] = current_list

    return result if result else None


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

# Matches fenced code block delimiters (backtick or tilde, 3+ chars)
_FENCE_RE = re.compile(r'^(`{3,}|~{3,})')

# Matches an opening fence: backticks/tildes with optional info string
_FENCE_OPEN_RE = re.compile(r'^(`{3,}|~{3,})(.*)$')


def _is_fence_line(stripped: str) -> bool:
    """Check if a stripped line is a fenced code block delimiter."""
    return bool(_FENCE_RE.match(stripped))


def _update_fence_state(
    stripped: str, in_code_block: bool, open_fence: str
) -> tuple:
    """Track fenced code block state per CommonMark spec.

    Returns (in_code_block, open_fence) tuple.

    Rules:
    - Opening fence: 3+ backticks/tildes, optionally followed by an info
      string.  Only recognised when NOT already inside a code block.
    - Closing fence: 3+ of the SAME character as the opener, with NO info
      string, and at least as many fence characters as the opener.
    - A line that looks like a fence but has an info string while inside a
      code block is treated as plain content (not a fence transition).
    """
    m = _FENCE_OPEN_RE.match(stripped)
    if not m:
        return in_code_block, open_fence

    fence_chars = m.group(1)   # e.g. "```" or "~~~~"
    info_string = m.group(2).strip()

    if not in_code_block:
        # Opening fence — enter code block regardless of info string
        return True, fence_chars
    else:
        # Inside a code block — only close if:
        # 1. Same fence character type (backtick vs tilde)
        # 2. At least as many chars as the opener
        # 3. No info string
        same_char = fence_chars[0] == open_fence[0]
        long_enough = len(fence_chars) >= len(open_fence)
        if same_char and long_enough and not info_string:
            return False, ""
        # Otherwise it's just content inside the code block
        return in_code_block, open_fence

# Matches [text](target) and [text](target "title")
_INLINE_LINK_RE = re.compile(
    r'\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)'
)

# Matches [text]: target  (reference-style links, with optional angle brackets)
_REF_LINK_RE = re.compile(
    r'^\[([^\]]+)\]:\s+<?(\S+?)>?(?:\s|$)', re.MULTILINE
)

# Matches <img src="..."> and <img src='...'>
_IMG_SRC_RE = re.compile(
    r'<img\s[^>]*src=["\']([^"\']+)["\']', re.IGNORECASE
)

# Matches backtick-quoted file paths like `src/foo.ts` or `docs/bar.md`
_BACKTICK_PATH_RE = re.compile(
    r'`([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)`'
)

# Patterns that look like file paths but are not
_NON_FILE_PREFIXES = re.compile(
    r'^(?:'
    r'(?:feature|fix|release|hotfix|bugfix|chore|dependabot)/'  # git branches
    r'|roles/'                                                    # IAM roles
    r')',
    re.IGNORECASE,
)

# Known code file extensions (for owner/repo disambiguation)
_CODE_EXTENSIONS = {
    "md", "py", "js", "ts", "tsx", "jsx", "go", "rs", "java",
    "kt", "kts", "rb", "php", "c", "h", "cpp", "hpp", "cs", "swift",
    "yaml", "yml", "json", "toml", "xml", "html", "css", "scss",
    "sql", "sh", "bash", "zsh", "ps1", "bat", "cmd",
    "txt", "cfg", "ini", "conf", "env", "lock", "sum",
    "vue", "svelte", "astro", "mdx", "png", "jpg", "svg", "gif",
    "gradle", "properties", "sq",
}


def _is_likely_file_path(path: str) -> bool:
    """Heuristic: does this backtick-quoted string look like a file path?

    Returns False for git branches, IAM roles, runtime URLs, and owner/repo refs.
    """
    if _NON_FILE_PREFIXES.match(path):
        return False

    # Skip owner/repo patterns: exactly 2 segments with non-code extension
    # e.g. "deznode/skola.dev" (TLD), but keep "src/main.py" (code extension)
    segments = path.split("/")
    if len(segments) == 2 and "." not in segments[0] and "." in segments[1]:
        ext = segments[1].rsplit(".", 1)[-1].lower()
        if ext not in _CODE_EXTENSIONS:
            return False

    return True


def parse_markdown_links(content: str) -> List[Dict[str, object]]:
    """Extract all links from markdown content.

    Returns list of dicts with keys: text, target, line, type.
    Types: 'inline', 'reference', 'image'.
    Skips links inside fenced code blocks.
    """
    links: List[Dict[str, object]] = []
    lines = content.splitlines()
    in_code_block = False
    open_fence = ""

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        prev_state = in_code_block
        in_code_block, open_fence = _update_fence_state(
            stripped, in_code_block, open_fence
        )
        if in_code_block or prev_state != in_code_block:
            continue

        for match in _INLINE_LINK_RE.finditer(line):
            links.append({
                "text": match.group(1),
                "target": match.group(2),
                "line": line_num,
                "type": "inline",
            })

        # Strip inline backtick spans before checking HTML img tags
        # to avoid matching <img src="..."> inside code spans
        line_no_backticks = re.sub(r'`[^`]+`', '', line)
        for match in _IMG_SRC_RE.finditer(line_no_backticks):
            links.append({
                "text": "(image)",
                "target": match.group(1),
                "line": line_num,
                "type": "image",
            })

        # Reference-style links on this line
        ref_match = _REF_LINK_RE.match(line)
        if ref_match:
            links.append({
                "text": ref_match.group(1),
                "target": ref_match.group(2),
                "line": line_num,
                "type": "reference",
            })

    return links


def extract_backtick_paths(content: str) -> List[Dict[str, object]]:
    """Extract backtick-quoted file paths from markdown content.

    Filters for paths that look like actual file references (contain / and extension).
    """
    paths: List[Dict[str, object]] = []
    lines = content.splitlines()
    in_code_block = False
    open_fence = ""

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        prev_state = in_code_block
        in_code_block, open_fence = _update_fence_state(
            stripped, in_code_block, open_fence
        )
        if in_code_block or prev_state != in_code_block:
            continue

        for match in _BACKTICK_PATH_RE.finditer(line):
            path = match.group(1)
            # Only include paths with a directory separator that look like files
            if "/" in path and _is_likely_file_path(path):
                paths.append({
                    "path": path,
                    "line": line_num,
                })

    return paths


def extract_headings(content: str) -> List[Dict[str, object]]:
    """Extract markdown headings from content.

    Returns list of dicts with keys: level, text, slug, line.
    """
    headings: List[Dict[str, object]] = []
    lines = content.splitlines()
    in_code_block = False
    open_fence = ""

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        prev_state = in_code_block
        in_code_block, open_fence = _update_fence_state(
            stripped, in_code_block, open_fence
        )
        if in_code_block or prev_state != in_code_block:
            continue

        match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*#*\s*)?$', stripped)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            slug = heading_to_slug(text)
            headings.append({
                "level": level,
                "text": text,
                "slug": slug,
                "line": line_num,
            })

    return headings


# ---------------------------------------------------------------------------
# Severity helpers (shared across formatters)
# ---------------------------------------------------------------------------

# Severity ordering (higher = more severe)
SEVERITY_ORDER: Dict[str, int] = {
    "critical": 3,
    "error": 3,      # Treat "error" same as "critical"
    "warning": 2,
    "info": 1,
}


def normalize_severity(raw: str) -> str:
    """Normalize severity string to one of: error, warning, info.

    Maps 'critical', 'ERROR', 'broken', 'mismatch' etc. to canonical levels.
    """
    lower = raw.lower().strip()
    if lower in ("critical", "error", "broken", "mismatch"):
        return "error"
    if lower in ("warning", "warn", "minor_mismatch", "outdated_frontmatter"):
        return "warning"
    return "info"


def severity_meets_threshold(severity: str, threshold: str) -> bool:
    """Check if a severity meets the minimum threshold."""
    sev_rank = SEVERITY_ORDER.get(severity, 0)
    thr_rank = SEVERITY_ORDER.get(threshold, 0)
    return sev_rank >= thr_rank


def heading_to_slug(text: str) -> str:
    """Convert a heading to a GitHub-compatible anchor slug.

    Rules: lowercase, spaces→hyphens, strip non-ASCII and non-alphanumeric
    except hyphens. Matches GitHub's anchor generation algorithm.
    """
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s', '-', slug)
    slug = slug.strip('-')
    return slug


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git_last_modified(file_path: str, project_root: str) -> Optional[str]:
    """Get the last commit date for a file via git log.

    Returns strict ISO 8601 date string (e.g., '2026-03-15T10:30:00-04:00') or None.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", file_path],
            capture_output=True, text=True, timeout=10,
            cwd=project_root,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def git_is_available(project_root: str) -> bool:
    """Check if git is available and the directory is a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=5,
            cwd=project_root,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def resolve_relative_path(
    from_file: Path, link_target: str, project_root: Optional[Path] = None
) -> Path:
    """Resolve a relative link target from a document's location.

    If project_root is provided, returns Path("") for paths that
    escape the project root (path traversal protection).
    """
    # Strip anchor fragments
    target = link_target.split("#")[0]
    if not target:
        return from_file  # Same-file anchor
    resolved = (from_file.parent / target).resolve()
    if project_root is not None:
        try:
            resolved.relative_to(project_root.resolve())
        except ValueError:
            return Path("")  # Escapes project root
    return resolved


def discover_markdown_files(
    root: Path,
    patterns: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> List[Path]:
    """Discover markdown files in a project using glob patterns.

    Args:
        root: Project root directory.
        patterns: Glob patterns to search. Defaults to DEFAULT_DOC_PATTERNS.
        exclude: Glob patterns to exclude. Defaults to DEFAULT_EXCLUDE_PATTERNS.

    Returns:
        Sorted list of unique markdown file paths.
    """
    if patterns is None:
        patterns = DEFAULT_DOC_PATTERNS
    if exclude is None:
        exclude = DEFAULT_EXCLUDE_PATTERNS

    # Build exclusion set
    excluded: Set[Path] = set()
    for pattern in exclude:
        excluded.update(root.glob(pattern))

    # Discover files
    found: Set[Path] = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file() and path not in excluded:
                # Check not inside a skip directory
                parts = path.relative_to(root).parts
                if not any(part in SKIP_DIRS for part in parts):
                    found.add(path)

    return sorted(found)
