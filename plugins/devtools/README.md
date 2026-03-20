# devtools

Developer tooling setup and management plugin for Claude Code.

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| `sops-setup` | `/devtools:sops-setup` | Set up SOPS + age encryption for .env files |
| `sops-encrypt` | `/devtools:sops-encrypt` | Encrypt .env files |
| `sops-decrypt` | `/devtools:sops-decrypt` | Decrypt .env.encrypted files |
| `sops-add-key` | `/devtools:sops-add-key` | Add a machine's public key and re-encrypt |
| `claude-setup` | `/devtools:claude-setup` | Interactive Claude Code environment setup wizard |

## Claude Code Setup

Interactive environment setup wizard that detects existing Claude Code configuration and guides through best-practice setup for Global CLAUDE.md, project scaffolding, MCP servers, hooks, custom agents, keybindings, and settings.

Run `/devtools:claude-setup` to start the wizard, or `/devtools:claude-setup [category]` to configure a specific category (e.g., `hooks`, `mcp`).

## SOPS + age Overview

[SOPS](https://github.com/getsops/sops) (Secrets OPerationS) encrypts file values while keeping keys in plaintext for meaningful git diffs. Combined with [age](https://github.com/FiloSottile/age), it provides simple, secure encryption for sharing `.env` files across machines without external services.

### Multi-Machine Workflow

Each machine generates its own age key pair. Public keys are listed in `.sops.yaml` (committed to git). Encrypted files can be decrypted by any authorized machine. To add a new machine, run `/devtools:sops-add-key`.
