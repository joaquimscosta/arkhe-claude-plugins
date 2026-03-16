# Examples: Sync Docs

## Example 1: No Changes

All documentation is up to date — no upstream changes detected.

```
=== Documentation Sync Impact Report ===

## Sync Summary
| File                 | Status    | +Lines | -Lines |
|----------------------|-----------|--------|--------|
| SUBAGENTS.md         | unchanged |      0 |      0 |
| PLUGINS.md           | unchanged |      0 |      0 |
| HOOKS.md             | unchanged |      0 |      0 |
| SKILLS.md            | unchanged |      0 |      0 |
| SETTINGS.md          | unchanged |      0 |      0 |
| MCP.md               | unchanged |      0 |      0 |
| PLUGINS_REFERENCE.md | unchanged |      0 |      0 |
| BEST_PRACTICES.md    | unchanged |      0 |      0 |

All documentation is up to date. No impacts detected.
```

## Example 2: New Frontmatter Field Added (CRITICAL)

Anthropic adds a new `isolation` frontmatter field to SKILLS.md.

```
=== Documentation Sync Impact Report ===

## Sync Summary
| File                 | Status    | +Lines | -Lines | New Sections |
|----------------------|-----------|--------|--------|--------------|
| SKILLS.md            | changed   |     12 |      0 | ### isolation |
| HOOKS.md             | unchanged |      0 |      0 |              |
| ...                  | unchanged |      0 |      0 |              |

## CRITICAL: Skill Validator Updates Required

### 1. New frontmatter field: `isolation`
- **Source**: SKILLS.md now documents `isolation` field (line 201)
- **Impact**: Validator will flag `isolation` as "Unknown frontmatter key" (FM009)
- **Fix**: Add `'isolation'` to `ALLOWED_FRONTMATTER_KEYS` in
  `.claude/skills/skill-validator/scripts/validate_skill.py` (~line 151)
- **Current value**:
  ```python
  ALLOWED_FRONTMATTER_KEYS = {
      'name', 'description', 'license', 'allowed-tools', 'metadata',
      'model', 'context', 'agent', 'hooks', 'user-invocable',
      'disable-model-invocation', 'argument-hint',
      'maxTurns', 'mcpServers', 'memory', 'skills'
  }
  ```
- **Recommended**:
  ```python
  ALLOWED_FRONTMATTER_KEYS = {
      'name', 'description', 'license', 'allowed-tools', 'metadata',
      'model', 'context', 'agent', 'hooks', 'user-invocable',
      'disable-model-invocation', 'argument-hint',
      'maxTurns', 'mcpServers', 'memory', 'skills', 'isolation'
  }
  ```

## WARNING: Project Documentation Stale

### 1. CLAUDE.md — Plugin Component Guidelines
- The YAML frontmatter reference in "Skill Files" section does not mention `isolation`
- **Fix**: Add `isolation` to the frontmatter field list

### 2. docs/SKILL_DEVELOPMENT_BEST_PRACTICES.md
- The frontmatter reference does not include the new field
- **Fix**: Add documentation for the `isolation` field

## INFO: New Capabilities Available

- The `isolation` field allows skills to run in isolated worktree contexts
- No plugins currently use this field — consider adopting for skills that
  modify files destructively
```

## Example 3: New Hook Event Added (CRITICAL)

Anthropic adds `WorktreeCreate` and `WorktreeRemove` hook events.

```
=== Documentation Sync Impact Report ===

## Sync Summary
| File     | Status  | +Lines | -Lines | New Sections                       |
|----------|---------|--------|--------|------------------------------------|
| HOOKS.md | changed |     24 |      2 | ### WorktreeCreate, WorktreeRemove |

## CRITICAL: Skill Validator Updates Required

### 1. New hook events: `WorktreeCreate`, `WorktreeRemove`
- **Source**: HOOKS.md hook events table (lines 42-43)
- **Impact**: Validator will flag these as "Unknown hook event" (HK001)
- **Fix**: Add to `VALID_HOOK_EVENTS` in `validate_skill.py` (~line 1021)
- **Recommended**:
  ```python
  VALID_HOOK_EVENTS = {
      'PreToolUse', 'PostToolUse', 'Stop',
      'SessionStart', 'UserPromptSubmit', 'PermissionRequest',
      'PostToolUseFailure', 'Notification', 'SubagentStart',
      'SubagentStop', 'TeammateIdle', 'TaskCompleted',
      'PreCompact', 'SessionEnd', 'ConfigChange',
      'WorktreeCreate', 'WorktreeRemove',
  }
  ```

## WARNING: Plugin Components Affected

No plugins currently use hook events that were modified.

## INFO: New Capabilities Available

- `WorktreeCreate` fires when a worktree is created via `--worktree` or `isolation: "worktree"`
- `WorktreeRemove` fires when a worktree is removed at session exit or subagent finish
- Consider using these in plugins that need to set up/tear down worktree-specific state
```

## Example 4: Dry Run Mode

```bash
$ scripts/sync_and_diff.py --dry-run
Dry run: downloading to memory without overwriting...
```

Output is identical JSON format but with `"dry_run": true` and no files are overwritten locally. Use this to preview what would change before committing to the sync.
