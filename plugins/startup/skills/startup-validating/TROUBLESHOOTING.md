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

### Resuming a paused pipeline

**Cause**: You chose PAUSE at a decision gate and want to continue later.
**Fix**: Use `/startup-validate --from <next-stage> --name <slug>`. The orchestrator will auto-load `pipeline-state.json` from the output directory with your previous scores and settings. If the state file is missing but stage reports exist on disk, the pipeline will still work — it just won't have the saved scores context.

### "Report lacks specific data" warning

**Cause**: The orchestrator verification step found that a stage report contains few specific data points (numbers, dates, named entities).
**Fix**: This is a quality warning, not an error. Consider re-running the stage with `--deep` mode for more thorough research, or check that the EXA deep-research skill is properly configured.

### "No external sources consulted" warning

**Cause**: The orchestrator found that the stage report's Sources section indicates no external URLs were consulted via deep-research.
**Fix**: This means the analysis may rely on stale training data. Ensure the core plugin is installed and the EXA MCP server is configured. Re-running the stage should trigger deep-research with real-time data.

### Agent errors or timeouts

**Cause**: Complex ideas with multiple presets may produce large context payloads.
**Fix**: Try running with fewer presets, or use `--stage N` to run one stage at a time. If a specific stage consistently fails, check the agent file for issues.
