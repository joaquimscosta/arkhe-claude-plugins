# Troubleshooting Guide

Common issues and solutions for Arkhe Claude Plugins.

## Plugin Installation Issues

### Plugins Not Showing Up

**Symptom:** After installation, plugins don't appear in `/plugin` list.

**Solutions:**
1. Restart Claude Code after installation
2. Verify marketplace is added: `/plugin marketplace list`
3. Check for typos in plugin names
4. Ensure repository path is correct

```bash
# Verify marketplace
/plugin marketplace list

# Re-add marketplace if needed
/plugin marketplace add ./arkhe-claude-plugins

# Reinstall plugin
/plugin install plugin-name@arkhe-claude-plugins
```

### "Plugin not found" Error

**Symptom:** Installation fails with "plugin not found" message.

**Solutions:**
1. Check the plugin name in `marketplace.json`
2. Ensure you're in the correct directory
3. Verify the plugin directory exists

```bash
# List available plugins
ls -la arkhe-claude-plugins/
```

---

## Command Issues

### Commands Not Working

**Symptom:** Slash commands don't execute or show errors.

**Solutions:**
1. Check command name with `/help`
2. Verify plugin is installed and enabled: `/plugin`
3. Try namespaced invocation if conflicts exist

```bash
# Check all available commands
/help

# Use namespaced version
/git:commit
/specprep:specify
```

### Command Conflicts

**Symptom:** Wrong command executes when multiple plugins have similar commands.

**Solution:** Use namespaced invocation:

```bash
# Instead of
/specify

# Use namespaced version
/specprep:specify        # For Spec Kit preparation
/design-intent:feature   # For Design Intent features
```

---

## Agent Issues

### Agents Not Appearing

**Symptom:** Agents don't show in `/agents` list.

**Solutions:**
1. Verify plugin is installed: `/plugin`
2. Check that plugin is enabled (not disabled)
3. Restart Claude Code

```bash
# Check installed plugins
/plugin

# Re-enable if disabled
/plugin enable plugin-name@arkhe-claude-plugins
```

### Agent Not Responding as Expected

**Symptom:** Agent behavior doesn't match documentation.

**Solutions:**
1. Provide clear, specific prompts
2. Include relevant context (file paths, error messages)
3. Try invoking directly via `/agents` menu

---

## Skill Issues

### Skills Not Activating

**Symptom:** Auto-invoke skills don't trigger on relevant keywords.

**Solutions:**
1. Use explicit trigger keywords in your prompt
2. Verify the plugin is installed
3. Check skill description for trigger phrases

**Skill Triggers:**
- **mermaid**: "diagram", "flowchart", "sequence diagram", "ERD"
- **generating-changelog**: Edit CHANGELOG.md, mention "changelog", "release notes"
- **design-intent-specialist**: "implement from Figma", "screenshot", visual references
- **scripting-bash**: "bash script", "shell script", "automation script"

### Skills Producing Incorrect Output

**Symptom:** Skill output doesn't match expectations.

**Solutions:**
1. Be specific about output format requirements
2. Provide examples of desired output
3. Use progressive disclosure - ask for WORKFLOW.md if needed

---

## MCP Server Issues

### Playwright MCP Issues (for design-review)

**Symptom:** `/design` command or `design-review` agent fails.

**Solutions:**
1. Verify Playwright MCP server is installed
2. Check `.mcp.json` configuration in your project
3. Ensure preview environment is accessible
4. Review MCP server logs for errors

```bash
# Check MCP configuration
cat .mcp.json

# Verify Playwright is installed
npx playwright --version
```

### GitHub CLI Issues (for git plugin)

**Symptom:** PR commands fail with authentication errors.

**Solutions:**
1. Verify GitHub CLI is installed: `gh --version`
2. Authenticate: `gh auth login`
3. Check authentication status: `gh auth status`

```bash
# Install GitHub CLI (macOS)
brew install gh

# Authenticate
gh auth login

# Verify authentication
gh auth status
```

---

## Performance Issues

### Slow Plugin Response

**Symptom:** Commands or agents take too long to respond.

**Solutions:**
1. Reduce context size by focusing prompts
2. Use specific file paths instead of broad searches
3. Consider using haiku model for simple tasks

### High Token Usage

**Symptom:** Conversations consume tokens quickly.

**Solutions:**
1. Use progressive disclosure - load only what you need
2. Be specific about required information
3. Close and restart conversations periodically

---

## Configuration Issues

### CLAUDE.md Not Being Used

**Symptom:** Project-specific instructions aren't followed.

**Solutions:**
1. Verify CLAUDE.md exists in repository root
2. Check file permissions
3. Ensure content follows expected format

### Plugin Not Following Custom Instructions

**Symptom:** Plugin behavior doesn't match CLAUDE.md guidance.

**Solutions:**
1. Plugins may have their own system prompts
2. Be explicit about requirements in your prompts
3. Consider editing plugin files directly for customization

---

## Getting Help

If you can't resolve an issue:

1. **Check plugin README:** Each plugin has detailed documentation
2. **Review docs/ directory:** Contains synced Claude documentation
3. **Search existing issues:** Check if others have reported similar problems
4. **Open an issue:** Provide:
   - Plugin name and version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs

---

## Quick Reference

| Issue | First Step |
|-------|------------|
| Plugin not found | Check marketplace: `/plugin marketplace list` |
| Command not working | Check help: `/help` |
| Agent missing | Check plugins: `/plugin` |
| Skill not triggering | Use explicit trigger keywords |
| MCP error | Check configuration: `cat .mcp.json` |
| GitHub CLI error | Authenticate: `gh auth login` |
