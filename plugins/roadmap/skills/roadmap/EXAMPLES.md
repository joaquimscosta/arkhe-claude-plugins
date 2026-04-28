# Roadmap Skill — Examples

Usage examples for the Roadmap Analyst skill.

## Example 1: Status Dashboard

**Input:** `/roadmap:roadmap status`

**Output:**

```
## Project Status Dashboard
_Generated: 2026-02-17_

### Module Overview

| Module | Backend | Frontend | Maturity | Notes |
|--------|---------|----------|----------|-------|
| auth | JWT + refresh tokens | Login page + protected routes | API Ready | Missing MFA |
| catalog | CRUD endpoints | List + detail pages | Tested | Good coverage |
| orders | Service layer only | Not started | Service Layer | No controllers yet |
| payments | Stub (Stripe types) | Not started | Stub | Blocked on Stripe setup |
| notifications | Not started | Not started | — | Not yet considered |

### Working Features
- User authentication: `src/auth/` (JWT, refresh, logout)
- Catalog browsing: `src/catalog/` (6 endpoints, paginated)
- Product search: `src/catalog/search.ts` (full-text via Postgres)

### Planned Features
- Order management: spec exists (`arkhe/specs/003-orders/spec.md`)
- Payment processing: referenced in roadmap, no spec yet

### Missing / Not Started
- Notifications: no docs, no code
- Admin dashboard: mentioned in README but no further planning

### Recommended Next Actions
1. Complete orders module (controllers + frontend) — spec ready
2. Create payment spec — blocks revenue features
3. Design notification system — growing user need
```

## Example 2: Gap Analysis

**Input:** `/roadmap:roadmap gaps`

**Output:**

```
## Gap Analysis Tracking

| Gap | Source | Status | Evidence |
|-----|--------|--------|----------|
| No rate limiting | api-gap-analysis.md | Open | No middleware found |
| Missing input validation | api-gap-analysis.md | Closed | `src/middleware/validate.ts` |
| No error boundaries | design-gap-analysis.md | In Progress | `ErrorBoundary.tsx` exists, not wired to all routes |
| No loading states | design-gap-analysis.md | Closed | Skeleton components in `src/components/ui/` |
| No audit trail | security-review.md | Open | No logging beyond console |
| No backup strategy | infra-review.md | Open | No backup scripts or config |

### Summary
- **Total gaps:** 6
- **Closed:** 2 (33%)
- **In Progress:** 1 (17%)
- **Open:** 3 (50%)

### Priority Open Gaps
1. Rate limiting — security risk, should address before launch
2. Audit trail — compliance requirement
3. Backup strategy — data loss risk
```

## Example 3: Blockers Analysis

**Input:** `/roadmap:roadmap blockers`

**Output:**

```
## Blocking Chain Analysis

### Critical Path
Stripe API keys → Payment module → Order checkout → Revenue features

### Blocking Items

| Blocker | Blocks | Owner | Needed Action |
|---------|--------|-------|---------------|
| Stripe API keys not provisioned | Payment module | DevOps | Request sandbox keys |
| Payment module stub | Order checkout flow | Backend | Implement after Stripe |
| No CI/CD pipeline | Production deployment | DevOps | Set up GitHub Actions |
| Design system incomplete | All new UI work | Frontend | Finish token migration |

### External Dependencies
- **Stripe**: Sandbox access needed. No ETA from provider.
- **DNS**: Domain purchased but not configured for production.

### Unblocking Recommendations
1. Request Stripe sandbox keys immediately (unblocks payment → orders)
2. Set up CI/CD pipeline (unblocks deployments)
3. Complete design token migration (unblocks UI work)
```

## Example 4: Delta Report

**Input:** `/roadmap:roadmap delta`

**Output:**

```
## Delta Report
_Comparing PROJECT-STATUS.md (2026-02-10) vs current codebase_

### New Since Last Update
- 3 new migration files: V005, V006, V007
- New module: `src/search/` (full-text search)
- 12 new test files in `tests/catalog/`
- New component: `SearchBar.tsx`

### Gaps Closed
- Input validation: now present in all API routes
- Loading states: skeleton components added

### New Issues
- `src/orders/checkout.ts` has TODO: "implement payment integration"
- Test coverage dropped in `auth` module (removed 2 test files)

### Metrics
| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Source files | 47 | 58 | +11 |
| Test files | 23 | 33 | +10 |
| Migrations | 4 | 7 | +3 |
| API endpoints | 12 | 15 | +3 |
```

## Example 5: Risk Register

**Input:** `/roadmap:roadmap risks`

**Output:**

