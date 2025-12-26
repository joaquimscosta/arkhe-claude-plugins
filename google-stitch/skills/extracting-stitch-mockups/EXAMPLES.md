# Examples: Extract Stitch Mockups

Sample extractions demonstrating skill usage and outputs.

---

## Example 1: Basic Extraction

### Input
```
User: Extract the mockups from this Stitch project
URL: https://stitch.withgoogle.com/projects/3236066188909813678
```

### Execution
```bash
uv run scripts/extract_images.py "https://stitch.withgoogle.com/projects/3236066188909813678"
```

### Output
```
Navigating to: https://stitch.withgoogle.com/projects/3236066188909813678
Project title: Eco-Travel Home Screen
Auto-detected feature directory: eco-travel
Found 3 mockup images
  Saved: mockup-1.png
  Saved: mockup-2.png
  Saved: mockup-3.png

Extracted 3 mockups from Stitch project

Project: Eco-Travel Home Screen
URL: https://stitch.withgoogle.com/projects/3236066188909813678

Saved to: design-intent/google-stitch/eco-travel/exports
```

### Result
```
design-intent/google-stitch/eco-travel/
├── prompt-v1.md
├── exports/
│   ├── mockup-1.png    <- New
│   ├── mockup-2.png    <- New
│   └── mockup-3.png    <- New
└── wireframes/
```

---

## Example 2: Explicit Feature Directory

### Input
```
User: Save the Stitch mockups to the dashboard feature directory
URL: https://stitch.withgoogle.com/projects/9876543210
```

### Execution
```bash
uv run scripts/extract_images.py "https://stitch.withgoogle.com/projects/9876543210" --feature dashboard
```

### Output
```
Navigating to: https://stitch.withgoogle.com/projects/9876543210
Project title: Analytics Dashboard v2
Found 4 mockup images
  Saved: mockup-1.png
  Saved: mockup-2.png
  Saved: mockup-3.png
  Saved: mockup-4.png

Extracted 4 mockups from Stitch project

Project: Analytics Dashboard v2
URL: https://stitch.withgoogle.com/projects/9876543210

Saved to: design-intent/google-stitch/dashboard/exports
```

---

## Example 3: No Matching Feature (User Selection Required)

### Input
```
User: Extract these Stitch designs
URL: https://stitch.withgoogle.com/projects/1111111111
```

### Execution
```bash
uv run scripts/extract_images.py "https://stitch.withgoogle.com/projects/1111111111"
```

### Output
```
Navigating to: https://stitch.withgoogle.com/projects/1111111111
Project title: User Settings Panel
Found 2 mockup images

Could not auto-detect feature directory.
Existing feature directories:
  1. dashboard
  2. eco-travel
  3. landing

Please re-run with --feature <name> to specify target directory.
Or create new feature directory with authoring-stitch-prompts skill first.
```

### Resolution
Either:
1. Specify existing: `--feature settings` (if created)
2. Create new feature first with authoring-stitch-prompts skill
3. Script creates new directory if none exist

---

## Example 4: Generation Still In Progress

### Input
```
User: Get the mockups from my latest Stitch generation
URL: https://stitch.withgoogle.com/projects/2222222222
```

### Execution
```bash
uv run scripts/extract_images.py "https://stitch.withgoogle.com/projects/2222222222"
```

### Output
```
Navigating to: https://stitch.withgoogle.com/projects/2222222222
Error: Project is still generating.
Please wait for generation to complete and try again.
```

---

## Example 5: Custom Output Directory

### Input
```
User: Extract mockups to a custom location
URL: https://stitch.withgoogle.com/projects/3333333333
Output: ~/Desktop/stitch-exports
```

### Execution
```bash
uv run scripts/extract_images.py "https://stitch.withgoogle.com/projects/3333333333" --output ~/Desktop/stitch-exports
```

### Output
```
Navigating to: https://stitch.withgoogle.com/projects/3333333333
Project title: Mobile App Onboarding
Found 5 mockup images
  Saved: mockup-1.png
  Saved: mockup-2.png
  Saved: mockup-3.png
  Saved: mockup-4.png
  Saved: mockup-5.png

Extracted 5 mockups from Stitch project

Project: Mobile App Onboarding
URL: https://stitch.withgoogle.com/projects/3333333333

Saved to: /Users/jcosta/Desktop/stitch-exports
```

---

## Example 6: First Extraction (No Existing Features)

### Input
```
User: Extract my first Stitch project
URL: https://stitch.withgoogle.com/projects/4444444444
```

### Execution
```bash
uv run scripts/extract_images.py "https://stitch.withgoogle.com/projects/4444444444"
```

### Output
```
Navigating to: https://stitch.withgoogle.com/projects/4444444444
Project title: Landing Page Hero
Creating new feature directory: landing-page-hero
Found 2 mockup images
  Saved: mockup-1.png
  Saved: mockup-2.png

Extracted 2 mockups from Stitch project

Project: Landing Page Hero
URL: https://stitch.withgoogle.com/projects/4444444444

Saved to: design-intent/google-stitch/landing-page-hero/exports
```

### Result
```
design-intent/google-stitch/
└── landing-page-hero/
    └── exports/
        ├── mockup-1.png
        └── mockup-2.png
```

---

## Workflow Integration Example

### Complete Design Cycle

1. **Create prompt** (authoring-stitch-prompts skill)
```
User: Create a Stitch prompt for a mobile banking dashboard
```
Result: `design-intent/google-stitch/banking-dashboard/prompt-v1.md`

2. **Generate in Stitch**
- Copy prompt to Stitch
- Generate designs
- Get project URL

3. **Extract mockups** (extract-stitch-mockups skill)
```
User: Extract the mockups from https://stitch.withgoogle.com/projects/5555555555
```
Result: Auto-detects `banking-dashboard` directory

4. **Final structure**
```
design-intent/google-stitch/banking-dashboard/
├── prompt-v1.md
├── exports/
│   ├── mockup-1.png
│   ├── mockup-2.png
│   └── mockup-3.png
└── wireframes/
```
