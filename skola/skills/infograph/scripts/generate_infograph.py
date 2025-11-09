#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = ["google-genai>=0.2.0"]
# ///
# -*- coding: utf-8 -*-
"""
Render technical-education infographics via Gemini or Nano Banana.

Supports:
- Free-form text prompt mode
- Structured JSON layout mode (title, regions, labels, optional code)
- Dual-engine toggle: gemini | nanobanana

Usage:
  uv run generate_infograph.py --engine gemini --mode text --prompt-file brief.txt --output-dir ./output
  uv run generate_infograph.py --engine gemini --mode structured --layout-file layout.json --output-dir ./output
  uv run generate_infograph.py --engine nanobanana --mode structured --layout-file layout.json --output-dir ./output
"""

import argparse
import base64
import json
import mimetypes
import os
import pathlib
import sys
from datetime import datetime

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


def validate_environment():
    """Validate required environment variables."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "❌ GEMINI_API_KEY environment variable not set.\n"
            "   Get your API key: https://aistudio.google.com/apikey\n"
            "   Set it with: export GEMINI_API_KEY='your-key-here'"
        )
    return api_key


def ensure_dir(p: pathlib.Path):
    p.mkdir(parents=True, exist_ok=True)


def save_binary_file(path: pathlib.Path, data: bytes):
    with open(path, "wb") as f:
        f.write(data)
    print(f"[saved] {path}")


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def build_structured_prompt(layout: dict) -> str:
    """Turn a JSON wireframe into a concise, renderable prompt."""
    title = layout.get("title", "Untitled Infographic")
    canvas = layout.get("canvas", {"width": 1600, "height": 1000})
    palette = layout.get("palette", "light")

    lines = []
    lines.append(f"Educational infographic titled '{title}' "
                 f"(canvas {canvas.get('width')}x{canvas.get('height')}, palette={palette}).")
    lines.append("Follow the structured layout and visualize the following regions clearly:")
    for r in layout.get("regions", []):
        rid = r.get("id", "r")
        rtype = r.get("type", "panel")
        label = r.get("label", "")
        x, y, w, h = r.get("x", 0), r.get("y", 0), r.get("w", 400), r.get("h", 200)
        if rtype == "code":
            code = r.get("code", "")
            lines.append(f"- Region {rid} [{rtype}] @({x},{y},{w},{h}) label:{label} code:\n{code}")
        elif rtype == "diagram":
            lines.append(f"- Region {rid} [{rtype}] @({x},{y},{w},{h}) label:{label} "
                         f"(use arrows, boxes, and labels to show relationships)")
        else:
            text = r.get("text", "") or " "
            bullets = r.get("bullets", [])
            content = text if text.strip() else ("; ".join(bullets) if bullets else "")
            lines.append(f"- Region {rid} [{rtype}] @({x},{y},{w},{h}) label:{label} content:{content}")
    lines.append("Render this infographic with clarity, hierarchy, and balanced whitespace.")
    return "\n".join(lines)


def build_prompt_nano_banana(layout: dict) -> str:
    """
    Convert structured infographic layout JSON into a natural-language SAE-ALD prompt
    compatible with Nano Banana (Gemini 2.5 Flash Image).

    SAE-ALD = Subject + Action + Environment + Art Style + Lighting + Details
    """
    title = layout.get("title", "Technical Infographic")
    notes = layout.get("notes", "")
    regions = layout.get("regions", [])

    # Collect key region labels or text snippets
    key_panels = [
        (r.get("label") or r.get("text") or r.get("type"))
        for r in regions if (r.get("label") or r.get("text"))
    ]

    # Compose SAE-ALD fields
    subject = f"an educational infographic titled '{title}'"
    action = ("illustrating key concepts such as " + ", ".join(key_panels[:5])) if key_panels else "explaining its main components"
    environment = "a clean, flat vector layout with balanced spacing and neutral background"
    style = "modern minimalist infographic style with soft colors, crisp icons, and readable typography"
    lighting = "even diffuse lighting with subtle shadows for clarity"
    details = "consistent iconography, clear hierarchy, and smooth flow between panels"
    constraints = (
        "no extra text beyond labels; no watermarks or signatures; "
        "avoid clutter; icons appear natural and proportional."
    )

    # Construct SAE-ALD narrative
    prompt = (
        f"A {style} depiction of {subject}, {action}, set in {environment}, "
        f"illuminated by {lighting}. The design emphasizes {details}. {constraints}"
    )

    # Optional contextual notes (≤80 words)
    if notes:
        prompt += f" Context: {notes.strip()}"

    return prompt.strip()


def call_gemini(prompt_text: str, model: str, outdir: pathlib.Path, basename: str):
    """Render image via Gemini."""
    if genai is None:
        raise RuntimeError(
            "❌ google-genai not installed.\n"
            "   Install with: uv pip install google-genai\n"
            "   Or run this script with: uv run generate_infograph.py"
        )

    api_key = validate_environment()
    client = genai.Client(api_key=api_key)
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)])]
    cfg = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        image_config=types.ImageConfig(image_size="1K"),
    )

    try:
        file_index = 0
        for chunk in client.models.generate_content_stream(model=model, contents=contents, config=cfg):
            if not chunk.candidates:
                continue
            part = chunk.candidates[0].content.parts[0]
            if getattr(part, "inline_data", None) and getattr(part.inline_data, "data", None):
                ext = mimetypes.guess_extension(part.inline_data.mime_type) or ".png"
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = outdir / f"{basename}_{file_index}_{ts}{ext}"
                save_binary_file(path, part.inline_data.data)
                file_index += 1
            elif getattr(chunk, "text", None):
                (outdir / f"{basename}.txt").write_text(chunk.text, encoding="utf-8")
    except Exception as e:
        raise RuntimeError(
            f"❌ Image generation failed: {e}\n"
            f"   Check: API key validity, model name, rate limits"
        ) from e


def call_nanobanana(prompt_text: str, outdir: pathlib.Path, basename: str):
    """Save Nano Banana SAE-ALD optimized prompt for manual rendering."""
    print("[Nano Banana] Preparing SAE-ALD optimized prompt...")

    # Save the pre-built SAE-ALD prompt
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = outdir / f"{basename}_{ts}_nanobanana_prompt.txt"
    out_file.write_text(prompt_text, encoding="utf-8")

    print(f"[Nano Banana] Prompt saved for rendering: {out_file}")
    print("Note: Send this prompt to Nano Banana (Gemini 2.5 Flash Image) for visual generation.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["gemini", "nanobanana"], required=True)
    parser.add_argument("--mode", choices=["text", "structured"], required=True)
    parser.add_argument("--prompt-file")
    parser.add_argument("--layout-file")
    parser.add_argument("--model", default="gemini-2.5-flash-image")
    parser.add_argument("--output-dir", default="./output")
    parser.add_argument("--basename", default="infographic")
    args = parser.parse_args()

    outdir = pathlib.Path(args.output_dir)
    ensure_dir(outdir)

    if args.mode == "structured":
        layout = json.loads(read_text(pathlib.Path(args.layout_file)))
        # Use engine-specific prompt builders
        if args.engine == "gemini":
            prompt = build_structured_prompt(layout)
        else:  # nanobanana
            prompt = build_prompt_nano_banana(layout)
    else:
        # Text mode: use raw text for both engines
        prompt = read_text(pathlib.Path(args.prompt_file))

    if args.engine == "gemini":
        call_gemini(prompt, args.model, outdir, args.basename)
    else:
        call_nanobanana(prompt, outdir, args.basename)


if __name__ == "__main__":
    main()
