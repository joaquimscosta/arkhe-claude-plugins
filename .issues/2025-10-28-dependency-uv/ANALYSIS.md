# Extract-YouTube Skill: Dependency Management Issue Analysis

**Date:** 2025-10-28
**Status:** Issue Identified - Awaiting Fix Implementation

## Executive Summary

The `extract-youtube` skill fails to install its required dependency (`youtube-transcript-api`) when using the documented `uv pip install` command. The root cause is a combination of system configuration (Python 2.7 as default) and incomplete installation instructions that don't account for `uv`'s requirements for virtual environments or explicit Python version specification.

---

## Issue Description

### Symptom
When attempting to extract YouTube content using the skill, the dependency installation fails with:

```bash
$ uv pip install youtube-transcript-api
error: Failed to inspect Python interpreter from first executable in the search path at `/usr/local/bin/python`
  Caused by: Can't use Python at `/usr/local/bin/python`
  Caused by: Python executable does not support `-I` flag. Please use Python 3.8 or newer.
```

### Impact
- Users cannot use the extract-youtube skill without manual intervention
- Installation instructions in documentation are incorrect/incomplete
- No automated setup process exists
- Inconsistent with the goal of making skills easy to use

---

## Root Cause Analysis

### 1. System Configuration Issue

**Python Version Conflict:**
- System has Python 2.7.17 at `/usr/local/bin/python` (default `python` command)
- Python 3.14.0 is available but only as `python3` command
- `uv` searches for first `python` in PATH, finds Python 2.7
- Python 2.7 doesn't support the `-I` flag required by `uv`

**Verification:**
```bash
$ python --version
Python 2.7.17

$ python3 --version
Python 3.14.0

$ which python
/usr/local/bin/python

$ which python3
/usr/local/bin/python3
```

### 2. UV Configuration Issue

**No Virtual Environment:**
When specifying Python 3 explicitly, `uv` still fails:

```bash
$ uv pip install --python python3 youtube-transcript-api
error: No virtual environment found for Python 3; run `uv venv` to create an environment,
or pass `--system` to install into a non-virtual environment
```

**UV Behavior:**
- `uv pip install` expects either:
  1. An active virtual environment, OR
  2. The `--system` flag for global installation
- Current documentation doesn't mention either requirement

### 3. Documentation Gaps

**Current Instructions (SKILL.md lines 28-40):**
```markdown
## Requirements

- **Python**: 3.8+ (verify with `python3 --version`)
- **uv**: Package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Dependencies**: Install with `uv pip install youtube-transcript-api`
```

**Problems:**
- Assumes `uv pip install` works without flags
- Doesn't mention virtual environment creation
- Doesn't handle Python 2.7 as default `python`
- No `--python python3` or `--system` flags documented

---

## Current State: File Structure

### Extract-YouTube Skill
**Location:** `arkhe-claude-plugins/skola/skills/extract-youtube/`

**Files Present:**
```
extract-youtube/
├── SKILL.md                    # Main documentation
├── TROUBLESHOOTING.md          # Error handling guide
├── WORKFLOW.md                 # Implementation steps
├── EXAMPLES.md                 # Usage examples
└── scripts/
    ├── extract.py              # Main orchestrator
    ├── youtube_client.py       # URL parsing, metadata
    ├── transcript_extractor.py # Transcript fetching
    └── file_writer.py          # File organization
```

**Files Missing:**
- `pyproject.toml` - Modern Python project configuration
- `requirements.txt` - Dependency list for pip
- `uv.toml` - UV-specific configuration
- `.venv/` - Virtual environment directory
- `setup.sh` - Automated setup script
- Any dependency management automation

### Extract-Udemy Skill (Comparison)
**Location:** `arkhe-claude-plugins/skola/skills/extract-udemy/`

**Key Difference:**
```markdown
- **Libraries**: Standard library only (no pip packages needed)
```

Extract-udemy uses only Python's standard library, so it has no dependency installation issues.

### Project Root
**Location:** `/Users/jcosta/Projects/skola.dev/`

**Findings:**
- No project-wide `pyproject.toml`
- No shared virtual environment
- `arkhe-claude-plugins` is a symlink to `/Users/jcosta/Projects/arkhe-claude-plugins`
- Each skill is independent (no shared dependency management)

---

## Dependency Requirements

### youtube-transcript-api

