# Claude Setup Examples

## Example 1: Fresh Environment

A developer with no existing Claude Code configuration runs `/claude-setup` for the first time.

### Detection Output

```json
{
  "global": {
    "claude_md": {"exists": false},
    "settings_json": {"exists": false},
    "keybindings_json": {"exists": false},
    "hooks_dir": {"exists": false},
    "agents_dir": {"exists": false}
  },
  "project": {
    "claude_md": {"exists": false},
    "claude_dir": {"exists": false, "has_skills": false, "has_agents": false, "has_commands": false},
    "env_example": {"exists": false},
    "gitignore": {"exists": true, "has_env_rule": false},
    "src_dir": {"exists": true},
    "tests_dir": {"exists": false},
    "docs_dir": {"exists": false},
    "scripts_dir": {"exists": false}
  }
}
```

### Interaction Flow

1. **Category selection**: User selects all 7 categories (everything shows "not configured")

2. **Global CLAUDE.md**: User selects all 3 security rules, provides GitHub username "jdoe", chooses HTTPS, provides git identity

3. **Project Scaffolding**: User selects `.env.example`, updates `.gitignore` (add .env rule), `CLAUDE.md`, `.claude/` dirs, `tests/`, `docs/`, `scripts/` (skips `src/` — already exists)

4. **MCP Servers**: User selects Context7, Sequential Thinking (global scope)

5. **Hooks**: User selects block-secrets hook only

6. **Custom Agents**: User selects code-reviewer (personal scope)

7. **Keybindings**: User selects all 4 recommended shortcuts

8. **Settings**: English, background tasks enabled

9. **Confirmation**: 12 creates, 2 installs, 1 settings update. User confirms.

10. **Post-setup**: All items show as completed.

---

## Example 2: Partial Setup

A developer who already has Global CLAUDE.md and some MCP servers runs `/claude-setup` to fill gaps.

### Detection Output

```json
{
  "global": {
    "claude_md": {"exists": true, "size_bytes": 856},
    "settings_json": {"exists": true, "has_hooks": false},
    "keybindings_json": {"exists": false},
    "hooks_dir": {"exists": false},
    "agents_dir": {"exists": true, "count": 1}
  },
  "project": {
    "claude_md": {"exists": true},
    "claude_dir": {"exists": true, "has_skills": true, "has_agents": false, "has_commands": true},
    "env_example": {"exists": true},
    "gitignore": {"exists": true, "has_env_rule": true},
    "src_dir": {"exists": true},
    "tests_dir": {"exists": true},
    "docs_dir": {"exists": true},
    "scripts_dir": {"exists": true}
  }
}
```

### Interaction Flow

1. **Category selection**: Shows status indicators:
   - Global CLAUDE.md — configured
   - Project Scaffolding — configured
   - MCP Servers — partially configured (2 of 3 core servers)
   - Hooks — not configured
   - Custom Agents — partially configured (1 agent)
   - Keybindings — not configured
   - Settings — partially configured

   User selects: Hooks, Keybindings, MCP Servers

2. **MCP Servers**: Only shows servers not yet installed. User adds Sequential Thinking.

3. **Hooks**: User selects block-secrets hook.

4. **Keybindings**: User selects 2 of 4 shortcuts.

5. **Confirmation**: 3 creates, 1 install, 1 settings update. User confirms.

---

## Example 3: Single Category

A developer runs `/claude-setup hooks` to only configure hooks.

### Interaction Flow

1. **Detection runs** — focuses on hooks-related state

2. **Skips category selection** — goes directly to Hooks category

3. **Hooks**: User selects block-secrets hook and Setup hook

4. **Confirmation**: 1 file create, 1 settings update

5. **Post-setup**: Shows hooks-only summary with next steps
