# Release-Please Setup: Examples

---

## Example 1: sellabella-style monorepo (backend services + frontend)

**Scenario:** A Gradle/Spring Boot backend monorepo with 10+ services under `backend/` and a Next.js frontend at `frontend/sellabella-ui`. All packages use `release-type: simple` (Gradle) except the frontend which uses `node`.

### Run

```bash
python3 "$SCRIPTS/release_please_setup.py" \
  --root . \
  --globs "backend/*,frontend/*" \
  --dry-run
```

### Generated config (excerpt — 3 packages shown)

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    "backend/user-service": {
      "release-type": "simple",
      "package-name": "user-service",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": true,
      "include-component-in-tag": true,
      "tag-separator": "-",
      "exclude-paths": [
        "backend/common-libs",
        "backend/analytics-service",
        "frontend/sellabella-ui"
      ]
    },
    "backend/analytics-service": {
      "release-type": "simple",
      "package-name": "analytics-service",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": true,
      "include-component-in-tag": true,
      "tag-separator": "-",
      "exclude-paths": [
        "backend/common-libs",
        "backend/user-service",
        "frontend/sellabella-ui"
      ]
    },
    "frontend/sellabella-ui": {
      "release-type": "node",
      "package-name": "sellabella-ui",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": true,
      "include-component-in-tag": true,
      "tag-separator": "-"
    }
  },
  "changelog-sections": [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
    {"type": "perf", "section": "Performance Improvements"},
    {"type": "refactor", "section": "Code Refactoring"},
    {"type": "docs", "section": "Documentation"},
    {"type": "test", "section": "Tests"},
    {"type": "ci", "section": "CI/CD"},
    {"type": "security", "section": "Security"},
    {"type": "chore", "section": "Miscellaneous", "hidden": true}
  ]
}
```

### Generated manifest

```json
{
  "backend/user-service": "0.0.0",
  "backend/analytics-service": "0.0.0",
  "frontend/sellabella-ui": "0.0.0"
}
```

### Deploy templates to pair

- **Backend services** → `deploy-docker-matrix.yml` (one workflow covers all services; derives component from tag at runtime using `sed 's/-v[0-9]*\.[0-9]*\.[0-9]*$//'`).
- **Frontend** → `deploy-frontend-host.yml` (gated quality gates: type-check, lint, format, tests, build; then Amplify/Vercel deploy triggered on `sellabella-ui-v*`).

Tags produced: `user-service-v1.2.0`, `analytics-service-v2.3.0`, `sellabella-ui-v0.5.1`.

---

## Example 2: papia-studio migration (pnpm monorepo with existing tags)

**Scenario:** A pnpm monorepo at `packages/` with packages including `text-cli` (npm-published), `vscode-papia` (VS Code extension), and `skrebe-web` (Fly.io app). All have existing `<package>-v*` tags. Adopting release-please should not disturb the existing publish workflows.

### Run

```bash
python3 "$SCRIPTS/release_please_setup.py" \
  --root . \
  --globs "packages/*" \
  --migrate \
  --dry-run
```

### Generated manifest (versions seeded from file detection + git tag fallback)

```json
{
  "packages/text-cli": "0.3.0",
  "packages/skrebe-web": "0.1.0",
  "packages/vscode-papia": "0.2.1"
}
```

The script found `"version": "0.3.0"` in `packages/text-cli/package.json`, `"version": "0.1.0"` in `packages/skrebe-web/package.json`, and fell back to the highest `vscode-papia-v*` git tag for `vscode-papia`.

### Config excerpt

```json
{
  "packages": {
    "packages/text-cli": {
      "release-type": "node",
      "package-name": "text-cli",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": true,
      "include-component-in-tag": true,
      "tag-separator": "-",
      "exclude-paths": ["packages/skrebe-web", "packages/vscode-papia"]
    },
    "packages/skrebe-web": {
      "release-type": "node",
      "package-name": "skrebe-web",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": true,
      "include-component-in-tag": true,
      "tag-separator": "-",
      "exclude-paths": ["packages/text-cli", "packages/vscode-papia"]
    },
    "packages/vscode-papia": {
      "release-type": "node",
      "package-name": "vscode-papia",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": true,
      "include-component-in-tag": true,
      "tag-separator": "-",
      "exclude-paths": ["packages/text-cli", "packages/skrebe-web"]
    }
  }
}
```

### Deploy templates to pair

- **text-cli** → `publish-npm-oidc.yml` (npm Trusted Publishing; no token, OIDC only). Existing `release-text-cli.yml` workflow keeps firing because the tag format is unchanged.
- **vscode-papia** → `release-asset.yml` (build `.vsix` → draft GitHub Release). Fill `__ARTIFACT_NAME__` with `vscode-papia`.
- **skrebe-web** → `deploy-fly.yml` (Fly.io deploy on `skrebe-web-v*`). Fill `__APP__` with `Skrebe Web`, `__COMPONENT__` with `skrebe-web`.

**Note:** The existing `push: tags: ["text-cli-v*"]` and `push: tags: ["vscode-papia-v*"]` workflows continue to fire unchanged — release-please produces the exact same tag format. On day one you can run both in parallel before switching over entirely.

**Out of scope:** The umbrella `vX.Y.Z` narrative release scheme (root `CHANGELOG.md`) has no release-please equivalent. Keep cutting those by hand.

---

## Example 3: single-package repo

**Scenario:** A standalone Node.js library in the repo root. No monorepo layout.

### Run

```bash
python3 "$SCRIPTS/release_please_setup.py" --root . --globs "." --single --dry-run
```

**`--globs "."` is required for a root-level package.** The default globs (`packages/*,backend/*,frontend/*`) only match sub-directories, so without `--globs "."` a single-package-at-root repo discovers nothing and produces an empty config. Once the root package is discovered, `--single` is optional — the script auto-detects ≤1 package and uses single-package mode anyway — but it's clearer to pass it explicitly.

### Generated config

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    ".": {
      "release-type": "node",
      "package-name": "my-lib"
    }
  },
  "changelog-sections": [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
    {"type": "chore", "section": "Miscellaneous", "hidden": true}
  ]
}
```

No `include-component-in-tag`, no `exclude-paths`. Tags are `v<semver>` (e.g. `v1.4.2`).

### Generated manifest

```json
{
  ".": "0.0.0"
}
```

### Deploy template to pair

Use `deploy-generic.yml`. Replace `__COMPONENT__` with your tag pattern prefix — for single-package, if you want `v*` triggers, edit the workflow's `tags:` field to `- "v*"` and remove the version-check step that expects the `<component>-v<ver>` format.

Alternatively, use `publish-npm-oidc.yml` if the package goes to npm — change the `tags:` trigger to `- "v*"` and set `__PACKAGE_PATH__` to `.`.