**Package:** `youtube-transcript-api`
**Purpose:** Extract video transcripts from YouTube
**Installation:** Not currently installed
**PyPI:** https://pypi.org/project/youtube-transcript-api/

**Verification of Missing Dependency:**
```bash
$ python3 -c "import youtube_transcript_api"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'youtube_transcript_api'
```

---

## Proposed Solutions

### Option A: Virtual Environment Approach (Recommended)

**Benefits:**
- Isolated dependencies per skill
- Professional Python development practice
- Avoids version conflicts with other projects
- Aligns with modern Python tooling

**Implementation:**
1. Create `pyproject.toml` in `extract-youtube/`:
   ```toml
   [project]
   name = "extract-youtube"
   version = "0.1.0"
   requires-python = ">=3.8"
   dependencies = [
       "youtube-transcript-api>=0.6.0",
   ]
   ```

2. Create `setup.sh` script:
   ```bash
   #!/bin/bash
   cd "$(dirname "$0")"
   uv venv --python python3
   source .venv/bin/activate
   uv pip install -r pyproject.toml
   echo "Setup complete! Activate with: source .venv/bin/activate"
   ```

3. Update `SKILL.md` to reference setup script
4. Modify `extract.py` to use venv Python or check for activation

**Files to Create:**
- `pyproject.toml`
- `setup.sh`
- `requirements.txt` (optional, for pip fallback)

**Files to Update:**
- `SKILL.md` - Update installation section
- `TROUBLESHOOTING.md` - Add venv troubleshooting
- `WORKFLOW.md` - Include venv activation step

---

### Option B: System-Wide Installation Approach

**Benefits:**
- Simplest to document
- No virtual environment complexity
- Works with existing `uv` installation

**Implementation:**
1. Update documentation with corrected command:
   ```bash
   uv pip install --python python3 --system youtube-transcript-api
   ```

2. Add fallback to standard pip:
   ```bash
   # Or using pip directly:
   python3 -m pip install youtube-transcript-api
   ```

3. Create `requirements.txt`:
   ```
   youtube-transcript-api>=0.6.0
   ```

**Files to Create:**
- `requirements.txt`

**Files to Update:**
- `SKILL.md` - Fix installation command
- `TROUBLESHOOTING.md` - Document Python 2.7 issue

**Drawbacks:**
- Installs globally (potential conflicts)
- Less isolated than venv approach
- May require sudo/admin permissions

---

### Option C: Self-Contained Script Approach

**Benefits:**
- Most user-friendly (auto-installs on first run)
- No separate setup step required
- Handles missing dependencies gracefully

**Implementation:**
1. Add dependency check to `extract.py`:
   ```python
   import sys
   import subprocess

   def check_dependencies():
       try:
           import youtube_transcript_api
       except ImportError:
           print("youtube-transcript-api not found. Installing...")
           response = input("Install youtube-transcript-api? (y/n): ")
           if response.lower() == 'y':
               subprocess.check_call([
                   sys.executable, "-m", "pip", "install", "youtube-transcript-api"
               ])
               print("Installation complete. Please run the script again.")
               sys.exit(0)
           else:
               print("Cannot proceed without youtube-transcript-api.")
               sys.exit(1)

   check_dependencies()
   ```

2. Update documentation to mention auto-install feature

**Files to Update:**
- `scripts/extract.py` - Add dependency check
- `SKILL.md` - Document auto-install behavior

**Drawbacks:**
- Modifies user's environment without explicit setup
- May surprise users with unexpected installations
- Requires user interaction during execution

---

## Comparison: Pattern Across Skills

### Extract-Udemy
- **Dependencies:** None (stdlib only)
- **Setup Required:** No
- **Works Out of Box:** Yes

### Extract-YouTube
- **Dependencies:** `youtube-transcript-api`
- **Setup Required:** Yes (currently manual, broken)
- **Works Out of Box:** No

### Future Skills (Planned)
Need to establish consistent pattern for:
- Blog article extraction
- Coursera/edX course extraction
- Documentation site extraction

**Recommendation:** Establish standard dependency management pattern now to apply to all future skills.

---

## Recommended Fix Strategy

### Phase 1: Immediate Fix (Option B)
1. Update `SKILL.md` with correct `uv` command
2. Add `requirements.txt` for clarity
3. Document both `uv` and `pip` installation methods
4. Update `TROUBLESHOOTING.md` with Python 2.7 issue

