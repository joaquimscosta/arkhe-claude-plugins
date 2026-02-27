#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["Pillow>=10.0.0"]
# ///
"""
Generate platform icon assets from a master SVG.

Produces favicon.ico, apple-touch-icon.png, PWA manifest icons,
maskable icons, iOS source icon, manifest.webmanifest, and integration guide.
Supports framework-specific file naming (e.g., --framework nextjs).

Requires one of these system tools for SVG-to-PNG conversion:
  - rsvg-convert (brew install librsvg)
  - magick / convert (brew install imagemagick)

Usage:
    uv run generate_assets.py --svg icon.svg [options]

Examples:
    uv run generate_assets.py --svg logo.svg --name "My App" --output-dir ./icons
    uv run generate_assets.py --svg logo.svg --dark-svg logo-dark.svg --bg-color "#1a1a2e"
    uv run generate_assets.py --svg logo.svg --framework nextjs --output-dir ./brand-assets
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image


# ---------------------------------------------------------------------------
# Framework-specific file naming
# ---------------------------------------------------------------------------

FRAMEWORK_FILE_MAP: dict[str, dict[str, str]] = {
    "nextjs": {
        "favicon.svg": "icon.svg",
        "apple-touch-icon.png": "apple-icon.png",
    },
}


def resolve_name(canonical: str, framework: str | None) -> str:
    """Return framework-specific filename, or canonical name if no framework set."""
    if framework is None:
        return canonical
    return FRAMEWORK_FILE_MAP.get(framework, {}).get(canonical, canonical)


# ---------------------------------------------------------------------------
# SVG validation
# ---------------------------------------------------------------------------

def validate_svg(svg_path: Path) -> str:
    """Read and validate that the file is a plausible SVG."""
    if not svg_path.exists():
        print(f"Error: SVG file not found: {svg_path}", file=sys.stderr)
        sys.exit(1)
    content = svg_path.read_text(encoding="utf-8")
    if "<svg" not in content:
        print(f"Error: {svg_path} does not appear to be a valid SVG file.", file=sys.stderr)
        sys.exit(2)
    return content


# ---------------------------------------------------------------------------
# SVG to PNG conversion via system tools
# ---------------------------------------------------------------------------

def find_svg_converter() -> str:
    """Detect available SVG-to-PNG converter. Returns tool name or exits."""
    for tool in ("rsvg-convert", "magick", "convert"):
        if shutil.which(tool):
            return tool
    print(
        "Error: No SVG-to-PNG converter found.\n"
        "Install one of:\n"
        "  brew install librsvg    (recommended — provides rsvg-convert)\n"
        "  brew install imagemagick (provides magick/convert)\n",
        file=sys.stderr,
    )
    sys.exit(1)


def svg_to_png_file(svg_path: Path, png_path: Path, size: int, tool: str) -> None:
    """Convert SVG to PNG at *size x size* using a system tool."""
    if tool == "rsvg-convert":
        cmd = [
            "rsvg-convert",
            "-w", str(size), "-h", str(size),
            "--keep-aspect-ratio",
            "-o", str(png_path),
            str(svg_path),
        ]
    elif tool in ("magick", "convert"):
        cmd = [
            tool,
            "-background", "none",
            "-density", "300",
            "-resize", f"{size}x{size}",
            str(svg_path),
            f"PNG32:{png_path}",
        ]
    else:
        raise ValueError(f"Unknown converter: {tool}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"{tool} failed (exit {result.returncode}): {result.stderr.strip()}"
        )


def svg_to_image(svg_path: Path, size: int, tool: str) -> Image.Image:
    """Render SVG to a Pillow RGBA Image at *size x size*."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        svg_to_png_file(svg_path, tmp_path, size, tool)
        return Image.open(tmp_path).convert("RGBA")
    finally:
        tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Asset builders
# ---------------------------------------------------------------------------

def create_icon_with_bg(
    svg_path: Path, size: int, bg_color: str, tool: str
) -> Image.Image:
    """Render icon on a solid background (no transparency)."""
    fg = svg_to_image(svg_path, size, tool)
    bg = Image.new("RGBA", (size, size), bg_color)
    bg.paste(fg, (0, 0), fg)
    return bg.convert("RGB")


