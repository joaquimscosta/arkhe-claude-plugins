# Claude Setup Troubleshooting

## WebFetch Fails

**Symptom**: Cannot fetch the Claude Code Guide from GitHub.

**Cause**: Network restrictions, GitHub rate limiting, or URL change.

**Fix**: The skill proceeds with LLM knowledge only. All setup categories still work — the guide just provides additional context. If you need the latest guide content, read it locally:
```
docs/CLAUDE_CODE_GUIDE.md
```

---

## Permission Denied on ~/.claude/

**Symptom**: Cannot create files in `~/.claude/` directory.

**Cause**: Directory permissions or ownership issues.

**Fix**:
```bash
# Check ownership
ls -la ~/.claude/

# Fix permissions if needed
chmod 755 ~/.claude/
```

---

## MCP Server Install Fails

**Symptom**: `claude mcp add` command fails.

**Cause**: Node.js or npx not installed, or package not found.

**Fix**:
1. Verify Node.js is installed: `node --version` (requires v18+)
2. Verify npx is available: `npx --version`
3. Try installing the server manually with the full command from the guide
4. For Python-based servers (Docling), verify `uvx` is available

---

## Settings.json Merge Conflict

**Symptom**: Existing settings get overwritten or corrupted.

**Cause**: The skill read/write cycle encountered malformed JSON.

**Fix**:
1. Check `~/.claude/settings.json` for syntax errors:
   ```bash
   python3 -m json.tool ~/.claude/settings.json
   ```
2. If corrupted, restore from backup or recreate manually
3. Re-run `/devtools:claude-setup` for the affected category

---

## Detection Script Errors

**Symptom**: `detect_setup.py` fails or returns unexpected output.

**Cause**: Python version too old or permission issues.

**Fix**:
1. Verify Python 3.8+: `python3 --version`
2. Run manually to see errors:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/detect_setup.py
   ```
3. The skill can proceed without detection — it will ask about everything instead of auto-detecting.

---

## Hooks Not Triggering

**Symptom**: Block-secrets hook is configured but doesn't prevent file access.

**Cause**: Hook script not executable, wrong path, or settings.json not in the right location.

**Fix**:
1. Verify script is executable: `ls -la ~/.claude/hooks/block-secrets.py`
2. Verify settings.json is at `~/.claude/settings.json` (not project-level)
3. Check the hook command path matches the actual file location
4. Test manually:
   ```bash
   echo '{"tool_input":{"file_path":".env"}}' | python3 ~/.claude/hooks/block-secrets.py
   ```
   Should exit with code 2.

---

## Re-running Setup

The skill is designed for incremental updates. Running `/devtools:claude-setup` again will:
- Detect what is already configured
- Skip completed items
- Offer to add new items or modify existing ones
- Never overwrite without asking
