---
description: Automate semantic versioning releases or scaffold release infrastructure
argument-hint: <version> | --setup [--skip-monitor]
---

# Release Command

Automate the full release process: validate CHANGELOG, update comparison links, commit, trigger GitHub Actions workflow, and monitor completion. Or scaffold release infrastructure for new projects.

## Usage

```bash
/release <version>                 # Execute release (e.g., /release 1.6.0)
/release --setup                   # Scaffold release infrastructure
/release <version> --skip-monitor  # Trigger without monitoring
```

## Examples

```bash
/release 1.6.0                    # Release version 1.6.0
/release v2.0.0                   # Works with 'v' prefix too
/release --setup                  # Create release.sh, workflow, and helper scripts
```

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- CHANGELOG.md entry for the version (use `/changelog` first)
- `.github/workflows/release.yml` exists (use `--setup` to create)

## Implementation

Invoke the Skill tool with skill name "git:releasing" and arguments: $ARGUMENTS

The skill handles version validation, CHANGELOG checks, comparison link management, commit/push, workflow triggering, and monitoring.
