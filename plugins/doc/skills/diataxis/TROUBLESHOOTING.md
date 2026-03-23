# Diataxis Troubleshooting

Common issues and solutions when using the Diataxis skill.

---

## Script Execution Issues

### `uv` command not found

**Symptom:** `command not found: uv`

**Fix:** Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or run scripts directly with Python:
```bash
python3 scripts/diataxis_classify.py docs/*.md
```

### Permission denied

**Symptom:** `bash: permission denied: scripts/diataxis_classify.py`

**Fix:**
```bash
chmod +x scripts/diataxis_classify.py
```

### ModuleNotFoundError: shared

**Symptom:** `ModuleNotFoundError: No module named 'shared'`

**Fix:** Run scripts from the skill directory or ensure the scripts directory contains `shared.py`:
```bash
ls plugins/doc/skills/diataxis/scripts/shared.py
```

---

## Classification Issues

### All files classified as "low" confidence

**Possible causes:**
1. Files lack quadrant-specific keywords in titles or content
2. Files are very short (< 10 lines)
3. Files use non-standard naming conventions

**Diagnosis:**
```bash
uv run scripts/diataxis_classify.py docs/*.md --verbose
```
Check the per-quadrant scores. If all scores are near 0, the content may not match any keyword patterns.

**Solutions:**
- Rename files with clearer names (e.g., `notes.md` → `how-to-deploy.md`)
- Add clear headings that signal the quadrant type
- Use `--no-content` to test filename-only classification

### README.md always classified as "low" confidence

**Expected behavior.** README files are intentionally mixed-purpose documents. They typically contain elements of multiple quadrants (quick start tutorial, feature reference, installation how-to). Low confidence is correct — the README is not a pure Diataxis document.

**Recommendation:** Exclude README.md from Diataxis analysis or accept the low confidence. Add `"README.md"` to the `ignore` list in `.diataxis-config.json`.

### Tutorial vs How-to misclassification

**Common issue:** Short tutorials classified as how-to guides, or detailed how-to guides classified as tutorials.

**Key distinction:**
- **Tutorial** = learning journey (for study, builds skills)
- **How-to** = task solution (for work, solves a problem)

**Tips to improve classification:**
- Tutorials should have: "What you'll learn", prerequisites, numbered steps that build on each other
- How-to guides should have: clear problem statement, concise steps, assumed competence

### Collapsed document false positives

**Symptom:** A document is flagged as collapsed but should be a single document.

**When this is OK:**
- README files (always mixed)
- Small docs that naturally combine two types
- ADR/RFC documents (explanation + reference by nature)

**When to split:**
- A tutorial that includes 5+ configuration tables → extract tables to reference
- A how-to guide with 500+ words of theory → extract theory to explanation
- An architecture doc with API endpoint tables → extract endpoints to reference

---

## Validation Issues

### DX001: Tutorial contains reference tables

**What it means:** Your tutorial has tabular data (parameter lists, option tables) that belongs in a Reference document.

**Fix:** Extract the tables into a separate reference doc and link to it:
```markdown
For the full list of options, see the Configuration Reference (`reference/config.md`).
```

### DX002: How-to has long preamble

**What it means:** Your how-to guide has 100+ words of text before the first actionable step. How-to guides should get to the point quickly.

**Fix:** Move the conceptual introduction to an Explanation document. Start the how-to with the problem statement and first step.

### DX003: Reference contains steps

**What it means:** Your reference document has numbered step-by-step instructions. Reference docs should describe, not instruct.

**Fix:** Move the procedural content to a How-to guide. Keep the reference factual and tabular.

### DX004: Explanation contains commands

**What it means:** Your explanation document has executable code blocks. Explanations should explain concepts, not show how to do things.

**Fix:** Move command examples to a How-to guide. Keep the explanation focused on the "why" and "how it works" conceptually.

### DX006: Collapsed document

**What it means:** The document has strong signals for two or more quadrants (both score > 0.3 with a ratio < 2:1).

**Fix:** Split the document. See [Example 6 in EXAMPLES.md](EXAMPLES.md#example-6-handling-collapsed-documents) for a step-by-step guide.

---

## Audit Issues

### Quality score below 50

**Components to address:**
- **Low coverage balance**: Write docs for missing quadrants
- **Low quadrant purity**: Split collapsed documents
- **Low classification confidence**: Improve file naming and headings
- **Low documentation volume**: Write more documentation

### "No markdown files found"

**Check:**
1. The `--dir` path is correct
2. Files have `.md` extension
3. Files are not excluded by ignore patterns in `.diataxis-config.json`

---

## Config Issues

### Config file not found

**Symptom:** `Warning: Config not found: .diataxis-config.json, using defaults`

**Not a problem.** The config file is optional. All scripts work with sensible defaults. Create one with:
```bash
uv run scripts/diataxis_scaffold.py --init-config
```

### Custom ignore patterns not working

**Check:** The `ignore` array in `.diataxis-config.json` uses glob patterns:
```json
{
  "ignore": ["node_modules", ".git", "adr", "*.pdf", "README.md"]
}
```

Patterns match directory and file names (not full paths).
