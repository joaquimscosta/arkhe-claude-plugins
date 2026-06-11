---
description: Scaffold or migrate a repo onto release-please (config, manifest, release workflow) with optional tag-keyed deploy/publish templates
---

# Release-Please Setup

Invoke the `release-please-setup` skill to configure [release-please](https://github.com/googleapis/release-please) for the current repository.

Arguments (parse from user input, all optional):
- `--migrate` — migrate an existing manual-tag repo (seed manifest from current versions) instead of greenfield.
- `--single` — force single-package mode (skip monorepo exclude-paths matrix).
- `--globs <glob[,glob]>` — package directory globs to scan (default: `packages/*`, `backend/*`, `frontend/*`, and repo root).
- `--initial <semver>` — initial version for greenfield packages (default `0.0.0`).
- `--dry-run` — print generated files without writing.

Deploy/publish templates are copied **interactively**, not via a script flag: after generating the config + manifest, copy the relevant template(s) from `skills/release-please-setup/templates/` (`fly`, `npm-oidc`, `release-asset`, `docker-matrix`, `frontend-host`, `generic`) into `.github/workflows/` and fill their placeholders. See `WORKFLOW.md` for the menu and placeholder reference.

Follow `SKILL.md`. Always run the generator in `--dry-run` first and show the user the diff before writing.
