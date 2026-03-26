---
title: "Cross-Cutting Developer Tools Evaluation"
version: "1.0.0"
status: Published
created: 2026-03-25
last_updated: 2026-03-25
---

# Cross-Cutting Developer Tools Evaluation

## A Practitioner's Guide for Polyglot Engineering Teams

> **Scope**: Language-agnostic tools that span JVM, Node.js, and Python projects
>
> This guide evaluates 15+ tools across six categories that apply regardless of the primary
> programming language your team uses. Every tool listed is free or has a meaningful free tier.
> Configurations are shown for the most common ecosystem contexts where applicable.

---

## Executive Summary

### Tool Landscape at a Glance

| Tool | Category | Version | JVM | Node.js | Python | Cost | Stars |
|------|----------|---------|-----|---------|--------|------|-------|
| **Lefthook** | Git Hooks | 2.1.4 | Yes | Yes | Yes | Free | 7.8k |
| **Husky** | Git Hooks | 9.x | No | Yes (native) | No | Free | 33k |
| **pre-commit** | Git Hooks | 4.5.1 | Via hook | Via hook | Native | Free | 15.1k |
| **commitlint** | Commit Conventions | 20.5.0 | Via CI | Yes (native) | Via CI | Free | 17k |
| **commitizen** (Python) | Commit Conventions | 4.13.9 | Via CI | Via CI | Native | Free | 3.4k |
| **commitizen** (JS) | Commit Conventions | 4.3.x | No | Native | No | Free | 10.4k |
| **conventional-changelog** | Commit Conventions | ecosystem | Yes | Yes | Yes | Free | varies |
| **.editorconfig** | Editor Config | 0.17.x | Yes | Yes | Yes | Free | N/A |
| **Renovate** | Dependency Automation | 40.x | Yes | Yes | Yes | Free | 21.1k |
| **Dependabot** | Dependency Automation | SaaS | Yes | Yes | Yes | Free | N/A |
| **Trivy** | Security Scanning | 0.69.x | Yes | Yes | Yes | Free | 34k |
| **Gitleaks** | Security Scanning | 8.30.x | Yes | Yes | Yes | Free | 24.4k |
| **Snyk** | Security Scanning | SaaS | Yes | Yes | Yes | Freemium | N/A |
| **GitHub Actions** | CI/CD Quality Gates | N/A | Yes | Yes | Yes | Freemium | N/A |
| **Codecov** | CI/CD Quality Gates | SaaS | Yes | Yes | Yes | Freemium | N/A |
| **SonarCloud** | CI/CD Quality Gates | SaaS | Yes | Yes | Yes | Freemium | N/A |

### Recommended Starting Sets

#### Solo Developer / Small Team

| Layer | Tool | Why |
|-------|------|-----|
| Git Hooks | Lefthook | Single YAML, Go binary, no Node.js dependency, parallel execution |
| Commit Conventions | commitlint + commitizen | Enforce format + interactive prompting |
| Editor Config | .editorconfig | Zero-effort cross-IDE consistency |
| Dependency Automation | Dependabot (security) + Renovate (updates) | Dependabot free for security; Renovate for broader updates |
| Security Scanning | Trivy | Free, comprehensive, single binary |
| Secrets | Gitleaks | Pre-commit hook blocks accidental secret commits |
| CI/CD | GitHub Actions + Codecov | Free tier covers most open-source or small private projects |

#### Multi-Ecosystem Monorepo

| Layer | Tool | Why |
|-------|------|-----|
| Git Hooks | Lefthook | `extends` splits config per sub-project; `root` scopes commands |
| Commit Conventions | commitlint | Enforces standard across all teams sharing the repo |
| Editor Config | .editorconfig | Language-specific sections in one file covers Java, JS, Python |
| Dependency Automation | Renovate | 90+ package managers; regex managers; grouped PRs per ecosystem |
| Security Scanning | Trivy | Scans containers, IaC, and all dependency ecosystems from one CLI |
| Secrets | Gitleaks | Baseline mode to ignore historical findings; CI and pre-commit |
| CI/CD | GitHub Actions reusable workflows + Codecov | Shared quality workflow called from each sub-project |

#### Enterprise / Compliance-Driven Team

| Layer | Tool | Why |
|-------|------|-----|
| Git Hooks | Lefthook | Binary distribution avoids npm supply chain risk; no runtime needed |
| Commit Conventions | commitlint + conventional-changelog | Full traceability from commit to release notes to JIRA |
| Editor Config | .editorconfig + IDE enforcement | Verified via CI linting in addition to IDE plugins |
| Dependency Automation | Renovate self-hosted | AGPL-3.0 self-hostable; full audit log; custom preset org governance |
| Security Scanning | Trivy + Snyk (paid) | Trivy for CI speed; Snyk for reachability analysis + fix PRs |
| Secrets | Gitleaks + GitHub Secret Scanning | Defense in depth; Gitleaks pre-commit + GitHub server-side |
| CI/CD | GitHub Actions + SonarCloud / SonarQube | Quality gates + PR decoration + compliance dashboards |
| Coverage | Codecov Pro | SAML SSO, carryforward flags, bundle analysis |

---

## 1. Git Hooks

### 1.1 Lefthook

