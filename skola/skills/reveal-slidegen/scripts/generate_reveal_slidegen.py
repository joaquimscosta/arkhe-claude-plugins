#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
# -*- coding: utf-8 -*-
"""
generate_reveal_slidegen.py
--------------------------------------
Skill runner for the `reveal-slidegen` Claude Code skill.

This script:
  - Accepts a tutorial outline or structured markdown input (file path or stdin)
  - Sends the content to the reveal-slidegen skill
  - Receives a fully-rendered Reveal.js standalone HTML deck
  - Writes the output to a target `.html` file (or stdout)

Usage:
  uv run generate_reveal_slidegen.py --input tutorial.md --output deck.html
  cat tutorial.md | uv run generate_reveal_slidegen.py > deck.html
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_skill(input_text: str, engine: str = "claude-code") -> str:
    """Execute the reveal-slidegen skill via the Skill tool."""
    payload = {
        "command": "reveal-slidegen",
        "arguments": input_text,
        "engine": engine,
    }

    process = subprocess.Popen(
        ["skill", "run"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    out, err = process.communicate(json.dumps(payload))

    if err:
        print(f"[Skill Error] {err}", file=sys.stderr)

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Reveal.js slides from tutorial markdown.")
    parser.add_argument("--input", "-i", type=str, help="Path to input markdown file. Reads stdin if omitted.")
    parser.add_argument("--output", "-o", type=str, help="Output HTML file. Prints to stdout if omitted.")
    parser.add_argument(
        "--engine",
        "-e",
        type=str,
        default="claude-code",
        help="Engine to use (claude-code, nano-banana, etc.)",
    )
    args = parser.parse_args()

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"[Error] Input file not found: {input_path}", file=sys.stderr)
            sys.exit(1)
        input_text = input_path.read_text(encoding="utf-8")
    else:
        input_text = sys.stdin.read()

    html_output = run_skill(input_text, engine=args.engine)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(html_output, encoding="utf-8")
        print(f"[OK] Slide deck generated → {output_path}")
    else:
        print(html_output)


if __name__ == "__main__":
    main()
