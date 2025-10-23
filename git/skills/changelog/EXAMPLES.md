# Changelog Generator Examples

Real-world scenarios for generating changelogs in the your project monorepo.

## Example 1: Service Release (user-service v1.2.0)

### Context
User-service needs a release with JWT improvements and bug fixes.

### Command
```bash
cd backend/user-service
/changelog-generator --since v1.1.0 --version 1.2.0 --append
```

### Git History (user-service)
```
feat: add JWT token refresh endpoint (#145)
fix: resolve token expiration race condition (#146)
docs: update API documentation for auth endpoints
test: add integration tests for JWT refresh flow
chore: upgrade Spring Security to 6.2.1
```

### Generated Changelog
```markdown
# Changelog

All notable changes to the User Service will be documented in this file.

## [1.2.0] - 2025-10-22

### Added
- JWT token refresh endpoint for improved session management (#145)

### Fixed
- Token expiration race condition in authentication flow (#146)

### Changed
- Upgraded Spring Security to 6.2.1 for security improvements

## [1.1.0] - 2025-09-15

...
```

### Skill Output
```
✅ Changelog generated successfully
📊 Analysis:
   - 5 commits analyzed
   - Version bump: MINOR (1.1.0 → 1.2.0)
   - Categories: 1 feat, 1 fix, 1 docs, 1 test, 1 chore
   - Breaking changes: 0

📝 Updated: backend/user-service/CHANGELOG.md
🏷️  Suggested tag: git tag -a v1.2.0 -m "Release v1.2.0"
```

## Example 2: Frontend Release (web-ui v2.1.0)

### Context
Major UI update with UIFort components and Material-UI theme changes.

### Command
```bash
cd frontend/web-ui
/changelog-generator --format keepachangelog --version 2.1.0
```

### Git History (web-ui)
```
feat: integrate UIFort data table for keyword research (#201)
feat: add multi-currency support in revenue dashboard (#202)
feat!: migrate from Redux to TanStack Query + Zustand (#203)
fix: resolve hydration errors in Next.js 14 (#204)
perf: optimize bundle size (reduced by 30%) (#205)
style: update Material-UI theme to livingCoral preset (#206)
docs: add UIFort integration guide
```

### Generated Changelog
```markdown
# Changelog

All notable changes to your project UI will be documented in this file.

## [2.1.0] - 2025-10-22

### Added
- UIFort data table component for keyword research with sorting, filtering, and pagination (#201)
- Multi-currency support in revenue dashboard with automatic USD conversion (#202)
- Material-UI livingCoral theme preset for improved visual consistency (#206)

### Changed
- **BREAKING**: Migrated state management from Redux to TanStack Query + Zustand (#203)
  - Redux store removed - see migration guide
  - React Query now handles server state
  - Zustand manages client UI state

### Fixed
- Next.js 14 hydration errors in server components (#204)

### Performance
- Reduced bundle size by 30% through code splitting and lazy loading (#205)

## [2.0.0] - 2025-08-01

...
```

### Skill Output
```
⚠️  BREAKING CHANGES DETECTED
📊 Analysis:
   - 7 commits analyzed
   - Version bump: MAJOR (2.0.0 → 2.1.0) - Contains breaking change
   - Categories: 3 feat, 1 fix, 1 perf, 1 style, 1 docs
   - Breaking changes: 1 (state management migration)

🚨 Breaking Change Details:
   - Commit: feat!: migrate from Redux to TanStack Query + Zustand (#203)
   - Impact: State management architecture change
   - Action Required: Update consuming components

📝 Updated: frontend/web-ui/CHANGELOG.md
🏷️  Suggested tag: git tag -a v2.1.0 -m "Release v2.1.0"
```

## Example 3: Monorepo Root Release (v1.5.0)

### Context
Project-wide release affecting multiple services and common-libs.

### Command
```bash
# From monorepo root
/changelog-generator --since v1.4.0 --version 1.5.0 --format github
```

### Git History (monorepo)
```
feat(common-libs): add ApiResponse standardization (#301)
feat(search-service): integrate OpenSearch with Valkey cache (#302)
feat(supply-analytics): add competition scoring algorithm (#303)
fix(trend-service): resolve ARIMA calculation accuracy (#304)
fix(favorite-service): fix race condition in list operations (#305)
docs: update architecture documentation
build: upgrade Spring Boot to 3.4.3 across all services (#306)
ci: configure GitHub Actions for automated testing (#307)
```

### Generated Changelog (GitHub Format)
```markdown
# Changelog

## What's Changed in v1.5.0

**New Features:**
- Added ApiResponse standardization in common-libs by @johndoe in #301
- Integrated OpenSearch with Valkey cache in search-service by @janesmith in #302
- Added keyword competition scoring algorithm in supply-analytics by @bobsmith in #303

**Bug Fixes:**
- Resolved ARIMA calculation accuracy in trend-service by @alicejones in #304
- Fixed race condition in favorite-service list operations by @johndoe in #305

**Infrastructure:**
- Upgraded Spring Boot to 3.4.3 across all services by @devops in #306
- Configured GitHub Actions for automated testing by @devops in #307

**Documentation:**
- Updated architecture documentation

**Full Changelog**: v1.4.0...v1.5.0

**Contributors:**
@johndoe, @janesmith, @bobsmith, @alicejones, @devops
```

