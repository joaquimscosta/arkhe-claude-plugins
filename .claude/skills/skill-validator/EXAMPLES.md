# Validation Examples

## Example 1: Well-Formed Skill

```bash
$ scripts/validate_skill.py /path/to/pdf-processing

=== Skill Validation Report: pdf-processing ===
Path: /path/to/pdf-processing

Summary: No issues found!

─────────────────────────────────────────────────────────────────────
```

## Example 2: Skill with Multiple Issues

```bash
$ scripts/validate_skill.py /path/to/my-skill

=== Skill Validation Report: my-skill ===
Path: /path/to/my-skill

Summary: 1 critical, 2 error, 3 warning, 1 suggestion

──────────────────────────────────────────────────────────────────────

[CRITICAL] FM001: Required field 'name' missing from frontmatter
  Location: SKILL.md frontmatter
  Fix: Add 'name: your-skill-name' to frontmatter

──────────────────────────────────────────────────────────────────────

[ERROR] SS002: SKILL.md exceeds 500 line limit (523 lines)
  Location: SKILL.md
  Fix: Split content into WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md

──────────────────────────────────────────────────────────────────────

[ERROR] FO004: Script not executable
  Location: scripts/process.py
  Fix: Run: chmod +x scripts/process.py

──────────────────────────────────────────────────────────────────────

[WARNING] CW001: Second-person language detected
  Location: SKILL.md:45
  Found: you should
  Fix: Use imperative form: 'Create...' not 'You should create...'

──────────────────────────────────────────────────────────────────────

[WARNING] FM010: Description should include trigger scenarios
  Location: SKILL.md frontmatter
  Fix: Add 'Use when [scenario]' to description to help Claude know when to invoke

──────────────────────────────────────────────────────────────────────

[WARNING] RI002: File not referenced from SKILL.md
  Location: references/old-docs.md
  Fix: Add reference in SKILL.md or remove if unused

──────────────────────────────────────────────────────────────────────

[SUGGESTION] FM011: Consider using gerund naming convention (verb+ing)
  Location: SKILL.md frontmatter
  Found: pdf-editor
  Fix: Example: 'processing-pdfs' instead of 'pdf-processor'

──────────────────────────────────────────────────────────────────────

Use --ignore RULE1,RULE2 to suppress specific rules.
```

## Example 3: JSON Output

```bash
$ scripts/validate_skill.py /path/to/my-skill --format json

{
  "skill_name": "my-skill",
  "skill_path": "/path/to/my-skill",
  "summary": {
    "critical": 0,
    "error": 1,
    "warning": 2,
    "suggestion": 1,
    "total": 4
  },
  "issues": [
    {
      "rule_id": "SS002",
      "severity": "ERROR",
      "message": "SKILL.md exceeds 500 line limit (523 lines)",
      "location": "SKILL.md",
      "current_value": null,
      "fix_suggestion": "Split content into WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md"
    }
  ],
  "passed": false
}
```

## Example 4: Filtering by Severity

```bash
# Only show errors and critical issues
$ scripts/validate_skill.py /path/to/my-skill --min-severity error

=== Skill Validation Report: my-skill ===
Path: /path/to/my-skill

Summary: 1 error

──────────────────────────────────────────────────────────────────────

[ERROR] SS002: SKILL.md exceeds 500 line limit (523 lines)
  Location: SKILL.md
  Fix: Split content into WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md

──────────────────────────────────────────────────────────────────────
```

## Example 5: Ignoring Specific Rules

```bash
# Ignore second-person language warnings
$ scripts/validate_skill.py /path/to/my-skill --ignore CW001,CW002

=== Skill Validation Report: my-skill ===
Path: /path/to/my-skill

Summary: 1 warning

──────────────────────────────────────────────────────────────────────

[WARNING] FM010: Description should include trigger scenarios
  Location: SKILL.md frontmatter
  Fix: Add 'Use when [scenario]' to description

──────────────────────────────────────────────────────────────────────
```

## Example 6: Security Issue Detection

```bash
$ scripts/validate_skill.py /path/to/risky-skill

=== Skill Validation Report: risky-skill ===
Path: /path/to/risky-skill

Summary: 1 critical, 1 warning

──────────────────────────────────────────────────────────────────────

[CRITICAL] SC001: Dynamic code execution detected (eval/exec)
  Location: scripts/processor.py:42
  Fix: Remove eval/exec or add '# skill-validator: ignore SC001' with justification

──────────────────────────────────────────────────────────────────────

[WARNING] SC002: Undocumented numeric constant: 86400
  Location: scripts/processor.py:15
  Fix: Add comment explaining the constant's purpose

──────────────────────────────────────────────────────────────────────
```
