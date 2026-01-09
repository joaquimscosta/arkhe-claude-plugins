---
name: skill-validator
description: Validate skills against best practices for YAML frontmatter, structure, content standards, file organization, and security. Use when creating new skills, updating existing skills, before packaging skills, reviewing skill quality, or when user mentions "validate skill", "check skill", "skill best practices", "skill review", or "lint skill".
---

# Skill Validator

Validate skills against Anthropic's best practices for structure, content, and security.

## Quick Start

```bash
scripts/validate_skill.py /path/to/skill-directory
```

With severity filter:

```bash
scripts/validate_skill.py /path/to/skill --min-severity warning
```

## Validation Categories

| Category | Rules | Checks |
|----------|-------|--------|
| **Frontmatter** | FM001-FM012 | Required fields, naming, description quality |
| **Structure** | SS001-SS006 | Line limits, progressive disclosure |
| **Content** | CW001-CW006 | Writing style, terminology |
| **Files** | FO001-FO007 | Naming conventions, forbidden files |
| **References** | RI001-RI003 | Broken links, orphan files |
| **Security** | SC001-SC005 | eval/exec, undocumented constants |

## Severity Levels

| Level | Action |
|-------|--------|
| CRITICAL | Must fix before publishing |
| ERROR | Should fix |
| WARNING | Consider fixing |
| SUGGESTION | Optional improvement |

## Output Example

```
=== Skill Validation Report: my-skill ===

Summary: 0 critical, 1 error, 2 warnings, 1 suggestion

[ERROR] SS002: SKILL.md exceeds 500 lines (523 lines)
  Location: SKILL.md
  Fix: Split content into WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md

[WARNING] CW001: Second-person language detected
  Location: SKILL.md:45
  Found: "You should create..."
  Fix: Use imperative: "Create..."
```

## Command Options

```bash
--min-severity {critical,error,warning,suggestion}  # Filter output
--format {text,json}                                # Output format
--ignore RULE1,RULE2                                # Skip specific rules
```

## Common Issues

**"False positive on second-person"**
- Context-appropriate "you" may be acceptable
- Use `--ignore CW001` to suppress

**"Script security warning"**
- Add inline comment: `# skill-validator: ignore SC001`

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete issue handling.

## References

- [EXAMPLES.md](EXAMPLES.md) - Real validation outputs
- [references/RULES_REFERENCE.md](references/RULES_REFERENCE.md) - Complete rules documentation
