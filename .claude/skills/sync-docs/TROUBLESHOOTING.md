# Troubleshooting: Sync Docs

## Common Issues

### "curl: command not found"

The underlying `update-claude-docs.sh` requires `curl`.

**Fix**: Install curl via your package manager:
```bash
# macOS (usually pre-installed)
brew install curl

# Ubuntu/Debian
sudo apt-get install curl
```

### "Permission denied" on sync script

The bash script or Python script lacks execute permission.

**Fix**:
```bash
chmod +x docs/reference/update-claude-docs.sh
chmod +x .claude/skills/sync-docs/scripts/sync_and_diff.py
```

### Network errors during sync

Individual file failures are handled gracefully — the sync continues with remaining files. Failed files appear as unchanged in the diff output.

**Symptoms**: `sync_result.exit_code` is non-zero, some files show `changed: false` when changes were expected.

**Fix**: Check network connectivity and retry. The sync script has a 30-second per-file timeout.

### Empty diffs despite known upstream changes

**Possible causes**:
1. Upstream docs haven't actually changed since last sync
2. Network returned cached content (CDN caching)
3. The sync script downloaded empty content and skipped the update (safety feature)

**Diagnosis**: Check `sync_result.stdout` for the script's own status messages (updated/failed/skipped counts).

### Validator constant extraction failed

The Python script uses regex to extract hardcoded constants from `validate_skill.py`. If the code structure changes significantly, extraction may fail.

**Symptoms**: `validator_constants.extraction_errors` contains error messages.

**Fix**: The script reports which constants it couldn't extract. Fall back to manually reading `validate_skill.py` and comparing against the updated docs. Update the regex patterns in `sync_and_diff.py` if needed.

### Doc field extraction returned empty

The script parses markdown tables from synced docs to extract field names. If the table format changes, extraction may fail.

**Symptoms**: `doc_fields.skills_frontmatter_fields` or `doc_fields.hook_events` is empty, with errors in `doc_fields.extraction_errors`.

**Fix**: Read the synced doc directly and check if the table format changed. Update the regex patterns in `sync_and_diff.py` if the markdown structure is different.

### Dry-run mode fails to download

In dry-run mode, the script downloads docs via Python's `urllib.request` instead of the bash script. This may fail if:
- The URLs require specific headers or authentication
- Python's SSL certificates are outdated
- The server blocks Python's default user agent

**Fix**: Run without `--dry-run` to use the full bash script (which uses curl with proper headers). Or update Python's certificates:
```bash
# macOS
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Script hangs or times out

The sync script has a 30-second timeout per file. The Python wrapper has a 300-second total timeout.

**Fix**: Check if `code.claude.com` is accessible from your network. The script will time out gracefully and report failures.

## Getting Help

If the impact analysis produces unexpected results:
1. Check the raw JSON output for errors in `extraction_errors` fields
2. Manually read the changed synced docs to verify what actually changed
3. Compare the `validator_constants` against `doc_fields` manually
