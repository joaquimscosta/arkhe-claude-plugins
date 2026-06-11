# Release-Please Setup: Troubleshooting

---

## Release PR not created

**Symptom:** The `release-please.yml` workflow runs on every push to main but never opens a Release PR.

**Causes and fixes:**

1. **No qualifying commits.** Release-please only bumps a version when it sees a [Conventional Commits](https://conventionalcommits.org) type that maps to a release. `feat:` → minor, `fix:` / `perf:` → patch, `feat!:` / `fix!:` → major. `chore:`, `docs:`, `test:`, `ci:` do not trigger a release by default. If every commit since the last release is `chore:`, no PR is created — that is correct behaviour.

2. **Not on the default branch.** Release-please only watches `push: branches: [main]`. If your default branch is `master` or something else, update `release-please.yml` accordingly.

3. **Insufficient workflow permissions.** The workflow needs `contents: write` and `pull-requests: write`. Check the `permissions:` block in `.github/workflows/release-please.yml`. If the organisation has restricted default permissions, you must set these explicitly.

4. **Config or manifest file not found.** Confirm `release-please-config.json` and `.release-please-manifest.json` are committed at the repo root and the `config-file` / `manifest-file` paths in the workflow match.

---

## Deploy workflow didn't fire after the release

**Symptom:** Release-please merged the Release PR, the tag exists, the GitHub Release was created, but your `push: tags:` deploy workflow never ran (or the Actions tab shows no run at all).

**Root cause: the REPO_TOKEN gotcha.** ⚠️

Tags and releases created by `GITHUB_TOKEN` do **not** trigger other workflows. This is GitHub's recursive-workflow guard. The tag lands silently — no error, no warning, no deploy.

**Fix:** Set a PAT (Personal Access Token with `repo` scope) as a repository secret named `REPO_TOKEN`. The `release-please.yml` template in this skill already uses:

```yaml
token: ${{ secrets.REPO_TOKEN || secrets.GITHUB_TOKEN }}
```

The fallback allows the workflow to run without `REPO_TOKEN` (useful during setup), but deploy workflows will only fire once `REPO_TOKEN` is set.

See CONTRACT.md for the full explanation and GitHub App token as an alternative.

---

## Wrong version in manifest after migration

**Symptom:** After running `--migrate`, some packages have `"0.0.0"` in `.release-please-manifest.json` instead of their current version. Release-please would then try to release from `0.0.0`, potentially creating conflicting tags.

**Causes and fixes:**

1. **File-based detection found nothing.** Discovery reads `package.json` → `version`, `pyproject.toml` → `[project].version` or `[tool.poetry].version`, `gradle.properties` → `version`. If none of those exist or the field is absent, detection returns `None` and the git-tag fallback runs. If there are no `<component>-v*` tags either, the manifest falls back to `0.0.0`.

   **Fix:** Add a `version` field to the package file, then re-run `--migrate`. Or edit `.release-please-manifest.json` directly after writing, setting the correct version.

2. **Package name in git tag doesn't match the discovered `name`.** The orchestrator looks for tags matching `<name>-v*` where `name` is derived from `package.json` `name` (stripped of `@scope/`) or the directory name. A mismatch means no tag is found.

   **Fix:** Edit `.release-please-manifest.json` manually and set the correct version for affected packages.

---

## Tag/version mismatch error in deploy

**Symptom:** Deploy workflow fails with `::error::Tag 'my-service-v1.2.0' does not match expected 'my-service-v1.3.0'` (or similar).

**Root cause:** The deploy template reads the version from `package.json` (or equivalent) and compares it to `github.ref_name`. They don't match.

**Causes:**

- The version in `package.json` was bumped manually after release-please already created the Release PR. Release-please bumped it to `1.3.0` in its PR, but someone also bumped it to `1.2.0` on a separate commit.
- A stale tag was pushed by hand that doesn't correspond to the current file version.

**Fix:** Ensure the tag being pushed matches `package.json` `version`. If using release-please, never bump the version manually — let the Release PR do it. If you pushed a manual tag, either fix `package.json` to match, delete the tag and retag after fixing, or skip the verify step for a one-off emergency deploy.

---

## Python version not detected

**Symptom:** Migration mode seeds `"0.0.0"` for a Python package even though `pyproject.toml` exists.

**Root cause:** The discovery script reads `version` only from `[project]` or `[tool.poetry]` tables in `pyproject.toml`. Other table names (e.g. `[tool.hatch.version]` dynamic versioning, `[tool.setuptools.dynamic]`) are not supported.

**Fix:** Add a `version = "x.y.z"` line under `[project]` or `[tool.poetry]` in `pyproject.toml`, re-run `--migrate --dry-run`, and verify the manifest shows the correct version.

---

## release-type wrong for a package

**Symptom:** The generated config has `"release-type": "simple"` for a Node.js package (or vice versa), and release-please uses the wrong bump / changelog strategy.

**Root cause:** Discovery maps:
- `package.json` present → `node`
- `pyproject.toml` present (and no `package.json`) → `python`
- `build.gradle` or `build.gradle.kts` present (and none of the above) → `simple`
- Anything else → `simple`

If the package directory has an unexpected layout (e.g. a Python package with only a `setup.py`, no `pyproject.toml`), discovery falls back to `simple`.

**Fix:** Edit the generated `release-please-config.json` and change `"release-type"` to the correct value (`node`, `python`, `simple`, `go`, `java`, etc.). See the [release-please release types documentation](https://github.com/googleapis/release-please/blob/main/docs/release-types.md) for the full list. The config file is plain JSON and safe to edit by hand.
