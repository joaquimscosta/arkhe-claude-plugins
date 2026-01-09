# Complete Rules Reference

## Table of Contents

- [Frontmatter Rules (FM)](#frontmatter-rules-fm)
- [Structure Rules (SS)](#structure-rules-ss)
- [Content Rules (CW)](#content-rules-cw)
- [File Organization Rules (FO)](#file-organization-rules-fo)
- [Reference Integrity Rules (RI)](#reference-integrity-rules-ri)
- [Security Rules (SC)](#security-rules-sc)

---

## Frontmatter Rules (FM)

### FM001: Name Required [CRITICAL]
**Check**: `name` field exists in YAML frontmatter.
**Fix**: Add `name: your-skill-name` to frontmatter.

### FM002: Description Required [CRITICAL]
**Check**: `description` field exists in YAML frontmatter.
**Fix**: Add `description: What it does. Use when [triggers].`

### FM003: Name Format [ERROR]
**Check**: Name contains only lowercase letters, digits, and hyphens.
**Pattern**: `^[a-z0-9-]+$`
**Fix**: Convert to lowercase-with-hyphens format.

### FM004: Name Length [ERROR]
**Check**: Name is 64 characters or less.
**Fix**: Shorten name.

### FM005: Reserved Words [ERROR]
**Check**: Name does not contain "anthropic" or "claude".
**Fix**: Remove reserved words from name.

### FM006: Hyphen Placement [ERROR]
**Check**: Name does not start/end with hyphen or contain consecutive hyphens.
**Fix**: Adjust hyphen placement.

### FM007: Description Length [ERROR]
**Check**: Description is 1024 characters or less.
**Fix**: Shorten description; move details to body.

### FM008: Angle Brackets [ERROR]
**Check**: Description does not contain `<` or `>`.
**Fix**: Remove angle brackets.

### FM009: Unknown Keys [WARNING]
**Check**: All frontmatter keys are recognized.
**Allowed**: `name`, `description`, `license`, `allowed-tools`, `metadata`, `model`, `context`, `agent`, `hooks`, `user-invocable`
**Fix**: Remove unrecognized keys.

### FM010: Trigger Keywords [WARNING]
**Check**: Description includes trigger scenarios.
**Patterns**: "use when", "when user", "trigger", "activate", "invoke"
**Fix**: Add "Use when [scenario]" to description.

### FM011: Gerund Naming [SUGGESTION]
**Check**: Name uses verb+ing convention.
**Examples**: `processing-pdfs`, `generating-reports`
**Fix**: Optional - consider renaming.

### FM012: Person in Description [WARNING]
**Check**: Description uses third person.
**Avoid**: "I can...", "You should...", "You can..."
**Fix**: Use "This skill...", "Extracts data from..."

---

## Structure Rules (SS)

### SS001: SKILL.md Exists [CRITICAL]
**Check**: SKILL.md file exists in skill directory.
**Fix**: Create SKILL.md with proper frontmatter.

### SS002: Line Limit [ERROR]
**Check**: SKILL.md is 500 lines or less.
**Fix**: Split content into WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md.

### SS003: Line Warning [WARNING]
**Check**: SKILL.md is under 300 lines.
**Fix**: Consider extracting detailed content.

### SS004: Supporting Docs [WARNING]
**Check**: Large SKILL.md (>200 lines) has supporting docs.
**Expected**: WORKFLOW.md, EXAMPLES.md, or TROUBLESHOOTING.md
**Fix**: Create supporting documentation files.

### SS005: Reference TOC [SUGGESTION]
**Check**: Reference files >100 lines have table of contents.
**Fix**: Add TOC at top of long reference files.

### SS006: Nested References [WARNING]
**Check**: References are one level deep from SKILL.md.
**Avoid**: SKILL.md → A.md → B.md
**Fix**: Link all reference files directly from SKILL.md.

---

## Content Rules (CW)

### CW001: Second Person [WARNING]
**Check**: Body does not use second-person language.
**Patterns**: "you should", "you can", "you will", "you need", "you'll", "your"
**Fix**: Use imperative form: "Create..." not "You should create..."

### CW002: First Person [WARNING]
**Check**: Body does not use first-person language.
**Patterns**: "I can", "I will", "I'll", "I am", "I'm"
**Fix**: Use third person: "This skill provides..."

### CW003: Multiple Options [SUGGESTION]
**Check**: Lists of alternatives include a default.
**Fix**: Add "(default)" or "(recommended)" to preferred option.

### CW004: MCP Tool Names [WARNING]
**Check**: MCP tools use fully qualified names.
**Pattern**: `ServerName:tool_name`
**Fix**: Use full `ServerName:tool_name` format.

### CW005: Time-Sensitive Info [WARNING]
**Check**: Content avoids dates or version-specific info.
**Fix**: Use collapsible sections for deprecated content.

### CW006: Inconsistent Terms [SUGGESTION]
**Check**: Uses consistent terminology.
**Fix**: Pick one term (e.g., "endpoint" vs "URL") throughout.

---

## File Organization Rules (FO)

### FO001: Forbidden Files [WARNING]
**Check**: Skill does not contain auxiliary documentation.
**Forbidden**: README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, QUICK_REFERENCE.md, CONTRIBUTING.md, LICENSE.md
**Fix**: Remove these files.

### FO002: Doc Naming [WARNING]
**Check**: Documentation files use UPPERCASE.md.
**Fix**: Rename `example.md` to `EXAMPLES.md`.

### FO003: Script Naming [WARNING]
**Check**: Script files use lowercase_with_underscores.py.
**Fix**: Rename `MyScript.py` to `my_script.py`.

### FO004: Script Executable [ERROR]
**Check**: Python scripts are executable.
**Fix**: Run `chmod +x scripts/*.py`.

### FO005: Script Shebang [ERROR]
**Check**: Python scripts have shebang.
**Fix**: Add `#!/usr/bin/env python3` as first line.

### FO006: Empty Directories [SUGGESTION]
**Check**: Resource directories contain files.
**Fix**: Remove empty `scripts/`, `references/`, or `assets/`.

### FO007: Path Separators [WARNING]
**Check**: Uses Unix-style paths.
**Fix**: Replace `\` with `/` in all paths.

---

## Reference Integrity Rules (RI)

### RI001: Broken Links [ERROR]
**Check**: All markdown links resolve to existing files.
**Fix**: Fix path or create missing file.

### RI002: Orphan Files [WARNING]
**Check**: All .md files are referenced from SKILL.md.
**Fix**: Add reference or remove unused file.

### RI003: Broken Anchors [WARNING]
**Check**: Anchor links (#section) resolve to existing headings.
**Fix**: Fix anchor or create target heading.

---

## Security Rules (SC)

### SC001: Dynamic Execution [CRITICAL]
**Check**: Scripts do not use `eval()` or `exec()`.
**Fix**: Remove or add inline suppression with justification.

### SC002: Magic Numbers [WARNING]
**Check**: Numeric constants have comments.
**Fix**: Add comment explaining purpose.

### SC003: Error Handling [WARNING]
**Check**: Errors are handled explicitly.
**Fix**: Add try/except with meaningful handling.

### SC004: Obfuscated Code [WARNING]
**Check**: No base64/hex encoded strings.
**Fix**: Explain purpose or remove obfuscation.

### SC005: Sensitive Logging [SUGGESTION]
**Check**: Logs don't contain credentials.
**Fix**: Remove sensitive data from log statements.