**Timeline:** Quick fix (1 session)
**Risk:** Low
**User Impact:** Minimal (just documentation update)

### Phase 2: Long-Term Solution (Option A)
1. Implement virtual environment approach
2. Create automated setup script
3. Establish pattern for future skills
4. Update all skill documentation

**Timeline:** More involved (2-3 sessions)
**Risk:** Low to Medium
**User Impact:** Better isolation, more professional

### Phase 3: Enhancement (Optional)
1. Consider Option C for ultimate convenience
2. Create skill-wide dependency manager
3. Add pre-flight checks to all skills

---

## Questions to Resolve

Before implementing fix, need to decide:

1. **Which approach to use?**
   - Quick fix (Option B) vs Long-term (Option A) vs User-friendly (Option C)
   - Can combine approaches (e.g., venv + auto-setup)

2. **Virtual environment location?**
   - Per-skill: `extract-youtube/.venv/`
   - Shared: `arkhe-claude-plugins/skola/.venv/`
   - Project root: `skola.dev/.venv/`

3. **Dependency file format?**
   - Modern: `pyproject.toml` (preferred for new projects)
   - Traditional: `requirements.txt` (more universal)
   - Both: for compatibility

4. **Setup automation level?**
   - Manual: User runs setup script
   - Semi-auto: Script checks and prompts
   - Fully auto: Script installs without asking

5. **Pattern for other skills?**
   - Apply same approach to all future skills?
   - Document as standard in skill development guide?

---

## Related Files to Review

### Documentation
- `arkhe-claude-plugins/skola/skills/extract-youtube/SKILL.md:28-40` - Installation instructions
- `arkhe-claude-plugins/skola/skills/extract-youtube/TROUBLESHOOTING.md:78-87` - Dependency troubleshooting
- `arkhe-claude-plugins/skola/skills/extract-youtube/WORKFLOW.md` - Implementation workflow

### Scripts
- `arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py` - Main entry point
- `arkhe-claude-plugins/skola/skills/extract-youtube/scripts/transcript_extractor.py` - Uses youtube-transcript-api

### Comparison
- `arkhe-claude-plugins/skola/skills/extract-udemy/SKILL.md` - No dependencies example

---

## Testing Checklist

After implementing fix, verify:

- [ ] Installation works on system with Python 2.7 as default
- [ ] Installation works on system with Python 3 as default
- [ ] Extraction script can import `youtube-transcript-api`
- [ ] Documentation accurately reflects installation steps
- [ ] TROUBLESHOOTING.md covers common issues
- [ ] Works with both `uv` and `pip` (fallback)
- [ ] Virtual environment (if used) is properly isolated
- [ ] Setup script (if created) is executable and idempotent
- [ ] Pattern is documented for future skill development

---

## Next Steps

1. Review this analysis document
2. Decide on approach (A, B, or C)
3. Answer questions in "Questions to Resolve" section
4. Implement chosen solution
5. Test on fresh system/environment
6. Update related documentation
7. Apply pattern to future skills

---

## Additional Context

### System Information
- **Working Directory:** `/Users/jcosta/Projects/skola.dev`
- **Python 2.7 Location:** `/usr/local/bin/python`
- **Python 3.14 Location:** `/usr/local/bin/python3`
- **UV Version:** 0.8.22 (ade2bdbd2 2025-09-23)
- **Git Branch:** main
- **arkhe-claude-plugins:** Symlink to `/Users/jcosta/Projects/arkhe-claude-plugins`

### Current Workaround
To manually install the dependency and test the skill:

```bash
# Option 1: Using pip
python3 -m pip install youtube-transcript-api

# Option 2: Using uv with correct flags
uv pip install --python python3 --system youtube-transcript-api

# Verify installation
python3 -c "import youtube_transcript_api; print('Success!')"

# Test extraction
python3 arkhe-claude-plugins/skola/skills/extract-youtube/scripts/extract.py "https://youtu.be/VIDEO_ID"
```

---

## References

- **UV Documentation:** https://github.com/astral-sh/uv
- **youtube-transcript-api:** https://github.com/jdepoix/youtube-transcript-api
- **Python Packaging Guide:** https://packaging.python.org/
- **pyproject.toml Spec:** https://peps.python.org/pep-0621/