def create_maskable_icon(
    svg_path: Path, size: int, bg_color: str, tool: str
) -> Image.Image:
    """Render icon centered in the safe zone (central 80%) on a solid background."""
    safe_size = int(size * 0.80)
    fg = svg_to_image(svg_path, safe_size, tool)
    bg = Image.new("RGBA", (size, size), bg_color)
    offset = (size - safe_size) // 2
    bg.paste(fg, (offset, offset), fg)
    return bg.convert("RGB")


def create_favicon_ico(svg_path: Path, out_path: Path, tool: str) -> None:
    """Build a multi-resolution ICO containing 16x16 and 32x32 frames."""
    img_32 = svg_to_image(svg_path, 32, tool)
    img_16 = svg_to_image(svg_path, 16, tool)
    img_32.save(str(out_path), format="ICO", append_images=[img_16])


def create_manifest(
    name: str, short_name: str, theme_color: str, bg_color: str
) -> str:
    """Generate manifest.webmanifest JSON content."""
    manifest = {
        "name": name,
        "short_name": short_name,
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {
                "src": "/icon-maskable-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable",
            },
            {
                "src": "/icon-maskable-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable",
            },
        ],
        "theme_color": theme_color,
        "background_color": bg_color,
        "display": "standalone",
    }
    return json.dumps(manifest, indent=2) + "\n"


def create_html_snippet() -> str:
    """Generate the HTML <link> tags for the document <head>."""
    return (
        "<!-- Favicon Package -- paste into <head> -->\n"
        '<link rel="icon" href="/favicon.ico" sizes="32x32">\n'
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
        '<link rel="manifest" href="/manifest.webmanifest">\n'
    )


