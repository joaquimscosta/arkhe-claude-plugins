# Startup Validation — Troubleshooting

## Common Issues

### "Preset not found" warning

**Cause**: The `--preset` name doesn't match any file in `presets/`.
**Fix**: Check available presets: `fintech`, `cape-verde`, `saas`, `marketplace`. Preset names must match the filename without `.md` extension.

### Stages produce generic analysis (no real data)

**Cause**: The deep-research skill (EXA) may not be configured or available.
**Fix**: Ensure the core plugin is installed and the EXA MCP server is configured. Without EXA, agents fall back to LLM training data which may be stale.

### "No prior stage reports found" when using --from

**Cause**: Previous stage report files don't exist in the output directory.
**Fix**: This is a warning, not an error. The agent will proceed without prior context. To provide context, run earlier stages first or place existing analysis files in the output directory.

### Deep mode is slow

**Cause**: `--deep` spawns 3 sub-agents + 1 critic per stage, multiplied by the number of stages.
**Fix**: Use `--deep` selectively with `--stage N` to deep-dive only the stages that need it. For a quick pass, use standard mode (no `--deep`).

### Decision gate doesn't appear

**Cause**: You're running in `--fast` mode.
**Fix**: Remove the `--fast` flag to enable interactive decision gates.

### Output directory already exists

**Cause**: A previous run with the same name/slug exists.
**Fix**: This is intentional — resume mode. Existing stage reports are preserved. New runs will overwrite only the stages being re-run. Use `--name` with a different slug for a fresh run.

### Agent errors or timeouts

**Cause**: Complex ideas with multiple presets may produce large context payloads.
**Fix**: Try running with fewer presets, or use `--stage N` to run one stage at a time. If a specific stage consistently fails, check the agent file for issues.
