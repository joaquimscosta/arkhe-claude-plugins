# Dependabot Review: Detailed Workflow

This document provides a detailed step-by-step breakdown of the Dependabot PR triage and merge process.

For quick start instructions, see [SKILL.md](SKILL.md).

## Overview

The review follows 5 phases:

1. **Discovery** — Fetch PRs, parse metadata, detect ecosystems
2. **Classification** — Apply risk matrix to each PR
3. **Presentation** — Structured triage report
4. **Action** — Merge, rebase, or skip per user choice
5. **Summary** — Report actions taken

---

## Phase 1: Discovery

### Fetching PRs

Use `gh pr list --author "app/dependabot"` to get all open Dependabot PRs. The key JSON fields:

| Field | Purpose |
|-------|---------|
| `number` | PR number for subsequent commands |
| `title` | Parse package name, old/new versions |
| `labels` | Check for `security` label |
| `headRefName` | Parse ecosystem: `dependabot/{ecosystem}/{package}` |
| `baseRefName` | Current target branch |
| `mergeable` | `MERGEABLE`, `CONFLICTING`, or `UNKNOWN` |
| `statusCheckRollup` | Array of CI check results |
| `createdAt` | Age of the PR (older = more likely to conflict) |

### Parsing Version Info

**Single package PRs** — title format:
```
build(deps): bump <package> from <old> to <new> in <path>
build(deps-dev): bump <package> from <old> to <new> in <path>
```

The `deps-dev` prefix indicates a development dependency.

**Grouped PRs** — title format:
```
build(deps): bump the <group> group across N directory with M updates
```

For grouped PRs, parse the markdown table in the PR body:
```markdown
| Package | From | To |
| --- | --- | --- |
| [package-name](url) | `1.0.0` | `2.0.0` |
```

### Detecting Ecosystems

Parse from `headRefName`:
- `dependabot/npm_and_yarn/...` → npm/yarn
- `dependabot/gradle/...` → Gradle/JVM
- `dependabot/github_actions/...` → GitHub Actions
- `dependabot/terraform/...` → Terraform
- `dependabot/docker/...` → Docker
- `dependabot/pip/...` → Python pip

### Files Changed Analysis

Run `gh pr diff <number> --name-only` per PR. Key patterns:

- **Lockfile only**: `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `gradle.lockfile`, `Cargo.lock` — lowest risk
- **Manifest + lockfile**: `package.json` + lockfile — normal dependency update
- **Source code**: `.ts`, `.kt`, `.java`, `.py` files changed — unusual for Dependabot, flag for review
- **Workflow files**: `.github/workflows/*.yml` — GitHub Actions updates

---

## Phase 2: Classification

### Risk Matrix

| Semver | dev dependency | prod dependency | indirect/lockfile-only |
|--------|---------------|-----------------|----------------------|
| patch | SAFE | SAFE | SAFE |
| minor | SAFE (if known-safe pattern) | REVIEW | SAFE |
| minor | REVIEW (if framework) | REVIEW | SAFE |
| major | HUMAN REVIEW | HUMAN REVIEW | HUMAN REVIEW |

### Override Rules

These override the standard matrix:

1. **Security label** → PR stays in its normal tier but gets an urgency callout at the top of the report
2. **CI failing** → BLOCKED (never merge)
3. **Merge conflict** → BLOCKED (suggest rebase)
4. **Lockfile-only** → SAFE (regardless of semver, since the actual dependency version is controlled by the manifest)
5. **Grouped PR with any major** → HUMAN REVIEW (entire PR contaminated)

### Known-Safe Packages

These packages are safe to merge at `minor` level:
- Type definitions: `@types/*`
- Linting: `eslint`, `eslint-*`, `prettier`, `@typescript-eslint/*`, `ktlint`
- Testing: `@testing-library/*`, `@playwright/test`, `vitest`, `jest`, `mockito-*`
- CI: `actions/*`, `docker/*`, `hashicorp/setup-*`, `aquasecurity/trivy-action`

### Framework Watchlist

Always flag for review even at `minor`:
- Frontend: `next`, `react`, `react-dom`, `svelte`, `vue`, `angular`, `framer-motion`
- Backend: `spring-boot`, `kotlin`, `gradle`, `quarkus`
- Data: `supabase-js`, `@supabase/*`, `prisma`, `drizzle-orm`
- Maps: `mapbox-gl`, `react-map-gl`

---

## Phase 3: Presentation

### Report Structure

Present PRs grouped by tier with the most actionable information visible:

1. **SAFE TO MERGE** — ready to merge now, one command away
2. **REVIEW RECOMMENDED** — likely fine but deserves a glance
3. **REQUIRES HUMAN REVIEW** — major bumps, breaking changes possible
4. **BLOCKED** — can't merge until CI/conflicts resolved

Within each tier, sort by:
1. Security PRs first
2. Then by age (oldest first — most likely to accumulate conflicts)

### CI Failure Context

When presenting BLOCKED PRs with CI failures, include diagnostic notes:

- If only lockfile changed: "CI failure is pre-existing — lockfile changes cannot cause lint/type/build failures"
- If error mentions env vars: "Dependabot PRs lack access to repo secrets — this is expected"
- If same check fails on base branch: "Same CI failure exists on base branch — not caused by this PR"

---

## Phase 4: Action

### Merge Flow

1. Ask user for target branch (always)
2. Retarget PRs if needed (`gh pr edit --base`)
3. Approve each PR (`gh pr review --approve`)
4. Merge with squash strategy (`gh pr merge --squash`)
5. Handle merge method failures gracefully (try squash → merge → rebase)

### Rebase Flow

For conflicted PRs:
```bash
gh pr comment <number> --body "@dependabot rebase"
```

This tells Dependabot to regenerate the PR against the current base. The PR will update within a few minutes.

### Skip Flow

For REVIEW RECOMMENDED and HUMAN REVIEW tiers, present the recommendation but take no action unless explicitly asked.

---

## Phase 5: Summary

Report all actions taken in a structured format:
- PRs merged (with numbers and package names)
- PRs rebased (with numbers)
- PRs skipped (with reasons)
- PRs still requiring attention
