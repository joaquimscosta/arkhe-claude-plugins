# devtools

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Gemini equivalents. Install the `core` extension if you have not already.

@../../plugins/core/skills/using-arkhe-skills/SKILL.md

## Skills

- **code-env-setup** — Interactive Claude Code environment setup wizard. Detects existing configuration, guides through best-practice setup for Global CLAUDE.md, project scaffolding, MCP servers, hooks, custom agents, keybindings, and settings. Use when user runs /devtools:code-env-setup, mentions "setup claude code", "configure claude", "claude code setup", "environment setup", or "initialize claude code".
- **quality-stack** — Scan a project to detect configured quality and testing tools across JVM (Gradle/Maven), Android (AGP/Compose/KMP), Node.js/TypeScript, and Python ecosystems. Cross-reference against research-backed recommendations and assist with setup. Auto-detects project type(s) including monorepos with mixed ecosystems. Use when user asks to "audit tooling", "recommend tools", "quality stack", "what tools am I missing", "setup eslint", "setup detekt", "add coverage", "add ruff", "configure CI quality pipeline", "scan project tools", "tooling audit", "android tooling", "android quality", "compose testing", "kmp testing", or "screenshot testing".
- **sops-add-key** — Add a new machine's age public key to .sops.yaml and re-encrypt all files. Use for multi-machine setups. Use when user mentions "add key", "add machine", "sops add key", "new machine", "authorize machine", "share key", "add public key", "multi machine sops".
- **sops-decrypt** — Decrypt SOPS-encrypted YAML files back to .env format. Finds *.enc.yaml files, decrypts, and converts YAML back to dotenv. Use when user mentions "decrypt env", "sops decrypt", "decrypt secrets", "restore env", "decrypt .env", "restore secrets", "decrypt environment files".
- **sops-encrypt** — Encrypt .env files using SOPS + age. Converts dotenv to YAML format (avoids SOPS bug #1435), then encrypts. Auto-detects unencrypted .env files. Use when user mentions "encrypt env", "sops encrypt", "encrypt secrets", "encrypt .env", "encrypt environment", "re-encrypt", "update encrypted".
- **sops-setup** — Set up SOPS + age encryption for sharing .env files securely across machines. Detects existing state, installs tools, generates age keys, creates .sops.yaml, and encrypts .env files as YAML (avoids SOPS dotenv bug #1435). Use when user mentions "sops setup", "encrypt env", "share secrets", "secure env files", "sops age setup", "env encryption", "setup sops", "share env across machines".
- **taskfile-setup** — Install Taskfile (task) and scaffold or audit Taskfile.yml configurations with ecosystem-aware templates. Auto-detects Node.js/pnpm, JVM/Gradle, Python/uv, Docker, and recommends single-file or multi-file (includes) patterns based on project complexity. Use when user runs /devtools:taskfile-setup, mentions "taskfile setup", "setup task runner", "audit taskfile", "scaffold taskfile", "add taskfile", "taskfile.yml", or "developer tasks".

## Commands

See `commands/` directory for transpiled Gemini TOML commands.
