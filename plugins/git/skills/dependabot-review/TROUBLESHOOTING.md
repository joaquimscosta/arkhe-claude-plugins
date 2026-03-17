# Dependabot Review: Troubleshooting

Solutions to common issues when using the `dependabot-review` skill.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).
For examples, see [EXAMPLES.md](EXAMPLES.md).

---

## Common Issues

### Issue 1: CI Fails on All Dependabot PRs

**Symptom**: Every Dependabot PR shows CI failures, even trivial patches.

**Cause**: Dependabot PRs run with a read-only `GITHUB_TOKEN` and cannot access repository Actions secrets. Any workflow step that requires secrets (API keys, deploy tokens, private registry auth) will fail.

**Solutions**:

**Solution A: Add Dependabot-specific secrets**

Go to Settings > Security > Dependabot secrets and add the required env vars there. These are separate from Actions secrets.

**Solution B: Skip steps for Dependabot**

In your workflow, conditionally skip steps that need secrets:

```yaml
- name: Deploy
  if: github.actor != 'dependabot[bot]'
  run: ...
```

**Solution C: Merge despite failures**

If the failure is clearly unrelated (lockfile-only change, missing env var error), the skill will flag it as pre-existing and the PR can be merged with `--admin` flag:

```bash
gh pr merge <number> --squash --admin
```

---

### Issue 2: Merge Conflicts on Lock Files

**Symptom**: PR shows `CONFLICTING` status. Common when multiple Dependabot PRs are open simultaneously.

**Cause**: Multiple PRs touch the same lockfile. After merging one, the others conflict.

**Solutions**:

**Solution A: Rebase via Dependabot**

```bash
gh pr comment <number> --body "@dependabot rebase"
```

Dependabot will regenerate the lockfile against the current base branch within a few minutes.

**Solution B: Batch merge order**

Merge PRs one at a time, rebasing conflicted ones after each merge. The skill handles this automatically when using `--merge-safe`.

---

### Issue 3: `--squash` Not Allowed on Repository

**Symptom**: `gh pr merge --squash` fails with "Squash merges are not allowed on this repository".

**Cause**: Repository settings only allow certain merge strategies.

**Solution**: The skill automatically falls back:
1. Try `--squash`
2. If fails, try `--merge`
3. If fails, try `--rebase`

If all fail, check repo settings: Settings > Pull Requests > Allow merge commits / squash / rebase.

---

### Issue 4: PRs Targeting Wrong Base Branch

**Symptom**: Dependabot PRs target `main` but you want them on `develop`.

**Cause**: Dependabot defaults to the repo's default branch. The `dependabot.yml` config can override this with `target-branch`.

**Solutions**:

**Solution A: Retarget in the skill**

The skill asks for the target branch before merging and retargets automatically:

```bash
gh pr edit <number> --base develop
```

**Solution B: Configure Dependabot**

Update `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/apps/web"
    schedule:
      interval: "weekly"
    target-branch: "develop"
```

---

### Issue 5: Grouped PR Contains Unexpected Packages

**Symptom**: A grouped Dependabot PR includes packages you didn't expect, or is missing packages from the group.

**Cause**: Known Dependabot issue with grouped updates (#10487). Group membership can be inconsistent.

**Solutions**:

**Solution A: Recreate the PR**

```bash
gh pr comment <number> --body "@dependabot recreate"
```

**Solution B: Review individual packages**

Use `--pr <number>` mode to see the full package breakdown and assess each update individually.

---

### Issue 6: `gh` CLI Not Authenticated

**Symptom**: All commands fail with authentication errors.

**Solution**:

```bash
gh auth status
gh auth login
```

Ensure the token has `repo` scope for private repositories.

---

### Issue 7: No Dependabot PRs Found

**Symptom**: Skill reports "No open Dependabot PRs found" but you expected some.

**Causes**:
- Dependabot is not enabled: Check Settings > Security > Code security > Dependabot
- PRs were auto-closed: Dependabot closes PRs after 30 days of inactivity
- Wrong repository: Verify you're in the correct repo with `gh repo view`

**Verification**:

```bash
gh pr list --author "app/dependabot" --state all --limit 10
```

This shows both open and closed Dependabot PRs to confirm whether any were created.

---

## Dependabot Comment Commands Reference

These commands can be posted as PR comments to control Dependabot:

| Command | Effect |
|---------|--------|
| `@dependabot rebase` | Rebase PR against current base (fixes lock conflicts) |
| `@dependabot recreate` | Close and recreate the PR from scratch |
| `@dependabot merge` | Merge when CI passes (Dependabot handles it) |
| `@dependabot squash and merge` | Squash merge when CI passes |
| `@dependabot cancel merge` | Cancel a pending auto-merge |
| `@dependabot close` | Close the PR |
| `@dependabot ignore this major version` | Ignore this major version forever |
| `@dependabot ignore this minor version` | Ignore this minor version forever |
| `@dependabot ignore this dependency` | Ignore this dependency forever |

---

## Getting Help

- [GitHub Dependabot docs](https://docs.github.com/en/code-security/dependabot)
- [GitHub CLI docs](https://cli.github.com/manual/)
- File issues at the plugin repository
