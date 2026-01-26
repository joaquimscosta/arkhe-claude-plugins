# SDLC Develop Troubleshooting

Common issues and solutions when using the `/develop` command.

---

## Configuration Issues

### No `.arkhe.yaml` found

**Symptom:** First run prompts for configuration

**Solution:** Normal behavior - choose your preferences or accept defaults. Config will be saved.

### Spec directory doesn't exist

**Symptom:** Error when saving spec files

**Solution:** The skill auto-creates the configured spec directory on first use. If you have a custom `specs_dir` in `.arkhe.yaml`, ensure the parent directory exists.

---

## Mode Detection Issues

### Resume mode not detecting existing plan

**Symptom:** `/develop @path/to/spec/` starts fresh instead of resuming

**Solution:** Ensure path contains `plan.md`. Check exact path - it should point to the spec directory, not the plan file:
```bash
# Correct
/develop @arkhe/specs/01-feature/

# Incorrect
/develop @arkhe/specs/01-feature/plan.md
```

### Plan-only mode ignored

**Symptom:** `--plan-only` flag doesn't stop after Phase 2

**Solution:** Ensure flag is after the feature description:
```bash
# Correct
/develop add feature --plan-only

# Incorrect
/develop --plan-only add feature
```

---

## Phase Execution Issues

### Phase 0 skipping existing analysis

**Symptom:** No REUSE/ENHANCE/CREATE classifications

**Solution:** Phase 0c is mandatory. If it's being skipped, ensure the gating step (0a) returned PROCEED. Check if code-explorer agent is available.

### Architecture agents not running in parallel

**Symptom:** Only one architecture option presented

**Solution:** Verify:
- code-architect agent is available
- Sufficient context for multiple approaches
- No `--auto` mode (which may consolidate)

### Validation not running with `--validate`

**Symptom:** No opus-level validation in Phase 4

**Solution:** `--validate` enables deep validation. Ensure flag is included:
```bash
/develop add feature --validate
```

---

## Template Generation Issues

### Templates not found

**Symptom:** Error when generating spec files

**Solution:** Templates should be at `plugins/core/skills/sdlc-develop/templates/`. Verify plugin installation:
```bash
/plugin uninstall core@arkhe-claude-plugins
/plugin install core@arkhe-claude-plugins
```

### Wrong NN prefix generated

**Symptom:** Spec directory has unexpected number prefix

**Solution:** The skill auto-increments based on highest existing prefix in the configured spec directory. Check for gaps in numbering or manual directories.

---

## Checkpoint Issues

### Checkpoints not appearing

**Symptom:** No user prompts between phases

**Solution:** You're likely in `--auto` mode. Run without the flag for interactive checkpoints:
```bash
# Interactive (with checkpoints)
/develop add feature

# Autonomous (no checkpoints)
/develop add feature --auto
```

### Checkpoint stuck

**Symptom:** Phase doesn't proceed after approval

**Solution:** Respond clearly with "yes", "proceed", or "continue". Ambiguous responses may trigger clarification.

---

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| "Request not actionable" | Phase 0a gating failed | Provide clearer feature description |
| "No existing implementations" | Phase 0c found nothing | Normal for greenfield features |
| "Plan.md not found" | Resume mode path incorrect | Verify path points to spec directory |
| "Template not found" | Plugin installation issue | Reinstall plugin |

---

## Getting Help

If issues persist:
1. Check the [EXAMPLES.md](EXAMPLES.md) for correct usage patterns
2. Review [SKILL.md](SKILL.md) for mode detection logic
3. Use `/debug` to analyze specific errors