```
## Risk Register

| # | Risk | Likelihood | Impact | Score | Mitigation |
|---|------|-----------|--------|-------|------------|
| 1 | No rate limiting | High | High | Critical | Add express-rate-limit before launch |
| 2 | Single point of failure (1 server) | Medium | High | High | Plan horizontal scaling |
| 3 | No backup strategy | Low | High | Medium | Implement daily DB backups |
| 4 | Payment integration delay | Medium | Medium | Medium | Build order system without payments first |
| 5 | Design system debt | Medium | Low | Low | Schedule token migration sprint |
```

## Example 6: Spec Pipeline

**Input:** `/roadmap:roadmap specs`

**Output:**

```
## Spec Pipeline

| Spec | Title | Status | Evidence |
|------|-------|--------|----------|
| 001-auth | Authentication | Complete | All endpoints live, tests passing |
| 002-catalog | Product Catalog | Complete | CRUD + search implemented |
| 003-orders | Order Management | In Progress | Service layer only, no controllers |
| 004-payments | Payment Processing | Proposed | Spec exists, no implementation |
| 005-notifications | Notifications | — | No spec, no implementation |

### Summary
- **Complete:** 2/4 (50%)
- **In Progress:** 1/4 (25%)
- **Proposed:** 1/4 (25%)
- **No Spec:** 1 feature mentioned in roadmap but not specified
```

## Example 7: Update with Git History (Phase A + B)

**Input:** `/roadmap update`

**Output (Phase A — What Shipped):**

```
## What Shipped Since Last Update
_Last update: 2026-03-09 (da3c514), 10 commits ago_

1. **Glossary Management + Dictionary Browser** (PR #32)
   - Specs: 022, 023, 024, 025
   - 6 new components, 2 hooks, 5 test files
   - New route: /dictionary

2. **App Header Unification** (PR #33)
   - Refactored: AppHeader.tsx, NavLinks.tsx

3. **skrebe.app Redirect** (1aff903)
   - New ADR: 0010-skrebe-app-domain-redirect.md

⚠️  CHANGELOG.md [Unreleased] is missing entries for 3 features.

Running full codebase scan...
```

**Output (Phase B — Proposed Updates):**

```
## Proposed Updates to docs/PROJECT-STATUS.md

  ~ Last updated: 2026-03-09 → 2026-03-15
  ~ Branch: da3c514 → 1aff903
  ~ Velocity: 129 → 139 commits
  ~ skrebe-web: 4 routes → 5 routes, ~54 → ~63 components, 12 → 18 hooks
  ~ text-core: 8 → 10 test files
  + Phase 3e: Glossary Management + Dictionary Browser → Done
  + Phase 3f: ALUPEC Phonology Rule → Done
  + Spec 022: Glossary Management UX → Complete
  + Spec 023: Glossary UX Polish → Complete
  + Spec 024: Glossary Gap Detection → Complete
  + Spec 025: Dictionary Browser → Complete
  + ADR 0010: skrebe.app → papia.studio redirect → Active
  + Test row: Glossary (4 files) + Dictionary (3 files)

Apply updates to PROJECT-STATUS.md? (y/N)
```

**After approval, if CHANGELOG gaps exist:**

```
Add CHANGELOG entries for 3 shipped features under [Unreleased]? (y/N)
```

**After CHANGELOG (if plan exists and phase changed):**

```
Phase status changed — syncing project plan...

## Proposed Updates to docs/PROJECT-PLAN.md

### Phases
  + Phase 3e: Glossary Management + Dictionary Browser -> Done

### Spec Traceability
  + Spec 022-025 -> linked to Phase 3e [MANUAL]

### ADR Traceability
  + ADR 0010: skrebe.app redirect -> linked to Phase 3f [AUTO-LINKED]

Apply updates to docs/PROJECT-PLAN.md? (y/N)
```

## Example 8: Status with Drift Warning

**Input:** `/roadmap status`

**Output (end of dashboard):**

```
### Recommended Next Actions
1. Translation Memory + Eval Harness (Phase 4) — next on Track A
2. Expand LLM golden pairs — 5 → 10-15

---
⚠️  Documentation may be stale: 4 feature/fix commits since last status update (2026-03-09).
Run `/roadmap update` to sync.
```

## Zero-Config Example

The skill adapts to any project structure:

```
[No .arkhe.yaml found — using dynamic discovery]
[Read CLAUDE.md — identified as Python Django project]
[Detected: pyproject.toml, Django 5.0]
[Found apps/: users, products, orders, payments]
[Found tests/: 45 test files]
[Found docs/: architecture.md, api-spec.md]

## Project Status Dashboard
...
```

---

## Example 9: Plan Scaffold

**Input:** `/roadmap:roadmap plan scaffold`

**Output:**

