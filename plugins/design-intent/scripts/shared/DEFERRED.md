# Deferred Implementation: Shared Scripts

**Status:** Deferred
**Reason:** Create when reusable logic emerges from actual usage
**Original Plan Date:** 2024-01-15

---

## Overview

The stitch-to-react skill was implemented with instructional guidance only. Python scripts for automating pattern checking and conflict detection were deferred until usage patterns reveal the need for programmatic automation.

## Deferred Scripts

### 1. pattern_checker.py

**Purpose:** Programmatically scan and report existing design intent patterns.

**Planned Functionality:**
```python
#!/usr/bin/env python3
"""
Scan /design-intent/patterns/ and return structured pattern data.

Usage:
    python pattern_checker.py [project_root]

Output:
    JSON with pattern names, key decisions, and applicable contexts.
"""

def scan_patterns(patterns_dir: Path) -> list[dict]:
    """
    Scan pattern files and extract:
    - Pattern name (from filename)
    - Decision summary (from ## Decision section)
    - When to use (from ## When to Use section)
    - Key values (spacing, colors, components mentioned)
    """
    pass

def check_pattern_applicability(patterns: list[dict], context: str) -> list[dict]:
    """
    Given a context description, return patterns that might apply.
    Uses keyword matching against pattern content.
    """
    pass
```

**Trigger for Implementation:**
- Multiple users report forgetting to check patterns manually
- Need for CI/CD integration to validate pattern compliance
- Automated pattern suggestions become a requested feature

---

### 2. conflict_resolver.py

**Purpose:** Detect conflicts between Stitch output and existing patterns.

**Planned Functionality:**
```python
#!/usr/bin/env python3
"""
Compare Stitch export tokens against existing pattern values.

Usage:
    python conflict_resolver.py <stitch_html> <patterns_dir>

Output:
    JSON with detected conflicts and resolution options.
"""

def extract_stitch_tokens(html_path: Path) -> dict:
    """
    Parse Stitch HTML and extract:
    - tailwind.config colors, spacing, fonts
    - Custom CSS values from <style> blocks
    - Component structure hints
    """
    pass

def compare_with_patterns(stitch_tokens: dict, patterns: list[dict]) -> list[dict]:
    """
    Compare extracted tokens against pattern values.
    Return conflicts with:
    - Element name
    - Stitch value
    - Pattern value
    - Pattern file reference
    - Suggested resolution options
    """
    pass

def format_conflict_report(conflicts: list[dict]) -> str:
    """
    Format conflicts as markdown for user presentation.
    """
    pass
```

**Trigger for Implementation:**
- Manual conflict detection becomes error-prone at scale
- Users request automated pre-conversion validation
- Integration with design review workflows needed

---

## Implementation Guidelines

When implementing these scripts, follow CLAUDE.md requirements:

### Script Requirements
- Python 3.8+ with standard library only
- No pip install or third-party packages
- Executable with shebang (`#!/usr/bin/env python3`)
- `chmod +x` before committing

### Allowed Standard Library Modules
```python
import json          # Pattern/conflict data serialization
import re            # Token extraction from HTML/CSS
import pathlib       # File system operations
from pathlib import Path
import sys           # CLI arguments
import argparse      # Argument parsing (optional)
```

### Forbidden
```python
# No third-party packages
import requests      # ❌
import beautifulsoup # ❌
import yaml          # ❌ (use json instead)

# No runtime installation
os.system("pip install...")  # ❌

# No code execution risks
eval(user_input)  # ❌
exec(...)         # ❌
```

---

## File Structure (When Implemented)

```
plugins/design-intent/
├── scripts/
│   └── shared/
│       ├── DEFERRED.md          # This file (remove after implementation)
│       ├── pattern_checker.py   # Pattern scanning utility
│       └── conflict_resolver.py # Conflict detection utility
└── skills/
    └── stitch-to-react/
        └── SKILL.md             # Update to reference scripts
```

---

## Success Criteria for Implementation

Implement these scripts when ANY of these conditions are met:

1. **Usage Volume:** The stitch-to-react skill is used 10+ times and manual pattern checking is reported as friction

2. **Error Rate:** Users report missing conflicts that scripts would have caught

3. **Integration Request:** CI/CD or design review workflow integration is requested

4. **Complexity Growth:** Pattern library grows beyond 10 patterns, making manual review impractical

---

## Related Documentation

- `skills/stitch-to-react/SKILL.md` - Current instructional approach
- `skills/stitch-to-react/WORKFLOW.md` - Manual workflow (Phase 1 & 4)
- `CLAUDE.md` - Python script guidelines
