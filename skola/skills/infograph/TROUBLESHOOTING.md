# Troubleshooting

## UV-Specific Issues

**Script won't execute / Module not found**
```bash
# Solution 1: Use uv run (recommended)
uv run scripts/generate_infograph.py --help

# Solution 2: Dependencies auto-install on first run
# If you see "Installed 23 packages", this is normal and expected
```

**"uv: command not found"**
```bash
# Install uv first (choose one method):

# Via curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Via pip
pip install uv

# Via homebrew (macOS)
brew install uv

# Verify installation
uv --version
```

**Dependencies not installing automatically**
```bash
# Check Python version (must be 3.8+)
python3 --version

# Force dependency install if needed
uv pip install google-genai>=0.2.0

# Check uv version
uv --version
```

**Script executes but google-genai still missing**
```bash
# The script has inline dependencies (PEP 723)
# Should auto-install on first uv run

# If it fails, manually install:
uv pip install google-genai>=0.2.0

# Or use system pip:
pip install google-genai>=0.2.0
```

**Permission errors when running script**
```bash
# Make script executable
chmod +x scripts/generate_infograph.py

# Then run directly
./scripts/generate_infograph.py --help

# Or always use uv run (no chmod needed)
uv run scripts/generate_infograph.py --help
```

---

## API & Generation Issues

**Gemini auth**
- Ensure `GEMINI_API_KEY` is set in environment.

**Missing output**
- Check `--output-dir` permissions; default `./output/`.

**Structured JSON errors**
- Validate keys: `title`, `canvas{width,height}`, `regions[*]{id,type,x,y,w,h,(text|bullets|code|label)}`.
- Unknown types fallback to “panel” with text.

**Skill not triggering**
- Description must include specific triggers; keep concise and third-person :contentReference[oaicite:17]{index=17}:contentReference[oaicite:18]{index=18}.

**Oversized SKILL.md**
- Move long content into `references/` per progressive disclosure best practice :contentReference[oaicite:19]{index=19}.

