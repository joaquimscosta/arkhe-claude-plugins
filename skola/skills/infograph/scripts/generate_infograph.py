#!/usr/bin/env python3
import argparse, base64, json, mimetypes, os, pathlib, sys
from datetime import datetime
from google import genai
from google.genai import types

def ensure_dir(p): pathlib.Path(p).mkdir(parents=True, exist_ok=True)
def save_binary_file(path, data): open(path, "wb").write(data); print(f"[saved] {path}")
def read_text(p): return pathlib.Path(p).read_text()

def build_structured_prompt(layout):
    title = layout.get("title","Infographic")
    lines = [f"Educational infographic titled '{title}'"]
    for r in layout.get("regions", []):
        lines.append(f"- {r.get('id')}: {r.get('label','')} ({r.get('type')})")
    return "\n".join(lines)

def call_gemini(prompt, model, outdir, name):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    cfg=types.GenerateContentConfig(response_modalities=["IMAGE"], image_config=types.ImageConfig(image_size="1K"))
    for chunk in client.models.generate_content_stream(model=model, contents=contents, config=cfg):
        if not chunk.candidates: continue
        part=chunk.candidates[0].content.parts[0]
        if part.inline_data:
            ext=mimetypes.guess_extension(part.inline_data.mime_type) or ".png"
            path=pathlib.Path(outdir)/f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            save_binary_file(path, part.inline_data.data)

def main():
    a=argparse.ArgumentParser();a.add_argument("--mode",choices=["text","structured"],required=True)
    a.add_argument("--prompt-file");a.add_argument("--layout-file");a.add_argument("--output-dir",default="./output")
    a.add_argument("--model",default="gemini-2.5-flash-image");a.add_argument("--basename",default="infographic")
    args=a.parse_args();ensure_dir(args.output_dir)
    if args.mode=="structured":
        layout=json.loads(read_text(args.layout_file));prompt=build_structured_prompt(layout)
    else: prompt=read_text(args.prompt_file)
    call_gemini(prompt,args.model,args.output_dir,args.basename)

if __name__=="__main__": main()