**What**: Fast, polyglot Git hooks manager written in Go
**Site**: [lefthook.dev](https://lefthook.dev/) | **Version**: 2.1.4 (Mar 2026) | **License**: MIT
**Compat**: JVM Yes (via shell), Node.js Yes (npm package), Python Yes (pipx/pip)

#### Why It Matters

Lefthook eliminates the two most painful aspects of Git hook management: runtime startup overhead and scattered configuration. Because it is a compiled Go binary, there is no Node.js or Python process to spin up before the first hook runs. A single `lefthook.yml` at the repository root defines every hook, every command, and every file filter. On large projects the difference is measurable: parallel execution of lint + format + typecheck takes roughly half the wall-clock time of sequential Husky + lint-staged execution. In 2026, Lefthook v2 shipping priority-aware parallel jobs (`jobs` + `group` nesting) made it even better suited for teams that need specific ordering within a hook stage.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Cross-Ecosystem Support | **Strong** - npm, gem, pip, go, brew, apt, winget |
| Performance | **Strong** - Go binary, parallel by default, ~40-90ms overhead |
| Configuration | **Strong** - Single YAML; `extends` for monorepos |
| Monorepo Support | **Strong** - `root`, `glob`, and `extends` per sub-project |
| Staged-files Support | **Strong** - `{staged_files}`, `stage_fixed: true` built in |
| CI Integration | **Strong** - `LEFTHOOK=0` env var disables in CI |
| Setup Effort | **Low** - `npm install lefthook && lefthook install` |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 7.8k stars, 130 contributors, Evil Martians |

#### Quick Start

```yaml
# lefthook.yml
pre-commit:
  parallel: true
  commands:
    lint:
      glob: "*.{ts,tsx,js}"
      run: npx eslint {staged_files} --fix
      stage_fixed: true
    format:
      glob: "*.{ts,tsx,json,md}"
      run: npx prettier --write {staged_files}
      stage_fixed: true
    spotless:
      glob: "*.{java,kt}"
      run: ./gradlew spotlessApply
      stage_fixed: true

commit-msg:
  commands:
    commitlint:
      run: npx commitlint --edit {1}
```

```bash
# Install (choose your package manager)
npm install lefthook --save-dev
# or: brew install lefthook
# or: pipx install lefthook
# or: go install github.com/evilmartians/lefthook/v2@latest

lefthook install   # Writes .git/hooks/ entries
```

**Monorepo pattern (extends):**
```yaml
# root lefthook.yml
extends:
  - packages/frontend/lefthook.yml
  - packages/backend/lefthook.yml

# packages/frontend/lefthook.yml
pre-commit:
  commands:
    frontend-lint:
      root: "packages/frontend/"
      glob: "*.{ts,tsx}"
      run: yarn eslint {staged_files}
```

#### Key Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `parallel: true` | Run all commands in a hook concurrently | `false` |
| `stage_fixed: true` | Re-stage files after auto-fix | `false` |
| `glob` | Only run command when matching files are staged | None (all files) |
| `root` | Execute command scoped to a sub-directory | Repo root |
| `skip: [merge, rebase]` | Skip hook in specific Git operations | None |
| `extends` | Merge additional YAML files into config | None |
| `min_version` | Assert minimum Lefthook version | None |
| `assert_lefthook_installed` | Fail commit if hook binary not installed | `false` |

#### Known Limitations

- Parallel execution occasionally hangs on Windows with PowerShell 7.5.x (tracked issue; workaround: disable parallel for Windows developers via `lefthook-local.yml`)
- `lefthook install` must be run manually after clone; no npm `prepare` script equivalent unless added manually
- Remote hooks (fetched from external URLs) require network access at install time
- No GUI; entirely CLI-driven

---

### 1.2 Husky

**What**: Git hooks manager tightly integrated with Node.js and npm lifecycle
**Site**: [typicode.github.io/husky](https://typicode.github.io/husky/) | **Version**: 9.1.x | **License**: MIT
**Compat**: JVM No (requires Node.js), Node.js Yes (native), Python No

#### Why It Matters

Husky is the industry-standard Git hooks manager for JavaScript and TypeScript projects. With approximately 5 million weekly npm downloads and adoption by React, Next.js, Vite, and thousands of open-source projects, it is the de facto choice when your project is already Node.js-first. Husky v9 dropped the `prepare` auto-install footgun from earlier versions and reduced the package to 2 KB with zero runtime dependencies. Each hook is a plain shell script in `.husky/`, which makes them easy to read, diff, and debug without knowing Husky internals. The typical pairing is `husky` (hook runner) + `lint-staged` (staged-file filtering), though Lefthook now offers both in one tool.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Cross-Ecosystem Support | **Weak** - Node.js only; requires `npm install` for every developer |
| Performance | **Medium** - Node.js startup overhead per hook; sequential with lint-staged |
| Configuration | **Medium** - Hook scripts in `.husky/`, linting config separate |
| Monorepo Support | **Medium** - Works but requires per-package setup or root lint-staged config |
| Staged-files Support | **Strong** - lint-staged companion tool is purpose-built for this |
| CI Integration | **Strong** - `HUSKY=0` env var disables in CI |
| Setup Effort | **Low** - `npm install husky && npx husky init` |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 33k stars, 5M weekly downloads, widely documented |

#### Quick Start

```bash
npm install --save-dev husky lint-staged
npx husky init
```

```bash
# .husky/pre-commit
npx lint-staged
```

```bash
# .husky/commit-msg
npx commitlint --edit $1
```

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx,js}": ["eslint --fix", "prettier --write"],
    "*.{json,md}": "prettier --write"
  }
}
```

#### Key Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `HUSKY=0` | Disable all hooks (CI environments) | Not set |
| `HUSKY_GIT_PARAMS` | Passed hook arguments | Automatic |
| `lint-staged` config | Which commands run on which file patterns | In `package.json` or `.lintstagedrc` |
| `.husky/_/husky.sh` | Internal Husky bootstrap (do not edit) | Auto-generated |

#### Known Limitations

- Node.js-only: teams using JVM or Python services in the same repo must install Node.js on every developer machine
- Husky's `prepare` script in older versions would silently wipe committed hook files after `npm install` or `yalc publish`
- Sequential execution unless lint-staged is configured with careful ordering
- `lint-staged` is a separate dependency adding ~1,500 transitive packages

---

### 1.3 pre-commit

**What**: Python-native multi-language hook framework with a curated hook registry
**Site**: [pre-commit.com](https://pre-commit.com/) | **Version**: 4.5.1 (Dec 2025) | **License**: MIT
**Compat**: JVM Via hook scripts, Node.js Via hook scripts, Python Native

#### Why It Matters

pre-commit takes a different approach from Husky and Lefthook: instead of running local scripts, it manages isolated virtual environments per hook repository. You declare hooks by referencing GitHub repos and tags, and pre-commit handles installation, isolation, and caching. This makes it trivially easy to consume a shared hook library (e.g., `pre-commit/pre-commit-hooks`, `gitleaks`, `detect-secrets`) without polluting the project's dependency tree. With over 100 million monthly PyPI downloads and native Python support, it is the dominant choice for Python-first teams. The `pre-commit.ci` managed service provides free CI enforcement for open-source projects.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Cross-Ecosystem Support | **Strong** - Supports Python, Node, Ruby, Go, system hooks |
| Performance | **Medium** - Virtual env isolation adds startup cost; caching mitigates |
| Configuration | **Strong** - Single `.pre-commit-config.yaml`; hooks from any git repo |
| Hook Registry | **Strong** - Hundreds of community-maintained hook repos |
| Staged-files Support | **Strong** - `pass_filenames: true` filters to staged files by default |
| CI Integration | **Strong** - `pre-commit run --all-files` in CI; `pre-commit.ci` service |
| Setup Effort | **Low** - `pip install pre-commit && pre-commit install` |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 15.1k stars, 100M+ monthly downloads, Anthony Sottile |

#### Quick Start

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

```bash
pip install pre-commit        # or: brew install pre-commit
pre-commit install             # Install .git/hooks/pre-commit
pre-commit run --all-files     # Manual run on all files
```

#### Key Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `rev` | Git tag/SHA for hook repo; pin to exact version | Required |
| `stages` | Limit hook to specific stages (commit, push, etc.) | All stages |
| `pass_filenames: false` | Run command once without file list | `true` |
| `always_run: true` | Run even when no matching files staged | `false` |
| `language_version` | Pin interpreter version for isolation | System default |
| `ci.skip` | Skip specific hooks in `pre-commit.ci` | None |

#### Known Limitations

- Slower first run while hook environments are being built (subsequent runs use cache)
- Hook isolation means hooks cannot easily share the project's installed packages
- Each hook repo revision must be pinned; `pre-commit autoupdate` keeps them fresh
- Not well-suited for running project-local scripts unless using `repo: local`

---

### Choosing Between Git Hook Managers

| Scenario | Recommendation |
|----------|---------------|
| Pure JavaScript/TypeScript project | Husky + lint-staged (ecosystem standard, widely documented) |
| Python-first project | pre-commit (native, isolated environments, huge hook library) |
| Multi-ecosystem or language-agnostic | Lefthook (Go binary, no runtime dependency, single config) |
| Monorepo with mixed languages | Lefthook (extends config, root scoping) |
| Enterprise with no Node.js guarantee | Lefthook (binary distribution, no npm required) |

---

## 2. Commit Conventions

### 2.1 commitlint

**What**: Lint commit messages against the Conventional Commits specification
**Site**: [commitlint.js.org](https://commitlint.js.org/) | **Version**: 20.5.0 (Mar 2026) | **License**: MIT
**Compat**: JVM Via CI/CD, Node.js Native, Python Via CI/CD

#### Why It Matters

Unstructured commit messages are one of the most common contributors to poor release automation and unreadable Git history. commitlint enforces the Conventional Commits format (`type(scope): subject`) at commit time, blocking messages like "fix stuff" or "wip" before they land in the history. When combined with `semantic-release` or `conventional-changelog`, well-formed commit messages drive automatic versioning (MAJOR for `BREAKING CHANGE`, MINOR for `feat`, PATCH for `fix`) and auto-generated release notes. With 17k GitHub stars and 1,360 downstream dependents of `@commitlint/config-conventional` alone, it is the standard choice for JavaScript-heavy teams.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Rule Coverage | **Strong** - Type, scope, subject, body, footer, max-length rules |
| Configuration | **Strong** - Extends shareable configs; fully customizable rules |
| CI Integration | **Strong** - Official GitHub Actions guide; validates last commit or full PR range |
| Cross-Ecosystem | **Medium** - Node.js native; other ecosystems run it via CI container |
| Developer Experience | **Strong** - Clear error messages with help URLs |
| Setup Effort | **Low** - Two packages + one config file |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 17k stars; React, Vue, Angular use it |

#### Quick Start

```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional
```

```js
// commitlint.config.js
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Override: allow longer headers for monorepos with verbose scopes
    'header-max-length': [2, 'always', 120],
    // Custom scope allowlist
    'scope-enum': [
      2,
      'always',
      ['api', 'web', 'infra', 'docs', 'deps']
    ]
  }
};
```

**Add to Lefthook (recommended):**
```yaml
# lefthook.yml
commit-msg:
  commands:
    commitlint:
      run: npx commitlint --edit {1}