def create_nextjs_guide() -> str:
    """Generate a Next.js App Router placement guide."""
    return (
        "# Next.js App Router — Icon Placement Guide\n"
        "#\n"
        "# Copy to app/ directory (auto-detected by Next.js):\n"
        "#   favicon.ico           → app/favicon.ico\n"
        "#   icon.svg              → app/icon.svg\n"
        "#   apple-icon.png        → app/apple-icon.png\n"
        "#   manifest.webmanifest  → app/manifest.webmanifest\n"
        "#\n"
        "# Copy to public/ directory (referenced by manifest):\n"
        "#   icon-192.png          → public/icon-192.png\n"
        "#   icon-512.png          → public/icon-512.png\n"
        "#   icon-maskable-192.png → public/icon-maskable-192.png\n"
        "#   icon-maskable-512.png → public/icon-maskable-512.png\n"
        "#\n"
        "# Next.js auto-generates <link> tags from file-based metadata.\n"
        "# No manual <link> tags needed in layout.tsx.\n"
        "#\n"
        "# Reference: https://nextjs.org/docs/app/api-reference/"
        "file-conventions/metadata/app-icons\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate platform icon assets from a master SVG.",
    )
    parser.add_argument(
        "--svg", required=True, type=Path, help="Path to master SVG icon file"
    )
    parser.add_argument(
        "--dark-svg", type=Path, default=None,
        help="Path to dark-mode SVG for favicon.svg (defaults to --svg)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("./brand-assets"),
        help="Output directory (default: ./brand-assets)",
    )
    parser.add_argument(
        "--bg-color", default="#ffffff",
        help="Background color for apple-touch-icon and maskable icons (default: #ffffff)",
    )
    parser.add_argument(
        "--name", default="App",
        help="App name for manifest.webmanifest (default: App)",
    )
    parser.add_argument(
        "--short-name", default=None,
        help="Short name for manifest (defaults to --name)",
    )
    parser.add_argument(
        "--theme-color", default=None,
        help="Theme color for manifest (defaults to --bg-color)",
    )
    parser.add_argument(
        "--framework", choices=["nextjs"], default=None,
        help="Target framework for file naming (auto-detected by skill)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    short_name = args.short_name or args.name
    theme_color = args.theme_color or args.bg_color
    framework = args.framework

    # Validate inputs
    validate_svg(args.svg)
    dark_svg_path = args.dark_svg or args.svg
    if args.dark_svg:
        validate_svg(args.dark_svg)

    # Find converter
    tool = find_svg_converter()

    # Create output directory
    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"Error: Cannot create output directory: {exc}", file=sys.stderr)
        return 3

    print("Brand Icon Asset Generation")
    print("=" * 40)
    print(f"Input SVG:        {args.svg}")
    if args.dark_svg:
        print(f"Dark-mode SVG:    {args.dark_svg}")
    print(f"Background color: {args.bg_color}")
    print(f"Converter:        {tool}")
    if framework:
        print(f"Framework:        {framework}")
    print(f"Output directory:  {args.output_dir}/")
    print()
    print("Generating assets...")

    generated = []

    try:
        # 1. favicon.ico (16x16 + 32x32 via Pillow ICO save)
        out = args.output_dir / "favicon.ico"
        create_favicon_ico(args.svg, out, tool)
        generated.append(("favicon.ico", "16x16 + 32x32", out))

        # 2. favicon.svg / icon.svg (dark-mode-aware copy)
        svg_name = resolve_name("favicon.svg", framework)
        out = args.output_dir / svg_name
        shutil.copy2(dark_svg_path, out)
        generated.append((svg_name, "vector", out))

        # 3. apple-touch-icon.png / apple-icon.png (180x180, solid bg)
        apple_name = resolve_name("apple-touch-icon.png", framework)
        img = create_icon_with_bg(args.svg, 180, args.bg_color, tool)
        out = args.output_dir / apple_name
        img.save(str(out), "PNG")
        generated.append((apple_name, "180x180", out))

        # 4-5. Standard PNG icons (transparent background)
        for size in (192, 512):
            out = args.output_dir / f"icon-{size}.png"
            svg_to_png_file(args.svg, out, size, tool)
            generated.append((f"icon-{size}.png", f"{size}x{size}", out))

        # 6-7. Maskable icons (80% safe zone, solid bg)
        for size in (192, 512):
            img = create_maskable_icon(args.svg, size, args.bg_color, tool)
            out = args.output_dir / f"icon-maskable-{size}.png"
            img.save(str(out), "PNG")
            generated.append(
                (f"icon-maskable-{size}.png", f"{size}x{size} safe zone", out)
            )

        # 8. iOS App Store source (1024x1024, solid bg)
        img = create_icon_with_bg(args.svg, 1024, args.bg_color, tool)
        out = args.output_dir / "icon-1024.png"
        img.save(str(out), "PNG")
        generated.append(("icon-1024.png", "1024x1024", out))

        # 9. Master SVG copy
        out = args.output_dir / "master-icon.svg"
        shutil.copy2(args.svg, out)
        generated.append(("master-icon.svg", "vector", out))

        # 10. manifest.webmanifest
        manifest = create_manifest(args.name, short_name, theme_color, args.bg_color)
        out = args.output_dir / "manifest.webmanifest"
        out.write_text(manifest, encoding="utf-8")
        generated.append(("manifest.webmanifest", "JSON", out))

        # 11. Integration guide (framework-specific or generic HTML snippet)
        if framework == "nextjs":
            guide = create_nextjs_guide()
            out = args.output_dir / "_nextjs-guide.txt"
            out.write_text(guide, encoding="utf-8")
            generated.append(("_nextjs-guide.txt", "placement guide", out))
        else:
            snippet = create_html_snippet()
            out = args.output_dir / "_html-snippet.html"
            out.write_text(snippet, encoding="utf-8")
            generated.append(("_html-snippet.html", "HTML", out))

    except Exception as exc:
        print(f"\nError during asset generation: {exc}", file=sys.stderr)
        return 2

    # Report
    for name, desc, path in generated:
        size_kb = path.stat().st_size / 1024
        print(f"  [OK] {name:<30s} ({desc}) -- {size_kb:.1f} KB")

    print(f"\nDone! {len(generated)} files generated in {args.output_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
