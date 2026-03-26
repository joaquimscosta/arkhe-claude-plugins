#!/usr/bin/env python3
"""
Version staleness detection for doc-freshness.

Extracts version references from markdown files and compares them
against ground truth sources (package.json, .nvmrc, pyproject.toml, etc.).

Uses only standard library (no external dependencies). Python 3.8+.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import extract_frontmatter, read_file_safe, read_json_safe


# ---------------------------------------------------------------------------
# Ground truth extractors
# ---------------------------------------------------------------------------

def _extract_from_package_json(root: Path) -> Dict[str, str]:
    """Extract version info from package.json."""
    versions: Dict[str, str] = {}
    data = read_json_safe(root / "package.json")
    if data:
        if "version" in data:
            versions["package-version"] = data["version"]
        engines = data.get("engines", {})
        if "node" in engines:
            # Extract numeric version from range like ">=18.0.0"
            match = re.search(r'(\d+(?:\.\d+)*)', engines["node"])
            if match:
                versions["node"] = match.group(1)
        if "npm" in engines:
            match = re.search(r'(\d+(?:\.\d+)*)', engines["npm"])
            if match:
                versions["npm"] = match.group(1)
    return versions


def _extract_from_nvmrc(root: Path) -> Dict[str, str]:
    """Extract Node version from .nvmrc."""
    content = read_file_safe(root / ".nvmrc")
    if content:
        version = content.strip().lstrip("v")
        if re.match(r'\d+', version):
            return {"node": version}
    return {}


def _extract_from_python_version(root: Path) -> Dict[str, str]:
    """Extract Python version from .python-version."""
    content = read_file_safe(root / ".python-version")
    if content:
        version = content.strip()
        if re.match(r'\d+\.\d+', version):
            return {"python": version}
    return {}


def _extract_from_pyproject(root: Path) -> Dict[str, str]:
    """Extract Python version requirement from pyproject.toml."""
    content = read_file_safe(root / "pyproject.toml")
    if content:
        versions: Dict[str, str] = {}
        # requires-python = ">=3.8"
        match = re.search(r'requires-python\s*=\s*"([^"]+)"', content)
        if match:
            ver_match = re.search(r'(\d+\.\d+)', match.group(1))
            if ver_match:
                versions["python"] = ver_match.group(1)
        # version = "1.2.3"
        match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if match:
            versions["package-version"] = match.group(1)
        return versions
    return {}


def _extract_from_go_mod(root: Path) -> Dict[str, str]:
    """Extract Go version from go.mod."""
    content = read_file_safe(root / "go.mod")
    if content:
        match = re.search(r'^go\s+(\d+\.\d+)', content, re.MULTILINE)
        if match:
            return {"go": match.group(1)}
    return {}


def _extract_from_tool_versions(root: Path) -> Dict[str, str]:
    """Extract versions from .tool-versions (asdf)."""
    content = read_file_safe(root / ".tool-versions")
    if content:
        versions: Dict[str, str] = {}
        for line in content.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                tool = parts[0].lower()
                version = parts[1]
                if tool in ("nodejs", "node"):
                    versions["node"] = version
                elif tool == "python":
                    versions["python"] = version
                elif tool == "golang":
                    versions["go"] = version
                elif tool == "java":
                    versions["java"] = version
                elif tool == "ruby":
                    versions["ruby"] = version
                else:
                    versions[tool] = version
        return versions
    return {}


def _extract_from_gradle(root: Path) -> Dict[str, str]:
    """Extract Java version from build.gradle.kts or build.gradle."""
    for filename in ("build.gradle.kts", "build.gradle"):
        content = read_file_safe(root / filename)
        if content:
            versions: Dict[str, str] = {}
            # Java toolchain: jvmToolchain(21) or languageVersion.set(JavaLanguageVersion.of(21))
            match = re.search(r'jvmToolchain\((\d+)\)', content)
            if match:
                versions["java"] = match.group(1)
            else:
                match = re.search(r'JavaLanguageVersion\.of\((\d+)\)', content)
                if match:
                    versions["java"] = match.group(1)
            # sourceCompatibility / targetCompatibility
            if "java" not in versions:
                match = re.search(
                    r'(?:source|target)Compatibility\s*=\s*["\']?(\d+)["\']?',
                    content,
                )
                if match:
                    versions["java"] = match.group(1)
            return versions
    return {}


def _extract_from_pom(root: Path) -> Dict[str, str]:
    """Extract Java version from pom.xml."""
    content = read_file_safe(root / "pom.xml")
    if content:
        # Use capturing group for tag name, backreference for closing tag
        match = re.search(
            r'<(java\.version|maven\.compiler\.(?:source|target))>(\d+)</\1>',
            content,
        )
        if match:
            return {"java": match.group(2)}
    return {}


def collect_ground_truth(root: Path) -> Dict[str, str]:
    """Collect all version ground truth from project files.

    Returns dict mapping tool/language name to version string.
    Later sources override earlier ones (more specific wins).
    """
    truth: Dict[str, str] = {}

    # Order matters: more specific sources override generic ones
    extractors = [
        _extract_from_tool_versions,
        _extract_from_package_json,
        _extract_from_nvmrc,
        _extract_from_python_version,
        _extract_from_pyproject,
        _extract_from_go_mod,
        _extract_from_gradle,
        _extract_from_pom,
    ]

    for extractor in extractors:
        truth.update(extractor(root))

    return truth


# ---------------------------------------------------------------------------
# Version extraction from markdown
# ---------------------------------------------------------------------------

# Common patterns for version references in docs
_VERSION_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("node", re.compile(
        r'(?:Node(?:\.js)?|node)\s*(?:>=?\s*)?v?(\d+(?:\.\d+)*)', re.IGNORECASE
    )),
    ("python", re.compile(
        r'(?:Python|python)\s*(?:>=?\s*)?(\d+\.\d+(?:\.\d+)?)', re.IGNORECASE
    )),
    ("java", re.compile(
        r'(?:Java|JDK|java)\s*(?:>=?\s*)?(\d+)(?:\.\d+)?', re.IGNORECASE
    )),
    ("go", re.compile(
        r'(?:Go|golang)\s*(?:>=?\s*)?v?(\d+\.\d+(?:\.\d+)?)', re.IGNORECASE
    )),
    ("ruby", re.compile(
        r'(?:Ruby|ruby)\s*(?:>=?\s*)?(\d+\.\d+(?:\.\d+)?)', re.IGNORECASE
    )),
    ("rust", re.compile(
        r'(?:Rust|rust)\s*(?:>=?\s*)?(\d+\.\d+(?:\.\d+)?)', re.IGNORECASE
    )),
]


def extract_doc_versions(
    content: str,
) -> List[Dict[str, object]]:
    """Extract version references from markdown content.

    Returns list of dicts with keys: name, value, line.
    """
    found: List[Dict[str, object]] = []
    lines = content.splitlines()
    in_code_block = False

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for name, pattern in _VERSION_PATTERNS:
            for match in pattern.finditer(line):
                found.append({
                    "name": name,
                    "value": match.group(1),
                    "line": line_num,
                })

    return found


def check_versions(
    doc_path: Path, project_root: Path, ground_truth: Dict[str, str]
) -> List[Dict[str, object]]:
    """Check version references in a doc against ground truth.

    Returns list of findings with keys:
        doc, line, name, doc_value, actual, source, status.
    """
    content = read_file_safe(doc_path)
    if content is None:
        return []

    findings: List[Dict[str, object]] = []
    rel_doc = str(doc_path.relative_to(project_root))
    doc_versions = extract_doc_versions(content)

    for ref in doc_versions:
        name = str(ref["name"])
        if name not in ground_truth:
            continue

        doc_value = str(ref["value"])
        actual = ground_truth[name]

        # Compare major version at minimum
        doc_major = doc_value.split(".")[0]
        actual_major = actual.split(".")[0]

        if doc_major != actual_major:
            findings.append({
                "doc": rel_doc,
                "line": ref["line"],
                "name": name,
                "doc_value": doc_value,
                "actual": actual,
                "status": "mismatch",
            })
        elif doc_value != actual and len(doc_value.split(".")) > 1:
            # Minor/patch mismatch
            findings.append({
                "doc": rel_doc,
                "line": ref["line"],
                "name": name,
                "doc_value": doc_value,
                "actual": actual,
                "status": "minor_mismatch",
            })

    return findings


def check_all_versions(
    doc_paths: List[Path], project_root: Path
) -> Dict[str, object]:
    """Check version references across all documentation files.

    Returns dict with:
        ground_truth: collected version info
        findings: list of mismatches
        summary: {total_refs, mismatches, minor_mismatches}
    """
    truth = collect_ground_truth(project_root)
    all_findings: List[Dict[str, object]] = []
    total_refs = 0
    mismatches = 0
    minor = 0

    for doc_path in doc_paths:
        # Count total version references in this doc
        content = read_file_safe(doc_path)
        if content:
            total_refs += len(extract_doc_versions(content))

        findings = check_versions(doc_path, project_root, truth)
        for f in findings:
            if f["status"] == "mismatch":
                mismatches += 1
            elif f["status"] == "minor_mismatch":
                minor += 1
        all_findings.extend(findings)

    return {
        "ground_truth": truth,
        "findings": all_findings,
        "summary": {
            "total_refs": total_refs,
            "mismatches": mismatches,
            "minor_mismatches": minor,
        },
    }


def check_last_updated(
    doc_path: Path, project_root: Path
) -> Optional[Dict[str, object]]:
    """Check if a doc's last_updated frontmatter matches its git history.

    Only applies to deep-tier docs (those with last_updated in frontmatter).
    Returns a finding dict if the dates differ by >7 days, or None.
    """
    import subprocess

    content = read_file_safe(doc_path)
    if content is None:
        return None

    fm = extract_frontmatter(content)
    if not fm or "last_updated" not in fm:
        return None

    last_updated_str = fm["last_updated"]
    # Parse frontmatter date (YYYY-MM-DD)
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', last_updated_str)
    if not date_match:
        return None

    from datetime import datetime
    try:
        fm_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
    except ValueError:
        return None

    # Get git last modified date
    rel_doc = str(doc_path.relative_to(project_root))
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", rel_doc],
            capture_output=True, text=True, timeout=10,
            cwd=str(project_root),
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        git_date_str = result.stdout.strip()[:10]
        git_date = datetime.strptime(git_date_str, "%Y-%m-%d")
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return None

    # Compare dates
    diff_days = abs((git_date - fm_date).days)
    if diff_days > 7:
        return {
            "doc": rel_doc,
            "frontmatter_date": date_match.group(1),
            "git_date": git_date_str,
            "diff_days": diff_days,
            "status": "outdated_frontmatter",
        }

    return None


if __name__ == "__main__":
    import json

    if len(sys.argv) < 3:
        print("Usage: version_checker.py <project-root> <doc-file> [<doc-file> ...]",
              file=sys.stderr)
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    doc_files = [Path(f).resolve() for f in sys.argv[2:]]

    result = check_all_versions(doc_files, root)
    print(json.dumps(result, indent=2, default=str))
