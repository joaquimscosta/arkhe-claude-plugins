# Release Skill: Troubleshooting

## Common Issues

### "No CHANGELOG entry found for version X.Y.Z"

**Cause:** CHANGELOG.md doesn't have a `## [X.Y.Z]` header.

**Fix:**
```bash
# Generate the entry
/changelog --version X.Y.Z

# Or manually add the header
echo "## [X.Y.Z] - $(date +%Y-%m-%d)" >> CHANGELOG.md
```

### "Release vX.Y.Z already exists"

**Cause:** A GitHub Release with this tag already exists.

**Fix:**
```bash
# Delete the existing release
gh release delete vX.Y.Z --yes

# Optionally delete the tag too
git push origin --delete vX.Y.Z
git tag -d vX.Y.Z

# Retry
/release X.Y.Z
```

### "Invalid version format"

**Cause:** Version doesn't match semantic versioning (`X.Y.Z`).

**Valid formats:**
- `1.6.0`
- `v1.6.0` (v prefix is stripped automatically)

**Invalid formats:**
- `1.6` (missing patch)
- `1.6.0-beta` (pre-release suffixes not supported)
- `v1.6` (missing patch even with prefix)

### "Could not find workflow run"

**Cause:** The workflow didn't start within the 5-second wait period, or the workflow file doesn't exist.

**Fix:**
1. Check the workflow exists:
   ```bash
   gh workflow list
   ```
2. If missing, scaffold it:
   ```bash
   /release --setup
   ```
3. If it exists but didn't trigger, check permissions:
   ```bash
   gh api repos/{owner}/{repo}/actions/permissions
   ```

### gh CLI Not Authenticated

**Cause:** `gh` CLI is not installed or not authenticated.

**Fix:**
```bash
# Install gh CLI
brew install gh    # macOS
# or see https://cli.github.com/

# Authenticate
gh auth login
```

### "Could not find [Unreleased] link to update"

**Cause:** CHANGELOG.md doesn't have an `[Unreleased]:` link reference at the bottom.

**Fix:** Add the link reference manually:
```markdown
[Unreleased]: https://github.com/user/repo/compare/vX.Y.Z...HEAD
```

### Workflow Fails with "CHANGELOG entry not found"

**Cause:** The CHANGELOG.md was not pushed to the remote before the workflow ran.

**Fix:** Ensure Step 4 (commit and push) completed before the workflow triggers. Re-run:
```bash
git push origin main
/release X.Y.Z
```

### Setup Files Already Exist

**Cause:** Running `--setup` when release infrastructure already exists.

**Fix:** The skill will warn about existing files. Choose to:
- **Overwrite** — Replace with latest templates
- **Skip** — Keep existing files unchanged

### sed Errors on macOS vs Linux

**Cause:** `sed -i` behaves differently on macOS (BSD) and Linux (GNU).

**Fix:** The scripts use `sed -i.bak` which works on both platforms. The `.bak` files are cleaned up automatically with `rm -f *.bak`.

## Debugging Tips

### Check Workflow Status Manually

```bash
# List recent workflow runs
gh run list --workflow=release.yml --limit=5

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

### Verify CHANGELOG Format

```bash
# Check version headers
grep -E "^## \[" CHANGELOG.md

# Check link references
grep -E "^\[" CHANGELOG.md | tail -10
```

### Test Release Script Locally

```bash
# Dry run (validate only, don't trigger)
# Check prerequisites
gh auth status
gh repo view --json url -q '.url'
grep -E "^## \[1.6.0\]" CHANGELOG.md
gh release view v1.6.0 2>/dev/null; echo "Exit: $?"
```
