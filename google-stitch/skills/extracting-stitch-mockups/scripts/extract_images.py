#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "playwright>=1.50.0",
# ]
# ///
"""
Extract mockup images from Google Stitch project pages.

Requires:
- uv (https://github.com/astral-sh/uv)
- Authenticated Chrome profile with Google session
- Playwright browsers: uv run playwright install chromium

Usage:
    uv run extract_images.py <project_url> [--feature <name>] [--output <dir>]

    # Or make executable and run directly:
    chmod +x extract_images.py
    ./extract_images.py <project_url>
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path


def get_chrome_profile_path():
    """Get default Chrome profile path for macOS."""
    home = Path.home()
    profile_path = home / "Library" / "Application Support" / "Google" / "Chrome"
    if profile_path.exists():
        return str(profile_path)
    return None


def get_repo_root():
    """Get git repository root directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return Path.cwd()


def normalize_feature_name(name):
    """Convert name to feature directory format."""
    # Lowercase
    name = name.lower()
    # Replace whitespace with hyphens
    name = re.sub(r'\s+', '-', name)
    # Strip non-alphanumeric except hyphens
    name = re.sub(r'[^a-z0-9-]', '', name)
    # Collapse duplicate hyphens
    name = re.sub(r'-+', '-', name)
    # Trim ends
    name = name.strip('-')
    return name


def find_existing_features(repo_root):
    """Find existing feature directories in .google-stitch/."""
    stitch_dir = repo_root / ".google-stitch"
    if not stitch_dir.exists():
        return []

    features = []
    for item in stitch_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            features.append(item.name)
    return sorted(features)


def match_feature_directory(project_title, existing_features):
    """Try to match project title to existing feature directory."""
    normalized = normalize_feature_name(project_title)

    # Exact match
    if normalized in existing_features:
        return normalized

    # Partial match (project title contains feature name or vice versa)
    matches = []
    for feature in existing_features:
        if feature in normalized or normalized in feature:
            matches.append(feature)

    if len(matches) == 1:
        return matches[0]

    return None


