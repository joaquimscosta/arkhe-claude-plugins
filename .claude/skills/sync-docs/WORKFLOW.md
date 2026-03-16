# Workflow: Sync Docs Impact Analysis

Detailed instructions for each phase of the impact analysis.

## Phase 1: Run the Script

Execute the sync and diff script:

```bash
scripts/sync_and_diff.py           # Full sync
scripts/sync_and_diff.py --dry-run # Preview only
```

The script outputs JSON to stdout. Parse it and use the structured data for analysis.

### JSON Output Structure

```json
{
  "sync_result": { "exit_code": 0, "summary": "3 changed, 5 unchanged" },
  "files": [
    {
      "filename": "SKILLS.md",
      "changed": true,
      "added_lines": 42,
      "removed_lines": 15,
      "added_sections": ["### New field: isolation"],
      "removed_sections": [],
      "diff": "... unified diff ..."
    }
  ],
  "validator_constants": {
    "allowed_frontmatter_keys": ["agent", "allowed-tools", ...],
    "valid_hook_events": ["ConfigChange", "Notification", ...],
    "valid_memory_scopes": ["local", "project", "user"]
  },
  "doc_fields": {
    "skills_frontmatter_fields": ["agent", "allowed-tools", ...],
    "subagents_frontmatter_fields": ["description", "maxTurns", ...],
    "hook_events": ["ConfigChange", "Notification", ...]
  },
  "discrepancies": {
    "frontmatter_keys": {
      "in_docs_not_validator": [],
      "in_validator_not_docs": []
    },
    "hook_events": { ... },
    "memory_scopes": { ... }
  }
}
```

## Phase 2a: Skill Validator Impact

### Frontmatter Keys

1. Read `discrepancies.frontmatter_keys`
2. If `in_docs_not_validator` is non-empty:
   - **Severity**: CRITICAL
   - **Impact**: The validator will flag these as "Unknown frontmatter key(s)" via rule FM009
   - **Fix**: Add the new keys to `ALLOWED_FRONTMATTER_KEYS` in `.claude/skills/skill-validator/scripts/validate_skill.py` (~line 151)
   - **Report**: List each new key and its description from the synced doc
3. If `in_validator_not_docs` is non-empty:
   - **Severity**: WARNING
   - **Impact**: The validator allows keys that docs don't document. These may be undocumented internal fields or deprecated.
   - **Action**: Review whether these keys should remain in the validator

### Hook Events

1. Read `discrepancies.hook_events`
2. If `in_docs_not_validator` is non-empty:
   - **Severity**: CRITICAL
   - **Impact**: The validator will flag these as "Unknown hook event" via rule HK001
   - **Fix**: Add the new events to `VALID_HOOK_EVENTS` in `validate_skill.py` (~line 1021)
3. If `in_validator_not_docs` is non-empty:
   - **Severity**: WARNING
   - **Impact**: The validator accepts events that docs no longer list

### Memory Scopes

1. If SUBAGENTS.md changed, read the diff for the memory section
2. Look for new scope values beyond `user`, `project`, `local`
3. If found:
   - **Severity**: CRITICAL
   - **Fix**: Update `valid_scopes` in `validate_skill.py` (~line 473)

### Extraction Errors

Check `validator_constants.extraction_errors` and `doc_fields.extraction_errors`. If any:
- Report the error
- Fall back to manual inspection: read the relevant file directly and compare

## Phase 2b: Plugin Component Impact

For each **changed** synced doc:

### SKILLS.md Changes
1. Identify new/removed/modified frontmatter fields from the diff
2. Grep `plugins/*/skills/*/SKILL.md` for usage of affected fields
3. Check if any plugin skill uses a field that was removed or renamed

### HOOKS.md Changes
1. Identify new/removed hook events from the diff
2. Grep `plugins/*/` for hook configurations referencing affected events
3. Check hookify rules in `.claude/` for affected events

### SUBAGENTS.md Changes
1. Identify new agent configuration options
2. Grep `plugins/*/agents/*.md` for affected frontmatter fields
3. Note new capabilities (e.g., new agent fields) as INFO

### PLUGINS_REFERENCE.md Changes
1. Identify changes to plugin manifest schema
2. Check all `plugins/*/.claude-plugin/plugin.json` files for compliance
3. Check `.claude-plugin/marketplace.json` for affected fields

### BEST_PRACTICES.md Changes
1. Note any changes to recommended patterns
2. Cross-reference with CLAUDE.md guidelines section

### SETTINGS.md / MCP.md Changes
1. Note configuration changes
2. Check `.claude/settings.json` and `.mcp.json` for affected settings

## Phase 2c: Project Documentation Impact

### CLAUDE.md
Read the following sections and compare against the updated synced docs:
- "Plugin Component Guidelines" → compare frontmatter field reference against SKILLS.md
- "Key Documentation Files" → verify descriptions match synced file content
- "Plugin Development Workflow" → verify patterns match current docs

### docs/README.md
- "Synced Documentation" list → verify all 8 files are listed with correct descriptions
- Learning path references → verify links are still valid

### docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md
- Frontmatter reference sections → compare against SKILLS.md table
- Hook event references → compare against HOOKS.md table
- Any code patterns → verify they match current official recommendations

## Phase 3: Report Generation

Compile findings into the report format specified in SKILL.md. Group by severity:

1. **CRITICAL**: Validator will reject valid configurations → must fix
2. **WARNING**: Stale references or deprecated patterns → should fix
3. **INFO**: New capabilities available → optional to leverage

For each finding, include:
- The specific file and line number affected
- What changed in the synced doc
- The recommended fix (with code snippet if applicable)
