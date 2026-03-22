# Troubleshooting: Taskfile Setup

## Installation Issues

### `brew install task` installs Taskwarrior instead of Taskfile

**Symptom**: Running `task` shows a TODO manager instead of a task runner.

**Cause**: `brew install task` installs Taskwarrior, not Taskfile.

**Fix**: Uninstall and reinstall with the correct formula:
```bash
brew uninstall task
brew install go-task
```

Verify: `task --version` should show something like `Task version: v3.x.x`.

### `task` command not found after install

**Symptom**: `command not found: task` after running install script.

**Cause**: The binary was installed to a directory not in your PATH.

**Fix**:
1. Check where it was installed: `ls ~/.local/bin/task` or `ls /usr/local/bin/task`
2. Add to PATH in your shell profile:
   ```bash
   # In ~/.zshrc or ~/.bashrc
   export PATH="$HOME/.local/bin:$PATH"
   ```
3. Restart your terminal or run `source ~/.zshrc`

### Version too old for `version: '3'`

**Symptom**: `task: Failed to parse` error when running tasks.

**Cause**: Task version 2.x does not support `version: '3'` schema.

**Fix**: Upgrade to Task 3.x:
```bash
# macOS
brew upgrade go-task

# Linux (install script)
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
```

---

## Detection Issues

### Ecosystems not detected

**Symptom**: Detector returns empty `ecosystems` array despite project files existing.

**Causes**:
- Running from wrong directory — pass explicit project root
- Deeply nested project structure (detector only checks root + one level deep)

**Fix**:
```bash
# Specify the project root explicitly
python3 ${CLAUDE_SKILL_DIR}/scripts/detect_taskfile.py /path/to/project
```

### Audit reports false positives

**TF008 (deps for sequential)**: The detector flags `deps:` usage as INFO-level. However, `deps:` is intentionally parallel in many cases (e.g., `dev:` running API + web simultaneously). This is an informational hint, not a bug.

**TF005 (missing desc)**: Internal tasks (prefixed with underscore like `_helper`) conventionally omit `desc:` to hide from `task --list`. The detector currently flags these. Skip these violations when reviewing.

**TF007 (absolute paths)**: Comments containing file paths may trigger this rule. The detector skips comment lines starting with `#`, but inline comments are not filtered.

### YAML parsing misses tasks

**Symptom**: Detector reports fewer tasks than expected.

**Cause**: The stdlib-only parser uses line-level indentation tracking. Complex YAML constructs may not be recognized:
- YAML anchors and aliases (`<<: *defaults`)
- Flow-style mappings (`{key: value}`)
- Multi-line strings with unusual indentation

**Workaround**: The audit results are best-effort. Review the full Taskfile manually for any missed tasks. The detector's primary purpose is ecosystem detection and common-pattern auditing.

---

## Scaffold Issues

### Generated Taskfile has wrong tool paths

**Symptom**: `task dev` fails because `pnpm` or `./gradlew` is not at the expected location.

**Cause**: The scaffold used default directory names that don't match your project structure.

**Fix**: Edit the `vars:` section in your Taskfile.yml:
```yaml
vars:
  API_DIR: backend          # Was: apps/api
  WEB_DIR: frontend         # Was: apps/web
```

### Include files not found

**Symptom**: `task: Taskfile "taskfiles/api.yml" not found`.

**Cause**: The included Taskfile path is relative to the root Taskfile's location.

**Fix**: Ensure paths are correct relative to the root Taskfile:
```yaml
includes:
  api:
    taskfile: ./taskfiles/api.yml    # Relative to root Taskfile
    dir: ./apps/api                  # Working directory for tasks
```

### dotenv not loading in included Taskfiles

**Symptom**: Environment variables from `.env` are not available in included Taskfile tasks.

**Cause**: This is a known Taskfile limitation — `dotenv:` declarations only work in the root Taskfile. They cannot be declared in included Taskfiles.

**Fix**: Define `dotenv:` only at the root level:
```yaml
# Root Taskfile.yml — this works
version: "3"
dotenv: [".env.local", ".env"]

includes:
  api:
    taskfile: ./taskfiles/api.yml
    # env vars from dotenv ARE available in included tasks
```

---

## Runtime Issues

### `task: command not found` in CI

**Symptom**: CI pipeline fails because `task` is not installed.

**Cause**: Task is not installed in the CI environment by default.

**Fix for GitHub Actions**:
```yaml
- name: Install Task
  uses: go-task/setup-task@v1
  with:
    version: '3.x'
```

**Fix for other CI**: Add install step:
```bash
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
```

### Tasks run multiple times

**Symptom**: A setup task runs every time even though it only needs to run once.

**Cause**: Missing `run: once` on idempotent tasks.

**Fix**: Add `run: once` to tasks that should only execute once per invocation:
```yaml
tasks:
  setup:
    run: once
    desc: Install dependencies
    cmds:
      - pnpm install
```

### Variables not available in included Taskfiles

**Symptom**: `{{.MY_VAR}}` is empty in an included Taskfile's tasks.

**Cause**: Variables from the root Taskfile don't automatically propagate to includes.

**Fix**: Pass variables explicitly:
```yaml
includes:
  api:
    taskfile: ./taskfiles/api.yml
    dir: ./apps/api
    vars:
      PROFILE: "{{.PROFILE}}"
      ENV: "{{.ENV}}"
```

Or define variables in the included Taskfile itself.