```
## Context Discovery
[Standard context discovery — found .arkhe.yaml, PROJECT-STATUS.md, 2 roadmaps, 1 backlog]

## Planning Artifacts Found
- docs/PROJECT-STATUS.md — 14 phases, 26 specs in pipeline, 10 ADRs
- docs/skrebe/roadmap.md — 9 backlog themes
- docs/papia-asr/roadmap.md — 6 backlog themes
- arkhe/specs/ — 26 spec directories scanned

## Hybrid Linking Results

### Confirmed (from existing docs)
- Spec 01 → Phase 1c [MANUAL] — listed in PROJECT-STATUS.md "PR #6"
- Spec 022-025 → Phase 3e [MANUAL] — listed in PROJECT-STATUS.md
- ADR-0007 → Phase ASR-1 [MANUAL] — referenced in papia-asr/roadmap.md
  (22 specs + 8 ADRs confirmed from docs)

### Auto-Detected (from git history)
- Spec 020 → Phase 3d [AUTO-LINKED] — created 2026-03-08, during Phase 3d window
- ADR-0010 → Phase 3b [AUTO-LINKED] — created 2026-03-01

### Unlinked
- Spec 000 (Trust Guards) → ? [UNLINKED] — predates defined phases

Review the proposed plan. Adjust any linkages? (Type corrections or 'approve')
> Spec 000 → Phase 0. Otherwise approve.

Writing to docs/PROJECT-PLAN.md...
Plan created with 14 phases, 26 specs linked, 10 ADRs linked, 9 backlog themes.
```

---

## Example 10: Plan Show

**Input:** `/roadmap:roadmap plan`

**Output:**

```
## Project Plan Summary
_Source: docs/PROJECT-PLAN.md (last synced: 2026-04-03)_

### Timeline
| Phase | Status | Specs | ADRs |
|-------|--------|-------|------|
| 0 | Done | 1 | 2 |
| 1a-b | Done | 2 | 1 |
| 1c | Done | 1 | 0 |
| 1d | Done | 1 | 0 |
| 1e | Done | 3 | 0 |
| 2 | Done | 3 | 0 |
| 3a-f | Done | 6 | 2 |
| 4 | In Progress | 0 | 0 |
| ASR-1 | Done | 1 | 1 |
| ASR-2 | Not Started | 0 | 0 |

### Progress
- Phases: 13/16 complete (81%)
- Specs: 26/26 linked to phases
- ADRs: 10/10 linked to phases
- Backlog: 9 themes (1 active)

### Active Phase(s)
**Phase 4: TM + Eval** — TM core shipped (PR #35); eval harness + fuzzy UX remaining

### Next Up
Backlog Theme 5: Word List Quality (High priority, no blockers)
```

---

## Example 11: Plan Sync

**Input:** `/roadmap:roadmap plan sync`

**Output:**

```
## What Changed Since Last Sync
_Last sync: 2026-04-01 (bb4804d), 3 commits ago_

1. **CI Workflow** (PR #37, ci:) — new GitHub Actions workflow
2. **TM Case Fix + F1 Selector** (PR #38, fix:) — bug fixes in TM matching
3. **Docs updates** (docs:) — PROJECT-STATUS.md, roadmap sync

## Auto-Detection
- No new specs found
- No new ADRs found
- Phase 4: no completion signal (still In Progress)

## Proposed Updates to docs/PROJECT-PLAN.md

  ~ Phase 4 evidence: added "PR #38 — case-insensitive TM matching"
  ~ Timeline last-synced date: 2026-04-01 → 2026-04-03

Apply updates to docs/PROJECT-PLAN.md? (y/N)
> y

Plan document updated. 2 changes applied.
```

---

## Example 12: Incremental Update (Post-Sprint Sync)

**Input:** `/roadmap:roadmap update --incremental`

**Context:** After completing Sprint 010 using `/core:develop`. Wave context files exist.

**Output:**

```
## Wave Context
Found wave-context-3.md from /core:develop session (2026-04-02).
Features built: offline sync engine, conflict resolution UI, service worker.

## What Shipped Since Last Update (2026-03-28, 8 commits ago)

1. **Offline Sync Engine** (PR #38, feat:, specs 027-029)
   - 4 services, 2 hooks, 8 test files
2. **Conflict Resolution UI** (PR #39, feat:, spec 030)
   - 3 components, 1 hook, 4 test files
3. **Service Worker Registration** (PR #40, fix:)
   - Updated PWA config, added cache strategies

## Proposed Updates to docs/PROJECT-STATUS.md

### Header
  ~ Last updated: 2026-03-28 -> 2026-04-02
  ~ Commits: 144 -> 152
  ~ Branch hash: a1b2c3d -> e4f5g6h

### Module Maturity
  ~ offline-sync: Service Layer -> Tested
  ~ conflict-resolution: Stub -> Service Layer

### Phases
  ~ Phase 2 (Offline-First): In Progress -> Done

### Specs
  + Spec 027: Sync Engine Core -> Complete
  + Spec 028: Conflict Detection -> Complete
  + Spec 029: Background Sync -> Complete
  + Spec 030: Conflict Resolution UI -> Complete

Apply updates to docs/PROJECT-STATUS.md? (y/N)
> y

Status document updated. 9 changes applied.

Phase status changed — syncing project plan...

## Proposed Updates to docs/PROJECT-PLAN.md

### Timeline
  ~ Phase 2 (Offline-First): In Progress -> Done

### Spec Traceability
  + Spec 027: Sync Engine Core -> linked to Phase 2 [AUTO-LINKED]
  + Spec 028: Conflict Detection -> linked to Phase 2 [AUTO-LINKED]
  + Spec 029: Background Sync -> linked to Phase 2 [AUTO-LINKED]
  + Spec 030: Conflict Resolution UI -> linked to Phase 2 [AUTO-LINKED]

Apply updates to docs/PROJECT-PLAN.md? (y/N)
> y

Project plan updated. 5 changes applied.
```

