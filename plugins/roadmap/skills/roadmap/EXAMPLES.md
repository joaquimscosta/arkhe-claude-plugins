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
