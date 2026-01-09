# Troubleshooting Guide

## Table of Contents

- [False Positives](#false-positives)
- [Rule Suppression](#rule-suppression)
- [Common Issues](#common-issues)

## False Positives

### CW001: Second-Person Language

**Issue**: False positive on acceptable "you" usage in examples or quotes.

**Solution**: Some second-person usage is appropriate:
- Inside code examples
- In quoted user messages
- In UI text examples

Suppress with: `--ignore CW001`

### CW002: First-Person Language

**Issue**: False positive in examples showing Claude's responses.

**Solution**: First-person in example outputs is acceptable.

Suppress with: `--ignore CW002`

### FM011: Gerund Naming

**Issue**: Not all skills benefit from gerund naming.

**Solution**: This is a suggestion only. Skills like `pdf`, `docx`, `xlsx` are valid.

This rule is SUGGESTION severity and can be ignored.

### RI002: Orphan Files

**Issue**: Files referenced indirectly (through scripts) flagged as orphan.

**Solution**: Add a brief reference in SKILL.md even if file is primarily used by scripts.

Example:
```markdown
## Resources
- Scripts in `scripts/` use templates from `assets/`
```

## Rule Suppression

### Command-Line Suppression

```bash
# Ignore specific rules
scripts/validate_skill.py /path/to/skill --ignore CW001,CW002

# Ignore multiple rules
scripts/validate_skill.py /path/to/skill --ignore FM011,CW001,CW002,CW003
```

### Inline Suppression (Scripts Only)

Add comment in Python scripts:

```python
# skill-validator: ignore SC001
result = eval(user_expression)  # Safe: expression is validated
```

## Common Issues

### "SKILL.md not found"

**Cause**: Wrong directory or missing file.

**Solution**:
1. Verify path points to skill directory (not parent)
2. Create SKILL.md with proper frontmatter

### "Invalid YAML in frontmatter"

**Cause**: YAML syntax error.

**Common fixes**:
- Ensure `---` delimiters on their own lines
- Quote strings with special characters
- Check indentation (use spaces, not tabs)

### "Name must be lowercase-with-hyphens"

**Cause**: Name contains uppercase, underscores, or spaces.

**Solution**: Convert to format `my-skill-name`:
- `MySkill` → `my-skill`
- `my_skill` → `my-skill`
- `My Skill` → `my-skill`

### "Description exceeds 1024 characters"

**Cause**: Description too long.

**Solution**:
1. Move detailed explanation to SKILL.md body
2. Keep description focused on triggers
3. Use template: "[What it does]. Use when [triggers]."

### "Script not executable"

**Cause**: Missing execute permission.

**Solution**:
```bash
chmod +x scripts/*.py
```

### "Python script missing shebang"

**Cause**: First line doesn't start with `#!`.

**Solution**: Add as first line:
```python
#!/usr/bin/env python3
```

### "eval/exec detected"

**Cause**: Dynamic code execution found.

**Solutions**:
1. **Remove if possible**: Refactor to avoid eval/exec
2. **If necessary**: Add inline suppression with justification:
   ```python
   # skill-validator: ignore SC001
   # Required for dynamic expression evaluation in calculator
   result = eval(sanitized_expr)
   ```

### "Undocumented numeric constant"

**Cause**: Magic number without explanation.

**Solution**: Add comment on same line or line above:
```python
# Seconds per day (24 * 60 * 60)
SECONDS_PER_DAY = 86400
```

### "Deeply nested reference detected"

**Cause**: Reference file links to another reference file.

**Solution**: Flatten structure:
- SKILL.md should link directly to all reference files
- Avoid A.md → B.md → C.md chains

### "File not referenced from SKILL.md"

**Cause**: Markdown file exists but isn't linked.

**Solutions**:
1. Add reference in SKILL.md
2. Delete if truly unused
3. If used by scripts only, add brief mention in SKILL.md
