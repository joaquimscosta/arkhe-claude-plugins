---
description: Scaffold or migrate a repo onto release-please (config, manifest, release workflow) with optional tag-keyed deploy/publish templates
---

# Release-Please Setup

Invoke the `release-please-setup` skill to configure [release-please](https://github.com/googleapis/release-please) for the current repository.

Arguments (parse from user input, all optional):
- `--migrate` — migrate an existing manual-tag repo (seed manifest from current versions) instead of greenfield.
- `--single` — force single-package mode (skip monorepo exclude-paths matrix).
- `--globs <glob[,glob]>` — package directory globs to scan (default: `packages/*`, `backend/*`, `frontend/*`, and repo root).
- `--templates <name[,name]>` — deploy/publish templates to copy: `docker-matrix`, `frontend-host`, `npm-oidc`, `release-asset`, `fly`, `generic`.
- `--dry-run` — print generated files without writing.

Follow `SKILL.md`. Always run the generator in `--dry-run` first and show the user the diff before writing.
