# devtools

Developer tooling setup and management plugin for Claude Code.

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| `sops-setup` | `/devtools:sops-setup` | Set up SOPS + age encryption for .env files |
| `sops-encrypt` | `/devtools:sops-encrypt` | Encrypt .env files |
| `sops-decrypt` | `/devtools:sops-decrypt` | Decrypt .env.encrypted files |
| `sops-add-key` | `/devtools:sops-add-key` | Add a machine's public key and re-encrypt |
| `code-env-setup` | `/devtools:code-env-setup` | Interactive Claude Code environment setup wizard |
| `quality-stack` | `/devtools:quality-stack` | JVM project quality/testing tooling audit and setup |
| `taskfile-setup` | `/devtools:taskfile-setup` | Install Taskfile and scaffold/audit Taskfile.yml |
| `tilt-setup` | `/devtools:tilt-setup` | Install Tilt and scaffold/audit Tiltfile + tilt/ for local Kubernetes development |
| `browser-companion` | `arkhe-preview` CLI on PATH | Zero-dep agent↔browser live-preview server (HTTP + WebSocket + file watcher) |

## Claude Code Setup

Interactive environment setup wizard that detects existing Claude Code configuration and guides through best-practice setup for Global CLAUDE.md, project scaffolding, MCP servers, hooks, custom agents, keybindings, and settings.

Run `/devtools:code-env-setup` to start the wizard, or `/devtools:code-env-setup [category]` to configure a specific category (e.g., `hooks`, `mcp`).

## SOPS + age Overview

[SOPS](https://github.com/getsops/sops) (Secrets OPerationS) encrypts file values while keeping keys in plaintext for meaningful git diffs. Combined with [age](https://github.com/FiloSottile/age), it provides simple, secure encryption for sharing `.env` files across machines without external services.

### Multi-Machine Workflow

Each machine generates its own age key pair. Public keys are listed in `.sops.yaml` (committed to git). Encrypted files can be decrypted by any authorized machine. To add a new machine, run `/devtools:sops-add-key`.

## Taskfile Setup

Install [Taskfile](https://taskfile.dev/) and scaffold or audit `Taskfile.yml` configurations with ecosystem-aware templates. Auto-detects Node.js/pnpm, JVM/Gradle, Python/uv, Docker, and recommends single-file or multi-file patterns based on project complexity.

### Two-Phase Workflow

1. **Audit** (when Taskfile exists) — Analyze for best-practice violations (missing desc, no preconditions on deploy tasks, no dotenv config, etc.) and offer fixes
2. **Scaffold** (when no Taskfile exists) — Detect ecosystems, choose pattern (single-file or multi-file), generate Taskfile.yml with ecosystem-specific task groups

Run `/devtools:taskfile-setup` to get started.

## Tilt Setup

Install [Tilt](https://tilt.dev/) and scaffold or audit `Tiltfile` + `tilt/` configurations for local Kubernetes development. Auto-detects Java/Gradle (Spring Boot), Next.js, Python/uv, and external infrastructure; recommends single-file or modular `tilt/*.star + service-config.yaml + environments.yaml` patterns based on project complexity.

### Two-Phase Workflow

1. **Audit** (when Tiltfile exists) — Run rules `TILT001`–`TILT025` against the Tiltfile (no production safety guard, deprecated `restart_container`, missing `live_update`/`watch_settings`/`update_settings`, etc.) and offer fixes.
2. **Scaffold** (when no Tiltfile exists) — Detect ecosystems and kubectl context, choose pattern (single-file or modular), generate Tiltfile + supporting files with optional features (manual context guard, PVC persistence toggle, JDWP debug ports, monitoring/gateway scaffolds).

The skill refuses to scaffold or modify configuration when `kubectl config current-context` matches a production pattern (`arn:aws:eks:`, `gke_`, `prod`, `staging`).

Run `/devtools:tilt-setup` to get started. Reference base: `docs/research/tilt-local-kubernetes-development-setup.md`.

## Quality Stack

Scans JVM projects (Gradle/Maven) to detect configured quality and testing tools, cross-references against research-backed recommendations, and assists with setup.

### Two-Phase Workflow

1. **Recommend** — Run the scanner, fetch research docs, cross-reference, generate a prioritized report
2. **Setup** — User selects tools from the report, skill configures build files, creates config files, and verifies detection

Run `/devtools:quality-stack` to audit your project's tooling.

## Browser Companion

Zero-dependency Node.js HTTP + WebSocket server that gives any skill a live-reloading browser preview with bidirectional event capture. Watches a content directory, wraps HTML fragments in a configurable frame template, broadcasts live-reload to connected browsers, and persists browser-side click events as JSONL for the agent to read.

The skill ships a public CLI named `arkhe-preview` in `plugins/devtools/bin/`. Any plugin's skill can invoke it as a bare bash command (no need to know the devtools install path) — Claude Code adds plugin `bin/` directories to the Bash tool's PATH while the plugin is enabled.

```bash
# Start a session scoped to the current project
arkhe-preview start --project-dir "$(pwd)"
# → {"type":"server-started","url":"http://localhost:54123","screen_dir":"…/<id>/content", ...}

# Write a fragment — browser auto-reloads
echo '<h2>Hello</h2><button data-event="ok">OK</button>' > "$SCREEN_DIR/hello.html"

# Read user clicks
tail -f "$STATE_DIR/events.jsonl"

# Stop when done
arkhe-preview stop "$SESSION_DIR"
```

Two reference UI flavors ship under `skills/browser-companion/examples/`:
- `brainstorm/` — multi-choice option lists with a selection indicator bar
- `gallery/` — variant browsing in a Tailwind-styled sidebar

These are static reference docs (copy what you need), not runtime presets. See [skills/browser-companion/SKILL.md](skills/browser-companion/SKILL.md) for the full reference and [skills/browser-companion/EXAMPLES.md](skills/browser-companion/EXAMPLES.md) for end-to-end walkthroughs.

Inherits zero-dep server code from Jesse Vincent's [superpowers](https://github.com/obra/superpowers) project (MIT, 2025); see [skills/browser-companion/WORKFLOW.md > Attribution](skills/browser-companion/WORKFLOW.md#attribution).
