#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Classify files into Johnny.Decimal areas using keyword heuristics.

Usage:
    uv run jd_classify.py docs/roadmap.md docs/api-design.md
    uv run jd_classify.py docs/*.md
    uv run jd_classify.py docs/*.md --move --yes
    uv run jd_classify.py docs/*.md --no-content
"""

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    DEFAULT_AREAS,
    find_area_by_prefix,
    normalize_filename,
    resolve_config,
)
from jd_index import re_index

# Expanded keyword table for classification
CLASSIFICATION_KEYWORDS: dict[str, list[str]] = {
    "00": [
        "mvp", "requirements", "roadmap", "phase", "setup", "getting-started",
        "execution-plan", "next-steps", "checklist", "onboarding", "quickstart",
        "quick-start", "install", "installation", "tutorial",
    ],
    "10": [
        "product", "branding", "features", "priority", "design-system",
        "editor", "spec", "ux", "ui", "wireframe", "mockup", "prototype",
        "user-story", "persona", "journey",
    ],
    "20": [
        "architecture", "tech-stack", "integration", "structure", "refactor",
        "strategy", "stack", "system-design", "api", "schema", "database",
        "infrastructure", "convention", "pattern", "ddd", "deployment",
    ],
    "30": [
        "research", "resources", "analysis", "investigation", "alternatives",
        "sources", "audit", "spike", "benchmark", "comparison", "evaluation",
        "reference", "study", "exploration",
    ],
    "90": [
        "archive", "old", "deprecated", "historical", "retrospective",
        "v0", "v1", "legacy", "retired", "obsolete",
    ],
}


@dataclass
class ClassificationResult:
    """Result of classifying a single file."""

    file_path: Path
    suggested_prefix: str = ""
    suggested_area: str = ""
    confidence: str = "low"  # high, medium, low
    score: float = 0.0
    reason: str = ""
    filename_matches: list[str] = field(default_factory=list)
    content_matches: list[str] = field(default_factory=list)


def _parse_first_heading(filepath: Path) -> str:
    """Extract the first markdown heading from a file."""
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip().lower()
    except (OSError, UnicodeDecodeError):
        pass
    return ""


def _read_first_n_lines(filepath: Path, n: int = 50) -> str:
    """Read the first N lines of a file as lowercase text."""
    try:
        lines = []
        with open(filepath) as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                lines.append(line.lower())
        return " ".join(lines)
    except (OSError, UnicodeDecodeError):
        return ""


def _match_keywords(
    text: str,
    segments: set[str],
    keywords: dict[str, list[str]],
) -> dict[str, tuple[float, list[str]]]:
    """Match text against keyword table.

    Returns dict of prefix -> (score, matched_keywords).
    Checks both full-text containment and segment-level matching.
    """
    scores: dict[str, tuple[float, list[str]]] = {}
    for prefix, kws in keywords.items():
        matched = []
        for kw in kws:
            if kw in text or kw in segments:
                matched.append(kw)
        if matched:
            # 0.5 for first match, +0.1 per additional, cap at 0.7
            score = min(0.5 + 0.1 * (len(matched) - 1), 0.7)
            scores[prefix] = (score, matched)
    return scores


def classify_file(
    filepath: Path,
    config: dict,
    scan_content: bool = True,
) -> ClassificationResult:
    """Classify a file by combining filename and content signals."""
    result = ClassificationResult(file_path=filepath)
    areas = config.get("areas", DEFAULT_AREAS)

    # Prepare filename for matching
    stem = filepath.stem.lower()
    # Normalize separators to hyphens for segment splitting
    normalized_stem = re.sub(r"[_ ]+", "-", stem)
    segments = set(normalized_stem.split("-"))

    # Pass 1: Filename analysis
    filename_scores = _match_keywords(
        normalized_stem, segments, CLASSIFICATION_KEYWORDS,
    )
    for prefix, (_, kws) in filename_scores.items():
        result.filename_matches.extend(kws)

    # Pass 2: Content analysis (optional)
    content_scores: dict[str, tuple[float, list[str]]] = {}
    if scan_content and filepath.suffix.lower() == ".md" and filepath.is_file():
        heading = _parse_first_heading(filepath)
        body = _read_first_n_lines(filepath, 50)

        # Heading matches (weight 0.3)
        heading_segments = set(re.sub(r"[_ ]+", "-", heading).split("-"))
        heading_scores = _match_keywords(heading, heading_segments, CLASSIFICATION_KEYWORDS)

        # Body matches (weight 0.1 per match, cap 0.3)
        body_segments = set(re.sub(r"[_ ]+", "-", body).split("-"))
        body_scores = _match_keywords(body, body_segments, CLASSIFICATION_KEYWORDS)

        for prefix in set(list(heading_scores) + list(body_scores)):
            h_score = heading_scores.get(prefix, (0, []))[0] * 0.3 / 0.5  # Normalize: max 0.3
            h_kws = heading_scores.get(prefix, (0, []))[1]

            b_raw = body_scores.get(prefix, (0, []))[0]
            b_score = min(b_raw * 0.1 / 0.5, 0.3)  # Normalize: max 0.3
            b_kws = body_scores.get(prefix, (0, []))[1]

            combined_score = h_score + b_score
            combined_kws = list(set(h_kws + b_kws))
            content_scores[prefix] = (min(combined_score, 0.5), combined_kws)

            result.content_matches.extend(combined_kws)

    # Deduplicate content matches
    result.content_matches = list(set(result.content_matches))

    # Combine scores
    all_prefixes = set(list(filename_scores) + list(content_scores))
    combined: dict[str, float] = {}
    for prefix in all_prefixes:
        fn_score = filename_scores.get(prefix, (0, []))[0]
        ct_score = content_scores.get(prefix, (0, []))[0]
        # Agreement bonus when both signals point to same area
        bonus = 0.15 if fn_score > 0 and ct_score > 0 else 0
        combined[prefix] = min(fn_score + ct_score + bonus, 1.0)

    if not combined:
        result.reason = "No keyword matches"
        return result

    # Pick the best
    best_prefix = max(combined, key=lambda k: combined[k])
    result.score = combined[best_prefix]
    result.suggested_prefix = best_prefix
    result.suggested_area = f"{best_prefix}-{areas.get(best_prefix, 'unknown')}"

    if result.score >= 0.7:
        result.confidence = "high"
    elif result.score >= 0.4:
        result.confidence = "medium"
    else:
        result.confidence = "low"

    # Build reason string
    reasons = []
    fn_kws = filename_scores.get(best_prefix, (0, []))[1]
    ct_kws = [k for k in content_scores.get(best_prefix, (0, []))[1] if k not in fn_kws]
    if fn_kws:
        reasons.append(f"Filename: {', '.join(repr(k) for k in fn_kws[:3])}")
    if ct_kws:
        reasons.append(f"Content: {', '.join(repr(k) for k in ct_kws[:3])}")
    result.reason = "; ".join(reasons) if reasons else "Weak keyword match"

    return result


def format_table(results: list[ClassificationResult]) -> str:
    """Format classification results as a human-readable table."""
    # Calculate column widths
    file_w = max(len("File"), max(len(r.file_path.name) for r in results))
    area_w = max(len("Suggested Area"), max(len(r.suggested_area or "(unknown)") for r in results))
    conf_w = len("Confidence")

    header = f"{'File':<{file_w}} | {'Suggested Area':<{area_w}} | {'Confidence':<{conf_w}} | Reason"
    sep = f"{'-' * file_w}-+-{'-' * area_w}-+-{'-' * conf_w}-+{'-' * 30}"

    lines = [header, sep]
    for r in results:
        area = r.suggested_area or "(unknown)"
        lines.append(
            f"{r.file_path.name:<{file_w}} | {area:<{area_w}} | {r.confidence:<{conf_w}} | {r.reason}"
        )
    return "\n".join(lines)


def format_json(results: list[ClassificationResult]) -> str:
    """Format classification results as JSON."""
    data = []
    for r in results:
        data.append({
            "file": str(r.file_path),
            "suggested_area": r.suggested_area,
            "suggested_prefix": r.suggested_prefix,
            "confidence": r.confidence,
            "score": round(r.score, 2),
            "reason": r.reason,
            "filename_matches": r.filename_matches,
            "content_matches": r.content_matches,
        })
    return json.dumps(data, indent=2)


def move_files(
    results: list[ClassificationResult],
    docs_dir: Path,
    config: dict,
    dry_run: bool,
) -> list[tuple[Path, Path]]:
    """Move files to their suggested areas. Returns list of (src, dst) pairs."""
    moved: list[tuple[Path, Path]] = []

    for r in results:
        if r.confidence == "low" or not r.suggested_prefix:
            print(f"  Skip (low confidence): {r.file_path.name} — flag for Claude review")
            continue

        area_dir = find_area_by_prefix(docs_dir, r.suggested_prefix)
        if not area_dir:
            print(f"  Skip (area not found): {r.file_path.name} — {r.suggested_area} doesn't exist")
            continue

        new_name = normalize_filename(r.file_path.name)
        dst = area_dir / new_name

        if dst.exists():
            print(f"  Skip (conflict): {r.file_path.name} — {dst.name} already exists in {area_dir.name}/")
            continue

        if dry_run:
            print(f"  Would move: {r.file_path.name} -> {area_dir.name}/{new_name}")
        else:
            shutil.move(str(r.file_path), str(dst))
            print(f"  Moved: {r.file_path.name} -> {area_dir.name}/{new_name}")
        moved.append((r.file_path, dst))

    return moved


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify files into Johnny.Decimal areas using keyword heuristics"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="File paths to classify",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files to suggested areas (high/medium confidence only)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt when using --move",
    )
    parser.add_argument(
        "--no-content",
        action="store_true",
        help="Disable content scanning (filename-only classification)",
    )
    parser.add_argument(
        "--dir",
        "-d",
        default=None,
        help="Docs directory (default: from config or 'docs')",
    )
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Path to .jd-config.json (auto-detected if not specified)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview move operations without executing",
    )

    args = parser.parse_args()
    base_path = Path.cwd()

    # Load config
    config = resolve_config(args.config, base_path)

    # Resolve docs directory
    if args.dir:
        docs_dir = Path(args.dir)
        if not docs_dir.is_absolute():
            docs_dir = base_path / docs_dir
    else:
        docs_dir = base_path / config.get("root", "docs")

    # Resolve and validate file paths
    files: list[Path] = []
    for f in args.files:
        p = Path(f)
        if not p.is_absolute():
            p = base_path / p
        if not p.exists():
            print(f"Warning: File not found: {f}", file=sys.stderr)
            continue
        if not p.is_file():
            continue
        files.append(p)

    if not files:
        print("Error: No valid files to classify")
        return 1

    # Classify
    scan_content = not args.no_content
    results = [classify_file(f, config, scan_content) for f in files]

    # Output
    if args.json_output:
        print(format_json(results))
    else:
        print(format_table(results))

    # Summary
    high = sum(1 for r in results if r.confidence == "high")
    medium = sum(1 for r in results if r.confidence == "medium")
    low = sum(1 for r in results if r.confidence == "low")
    print(f"\nSummary: {high} high, {medium} medium, {low} low confidence")

    if low > 0:
        print(f"  {low} file(s) need Claude review (low confidence)")

    # Move if requested
    if args.move:
        moveable = [r for r in results if r.confidence != "low" and r.suggested_prefix]
        if not moveable:
            print("\nNo files to move (all low confidence).")
            return 0

        if not args.yes and not args.dry_run:
            print(f"\nAbout to move {len(moveable)} file(s). Proceed? [y/N] ", end="")
            try:
                answer = input().strip().lower()
            except EOFError:
                answer = "n"
            if answer not in ("y", "yes"):
                print("Aborted.")
                return 0

        print()
        moved = move_files(results, docs_dir, config, args.dry_run)

        if moved and not args.dry_run:
            print("\nRe-indexing...")
            re_index(docs_dir, config, dry_run=False)

        print(f"\n{'Would move' if args.dry_run else 'Moved'}: {len(moved)} file(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