### Skill Output
```
✅ Monorepo changelog generated
📊 Analysis:
   - 8 commits analyzed (across 5 services + common-libs)
   - Version bump: MINOR (1.4.0 → 1.5.0)
   - Services affected: common-libs, search-service, supply-analytics-service, trend-service, favorite-service
   - Categories: 3 feat, 2 fix, 1 docs, 1 build, 1 ci
   - Breaking changes: 0

📝 Updated: CHANGELOG.md (root)
🏷️  Suggested tag: git tag -a v1.5.0 -m "Release v1.5.0"
```

## Example 4: Patch Release (search-service v1.1.1)

### Context
Hotfix release for search-service with only bug fixes.

### Command
```bash
cd backend/search-service
/changelog-generator --since v1.1.0 --version 1.1.1 --append
```

### Git History (search-service)
```
fix: resolve OpenSearch connection timeout (#401)
fix: correct facet aggregation for keyword filters (#402)
test: add integration tests for timeout scenarios
```

### Generated Changelog
```markdown
# Changelog

## [1.1.1] - 2025-10-22

### Fixed
- OpenSearch connection timeout during high load scenarios (#401)
- Facet aggregation incorrect results for keyword filters (#402)

## [1.1.0] - 2025-10-15

...
```

### Skill Output
```
✅ Patch release generated
📊 Analysis:
   - 3 commits analyzed
   - Version bump: PATCH (1.1.0 → 1.1.1)
   - Categories: 2 fix, 1 test
   - Breaking changes: 0
   - ⚡ Hotfix recommended for production

📝 Updated: backend/search-service/CHANGELOG.md
🏷️  Suggested tag: git tag -a v1.1.1 -m "Hotfix v1.1.1"
```

## Example 5: Pre-Release (common-libs v1.6.0-rc1)

### Context
Release candidate for common-libs before production deployment.

### Command
```bash
cd backend/common-libs
/changelog-generator --since v1.5.5 --version 1.6.0-rc1 --format conventional
```

### Git History (common-libs)
```
feat: add distributed tracing utilities (#501)
feat: add rate limiting interceptor (#502)
refactor: optimize ApiResponse serialization (#503)
test: add performance benchmarks for ApiResponse
docs: update JavaDoc for new tracing utilities
```

### Generated Changelog (Conventional Format)
```markdown
# Changelog

## 1.6.0-rc1 (2025-10-22)

#### Features
* feat: add distributed tracing utilities for microservices (abc123) #501
* feat: add rate limiting interceptor for API endpoints (def456) #502

#### Code Refactoring
* refactor: optimize ApiResponse serialization for better performance (ghi789) #503

#### Documentation
* docs: update JavaDoc for new tracing utilities (jkl012)

#### Tests
* test: add performance benchmarks for ApiResponse (mno345)
```

### Skill Output
```
✅ Pre-release changelog generated
📊 Analysis:
   - 5 commits analyzed
   - Version bump: MINOR → PRE-RELEASE (1.5.5 → 1.6.0-rc1)
   - Categories: 2 feat, 1 refactor, 1 docs, 1 test
   - Breaking changes: 0
   - 🧪 Pre-release: Requires testing before stable release

⚠️  Next Steps:
   1. Deploy to staging environment
   2. Run integration tests
   3. If successful: /changelog-generator --version 1.6.0 (stable)

📝 Updated: backend/common-libs/CHANGELOG.md
🏷️  Suggested tag: git tag -a v1.6.0-rc1 -m "Release candidate v1.6.0-rc1"
```

## Example 6: Date Range (Monthly Summary)

### Context
Generate monthly changelog for October 2025 progress report.

### Command
```bash
/changelog-generator --since "2025-10-01" --until "2025-10-31" --output OCTOBER_2025.md
```

### Generated Output
```markdown
# October 2025 Progress Report

## Summary
- Total commits: 47
- Contributors: 5 (@johndoe, @janesmith, @bobsmith, @alicejones, @devops)
- Services updated: 8
- Features: 12
- Bug fixes: 8
- Performance improvements: 3

## Features Delivered

### Backend Services
- Keyword competition scoring algorithm (supply-analytics-service) #303
- JWT token refresh endpoint (user-service) #145
- OpenSearch integration with Valkey cache (search-service) #302

### Frontend
- UIFort data table integration (web-ui) #201
- Multi-currency revenue dashboard (web-ui) #202
- Material-UI theme presets (web-ui) #206

### Infrastructure
- Distributed tracing utilities (common-libs) #501
- GitHub Actions CI/CD pipeline (root) #307

## Bug Fixes

### Critical
- JWT token expiration race condition (user-service) #146
- ARIMA calculation accuracy (trend-service) #304

### High Priority
- Next.js hydration errors (web-ui) #204
- OpenSearch connection timeout (search-service) #401

## Performance Improvements
- 30% bundle size reduction (web-ui) #205
- ApiResponse serialization optimization (common-libs) #503
- Search service query optimization (search-service) #302

## Infrastructure Updates
- Spring Boot upgraded to 3.4.3 across all services #306
- Spring Security upgraded to 6.2.1 (user-service)

## Documentation
- Architecture documentation updated
- UIFort integration guide added
- API documentation updated for auth endpoints

## Testing
- Integration tests added for JWT refresh flow
- Performance benchmarks added for ApiResponse
- Timeout scenario tests for search-service
```

### Skill Output
```
✅ Monthly summary generated
📊 Analysis:
   - Date range: 2025-10-01 to 2025-10-31
   - 47 commits analyzed
   - 5 contributors
   - 8 services affected

📝 Created: OCTOBER_2025.md
```

## Next Steps

- **Level 4**: See `TROUBLESHOOTING.md` for common issues and solutions

## Version

1.0.0
