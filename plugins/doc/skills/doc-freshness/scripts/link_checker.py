#!/usr/bin/env python3
"""
Broken link and file reference detection for doc-freshness.

Parses markdown files for internal links, anchor references, and
backtick-quoted file paths. Verifies targets exist.

Uses only standard library (no external dependencies). Python 3.8+.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    extract_backtick_paths,
    extract_headings,
    heading_to_slug,
    parse_markdown_links,
    read_file_safe,
    resolve_relative_path,
)


def check_links(
    doc_path: Path, project_root: Path, content: Optional[str] = None,
    check_backtick_paths: bool = False,
) -> List[Dict[str, object]]:
    """Check all internal links in a markdown file.

    Returns list of findings with keys:
        doc, line, target, status ('ok'|'broken'|'warning'), reason, type.
    """
    if content is None:
        content = read_file_safe(doc_path)
    if content is None:
        return [{
            "doc": str(doc_path.relative_to(project_root)),
            "line": 0,
            "target": "(file)",
            "status": "broken",
            "reason": "Cannot read file",
            "type": "file",
        }]

    findings: List[Dict[str, object]] = []
    rel_doc = str(doc_path.relative_to(project_root))

    # Check markdown links
    links = parse_markdown_links(content)
    self_heading_slugs = {str(h["slug"]) for h in extract_headings(content)}
    for link in links:
        target = str(link["target"])
        line = link["line"]

        # Skip external URLs
        if target.startswith(("http://", "https://", "mailto:", "ftp://", "data:")):
            continue

        # Skip pure anchor links within same file
        if target.startswith("#"):
            slug = target[1:]
            if slug not in self_heading_slugs:
                findings.append({
                    "doc": rel_doc,
                    "line": line,
                    "target": target,
                    "status": "broken",
                    "reason": f"Anchor '{slug}' not found in this file",
                    "type": "anchor",
                })
            continue

        # Handle target#anchor
        has_anchor = "#" in target
        anchor = ""
        if has_anchor:
            target_path_str, anchor = target.rsplit("#", 1)
        else:
            target_path_str = target

        # Resolve the target path (with project root boundary check)
        resolved = resolve_relative_path(doc_path, target_path_str, project_root)

        if not resolved.exists():
            findings.append({
                "doc": rel_doc,
                "line": line,
                "target": target,
                "status": "broken",
                "reason": "Target file does not exist",
                "type": "link",
            })
        elif has_anchor and anchor:
            # Verify anchor in target file
            target_content = read_file_safe(resolved)
            if target_content:
                headings = extract_headings(target_content)
                heading_slugs = {str(h["slug"]) for h in headings}
                if anchor not in heading_slugs:
                    findings.append({
                        "doc": rel_doc,
                        "line": line,
                        "target": target,
                        "status": "broken",
                        "reason": f"Anchor '#{anchor}' not found in {target_path_str}",
                        "type": "anchor",
                    })

    # Check backtick-quoted file paths (opt-in, off by default)
    if not check_backtick_paths:
        return findings
    backtick_paths = extract_backtick_paths(content)
    for ref in backtick_paths:
        ref_path = str(ref["path"])
        line = ref["line"]

        # Resolve relative to project root (backtick paths are typically root-relative)
        resolved = project_root / ref_path
        if not resolved.exists():
            # Also try relative to the doc's directory
            resolved_from_doc = doc_path.parent / ref_path
            if not resolved_from_doc.exists():
                findings.append({
                    "doc": rel_doc,
                    "line": line,
                    "target": ref_path,
                    "status": "warning",
                    "reason": "Referenced file path does not exist",
                    "type": "file_ref",
                })

    return findings


def check_all_links(
    doc_paths: List[Path], project_root: Path,
    check_backtick_paths: bool = False,
) -> Dict[str, object]:
    """Check links across all discovered documentation files.

    Returns dict with:
        findings: list of all findings (broken/warning only)
        summary: {total_checked, broken, warnings, ok}
    """
    all_findings: List[Dict[str, object]] = []
    total_links = 0
    broken = 0
    warnings = 0

    for doc_path in doc_paths:
        content = read_file_safe(doc_path)
        if content:
            total_links += len(parse_markdown_links(content))
            if check_backtick_paths:
                total_links += len(extract_backtick_paths(content))

        findings = check_links(doc_path, project_root, content, check_backtick_paths)
        for f in findings:
            if f["status"] == "broken":
                broken += 1
            elif f["status"] == "warning":
                warnings += 1
        all_findings.extend(findings)

    return {
        "findings": all_findings,
        "summary": {
            "total_checked": total_links,
            "broken": broken,
            "warnings": warnings,
            "ok": total_links - broken - warnings,
        },
    }


if __name__ == "__main__":
    import json

    if len(sys.argv) < 3:
        print("Usage: link_checker.py <project-root> <doc-file> [<doc-file> ...]",
              file=sys.stderr)
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    doc_files = [Path(f).resolve() for f in sys.argv[2:]]

    result = check_all_links(doc_files, root)
    print(json.dumps(result, indent=2, default=str))
