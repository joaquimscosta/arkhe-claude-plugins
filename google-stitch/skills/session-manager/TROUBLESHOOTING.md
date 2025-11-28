# Stitch Session Manager — Troubleshooting

## Missing Session Folder
- **Symptom:** `session.json not found`.
- **Fix:** Run `session:new` with the intended project name or provide the relative path to an existing session.
- **Prevention:** Reference the session path in follow-up prompts (“Continue the Mobile Banking session”).

## Duplicate Screen IDs
- **Symptom:** Attempting to add `dashboard` again overwrites or errors.
- **Fix:** The Skill auto-increments numeric suffixes (`dashboard-002`). Confirm the version you want; if it should replace v1, delete the prior file manually before re-running.

## Style Drift
- **Symptom:** New prompts ignore earlier palette/typography.
- **Fix:** Issue `session:style` (or “Re-state current style cues”) before adding a screen. Ensure earlier logs contain style descriptors; edit `session.json.style_guide` if needed.

## Export Errors
- **Symptom:** `summary.md` missing sections.
- **Fix:** Re-run `session:export`. If discrepancy persists, open `screen-log/*.json` and ensure each file has `name` and `prompt` fields; repair malformed entries.

## Closing Too Early
- **Symptom:** Session marked closed but new prompts required.
- **Fix:** Remove `closed_at` from `session.json` and continue, or start a fresh session (`project-name-v2`) for the next design cycle.
