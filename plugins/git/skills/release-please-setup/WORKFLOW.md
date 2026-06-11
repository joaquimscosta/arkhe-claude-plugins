# Release-Please Setup: Detailed Runbook

## Greenfield flow

Use when starting fresh — no prior release tags.

### 1. Discover and dry-run

```bash
# Substitute the absolute path to this skill's scripts/ directory
SCRIPTS=/path/to/plugins/git/skills/release-please-setup/scripts

python3 "$SCRIPTS/release_please_setup.py" --root . --dry-run
```

Review the printed `release-please-config.json` and `.release-please-manifest.json`.

- Every discovered package starts at `0.0.0`. Override with `--initial 1.0.0` if you want a different starting version.
- Default discovery globs: `packages/*`, `backend/*`, `frontend/*`. Override with `--globs packages/*,apps/*` etc.
- Monorepos get a mutual `exclude-paths` matrix so each package only triggers its own Release PR.
- Single-package repos (auto-detected when ≤1 package, or `--single`) get a minimal entry without component-in-tag; tags are `v<semver>`.

### 2. Write the files

```bash
python3 "$SCRIPTS/release_please_setup.py" --root .
```

This writes `release-please-config.json` and `.release-please-manifest.json` at the repo root.

### 3. Add the release-please workflow

```bash
mkdir -p .github/workflows
cp "$SKILLS/release-please-setup/templates/release-please.yml" .github/workflows/
```

### 4. Set REPO_TOKEN secret

In GitHub → repo Settings → Secrets → Actions, add a secret named `REPO_TOKEN` containing a PAT with `repo` scope (or a GitHub App installation token).

**Why required:** GITHUB_TOKEN-created tags do not trigger other workflows. Without REPO_TOKEN, release-please pushes the tag but every tag-keyed deploy workflow is silently skipped. See CONTRACT.md.

### 5. Pick and copy a deploy template (optional)

Pick one or more from `templates/`:

| Template | Trigger tag pattern |
|---|---|
| `deploy-fly.yml` | `__COMPONENT__-v*` |
| `publish-npm-oidc.yml` | `__COMPONENT__-v*` |
| `release-asset.yml` | `__COMPONENT__-v*` |
| `deploy-docker-matrix.yml` | `*-v*` (derives component at runtime) |
| `deploy-frontend-host.yml` | `__COMPONENT__-v*` |
| `deploy-generic.yml` | `__COMPONENT__-v*` |

```bash
cp templates/deploy-fly.yml .github/workflows/deploy-skrebe-web.yml
```

### 6. Fill placeholders

Replace every `__TOKEN__` in the copied template. See the placeholder reference table below.

### 7. Set the GitHub secrets the template needs

Consult the template's `env:` blocks. Common secrets: `FLY_API_TOKEN`, `AWS_ECR_ROLE_ARN`, `AWS_REGION`, `ECR_REPOSITORY`, `DEPLOY_SECRET` (generic).

### 8. Commit

```bash
git add release-please-config.json .release-please-manifest.json .github/workflows/
git commit -m "chore: scaffold release-please"
git push origin main
```

### 9. First merge to main opens Release PRs

After the commit lands on main, the `release-please.yml` workflow runs and opens one Release PR per package. Merging a Release PR cuts the tag, creates the GitHub Release, and fires any tag-keyed deploy workflow.

---

## Migration flow (existing manual-tag repo)

Use when a repo already has `<component>-v*` tags created by hand (like papia-studio).

### Key principle

Release-please's monorepo tag format (`<component>-v<semver>`) is **byte-identical** to a hand-maintained `<component>-v*` scheme. Existing `push: tags:` workflows keep working unchanged — no deploy-side edits are required on day one.

### 1. Run with --migrate

```bash
python3 "$SCRIPTS/release_please_setup.py" --root . --migrate --dry-run
```

The script:
- Detects the current version from `package.json` / `pyproject.toml` / `gradle.properties`.
- Falls back to the highest `<component>-v*` git tag for packages where file-based detection found nothing.
- Seeds the manifest with detected versions so release-please starts from the right baseline.

### 2. Review and write

```bash
python3 "$SCRIPTS/release_please_setup.py" --root . --migrate
```

### 3. Add release-please.yml, set REPO_TOKEN, pick deploy templates

Same steps 3–8 as the greenfield flow above.

### 4. What to STOP doing

After release-please is adopted:

- ✅ Stop bumping version fields manually in `package.json` / `pyproject.toml`.
- ✅ Stop writing CHANGELOG entries by hand.
- ✅ Stop pushing `<component>-v*` tags by hand.

Release-please does all three when you merge its Release PR.

### 5. What to KEEP

- ✅ Keep existing `push: tags: ["<component>-v*"]` publish and deploy workflows — they keep firing.
- ✅ Keep per-package `CHANGELOG.md` files — release-please appends to them.

### 6. Out of scope: umbrella narrative releases

Umbrella `vX.Y.Z` releases (a project-state snapshot that isn't tied to any single package) have no release-please equivalent. If your repo uses an umbrella scheme alongside per-package schemes, keep the umbrella releases manual. Release-please manages the per-package tracks only.

---

## Placeholder reference table

Every template uses a subset of these `__TOKEN__` placeholders. Replace all that appear in the file you copied.

| Token | What to fill |
|---|---|
| `__COMPONENT__` | Tag prefix and component name, e.g. `user-service`, `skrebe-web`, `text-cli` |
| `__PACKAGE_PATH__` | Relative path to the package directory, e.g. `packages/text-cli`, `frontend/sellabella-ui` |
| `__APP__` | Human-readable Fly app display name used in the workflow name, e.g. `Skrebe Web` |
| `__APP_ID__` | Host platform app identifier, e.g. Amplify app-id (`d1abc23xyz`) |
| `__ARTIFACT_NAME__` | Base filename for the release asset (without version suffix), e.g. `my-extension` (produces `my-extension-1.2.3.vsix`) |
| `__BUILD_ARG_NAME__` | Build-time public env var name passed as `--build-arg` to Docker, e.g. `NEXT_PUBLIC_API_URL` |
| `__BUILD_ARG_SECRET__` | GitHub secret name whose value is passed as `__BUILD_ARG_NAME__`, e.g. `NEXT_PUBLIC_API_URL_SECRET` |
| `__DEPLOY_SECRET__` | GitHub secret name for the generic deploy token (deploy-generic.yml), e.g. `DEPLOY_TOKEN` |
| `__DOCKERFILE_PATH__` | Relative path to the Dockerfile, e.g. `backend/user-service/Dockerfile` |
| `__BUILD_CONTEXT__` | Docker build context path, e.g. `.` or `backend/user-service` |

Tokens present per template:

| Template | Tokens used |
|---|---|
| `deploy-fly.yml` | `__COMPONENT__`, `__APP__`, `__PACKAGE_PATH__`, `__BUILD_ARG_NAME__`, `__BUILD_ARG_SECRET__` |
| `publish-npm-oidc.yml` | `__COMPONENT__`, `__PACKAGE_PATH__` |
| `release-asset.yml` | `__COMPONENT__`, `__PACKAGE_PATH__`, `__ARTIFACT_NAME__` |
| `deploy-docker-matrix.yml` | `__COMPONENT__`, `__DOCKERFILE_PATH__`, `__BUILD_CONTEXT__` |
| `deploy-frontend-host.yml` | `__COMPONENT__`, `__PACKAGE_PATH__`, `__APP_ID__` |
| `deploy-generic.yml` | `__COMPONENT__`, `__PACKAGE_PATH__`, `__DEPLOY_SECRET__` |
