```python
#!/usr/bin/env python3
"""
Render technical-education infographics via Gemini or Nano Banana.

Supports:
- Free-form text prompt mode
- Structured JSON layout mode (title, regions, labels, optional code)
- Dual-engine toggle: gemini | nanobanana

Usage:
  python3 scripts/generate_infograph.py --engine gemini --mode text --prompt-file brief.txt --output-dir ./output
  python3 scripts/generate_infograph.py --engine gemini --mode structured --layout-file layout.json --output-dir ./output
  python3 scripts/generate_infograph.py --engine nanobanana --mode structured --layout-file layout.json --output-dir ./output
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


def call_gemini(prompt_text: str, model: str, outdir: pathlib.Path, basename: str):
    """Render image via Gemini."""
    if genai is None:
        raise RuntimeError("google-genai not installed. Run: pip install google-genai")

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)])]
    cfg = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        image_config=types.ImageConfig(image_size="1K"),
    )
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


def call_nanobanana(prompt_text: str, outdir: pathlib.Path, basename: str):
    """Simulate Nano Banana prompt structure based on your best practices guide."""
    print("[Nano Banana] Preparing prompt...")
    prompt = f"""SAE-ALD Structure:
- Subject: Educational Infographic
- Action: Design
- Emotion: Clear, balanced, instructive
- Aesthetic: Minimalist, tech-diagram style, modern typography
- Layout: Centered title, modular regions, equal spacing
- Details: Use a consistent color palette, crisp lines, and no heavy shadows.

PROMPT:
{prompt_text}
"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = outdir / f"{basename}_{ts}_nanobanana_prompt.txt"
    out_file.write_text(prompt, encoding="utf-8")
    print(f"[Nano Banana] Prompt saved for rendering: {out_file}")
    print("Note: Send this prompt to Nano Banana for visual generation.")


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
        prompt = build_structured_prompt(layout)
    else:
        prompt = read_text(pathlib.Path(args.prompt_file))

    if args.engine == "gemini":
        call_gemini(prompt, args.model, outdir, args.basename)
    else:
        call_nanobanana(prompt, outdir, args.basename)


if __name__ == "__main__":
    main()