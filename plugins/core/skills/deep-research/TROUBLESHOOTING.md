# Troubleshooting Deep Research

Common issues and solutions when using the deep research skill.

## Cache Issues

### Problem: Cache directory doesn't exist
**Symptoms:** "Cache entry not found" even after researching.

**Solution:** The cache is created on first use at `~/.claude/plugins/research/`. If it doesn't exist, ensure the agent has write permissions to your home directory. You can manually create it:
```bash
mkdir -p ~/.claude/plugins/research/entries
echo "{}" > ~/.claude/plugins/research/index.json
```

### Problem: Research not found after researching
**Symptoms:** `/research list` shows empty, but research was conducted.

**Solution:** Check if the research was successful. The agent needs to complete the full flow including cache write. If interrupted, re-run the research command.

### Problem: Cache entries showing as expired immediately
**Symptoms:** Research expires right after being cached.

**Solution:** Check system clock. The TTL calculation uses UTC timestamps. If your system clock is significantly wrong, entries may appear expired.

---

## EXA API Issues

### Problem: EXA tools not available
**Symptoms:** Agent reports MCP tools not found or unavailable.

**Solution:**
1. Verify EXA MCP server is configured in your Claude Code settings
2. Check that the EXA API key is valid
3. Restart Claude Code to reload MCP connections

### Problem: Research returns empty or poor results
**Symptoms:** Research completes but content is minimal or irrelevant.

**Solutions:**
1. Try more specific search terms
2. Use quotes for exact phrases: `/research "React Server Components"`
3. Add context words: `/research domain-driven design best practices`

### Problem: Rate limiting or API errors
**Symptoms:** Research fails with API errors.

**Solution:** EXA has rate limits. If you hit them:
1. Wait a few minutes before retrying
2. Check your EXA account quota
3. Use cached research when available to reduce API calls

---

## Promotion Issues

### Problem: Promote fails with "not found"
**Symptoms:** `/research promote <slug>` says research not cached.

**Solutions:**
1. Run `/research list` to see available slugs
2. Check slug spelling matches exactly (lowercase, hyphenated)
3. Run `/research <topic>` first to cache it

### Problem: Team notes lost after refresh
**Symptoms:** `<!-- TEAM-NOTES -->` section is empty after refresh.

**Solution:** This shouldn't happen - the refresh flow preserves team notes. If it does:
1. Check git history for the previous version
2. Verify the file had proper `<!-- TEAM-NOTES: Start -->` and `<!-- TEAM-NOTES: End -->` markers
3. Report as a bug if markers were correct

### Problem: Promoted file not appearing in README
**Symptoms:** File exists in `docs/research/` but not in README index.

**Solution:** Run the index generator manually:
```bash
python plugins/core/skills/deep-research/scripts/index_generator.py --docs
```

---

## Slug/Alias Issues

### Problem: Different topics colliding to same slug
**Symptoms:** Researching "ES6" overwrites "Event Sourcing" (both normalize to similar slugs).

**Solution:** Use more specific topic names:
- "ES6 JavaScript features" → `es6-javascript-features`
- "Event Sourcing pattern" → `event-sourcing-pattern`

### Problem: Alias not resolving
**Symptoms:** `/research DDD` doesn't find cached "domain-driven-design".

**Solution:** Aliases must be explicitly added during research. To add an alias:
1. Edit the cached `metadata.json` file
2. Add to the `aliases` array
3. The next lookup will resolve it

---

## Script Execution Issues

### Problem: Scripts fail with permission denied
**Symptoms:** Python scripts can't execute.

**Solution:** Make scripts executable:
```bash
chmod +x plugins/core/skills/deep-research/scripts/*.py
```

### Problem: Scripts fail with import errors
**Symptoms:** ModuleNotFoundError or similar.

**Solution:** Scripts use standard library only. Verify Python 3.8+ is installed:
```bash
python3 --version
```

---

## Getting Help

If issues persist:
1. Check `/research list` output for diagnostic info
2. Review cache files at `~/.claude/plugins/research/`
3. Check for JSON parsing errors in `index.json`
4. Report persistent issues with steps to reproduce