def extract_mockups(url, feature=None, output_dir=None):
    """Extract mockup images from Stitch project page."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: Playwright not installed.")
        print("Install browsers with: uv run playwright install chromium")
        sys.exit(1)

    # Validate URL
    if "stitch.withgoogle.com/projects/" not in url:
        print(f"Error: Invalid Stitch project URL: {url}")
        print("Expected format: https://stitch.withgoogle.com/projects/<id>")
        sys.exit(1)
    print(f"✓ URL validated")

    chrome_profile = get_chrome_profile_path()
    if not chrome_profile:
        print("Error: Chrome profile not found.")
        print("Expected location: ~/Library/Application Support/Google/Chrome")
        sys.exit(1)
    print(f"✓ Chrome profile found: {chrome_profile}")

    repo_root = get_repo_root()
    print(f"✓ Repository root: {repo_root}")

    collected_images = []
    project_title = None

    print("Launching Chrome browser with authenticated profile...")
    with sync_playwright() as p:
        # Launch Chrome with user profile for authentication
        browser = p.chromium.launch_persistent_context(
            user_data_dir=chrome_profile,
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        print("✓ Browser launched")

        # Track image responses
        def handle_response(response):
            try:
                if response.request.resource_type == "image":
                    img_url = response.url
                    # Filter for Stitch mockup images
                    if "lh3.googleusercontent.com/aida/" in img_url:
                        collected_images.append({
                            "url": img_url,
                            "body": response.body()
                        })
                        print(f"  → Captured mockup image ({len(collected_images)})")
            except Exception:
                pass  # Ignore failed image responses

        page.on("response", handle_response)

        print(f"Navigating to: {url}")
        page.goto(url, wait_until="networkidle")
        print("✓ Page loaded (network idle)")

        # Wait for content to load
        print("Waiting for content to render (3s)...")
        page.wait_for_timeout(3000)

        # Check if still generating
        print("Checking generation status...")
        page_content = page.content()
        if "Generating" in page_content and "estimated time" in page_content.lower():
            print("Error: Project is still generating.")
            print("Please wait for generation to complete and try again.")
            browser.close()
            sys.exit(1)
        print("✓ Generation complete")

        # Extract project title
        print("Extracting project metadata...")
        try:
            title_element = page.query_selector('h1, [class*="title"], [class*="project-name"]')
            if title_element:
                project_title = title_element.inner_text().strip()
        except Exception:
            pass

        if not project_title:
            # Fallback: extract from URL
            project_id = url.split("/projects/")[-1].split("/")[0].split("?")[0]
            project_title = f"stitch-project-{project_id}"

        print(f"✓ Project title: {project_title}")

        # Wait a bit more for lazy-loaded images
        print("Waiting for lazy-loaded images (2s)...")
        page.wait_for_timeout(2000)

        print("Closing browser...")
        browser.close()
        print("✓ Browser closed")

    if not collected_images:
        print("No mockup images found on the page.")
        print("Make sure the project has completed generating.")
        sys.exit(1)

    # Filter images by size (>= 400px typically indicates mockups)
    # We'll save all collected images since they're already filtered by URL pattern
    print(f"✓ Found {len(collected_images)} mockup images")
    print("\nResolving output directory...")

    # Determine output directory
    if output_dir:
        save_dir = Path(output_dir)
    elif feature:
        save_dir = repo_root / ".google-stitch" / feature / "exports"
    else:
        # Try to auto-detect feature directory
        existing_features = find_existing_features(repo_root)
        matched_feature = match_feature_directory(project_title, existing_features)

        if matched_feature:
            print(f"Auto-detected feature directory: {matched_feature}")
            save_dir = repo_root / ".google-stitch" / matched_feature / "exports"
        elif existing_features:
            print("\nCould not auto-detect feature directory.")
            print("Existing feature directories:")
            for i, feat in enumerate(existing_features, 1):
                print(f"  {i}. {feat}")
            print(f"\nPlease re-run with --feature <name> to specify target directory.")
            print(f"Or create new feature directory with authoring-stitch-prompts skill first.")
            sys.exit(1)
        else:
            # No existing features, create based on project title
            feature_name = normalize_feature_name(project_title)
            save_dir = repo_root / ".google-stitch" / feature_name / "exports"
            print(f"Creating new feature directory: {feature_name}")

    # Create output directory
    save_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory: {save_dir}")

    # Save images
    print("\nSaving mockup images...")
    saved_files = []
    for i, img_data in enumerate(collected_images, 1):
        filename = f"mockup-{i}.png"
        filepath = save_dir / filename

        with open(filepath, "wb") as f:
            f.write(img_data["body"])

        saved_files.append(filename)
        print(f"  ✓ Saved: {filename}")

    # Print summary
    print(f"\nExtracted {len(saved_files)} mockups from Stitch project")
    print(f"\nProject: {project_title}")
    print(f"URL: {url}")
    print(f"\nSaved to: {save_dir.relative_to(repo_root)}")

    return {
        "project_title": project_title,
        "url": url,
        "output_dir": str(save_dir),
        "files": saved_files
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract mockup images from Google Stitch project pages."
    )
    parser.add_argument(
        "url",
        help="Stitch project URL (https://stitch.withgoogle.com/projects/<id>)"
    )
    parser.add_argument(
        "--feature",
        help="Target feature directory name (e.g., 'dashboard')"
    )
    parser.add_argument(
        "--output", "--output-dir",
        dest="output",
        help="Custom output directory path"
    )

    args = parser.parse_args()

    result = extract_mockups(
        url=args.url,
        feature=args.feature,
        output_dir=args.output
    )

    # Output JSON for programmatic use
    if os.environ.get("OUTPUT_JSON"):
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
