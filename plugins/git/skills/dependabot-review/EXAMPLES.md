# Dependabot Review: Examples

Real-world scenarios showing the skill in action.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).

---

## Example 1: Standard Triage with Mixed PRs

### Scenario
A Next.js + Spring Boot monorepo has 5 open Dependabot PRs after a week away.

### Command
```bash
/dependabot-review
```

### Execution

**Discovery**: Fetches 5 PRs, enriches with file diffs and CI status.

**Classification & Report**:

```
## Dependabot PR Triage — deznode/nosilha
5 open PRs found

### SAFE TO MERGE (2)
| PR | Package | From -> To | Type | Scope | CI | Files |
|----|---------|-----------|------|-------|----|-------|
| #129 | undici | 7.22.0 -> 7.24.3 | patch | indirect | fail* | lockfile |
| #125 | actions group (13) | various | minor | actions | none | workflows |

*CI failure is pre-existing — lockfile-only changes cannot cause lint failures

### REVIEW RECOMMENDED (1)
| PR | Package | From -> To | Type | Reason | CI |
|----|---------|-----------|------|--------|----|
| #126 | npm group (39) | various | mixed | includes shiki 3->4 (major), framework minors | none |

### REQUIRES HUMAN REVIEW (1)
| PR | Package | From -> To | Type | Reason |
|----|---------|-----------|------|--------|
| #102 | hashicorp/google | 6.39.0 -> 7.23.0 | major | Terraform provider major version |

### BLOCKED (1)
| PR | Package | Issue | Action |
|----|---------|-------|--------|
| #127 | gradle group (10) | conflict | `@dependabot rebase` |
```

**User chooses**: "Merge the 2 safe ones to develop"

**Actions**:
```
What branch should these PRs target? develop

Retargeting #129 from main -> develop... done
Retargeting #125 from main -> develop... done
Merging #129 (undici 7.22->7.24.3)... merged
Merging #125 (actions group)... merged

## Summary
- Merged: 2 PRs (#129, #125)
- Remaining: 3 PRs (1 review, 1 human review, 1 blocked)
```

---

## Example 2: Security Update Expedited

### Scenario
A critical security vulnerability is reported in a transitive dependency.

### Command
```bash
/dependabot-review
```

### Report

```
## Dependabot PR Triage — myorg/myapp
3 open PRs found

### SAFE TO MERGE (2)
| PR | Package | From -> To | Type | Scope | CI |
|----|---------|-----------|------|-------|----|
| #45 | lodash | 4.17.20 -> 4.17.21 | patch | direct:prod | pass |
| #44 | @types/node | 20.11 -> 20.12 | minor | dev | pass |

> **SECURITY**: #45 (lodash) has the `security` label — prototype pollution fix (CVE-2024-XXXX)

### REVIEW RECOMMENDED (1)
| PR | Package | From -> To | Type | Reason | CI |
|----|---------|-----------|------|--------|----|
| #43 | express | 4.18 -> 4.19 | minor | framework | pass |
```

### Key Takeaway
Security PRs are always surfaced prominently with a callout, even when they fall into the SAFE tier. The skill highlights the CVE context from the PR body.

---

## Example 3: Grouped PR with Major Bump

### Scenario
Dependabot groups npm dependencies. One package in the group has a major bump.

### Command
```bash
/dependabot-review --pr 126
```

### Deep-Dive Output

```
## PR #126: bump the dependencies group (39 updates)

### Package Breakdown
| Package | From | To | Semver | Risk |
|---------|------|----|--------|------|
| @next/third-parties | 16.0.3 | 16.1.6 | minor | framework |
| shiki | 3.20.0 | 4.0.2 | MAJOR | breaking |
| react | 19.2.0 | 19.2.4 | patch | safe |
| framer-motion | 12.23.26 | 12.36.0 | minor | framework |
| zod | 4.2.1 | 4.3.6 | minor | safe |
| ... (34 more) | | | | |

### Risk Assessment: REQUIRES HUMAN REVIEW
- Contains 1 major bump: shiki 3 -> 4
- Contains 5 framework minors: next, react, framer-motion, supabase-js, mapbox-gl
- 39 total updates — large blast radius

### Recommendation
Do NOT auto-merge. The shiki 3->4 major bump likely has breaking API changes.

Options:
1. **Wait for Dependabot to split**: Close this PR, configure Dependabot to separate major updates
2. **Merge and fix**: Merge to a feature branch, resolve any shiki breaking changes
3. **Comment `@dependabot recreate`**: Force Dependabot to regenerate without the major bump (may not work for grouped updates)

### Files Changed
- apps/web/package.json (39 additions, 39 deletions)

### CI Status
No checks ran (grouped PRs often lack CI due to base branch conflicts)
```

---

## Example 4: CI Failure from Missing Secrets

### Scenario
A Dependabot PR fails CI, but the dependency change is trivial.

### Command
```bash
/dependabot-review
```

### Report (BLOCKED section)

```
### BLOCKED (1)
| PR | Package | Issue | Action |
|----|---------|-------|--------|
| #88 | undici | 7.22 -> 7.24 | CI fail |

#### CI Failure Diagnosis for #88:
- Files changed: `pnpm-lock.yaml` (lockfile only)
- Failed checks: "Lint & Type Check", "Bundle Size Analysis"
- Error: `Missing required environment variable: NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN`

**Diagnosis**: Dependabot PRs cannot access repository Actions secrets.
The lockfile-only change cannot cause lint or build failures.
These failures are pre-existing on the base branch.

**Recommendation**: Safe to merge despite CI failures. Use `--merge-safe` or
merge manually with `gh pr merge 88 --squash --admin`.
```

### Key Takeaway
The skill distinguishes between CI failures caused by the dependency update vs pre-existing issues or Dependabot secret limitations.

---

## Common Patterns

1. **Lockfile-only PRs**: Almost always safe — the actual dependency versions are controlled by the manifest file, and lockfile changes just pin transitive dependencies
2. **Grouped PRs**: Check every package in the group — one major bump contaminates the entire PR
3. **GitHub Actions**: Minor bumps are safe (they use major version tags); major bumps need workflow syntax review
4. **Terraform providers**: Major bumps are high risk — always run `terraform plan` before merging
5. **Security PRs**: Merge quickly — they exist because a vulnerability was found
