# Spring Refresh Troubleshooting

## Common Issues

### Git not available

**Symptom:** Script fails with "git: command not found" or returns no dates.

**Cause:** Git is not installed or not in PATH.

**Fix:** The script falls back gracefully — it will use `last_updated` from YAML frontmatter instead of git dates. Dates may be less accurate but the report will still work.

### Deep-research skill not installed

**Symptom:** `/spring-refresh refresh` fails to invoke deep-research.

**Cause:** The core plugin (which provides deep-research) is not installed.

**Fix:** Run `check` mode instead — it works without deep-research. To use `refresh` mode, install the core plugin:
```
/plugin install core@arkhe-claude-plugins
```

### EXA MCP tools not available

**Symptom:** Research refresh runs but produces minimal results.

**Cause:** The EXA MCP server is not configured.

**Fix:** The deep-research skill can still work with WebFetch/WebSearch as fallbacks. For best results, configure EXA MCP in your Claude Code settings.

### Research docs directory missing

**Symptom:** Report shows no research docs.

**Cause:** `docs/research/` directory doesn't contain Spring Boot research files.

**Fix:** Verify the files exist relative to the git project root:
```bash
ls docs/research/spring-boot-*.md
```
Expected files: `spring-boot-ecosystem-research.md`, `spring-boot-ddd-implementation.md`, `spring-boot-security-observability-testing.md`

### Frontmatter parse errors

**Symptom:** Skills show `unknown` for version or name.

**Cause:** The YAML frontmatter in SKILL.md doesn't include the expected fields.

**Fix:** Ensure each SKILL.md has proper frontmatter:
```yaml
---
name: skill-name
description: ...
spring-boot-version: "4.0"
---
```

### All skills show "NEEDS_UPDATE" after adding version metadata

**Symptom:** Every skill shows drift immediately after adding `spring-boot-version`.

**Cause:** This is expected if the skills haven't been modified since the research docs were last updated. The freshness check compares git modification dates.

**Fix:** Review each skill using `/spring-refresh update <skill-name>`. If the content is already accurate, simply touch the file (make any minor edit) to update its git timestamp.

### Viewing research docs on GitHub

**Symptom:** You want to browse research docs without cloning the repo.

**Links:**
- [spring-boot-ecosystem-research.md](https://github.com/joaquimscosta/arkhe-claude-plugins/blob/main/docs/research/spring-boot-ecosystem-research.md)
- [spring-boot-ddd-implementation.md](https://github.com/joaquimscosta/arkhe-claude-plugins/blob/main/docs/research/spring-boot-ddd-implementation.md)
- [spring-boot-security-observability-testing.md](https://github.com/joaquimscosta/arkhe-claude-plugins/blob/main/docs/research/spring-boot-security-observability-testing.md)

---

### Script shows wrong project root

**Symptom:** Research docs not found because the project root is incorrect.

**Cause:** The script uses `git rev-parse --show-toplevel` to find the project root.

**Fix:** Run the script from within the git repository, or pass the correct plugin root path:
```bash
python3 scan_skill_freshness.py /path/to/arkhe-claude-plugins/plugins/spring-boot
```
