# Release-Please Contract

Release-please produces a **stable contract**: on every merge to `main` it maintains
a Release PR; when that PR is merged it pushes a semver Git tag, creates a GitHub
Release, and surfaces per-package job outputs. Deploy and publish workflows are
consumers of that contract — they never need to know how a tag was born, only that
it exists and follows a predictable format. All templates in this skill key on the
**tag**, making them interchangeable between a release-please-managed repo and one
where tags are pushed by hand.

---

## Tag format

When `release-please-config.json` sets `include-component-in-tag: true` and
`tag-separator: "-"` (the monorepo defaults this skill generates), release-please
creates tags of the form:

```
<component>-v<semver>
```

Examples: `text-cli-v0.3.0`, `user-service-v3.1.2`, `analytics-service-v2.3.0`.

Single-package repos (no `include-component-in-tag`) produce the simpler form:

```
v<semver>
```

Example: `v1.4.2`.

**Key consequence:** The monorepo tag format is byte-identical to a hand-maintained
`<component>-v*` tagging scheme. Any existing `push: tags: ["<component>-v*"]`
deploy or publish workflow keeps working after adopting release-please — no changes
to the deploy side are required on day one.

---

## The token gotcha (READ THIS) ⚠️

Tags and releases created using the default `GITHUB_TOKEN` do **NOT** trigger other
workflows. This is GitHub's recursive-workflow guard: a workflow token cannot cause
another workflow to run.

**Consequence:** a `push: tags` deploy workflow will **silently do nothing** when
release-please creates the tag with `GITHUB_TOKEN`. The tag lands, the Release is
created, and every downstream workflow is skipped — no error, no warning.

**Fix:** give release-please a token that bypasses the guard:

- A **PAT** (Personal Access Token) with `repo` scope, stored as a repository or
  organisation secret — conventionally `secrets.REPO_TOKEN`.
- A **GitHub App** installation token (preferred at scale; avoids attaching a token
  to a human account).

The `release-please.yml` template in this skill uses:

```yaml
token: ${{ secrets.REPO_TOKEN || secrets.GITHUB_TOKEN }}
```

The `|| secrets.GITHUB_TOKEN` fallback lets the workflow run in forks or repos where
`REPO_TOKEN` hasn't been provisioned yet (useful during initial setup), while
production repos should always have `REPO_TOKEN` set, and most real setups
use `secrets.REPO_TOKEN` for exactly this reason.

✅ With `REPO_TOKEN`: release-please pushes tag → tag-keyed deploy workflows fire.  
❌ With `GITHUB_TOKEN` only: release-please pushes tag → deploy workflows are skipped.

---

## Job outputs

`googleapis/release-please-action` exposes per-package boolean and string outputs on
the step identified by its `id` (conventionally `release`). The access pattern for
multi-package repos uses the package path as a key prefix:

```
steps.<id>.outputs['<package-path>--release_created']   # "true" / ""
steps.<id>.outputs['<package-path>--tag_name']           # e.g. "text-cli-v0.3.0"
steps.<id>.outputs['<package-path>--version']            # e.g. "0.3.0"
steps.<id>.outputs['<package-path>--major']              # e.g. "0"
steps.<id>.outputs['<package-path>--minor']              # e.g. "3"
steps.<id>.outputs['<package-path>--patch']              # e.g. "0"
```

The top-level `releases_created` output is `"true"` if **any** package was released.

**Real-world example** — propagating the output to a downstream deploy job:

```yaml
outputs:
  frontend-release-created: ${{ steps.release.outputs['frontend/acme-ui--release_created'] }}
```

A downstream job then conditions on:

```yaml
if: needs.release-please.outputs.frontend-release-created == 'true'
```

Use job outputs when you want to gate a **same-workflow** deploy step on whether a
specific package was released, as an alternative to a separate tag-keyed workflow.

---

## The `release: published` fan-out variant

Instead of `push: tags`, a workflow can trigger on:

```yaml
on:
  release:
    types: [published]
```

and derive the component name at runtime:

```bash
COMPONENT=$(echo "${{ github.event.release.tag_name }}" | sed 's/-v[0-9]*\.[0-9]*\.[0-9]*$//')
```

This is the pattern used by a `release-affected-services.yml` workflow that
builds all affected backend services from a single release event using a matrix.

**Trade-offs:**

| Approach | Tag-keyed (`push: tags`) | Release-event (`release: published`) |
|---|---|---|
| Trigger source | Tag push | GitHub Release published |
| Portability | Works with manual tags too | Coupled to GitHub Release creation |
| Workflow count | One workflow per component | One centralised workflow |
| Fan-out | Each component triggers its own | Matrix over affected services |
| Complexity | Lower — easy to reason about | Higher — matrix logic centralised |

This skill ships **tag-keyed templates as primary** because they are portable (work
before and after adopting release-please), simpler to audit, and require no changes
when a repo starts from manual tagging. Adapt to the release-event approach when you
need a single workflow to fan out across a matrix of services.

---

## PyPI (not yet a first-class template)

Publishing to PyPI is not shipped as a template in this skill yet. The pattern to
adapt is `publish-npm-oidc.yml` — replace the npm publish step with PyPI Trusted
Publishing using OIDC (no long-lived token required):

```yaml
permissions:
  id-token: write   # required for OIDC Trusted Publishing

steps:
  - uses: actions/checkout@v6

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: "3.12"

  - name: Build distributions
    run: pip install build && python -m build

  - name: Publish to PyPI
    uses: pypa/gh-action-pypi-publish@release/v1
    # No token: OIDC Trusted Publishing handles auth automatically.
    # Configure the trusted publisher in your PyPI project settings first.
```

Configure the Trusted Publisher in your PyPI project at
`https://pypi.org/manage/project/<name>/settings/publishing/` before the first
publish run. No `PYPI_TOKEN` secret is needed once OIDC is set up.
