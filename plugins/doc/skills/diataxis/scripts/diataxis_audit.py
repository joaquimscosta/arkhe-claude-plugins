#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Audit documentation coverage across Diataxis quadrants.

Scans a docs directory, classifies every document, and produces a
coverage report with quadrant distribution, gaps, and quality score.

Usage:
    uv run diataxis_audit.py --dir docs
    uv run diataxis_audit.py --dir docs --json
    uv run diataxis_audit.py --dir docs --min-coverage 2
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    QUADRANTS,
    ClassificationResult,
    format_bar,
    resolve_config,
    scan_markdown_files,
)
from diataxis_classify import classify_file


# ---------------------------------------------------------------------------
# Coverage analysis
# ---------------------------------------------------------------------------

def compute_coverage(
    results: list[ClassificationResult],
) -> dict[str, list[ClassificationResult]]:
    """Group classification results by quadrant."""
    coverage: dict[str, list[ClassificationResult]] = {
        q: [] for q in QUADRANTS
    }
    coverage["unclassified"] = []

    for r in results:
        bucket = r.primary_quadrant if r.primary_quadrant in QUADRANTS else "unclassified"
        coverage[bucket].append(r)

    return coverage


def compute_quality_score(
    results: list[ClassificationResult],
    coverage: dict[str, list[ClassificationResult]],
) -> dict[str, int]:
    """Compute a 0-100 quality score with four components (25 pts each)."""
    total = len(results)
    if total == 0:
        return {"coverage_balance": 0, "quadrant_purity": 0,
                "classification_confidence": 0, "documentation_volume": 0, "total": 0}

    # 1. Coverage balance (25 pts) — how evenly distributed
    quadrant_counts = [len(coverage[q]) for q in QUADRANTS]
    non_zero = sum(1 for c in quadrant_counts if c > 0)

    if non_zero == 0:
        balance_score = 0
    elif non_zero == 4:
        # All quadrants present — score by evenness
        ideal = total / 4
        deviation = sum(abs(c - ideal) for c in quadrant_counts) / total
        balance_score = max(0, round(25 * (1 - deviation)))
    else:
        # Partial coverage — proportional
        balance_score = round(25 * non_zero / 4)

    # 2. Quadrant purity (25 pts) — penalize collapsed docs
    collapsed = sum(1 for r in results if r.is_collapsed)
    if total > 0:
        purity_ratio = 1 - (collapsed / total)
        purity_score = round(25 * purity_ratio)
    else:
        purity_score = 25

    # 3. Classification confidence (25 pts) — average confidence
    confidence_values = {"high": 1.0, "medium": 0.6, "low": 0.2}
    if total > 0:
        avg_conf = sum(confidence_values.get(r.confidence, 0) for r in results) / total
        confidence_score = round(25 * avg_conf)
    else:
        confidence_score = 0

    # 4. Documentation volume (25 pts) — scale by total count
    # 1 doc = 5 pts, up to 5+ per quadrant = 25 pts
    volume_score = min(25, total * 5 // max(non_zero, 1))

    total_score = balance_score + purity_score + confidence_score + volume_score

    return {
        "coverage_balance": balance_score,
        "quadrant_purity": purity_score,
        "classification_confidence": confidence_score,
        "documentation_volume": volume_score,
        "total": total_score,
    }


def find_gaps(
    coverage: dict[str, list[ClassificationResult]],
    total: int,
) -> list[dict[str, str]]:
    """Identify underrepresented quadrants."""
    gaps: list[dict[str, str]] = []

    suggestions: dict[str, str] = {
        "tutorial": "getting started guides, step-by-step lessons, or walkthrough documents",
        "how-to": "task-oriented guides like 'How to deploy' or 'How to configure X'",
        "reference": "API reference, configuration options, CLI commands, or parameter tables",
        "explanation": "architecture overviews, design rationale, or 'Why we chose X' docs",
    }

    for quadrant in QUADRANTS:
        count = len(coverage[quadrant])
        if count == 0:
            gaps.append({
                "quadrant": quadrant,
                "severity": "missing",
                "message": f"No {quadrant} documents found",
                "suggestion": f"Consider writing: {suggestions[quadrant]}",
            })
        elif total > 0 and count / total < 0.10:
            pct = round(count / total * 100)
            gaps.append({
                "quadrant": quadrant,
                "severity": "underrepresented",
                "message": f"{quadrant.capitalize()} is underrepresented ({count} docs, {pct}%)",
                "suggestion": f"Consider adding: {suggestions[quadrant]}",
            })

    return gaps


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_report(
    results: list[ClassificationResult],
    coverage: dict[str, list[ClassificationResult]],
    quality: dict[str, int],
    gaps: list[dict[str, str]],
    collapsed_results: list[ClassificationResult],
    docs_dir: Path,
) -> str:
    """Format a human-readable audit report."""
    total = len(results)
    lines = [
        "Diataxis Documentation Audit",
        "=" * 40,
        f"Directory: {docs_dir}",
        f"Total documents: {total}",
        "",
        "Quadrant Coverage",
        "-" * 20,
    ]

    for quadrant, meta in QUADRANTS.items():
        docs = coverage[quadrant]
        count = len(docs)
        pct = round(count / total * 100) if total > 0 else 0
        bar = format_bar(count, total)
        file_names = ", ".join(r.file_path.name for r in docs[:3])
        if len(docs) > 3:
            file_names += f", ... (+{len(docs) - 3} more)"
        label = f"{quadrant.capitalize():<12}"
        lines.append(f"  {label}: {bar} {count} docs ({pct}%)  [{file_names}]")

    # Unclassified
    unclassified = coverage.get("unclassified", [])
    if unclassified:
        count = len(unclassified)
        pct = round(count / total * 100) if total > 0 else 0
        bar = format_bar(count, total)
        file_names = ", ".join(r.file_path.name for r in unclassified[:3])
        if len(unclassified) > 3:
            file_names += f", ... (+{len(unclassified) - 3} more)"
        lines.append(f"  {'Unclassified':<12}: {bar} {count} docs ({pct}%)  [{file_names}]")

    lines.append("")

    # Gaps
    if gaps:
        lines.append("Coverage Gaps")
        lines.append("-" * 20)
        for gap in gaps:
            marker = "!" if gap["severity"] == "missing" else "-"
            lines.append(f"  {marker} {gap['message']}")
            lines.append(f"    {gap['suggestion']}")
        lines.append("")

    # Collapsed documents
    if collapsed_results:
        lines.append("Collapsed Documents (mixed quadrants)")
        lines.append("-" * 20)
        for r in collapsed_results:
            mixed = " + ".join(q.capitalize() for q in r.collapsed_quadrants)
            lines.append(f"  ! {r.file_path.name} — mixes {mixed}")
            # Generate split suggestion
            quads = r.collapsed_quadrants
            if len(quads) == 2:
                stem = r.file_path.stem
                lines.append(
                    f"    Suggestion: Split into {stem}-{quads[0]}.md "
                    f"({quads[0]}) and {stem}-{quads[1]}.md ({quads[1]})"
                )
        lines.append("")

    # Quality score
    lines.append("Quality Score: {}/100".format(quality["total"]))
    lines.append(f"  Coverage balance:          {quality['coverage_balance']}/25")
    lines.append(f"  Quadrant purity:           {quality['quadrant_purity']}/25")
    lines.append(f"  Classification confidence: {quality['classification_confidence']}/25")
    lines.append(f"  Documentation volume:      {quality['documentation_volume']}/25")
    lines.append("")

    # Result
    result = "PASS" if quality["total"] >= 50 else "NEEDS IMPROVEMENT"
    collapsed_count = len(collapsed_results)
    unclassified_count = len(unclassified)
    lines.append(
        f"Result: {result} ({total} docs, {collapsed_count} collapsed, "
        f"{unclassified_count} unclassified)"
    )

    return "\n".join(lines)


def format_audit_json(
    results: list[ClassificationResult],
    coverage: dict[str, list[ClassificationResult]],
    quality: dict[str, int],
    gaps: list[dict[str, str]],
    docs_dir: Path,
) -> str:
    """Format audit results as JSON."""
    data = {
        "directory": str(docs_dir),
        "total_documents": len(results),
        "coverage": {
            quadrant: {
                "count": len(docs),
                "percentage": round(len(docs) / len(results) * 100) if results else 0,
                "files": [str(r.file_path) for r in docs],
            }
            for quadrant, docs in coverage.items()
        },
        "gaps": gaps,
        "collapsed": [
            {
                "file": str(r.file_path),
                "quadrants": r.collapsed_quadrants,
            }
            for r in results if r.is_collapsed
        ],
        "quality_score": quality,
        "classifications": [
            {
                "file": str(r.file_path),
                "quadrant": r.primary_quadrant,
                "confidence": r.confidence,
                "score": round(r.score, 2),
                "is_collapsed": r.is_collapsed,
            }
            for r in results
        ],
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit documentation coverage across Diataxis quadrants"
    )
    parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Docs directory to audit",
    )
    parser.add_argument(
        "--min-coverage",
        type=int,
        default=1,
        help="Minimum docs per quadrant to pass (default: 1)",
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

    # Resolve directory
    docs_dir = Path(args.dir)
    if not docs_dir.is_absolute():
        docs_dir = base_path / docs_dir

    if not docs_dir.exists():
        print(f"Error: Directory does not exist: {docs_dir}")
        return 1

    # Scan and classify
    ignore = config.get("ignore", [])
    files = scan_markdown_files(docs_dir, ignore)

    if not files:
        print(f"No markdown files found in {docs_dir}")
        return 0

    results = [classify_file(f, config) for f in files]

    # Analyze
    coverage = compute_coverage(results)
    quality = compute_quality_score(results, coverage)
    gaps = find_gaps(coverage, len(results))
    collapsed_results = [r for r in results if r.is_collapsed]

    # Output
    if args.json_output:
        print(format_audit_json(results, coverage, quality, gaps, docs_dir))
    else:
        print(format_report(results, coverage, quality, gaps, collapsed_results, docs_dir))

    # Check minimum coverage
    failed = False
    for quadrant in QUADRANTS:
        if len(coverage[quadrant]) < args.min_coverage:
            failed = True
            if not args.json_output:
                print(f"\nNote: {quadrant} has fewer than {args.min_coverage} doc(s)")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