```

**GitHub Actions CI enforcement:**
```yaml
# .github/workflows/commitlint.yml
name: Lint commits
on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: lts/*
          cache: npm
      - run: npm install -D @commitlint/cli @commitlint/config-conventional
      - name: Validate current commit (push)
        if: github.event_name == 'push'
        run: npx commitlint --from HEAD~1 --to HEAD --verbose
      - name: Validate PR commits
        if: github.event_name == 'pull_request'
        run: npx commitlint --from ${{ github.event.pull_request.base.sha }} --to ${{ github.event.pull_request.head.sha }} --verbose
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `extends` | Shareable base config (`config-conventional`, `config-nx-scopes`) | None |
| `rules['type-enum']` | Allowed commit types | Conventional spec types |
| `rules['scope-enum']` | Allowed scopes; useful for monorepos | All scopes |
| `rules['header-max-length']` | Max characters in first line | `100` |
| `ignores` | Functions returning `true` skip linting | None |
| `helpUrl` | Custom URL shown on failure | commitlint docs |

#### Known Limitations

- Node.js runtime required; teams not using Node.js must install it or use a container in CI
- Does not auto-fix messages (by design); developer must amend and recommit
- Scope enforcement requires maintaining the allowlist as the codebase grows

---

### 2.2 commitizen (Python / cz-cli)

**What**: Interactive CLI to guide developers through writing compliant commit messages
**Site**: [commitizen-tools.github.io/commitizen](https://commitizen-tools.github.io/commitizen/) | **Version**: 4.13.9 (Feb 2026) | **License**: MIT
**Compat**: JVM Via pip/pipx, Node.js Via pip/pipx, Python Native

> Note: There are two "commitizen" tools. The **Python commitizen** (commitizen-tools, 3.4k stars) is a full-lifecycle tool covering bump + changelog + commit. The **JavaScript cz-cli** (commitizen/cz-cli, 10.4k stars) is a Node.js-native interactive commit prompt. This section covers the Python tool; the JS tool is discussed in the Node.js ecosystem section.

#### Why It Matters

The Python commitizen handles the full conventional commits lifecycle in one CLI: interactive prompting (`cz commit`), version bumping (`cz bump`), and changelog generation (`cz changelog`). For Python teams, it integrates naturally into `pyproject.toml` and supports `uv`, `poetry`, and `pip` workflows. Its `cz bump` command reads the commit history and determines the next semantic version automatically, then tags and updates version files atomically. This makes it the closest Python equivalent to `semantic-release` in the Node.js ecosystem.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Commit Prompting | **Strong** - Interactive TUI guides type, scope, subject, body, breaking |
| Version Bumping | **Strong** - Reads conventional commits; bumps `pyproject.toml`, `__version__`, etc. |
| Changelog Generation | **Strong** - Markdown changelog auto-generated from commits |
| Cross-Ecosystem | **Medium** - Python native; usable in any repo via pipx |
| CI Integration | **Strong** - `cz bump --changelog --yes` in release pipelines |
| Setup Effort | **Low** - `pip install commitizen` or `uv tool install commitizen` |
| Cost | **Free** |
| Ecosystem Maturity | **Medium** - 3.4k stars; actively maintained; 100+ releases |

#### Quick Start

```bash
pip install commitizen
# or
uv tool install commitizen
```

```toml
# pyproject.toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "1.0.0"
version_files = ["src/__version__.py", "pyproject.toml:version"]
tag_format = "v$version"
changelog_incremental = true
```

```bash
cz commit              # Interactive commit prompt
cz bump                # Auto-bump version + tag + update CHANGELOG.md
cz changelog           # Regenerate CHANGELOG.md from history
```

**Add to Lefthook:**
```yaml
# lefthook.yml
prepare-commit-msg:
  commands:
    commitizen-prompt:
      run: cz commit --retry
      interactive: true
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `name` | Commit rule adapter (e.g., `cz_conventional_commits`) | `cz_conventional_commits` |
| `version_files` | Files to update on `cz bump` | None |
| `tag_format` | Git tag format | `$version` |
| `changelog_incremental` | Only add new entries to existing CHANGELOG | `false` |
| `major_version_zero` | Don't bump major from 0.x even for breaking changes | `false` |
| `pre_bump_hooks` | Commands to run before bumping (e.g., tests) | None |

#### Known Limitations

- Python runtime required for use in non-Python repos
- Interactive TUI cannot be used in non-TTY environments (CI uses `--yes` flag)
- Custom adapters require Python code; less pluggable than commitlint's JS config

---

### 2.3 conventional-changelog

**What**: Ecosystem of parsers, writers, and tools for generating changelogs from conventional commits
**Site**: [github.com/conventional-changelog](https://github.com/conventional-changelog/conventional-changelog) | **License**: MIT
**Compat**: JVM Via CI, Node.js Native, Python Via CI

#### Why It Matters

conventional-changelog is not a single tool but a family of packages: `conventional-changelog-core` (the engine), preset adapters (`angular`, `conventionalcommits`), and the CLI (`conventional-changelog-cli`). `semantic-release` uses it under the hood. The ecosystem also includes `standard-version` (now deprecated in favor of `release-please`) and Google's `release-please` GitHub Action. For teams already using Conventional Commits, this ecosystem makes changelog generation and release automation nearly zero-effort.

**Key tools in the ecosystem:**

| Tool | Purpose | Stars |
|------|---------|-------|
| `conventional-changelog-cli` | CLI to generate CHANGELOG.md | part of mono-repo |
| `semantic-release` | Full CI release automation (version + tag + publish) | 21k |
| `release-please` (Google) | GitHub Action for releases; PR-based workflow | 7.8k |
| `standard-version` | Local bump + changelog (deprecated; use release-please) | 7.8k |

#### Quick Start (semantic-release)

```json
// package.json
{
  "release": {
    "branches": ["main"],
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator",
      "@semantic-release/changelog",
      "@semantic-release/github",
      "@semantic-release/npm"
    ]
  }
}
```

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: lts/*
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

#### Known Limitations

- `semantic-release` requires a CI environment with push access; cannot be run locally by default
- `release-please` creates a PR per release, which suits some teams but adds overhead for others
- The `standard-version` package is officially deprecated; migrate to `release-please` or `semantic-release`

---

## 3. Editor Config

### 3.1 .editorconfig

**What**: Cross-IDE file format specification for enforcing consistent coding style
**Site**: [editorconfig.org](https://editorconfig.org/) | **Spec version**: 0.17.x | **License**: Public Domain / CC0
**Compat**: JVM Yes (IntelliJ native, Eclipse plugin, VS Code), Node.js Yes, Python Yes

#### Why It Matters

The classic sources of noisy pull request diffs are not logic changes but whitespace, line-ending, and indentation disagreements between team members' editors. `.editorconfig` solves this by placing a single file at the repository root that every major IDE reads natively. IntelliJ IDEA, VS Code, Visual Studio, Neovim, Emacs, Sublime Text, and WebStorm all support `.editorconfig` either natively or via a widely available plugin. The file format uses glob-based sections, meaning you can apply different rules to `*.java`, `*.py`, `*.ts`, `Makefile`, and `*.md` in the same repository. It is the only tool in this guide that requires no installation and has no runtime dependency whatsoever.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Cross-Ecosystem Support | **Strong** - Works for any file type in any language |
| IDE Support | **Strong** - Native in IntelliJ, VS Code, Visual Studio, many others |
| Zero Setup | **Strong** - Drop a file; IDEs auto-detect and apply |
| CI Enforcement | **Medium** - `editorconfig-checker` CLI validates compliance |
| Rule Coverage | **Medium** - Covers whitespace, line endings, charset; not code style |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - De facto standard; part of many project templates |

#### Quick Start — Polyglot Monorepo

```ini
# .editorconfig
root = true

# Universal defaults (all files)
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# Java and Kotlin
[*.{java,kt,kts}]
indent_style = space
indent_size = 4
max_line_length = 120

# JavaScript, TypeScript, JSON
[*.{js,ts,tsx,jsx,json,jsonc}]
indent_style = space
indent_size = 2
max_line_length = 100

# Python
[*.py]
indent_style = space
indent_size = 4
max_line_length = 88

# YAML and TOML
[*.{yml,yaml,toml}]
indent_style = space
indent_size = 2

# Markdown
[*.md]
trim_trailing_whitespace = false
max_line_length = off

# Makefiles require tabs
[Makefile]
indent_style = tab

# Shell scripts
[*.{sh,bash,zsh}]
indent_style = space
indent_size = 2
end_of_line = lf
```

**CI enforcement with editorconfig-checker:**
```yaml
# .github/workflows/lint.yml
- name: Check editorconfig compliance
  uses: editorconfig-checker/action-editorconfig-checker@main
```

Or via the CLI:
```bash
npm install --save-dev editorconfig-checker
npx ec --exclude ".git,.node_modules"
```

#### Key Configuration Options

| Property | Values | Purpose |
|----------|--------|---------|
| `indent_style` | `tab` / `space` | Character used for indentation |
| `indent_size` | Integer | Number of spaces per indent level |
| `end_of_line` | `lf` / `crlf` / `cr` | Line ending character |
| `charset` | `utf-8`, `latin1`, etc. | File encoding |
| `trim_trailing_whitespace` | `true` / `false` | Remove trailing spaces |
| `insert_final_newline` | `true` / `false` | Ensure file ends with newline |
| `max_line_length` | Integer / `off` | Soft guideline (IDE warning only) |
| `root = true` | Flag | Stop searching parent directories |

#### Known Limitations

- `.editorconfig` is advisory in most IDEs — it does not automatically reformat existing files
- `max_line_length` is informational only; it does not enforce line wrapping
- No support for language-specific style rules (naming conventions, brace style) — use language-specific tools (Prettier, Black, ktlint) for those
- CI enforcement requires a separate tool (`editorconfig-checker`); `.editorconfig` alone is not CI-enforceable

---

## 4. Dependency Automation

### 4.1 Renovate

**What**: Highly configurable automated dependency update bot supporting 90+ package managers
**Site**: [docs.renovatebot.com](https://docs.renovatebot.com/) | **Version**: 40.x | **License**: AGPL-3.0
**Compat**: JVM Yes (Maven, Gradle), Node.js Yes (npm, yarn, pnpm), Python Yes (pip, poetry, uv, pip-compile)

#### Why It Matters

Renovate is the most capable dependency automation tool available in 2026. Its 90+ package manager support includes not just npm and Maven but also GitHub Actions versions, Docker image tags, Kubernetes Helm charts, Terraform provider versions, and even arbitrary version strings via regex managers. For polyglot monorepos, Renovate's package grouping means a Spring Boot version bump can be orchestrated as a single PR that updates both the Gradle dependency and the Docker base image. Configurable stability days (e.g., wait 3 days before proposing a patch update) reduce noise from packages that quickly release a follow-up patch for regressions. The Mend-hosted Renovate app is free for public and private repositories; self-hosting under AGPL-3.0 is also free.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Package Manager Coverage | **Strong** - 90+ managers including Gradle, Maven, npm, pip, Docker, Helm, Terraform |
| Configuration Flexibility | **Strong** - 400+ config options; shareable org presets |
| Monorepo Support | **Strong** - Grouped PRs; ecosystem-specific scheduling |
| Auto-Merge | **Strong** - Built-in; configurable by type (patch/minor/major), stability days |
| Multi-Platform | **Strong** - GitHub, GitLab, Bitbucket, Azure DevOps, Gitea |
| Security Updates | **Strong** - OSV.dev integration; vulnerability alerts auto-merge |
| Setup Effort | **Low** - Install GitHub App + commit `renovate.json` |
| Cost | **Free** (hosted or self-hosted) |
| Ecosystem Maturity | **Strong** - 21.1k stars; Mend-backed; 3k forks |

#### Quick Start

```json
// renovate.json (minimal, extend recommended presets)
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended",
    ":dependencyDashboard",
    ":semanticCommits",
    "group:monorepos",
    "schedule:weekly"
  ],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "matchCurrentVersion": "!/^0/",
      "automerge": true,
      "automergeType": "branch",
      "minimumReleaseAge": "3 days"
    },
    {
      "matchDepTypes": ["devDependencies"],
      "automerge": true,
      "automergeType": "branch"
    },
    {
      "groupName": "Spring Boot",
      "matchPackageNames": [
        "org.springframework.boot:spring-boot-starter-parent",
        "org.springframework.boot:*"
      ]
    }
  ]
}
```

#### Key Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `extends` | Shareable preset inheritance | None |
| `schedule` | When Renovate runs (cron syntax) | Continuous |
| `minimumReleaseAge` | Wait N days before proposing update | `0` |
| `automerge` | Automatically merge eligible PRs | `false` |
| `groupName` | Combine multiple updates into one PR | None |
| `packageRules` | Scoped overrides by package, type, ecosystem | None |
| `vulnerabilityAlerts` | Auto-create PRs for CVE fixes | `false` |
| `regexManagers` | Update arbitrary version strings in any file | None |
| `dependencyDashboard` | Single issue tracking all pending updates | `false` |

#### Known Limitations

- Self-hosted Renovate requires a persistent runner with appropriate token scopes
- Config is JSONC (JSON with comments), not YAML; 400+ options create a learning curve
- Grouping logic can produce large PRs that are harder to review
- The Mend hosted service (Renovate App) may have rate limits in very large orgs

---

### 4.2 Dependabot

**What**: GitHub's built-in automated dependency security and version update service
**Site**: [docs.github.com/dependabot](https://docs.github.com/en/code-security/dependabot) | **License**: Proprietary (GitHub-owned)
**Compat**: JVM Yes (Maven, Gradle), Node.js Yes (npm, yarn, pnpm), Python Yes (pip, poetry, pip-compile)

#### Why It Matters

Dependabot requires no installation: it is native to GitHub and activated via repository settings or a committed `.github/dependabot.yml`. For teams that live in GitHub and want dependency security patches applied automatically with minimal configuration overhead, Dependabot is the right default choice. GitHub's native secret scanning and security alerts integrate directly with Dependabot, meaning known-vulnerable dependency alerts surface automatically and Dependabot can open the fix PR without any extra configuration. It supports 30+ package managers with a simple per-ecosystem YAML config.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Setup Effort | **Low** - Enable in repo settings; optionally add `dependabot.yml` |
| GitHub Integration | **Strong** - Native; security alerts, secret scanning, code scanning unified |
| Package Manager Coverage | **Medium** - 30+ managers (vs. Renovate's 90+) |
| Configuration Flexibility | **Medium** - ~20 options per ecosystem (vs. 400+ in Renovate) |
| Auto-Merge | **Medium** - Requires additional GitHub Actions workflow |
| Multi-Platform | **Weak** - GitHub only |
| Grouped PRs | **Medium** - Basic grouping available; less powerful than Renovate |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - GitHub-native, no maintenance required |

#### Quick Start

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    labels:
      - "dependencies"
      - "java"
    groups:
      spring-boot:
        patterns:
          - "org.springframework.boot*"

  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    labels:
      - "dependencies"
      - "javascript"

  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "python"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Auto-merge patch updates via GitHub Actions:**
```yaml
# .github/workflows/dependabot-automerge.yml
name: Dependabot auto-merge
on: pull_request

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    steps:
      - uses: dependabot/fetch-metadata@v2
        id: fetch-metadata
        with:
          github-token: "${{ secrets.GITHUB_TOKEN }}"
      - uses: gh pr merge --auto --squash "${{ github.event.pull_request.html_url }}"
        if: steps.fetch-metadata.outputs.update-type == 'version-update:semver-patch'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### Key Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `package-ecosystem` | Ecosystem to watch | Required |
| `directory` | Where to look for manifests | `"/"` |
| `schedule.interval` | `daily`, `weekly`, `monthly` | Required |
| `target-branch` | Branch to open PRs against | Default branch |
| `groups` | Group updates from matching packages into one PR | None |
| `ignore` | Specific packages or versions to skip | None |
| `open-pull-requests-limit` | Max open PRs per ecosystem | `5` |

#### Known Limitations

- GitHub-only; cannot use with GitLab, Bitbucket, or self-hosted Git servers
- No cross-file regex managers (cannot update versions in arbitrary files)
- Auto-merge requires a separate GitHub Actions workflow
- Limited scheduling options compared to Renovate's cron-style schedules
- One PR per dependency by default (grouping is less powerful than Renovate's)

### Renovate vs Dependabot Decision Guide

| Factor | Choose Renovate | Choose Dependabot |
|--------|----------------|-------------------|
| Platform | GitLab, Bitbucket, Azure DevOps | GitHub-only is fine |
| Package managers | Need 90+ (Helm, Terraform, etc.) | 30+ is sufficient |
| Configuration | Complex grouping / scheduling needed | Simple weekly updates |
| Auto-merge | Need built-in, configurable auto-merge | Can add a GitHub Actions workaround |
| Compliance | Need self-hosted audit log | GitHub-native is acceptable |
| Team familiarity | Willing to invest in config learning | Prefer zero-config start |

**Practical recommendation**: Enable Dependabot for security alerts (free, instant, zero config) and add Renovate for version updates if you need grouping, cross-platform support, or complex policies.

---

## 5. Security Scanning

### 5.1 Trivy

**What**: Comprehensive, all-in-one security scanner for containers, code, IaC, secrets, and SBOM
**Site**: [trivy.dev](https://trivy.dev/) | **Version**: 0.69.3 (Mar 2026) | **License**: Apache 2.0
**Compat**: JVM Yes, Node.js Yes, Python Yes

#### Why It Matters

Trivy is the most complete free security scanner in the ecosystem in 2026. A single binary scans container images, filesystems, remote Git repositories, Kubernetes clusters, VM images, and IaC files (Terraform, CloudFormation, Helm, Kubernetes YAML). It detects known vulnerabilities (CVEs), IaC misconfigurations, hardcoded secrets, software licenses, and generates SBOMs in CycloneDX or SPDX format. With 34k GitHub stars and an Apache 2.0 license, it is production-ready at every scale. Version 0.67 made `--list-all-pkgs` the default, ensuring complete package visibility in JSON reports. The v0.66 streaming secret scanner reduced peak memory by 94% when scanning large files.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Vulnerability Coverage | **Strong** - CVEs via Aqua trivy-db (daily updates from NVD, OSV, RHSAs, etc.) |
| IaC Scanning | **Strong** - Terraform, CloudFormation, Helm, Kubernetes, Dockerfile |
| Secret Detection | **Strong** - Streaming scanner; 94% lower memory than v0.65 |
| SBOM Generation | **Strong** - CycloneDX 1.4+, SPDX 2.3, preserve structure |
| Kubernetes | **Strong** - Cluster scanning via `trivy k8s` |
| Performance | **Strong** - Fast; parallelized; cached vulnerability DB |
| CI Integration | **Strong** - Official GitHub Action; SARIF output for GitHub Code Scanning |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 34k stars; Aqua Security backed; CNCF ecosystem |

#### Quick Start

```bash
# Install
brew install trivy
# or: docker pull aquasec/trivy

# Scan a container image
trivy image python:3.13-slim

# Scan a local repository (deps + secrets + IaC)
trivy fs . --scanners vuln,secret,misconfig

# Scan Kubernetes cluster
trivy k8s --report summary cluster

# Generate SBOM
trivy image --format cyclonedx --output sbom.json myapp:latest

# CI: fail on HIGH/CRITICAL only
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest
```

**GitHub Actions integration:**
```yaml
# .github/workflows/trivy.yml
name: Trivy Security Scan
on:
  push:
    branches: [main]
  pull_request:

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner (repo)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          scanners: 'vuln,secret,misconfig'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'HIGH,CRITICAL'

      - name: Upload Trivy scan results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

#### Key Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `--scanners` | `vuln,secret,misconfig,license` | `vuln,secret` |
| `--severity` | `LOW,MEDIUM,HIGH,CRITICAL` filter | All |
| `--exit-code` | Return non-zero if issues found | `0` |
| `--ignore-unfixed` | Skip CVEs without available fix | `false` |
| `--format` | `table,json,sarif,cyclonedx,spdx` | `table` |
| `--skip-dirs` | Directories to exclude from scan | None |
| `.trivyignore` | CVE IDs to ignore permanently | None |
| `--list-all-pkgs` | Include all packages in JSON output | `true` (since 0.67) |

#### Known Limitations

- No SAST (code quality or logic errors); use Snyk Code or SonarCloud for that
- Does not automatically create fix PRs; reports vulnerabilities but remediation is manual
- The Aqua trivy-db is updated daily but relies on public advisory sources (NVD, etc.)
- `trivy k8s` requires kubectl access to the cluster being scanned
- False positives occur on vendored dependencies or private forks; `.trivyignore` manages these

---

### 5.2 Gitleaks

**What**: Fast secret scanner that detects hardcoded credentials in Git history and staged changes
**Site**: [gitleaks.io](https://gitleaks.io/) | **Version**: 8.30.1 (Nov 2025) | **License**: MIT
**Compat**: JVM Yes, Node.js Yes, Python Yes

#### Why It Matters

Gitleaks focuses exclusively on one problem: detecting secrets (API keys, tokens, passwords, private keys) committed to Git. This specialization makes it one of the most accurate and fastest tools in the category. With 24.4k GitHub stars and a growing detection ruleset, it outperforms entropy-only scanners on precision. Two operation modes are particularly valuable: `gitleaks git` scans the entire repository history (finding secrets committed years ago), and pre-commit hook mode blocks new secrets from being committed in the first place. SARIF output integrates directly with GitHub Advanced Security to surface findings in the Security tab and block PRs. The baseline feature lets teams scan a legacy repo, acknowledge existing findings, and then enforce clean code going forward.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Detection Accuracy | **Strong** - Regex + entropy; low false positive rate |
| Pre-commit Integration | **Strong** - Official pre-commit hook; Lefthook compatible |
| History Scanning | **Strong** - `git log` traversal; configurable depth |
| Output Formats | **Strong** - JSON, CSV, JUnit, SARIF |
| Baseline Support | **Strong** - Ignore known historical findings |
| Custom Rules | **Strong** - TOML config with regex + entropy thresholds |
| CI Integration | **Strong** - Official GitHub Action; SARIF upload |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 24.4k stars; MIT license |

#### Quick Start

```bash
brew install gitleaks

# Scan entire git history
gitleaks git --verbose .

# Scan staged/uncommitted changes only (pre-commit mode)
gitleaks protect --staged -v

# Create a baseline (for repos with known historical secrets)
gitleaks git --report-path gitleaks-baseline.json .
gitleaks git --baseline-path gitleaks-baseline.json --report-path new-findings.json .
```

**Add to Lefthook:**
```yaml
# lefthook.yml
pre-commit:
  commands:
    gitleaks:
      run: gitleaks protect --staged -v
```

**Add to pre-commit:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
```

**Custom rules (.gitleaks.toml):**
```toml
title = "Custom Gitleaks Config"

# Extend the default rules
[extend]
useDefault = true

[[rules]]
id = "internal-api-token"
description = "Internal API token"
regex = '''INTERNAL_TOKEN_[A-Za-z0-9]{32}'''
tags = ["key", "internal"]

[allowlist]
description = "Global allowlist"
regexes = ['''example\.com/api/key/[A-Z]+''']
paths = ["tests/fixtures/"]
```

#### Key Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `--config` | Custom rules file path | `.gitleaks.toml` |
| `--baseline-path` | JSON baseline to suppress known findings | None |
| `--report-path` | Output file path | None |
| `--report-format` | `json,csv,junit,sarif` | `json` |
| `--max-target-megabytes` | Skip files larger than N MB | `0` (no limit) |
| `--no-git` | Scan directory without git traversal | `false` |
| `GITLEAKS_ENABLE_COMMENTS` | Honor `# gitleaks:allow` inline suppression | `false` |

#### Known Limitations

- Regex-based detection can miss obfuscated or encoded secrets
- Does not scan binary files (images, compiled artifacts)
- Custom rules require TOML regex knowledge; complex patterns have a learning curve
- History scanning of very large monorepos (GB of git history) is slow; use `--log-opts` to limit range

---

### 5.3 Snyk (for comparison)

**What**: Commercial developer security platform covering SAST, SCA, container, and IaC scanning
**Site**: [snyk.io](https://snyk.io/) | **License**: Proprietary (free tier available)
**Compat**: JVM Yes, Node.js Yes, Python Yes

#### Why It Matters

Snyk fills the gap that Trivy and Gitleaks leave: SAST (static application security testing that analyzes code logic) and automated fix pull requests. Snyk Code uses the DeepCode AI engine to detect security issues in application logic — SQL injection patterns, XSS vulnerabilities, unsafe deserialization — that a dependency scanner cannot find. Snyk Open Source's fix PRs automatically propose upgrades or patches for vulnerable dependencies, reducing mean-time-to-remediation. Snyk's reachability analysis (for Java and JavaScript) determines whether vulnerable code paths are actually called by your application, reducing alert fatigue significantly.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| SAST | **Strong** - DeepCode AI; 19+ languages; unavailable in Trivy |
| SCA (dependency scanning) | **Strong** - Curated proprietary database; fix PRs |
| Reachability Analysis | **Strong** - Reduces noise to exploitable vulnerabilities only |
| Container Scanning | **Strong** - Monitors registry images continuously |
| Developer Experience | **Strong** - IDE plugins (VS Code, IntelliJ, Eclipse); PR decoration |
| Cost | **Freemium** - Free for individuals; team/enterprise features require paid plan |
| CI Integration | **Strong** - GitHub Actions, GitLab CI, CircleCI |
| Ecosystem Maturity | **Strong** - Founded 2015; widely adopted in enterprise |

#### Quick Start (CI integration)

```yaml
# .github/workflows/snyk.yml
name: Snyk Security Scan
on: [push, pull_request]

jobs:
  snyk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
```

#### Known Limitations

- SAST, PR decoration, and reachability analysis require paid plans for teams
- Vendor lock-in: Snyk's vulnerability database is proprietary
- Free tier limits apply to private repositories (number of tests/month)
- Requires `SNYK_TOKEN` configuration; more setup than Trivy

---

## 6. CI/CD Quality Gates

### 6.1 GitHub Actions Patterns

**What**: Event-driven CI/CD workflow engine native to GitHub
**Site**: [docs.github.com/actions](https://docs.github.com/en/actions) | **License**: Proprietary (free tier)
**Compat**: JVM Yes, Node.js Yes, Python Yes

#### Why It Matters

GitHub Actions is the CI/CD platform of choice for most teams hosting on GitHub, and in 2026 it offers the broadest ecosystem of community-built actions. For quality gates specifically, Actions enables a layered defense: commit linting, code coverage enforcement, security scanning, and static analysis all run as required status checks that block merging when they fail. The `on: pull_request` trigger combined with branch protection rules creates a fully automated quality gate that requires zero human involvement for routine PRs. GitHub reduced hosted runner prices by up to 39% on January 1, 2026.

#### Recommended Quality Pipeline Pattern

```yaml
# .github/workflows/quality.yml
name: Quality Gates

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # ---- Commit message validation ----
  commitlint:
    name: Lint commit messages
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: lts/*
          cache: npm
      - run: npm install -D @commitlint/cli @commitlint/config-conventional
      - run: npx commitlint --from ${{ github.event.pull_request.base.sha }} --to HEAD

  # ---- Security scanning ----
  security:
    name: Security scan
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - name: Trivy FS scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          scanners: vuln,secret,misconfig
          format: sarif
          output: trivy.sarif
          severity: HIGH,CRITICAL
          exit-code: 1
      - name: Upload to GitHub Security
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy.sarif

  # ---- Build and test ----
  test:
    name: Build and test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests with coverage
        run: ./gradlew test jacocoTestReport  # or: npm test / pytest --cov
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v5
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: true

  # ---- Coverage gate ----
  coverage-gate:
    name: Coverage threshold
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Download coverage artifact
        uses: actions/download-artifact@v4
        with:
          name: coverage-report
      - name: Enforce 80% line coverage
        run: |
          COVERAGE=$(grep -oP 'line-rate="\K[0-9.]+' coverage.xml | head -1)
          PCT=$(echo "$COVERAGE * 100 / 1" | bc)
          echo "Coverage: ${PCTS}%"
          if [ "$PCT" -lt "80" ]; then
            echo "Coverage ${PCT}% is below 80% threshold"
            exit 1
          fi
```

**Branch protection settings (recommended):**

```
Require status checks to pass before merging:
  ✓ commitlint
  ✓ security
  ✓ test
  ✓ coverage-gate

Require branches to be up to date before merging: ✓
Require conversation resolution before merging: ✓
Restrict who can push to matching branches: ✓ (CI service accounts only)
```

#### Reusable Workflow Pattern (monorepos)

```yaml
# .github/workflows/reusable-quality.yml
name: Reusable Quality Gates
on:
  workflow_call:
    inputs:
      coverage-threshold:
        type: number
        default: 80
      test-command:
        type: string
        required: true
    secrets:
      CODECOV_TOKEN:
        required: true

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ${{ inputs.test-command }}
      # ... coverage check, security scan
```

```yaml
# packages/api/.github/workflows/ci.yml
name: API CI
on: [push, pull_request]
jobs:
  quality:
    uses: ./.github/workflows/reusable-quality.yml
    with:
      test-command: "./gradlew test"
      coverage-threshold: 85
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

#### Key Configuration Options

| Feature | Purpose | Notes |
|---------|---------|-------|
| `concurrency.cancel-in-progress` | Cancel stale PR runs | Saves CI minutes |
| `permissions` | Limit GITHUB_TOKEN scope | Security best practice |
| `timeout-minutes` | Kill hung jobs | Default is 6 hours |
| Required status checks | Block merge until checks pass | Configure in branch protection |
| Environment protection rules | Gate deployments with manual approval | For production |
| Reusable workflows (`workflow_call`) | Share pipeline across repos/packages | Monorepo governance |

#### Known Limitations

- GitHub Actions is GitHub-only; GitLab users need GitLab CI equivalent patterns
- Workflow file format is YAML with some quirky expression syntax (`${{ }}`)
- Free tier limits: 2,000 minutes/month for private repos on GitHub Free plan
- No native quality gate threshold UI; thresholds must be implemented in shell or external actions

---

### 6.2 Codecov

**What**: Code coverage aggregation, trend reporting, and PR decoration service
**Site**: [codecov.io](https://codecov.io/) | **License**: Proprietary (free tier for open source and 1 private user)
**Compat**: JVM Yes (JaCoCo, Cobertura), Node.js Yes (Istanbul/nyc, Jest, c8), Python Yes (coverage.py)

#### Why It Matters

Codecov answers the questions that raw coverage numbers cannot: "Is coverage trending down? Which files have the worst coverage? Does this PR reduce coverage on the lines it touches?" The "patch coverage" feature is particularly valuable for incremental quality enforcement: it measures coverage only on the lines changed in a PR, making it easy to enforce that new code must be tested without requiring legacy code to be backfilled immediately. PR comments, status checks, and badges are automatically posted with every coverage upload. The Developer plan is completely free for unlimited public repositories and one private user.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Report Formats | **Strong** - LCOV, JaCoCo XML, Cobertura, Go coverage, Clover, etc. |
| PR Decoration | **Strong** - PR comment + per-file coverage table + diff coverage |
| Patch Coverage | **Strong** - Enforces coverage on new/changed lines only |
| Trend Reporting | **Strong** - Coverage over time; flags and components |
| GitHub Integration | **Strong** - Status checks; required check for branch protection |
| Cross-Ecosystem | **Strong** - Any coverage format with an LCOV or XML export |
| Cost | **Freemium** - Free for OSS; $5/user/month for teams |
| Ecosystem Maturity | **Strong** - 1M+ developer community; Sentry-owned |

#### Quick Start

```yaml
# .github/workflows/coverage.yml (Node.js example)
- name: Run tests with coverage
  run: npm test -- --coverage --coverageReporters=lcov

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v5
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: coverage/lcov.info
    flags: unittests
    fail_ci_if_error: true

# JVM (JaCoCo) example
- name: Run tests
  run: ./gradlew test jacocoTestReport

- name: Upload JaCoCo coverage to Codecov
  uses: codecov/codecov-action@v5
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: build/reports/jacoco/test/jacocoTestReport.xml
    fail_ci_if_error: true
```

**codecov.yml (enforce patch coverage gate):**
```yaml
# codecov.yml
coverage:
  status:
    project:
      default:
        target: 80%          # Project-wide minimum
        threshold: 2%         # Allow up to 2% drop before failing
    patch:
      default:
        target: 90%          # New/changed code must be 90% covered
        threshold: 0%

comment:
  layout: "reach,diff,flags,tree"
  behavior: default
  require_changes: false
```

#### Key Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `coverage.status.project.target` | Minimum project coverage to pass | Auto (based on history) |
| `coverage.status.patch.target` | Minimum patch coverage to pass | Auto |
| `coverage.status.*.threshold` | Allowed decrease before failing | `0%` |
| `flags` | Segment coverage by test suite | None |
| `components` | Named coverage groups (e.g., per-service) | None |
| `ignore` | File/directory patterns to exclude | None |

#### Known Limitations

- Free tier allows 250 uploads/month for private repos (1 user); team plans start at $5/user/month
- Coverage must be generated by the test suite before uploading; Codecov does not run tests
- Historical data is lost if a repository is transferred or re-connected

---

### 6.3 SonarCloud

**What**: SaaS static analysis platform with quality gates, code smell detection, and security hotspots
**Site**: [sonarcloud.io](https://sonarcloud.io/) | **License**: Proprietary (free for public repos)
**Compat**: JVM Yes (Java, Kotlin), Node.js Yes (JavaScript, TypeScript), Python Yes

#### Why It Matters

SonarCloud (the SaaS version of SonarQube) provides the most comprehensive code quality platform available with a free tier. Beyond vulnerability detection, it identifies code smells, cognitive complexity, duplicated blocks, and technical debt estimates. PR decoration posts an analysis summary directly on every pull request. Quality gates block merges when new code introduces bugs, security hotspots, or drops below coverage thresholds. The "New Code" concept is particularly useful: by focusing analysis on code changed in the last 30 days, SonarCloud enables teams to enforce quality on new code without being blocked by legacy issues. For Java and Kotlin projects, the JVM-specific analysis is exceptionally deep.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Language Coverage | **Strong** - 30+ languages; excellent Java/Kotlin/Python/JS depth |
| Quality Gate | **Strong** - Configurable; blocks PR merge on violation |
| PR Decoration | **Strong** - Inline issues + summary comment on every PR |
| Security Analysis | **Strong** - OWASP Top 10, CWE, SANS 25 detection |
| Technical Debt | **Strong** - Estimates remediation effort in minutes/hours |
| "New Code" Focus | **Strong** - Enforce standards on new code without legacy burden |
| CI Integration | **Strong** - Official GitHub Actions; scanner CLI |
| Cost | **Freemium** - Free for public repos; paid for private (per LOC) |
| Ecosystem Maturity | **Strong** - Sonar-backed; widely adopted in enterprise |

#### Quick Start

```yaml
# .github/workflows/sonarcloud.yml
name: SonarCloud Analysis
on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  sonar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # Required for blame info and new code detection

      - uses: actions/setup-java@v4
        with:
          java-version: 21
          distribution: temurin

      - name: Build and test
        run: ./gradlew build jacocoTestReport

      - name: SonarCloud Scan
        uses: SonarSource/sonarqube-scan-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

```properties
# sonar-project.properties
sonar.projectKey=org-name_repo-name
sonar.organization=org-name
sonar.sources=src/main
sonar.tests=src/test
sonar.java.coveragePlugin=jacoco
sonar.coverage.jacoco.xmlReportPaths=build/reports/jacoco/test/jacocoTestReport.xml
sonar.java.binaries=build/classes
```

**Quality Gate (configured in SonarCloud UI):**
```
New code quality gate (recommended defaults):
  Coverage on New Code >= 80%
  Duplicated Lines on New Code <= 3%
  Maintainability Rating = A
  Reliability Rating = A
  Security Rating = A
  Security Hotspots Reviewed = 100%
```

#### Key Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `sonar.coverage.jacoco.xmlReportPaths` | Path to JaCoCo XML report | Auto-detect |
| `sonar.exclusions` | File patterns to exclude from analysis | None |
| `sonar.cpd.exclusions` | Exclude from duplication detection | None |
| `sonar.qualitygate.wait` | Wait for quality gate result in CI | `false` |
| `sonar.newCode.referenceBranch` | Branch defining "new code" | `main` |
| Quality Gate rules | Conditions in SonarCloud UI (not a file) | Sonar Way preset |

#### Known Limitations

- Private repositories require a paid plan (SonarCloud pricing is per lines of code analyzed)
- Analysis is asynchronous; the `sonar.qualitygate.wait=true` option extends CI job duration
- SonarCloud quality gate and GitHub branch protection must be manually connected
- Deep analysis requires build artifacts to be present (compiled classes for Java/Kotlin)

---

## References

### Official Documentation

- **Lefthook**: [lefthook.dev/configuration](https://lefthook.dev/configuration) — Configuration reference; `lefthook.yml` schema
- **Husky**: [typicode.github.io/husky](https://typicode.github.io/husky/) — v9 migration guide and API
- **pre-commit**: [pre-commit.com](https://pre-commit.com/) — Hook spec; supported languages; CI setup
- **commitlint**: [commitlint.js.org](https://commitlint.js.org/) — Rules reference; CI setup guide
- **commitizen (Python)**: [commitizen-tools.github.io/commitizen](https://commitizen-tools.github.io/commitizen/) — `cz bump` and changelog docs
- **Conventional Commits spec**: [conventionalcommits.org](https://www.conventionalcommits.org/) — The underlying specification
- **semantic-release**: [semantic-release.gitbook.io](https://semantic-release.gitbook.io/) — Full release automation
- **EditorConfig spec**: [editorconfig.org](https://editorconfig.org/) — Property reference
- **editorconfig-checker**: [editorconfig-checker.github.io](https://editorconfig-checker.github.io/) — CLI linting tool
- **Renovate docs**: [docs.renovatebot.com](https://docs.renovatebot.com/) — Configuration options; presets
- **Dependabot docs**: [docs.github.com/dependabot](https://docs.github.com/en/code-security/dependabot) — YAML schema reference
- **Trivy docs**: [aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy/) — Scan targets; output formats; trivy.yaml config
- **Gitleaks**: [gitleaks.io](https://gitleaks.io/) — Rules format; TOML config
- **GitHub Actions**: [docs.github.com/actions](https://docs.github.com/en/actions) — Workflow syntax; reusable workflows
- **Codecov**: [docs.codecov.io](https://docs.codecov.io/) — codecov.yml reference; GitHub Actions action
- **SonarCloud**: [docs.sonarcloud.io](https://docs.sonarcloud.io/) — Sonar scanner properties; quality gate API

### Research Sources and Comparisons

- PkgPulse: "husky vs lefthook vs lint-staged: Git Hooks in Node.js (2026)" — download stats and ecosystem positioning (Mar 2026)
- AppSec Santa: "Dependabot vs Renovate (2026): SCA Compared" — feature comparison table (Mar 2026)
- AppSec Santa: "Trivy vs Snyk (2026): Open-Source vs Commercial SCA Compared" — detailed feature matrix (Mar 2026)
- AppSec Santa: "Gitleaks 2026: Top Open-Source Git Secret Scanner" — stars and capabilities (Feb 2026)
- Andy Madge: "Git Hook Frameworks Comparison" — hand-written approach, Husky, pre-commit, Lefthook (Mar 2026)
- DEV.to: "Ditch Husky: Speed Up Git Hooks with Lefthook" — migration guide and performance benchmarks (Mar 2026)
- SonarSource Learn: "Integrating Quality Gates into Your CI/CD Pipeline: SonarQube Setup Guide" (Oct 2025)

### GitHub Stars Reference (as of research date: 2026-03-25)

| Tool | Stars | Source |
|------|-------|--------|
| Lefthook | 7,790 (v2.1.4) | github.com/evilmartians/lefthook |
| Husky | ~33,000 | npm weekly downloads: ~5M |
| pre-commit | 15,100 | github.com/pre-commit/pre-commit |
| commitlint | ~17,000 | github.com/conventional-changelog/commitlint |
| commitizen (Python) | 3,400 | github.com/commitizen-tools/commitizen |
| Renovate | 21,100 | github.com/renovatebot/renovate |
| Trivy | ~34,000 | github.com/aquasecurity/trivy |
| Gitleaks | 24,400 | github.com/gitleaks/gitleaks |
| semantic-release | ~21,000 | github.com/semantic-release/semantic-release |
