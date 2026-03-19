# RFC Troubleshooting

## No RFC Directory Found

**Symptom**: `/rfc list` returns no results or `/rfc create` doesn't know where to write.

**Cause**: No RFC directory exists yet in the project.

**Fix**: `/rfc create` will automatically create `docs/rfcs/` as the default directory. For jd-docs projects, ensure `docs/20-architecture/` exists or create it first.

## RFC Numbering Conflict

**Symptom**: Auto-numbered RFC conflicts with an existing file.

**Cause**: RFCs exist across multiple convention paths (e.g., `docs/rfcs/` and `.arkhe/rfcs/`) and the highest number wasn't detected.

**Fix**: The skill searches all convention paths before numbering. If a conflict occurs, manually rename the file with the next available number.

## Template Not Found

**Symptom**: Create operation can't find the RFC template.

**Cause**: The template at `${CLAUDE_SKILL_DIR}/templates/rfc-template.md` is missing.

**Fix**: Verify the skill is properly installed. The template should be at `plugins/doc/skills/rfc/templates/rfc-template.md`. Reinstall the plugin if needed.

## No Architecture Standards for Review

**Symptom**: Review falls back to "general best practices" instead of project-specific standards.

**Cause**: No architecture documentation found in any of the expected locations.

**Fix**: Create architecture documentation in one of the supported paths:
- `.arkhe/roadmap/architecture.md` (arkhe convention)
- `docs/20-architecture/` directory (jd-docs convention)
- `docs/architecture.md` or `docs/architecture/` (generic)

## Update Changed Wrong Sections

**Symptom**: Sections that should have been preserved were modified.

**Cause**: Section boundaries were ambiguous or the update instruction was too broad.

**Fix**: Be specific about which sections to update (e.g., "update the Security Considerations and Data Model sections"). Review the diff summary output to verify changes.

## RFC Status Not Recognized

**Symptom**: `/rfc list` shows "Unknown" status for an RFC.

**Cause**: The `**Status**:` field is missing or uses a non-standard value.

**Fix**: Ensure the RFC header includes `**Status**: Draft` (or Review, Approved, Rejected, Superseded). The field must match exactly: `**Status**:` followed by one of the valid values.