---

## Example 13: Cached Next Actions with Smart Merge

**Input (first run):** `/roadmap:roadmap next`

**Output:**

```
## Recommended Next Actions
_Generated: 2026-04-11 (commit e4f5g6h)_

1. **Translation Memory Eval Harness** — Phase 4 blocker; specs ready, no implementation
2. **Expand LLM Golden Pairs** — 5 → 10-15 pairs for accuracy benchmarking
3. **Word List Quality Pipeline** — High priority backlog theme, no blockers
4. **API Rate Limiting** — Open gap from security review, pre-launch blocker

Saved to arkhe/roadmap/next-actions.md.
```

**Input (second run, 1 commit later):** `/roadmap:roadmap next`

**Output:**

```
## Recommended Next Actions
_Cached from 2026-04-11. 1 feat/fix commit since — below recalculation threshold._
_Run `/roadmap next --force` to recalculate._

1. **Translation Memory Eval Harness** — Phase 4 blocker; specs ready, no implementation
2. **Expand LLM Golden Pairs** — 5 → 10-15 pairs for accuracy benchmarking
3. **Word List Quality Pipeline** — High priority backlog theme, no blockers
4. **API Rate Limiting** — Open gap from security review, pre-launch blocker
```

**Input (after `/roadmap update`):** `/roadmap:roadmap next`

**Output:**

```
[Status doc updated since last calculation — recalculating with merge...]

## Proposed Updates to next-actions.md

  - **Translation Memory Eval Harness** — removed (completed: PR #45, spec 026 done)
  ~ **Expand LLM Golden Pairs** — 5 → 10-15 pairs (refreshed: now top priority after TM Eval shipped)
  = **Word List Quality Pipeline** — carried (still open, no completion evidence)
  = **API Rate Limiting** — carried (still open, pre-launch blocker)
  + **Offline Sync Polish** — new recommendation (Phase 3 ready after Phase 2 completion)

Apply merged recommendations? (y/N)
> y

Saved to arkhe/roadmap/next-actions.md.
```

---

## Example 14: User-Added Items Surviving Merge

A user manually adds an item to the `### User-Added` section of `next-actions.md`:

**File before recalculation:**

```markdown
---
generated: 2026-04-11
commit: e4f5g6h
source: /roadmap next
---

## Recommended Next Actions

1. **Translation Memory Eval Harness** — Phase 4 blocker; specs ready, no implementation
2. **Expand LLM Golden Pairs** — 5 → 10-15 pairs for accuracy benchmarking

### User-Added
- **Review onboarding UX with beta testers** — schedule before Phase 5 launch
- **Set up CI/CD pipeline** — needed for automated releases
```

**Input:** `/roadmap:roadmap next --force`

**Output:**

```
## Proposed Updates to next-actions.md

  - **Translation Memory Eval Harness** — removed (completed: spec 026 done, PR #45)
  ~ **Expand LLM Golden Pairs** — refreshed (still 5 pairs, now top priority)
  + **Word List Quality Pipeline** — new recommendation (high priority backlog theme)
  + **API Rate Limiting** — new recommendation (open gap from security review)
  = **Review onboarding UX with beta testers** (user-added, preserved)
  ? **Set up CI/CD pipeline** (user-added; CI/CD pipeline appears shipped in PR #48 — remove? keep?)

Apply merged recommendations? (y/N)
> y

Saved to arkhe/roadmap/next-actions.md.
```

**Resulting file:**

```markdown
---
generated: 2026-04-15
commit: b2c3d4e
source: /roadmap next
---

## Recommended Next Actions

1. **Expand LLM Golden Pairs** — 5 → 10-15 pairs for accuracy benchmarking
2. **Word List Quality Pipeline** — High priority backlog theme, no blockers
3. **API Rate Limiting** — Open gap from security review, pre-launch blocker

### User-Added
- **Review onboarding UX with beta testers** — schedule before Phase 5 launch
```
