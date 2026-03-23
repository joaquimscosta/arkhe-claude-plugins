#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Classify markdown files into Diataxis quadrants using multi-signal heuristics.

Usage:
    uv run diataxis_classify.py docs/getting-started.md
    uv run diataxis_classify.py docs/*.md
    uv run diataxis_classify.py docs/*.md --verbose
    uv run diataxis_classify.py docs/*.md --json
    uv run diataxis_classify.py docs/*.md --no-content
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import (
    QUADRANT_SIGNALS,
    QUADRANTS,
    ClassificationResult,
    format_confidence,
    read_document,
    resolve_config,
)


# ---------------------------------------------------------------------------
# Classification engine
# ---------------------------------------------------------------------------

def _match_title_keywords(
    stem: str,
    segments: set[str],
    keywords: list[str],
) -> tuple[float, list[str]]:
    """Match filename/title against keyword list. Max score 0.30."""
    matched: list[str] = []
    for kw in keywords:
        if kw in stem or kw in segments:
            matched.append(kw)
    if not matched:
        return 0.0, []
    score = min(0.15 + 0.05 * (len(matched) - 1), 0.30)
    return score, matched


def _match_heading_patterns(
    headings: list[str],
    patterns: list[str],
) -> tuple[float, list[str]]:
    """Match document headings against regex patterns. Max score 0.25."""
    matched: list[str] = []
    for heading in headings:
        for pattern in patterns:
            if re.search(pattern, heading, re.IGNORECASE):
                tag = f"heading:{heading[:40]}"
                if tag not in matched:
                    matched.append(tag)
    if not matched:
        return 0.0, []
    score = min(0.10 + 0.05 * (len(matched) - 1), 0.25)
    return score, matched


def _match_content_keywords(
    body: str,
    keywords: list[str],
) -> tuple[float, list[str]]:
    """Match body text against content keyword phrases. Max score 0.25."""
    matched: list[str] = []
    for kw in keywords:
        if kw in body:
            matched.append(kw)
    if not matched:
        return 0.0, []
    score = min(0.05 * len(matched), 0.25)
    return score, matched


def _analyze_structure(filepath: Path, max_lines: int = 200) -> dict[str, int]:
    """Analyze structural features of a document."""
    features: dict[str, int] = {
        "numbered_steps": 0,
        "tables": 0,
        "code_blocks": 0,
        "long_paragraphs": 0,
        "parameter_tables": 0,
        "command_blocks": 0,
    }

    try:
        with open(filepath) as f:
            in_code_block = False
            paragraph_words = 0
            code_block_content: list[str] = []
            table_header_seen = False

            for i, line in enumerate(f):
                if i >= max_lines:
                    break

                stripped = line.strip()

                # Track code blocks
                if stripped.startswith("```"):
                    if in_code_block:
                        # Closing code block — check if it contains commands
                        block_text = " ".join(code_block_content).lower()
                        if any(cmd in block_text for cmd in [
                            "run ", "install ", "npm ", "pip ", "docker ",
                            "curl ", "wget ", "git ", "cd ", "mkdir ",
                            "uv run", "python ", "node ",
                        ]):
                            features["command_blocks"] += 1
                        code_block_content = []
                    in_code_block = not in_code_block
                    features["code_blocks"] += 1
                    continue

                if in_code_block:
                    code_block_content.append(stripped)
                    continue

                # Numbered steps
                if re.match(r"^\d+\.\s+", stripped) or re.match(r"^step\s+\d+", stripped, re.IGNORECASE):
                    features["numbered_steps"] += 1

                # Tables
                if "|" in stripped and stripped.startswith("|"):
                    if not table_header_seen:
                        table_header_seen = True
                        # Check if it looks like a parameter table
                        lower_line = stripped.lower()
                        if any(col in lower_line for col in [
                            "type", "default", "required", "description",
                            "parameter", "option", "flag",
                        ]):
                            features["parameter_tables"] += 1
                    features["tables"] += 1
                else:
                    table_header_seen = False

                # Long paragraphs (non-heading, non-list, non-empty text)
                if stripped and not stripped.startswith(("#", "-", "*", ">", "|", "!")):
                    paragraph_words += len(stripped.split())
                else:
                    if paragraph_words > 80:
                        features["long_paragraphs"] += 1
                    paragraph_words = 0

            # Final paragraph check
            if paragraph_words > 80:
                features["long_paragraphs"] += 1

    except (OSError, UnicodeDecodeError):
        pass

    return features


def _score_structural_signals(
    features: dict[str, int],
    quadrant: str,
) -> tuple[float, list[str]]:
    """Score structural features for a specific quadrant. Max score 0.20."""
    matched: list[str] = []

    if quadrant == "tutorial":
        if features["numbered_steps"] >= 3:
            matched.append(f"numbered_steps({features['numbered_steps']})")
        if features["code_blocks"] >= 2 and features["long_paragraphs"] <= 2:
            matched.append("incremental_code")

    elif quadrant == "how-to":
        if features["command_blocks"] >= 1:
            matched.append(f"command_blocks({features['command_blocks']})")
        if features["numbered_steps"] >= 1 and features["long_paragraphs"] == 0:
            matched.append("short_steps")

    elif quadrant == "reference":
        if features["tables"] >= 3:
            matched.append(f"tables({features['tables']})")
        if features["parameter_tables"] >= 1:
            matched.append(f"parameter_tables({features['parameter_tables']})")
        if features["code_blocks"] >= 1 and features["long_paragraphs"] == 0:
            matched.append("code_signatures")

    elif quadrant == "explanation":
        if features["long_paragraphs"] >= 2:
            matched.append(f"long_paragraphs({features['long_paragraphs']})")
        if features["code_blocks"] <= 1 and features["long_paragraphs"] >= 1:
            matched.append("narrative_flow")

    if not matched:
        return 0.0, []
    score = min(0.10 + 0.05 * (len(matched) - 1), 0.20)
    return score, matched


def classify_file(
    filepath: Path,
    config: dict,
    scan_content: bool = True,
) -> ClassificationResult:
    """Classify a file by combining four signal sources."""
    result = ClassificationResult(file_path=filepath)

    # Prepare filename for matching
    stem = filepath.stem.lower()
    normalized_stem = re.sub(r"[_ ]+", "-", stem)
    segments = set(normalized_stem.split("-"))

    # Read document content
    if scan_content and filepath.suffix.lower() == ".md" and filepath.is_file():
        title, body, headings = read_document(filepath)
    else:
        title, body, headings = "", "", []

    # Include title in matching
    if title:
        title_stem = re.sub(r"[_ ]+", "-", title)
        title_segments = set(title_stem.split("-"))
        combined_stem = f"{normalized_stem} {title_stem}"
        combined_segments = segments | title_segments
    else:
        combined_stem = normalized_stem
        combined_segments = segments

    # Analyze structure once (reused for all quadrants)
    features = _analyze_structure(filepath) if scan_content else {}

    # Score each quadrant
    quadrant_scores: dict[str, float] = {}
    quadrant_signals: dict[str, list[str]] = {}

    for quadrant, signals in QUADRANT_SIGNALS.items():
        all_signals: list[str] = []
        total_score = 0.0
        signal_types_matched = 0

        # Signal 1: Title/filename keywords (max 0.30)
        s1_score, s1_matches = _match_title_keywords(
            combined_stem, combined_segments, signals["title_keywords"],
        )
        if s1_matches:
            all_signals.extend(f"title:{m}" for m in s1_matches)
            signal_types_matched += 1
        total_score += s1_score

        # Signal 2: Heading patterns (max 0.25)
        if headings:
            s2_score, s2_matches = _match_heading_patterns(
                headings, signals["heading_patterns"],
            )
            if s2_matches:
                all_signals.extend(s2_matches)
                signal_types_matched += 1
            total_score += s2_score

        # Signal 3: Content keywords (max 0.25)
        if body:
            s3_score, s3_matches = _match_content_keywords(
                body, signals["content_keywords"],
            )
            if s3_matches:
                all_signals.extend(f"content:{m}" for m in s3_matches)
                signal_types_matched += 1
            total_score += s3_score

        # Signal 4: Structural analysis (max 0.20)
        if features:
            s4_score, s4_matches = _score_structural_signals(features, quadrant)
            if s4_matches:
                all_signals.extend(f"structural:{m}" for m in s4_matches)
                signal_types_matched += 1
            total_score += s4_score

        # Agreement bonus when 3+ signal types converge
        if signal_types_matched >= 3:
            total_score = min(total_score + 0.10, 1.0)

        quadrant_scores[quadrant] = round(total_score, 3)
        quadrant_signals[quadrant] = all_signals

    result.scores = quadrant_scores

    # Pick the best quadrant
    if not any(s > 0 for s in quadrant_scores.values()):
        result.reason = "No keyword matches"
        return result

    best = max(quadrant_scores, key=lambda k: quadrant_scores[k])
    result.primary_quadrant = best
    result.score = quadrant_scores[best]
    result.confidence = format_confidence(result.score)
    result.signals = {q: sigs for q, sigs in quadrant_signals.items() if sigs}

    # Collapsed document detection
    above_threshold = [q for q, s in quadrant_scores.items() if s >= 0.3]
    if len(above_threshold) >= 2:
        sorted_scores = sorted(quadrant_scores.values(), reverse=True)
        ratio = sorted_scores[0] / sorted_scores[1] if sorted_scores[1] > 0 else float("inf")
        if ratio < 2.0:
            result.is_collapsed = True
            result.collapsed_quadrants = sorted(above_threshold)

    # Build reason string
    reasons: list[str] = []
    best_signals = quadrant_signals.get(best, [])
    title_sigs = [s.split(":", 1)[1] for s in best_signals if s.startswith("title:")]
    structural_sigs = [s.split(":", 1)[1] for s in best_signals if s.startswith("structural:")]
    content_sigs = [s.split(":", 1)[1] for s in best_signals if s.startswith("content:")]
    heading_sigs = [s.split(":", 1)[1] for s in best_signals if s.startswith("heading:")]

    if title_sigs:
        reasons.append(f"Title: {', '.join(repr(k) for k in title_sigs[:3])}")
    if heading_sigs:
        reasons.append(f"Headings: {', '.join(h[:25] for h in heading_sigs[:2])}")
    if structural_sigs:
        reasons.append(f"Structure: {', '.join(structural_sigs[:2])}")
    if content_sigs:
        reasons.append(f"Content: {', '.join(repr(k) for k in content_sigs[:2])}")

    result.reason = "; ".join(reasons) if reasons else "Weak keyword match"

    return result


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_table(results: list[ClassificationResult], verbose: bool = False) -> str:
    """Format classification results as a human-readable table."""
    if not results:
        return "No files to classify."

    file_w = max(len("File"), max(len(r.file_path.name) for r in results))
    quad_w = max(len("Quadrant"), max(len(r.primary_quadrant or "(unknown)") for r in results))
    conf_w = len("Confidence")

    # Compute collapsed column width accounting for actual content
    def _collapsed_str(r: ClassificationResult) -> str:
        if r.is_collapsed:
            return f"Yes ({'+'.join(q[0].upper() for q in r.collapsed_quadrants)})"
        return "No"
    coll_w = max(len("Collapsed"), max(len(_collapsed_str(r)) for r in results))

    header = (
        f"{'File':<{file_w}} | {'Quadrant':<{quad_w}} | "
        f"{'Confidence':<{conf_w}} | {'Collapsed':<{coll_w}} | Reason"
    )
    sep = (
        f"{'-' * file_w}-+-{'-' * quad_w}-+-"
        f"{'-' * conf_w}-+-{'-' * coll_w}-+{'-' * 30}"
    )

    lines = [header, sep]
    for r in results:
        quadrant = r.primary_quadrant or "(unknown)"
        collapsed = "Yes" if r.is_collapsed else "No"
        if r.is_collapsed:
            collapsed = f"Yes ({'+'.join(q[0].upper() for q in r.collapsed_quadrants)})"
        lines.append(
            f"{r.file_path.name:<{file_w}} | {quadrant:<{quad_w}} | "
            f"{r.confidence:<{conf_w}} | {collapsed:<{coll_w}} | {r.reason}"
        )

        if verbose and r.scores:
            scores_str = ", ".join(f"{q}: {s:.2f}" for q, s in sorted(r.scores.items()))
            lines.append(f"{'':>{file_w}}   Scores: {scores_str}")

    return "\n".join(lines)


def format_json(results: list[ClassificationResult]) -> str:
    """Format classification results as JSON."""
    data = []
    for r in results:
        data.append({
            "file": str(r.file_path),
            "primary_quadrant": r.primary_quadrant,
            "confidence": r.confidence,
            "score": round(r.score, 2),
            "scores": {q: round(s, 2) for q, s in r.scores.items()},
            "is_collapsed": r.is_collapsed,
            "collapsed_quadrants": r.collapsed_quadrants,
            "signals": r.signals,
            "reason": r.reason,
        })
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify markdown files into Diataxis quadrants"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="File paths to classify",
    )
    parser.add_argument(
        "--no-content",
        action="store_true",
        help="Filename-only classification (skip content scanning)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all quadrant scores per file",
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
        print(format_table(results, verbose=args.verbose))

        # Summary (human-readable only)
        by_quadrant: dict[str, int] = {}
        collapsed = 0
        for r in results:
            q = r.primary_quadrant or "(unknown)"
            by_quadrant[q] = by_quadrant.get(q, 0) + 1
            if r.is_collapsed:
                collapsed += 1

        print(f"\nSummary: {len(results)} files classified")
        for q in ["tutorial", "how-to", "reference", "explanation"]:
            count = by_quadrant.get(q, 0)
            if count:
                print(f"  {q}: {count}")
        unknown = by_quadrant.get("(unknown)", 0)
        if unknown:
            print(f"  unclassified: {unknown}")
        if collapsed:
            print(f"  collapsed: {collapsed} (mixed quadrants)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
